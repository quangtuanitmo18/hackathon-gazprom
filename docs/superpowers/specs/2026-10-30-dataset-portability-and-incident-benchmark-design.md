# Dataset-portable Incident Intelligence — Design Specification

**Date:** 2026-10-30  
**Status:** ACCEPTED AS WORKING DIRECTION by repository owner ("continue"), subject to detailed team review  
**Parent:** [ProductPulse system architecture](2026-10-30-productpulse-system-design.md)  
**Existing evidence:** [Verified Zenodo and Mendeley originals](../../data/source-verification-report.md)  
**Decision:** Use the existing **Hybrid AI Agent** approach and build strict, replaceable source adapters.

## Why this matters

The organizer has not supplied a Gazprom Neft dataset yet. Build a close surrogate: real IT-support messages for classification, real duplicate-linked bug reports for incident retrieval/grouping, and real helpdesk event histories for process metrics. **None alone has all the labels required by the case.** When organizer data arrives, add a mapping adapter and run domain evaluation; avoid changing the application architecture.

A new CSV does **not** guarantee equivalent quality: classification taxonomy, Russian terminology, duplicate prevalence, product ownership and thresholds may need new labeling/calibration.

## Considered approaches

| Option | Advantage | Disadvantage |
|---|---|---|
| Only Zenodo classification | Simplest, 2,229 labeled messages | No same-incident label, no timestamps |
| One artificial fully-populated dataset | Easy demo | Artificial metrics and ROI, no credible validation |
| **Canonical schema + complementary public datasets** | Every component has honest, separately evaluated evidence; organizer adapter independent | Extra source adapters and provenance controls |

**Selected direction:** third option; previously verified Zenodo/Mendeley + a public bug-duplicate candidate + small Russian behavioral fixtures.

## Canonical ticket and trust boundaries

\`\`\`json
{
  "schema_version": "1.0",
  "source_system": "gazprom-export",
  "source_ticket_id": "T-001",
  "created_at": "2026-10-21T10:01:00Z",
  "product_id": "product-a",
  "component_id": "auth",
  "title": "Не работает вход",
  "body_redacted": "HTTP 403 после обновления",
  "error_codes": ["HTTP 403"],
  "reported_version": "2.8.1",
  "pseudonymous_user_id": null,
  "attributes": {},
  "provenance_id": "dataset-manifest-hash"
}
\`\`\`

- Identity is \`(source_system, source_ticket_id)\`, never an unscoped integer ID.
- Nonempty text and provenance required; timestamp, product, component, user/version optional; unknown remains unknown.
- Local timezone may only be converted to UTC when source timezone is documented.
- **Input view:** attributes known by ticket arrival. **Evaluation-only gold:** duplicate-of/master, classification labels, final resolution, later owner. **Runtime state:** problem registry and reviewed insights. These are separately stored and cannot leak into each other.
- Never commit real company ticket text, names, credentials, personal data, or unpublished organizer exports.

## DatasetAdapter contract

\`\`\`python
class DatasetAdapter(Protocol):
    @property
    def capabilities(self) -> frozenset[str]: ...
    def iter_tickets(self) -> Iterator[CanonicalTicket]: ...
    def iter_events(self) -> Iterator[CanonicalEvent]: ...
    def iter_gold_labels(self) -> Iterator[GoldLabel]: ...
    def provenance(self) -> DatasetManifest: ...
\`\`\`

Capabilities include \`classification_gold\`, \`duplicate_links\`, \`created_at\`, \`status_events\`, \`owner_gold\`. An unavailable metric is reported **NOT EVALUABLE**, not zero or inferred from another label. Preserve existing working Zenodo and Mendeley adapters via compatibility tests.

## Source roles and validation status

| Dataset | Verified status | Task |
|---|---|---|
| [Zenodo 7648117](https://zenodo.org/records/7648117) | Publisher originals, 1,572 train + 657 test; \`id,text\`, \`id,category_truth\`; MD5 checked | Seven-category IT support classification, **not** business intent labels |
| [Mendeley Help Desk v3](https://data.mendeley.com/datasets/btm76zndnt/3) | 66,691 issues, 257,508 history events, 30,104 utterances, link integrity checked | Operational metadata, timing and assignment analysis; raw issues.csv lacks text |
| [GitBugs](https://github.com/av9ash/gitbugs) | Repository README and mapping files inspected; **not yet downloaded or validated for this project**. Author states CC BY 4.0 | Duplicate-linked bug reports and incident-like pair retrieval |
| [BugRepo](https://github.com/logpai/bughub) | Curated alternate benchmark, chronological splits documented | Backup if GitBugs link coverage/schema inadequate |
| Russian hand-authored hard negatives | Synthetic, explicit labels | Error code/version constraints, same topic ≠ same incident, prompt injection resilience |
| Organizer dataset | Unavailable | Domain evaluation and calibration after approval |

**Critical GitBugs caveat:** mapping files differ: \`Issue id,Duplicate id\` sometimes contain reciprocal entries, comma-separated IDs, or list-shaped strings; some links are not complete. Extract **positive links only when both endpoints exist in corresponding report corpus**. Missing link is *unlabeled*, NOT a verified negative. Self-links, cycles and missing targets require explicit audit. A bug-tracker duplicate relation is only a **proxy** for a recurring support incident.

## Architecture / data-flow

\`\`\`mermaid
flowchart TD
 A["Zenodo / Mendeley / GitBugs / Organizer Export"] --> B["Versioned source adapters"]
 B --> C["Canonical ticket contract + PII guard"]
 C --> D["Ticket Classification / Attribute Extraction"]
 D --> E["BM25 + Dense Candidate Retrieval"]
 E --> F["Same-incident verification / abstention"]
 F --> G["Auditable Problem Registry"]
 G --> H["Trend, impact and ownership policy"]
 H --> I["Evidence-based Agent + Human approval"]
 I --> J["Mock / permissioned Issue Tracker"]
 B --> K["Source-scoped Gold / events + provenance"]
 K --> L["Offline task-specific evaluation"]
 E --> L
 F --> L
\`\`\`

## Evaluation without label leakage

- **Classification:** preserve Zenodo author's original train/test; macro F1 and per-class metrics. Never assert these seven source categories equal \`incident/how_to/feature_request\`.
- **Duplicate retrieval:** for each query, only index historical reports known before that query (if arrival timestamps available). Recall@K and MRR with audited positive links. Duplicate status and master ID are gold-only. If timestamps absent, label the result **static retrieval**, not online.
- **Pair matching:** report precision only when audited negatives exist, preferably manually adjudicated hard negatives. Random unlinked tickets are not guaranteed true negatives.
- **Clustering:** B-cubed/pairwise F1 only with reliable group membership. Avoid transitive chain merges on raw similarity, and do not merge different problems just because issue texts are similar.
- **Time:** replay only source events with known timestamp semantics, and no future metadata/resolution. Missing manual escalation timestamps => manual TTAI **unknown**.
- **Business:** time manual vs AI-assisted processing (including review and corrections) with actual testers and logs, not invented percentages.

Temporal splitting must prevent duplicate families appearing across train and test when used for learned pair-verification, and document orphan master links.

## Acceptance tests / failure cases

1. Two sources share ticket ID \`42\` → distinct namespaced IDs.
2. Missing or naive timestamps → no replay, but classification may continue.
3. Duplicate CSV header changed or required fields missing → fail loudly, not silent column shift.
4. Merged list-like links, self-links, cycles, reciprocal edges, dangling master → normalized/quarantined with counts, never executed as code.
5. Same topic login vs password reset → must not auto-merge.
6. Labels/resolution at close cannot appear in arrival-time feature view.
7. Product-owner unavailable → agent returns needs_review, not fabricated team.
8. No PII / source text in GitHub logs.

## Organizer dataset onboarding

1. Secure authorized export privately, inspect source schema, legal/privacy requirements.
2. Create versioned **OrganizerAdapter** and field-mapping config; no edit to ML pipeline interface.
3. Run canonical contract tests, provenance, uniqueness, timezone/PII audit.
4. Inventory available labels and annotate small same-incident holdout with expert review.
5. Run unchanged baseline, then compare/recalibrate models/thresholds on organizer domain with a held-out evaluation subset.
6. Demo end-to-end under mock/read-only integrations first; after approval, implement real ITSM connections via secure backend tools.

## Delivery boundaries and next decision

Implement separately reviewed increments: (1) canonical capability contract; (2) GitBugs duplicate-link ingestion and audit; (3) real-source pair retrieval baseline; (4) organizer onboarding adapter. Before each, run Superpowers RED → GREEN → verification. **Do not** claim that a real incident-detection benchmark exists until the corpus is downloaded and link integrity measured.
