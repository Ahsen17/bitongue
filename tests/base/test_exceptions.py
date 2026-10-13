"""Tests for bitongue.base.exceptions."""

import pytest

from bitongue.base import (
    BitongueError,
    ConversionError,
    DeserializationError,
    SerializationError,
)


class TestExceptionHierarchy:
    """Every base exception derives from BitongueError."""

    @pytest.mark.parametrize(
        "exc_type",
        [SerializationError, DeserializationError, ConversionError],
    )
    def test_derives_from_bitongue_error(self, exc_type: type[Exception]) -> None:
        assert issubclass(exc_type, BitongueError)
