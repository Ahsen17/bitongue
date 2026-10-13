from typing import Literal

from msgspec import field

from bitongue.base import BaseStruct

__all__ = (
    "BaseMessage",
    "MessageEntry",
)


class BaseMessage(BaseStruct):
    """Base message for flowing."""

    type: Literal["text"]
    text: str | None = field(default=None)


class MessageEntry[T: BaseMessage](BaseStruct):
    """Entry of a message."""

    message: T

    enter_time: float
    timeout: float | None = field(default=None)
