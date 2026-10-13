"""Base data structures shared across the whole library.

Every bitongue data structure inherits from :class:`BaseStruct`, which layers
serialization helpers on top of msgspec's ``Struct``: plain dictionaries,
sorted-key JSON strings, and back again.
"""

from typing import Any, Self, cast

from msgspec import Struct, convert, json, to_builtins

from .exceptions import (
    ConversionError,
    DeserializationError,
    SerializationError,
)

__all__ = ("BaseStruct",)


class BaseStruct(Struct):
    """Base class for bitongue data structures.

    Subclasses declare fields as msgspec ``Struct`` attributes and inherit
    dictionary and JSON serialization with sorted keys, so equal structures
    always produce identical JSON.
    """

    def to_dict(self) -> dict[str, Any]:
        """Convert the structure into a plain dictionary.

        Nested structures are converted recursively, so the result contains
        only built-in types and is safe to pass to ``json.dumps`` or store.
        """

        return cast("dict[str, Any]", to_builtins(self))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Build an instance of the structure from a plain dictionary.

        Raises:
            ConversionError: If ``data`` does not match the structure's
                fields, for example a missing required field or an
                incompatible value type. The original conversion error is
                attached as ``__cause__``.
        """

        try:
            return convert(data, type=cls)

        except Exception as exc:
            raise ConversionError(
                f"Failed to convert data structure: {exc}",
            ) from exc

    def to_json(self) -> str:
        """Serialize the structure into a JSON string with sorted keys.

        Sorting keys makes the output deterministic, so two equal structures
        serialize to identical strings.

        Raises:
            SerializationError: If the structure cannot be encoded as JSON.
                The original encoding error is attached as ``__cause__``.
        """

        try:
            return json.encode(
                self,
                order="sorted",
            ).decode("utf-8")

        except Exception as exc:
            raise SerializationError(
                f"Failed to serialize data structure: {exc}",
            ) from exc

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Build an instance of the structure from a JSON string.

        Raises:
            DeserializationError: If ``json_str`` is not valid JSON or does
                not match the structure's fields. The original decoding
                error is attached as ``__cause__``.
        """

        try:
            return json.decode(json_str, type=cls)

        except Exception as exc:
            raise DeserializationError(
                f"Failed to deserialize data structure: {exc}",
            ) from exc

    def __repr__(self) -> str:
        """Return the sorted-key JSON representation of the structure."""

        return self.to_json()
