import pytest
from productpulse.data.adapters import parse_zenodo_split, parse_mendeley_rows


def test_zenodo_joins_labels_by_id_not_position():
    x = [{"id": "1", "text": "login failed"}, {"id": "2", "text": "printer problem"}]
    y = [{"id": "2", "label": "hardware"}, {"id": "1", "label": "software"}]
    tickets = parse_zenodo_split(x, y, "train")
    assert [(t.source_id, t.source_label) for t in tickets] == [("1", "software"), ("2", "hardware")]


def test_zenodo_rejects_missing_label():
    with pytest.raises(ValueError, match="unmatched"):
        parse_zenodo_split([{"id": "1", "text": "x"}], [], "train")


def test_zenodo_rejects_empty_id():
    with pytest.raises(ValueError, match="id"):
        parse_zenodo_split([{"id": "", "text": "x"}], [{"id": "", "label": "other"}], "train")


def test_mendeley_preserves_missing_timestamp():
    row = {"issue_id": "42", "description": "server failed", "project_id": "p-1"}
    ticket, = parse_mendeley_rows([row])
    assert ticket.created_at is None
    assert ticket.source_label is None
    assert ticket.product_id == "p-1"


def test_mendeley_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone"):
        parse_mendeley_rows([{"issue_id":"42", "description":"error", "created_at":"2026-10-30T12:00:00"}])


def test_zenodo_detects_duplicate_x_ids():
    with pytest.raises(ValueError, match="duplicate"):
        parse_zenodo_split([{"id":"1", "text":"a"}, {"id":"1", "text":"b"}], [{"id":"1", "label":"x"}], "test")
