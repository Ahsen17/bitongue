"""Tests for bitongue.filter.utils.tokenizer.

Kept in a dedicated file because jieba's first dictionary load is slow.
"""

from bitongue.filter.sparse import JiebaTokenizer


class TestTokenize:
    """Segmentation runs on normalized text, in jieba search-engine mode."""

    def test_chinese_search_segmentation(self) -> None:
        tokens = JiebaTokenizer.tokenize("我来到北京清华大学")
        assert "北京" in tokens
        assert "清华大学" in tokens

    def test_normalized_before_segmentation(self) -> None:
        tokens = [t for t in JiebaTokenizer.tokenize("ABC DEF") if t.strip()]
        assert tokens == ["abc", "def"]

    def test_unusable_text_yields_no_tokens(self) -> None:
        assert JiebaTokenizer.tokenize("!!!") == []
