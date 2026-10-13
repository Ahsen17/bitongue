from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from bitongue.flow import BaseMessage

    from .schemas import BaseResult


__all__ = ("BaseHandler",)


class BaseHandler[T: BaseMessage, R: BaseResult](Protocol):
    """Base handler for bitongue."""

    async def handle(self, message: "T") -> "R": ...
