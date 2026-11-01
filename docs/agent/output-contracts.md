# AI Agent V2 — строгие выходные контракты (proposal, не действующие API)

**Primary source:** case PDF стр. 2–4, 6; **сфера охвата — многие цифровые продукты**, Webneft только один набор иллюстраций; **Architecture chosen:** Hybrid C. До внедрения проверить фактический интерфейс и точное название модели «Qwen 3.8». Классификатор получает **только очищенный внутренний контекст**, не получает прав на выдачу паролей, статистических counts и внешнюю сеть.

## Contract 1 — `RequestAnalysisV1` (model suggestion)

`product_id` and `taxonomy_version` are **trusted request envelope metadata, not model-generated output**. The backend must validate the product mapping and taxonomy selection before presenting the allowlist to Qwen.

```json
{
  "schema_version": "request-analysis-v1",
  "business_journey": "electronic_queue_booking",
  "request_intent": "bug_report",
  "symptom_codes": ["booking_404_or_slot_missing"],
  "relation_type": "insufficient_evidence",
  "root_cause_status": "unknown",
  "recommended_action": "investigate",
  "evidence_refs": ["E1"],
  "abstain": false,
  "abstain_reason": null,
  "needs_human_review": false
}
```

Allowed values:
- `business_journey`: **код из утверждённого для данного `product_id` справочника** или `unknown`; Webneft example codes: `contract_onboarding`, `vehicle_management`, `shipment_operation`, `electronic_queue_booking`, `account_access`. Эти коды **не** являются глобальным enum для всех цифровых продуктов;
- `request_intent`: `bug_report`, `question`, `feature_request`, `service_request`, `unknown`;
- `symptom_codes`: allowlisted taxonomy **для доверенного `product_id + taxonomy_version`**, empty when unknown; never invent a new database/API symptom.
- `relation_type`: `same_problem_candidate`, `related_topic_only`, `unrelated`, `insufficient_evidence`. **No** `same_incident_confirmed`.
- `root_cause_status`: literal `unknown`; hypotheses, if separately allowed in an editorial description, are not facts. No `root_cause`, `owner_team_id`, `incident_id`, numerical `confidence` fields.
- `recommended_action`: `investigate`, `review_ux`, `answer_faq`, `route_service`, `none`. It's **suggested**, backend applies policy.
- `evidence_refs`: reference aliases **provided in trusted envelope only**, e.g. `E1` and `E2`. Backend validates each against permission-checked `source_ticket_keys`. A model-created `E42` when only E1 exists fails.
- `abstain_reason`: `insufficient_context`, `source_unavailable`, `sensitive_request`, `schema_failure`, or null. If `abstain=true` this field must be one of four reasons and action must be `none`.
- `needs_human_review`: Boolean suggestion. Backend can **escalate** irrespective of its value; model cannot set `false` to bypass human review.

## Contract 2 — `ProductSignalV1` (trusted aggregator output, NEVER model-authored)

```json
{
  "schema_version": "product-signal-v1",
  "signal_id": "SYN-QUEUE-OBSERVED-2026-10-01",
  "product_id": "webneft",
  "business_topic": "electronic_queue_booking",
  "observed_unique_ticket_count": 2,
  "window_start_utc": "2026-10-01T00:00:00Z",
  "window_end_utc": "2026-10-02T00:00:00Z",
  "evidence_ticket_keys": ["SYN-BOOKING-001", "SYN-BOOKING-002"],
  "source_coverage": "unknown_coverage",
  "trend_status": "not_assessable",
  "causal_claim_status": "unknown",
  "route_status": "needs_human",
  "delivery_status": "draft"
}
```

**All sample identifiers/timestamps are fabricated for demonstrating JSON syntax, not historical company data.** Under `unknown_coverage` it's acceptable to say “2 observed tickets in the accessible sample”, *not* “2 in the whole system”, “higher than last month” or “the same backend incident”. Count unique source records; if one call yields several transcript segments, it still counts as one request.

`trend_status`: `not_assessable`, `stable_observed`, `increase_observed`; latter two require an explicit data-completeness/quality policy and consistent windows. `source_coverage`: `complete` only with a trusted source manifest/watermark; no inference from records found.

## Contract 3 — `ProductDigestV1` (internal policy-approved advisory)

```json
{
  "schema_version": "product-digest-v1",
  "draft_id": "SYN-DRAFT-001",
  "target_team_ref": "TEAM_FROM_TRUSTED_REGISTRY",
  "evidence_ticket_keys": ["SYN-BOOKING-001", "SYN-BOOKING-002"],
  "observed_unique_ticket_count": 2,
  "coverage_note": "unknown_coverage: count is observed minimum only",
  "headline": "Повторяющиеся сообщения о проблеме электронной очереди (предварительно)",
  "proposed_action": "Проверить пользовательский путь бронирования",
  "root_cause_status": "unknown",
  "human_status": "unverified",
  "delivery_policy_id": "APPROVED_INTERNAL_ADVISORY_POLICY",
  "external_delivery": false
}
```

**Synthetic demonstration.** `target_team_ref` must be resolved from the authoritative internal routing map; in real use if unknown, don't publish. `delivery_policy_id` must exist and be approved; do not allow the model to invent this identifier. The draft may be sent only within an approved internal channel when risk/coverage rules permit, otherwise held for human triage. Approval of *information delivery* is not automatic confirmation of a common technical defect.

## Boundaries and validation gates

1. Model JSON parsed with strict schema (`extra=forbid`, enum, size/time budgets, unique evidence aliases, no duplicate JSON keys); unexpected JSON/executable markup/embedded instruction rejected.
2. Trusted envelope gives `tenant_scope`, **backend-authenticated product_id, product-specific taxonomy_version and allowed_journey/allowed_symptom code lists**, exact allowed E1..En→source mapping; IDs in the output are validated by backend. Qwen never self-grants access.
3. Time windows are half-open UTC intervals `[start,end)`; if `source_created_at` absent, don't invent it. `ingested_at` is recorded by our service on actual observation, not filled from PDF.
4. **Cross-product safety:** retrieval and aggregation are partitioned by `scope_id + product_id` by default; an unconfigured product/taxonomy/owner requires abstention/human triage. Webneft ontology must never be applied to unrelated digital products. Independent `ProductSignalV1` aggregation with verified source scope, dedup, watermark and exact counts. Failure to retrieve one data page is **unknown coverage**, not an empty success.
5. If user asks to reveal login/password/OTP or modify a shipment/contact record: refuse as automated AI action and route to existing authorized support; **no autonomous business mutation**.
6. Product routing and policy controls are checked by server, not a string returned by LLM. Audit `model_version`, `taxonomy_version`, `policy_version` and event timestamps without leaking PII.
7. Signed, authorized product-team feedback alone changes accepted/rejected/needs_info state. LLM does not cast human votes or assert product improvements completed.
8. Example output is a **design contract**, not a tested response from a real Qwen endpoint.
