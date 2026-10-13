"""Tests for bitongue.flow.schemas."""

from typing import Literal, cast

import msgspec
import pytest

from bitongue.flow import BaseMessage, MessageEntry


class TestBaseMessage:
    """Message construction contract."""

    def test_text_defaults_to_none(self) -> None:
        message = BaseMessage(type="text")

        assert message.text is None

    def test_rejects_unknown_type_in_conversion(self) -> None:
        # msgspec 不在 __init__ 时校验类型;Literal 约束在 convert/decode 处生效
        bogus = cast("Literal['text']", "voice")

        with pytest.raises(msgspec.ValidationError):
            msgspec.convert({"type": bogus, "text": "x"}, type=BaseMessage)


class TestMessageEntry:
    """Entry field defaults."""

    def test_timeout_defaults_to_none(self) -> None:
        message = BaseMessage(type="text", text="m")

        entry = MessageEntry(message=message, enter_time=1.0)

        assert entry.timeout is None
