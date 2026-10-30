from datetime import datetime, timezone

import pytest

from productpulse.data.adapters import parse_mendeley_rows, parse_zenodo_split
from productpulse.data.schema import CanonicalTicket


def test_zenodo_joins_label_by_id_even_when_y_order_differs():
    x_rows = [{"id": "101", "text": "HTTP 403 after release"}, {"id": "102", "text": "How do I reset a password?"}]
    y_rows = [{"id": "102", "label": "Access"}, {"id": "101", "label": "Software"}]
    tickets = parse_zenodo_split(x_rows, y_rows, "train")
    assert [(t.source_id, t.source_label, t.split) for t in tickets] == [
        ("101", "Software", "train"), ("102", "Access", "train")
    ]
    assert all(t.created_at is None for t in tickets)


def test_zenodo_rejects_unmatched_x_y_ids_without_unsafe_positional_join():
    with pytest.raises(ValueError, match="unmatched"):
        parse_zenodo_split([{"id": "101", "text": "issue"}], [{"id": "102", "label": "Software"}], "test")


def test_zenodo_rejects_duplicate_id():
    with pytest.raises(ValueError, match="duplicate"):
        parse_zenodo_split([{"id": "1", "text": "one"}, {"id": "1", "text": "two"}], [{"id": "1", "label": "IT"}], "train")


def test_zenodo_does_not_silently_accept_unknown_field_schema():
    with pytest.raises(ValueError, match="missing required fields"):
        parse_zenodo_split([{"id": "5", "description": "hello"}], [{"id": "5", "label": "A"}], "train")


def test_zenodo_invalid_split_fails_loudly():
    with pytest.raises(ValueError, match="split"):
        parse_zenodo_split([{"id": "1", "text": "a"}], [{"id": "1", "label": "A"}], "dev")


def test_canonical_ticket_rejects_blank_id_and_empty_text():
    with pytest.raises(ValueError):
        CanonicalTicket(source="zenodo", source_id="  ", text_redacted="hello")
    with pytest.raises(ValueError):
        CanonicalTicket(source="zenodo", source_id="5", text_redacted=" ")


def test_canonical_ticket_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone"):
        CanonicalTicket(source="mendeley", source_id="10", text_redacted="x", created_at="2026-01-02T12:00:00")


def test_canonical_ticket_normalizes_aware_timestamp_to_utc():
    record = CanonicalTicket(source="mendeley", source_id="10", text_redacted="x", created_at="2026-01-02T15:00:00+03:00")
    assert record.created_at == datetime(2026, 1, 2, 12, tzinfo=timezone.utc)


def test_mendeley_maps_reporter_messages_without_leaking_outcome_as_label():
    rows = [{"issue_id": 101, "text": "A report fails to open", "issue_created": "2026-01-02T12:00:00+00:00", "issue_proj": "analytics", "issue_type": "Ticket", "issue_resolution": "Done"}]
    result = parse_mendeley_rows(rows)
    assert len(result) == 1
    assert result[0].source_id == "101"
    assert result[0].product_id == "analytics"
    assert result[0].source_label is None  # 'issue_type' is NOT intent ground truth
    assert result[0].created_at == datetime(2026, 1, 2, 12, tzinfo=timezone.utc)


def test_mendeley_missing_timestamp_remains_null():
    result = parse_mendeley_rows([{"issue_id": "17", "text": "Login error"}])
    assert result[0].created_at is None


def test_mendeley_rejects_duplicate_id_without_double_counting():
    with pytest.raises(ValueError, match="duplicate"):
        parse_mendeley_rows([{"issue_id": 10, "text": "hello"}, {"issue_id": 10, "text": "again"}])


def test_mendeley_metadata_only_rows_cannot_pretend_to_be_tickets():
    with pytest.raises(ValueError, match="missing required fields"):
        parse_mendeley_rows([{"issue_id": 1, "issue_type": "Ticket"}])


def test_zenodo_original_2022_release_category_truth_field():
    """The downloaded Zenodo X/y CSVs use id,text and id,category_truth."""
    x_rows = [{"id": "1919", "text": "File share access"}]
    y_rows = [{"id": "1919", "category_truth": "Fileservice"}]
    tickets = parse_zenodo_split(x_rows, y_rows, "train")
    assert len(tickets) == 1
    assert tickets[0].source_label == "Fileservice"

