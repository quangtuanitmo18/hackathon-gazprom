# Webneft Intelligence Cup V2 — Evidence-First Product Feedback Agent

**Status: APPROACH C (Hybrid evidence-first, internal Qwen + deterministic tools) APPROVED BY USER on 2026-10-31.** Detailed diagram boundaries, tool interfaces, thresholds and business assumptions remain proposed pending review; this does **not** approve app implementation, merging, deploying or live data use.
**Inputs:** official 7-page case PDF (primary), 7 user-ticket descriptions (PDF p. 6), user-provided DeepSeek analysis (secondary), [evidence audit](../../research/deepseek-webneft-evidence-audit.md) with dated historical public sources. **Do not mistake an old article or DeepSeek root-cause guess for confirmed current Webneft product behavior.**

## Intent and constraints

**Business goal:** detect recurring *questions, enhancement wishes, non-critical friction* from support and quickly deliver an actionable, evidence-backed digest to the appropriate internal product team without additional support-staff reporting burden. Failure means building an elaborate incident tracker or classifier whose product team never uses its reports.

**PDF facts:** ~40 support managers across products (not RPS); one ticket system storing call recordings, tickets and attachments for ~1 year; internal models recorded as **“Qwen 3.8”, Qwen-ASR, Qwen-VL** with unspecified endpoints/version; **no external LLM or external API calls**; financial model does not need to price internal inference, but implementation complexity is a real tradeoff. Seven Webneft examples are narrative illustrations and **not** same-incident ground truth.

**Submission contract:** main Russian DOCX/DOC/PDF answering items 1–4,6 ≤15,000 chars; mandatory item 5 a separate `.md`; ~10 slides; optional honest AI Footnotes. These are the primary deliverables. Source code is optional.

## Approaches explored (decision proposed, pending approval)

| Option | Merit | Fundamental weakness |
|---|---|---|
| A — Rule/taxonomy + BM25 + scheduled digest | Fast, explainable, offline; safe demo baseline | Poor semantic recall for Russian paraphrases, calls, cross-product jargon |
| B — LLM-only single autonomous agent | Minimal hand-tuned rules; rich text summaries | Hallucinated counts/owners/root cause; weak replay/audit, prompt-injection surface, high inference dependence |
| **C — Hybrid evidence-first workflow (recommended)** | Internal Qwen for narrow interpretation; trusted aggregation/permissions/routing/delivery; measured baseline; graceful fallback A | A few clear services/tools and golden labels required |

**Chosen design:** C, confirmed by the user on 2026-10-31; A remains the offline fallback and benchmark. It must outperform or complement A on adjudicated labels; otherwise do not spend cost on model calls.

## Minimal architecture (logical boundaries, not compulsory microservices)

1. **Ingestion adapter (I/O-heavy):** read-only incremental snapshot/cursor from single company ticket DB; idempotent `(source_system, source_ticket_id)`; safely resolve permitted audio/images; preserve provenance and `source_created_at` vs `ingested_at`; handle late updates/deletes/1-year source retention; never silently treat partial scrape as full completeness.
2. **Multimodal workers (accelerator-heavy):** internal Qwen-ASR for permitted phone recordings, Qwen-VL for attachments if text extraction is needed; store only minimized derived text and pointers where permitted. Since audio/image bytes can contain PII *before* transcription, the internal boundary and retention apply at the very first step; redact/minimize derived content before passing it to the text model.
3. **Intelligence service (CPU/model-bound):** strict `RequestAnalysisV1` schema with independent axes `business_journey`, `request_intent`, `symptom_code`, `relation_type`, `urgency`, `root_cause_status=unknown`; confidence only if calibrated, otherwise `abstain`. Local Qwen suggests classification, deterministic code verifies ids/time/products; BM25 baseline retained as comparator, not automatic transitive incident merger.
4. **Signal aggregator / routing (mostly DB and queue):** count distinct source tickets by topic/symptom/time window, not fragments of the same call or multi-symptom ticket. Unknown source coverage => `unknown_coverage` / no extrapolation. Compute robust `observed_at`/watermark for online measurement. Resolve product owner only from authoritative registry; unknown route => human triage.
5. **Delivery/feedback (reliability-sensitive):** evidence-linked internal digest via durable transactional outbox (idempotency key `scope+signal+window+revision`), ack, feedback from team `accepted/rejected/needs_info/in_progress/resolved`. Policy-safe advisory digest may be sent automatically **inside** approved enterprise channel with `candidate/unverified` label; risky actions, secrets, urgent operational cases go to authenticated human process. No autonomous customer-account changes, OTP/password recovery, or external tracker writes.
6. **Evaluation/observability:** provenance-backed events, p50/p90 `qualified_at→sent_at` time, actionable precision, topic recall, routing, manual support reporting minutes, false grouping, delivery retry and feedback closure; baseline needs separate study.

**Deployment framing:** one modular Python API/worker application with PostgreSQL and a durable internal queue is enough for concept/MVP; a separate ASR/VL worker pool is justified by independent accelerator/compute needs. Extra physical microservices only after quantified load and failures. No fabricated production QPS.

## Canonical contracts (design, not implemented yet)

```text
SupportEventV1 {
  scope_id, source_system, source_ticket_id, product_id,
  source_created_at?, ingested_at!, channel: ticket|call,
  sanitized_text_ref?, attachment_refs[], source_hash,
  pii_policy_version, provenance_ref
}
RequestAnalysisV1 {
  ticket_key, product_id, business_journey, request_intent,
  symptom_code, relation_type, urgency,
  root_cause_status: "unknown", evidence_refs[],
  human_review_required, label_status: proposed|adjudicated
}
ProductSignalV1 {
  signal_id, product_id, business_topic, symptom_codes[],
  window_start, window_end, observed_unique_ticket_count,
  source_coverage: complete|unknown_coverage,
  evidence_ticket_keys[], routing_status: resolved|needs_human,
  candidate_status: unverified|human_confirmed
}
ProductFeedbackV1 {
  signal_id, reviewer_role, decision:
    accepted|rejected|needs_info|in_progress|resolved,
  decision_at, evidence_refs[], reason_sanitized?
}
```

Fields are **proposed**, not claimed existing in Webneft. Source `ingested_at` is captured on our side when the record is observed, and is not an invented retroactive field in the company's DB.

## Webneft taxonomy examples and non-inferences

| PDF # | Journey | Intent (proposed) | Symptom | Important negative |
|---|---|---|---|---|
| 1 | contract_onboarding | bug_report | legal_entity_form_mismatch | Cause of ИП vs ООО not established |
| 2 | contract_onboarding | bug_report | next_button_unresponsive | Related topic to #1, **not proven same incident** |
| 3 | vehicle_management | bug_report | vehicle_not_visible_already_exists | Cache / primary key causes **unproven** |
| 4 | shipment_operation | service_request | contact_change_requested | Deadline-based human routing; **not necessarily bug** |
| 5 | electronic_queue_booking | bug_report | booking_404_or_slot_missing | **One ticket, not two bugs counted**; no API trace |
| 6 | account_access | service_request | existing_contract_access | Never reveal an old password or account credentials |
| 7 | account_access | bug_report|question (uncertain) | sms_reset_code_missing | SMS provider failure **unproven** |

## Trust, security and failure model

- **Read only** source systems by default; no shared prod credentials or blind file download. Provenance & tenant scope enforced by backend; untrusted ticket/transcript/OCR text never gives executable tool instructions.
- No external LLM/API calls; internal Qwen endpoints require explicit access approval. **Text-model string “Qwen 3.8” must remain unresolved until checked**; cannot silently substitute another Qwen release.
- Original audio/images may carry PII; use corporate controls from ingest time, minimize/redact before text-model prompting; do not claim `scrubadub` alone sufficient for Russian PII or secrets.
- If ASR/Qwen unavailable: queue/retry with backoff and human-support unchanged; fallback deterministic topic/keyword shortlist and `needs_review` status, not fabricated complete insights.
- If product routing unknown or source coverage insufficient: draft or abstain, never invent recipient, counts or velocity.
- Internal digest is not an incident declaration. Human review gate is **risk-based**; a globally mandatory 2-reviewers+lead barrier would oppose the business goal of no extra support workload.
- No TTAI/ROI claim without historical arrival-time and measured baseline, no accuracy claims from 7 case examples or synthetic data.

## Quality & measurable acceptance (proposals, not measured outcomes)

1. Every emitted signal's source keys resolve and show distinct tickets and matching product/tenant; no duplicate count for one call's multiple transcript segments.
2. Identity, time window, `created_at vs ingested_at`, and source coverage validated by code; future/unknown values cannot appear as observed fact.
3. Safe fallback on malformed model JSON or prompt injection, and no unauthorized external egress.
4. Correct internal product routing or explicit human fallback; exactly-once *effect* for internal digest through idempotent outbox and retry.
5. Independently adjudicated topic / actionable labels and time-based holdout. Proposed initial pilot thresholds, subject to negotiation: actionable precision ≥0.80; routing accuracy ≥0.95; p90 qualified→sent ≤4h for async digest, **no degradation** in urgent support SLA. Recurring recall threshold only after establishing gold set.
6. Financial value scenarios show freed support hours with adoption and wage assumptions, separated from actual cash savings and unobserved ROI.

## User decision / design approval

**Decision recorded:** user chose hybrid option C and confirmed no app/runtime code is required for the contest. Focus first on mandatory docs, source diagrams, KPI and slides on clean V2 branch. Any later demo/code needs its own explicit scope decision. Details are still design proposals, not production authorization. No external model/data access is implied.

## References
- Primary: official `Кейс_Искусственный интеллект.pdf`, pages 1–7, user-uploaded.
- Secondary: [DeepSeek historical/current evidence audit](../../research/deepseek-webneft-evidence-audit.md).
- Submission rubric trace: [PDF traceability](../../requirements/pdf-traceability.md).
- Existing V2 [7 unadjudicated cases](../../../data/webneft/case-examples.json).
