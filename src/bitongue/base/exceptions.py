__all__ = (
    "BitongueError",
    "DeserializationError",
    "SerializationError",
)


class BitongueError(Exception):
    """Base class for bitongue exceptions."""


class SerializationError(BitongueError):
    """Exception raised for errors during serialization."""


class DeserializationError(BitongueError):
    """Exception raised for errors during deserialization."""


class ConversionError(BitongueError):
    """Exception raised for errors during conversion."""
