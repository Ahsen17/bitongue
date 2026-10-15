"""The in-memory message flowing window.

The window is a bounded FIFO buffer built on an anyio memory stream.
Producers :meth:`Flowing.draw` messages into it; the consumer iterates
:meth:`Flowing.flow` and receives messages in send order, with entries that
outlived their timeout silently dropped on the way out.
"""

import time
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

import anyio

from .exceptions import FlowingNotInitializedError
from .message import BaseMessage, MessageEntry

if TYPE_CHECKING:
    from anyio.streams.memory import (
        MemoryObjectReceiveStream,
        MemoryObjectSendStream,
    )


__all__ = ("Flowing",)


class Flowing[T: BaseMessage]:
    """A bounded in-memory window that buffers messages between ends.

    The window wraps each drawn message into a :class:`MessageEntry` that
    records the entry time and the configured timeout. When the buffer is
    full, producers wait until the consumer makes room, which acts as
    natural backpressure. The window must be :meth:`start`-ed before use;
    operating it while stopped raises :class:`FlowingNotInitializedError`.
    """

    def __init__(
        self,
        *,
        size: int,
        timeout: int | None = None,
    ) -> None:

        self._size = size
        self._timeout = timeout

        self._sender: MemoryObjectSendStream[MessageEntry[T]] | None = None
        self._receiver: MemoryObjectReceiveStream[MessageEntry[T]] | None = None

        self._running = False

    @property
    def running(self) -> bool:
        """Whether the window is currently running."""

        return self._running

    async def start(self) -> None:
        """Open the buffer and mark the window as running.

        Idempotent: calling it on a running window does nothing. The memory
        stream is created on the first start and recreated after a
        :meth:`shutdown`, so entries never survive a full stop/start cycle.
        """

        if self._running:
            return

        if self._sender is None or self._receiver is None:
            self._sender, self._receiver = anyio.create_memory_object_stream[
                MessageEntry[T]
            ](max_buffer_size=self._size)

        self._running = True

    async def shutdown(self) -> None:
        """Close both ends of the buffer and mark the window as stopped.

        Idempotent: calling it on a stopped window does nothing. Entries
        still inside the buffer are discarded with the stream.
        """

        if not self._running:
            return

        if self._sender is not None:
            await self._sender.aclose()
            self._sender = None

        if self._receiver is not None:
            await self._receiver.aclose()
            self._receiver = None

        self._running = False

    async def draw(self, message: "T") -> None:
        """Put a message into the window.

        The message is wrapped into a :class:`MessageEntry` that records the
        current time and the window's timeout. Waits while the buffer is
        full until the consumer takes an entry.

        Raises:
            FlowingNotInitializedError: If the window is not running.
        """

        if not self._running or self._sender is None:
            raise FlowingNotInitializedError(
                "Flowing is not running",
            )

        await self._sender.send(
            MessageEntry[T](
                message=message,
                enter_time=time.time(),
                timeout=self._timeout,
            ),
        )

    async def flow(self) -> AsyncGenerator["T", None]:
        """Yield messages from the window in send order.

        Entries whose timeout has passed since their entry time are dropped
        here, silently: expiry is enforced on the consumer side, so an
        expired message produces nothing rather than an error. The stream
        is single-consumer — only one task may iterate this generator at a
        time.

        Raises:
            FlowingNotInitializedError: If the window is not running.
        """

        if not self._running or self._receiver is None:
            raise FlowingNotInitializedError(
                "Flowing is not running",
            )

        async for entry in self._receiver:
            if (
                entry.timeout is not None
                and int(time.time()) - entry.enter_time > entry.timeout
            ):
                continue

            yield entry.message
