"""Russian synthetic cases are regression examples, NOT domain accuracy evidence."""
import json
from pathlib import Path

import pytest

from productpulse.data.canonical import CanonicalTicketV1
from productpulse.incident.verify import screen_pair


FIXTURE = Path(__file__).parents[1] / "fixtures" / "russian_incident_pairs.json"
CASES = json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_metadata_prevents_accuracy_misrepresentation():
    assert CASES["fixture_origin"] == "SYNTHETIC"
    assert "F1" in CASES["not_valid_for"]
    assert len(CASES["cases"]) >= 16
    assert len({x["id"] for x in CASES["cases"]}) == len(CASES["cases"])


@pytest.mark.parametrize("case", CASES["cases"], ids=[x["id"] for x in CASES["cases"]])
def test_conservative_verifier_behaviors_on_russian_synthetic_cases(case):
    a = CanonicalTicketV1(
        source_system="synthetic", source_ticket_id=case["id"] + "-a",
        provenance_id="SYNTHETIC:manual-fixture",
        **case["a"],
    )
    b = CanonicalTicketV1(
        source_system="synthetic", source_ticket_id=case["id"] + "-b",
        provenance_id="SYNTHETIC:manual-fixture",
        **case["b"],
    )
    output = screen_pair(a, b, *case["symptoms"])
    assert output.status == case["expected"]
    assert output.requires_human_review is True
    if case.get("blocker"):
        assert case["blocker"] in output.blockers
    # The policy never returns a confirmed incident relationship.
    assert output.status != "same_incident"
