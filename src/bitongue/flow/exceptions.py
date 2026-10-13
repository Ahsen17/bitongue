from bitongue.base import BitongueError

__all__ = (
    "FlowingNotInitializedError",
    "HandlerDuplicateError",
    "HandlerNotFoundError",
)


class HandlerDuplicateError(BitongueError):
    """Exception raised when a duplicate handler is found in the flow."""


class HandlerNotFoundError(BitongueError):
    """Exception raised when a handler is not found in the flow."""


class FlowingNotInitializedError(BitongueError):
    """Exception raised when the flow is not initialized."""
