# PDF-first Full Audit: Gazprom Neft scope vs Webneft examples

**31 October 2026 — independent-of-code source review; author review, not independent human approval.**
**Primary evidence:** original organizer PDF `Кейс_Искусственный интеллект.pdf`, pages 1–7, read directly. Previous DeepSeek Webneft research is secondary and MUST NOT override the PDF.

## Verdict
**Critical correction:** the proposed agent serves **many internal and external digital products of Gazprom Neft**, NOT only the Webneft B2B marketplace. **Webneft is one example product** with seven sample support requests (p6). Neither the PDF nor the examples make Webneft a mandatory deployment target or constrain other product taxonomies to fuel/logistics.

## Traceability checklist: exact PDF fact → consequence

| Page | Verified statement | What the solution must do | What would be an unsupported claim |
|---|---|---|---|
| p1–2 | Dozens of internal/external digital products, existing support→product communication, insufficient attention to repeated noncritical requests/wishes | Product-independent ingestion, per-product classification/routing, evidence-linked product digests, human feedback | "Only Webneft" or "the current process is entirely manual" |
| p2 | Q1 architecture, Q2 agent tools, Q3 annotated prompt, Q4 testing/acceptance | Self-contained technical proposal with boundaries and tests | "Real company APIs already implemented" |
| p3 | Q5 retrospective/future metrics; Q6 translate effects to money and discuss 3-year payback | KPI .md with baseline plan; honest three-year scenario and conditional break-even | Achieved accuracy/ROI, fabricated manual reporting times |
| p4 | ~40 support managers **across all products covered by the future agent** | Company-scope scenario N≈40, NOT 40 Webneft staff or real ticket throughput | "Webneft has 40 support agents" |
| p4 | Calls with recordings and tickets with file/images, one shared ticket system stored 1 year | Multi-modal processing and permission/retention boundary | Product-specific unknown ticket APIs or 1-year derived storage policy |
| p4 | No external API/LLM; internally deployed `Qwen 3.8`, Qwen-ASR, Qwen-VL; internal use/server cost exempt | Local-only model adapters, strict egress block, uncertain exact text-model interface | Cloud OpenAI/Anthropic, vendor login, assumed Qwen3-8B |
| p4 | Expense-side money calculation not required, though complexity and payback matter | Revenue/benefit scenarios and cost **threshold**, not invented installation budget | Guaranteed ROI/zero implementation cost |
| p5 | Main answer Q1–4,6 ≤15k chars DOC/DOCX/PDF, Q5 separately .md, ~10 slides; no appendix links to evade cap | Final deliverables standalone, visually checked | GitHub README as mandatory submission |
| p6 | **Seven support examples of one product Webneft**, B2B small wholesale fuel ordering; calls on similar topics | One clearly labeled Webneft worked example, seven tickets unadjudicated; no shared-incident labels | Extend Webneft's exact domain enum to all Gazprom products |
| p7 | Technical microservice decomposition+load, justified metrics/fallback, alternative investments/macro sensitivity, presentation clarity | Capacity scenarios, feedback process, strong evaluation, concise slides | Fake current RPS, current Russian inflation, measured Qwen accuracy |

## Coverage/reasoning gap assessment, severity

| Severity | Finding | Correction |
|---|---|---|
| **P0** | README, architecture spec, old binary slide/footer presented **WEBNEFT** as overarching solution identity | Rename to company-wide **ИИ-агент для ретрансляции обращений цифровых продуктов «Газпром нефти»**; explicitly `Вебнефть — один иллюстративный кейс` |
| **P0** | Text Qwen prompt and output schema hard-code Webneft-only `business_journey` enum | Backend sets and authorizes product_id + taxonomy version; Qwen chooses from **that product's** allowlist; if unknown => `unknown` / human route. No cross-product retrieval by default |
| **P1** | Multi-product routing/inference and no-products-configured fallback insufficiently prominent | Authoritative `product_id→team`, per-product tenant/source boundaries, source completeness per product; no invented owner |
| **P1** | KPI needs per-product slices as well as aggregate outcome and transparency about eligible/unsent items | Product/channel-specific p90, precision, delivery, routing coverage, staff time and cohort-mix reporting |
| **P1** | 40 support staff + finance can be misunderstood as Webneft-only benefit | Clarify ~40 personnel over agent's covered product scope, scenario workload assumption and `k` realizability |
| **P1** | Seven sample tickets can be overinterpreted as same-incident/recurrence ground truth | Continue one-ticket-one-count, `unknown` root cause, no historical recurrence labels, Webneft only illustration |
| **P1** | Old session DOCX/PDF/PPTX exported editorially apart from GitHub Markdown source | Re-export and verify final artifact, update GitHub text source; if binaries remain off GitHub disclose source/export difference |
| **P2** | Some diagrams use single `product_id` implicitly, without showing per-product routing | Show logical product scope explicitly, not one Webneft data path only |
| **P2** | Model phrase `Qwen 3.8` ambiguous | Quote exactly as in PDF, version/endpoints not invented |

## Correct proposed multi-product contract

```text
TrustedConfig {
  scope_id, product_id, taxonomy_version,
  allowed_business_journeys[], allowed_symptom_codes[],
  permitted_source_systems[], product_to_team_registry_version,
  routing_policy_version
}

LLM RequestAnalysisV1 {
  business_journey: allowed_for_product | "unknown",
  request_intent: global_enum, symptom_codes: allowed_for_product[],
  relation_type: candidate_only | unrelated | insufficient_evidence,
  root_cause_status: "unknown", evidence_refs: trusted_aliases[]
}
```

The trusted envelope is assigned by backend and is not editable by the LLM/ticket text. Retrieval and recurring-signal aggregation partition by `scope_id+product_id` by default. A cross-product view would need explicit approved normalized taxonomy, data-sharing permissions and independent evaluation, not an unrestricted join.

**Webneft example (PDF p6):** contract mismatch and unresponsive button share journey but do not prove common bug; vehicle invisible/already-exists is one ticket with two descriptions; 404/no slot is one ticket; urgent contact-change remains regular support SLA; account/OTP requests cannot expose credentials. No source timestamps, identical incident labels or root causes provided.

## Release/submission gates
- [ ] Main Russian narrative clearly company-wide, <15k Unicode text chars, covers 1–4,6 standalone.
- [ ] Q5 separate `.md` and company-wide KPI slicing/correct denominators.
- [ ] Prompt/tool schema dynamically product-scoped, second **synthetic** product test case and unknown product rejection.
- [ ] Ten editable slides frame Gazprom Neft scope; Webneft only p6 demo slide.
- [ ] Docs + slides rendered and independently checked, finance scenarios cross-file consistent.
- [ ] GitHub CI on current HEAD, record limitations, independent human content review before submission.
- [ ] No runtime code, no live Qwen/customer data, no merge/deploy.
