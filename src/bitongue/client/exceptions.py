from bitongue.base import BitongueError

__all__ = ("MessageHandleError",)


class MessageHandleError(BitongueError):
    """Raised when message handle fails."""
