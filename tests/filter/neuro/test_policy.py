"""Tests for bitongue.filter.neuro.policy."""

from typing import Any

import pytest

from bitongue.base import ConversionError
from bitongue.filter.neuro import NeuroFilterPolicy

_REQUIRED: dict[str, Any] = {
    "base_url": "https://unit.test/v1",
    "api_key": "unit-key",
    "model": "unit-model",
    "rules": "no spam",
}


class TestNeuroFilterPolicy:
    """Runtime configuration record: defaults, serialization, typing."""

    def test_timeout_defaults_to_ten(self) -> None:
        policy = NeuroFilterPolicy(**_REQUIRED)
        assert policy.timeout == 10.0

    def test_to_dict_expands_every_field(self) -> None:
        data = NeuroFilterPolicy(**_REQUIRED).to_dict()
        assert set(data) == {
            "base_url",
            "api_key",
            "model",
            "rules",
            "timeout",
        }

    @pytest.mark.parametrize(
        "rules",
        ["single rule", ["first", "second"]],
        ids=["str", "list"],
    )
    def test_json_round_trip(self, rules: str | list[str]) -> None:
        policy = NeuroFilterPolicy(**{**_REQUIRED, "rules": rules})
        assert NeuroFilterPolicy.from_json(policy.to_json()) == policy

    def test_from_dict_rejects_wrong_rules_type(self) -> None:
        with pytest.raises(ConversionError):
            NeuroFilterPolicy.from_dict({**_REQUIRED, "rules": 1})
