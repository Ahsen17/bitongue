"""Message admission gate for the flowing pipeline.

A filter decides whether a message is allowed to proceed to handling.
Implement the protocol with a plain class — no inheritance required.
"""

from typing import Protocol

from bitongue.flow import BaseMessage

__all__ = ("BaseFilter",)


class BaseFilter[T: BaseMessage](Protocol):
    """A predicate that decides which messages may proceed.

    Implementations should be side-effect-free predicates: the orchestrator
    runs every filter in the chain without short-circuiting, so a filter
    may be called even when an earlier one already rejected the message.

    Returns:
        ``True`` to release the message into handling; ``False`` to reject
        it, which drops the message silently with no result and no error.
    """

    async def filter(self, message: "T") -> bool: ...
