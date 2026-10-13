"""Tests for bitongue.base.schemas."""

from typing import Any

import pytest

from bitongue.base import (
    BaseStruct,
    ConversionError,
    DeserializationError,
    SerializationError,
)


class SampleStruct(BaseStruct):
    """Sample struct exercising the serialization surface."""

    zeta: str
    alpha: int


class OpaquePayload(BaseStruct):
    """Struct holding a JSON-unserializable value."""

    payload: Any


class TestBaseStruct:
    """to_dict / from_dict / to_json / from_json / repr behavior."""

    def test_to_dict_returns_plain_dict(self) -> None:
        sample = SampleStruct(zeta="v", alpha=1)

        assert sample.to_dict() == {"zeta": "v", "alpha": 1}

    def test_from_dict_round_trips(self) -> None:
        sample = SampleStruct(zeta="v", alpha=1)

        assert SampleStruct.from_dict({"zeta": "v", "alpha": 1}) == sample

    def test_to_json_sorts_keys(self) -> None:
        sample = SampleStruct(zeta="v", alpha=1)

        assert sample.to_json() == '{"alpha":1,"zeta":"v"}'

    def test_from_json_round_trips(self) -> None:
        sample = SampleStruct(zeta="v", alpha=1)

        assert SampleStruct.from_json('{"alpha":1,"zeta":"v"}') == sample

    def test_from_json_invalid_raises_deserialization_error(self) -> None:
        with pytest.raises(DeserializationError) as excinfo:
            SampleStruct.from_json("{not json")

        assert excinfo.type is DeserializationError
        assert excinfo.value.__cause__ is not None

    def test_from_dict_wrong_type_raises_conversion_error(self) -> None:
        with pytest.raises(ConversionError) as excinfo:
            SampleStruct.from_dict({"zeta": "v", "alpha": "not-an-int"})

        assert excinfo.type is ConversionError

    def test_to_json_unserializable_raises_serialization_error(self) -> None:
        weird = OpaquePayload(payload=object())  # msgspec 无对应编码器的类型

        with pytest.raises(SerializationError) as excinfo:
            weird.to_json()

        assert excinfo.type is SerializationError

    def test_repr_matches_to_json(self) -> None:
        sample = SampleStruct(zeta="v", alpha=1)

        assert repr(sample) == sample.to_json()
