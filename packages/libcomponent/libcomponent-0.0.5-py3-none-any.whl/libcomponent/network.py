"""Network - Module for sending events over the network."""

# Programmed by CoolCat467

from __future__ import annotations

# Copyright (C) 2023-2025  CoolCat467
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see
# <https://www.gnu.org/licenses/>.

__title__ = "Network"
__author__ = "CoolCat467"
__license__ = "GNU Lesser General Public License Version 3"


import contextlib
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    NoReturn,
)

import trio

from libcomponent.base_io import (
    BaseAsyncReader,
    BaseAsyncWriter,
    StructFormat,
)
from libcomponent.buffer import Buffer
from libcomponent.component import (
    Component,
    ComponentManager,
    Event,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from types import TracebackType

    from typing_extensions import Self

    from libcomponent.base_io import INT_FORMATS_TYPE


class NetworkTimeoutError(Exception):
    """Network Timeout Error."""

    __slots__ = ()


class NetworkEOFError(Exception):
    """Network End of File Error."""

    __slots__ = ()


class NetworkStreamNotConnectedError(Exception):
    """Network Stream Not Connected Error."""

    __slots__ = ()


class NetworkComponent(Component, BaseAsyncReader, BaseAsyncWriter):
    """Network Component (client)."""

    __slots__ = ("_stream", "timeout")

    def __init__(self, name: str) -> None:
        """Initialize Network Component."""
        super().__init__(name)

        self.timeout: int | float = 3
        self._stream: trio.abc.HalfCloseableStream | None = None

    @property
    def not_connected(self) -> bool:
        """Is stream None?."""
        return self._stream is None

    @property
    def stream(self) -> trio.abc.HalfCloseableStream:
        """Trio SocketStream or raise NetworkStreamNotConnectedError."""
        if self._stream is None:
            raise NetworkStreamNotConnectedError("Stream not connected!")
        return self._stream

    @classmethod
    def from_stream(
        cls,
        *args: object,
        kwargs: dict[str, object] | None = None,
        stream: trio.abc.HalfCloseableStream,
    ) -> Self:
        """Initialize from stream."""
        if kwargs is None:
            kwargs = {}
        self = cls(*args, **kwargs)  # type: ignore[arg-type]
        self._stream = stream
        return self

    async def connect(self, host: str, port: int) -> None:
        """Connect to host:port on TCP.

        Raises:
          OSError: if the connection fails.
          RuntimeError: if stream is already connected

        """
        if not self.not_connected:
            raise RuntimeError("Already connected!")
        try:  # pragma: nocover
            self._stream = await trio.open_tcp_stream(host, port)
        except OSError:  # pragma: nocover
            await self.close()
            raise

    async def read(self, length: int) -> bytearray:
        """Read `length` bytes from stream.

        Can raise following exceptions:
            NetworkStreamNotConnectedError - Network stream is not connected
            NetworkTimeoutError - Timeout
            NetworkEOFError - End of File
            OSError - Stopped responding
            trio.BusyResourceError - Another task is already writing data
            trio.BrokenResourceError - Something is wrong and stream is broken
            trio.ClosedResourceError - Stream is closed or another task closes stream
        """
        content = bytearray()
        while max_read_count := length - len(content):
            received: bytes | bytearray = b""
            # try:
            with trio.move_on_after(self.timeout) as cancel_scope:
                received = await self.stream.receive_some(max_read_count)
            cancel_called = cancel_scope.cancel_called
            # except (trio.BrokenResourceError, trio.ClosedResourceError):
            # await self.close()
            # raise
            if len(received) == 0:
                # No information at all
                if len(content) == 0:
                    if cancel_called:
                        raise NetworkTimeoutError("Read timed out.")
                    raise NetworkEOFError(
                        "Server did not respond with any information.",
                    )
                # Only sent a few bytes, but we requested more
                raise OSError(
                    f"Server stopped responding (got {len(content)} bytes, "
                    f"but expected {length} bytes)."
                    f" Partial obtained packet: {content!r}",
                )
            content.extend(received)
        return content

    async def write(self, data: bytes | bytearray | memoryview) -> None:
        """Send the given data through the stream, blocking if necessary.

        Args:
          data (bytes, bytearray, or memoryview): The data to send.

        Raises:
          trio.BusyResourceError: if another task is already executing a
              :meth:`send_all`, :meth:`wait_send_all_might_not_block`, or
              :meth:`HalfCloseableStream.send_eof` on this stream.
          trio.BrokenResourceError: if something has gone wrong, and the stream
              is broken.
          trio.ClosedResourceError: if you previously closed this stream
              object, or if another task closes this stream object while
              :meth:`send_all` is running.

        Most low-level operations in Trio provide a guarantee: if they raise
        :exc:`trio.Cancelled`, this means that they had no effect, so the
        system remains in a known state. This is **not true** for
        :meth:`send_all`. If this operation raises :exc:`trio.Cancelled` (or
        any other exception for that matter), then it may have sent some, all,
        or none of the requested data, and there is no way to know which.

        Copied from Trio docs.

        """
        await self.stream.send_all(data)

    async def close(self) -> None:
        """Close the stream, possibly blocking."""
        if self._stream is None:
            await trio.lowlevel.checkpoint()
            return
        await self._stream.aclose()
        self._stream = None

    async def send_eof(self) -> None:
        """Close the sending half of the stream.

        This corresponds to ``shutdown(..., SHUT_WR)`` (`man
          page <https://linux.die.net/man/2/shutdown>`__).

        If an EOF has already been sent, then this method should silently
        succeed.

        Raises:
          trio.BusyResourceError: if another task is already executing a
              :meth:`~SendStream.send_all`,
              :meth:`~SendStream.wait_send_all_might_not_block`, or
              :meth:`send_eof` on this stream.
          trio.BrokenResourceError: if something has gone wrong, and the stream
              is broken.

        Suppresses:
          trio.ClosedResourceError: if you previously closed this stream
              object, or if another task closes this stream object while
              :meth:`send_eof` is running.

        Copied from trio docs.

        """
        with contextlib.suppress(trio.ClosedResourceError):
            await self.stream.send_eof()

    async def wait_write_might_not_block(self) -> None:
        """Block until it's possible that :meth:`write` might not block.

        This method may return early: it's possible that after it returns,
        :meth:`send_all` will still block. (In the worst case, if no better
        implementation is available, then it might always return immediately
        without blocking. It's nice to do better than that when possible,
        though.)

        This method **must not** return *late*: if it's possible for
        :meth:`send_all` to complete without blocking, then it must
        return. When implementing it, err on the side of returning early.

        Raises:
          trio.BusyResourceError: if another task is already executing a
              :meth:`send_all`, :meth:`wait_send_all_might_not_block`, or
              :meth:`HalfCloseableStream.send_eof` on this stream.
          trio.BrokenResourceError: if something has gone wrong, and the stream
              is broken.
          trio.ClosedResourceError: if you previously closed this stream
              object, or if another task closes this stream object while
              :meth:`wait_send_all_might_not_block` is running.

        Note:
          This method is intended to aid in implementing protocols that want
          to delay choosing which data to send until the last moment. E.g.,
          suppose you're working on an implementation of a remote display server
          like `VNC
          <https://en.wikipedia.org/wiki/Virtual_Network_Computing>`__, and
          the network connection is currently backed up so that if you call
          :meth:`send_all` now then it will sit for 0.5 seconds before actually
          sending anything. In this case it doesn't make sense to take a
          screenshot, then wait 0.5 seconds, and then send it, because the
          screen will keep changing while you wait; it's better to wait 0.5
          seconds, then take the screenshot, and then send it, because this
          way the data you deliver will be more
          up-to-date. Using :meth:`wait_send_all_might_not_block` makes it
          possible to implement the better strategy.

          If you use this method, you might also want to read up on
          ``TCP_NOTSENT_LOWAT``.

          Further reading:

          * `Prioritization Only Works When There's Pending Data to Prioritize
            <https://insouciant.org/tech/prioritization-only-works-when-theres-pending-data-to-prioritize/>`__

          * WWDC 2015: Your App and Next Generation Networks: `slides
            <http://devstreaming.apple.com/videos/wwdc/2015/719ui2k57m/719/719_your_app_and_next_generation_networks.pdf?dl=1>`__,
            `video and transcript
            <https://developer.apple.com/videos/play/wwdc2015/719/>`__

        Copied from Trio docs.

        """
        return await self.stream.wait_send_all_might_not_block()

    async def __aenter__(self) -> Self:
        """Async context manager enter."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Async context manager exit. Close connection."""
        await self.close()


class NetworkEventComponent(NetworkComponent):
    """Network Event Component - Send events over the network."""

    __slots__ = (
        "_read_packet_id_to_event_name",
        "_write_event_name_to_packet_id",
        "packet_id_format",
        "read_lock",
        "write_lock",
    )

    def __init__(
        self,
        name: str,
        packet_id_format: INT_FORMATS_TYPE = StructFormat.UBYTE,
    ) -> None:
        """Initialize Network Event Component."""
        super().__init__(name)

        self.packet_id_format = packet_id_format

        self._read_packet_id_to_event_name: dict[int, str] = {}
        self._write_event_name_to_packet_id: dict[str, int] = {}
        self.read_lock = trio.Lock()
        self.write_lock = trio.Lock()

    def bind_handlers(self) -> None:
        """Register serverbound event handlers."""
        self.register_handlers(
            dict.fromkeys(
                self._write_event_name_to_packet_id,
                self.write_event,
            ),
        )

    def register_network_write_event(
        self,
        event_name: str,
        packet_id: int,
    ) -> None:
        """Map event name to serverbound packet id.

        Raises:
          ValueError: Event name already registered or infinite network loop.

        """
        if event_name in self._write_event_name_to_packet_id:
            raise ValueError(f"{event_name!r} event already registered!")
        if self._read_packet_id_to_event_name.get(packet_id) == event_name:
            raise ValueError(
                f"{event_name!r} events are also being received "
                f"from server with packet id {packet_id!r}, "
                "which will would lead to infinite looping over network",
            )
        self._write_event_name_to_packet_id[event_name] = packet_id
        if self.manager_exists:
            self.register_handler(event_name, self.write_event)

    def register_network_write_events(self, event_map: dict[str, int]) -> None:
        """Map event names to serverbound packet ids."""
        for event_name, packet_id in event_map.items():
            self.register_network_write_event(event_name, packet_id)

    def unregister_network_write_event(self, write_event_name: str) -> None:
        """Unregister given network write event.

        Will unregister all event handlers for given write event.

        Raises ValueError if given write event name is not registered.
        """
        if write_event_name not in self._write_event_name_to_packet_id:
            raise ValueError(
                f"{write_event_name!r} write event not registered!",
            )
        del self._write_event_name_to_packet_id[write_event_name]
        if self.manager_exists:
            self.unregister_handler_type(write_event_name)

    def unregister_network_write_events(
        self,
        write_events: Iterable[str],
    ) -> None:
        """Unregister given network write events.

        Will unregister all event handlers for given write events.

        Raises ValueError any given write event name is not registered.
        """
        for event_name in write_events:
            self.unregister_network_write_event(event_name)

    def unregister_all_network_write_events(self) -> None:
        """Unregister all network write events.

        Will unregister all event handlers for all write events.
        """
        self.unregister_network_write_events(
            tuple(self._write_event_name_to_packet_id),
        )

    async def write_event(
        self,
        event: Event[bytes | bytearray],
    ) -> None:
        """Send event to network.

        Raises:
          RuntimeError: if unregistered packet id received from network
          trio.BusyResourceError: if another task is already executing a
              :meth:`send_all`, :meth:`wait_send_all_might_not_block`, or
              :meth:`HalfCloseableStream.send_eof` on this stream.
          trio.BrokenResourceError: if something has gone wrong, and the stream
              is broken.
          trio.ClosedResourceError: if you previously closed this stream
              object, or if another task closes this stream object while
              :meth:`send_all` is running.

        """
        packet_id = self._write_event_name_to_packet_id.get(event.name)
        if packet_id is None:
            raise RuntimeError(f"Unhandled network event name {event.name!r}")

        buffer = Buffer()
        buffer.write_value(self.packet_id_format, packet_id)
        buffer.write_bytearray(event.data)

        async with self.write_lock:
            try:
                await self.write(buffer)
            except NetworkStreamNotConnectedError as exc:
                exc.add_note(f"{event = }")
                raise

    async def write_event_last_minute_data(
        self,
        event_name: str,
        event_data_function: Callable[[], bytes | bytearray],
    ) -> None:
        """Write event to network, but have data to send be generated last minute.

        `event_name` should be a valid registered event name.
        `event_data_function` should be a synchronous function that returns data to send in event payload.

        Workaround for using wait_write_might_not_block with
        `self.write_lock` acquired, otherwise can hit trio.BusyResourceError.

        Raises:
          RuntimeError: if unregistered packet id received from network
          trio.BusyResourceError: if another task is already executing a
              :meth:`send_all`, :meth:`wait_send_all_might_not_block`, or
              :meth:`HalfCloseableStream.send_eof` on this stream.
          trio.BrokenResourceError: if something has gone wrong, and the stream
              is broken.
          trio.ClosedResourceError: if you previously closed this stream
              object, or if another task closes this stream object while
              :meth:`send_all` is running.

        """
        packet_id = self._write_event_name_to_packet_id.get(event_name)
        if packet_id is None:
            raise RuntimeError(f"Unhandled network event name {event_name!r}")

        buffer = Buffer()
        buffer.write_value(self.packet_id_format, packet_id)

        async with self.write_lock:
            await self.wait_write_might_not_block()
            buffer.write_bytearray(event_data_function())
            await self.write(buffer)

    async def read_event(self) -> Event[bytearray]:
        """Receive event from network.

        Can raise following exceptions:
          RuntimeError - Unhandled packet id
          NetworkStreamNotConnectedError - Network stream is not connected
          NetworkTimeoutError - Timeout or no data
          OSError - Stopped responding
          trio.BrokenResourceError - Something is wrong and stream is broken
          trio.ClosedResourceError - Stream is closed or another task closes stream

        Shouldn't happen with write lock but still:
          trio.BusyResourceError - Another task is already writing data
        """
        async with self.read_lock:
            packet_id = await self.read_value(self.packet_id_format)
            event_data = await self.read_bytearray()
        event_name = self._read_packet_id_to_event_name.get(packet_id)
        if event_name is None:
            exc = RuntimeError(f"Unhandled packet ID {packet_id!r}")
            if sys.version_info >= (3, 11):
                exc.add_note(f"{event_data = }")
            raise exc
        return Event(event_name, event_data)

    def register_read_network_event(
        self,
        packet_id: int,
        event_name: str,
    ) -> None:
        """Map clientbound packet id to event name."""
        if packet_id in self._read_packet_id_to_event_name:
            raise ValueError(f"Packet ID {packet_id!r} already registered!")
        if self._write_event_name_to_packet_id.get(event_name) == packet_id:
            raise ValueError(
                f"Packet id {packet_id!r} packets are also being received "
                f"from server with as {event_name!r} events, "
                "which will would lead to infinite looping over network",
            )
        self._read_packet_id_to_event_name[packet_id] = event_name

    def register_read_network_events(self, packet_map: dict[int, str]) -> None:
        """Map clientbound packet ids to event names."""
        for packet_id, event_name in packet_map.items():
            self.register_read_network_event(packet_id, event_name)

    def unregister_read_network_event(self, read_packet_id: int) -> None:
        """Unregister given network read packet ID.

        Will unregister all event handlers for given read event.

        Raises ValueError if given read event packet ID is not registered.
        """
        if read_packet_id not in self._read_packet_id_to_event_name:
            raise ValueError(f"Packet ID {read_packet_id!r} not registered!")
        event_name = self._read_packet_id_to_event_name[read_packet_id]
        del self._read_packet_id_to_event_name[read_packet_id]
        if self.manager_exists:
            self.unregister_handler_type(event_name)

    def unregister_read_network_events(
        self,
        read_events: Iterable[int],
    ) -> None:
        """Unregister given network read packet IDs.

        Will unregister all event handlers for given read events.

        Raises ValueError any given read event packet ID is not registered.
        """
        for packet_id in read_events:
            self.unregister_read_network_event(packet_id)

    def unregister_all_read_network_events(self) -> None:
        """Unregister all network read packet IDs.

        Will unregister all event handlers for all read events.
        """
        self.unregister_read_network_events(
            tuple(self._read_packet_id_to_event_name),
        )


class Server(ComponentManager):
    """Asynchronous TCP Server."""

    __slots__ = ("serve_cancel_scope",)

    def __init__(self, name: str, own_name: str | None = None) -> None:
        """Initialize Server."""
        super().__init__(name, own_name)
        self.serve_cancel_scope: trio.CancelScope | None = None

    def stop_serving(self) -> None:
        """Cancel serve scope immediately.

        This method is idempotent, i.e., if the scope was already
        cancelled then this method silently does nothing.
        """
        if self.serve_cancel_scope is None:
            return
        self.serve_cancel_scope.cancel()

    # "Implicit return in function which does not return"
    async def serve(  # type: ignore[misc]  # pragma: nocover
        self,
        port: int,
        host: str | bytes | None = None,
        backlog: int | None = None,
    ) -> NoReturn:
        """Serve over TCP. See trio.open_tcp_listeners for argument details."""
        self.serve_cancel_scope = trio.CancelScope()
        async with trio.open_nursery() as nursery:
            listeners = await trio.open_tcp_listeners(
                port,
                host=host,
                backlog=backlog,
            )

            async def handle_serve(
                task_status: trio.TaskStatus[Any] = trio.TASK_STATUS_IGNORED,
            ) -> None:
                assert self.serve_cancel_scope is not None
                try:
                    with self.serve_cancel_scope:
                        await trio.serve_listeners(
                            self.handler,
                            listeners,
                            handler_nursery=nursery,
                            task_status=task_status,
                        )
                except trio.Cancelled:
                    # Close all listeners
                    async with trio.open_nursery() as cancel_nursery:
                        for listener in listeners:
                            cancel_nursery.start_soon(listener.aclose)

            await nursery.start(handle_serve)

    async def handler(
        self,
        stream: trio.SocketStream,
    ) -> None:  # pragma: nocover
        """Handle new client streams.

        Override in a subclass - Default only closes the stream
        """
        try:
            await stream.send_eof()
        finally:
            await stream.aclose()


if __name__ == "__main__":  # pragma: nocover
    print(f"{__title__}\nProgrammed by {__author__}.\n")
