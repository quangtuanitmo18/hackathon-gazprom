from productpulse.data.schema import CanonicalTicket


def test_canonical_ticket_trims_source_id_and_source_but_preserves_text():
    result = CanonicalTicket(source="  zenodo  ", source_id="  123  ", text_redacted="  error as typed  ")
    assert result.source == "zenodo"
    assert result.source_id == "123"
    assert result.text_redacted == "  error as typed  "
