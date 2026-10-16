"""Tests for bitongue.filter.neuro.provider."""

from autogen_core.models import ChatCompletionClient

from bitongue.filter.neuro import OpenAIClientProvider


class TestProvide:
    """The provider builds independent clients with the advertised
    capability set autogen needs for structured verdicts."""

    def test_provide_builds_compatible_client(self) -> None:
        client = OpenAIClientProvider(
            base_url="https://unit.test/v1",
            api_key="unit-key",
            model="unit-model",
        ).provide()
        assert isinstance(client, ChatCompletionClient)
        info = client.model_info
        assert info["structured_output"] is True
        assert info["json_output"] is True
        assert info["function_calling"] is True

    async def test_provides_are_independent_and_closable(self) -> None:
        provider = OpenAIClientProvider(
            base_url="https://unit.test/v1",
            api_key="unit-key",
            model="unit-model",
        )
        first = provider.provide()
        second = provider.provide()
        assert first is not second
        await first.close()
        await second.close()
