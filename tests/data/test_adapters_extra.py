from productpulse.data.schema import CanonicalTicket


def test_canonical_ticket_trims_source_id_and_source_but_preserves_text():
    result = CanonicalTicket(source="  zenodo  ", source_id="  123  ", text_redacted="  error as typed  ")
    assert result.source == "zenodo"
    assert result.source_id == "123"
    assert result.text_redacted == "  error as typed  "


def test_ticket_rejects_numeric_timestamp_instead_of_guessing_epoch():
    import pytest

    with pytest.raises(ValueError):
        CanonicalTicket(source="mendeley", source_id="1", text_redacted="hello", created_at=1735689600)

def test_ticket_rejects_numeric_string_timestamp_instead_of_epoch():
    import pytest
    with pytest.raises(ValueError):
        CanonicalTicket(source="mendeley", source_id="1", text_redacted="hello", created_at="1735689600")

def test_zenodo_rejects_nonfinite_ids():
    import pytest
    from productpulse.data.adapters import parse_zenodo_split
    with pytest.raises(ValueError, match="invalid"):
        parse_zenodo_split([{"id": float("nan"), "text": "body"}], [{"id": float("nan"), "label": "A"}], "train")

def test_zenodo_rejects_nonfinite_labels():
    import pytest
    from productpulse.data.adapters import parse_zenodo_split
    with pytest.raises(ValueError, match="label"):
        parse_zenodo_split([{"id": 1, "text": "body"}], [{"id": 1, "label": float("nan")}], "test")
