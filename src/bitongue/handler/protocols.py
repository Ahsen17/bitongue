"""Business handling extension point for the flowing pipeline.

A handler turns an admitted message into a result. Implement the protocol
with a plain class — no inheritance required.
"""

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from bitongue.flow import BaseMessage

    from .schemas import BaseResult


__all__ = ("BaseHandler",)


class BaseHandler[T: BaseMessage, R: BaseResult](Protocol):
    """A unit of business logic applied to each admitted message.

    The orchestrator bounds each call by the configured handle timeout and
    cancels the work when it runs out, skipping the message without
    blocking later ones. Any exception raised here is wrapped into
    :class:`bitongue.client.MessageHandleError` and propagates to the
    consumer of the results.

    Returns:
        The handling result, an ``R`` instance to yield to the consumer.
    """

    async def handle(self, message: "T") -> "R": ...
