# ProductPulse Retrieval-Ranked Human Review Queue and Privacy Guard

**Stage:** Hackathon MVP; tests with synthetic Russian tickets and an actual PostgreSQL+Keycloak CI runner. This is neither a trained incident classifier nor regulatory-grade anonymization.

## OSS components and why

- Reuse existing tested `productpulse.eval.retrieval_methods.BM25Index` to rank Cyrillic-language title/body text. A separate embedding model/vector service is **not necessary yet** for 500-ticket batches.
- Reuse [scrubadub](https://github.com/LeapBeyond/scrubadub), Apache-2.0, for common PII detectors (emails, phones, URLs and supported IDs). A deliberately narrow supplemental regex masks Bearer credentials, client secrets, API keys and PEM private keys.
- Existing FastAPI + SQLAlchemy + PostgreSQL16, Keycloak + Auth.js OIDC, Zod and TanStack UI. No new auth, ORM, UI or workflow engine built in-house.

## Ingestion: sanitized before storage

`POST /internal/v1/tickets` still requires the private service token. It now calls `sanitize_ticket(CanonicalTicketV1)` **before** `PersistentProblemRegistry.transact`. The sanitizer returns an immutable canonical copy. Source-scoped ID, provenance, structured product/version/error-code and pseudonymous metadata **are rejected**, not mutated, if common sensitive patterns are detected; modifying those would corrupt referential identity. PII/secret in `title` and `body_redacted` is replaced before PostgreSQL mutation, audit, review evidence or ranking.

Important:
- `scrubadub` **is not complete** Russian named-entity redaction: names, local street addresses, Russian tax IDs, custom order numbers and arbitrary business secrets may survive. It does NOT prove GDPR/Russian localization compliance. Real data requires a tested Russian-language PII detector, a DLP gate and human spot checks, plus retention/erasure controls.
- No raw content is committed or printed by CI. The CI test uses **fake** addresses/credentials.
- Existing stored content predating this change is **not retroactively scrubbed**. Production migration must quarantine/rescan legacy rows before exposing them.
- Structured IDs can themselves carry PII: this guard catches common patterns but cannot infer all sensitive company identifiers.
- Privacy rules can remove terms useful for retrieval. Accuracy must be remeasured on a properly anonymized dataset.

## Candidate ranking and semantics

`GET /internal/v1/review-candidates?limit=20` requires **both** internal service token and a cryptographically verified OIDC reviewer token with matching tenant scope. The fixed trusted server scope defines the complete candidate corpus. The in-memory BM25 index is rebuilt for this request using **all** available tickets in that scope, up to **500**; exceeding 500 produces HTTP 503 with an explicit message to install a scalable search service. Limit is 1–30 results.

- Uses BM25 over redacted ticket fields and technical metadata. Requires actual **incident narrative** word overlap after dropping obvious non-evidence generic terms; product/component alone never creates a candidate.
- Removes same-ticket pairs, tickets already sharing the same active Problem and existing third-person approved duplicate links.
- Returns **unique undirected pairs**, stable pair keys, `rank` (the minimum observed query-relative BM25 position) and supporting *categorical signals*: `lexical_overlap`, `same_product`, `same_component`, `shared_error_code`.
- Neither `rank` nor number of shared tokens is a calibrated duplicate probability. No gold duplicate links, future reviewer labels or future status fields are used to compute BM25.
- Source tracker duplicate links may not mean identical root cause; real false positive rate/F1 requires **human adjudicated negative pairs** and chronological/family-separated evaluation.
- Python implementation is O(N²) brute-force query ranking and JSONB snapshot is O(N) per write: **do not expose this 500-ticket prototype as a scalable production search endpoint**.

## Reviewer UX

Auth.js server-only BFF `GET /api/review` now calls signed `/internal/v1/review-candidates` and paginates `/internal/v1/review-tickets?limit=50&offset=N` until it has loaded all evidence up to the 500-ticket cap. This fixes a real usability bug: a candidate beyond ticket #50 is still selectable, rather than being an unusable card. It never forwards the Keycloak access token or `PRODUCTPULSE_INTERNAL_TOKEN` to browser-side JavaScript.

A reviewer can click a ranked suggested pair and inspect both redacted ticket bodies in the existing comparison UI. Labeling stays a **2 independent human reviewers + 3rd independent lead** action. No automatic merge or Jira writes. If candidate generation fails, the BFF displays an error rather than inventing a success or silently returning only the first page.

## Verification
- TDD tests for tenant-scoped ranked candidate API; Russian lexical similarity; shared-product false-positive regression; maximum corpus, deterministic pair ordering and gold-label avoidance.
- Real PostgreSQL ingest/audit test: fake email/secret omitted from persisted state and reviewer evidence; repeat raw POST sanitized identically before idempotency check.
- Frontend server BFF tests: malformed candidate response rejected, evidence pagination works past 50, private credentials never in browser payload.
- Real Keycloak + Chromium 3-account workflow: recommendation clicked, two independent votes and third-lead approval, DB audit verifies **no automatic merge**.

## Next increments
1. Load organizational dataset via configurable `OrganizerAdapter` with privacy policy and source event-time handling.
2. Add a searchable index (PostgreSQL tsvector + pg_trgm, OpenSearch or Qdrant+embeddings) to move beyond 500 tickets.
3. Evaluate BM25 vs multilingual embeddings and RRF hybrid on real adjudicated labels; report precision/recall only with confirmed negatives and time-safe splits.
4. Implement queue assignments and reviewer-blind evidence workflow so one reviewer cannot see the other's label before submitting.
