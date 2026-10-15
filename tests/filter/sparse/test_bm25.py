"""Tests for bitongue.filter.sparse.bm25 (local Bm25CN, no network access)."""

from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pytest
from fastembed.sparse.sparse_embedding_base import SparseEmbedding

from bitongue.filter import Bm25CN
from bitongue.filter.sparse.bm25 import Bm25CNWorker


class TestRawEmbed:
    """raw_embed: one embedding per document, deterministic, degenerate inputs."""

    def test_one_embedding_per_document(self) -> None:
        out = Bm25CN().raw_embed(["第一篇文档内容", "second document text"])
        assert len(out) == 2
        assert all(isinstance(embedding, SparseEmbedding) for embedding in out)

    def test_deterministic_for_same_text(self) -> None:
        sut = Bm25CN()
        first = sut.raw_embed(["稳定分词测试文本"])
        second = sut.raw_embed(["稳定分词测试文本"])
        assert np.array_equal(first[0].indices, second[0].indices)
        assert np.array_equal(first[0].values, second[0].values)

    def test_unusable_document_yields_empty_embedding(self) -> None:
        (only,) = Bm25CN().raw_embed(["!!!"])
        assert only.indices.size == 0


class TestTermFrequency:
    """The term-frequency part matches the BM25 definition (k/b/length sensitive)."""

    def test_formula_matches_definition(self) -> None:
        sut = Bm25CN(k=1.2, b=0.75, avg_len=3.0)
        tf = sut._term_frequency(["a", "a", "b"])
        expected_a = (2 * (1.2 + 1)) / (2 + 1.2 * (1 - 0.75 + 0.75 * (3 / 3)))
        expected_b = (1 * (1.2 + 1)) / (1 + 1.2 * (1 - 0.75 + 0.75 * (3 / 3)))
        assert tf[Bm25CN.compute_token_id("a")] == pytest.approx(expected_a)
        assert tf[Bm25CN.compute_token_id("b")] == pytest.approx(expected_b)

    def test_empty_tokens_yield_empty_map(self) -> None:
        assert Bm25CN()._term_frequency([]) == {}


class TestStem:
    """Token filtering: punctuation/stopword/length rules and file loading."""

    def test_punctuation_only_token_dropped(self) -> None:
        assert Bm25CN()._stem(["!!!", "word"]) == ["word"]

    def test_overlong_token_dropped(self) -> None:
        sut = Bm25CN(token_max_length=3)
        assert sut._stem(["abcd", "abc"]) == ["abc"]

    def test_custom_stopwords_filtered(self) -> None:
        sut = Bm25CN(stopwords={"The"})
        assert sut._stem(["the", "word"]) == ["word"]

    def test_stopwords_filepath_loaded_as_utf8(self, tmp_path: Path) -> None:
        path = tmp_path / "stopwords.txt"
        path.write_text("停用\n", encoding="utf-8")
        sut = Bm25CN(stopwords_filepath=path)
        assert sut._stem(["停用", "保留"]) == ["保留"]

    def test_stemmer_conflict_rejected(self) -> None:
        with pytest.raises(ValueError, match="stemmer"):
            Bm25CN(disable_stemmer=True, stemmer=object())  # type: ignore[arg-type]


class TestEmbedVariants:
    """embed input shapes and its signature-compatibility behavior."""

    def test_str_equals_single_element_list(self) -> None:
        sut = Bm25CN()
        from_str = next(iter(sut.embed("稳定分词测试文本")))
        from_list = next(iter(sut.embed(["稳定分词测试文本"])))
        assert np.array_equal(from_str.indices, from_list.indices)
        assert np.array_equal(from_str.values, from_list.values)

    def test_extra_kwargs_ignored(self) -> None:
        # kwargs exist only for fastembed base-class signature compatibility;
        # they are neither forwarded nor rejected.
        out = list(Bm25CN().embed(["文档"], bogus_kwarg=1))
        assert len(out) == 1

    def test_parallel_branch_routes_through_worker_pool(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # The parallel path never spawns real processes: the pool is a fake
        # that embeds inline, verifying only the routing.
        sut = Bm25CN()

        class _FakePool:
            def __init__(
                self,
                num_workers: int,
                worker: object,
                start_method: str,
            ) -> None:
                self.num_workers = num_workers
                self.worker = worker
                self.start_method = start_method

            def ordered_map(
                self,
                batches: Iterator[list[str]],
                **_kwargs: object,
            ) -> Iterator[list[SparseEmbedding]]:
                return (sut.raw_embed(batch) for batch in batches)

        monkeypatch.setattr(
            "bitongue.filter.sparse.bm25.ParallelWorkerPool",
            _FakePool,
        )

        out = list(
            sut.embed(["北京", "上海", "广州", "深圳"], batch_size=2, parallel=2),
        )
        assert len(out) == 4

    def test_token_count(self) -> None:
        sut = Bm25CN()
        assert sut.token_count(["北京", "上海"]) == 2
        assert sut.token_count("北京") == 1


class TestQueryEmbed:
    """Query-side binary vectors: all-ones values, dedup, document token space."""

    def test_binary_values(self) -> None:
        (embedding,) = list(Bm25CN().query_embed("北京 上海"))
        assert set(embedding.values.tolist()) == {1.0}

    def test_duplicate_tokens_deduplicated(self) -> None:
        (embedding,) = list(Bm25CN().query_embed("北京北京"))
        assert embedding.indices.size == 1

    def test_query_ids_within_document_ids(self) -> None:
        sut = Bm25CN()
        doc = sut.raw_embed(["北京 上海"])[0]
        (query,) = list(sut.query_embed("北京 上海"))
        assert set(query.indices.tolist()) <= set(doc.indices.tolist())


class TestTokenId:
    """mmh3 token id stability (uuid5 content addressing depends on it)."""

    def test_stable_across_calls(self) -> None:
        assert Bm25CN.compute_token_id("北京") == Bm25CN.compute_token_id("北京")

    def test_different_tokens_differ(self) -> None:
        assert Bm25CN.compute_token_id("北京") != Bm25CN.compute_token_id("上海")


class TestWorker:
    """Bm25CNWorker: direct construction and batch processing."""

    def test_init_embedding_builds_model(self) -> None:
        model = Bm25CNWorker.init_embedding(k=2.0)
        assert isinstance(model, Bm25CN)
        assert model.k == 2.0

    def test_start_returns_worker(self) -> None:
        worker = Bm25CNWorker.start(k=1.5)
        assert worker.model.k == 1.5

    def test_process_embeds_batches(self) -> None:
        worker = Bm25CNWorker.start()
        (idx, embeddings) = next(iter(worker.process([(0, ["北京"])])))
        assert idx == 0
        assert len(embeddings) == 1
