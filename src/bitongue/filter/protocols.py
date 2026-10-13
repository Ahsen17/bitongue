from typing import Protocol

from bitongue.flow import BaseMessage

__all__ = ("BaseFilter",)


class BaseFilter[T: BaseMessage](Protocol):
    """Base filter for bitongue messages flowing."""

    async def filter(self, message: "T") -> bool: ...
