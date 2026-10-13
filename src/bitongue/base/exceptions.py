"""Exception hierarchy shared across the library.

Every bitongue exception derives from :class:`BitongueError`, so callers can
catch the whole family with a single ``except BitongueError`` while still
being able to handle specific failures individually.
"""

__all__ = (
    "BitongueError",
    "DeserializationError",
    "SerializationError",
)


class BitongueError(Exception):
    """Base class for every exception raised by bitongue."""


class SerializationError(BitongueError):
    """Raised when a data structure cannot be encoded into JSON."""


class DeserializationError(BitongueError):
    """Raised when input cannot be decoded into a data structure."""


class ConversionError(BitongueError):
    """Raised when a dictionary does not match a data structure's fields."""
