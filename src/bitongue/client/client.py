from collections.abc import AsyncIterator, Iterable
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
    """Bitongue client."""

    def __init__(
        self,
        config: "BitongueConfig",
        *,
        handler: "BaseHandler[T, R]",
        filters: Iterable["BaseFilter[T]"] | None = None,
    ) -> None:

        self._config = config
        self._handler = handler
        self._filters = filters or []

        self._flow: Flowing[T] | None = None

    async def start(self) -> None:

        if self._flow is None:
            self._flow = Flowing[T](
                size=self._config.flowing_size,
                timeout=self._config.flowing_timeout,
            )

        if not self._flow.running:
            await self._flow.start()

    async def shutdown(self) -> None:

        if self._flow is not None:
            if self._flow.running:
                await self._flow.shutdown()

            self._flow = None

    async def send(self, message: "T") -> None:

        if self._flow is None or not self._flow.running:
            raise RuntimeError("Run `start` first.")

        await self._flow.draw(message)

    async def result(self) -> AsyncIterator["R"]:

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
