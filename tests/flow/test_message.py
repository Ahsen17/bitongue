"""Tests for bitongue.flow.message."""

from typing import Literal, cast
from uuid import UUID, uuid4

import msgspec
import pytest

from bitongue.flow import BaseMessage, MessageEntry


class TestBaseMessage:
    """Message construction contract."""

    def test_text_defaults_to_none(self) -> None:
        message = BaseMessage(id=uuid4(), type="text")

        assert message.text is None

    def test_id_round_trips_through_serialization(self) -> None:
        message = BaseMessage(id=uuid4(), type="text", text="m")

        assert BaseMessage.from_dict(message.to_dict()) == message
        assert BaseMessage.from_json(message.to_json()) == message
        assert isinstance(BaseMessage.from_dict(message.to_dict()).id, UUID)

    def test_rejects_unknown_type_in_conversion(self) -> None:
        # msgspec does not validate at __init__; Literal constraints apply
        # at convert/decode time. The dict carries a valid id so the
        # reported error is the bogus type, not the missing field.
        bogus = cast("Literal['text']", "voice")

        with pytest.raises(msgspec.ValidationError):
            msgspec.convert(
                {"id": str(uuid4()), "type": bogus, "text": "x"},
                type=BaseMessage,
            )


class TestMessageEntry:
    """Entry field defaults."""

    def test_timeout_defaults_to_none(self) -> None:
        message = BaseMessage(id=uuid4(), type="text", text="m")

        entry = MessageEntry(message=message, enter_time=1.0)

        assert entry.timeout is None
