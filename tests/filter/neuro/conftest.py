"""Fixtures for the neuro filter unit tests (replayed model client)."""

from collections.abc import Callable, Sequence

import pytest
from autogen_core.models import CreateResult, ModelFamily, ModelInfo
from autogen_ext.models.replay import ReplayChatCompletionClient

from bitongue.filter.neuro import NeuroFilter, NeuroFilterPolicy
from bitongue.flow import BaseMessage

type MakeNeuroFilter = Callable[
    ...,
    tuple[NeuroFilter[BaseMessage], ReplayChatCompletionClient],
]

# Mirror the capability claims the real provider hands to autogen, so the
# agent takes the same structured-output path it takes in production.
_REPLAY_MODEL_INFO: ModelInfo = {
    "vision": False,
    "function_calling": True,
    "json_output": True,
    "family": ModelFamily.UNKNOWN,
    "structured_output": True,
}


@pytest.fixture
def make_neuro_filter(monkeypatch: pytest.MonkeyPatch) -> MakeNeuroFilter:
    """Factory fixture: a NeuroFilter whose model client replays canned
    responses. The provider construction is patched at its lookup site;
    monkeypatch restores it after the test."""

    def _make(
        responses: Sequence[str | CreateResult],
        *,
        rules: str | list[str] = "no spam",
        timeout: float = 5.0,
    ) -> tuple[NeuroFilter[BaseMessage], ReplayChatCompletionClient]:
        replay = ReplayChatCompletionClient(
            list(responses),
            model_info=_REPLAY_MODEL_INFO,
        )

        class _StubProvider:
            def __init__(self, **_kwargs: object) -> None:
                return

            def provide(self) -> ReplayChatCompletionClient:
                return replay

        monkeypatch.setattr(
            "bitongue.filter.neuro.filter.OpenAIClientProvider",
            _StubProvider,
        )

        policy = NeuroFilterPolicy(
            base_url="https://unit.test/v1",
            api_key="unit-key",
            model="unit-model",
            rules=rules,
            timeout=timeout,
        )
        return NeuroFilter(policy), replay

    return _make
