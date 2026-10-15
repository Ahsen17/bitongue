"""Result models produced by handling messages."""

from uuid import UUID

from bitongue.base import BaseStruct

__all__ = ("BaseResult",)


class BaseResult(BaseStruct):
    """Base class for handling results.

    Subclass it to declare the fields a handler yields; results are
    msgspec structures with the same serialization abilities as messages.

    Attributes:
        id: Caller-supplied unique identifier, mirrored from the source
            message; bitongue never generates one.
    """

    id: UUID
