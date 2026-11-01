#!/usr/bin/env python3
"""Static checks for the official Intelligence Cup 2026 submission contract.

The source is the user-provided 7-page PDF, not any inferred online rules.
Run from the repository root: python3 scripts/validate_case_submission.py
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime
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
    assert "40" in main and ("один год" in main or "1 год" in main)
    assert ("сценар" in main.lower() or "гипотез" in main.lower()) and "неизвест" in main.lower()

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
    # Regression: Mermaid sequence diagrams treat a literal semicolon in a
    # message as a statement separator, even though it looks like prose.
    # Mermaid supports #59; to escape a literal semicolon.
    seq = read("docs/diagrams/feedback-sequence.mmd")
    assert "sequenceDiagram" in seq and "M-->>A: proposed intent" in seq
    for lineno, line in enumerate(seq.splitlines(), start=1):
        if re.match(r"^\s*\w+\s*-+>>?\s*\w+\s*:", line):
            message = line.split(":", 1)[1]
            unescaped = re.sub(r"#[A-Za-z0-9]+;", "", message)
            assert ";" not in unescaped, (
                f"Unescaped semicolon in sequence message at line {lineno}"
            )
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
    assert ("«Вебнефть» — один пример" in main or
            "«Вебнефть» — один иллюстративный продукт" in main)
    assert ("Мультипродуктовый контракт" in main or
            "Мультипродуктовый контроль" in main)
    assert "product_id" in main and "taxonomy" in main
    assert "allowed_business_journeys" in prompt_doc
    assert "allowed_symptom_codes" in prompt_doc
    assert "не" in contract_doc and "Webneft" in contract_doc
    assert "product_id" in contract_doc and "taxonomy_version" in contract_doc
    for case_id in ("T21", "T22", "T23", "T24"):
        assert f"| {case_id} |" in test_doc, f"Missing cross-product test {case_id}"
    assert "по каждому подключенному продукту" in metrics
    assert "общекорпоративный агрегат" in metrics
    outline = read("submissions/presentation-outline.ru.md")
    assert "Webneft" in outline and "один" in outline
    assert "10 слайдов" in outline
    print("PASS: multi-product scope, per-product taxonomy, routing and four product-boundary tests")
    # Demonstrate why qualification-to-send p90 alone can conceal the delay
    # from the first relevant complaint: these are SYNTHETIC timestamps,
    # not real support data or historical reconstructed ingested_at values.
    first = datetime.fromisoformat("2026-10-26T09:00:00+00:00")
    qualified = datetime.fromisoformat("2026-10-30T09:00:00+00:00")
    sent = datetime.fromisoformat("2026-10-30T09:05:00+00:00")
    assert first <= qualified <= sent
    assert (sent - qualified).total_seconds() == 5 * 60
    assert (sent - first).total_seconds() == 96 * 3600 + 5 * 60
    release = read("docs/evaluation/release-gates.md")
    for x in ("first_relevant_ingested_at", "Timely product decision rate",
              "96 h 5 min"):
        assert x in release, f"Missing release-gate evidence: {x}"
    for x in ("first_relevant_ingested_at", "End-to-End Insight Delay",
              "96 ч 5 минут", "Timely product decision rate",
              "undelivered/eligible"):
        assert x in metrics, f"Missing KPI explanation: {x}"
    print("PASS: distinct 5-minute delivery TPI vs 96h05 synthetic end-to-end "
          "discovery time; unknown clock and delivery selection caveats retained")

    # Independent 5-block workload regression based on explicitly hypothetical
    # inputs; never treat these numbers as measured corporate model capacity.
    capacity = json.loads(read("docs/architecture/per-service-capacity-scenario.json"))
    x = capacity["inputs"]
    exp = capacity["derived_expected"]
    q = x["support_managers"] * x["illustrative_tickets_per_manager_day"]
    active_hours = x["active_hours_per_day"]
    peak_hourly = q / active_hours * x["peak_factor"]
    peak_seconds = peak_hourly / 3600
    utilization = x["target_utilization"]
    assert x["support_managers"] == 40
    assert q == exp["tickets_per_day"] == 800
    assert q / active_hours == exp["tickets_per_hour_over_active_shift"]
    assert peak_hourly == exp["tickets_per_hour_at_assumed_peak"] == 300
    assert math.isclose(peak_seconds, exp["tickets_per_second_at_assumed_peak"])
    audio_minutes = q * x["illustrative_call_fraction"] * x["illustrative_audio_minutes_per_call"]
    asr_slots = math.ceil(
        audio_minutes * x["illustrative_asr_rtf"] * x["peak_factor"] /
        (active_hours * 60 * utilization)
    )
    assert audio_minutes == exp["audio_minutes_per_day"] == 720
    assert q * x["illustrative_call_fraction"] == exp["calls_per_day"] == 240
    assert asr_slots == exp["asr_peak_worker_equivalents"] == 4
    img_daily = q * x["illustrative_image_ticket_fraction"] * x["illustrative_images_per_eligible_ticket"]
    img_peak_hour = img_daily / active_hours * x["peak_factor"]
    img_slots = math.ceil(img_peak_hour * x["illustrative_vl_service_seconds_per_image"] / (3600 * utilization))
    assert img_daily == exp["image_inputs_per_day"] == 160
    assert img_peak_hour == exp["vl_peak_images_per_hour"] == 60
    assert img_slots == exp["vl_peak_concurrency_equivalents"] == 1
    text_peak_hour = peak_hourly * x["illustrative_text_inference_per_ticket"]
    text_slots = math.ceil(text_peak_hour * x["illustrative_text_service_seconds"] / (3600 * utilization))
    assert text_peak_hour == exp["text_inference_peak_per_hour"]
    assert text_slots == exp["text_peak_concurrency_equivalents"] == 2
    assert math.isclose(text_peak_hour * x["illustrative_input_tokens"] / 3600,
                        exp["text_input_tokens_peak_per_second"])
    assert math.isclose(text_peak_hour * x["illustrative_output_tokens"] / 3600,
                        exp["text_output_tokens_peak_per_second"])
    assert math.isclose(peak_seconds * x["illustrative_retrieval_queries_per_ticket"],
                        exp["retrieval_queries_peak_per_second"])
    assert math.isclose(peak_seconds * x["illustrative_db_writes_per_ticket"],
                        exp["db_write_ops_peak_per_second"])
    digest_peak_hour = x["illustrative_daily_advisory_digests"] / active_hours * x["peak_factor"]
    assert math.isclose(digest_peak_hour, exp["hypothetical_digests_peak_per_hour"])
    assert math.isclose(digest_peak_hour / 3600, exp["digests_peak_per_second"])
    assert all(t in main for t in ("0,0093/с", "0,0278/с", "0,0833/с",
                                   "720 аудиомин", "4` ASR-слота", "2 конкурентных слота",
                                   "0,25 write/s", "7,5/пиковый час"))
    assert "slots ≠ число GPU" in main
    capacity_doc = read("docs/architecture/per-service-capacity-analysis.ru.md")
    assert "проектный сценарий" in capacity_doc
    assert "НЕ" in capacity_doc
    print("PASS: five logical service workloads independently recalculated "
          "from tagged hypothetical inputs (ingest/ASR/VL/Qwen/BM25/DB/outbox)")

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
        # Full detail lives in the audited finance worksheet. The capped
        # standalone contest answer includes gross annual value and 3-year PV.
        for amount in ("expected_gross_annual_rub", "expected_gross_three_year_rub",
                       "expected_pv_realizable_rub"):
            shown = thousands(scenario[amount])
            assert shown in finance, f"finance missing {scenario['id']}: {shown}"
            if amount != "expected_gross_three_year_rub":
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
    # Contest example #5 is only ONE source narrative. The three additional
    # ticket IDs must remain visibly synthetic, not invented Webneft facts.
    business_story = read("docs/case-studies/webneft-synthetic-product-insight.md")
    slide_storyboard = read("submissions/presentation-outline.ru.md")
    blocks = re.findall(r"```json\s*([\s\S]*?)```", business_story)
    assert len(blocks) == 1, "Expected one demonstrative insight JSON"
    insight = json.loads(blocks[0])
    assert insight["synthetic"] is True
    assert insight["product_id"] == "webneft"
    assert insight["observed_unique_ticket_count"] == len(set(insight["evidence_refs"])) == 3
    assert all(ref.startswith("SYN-QUEUE-") for ref in insight["evidence_refs"])
    assert insight["coverage_status"] == "unknown_coverage"
    assert insight["root_cause_status"] == "unknown"
    assert insight["trend_status"] == "not_assessable"
    assert insight["delivery_status"] == "draft_not_sent"
    assert insight["feedback_status"] == "pending"
    assert "синтетических" in slide_storyboard.lower()
    assert "Webneft" in slide_storyboard and "10 слайдов" in slide_storyboard
    print("PASS: synthetic end-to-end insight has exactly 3 invented IDs, "
          "no real recurrence/causal/delivery claims")
    # Defense notes must match the 10-slide deck without presenting demo
    # counts, pilot targets, or financial scenarios as observed outcomes.
    speech = read("submissions/jury-defense-script.ru.md")
    q_and_a = read("submissions/jury-questions-answers.ru.md")
    slide_headings = re.findall(r"(?m)^## Слайд (\d+) —", speech)
    assert slide_headings == [str(i) for i in range(1, 11)], slide_headings
    questions = re.findall(r"(?m)^### (\d+)\.", q_and_a)
    assert questions == [str(i) for i in range(1, 23)], questions
    assert "официальном PDF не указан фиксированный регламент" in speech
    assert "полностью синтетический" in speech.lower()
    assert "SYN-QUEUE" in business_story and "синтетическ" in q_and_a.lower()
    assert "не реальные три тикета" in q_and_a.lower() or "полностью синтетические" in q_and_a.lower()
    for term in ("BM25", "Qwen-ASR", "Qwen-VL", "qualified_at", "0,80", "0,95",
                 "123", "1,64", "7,39", "baseline", "ROI"):
        assert term in speech + q_and_a, f"Defense materials lack {term}"
    assert "внешние" in q_and_a.lower() and "Webneft" in business_story
    assert "Intelligence_Cup_2026_GazpromNeft_Final_Presentation_Candidate.pptx" in speech
    assert "Intelligence_Cup_2026_GazpromNeft_Final_Presentation_Candidate.pptx" in q_and_a
    assert "Jury_Review_v2.pptx" not in speech + q_and_a
    for term in ("300", "4 ASR", "1 VL", "2", "слотов", "96 часов",
                 "qualified_at", "first_relevant_ingested_at"):
        assert term in speech + q_and_a, f"Final-deck oral defense missing {term}"
    assert "docs/reviews/2026-10-31-jury-red-team-final-deck.md" not in speech
    organizer_draft = read("docs/submission/organizer-eligibility-and-upload-inquiry.ru.md")
    assert "аспирантуры" in organizer_draft and "срок" in organizer_draft.lower()
    assert "не отправленное" in organizer_draft
    print("PASS: jury defense cites final 10-slide artifact, hypothetical capacity "
          "and synthetic two-clock KPI; organizer inquiry explicitly unsent")
    print("PASS: defense script covers slides 1..10 and 22 jury questions; "
          "uncertainty, synthetic case and scenario warnings documented")
    print("PASS: official case contract, 1–4 + 6, separate 5,",
          f"main={len(main)} chars, seven unadjudicated examples, ten slides")


if __name__ == "__main__":
    verify()
