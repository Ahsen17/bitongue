"""Tests for bitongue.flow.exceptions."""

import pytest

from bitongue.base import BitongueError
from bitongue.flow import (
    FlowingNotInitializedError,
    HandlerDuplicateError,
    HandlerNotFoundError,
)


class TestExceptionHierarchy:
    """Every flow exception derives from BitongueError."""

    @pytest.mark.parametrize(
        "exc_type",
        [FlowingNotInitializedError, HandlerDuplicateError, HandlerNotFoundError],
    )
    def test_derives_from_bitongue_error(self, exc_type: type[Exception]) -> None:
        assert issubclass(exc_type, BitongueError)
