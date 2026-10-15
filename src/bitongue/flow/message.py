"""Message models carried by the flowing window."""

from typing import Literal
from uuid import UUID

from msgspec import field

from bitongue.base import BaseStruct

__all__ = (
    "BaseMessage",
    "MessageEntry",
)


class BaseMessage(BaseStruct):
    """Base message delivered through the flowing window.

    Attributes:
        id: Caller-supplied unique identifier; bitongue never generates
            one — carry over the business-side ID the message came with.
        type: Message kind; currently fixed to ``"text"``.
        text: The message content; ``None`` means the message carries no
            text payload.
    """

    id: UUID
    type: Literal["text"]
    text: str | None = field(default=None)


class MessageEntry[T: BaseMessage](BaseStruct):
    """A message wrapped for buffering inside the flowing window.

    Attributes:
        message: The wrapped message itself.
        enter_time: Epoch seconds when the entry entered the window; the
            expiry clock starts here, including time spent waiting in the
            buffer.
        timeout: Lifetime of the entry in seconds; ``None`` means the entry
            never expires. Enforced when the entry is drawn, not while it
            waits.
    """

    message: T

    enter_time: float
    timeout: float | None = field(default=None)
