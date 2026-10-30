"""Realistic GitBugs duplicate-link parsing and auditing tests.

No missing edge may become a verified negative pair.
"""
import pytest

from productpulse.data.gitbugs import parse_duplicate_ids, normalize_positive_links


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("123", ("123",)),
        (" 00042 ", ("00042",)),
        ("123, 456", ("123", "456")),
        ("['123', '456']", ("123", "456")),
        ('["123", "456"]', ("123", "456")),
        ("['123']", ("123",)),
        ("", ()),
        ("[]", ()),
    ],
)
def test_parse_duplicate_ids_from_real_link_schemas(raw, expected):
    assert parse_duplicate_ids(raw) == expected


@pytest.mark.parametrize(
    "raw",
    ["-1", "abc", "123;456", "['123', __import__('os').system('id')]", "{'x': 1}", "123.4", "[1, None]"],
)
def test_parse_duplicate_ids_never_evaluates_arbitrary_content(raw):
    with pytest.raises(ValueError):
        parse_duplicate_ids(raw)


def test_normalize_reciprocal_edges_only_once():
    rows = [
        {"Issue id": "100", "Duplicate id": "200"},
        {"Issue id": "200", "Duplicate id": "100"},
        {"Issue id": "100", "Duplicate id": "200"},
    ]
    result = normalize_positive_links(rows, {"100", "200"})
    assert result.positives == frozenset({("100", "200")})
    assert result.reciprocal_or_repeated == 2
    assert result.orphan_count == 0


def test_multiple_targets_and_orphans_audited_separately():
    rows = [{"Issue id": "100", "Duplicate id": "['200', '300', '999']"}]
    result = normalize_positive_links(rows, {"100", "200", "300"})
    assert result.positives == frozenset({("100", "200"), ("100", "300")})
    assert result.orphan_count == 1
    assert result.unlabeled_count == 0


def test_self_link_is_not_positive():
    result = normalize_positive_links([{"Issue id": "100", "Duplicate id": "100"}], {"100"})
    assert result.positives == frozenset()
    assert result.self_link_count == 1


def test_missing_or_unparseable_mapping_row_is_quarantined():
    result = normalize_positive_links(
        [
            {"Issue id": "", "Duplicate id": "123"},
            {"Issue id": "1", "Duplicate id": "bad value"},
        ],
        {"1", "123"},
    )
    assert result.malformed_count == 2
    assert result.positives == frozenset()


def test_no_duplicate_link_is_unknown_not_negative_label():
    result = normalize_positive_links(
        [{"Issue id": "100", "Duplicate id": ""}], {"100", "200"}
    )
    assert result.positives == frozenset()
    assert result.unlabeled_count == 1
    assert not hasattr(result, "negative_pairs")


def test_deterministic_numerical_order_and_two_distinct_sources():
    result = normalize_positive_links([{"Issue id": "20", "Duplicate id": "3"}], {"20", "3"})
    assert result.positives == frozenset({("3", "20")})


def test_missing_index_does_not_prove_endpoints_exist():
    result = normalize_positive_links([{"Issue id": "1", "Duplicate id": "2"}], None)
    assert result.positives == frozenset({("1", "2")})
    assert result.link_index_validated is False
