"""Contract tests: runtime arrival-known fields vs evaluation-only truth."""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from productpulse.data.canonical import (
    CanonicalTicketV1,
    DatasetCapabilities,
    GoldDuplicateLink,
    ticket_key,
)


def make_ticket(**overrides):
    args = {
        "source_system": "zenodo",
        "source_ticket_id": "42",
        "title": None,
        "body_redacted": "HTTP 403 after release",
        "provenance_id": "sha256:abc",
    }
    args.update(overrides)
    return CanonicalTicketV1(**args)


def test_two_sources_with_same_id_have_distinct_ticket_keys():
    assert ticket_key(make_ticket(source_system="zenodo")) != ticket_key(
        make_ticket(source_system="gazprom")
    )


def test_namespaced_keys_have_no_delimiter_collision():
    assert ticket_key(make_ticket(source_system="ab", source_ticket_id="c")) != ticket_key(
        make_ticket(source_system="a", source_ticket_id="bc")
    )


def test_missing_or_blank_ticket_text_is_invalid():
    with pytest.raises(ValidationError, match="title or body"):
        make_ticket(title=None, body_redacted=None)
    with pytest.raises(ValidationError, match="title or body"):
        make_ticket(title=" ", body_redacted="")


def test_missing_or_blank_provenance_is_invalid():
    with pytest.raises(ValidationError, match="provenance"):
        make_ticket(provenance_id=" ")


def test_naive_timestamp_rejected():
    with pytest.raises(ValidationError, match="timezone"):
        make_ticket(created_at="2026-10-30T10:00:00")


def test_tz_aware_timestamp_converted_to_utc():
    t = make_ticket(created_at="2026-10-30T13:00:00+03:00")
    assert t.created_at == datetime(2026, 10, 30, 10, tzinfo=timezone.utc)


def test_absent_timestamp_or_product_allowed_without_invention():
    t = make_ticket()
    assert t.created_at is None
    assert t.product_id is None


def test_arrival_time_contract_forbids_gold_or_resolution_fields():
    with pytest.raises(ValidationError, match="extra_forbidden"):
        make_ticket(duplicate_of="master-100")
    with pytest.raises(ValidationError, match="extra_forbidden"):
        make_ticket(resolution="Fixed")


def test_gold_link_is_separate_from_ticket_and_cannot_link_to_itself():
    gold = GoldDuplicateLink(source_system="gitbugs", issue_id="101", master_id="202", evidence_type="source_duplicate_link")
    assert gold.issue_id == "101"
    with pytest.raises(ValidationError, match="self"):
        GoldDuplicateLink(source_system="gitbugs", issue_id="101", master_id="101", evidence_type="source_duplicate_link")


def test_dataset_capabilities_default_false_and_not_magic_inferred():
    flags = DatasetCapabilities(classification_gold=True)
    assert flags.classification_gold
    assert not flags.duplicate_links
    assert not flags.timestamps
    assert not flags.owner_gold
    assert not flags.status_events


def test_unsupported_schema_version_is_rejected():
    with pytest.raises(ValidationError, match="literal_error"):
        make_ticket(schema_version="2.0")
