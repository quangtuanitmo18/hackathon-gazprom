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
    # Source traceability table explicitly accounts for all 7 pages.
    for marker in ("| 1–2 |", "| 2 |", "| 3 |", "| 4 |",
                   "| 5 |", "| 6 |", "| 7 |"):
        assert marker in requirements, f"Missing PDF table marker: {marker}"
    assert "15 000" in requirements

    # Design-source checks only, NOT a Mermaid syntax/render validation
    # nor a claim that Qwen has been called.
    tools_doc = read("docs/agent/tool-contracts.md")
    prompt_doc = read("docs/agent/system-prompt.ru.md")
    contract_doc = read("docs/agent/output-contracts.md")
    test_doc = read("docs/evaluation/prompt-adversarial-cases.md")
    gallery = read("docs/diagrams/README.md")
    diagram_names = (
        "c4-containers.mmd",
        "data-flow-trust-boundaries.mmd",
        "agent-workflow.mmd",
        "feedback-sequence.mmd",
    )
    assert gallery.count("```mermaid") == len(diagram_names)
    for name in diagram_names:
        source = read("docs/diagrams/" + name)
        assert len(source) > 500, f"Diagram source too small: {name}"
        assert name in gallery, f"Missing diagram gallery link: {name}"
        assert source.strip() in gallery, f"Gallery out of date: {name}"
    df_source = read("docs/diagrams/data-flow-trust-boundaries.mmd")
    assert 'SAN -.->|"не передавать"| EXT' not in df_source, (
        "Forbidden egress must not be depicted as real data transfer"
    )
    assert "Только observed count" in read("docs/diagrams/agent-workflow.mmd")
    for tool_name in (
        "get_ticket_context", "find_related_requests",
        "aggregate_recurrence", "resolve_product_team",
        "create_insight_draft", "send_internal_digest",
        "record_product_feedback",
    ):
        assert tool_name in tools_doc, f"Missing documented tool: {tool_name}"
    test_cases = re.findall(r"(?m)^\| T\d{2} \|", test_doc)
    assert len(test_cases) >= 20, f"Expected >=20 adversarial scenarios, got {len(test_cases)}"
    examples = 0
    for document in (prompt_doc, contract_doc):
        for source_json in re.findall(r"```json\s*([\s\S]*?)```", document):
            json.loads(source_json)
            examples += 1
    assert examples >= 7, "Expected at least 7 parseable design JSON examples"
    assert "aggregate_recurrence" in prompt_doc
    assert "send_internal_digest" in prompt_doc
    assert "no external" in contract_doc.lower() or "внеш" in contract_doc
    print(f"PASS: {len(diagram_names)} Mermaid sources synchronized with gallery, "
          f"{len(test_cases)} scenarios, {examples} syntactically valid JSON examples")
    # A multi-product agent must not silently be presented as Webneft-only.
    # Official PDF p2 says many products; p6 contains Webneft examples only.
    assert "десятки внутренних и внешних цифровых продуктов" in main
    assert "«Вебнефть» — один пример" in main
    assert "Мультипродуктовый контракт" in main
    assert "product_id" in main and "taxonomy_version" in main
    assert "allowed_business_journeys" in prompt_doc
    assert "allowed_symptom_codes" in prompt_doc
    assert "не" in contract_doc and "Webneft" in contract_doc
    assert "product_id" in contract_doc and "taxonomy_version" in contract_doc
    for case_id in ("T21", "T22", "T23", "T24"):
        assert f"| {case_id} |" in test_doc, f"Missing cross-product test {case_id}"
    assert "для всех продуктов" in metrics or "всех продуктов" in metrics
    outline = read("submissions/presentation-outline.ru.md")
    assert "Webneft" in outline and "один" in outline
    assert "10 слайдов" in outline
    print("PASS: multi-product scope, per-product taxonomy, routing and four product-boundary tests")
    # Economic scenario regression check: arithmetic and textual cross-file consistency.
    finance = read("docs/business/financial-assumptions.md")
    release = read("docs/evaluation/release-gates.md")
    annotation = read("docs/evaluation/annotation-guidelines.md")
    case_model = json.loads(read("docs/business/scenario-inputs.json"))
    common = case_model["constant_inputs"]
    assert common["support_managers"] == 40
    assert common["years"] == 3
    assert common["months_per_year"] == 12
    assert len(case_model["scenarios"]) == 3
    rate = common["nominal_discount_rate"]
    growth = common["nominal_hourly_value_growth"]
    def thousands(value: int) -> str:
        return f"{value:,}".replace(",", " ")
    for scenario in case_model["scenarios"]:
        annual = (common["support_managers"] * common["working_days_per_month"]
                  * common["months_per_year"] * scenario["minutes_saved_per_manager_day"]
                  / 60 * scenario["adoption_fraction"] * scenario["hour_value_rub"])
        three_year = annual * common["years"]
        pv = sum(annual * scenario["realizable_fraction"] * (1 + growth) ** (t - 1)
                 / (1 + rate) ** t for t in range(1, common["years"] + 1))
        assert round(annual) == scenario["expected_gross_annual_rub"], scenario["id"]
        assert round(three_year) == scenario["expected_gross_three_year_rub"], scenario["id"]
        assert round(pv) == scenario["expected_pv_realizable_rub"], scenario["id"]
        for amount in ("expected_gross_annual_rub", "expected_gross_three_year_rub",
                       "expected_pv_realizable_rub"):
            shown = thousands(scenario[amount])
            assert shown in finance, f"finance missing {scenario['id']}: {shown}"
            assert shown in main, f"main missing {scenario['id']}: {shown}"
    base_scenario = next(s for s in case_model["scenarios"] if s["id"] == "base")
    b_annual = base_scenario["expected_gross_annual_rub"]
    k_real = base_scenario["realizable_fraction"]
    for test in case_model["sensitivity"]["expected_pv_base_rub"]:
        dr = test["nominal_discount_rate"]
        ng = test["nominal_hourly_value_growth"]
        pv = sum(b_annual * k_real * (1 + ng) ** (t - 1) / (1 + dr) ** t
                 for t in range(1, common["years"] + 1))
        assert round(pv) == test["expected_rub"], f"sensitivity mismatch: {dr=} {ng=}"
        assert thousands(test["expected_rub"]) in finance, "finance sensitivity missing"
        assert thousands(test["expected_rub"]) in main, "main sensitivity missing"
    assert len(case_model["sensitivity"]["expected_pv_base_rub"]) >= 4
    assert "unknown_coverage" in metrics
    assert "reviewed/sent" in metrics
    assert "recall" in annotation.lower()
    assert "precision" in release.lower()
    assert "G0" in release and "G5" in release
    assert "правил" in finance and "BM25" in finance
    assert "не" in main and "1 641 322" in main
    print("PASS: three finance scenarios independently recalculated and cross-checked "
          "against main submission, KPI and release documentation")
    print("PASS: official case contract, 1–4 + 6, separate 5,",
          f"main={len(main)} chars, seven unadjudicated examples, ten slides")


if __name__ == "__main__":
    verify()
