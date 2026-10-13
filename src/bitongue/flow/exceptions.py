"""Exceptions raised by the flowing window and its handler registry."""

from bitongue.base import BitongueError

__all__ = (
    "FlowingNotInitializedError",
    "HandlerDuplicateError",
    "HandlerNotFoundError",
)


class HandlerDuplicateError(BitongueError):
    """Raised when a handler is registered twice for the same kind."""


class HandlerNotFoundError(BitongueError):
    """Raised when no handler is registered for the requested kind."""


class FlowingNotInitializedError(BitongueError):
    """Raised when the window is used before it is started.

    :meth:`bitongue.flow.Flowing.draw` and
    :meth:`bitongue.flow.Flowing.flow` both require a started window; this
    error reports operating it while stopped.
    """
