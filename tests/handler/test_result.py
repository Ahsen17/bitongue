"""Tests for bitongue.handler.result."""

from uuid import uuid4

import pytest

from bitongue.handler import BaseResult


class SampleResult(BaseResult):
    """Concrete result exercising the base contract."""

    content: str


class TestBaseResult:
    """Result construction and serialization contract."""

    def test_id_is_required(self) -> None:
        with pytest.raises(TypeError):
            SampleResult(content="x")  # type: ignore[call-arg]

    def test_round_trips_through_dict_and_json(self) -> None:
        result = SampleResult(id=uuid4(), content="x")

        assert SampleResult.from_dict(result.to_dict()) == result
        assert SampleResult.from_json(result.to_json()) == result
