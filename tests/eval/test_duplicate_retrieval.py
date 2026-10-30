"""No unlinked pair is a negative; retrieval is evaluated against positive links."""
import pytest
from productpulse.eval.duplicate_retrieval import (
    build_query_positives, evaluate_positive_retrieval,
)


def test_positive_links_yield_both_query_directions():
    gold = build_query_positives({("100", "200"), ("100", "300")})
    assert gold == {
        "100": frozenset({"200", "300"}),
        "200": frozenset({"100"}),
        "300": frozenset({"100"}),
    }


def test_hit_recall_and_mrr_with_self_exclusion():
    gold = {"q1": {"p1"}, "q2": {"p2"}}
    ranks = {"q1": ["q1", "bad", "p1"], "q2": ["p2", "q2"]}
    result = evaluate_positive_retrieval(ranks, gold, ks=(1, 5))
    assert result["queries_evaluated"] == 2
    assert result["hit_at_1"] == pytest.approx(0.5)
    assert result["hit_at_5"] == pytest.approx(1.0)
    assert result["recall_at_1"] == pytest.approx(0.5)
    assert result["recall_at_5"] == pytest.approx(1.0)
    assert result["mrr_at_5"] == pytest.approx(0.75)


def test_multiple_true_positive_neighbors_are_not_binary_recall():
    gold = {"q": {"p1", "p2"}}
    result = evaluate_positive_retrieval({"q": ["p1", "wrong", "p2"]}, gold, ks=(1, 3))
    assert result["hit_at_1"] == 1.0
    assert result["recall_at_1"] == pytest.approx(0.5)
    assert result["recall_at_3"] == pytest.approx(1.0)


def test_no_positive_queries_never_report_zero_accuracy():
    result = evaluate_positive_retrieval({"q": ["p1"]}, {"q": set()}, ks=(1,))
    assert result["queries_evaluated"] == 0
    assert result["hit_at_1"] is None
    assert result["mrr_at_1"] is None
    assert result["queries_without_positive"] == 1


def test_gold_not_in_candidate_corpus_is_coverage_gap():
    result = evaluate_positive_retrieval({"q": ["r"]}, {"q": {"missing"}}, known_ids={"q", "r"}, ks=(1,))
    assert result["queries_evaluated"] == 0
    assert result["queries_with_unavailable_positive"] == 1


def test_missing_ranked_query_is_not_silently_ignored():
    result = evaluate_positive_retrieval({}, {"q": {"p"}}, ks=(1,))
    assert result["queries_evaluated"] == 0
    assert result["queries_without_ranking"] == 1


def test_duplicate_candidates_do_not_inflate_recall():
    result = evaluate_positive_retrieval({"q": ["p1", "p1"]}, {"q": {"p1","p2"}}, ks=(2,))
    assert result["recall_at_2"] == pytest.approx(0.5)


def test_evaluation_does_not_generate_precision_or_negative_pairs():
    result = evaluate_positive_retrieval({"q": ["p1", "x"]}, {"q": {"p1"}}, ks=(1,))
    assert "precision" not in str(result).lower()
    assert "negative" not in str(result).lower()
