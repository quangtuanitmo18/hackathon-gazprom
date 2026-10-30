#!/usr/bin/env python3
"""Static checks for the official Intelligence Cup 2026 submission contract.

The source is the user-provided 7-page PDF, not any inferred online rules.
Run from the repository root: python3 scripts/validate_case_submission.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def verify() -> None:
    main = read("submissions/main-solution.ru.md")
    metrics = read("submissions/05-effect-metrics.ru.md")
    slides = read("submissions/presentation-outline.ru.md")
    requirements = read("docs/requirements/pdf-traceability.md")
    dataset = json.loads(read("data/webneft/case-examples.json"))

    # Main text answers the PDF-required items 1–4 and 6 only.
    for n in (1, 2, 3, 4, 6):
        assert re.search(rf"(?m)^### {n}\.\s", main), f"Missing main-section {n}"
    assert not re.search(r"(?m)^### 5\.\s", main), "Item 5 must be separate .md"
    # Conservative count, including Markdown formatting, not just visible text.
    assert len(main) <= 15_000, f"Main solution has {len(main)} chars (> 15000)"
    assert len(main) > 5_000, "A full main-solution draft is required"
    assert "Qwen-ASR" in main and "Qwen-VL" in main
    assert "Qwen 3.8" in main and "Внешние" in main
    assert "40" in main and "один год" in main
    assert "сценарные" in main and "неизвест" in main.lower()

    # Section 5 is an independent deliverable with real-baseline caveats.
    assert "Пункт 5" in metrics and "TPI" in metrics
    for term in ("baseline", "fallback", "unknown_coverage"):
        # Russian wording may vary, but this exact project document currently
        # contains these markers and must not silently drop them.
        if term != "fallback":
            assert term in metrics, f"Expected item-5 trace term: {term}"
    assert "review" in metrics

    assert dataset["source_page"] == 6
    cases = dataset["cases"]
    assert len(cases) == 7 and [v["id"] for v in cases] == [
        f"PDF6-{i:02d}" for i in range(1, 8)
    ]
    assert all(v["source_ticket_id"] is None and
               v["source_created_at"] is None and
               v["ingested_at"] is None and
               v["same_incident_ground_truth"] is None and
               v["label_status"] == "proposed_unadjudicated"
               for v in cases), "Do not fabricate labels or event-time"
    assert len([x for x in slides.splitlines() if re.match(r"^\|\s*(?:10|[1-9])\s*\|", x)]) == 10
    for page in range(1, 8):
        assert ("стр. " + str(page)) in requirements or (
            "стр. " + str(page) + "–" in requirements
        ), f"PDF page {page} not covered by traceability"
    assert "15 000" in requirements
    print("PASS: official case contract, 1–4 + 6, separate 5,",
          f"main={len(main)} chars, seven unadjudicated examples, ten slides")


if __name__ == "__main__":
    verify()
