"""Result models produced by handling messages."""

from bitongue.base import BaseStruct

__all__ = ("BaseResult",)


class BaseResult(BaseStruct):
    """Base class for handling results.

    Subclass it to declare the fields a handler yields; results are
    msgspec structures with the same serialization abilities as messages.
    """
