import time
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

import anyio

from .exceptions import FlowingNotInitializedError
from .schemas import BaseMessage, MessageEntry

if TYPE_CHECKING:
    from anyio._core._streams import (  # type: ignore
        MemoryObjectReceiveStream,
        MemoryObjectSendStream,
    )


__all__ = ("Flowing",)


class Flowing[T: BaseMessage]:
    """Message flowing window for bitongue."""

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

        return self._running

    async def start(self) -> None:

        if self._running:
            return

        if self._sender is None or self._receiver is None:
            self._sender, self._receiver = anyio.create_memory_object_stream[
                MessageEntry[T]
            ](max_buffer_size=self._size)

        self._running = True

    async def shutdown(self) -> None:

        if not self._running:
            return

        if self._sender is not None:
            await self._sender.aclose()
            self._sender = None

        if self._receiver is not None:
            await self._receiver.aclose()
            self._receiver = None

        self._running = False

    async def draw(self, message: T) -> None:

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

    async def flow(self) -> AsyncIterator[T]:

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
