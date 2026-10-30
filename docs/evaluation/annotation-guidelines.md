# Protocol: independent human labels for Webneft V2

**Status:** proposed evaluation protocol, not a performed experiment. **Primary source:** official 7-page Intelligence Cup PDF, pages 2–4, 6–7. The seven cases in the PDF are **unadjudicated illustrations**, not gold positive pairs or recurring observations. Derived data must respect company authorization and the one-year retention of source records; derivative retention must be approved separately.

## 1. Corpus construction and sampling frame

1. **Before reading data:** obtain source owner approval, documented purpose, roles, Russian PII/secret handling and a retention schedule. Access remains within corporate network; use internal-only Qwen/Qwen-ASR/Qwen-VL. Raw call audio/screenshots are sensitive before transcription/OCR and must stay in a restricted processing zone.
2. Inventory all **products** and both **channels** (calls + ticket forms/attachments), source update semantics, deleted records, source-created vs first-observed clock, known coverage/ingestion watermarks. Do not silently treat an unreachable system as an empty bucket.
3. Use **source-scoped ticket identity** `(source_system, source_ticket_id)`; one ticket with two symptoms or ASR chunks still counts as one ticket. Distinct organization counting requires separately consented pseudonymous linkage and definition.
4. Obtain a permitted retrospective sample covering time windows, product types, channels, issue ages, rare topics and straightforward/ambiguous items. Selection of a **reviewed-only** dataset introduces bias; supplement with a random sample of incoming traffic, including records AI would abstain on and records not forwarded to a product team.
5. Avoid exposing original personal names, phone numbers, passwords, OTP, orders or contract content in annotation files or a public GitHub repo. Store only permitted sanitized excerpts, source references and hashed audit pseudonyms.

## 2. Independent annotation axes, not a single incident label

| Label | Definition | Typical classes / cardinality | Negative/inconclusive rule |
|---|---|---|---|
| `request_intent` | Why the user contacted support | `bug_report,question,feature_request,service_request,unknown` | Operational contact change ≠ automatically software bug |
| `business_journey` | The business step that was interrupted | `contract_onboarding,vehicle_management,shipment_operation,electronic_queue_booking,account_access,other,unknown` | Journey ≠ technical root cause |
| `symptom_code` | An **observed user symptom**, never diagnosis | Versioned taxonomy; can be multilabel | Two symptoms in one ticket don't create two independent calls |
| `same_problem_pair` | Does this specific pair describe a sufficiently matching symptom warranting joint review? | `candidate_same_symptom,related_topic_only,unrelated,insufficient_evidence` | Similarity and A~B, B~C **do not** prove A~C or common root cause |
| `actionable` | Would a product team consider this useful to investigate/improve? | `yes,no,needs_info` | Not synonymous with resolved incident or model confidence |
| `product_route` | Which team should receive the advisory report? | Authoritative team registry ID / `needs_human` | Do not invent owner based on wording |
| `urgency` | Does existing urgent support workflow need to act now? | `normal,operational_deadline,security_sensitive` | Urgent ticket bypasses analytic clustering delays |

**Important:** `same_problem_pair` is a *review candidate* label; independently confirmed common backend root cause would require additional logs/technical investigation. `root_cause_status` is **unknown** for PDF cases. `business_topic` may be grouped across different root causes without calling them one incident.

## 3. Gold process and disagreement resolution

- Two independent domain-capable annotators label every evaluation case **blind** to model output and prior reviewer choices. Provide a fixed taxonomy glossary + source evidence, randomize display order, make uncertain response permissible.
- One adjudicator resolves disagreements while preserving original A/B labels, final arbitration reason and taxonomy version. If experts cannot agree, mark `insufficient_evidence`, not artificial correctness.
- Assess agreement per label (e.g., percentage agreement / Cohen's kappa when appropriate) but never infer calibrated reliability from the 7 illustrative PDF examples.
- Construct pair evaluation from both similar/same-journey and hard negative pairs; include random negatives. Record actual pair prevalence of the sampling frame; otherwise pairwise precision/recall is not extrapolatable.
- Temporal holdout: train/tune on earlier periods and evaluate later arrivals as they would have appeared at decision time; avoid correlated near-duplicates across partitions, organization leakage and future event-time features. Use `ingested_at` recorded at first observation, never future `source_created_at` if unavailable.
- Separate primary slices by channel, product, issue intent, language, low-frequency topic and unavailable model/media. Report sample sizes, exclusions, CI and `unknown_coverage` in each slice. Rare classes may only permit qualitative results.

## 4. Source-specific acceptance examples (not pre-labeled truth)

| PDF item | What a reviewer can assert | What must remain unknown |
|---|---|---|
| #1 vs #2 | Both address contract onboarding with **distinct** observable symptoms | Whether they originate from one defect |
| #3 | Vehicle missing + already-exists message belong to **one user report** | Cache/database synchronization diagnosis |
| #4 | Contact correction before scheduled loading is an **operational service request** | Whether product self-service is technically absent |
| #5 | HTTP 404 / unavailable time in queue booking is **one** described report | Booking API race cause, real recurrence |
| #6 vs #7 | Both involve account access, but identity recovery vs SMS-code symptom differ | Same technical root cause; credential access |
| All seven | No authentic source timestamps, counts, product team routing or adjudicated labels in the PDF | Classifier accuracy, recall, ROI, or delivery improvement |

## 5. Metrics and aggregation rules

- Report **macro F1 per intent/journey** + per-class support and confusion matrix; do not hide `unknown`/abstentions. Multi-label symptom scoring needs per-label precision/recall.
- Pairwise detection: precision/recall on adjudicated candidate pairs, plus **false merge rate** when decisions would cause linking; no transitive union.
- Actionability: `accepted / (accepted + rejected + needs_info + missing_feedback)` for sent insights *if* treating missing as not confirmed, plus separate `accepted / reviewed` **conditional** metric; report denominator and maturity window. Never present review-only acceptance as population precision.
- Coverage: `coverage = independent audited source/time strata with valid watermark / expected strata`. If denominator of expected strata unknown, report **not assessable** and a lower bound for observed tickets, not unqualified trend.
- Confidence intervals: use stratified bootstrap by organization/product/time block as appropriate; if sample is too small, say `not estimable`. Do not set a hard statistical target from seven examples.
- Business primary metric: p50/p90 `qualified_at → sent_at` for comparable insights; `qualified_at` must be demonstrably when minimum evidence became available *to that workflow*. If historic data lacks this clock, use a clearly labeled proxy (e.g. first ingest→ack) and never compare a proxy with the new metric as if identical.

## 6. Review and release governance

A quality evaluator cannot use the same generated insight to create its own correct labels. Product team feedback informs usefulness but **not independently ground truth for every unreviewed item**. Freeze annotation rubric before evaluation. Record sampling design, missingness, reviewed proportions, baseline rules/BM25, Qwen model version and policy version.

**Approval gates (not completed):** source owner+privacy policy, independent annotators and adjudicator, held-out metrics with CI, stress tests and business acceptance. No real-company test corpus or Qwen run has been accessed for this design.
