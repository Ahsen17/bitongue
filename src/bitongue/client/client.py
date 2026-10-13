"""The high-level orchestrator assembling the message flowing pipeline."""

from collections.abc import AsyncGenerator, Collection
from typing import TYPE_CHECKING

import anyio

from bitongue.flow import BaseMessage, Flowing
from bitongue.handler import BaseResult

from .exceptions import MessageHandleError

if TYPE_CHECKING:
    from bitongue.filter import BaseFilter
    from bitongue.handler import BaseHandler

    from .config import BitongueConfig


class Bitongue[T: BaseMessage, R: BaseResult]:
    """Client that owns the full message flowing lifecycle.

    It wires a handler and an optional filter chain together with a
    :class:`bitongue.flow.Flowing` window created from the config:
    :meth:`start` opens the window, :meth:`send` feeds it, and
    :meth:`result` drains it through expiry removal, the filter chain, and
    the handler. Call :meth:`shutdown` when done.
    """

    def __init__(
        self,
        config: "BitongueConfig",
        *,
        handler: "BaseHandler[T, R]",
        filters: Collection["BaseFilter[T]"] | None = None,
    ) -> None:

        self._config = config
        self._handler = handler
        self._filters = filters or []

        self._flow: Flowing[T] | None = None

    async def start(self) -> None:
        """Create the flowing window from the config and start it.

        Idempotent: calling it on a started client does nothing.
        """

        if self._flow is None:
            self._flow = Flowing[T](
                size=self._config.flowing_size,
                timeout=self._config.flowing_timeout,
            )

        if not self._flow.running:
            await self._flow.start()

    async def shutdown(self) -> None:
        """Stop the flowing window and release it.

        Idempotent: calling it on a stopped client does nothing. Messages
        still buffered in the window are discarded.
        """

        if self._flow is not None:
            if self._flow.running:
                await self._flow.shutdown()

            self._flow = None

    async def send(self, message: "T") -> None:
        """Put a message into the flowing window.

        Waits while the window is full until the consumer makes room.

        Raises:
            RuntimeError: If the client has not been started, or was
                shut down after starting.
        """

        if self._flow is None or not self._flow.running:
            raise RuntimeError("Run `start` first.")

        await self._flow.draw(message)

    async def result(self) -> AsyncGenerator["R", None]:
        """Yield handling results for messages drawn from the window.

        Each message passes, in order: expiry removal, the filter chain
        (every filter must accept; the chain does not short-circuit), and
        the handler bounded by the configured handle timeout. A message
        whose filter rejects it or whose handling times out is skipped
        silently — no result, no error, later messages unaffected. An
        exception raised inside the handler is wrapped into
        :class:`MessageHandleError` and propagates to the consumer.

        The underlying stream is single-consumer: only one task may
        iterate this generator at a time.

        Raises:
            RuntimeError: If the client has not been started, or was
                shut down after starting.
            MessageHandleError: If the handler raises; the original
                exception is attached as ``__cause__``.
        """

        if self._flow is None or not self._flow.running:
            raise RuntimeError("Run `start` first.")

        async for message in self._flow.flow():
            try:
                with anyio.fail_after(
                    delay=self._config.handle_timeout,
                    reason="Handle timeout",
                ):
                    if not all(
                        [
                            await _filter.filter(
                                message,
                            )
                            for _filter in self._filters
                        ]
                        if self._filters
                        else []
                    ):
                        continue

                    try:
                        result = await self._handler.handle(message)

                    except Exception as exc:
                        raise MessageHandleError(
                            f"Message handle failed. Error: {exc}",
                        ) from exc

                yield result

            except anyio.get_cancelled_exc_class():
                raise

            except TimeoutError:
                continue
