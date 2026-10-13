"""Tests for bitongue.client.exceptions."""

from bitongue.base import BitongueError
from bitongue.client import MessageHandleError


class TestExceptionHierarchy:
    """Every client exception derives from BitongueError."""

    def test_derives_from_bitongue_error(self) -> None:
        assert issubclass(MessageHandleError, BitongueError)
