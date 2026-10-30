"""Requirements: source-specific lexical, vector and fixed-parameter fusion retrieval.

Tests are offline, deterministic and do not fetch ML weights.
"""
import pytest
from productpulse.eval.retrieval_methods import (
    tokenize, BM25Index, cosine_rank, reciprocal_rank_fusion
)


def test_tokenizer_preserves_technical_error_codes_and_versions():
    assert tokenize("Ошибка HTTP 403 E_AUTH_017 v2.8.1") == [
        "ошибка", "http", "403", "e_auth_017", "v2.8.1"
    ]


def test_bm25_ranks_exact_error_code_above_related_topic():
    index = BM25Index(
        ["1", "2", "3"],
        ["ошибка входа HTTP 403", "как поменять пароль для входа", "экспорт excel 403"],
    )
    candidates = index.rank("ошибка входа HTTP 403", exclude_id="1", k=2)
    assert candidates[0] == "3"
    assert len(candidates) == 2
    assert "1" not in candidates


def test_bm25_respects_self_exclusion_and_deterministic_ties():
    index = BM25Index(["z", "b", "a"], ["same text", "other", "other"])
    assert index.rank("unknown tokens", exclude_id="z", k=5) == ["b", "a"]


def test_bm25_duplicate_id_is_rejected():
    with pytest.raises(ValueError, match="unique"):
        BM25Index(["same", "same"], ["foo", "bar"])


def test_bm25_mismatched_corpus_length_is_rejected():
    with pytest.raises(ValueError, match="length"):
        BM25Index(["1"], ["a", "b"])


def test_cosine_rank_respects_self_and_normalization():
    embedding_ids = ["a", "b", "c"]
    vectors = [[2.0, 0.0], [0.8, 0.6], [-1.0, 0.0]]
    assert cosine_rank("a", embedding_ids, vectors, k=2) == ["b", "c"]


def test_cosine_rejects_nan_and_zero_vectors():
    with pytest.raises(ValueError, match="non-finite|invalid"):
        cosine_rank("a", ["a", "b"], [[1.0, 0.0], [float("nan"), 1.0]], k=1)
    with pytest.raises(ValueError, match="zero"):
        cosine_rank("a", ["a", "b"], [[0.0, 0.0], [1.0, 0.0]], k=1)


def test_cosine_unknown_query_does_not_silently_find_nearest():
    with pytest.raises(ValueError, match="unknown query"):
        cosine_rank("q", ["a"], [[1.0, 0.0]], k=1)


def test_rrf_combines_rank_positions_not_incomparable_scores():
    ranked = {"bm25": ["a", "b", "c"], "dense": ["b", "a", "z"]}
    assert reciprocal_rank_fusion(ranked, k=3, rrf_k=60)[:2] == ["a", "b"]


def test_rrf_excludes_self_deduplicates_and_respects_k():
    ranked = {"one": ["q", "a", "a", "b"], "two": ["q", "b"]}
    assert reciprocal_rank_fusion(ranked, k=2, exclude_id="q") == ["b", "a"]


def test_rrf_handles_empty_and_deterministic_ties():
    assert reciprocal_rank_fusion({"lex": [], "dense": []}, k=3) == []
    assert reciprocal_rank_fusion({"lex": ["b"], "dense": ["a"]}, k=3) == ["a", "b"]


def test_rrf_invalid_k_and_no_methods_rejected():
    with pytest.raises(ValueError):
        reciprocal_rank_fusion({}, k=2)
    with pytest.raises(ValueError):
        reciprocal_rank_fusion({"a": ["x"]}, k=0)
