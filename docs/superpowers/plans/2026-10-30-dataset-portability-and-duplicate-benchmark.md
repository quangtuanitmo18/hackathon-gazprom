# Dataset Portability & Duplicate Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (\`- [ ]\`) syntax for tracking.

**Goal:** Build a stable canonical ticket boundary plus a genuine duplicate-linked bug benchmark, so replacing the dataset requires a source adapter and calibration rather than rewriting the pipeline.

**Architecture:** Keep current Zenodo/Mendeley parsers working; add a namespaced canonical representation and capability manifest. Pin and audit GitBugs duplicate links separately from report texts; train and evaluate retrieval only on defensible positive links, with explicit unknown negatives.

**Tech Stack:** Python 3.11+, Pydantic 2, pytest, csv/json/hashlib, scikit-learn BM25/TF-IDF baseline later. No LLM needed in phase 1.

**Spec:** [Dataset-portable incident design](../specs/2026-10-30-dataset-portability-and-incident-benchmark-design.md).

## Global Constraints

- No Gazprom Neft data or sensitive ticket text committed to public GitHub.
- Gold labels, final resolution and duplicate-of fields never appear in arrival-time model input.
- No randomized pair splitting that exposes the same problem family across train/test.
- Source-specific labels must preserve source semantics; "no duplicate link" != negative.
- No claims of incident accuracy or ROI without verified evaluation data.
- Keep existing working Zenodo/Mendeley adapters and CI green.
- Apply Superpowers TDD: RED → GREEN → refactor → verify → commit on isolated branch.

## Review Focus

- Two sources use "42" => distinct identity and index keys (Task 1).
- Missing timestamp, unknown timezone => no fabricated creation time or replay (Task 1).
- Duplicate links include list-shaped strings, reciprocal edges and malformed values => no \`eval\`, no self-links (Task 2).
- Duplicate target absent from downloaded full report index => report orphan instead of manufacturing a match (Task 2).
- Learned pair verifier sees duplicate family across train/test => fail split audit (Task 3).

---

### Task 1: Canonical source boundary, capabilities and gold separation

**Files:**
- Create: \`src/productpulse/data/canonical.py\`
- Create: \`tests/data/test_canonical.py\`
- Modify: \`src/productpulse/data/adapters.py\` only if necessary for optional conversion.
- Test: existing \`tests/data/test_adapters.py\`.

**Interfaces:**
- \`CanonicalTicketV1(source_system: str, source_ticket_id: str, title: str | None, body_redacted: str | None, created_at: datetime | None, product_id: str | None, component_id: str | None, reported_version: str | None, provenance_id: str, schema_version: Literal["1.0"])\`.
- \`ticket_key(ticket: CanonicalTicketV1) -> str\`.
- \`DatasetCapabilities(classification_gold: bool, duplicate_links: bool, timestamps: bool, owner_gold: bool, status_events: bool)\`.
- \`GoldDuplicateLink(source: str, issue_id: str, master_id: str, evidence_type: str)\`, separated from runtime ticket object.

- [ ] Step 1: Write failing tests for namespaced identity, empty ticket text, blank provenance, invalid timezone, and absence of label fields in public runtime schema.
- [ ] Step 2: Run \`python -m pytest tests/data/test_canonical.py -v\` — expected RED (missing module).
- [ ] Step 3: Implement minimal frozen Pydantic models and namespaces; do not modify older adapters.
- [ ] Step 4: Run \`python -m pytest tests/data/test_canonical.py tests/data/test_adapters.py -q\` and full \`python -m pytest -q\` — expected GREEN.
- [ ] Step 5: Commit \`feat(data): add namespaced canonical ticket and gold separation\`.

### Task 2: Audit GitBugs duplicate links without publishing raw reports

**Files:**
- Create: \`src/productpulse/data/gitbugs.py\`
- Create: \`tests/data/test_gitbugs.py\`
- Create: \`scripts/datasets/audit_gitbugs.py\`
- Create: \`docs/data/gitbugs-audit.md\` (measured findings only).
- Modify: \`.github/workflows/verify-upstream-datasets.yml\` only after agreeing run scope.

**Interfaces:**
- \`parse_duplicate_ids(raw: str) -> tuple[str, ...]\` — accepts exact scalar or safe structured quoted list, never evaluate arbitrary code.
- \`normalize_positive_links(rows: Iterable[Mapping], available_ids: set[str] | None) -> DuplicateLinkAudit\` with positive undirected pairs, invalid count, self-link count, orphan count, reciprocal dedup.
- \`audit_report_index(csv_path: Path, mapping_path: Path) -> Mapping[str, int]\` — source schema pinned and checked.

- [ ] Step 1: Failing tests: \`['123','456']\`, \`"123,456"\`, duplicate reverse pairs, malformed and self links, missing master ID.
- [ ] Step 2: Run \`python -m pytest tests/data/test_gitbugs.py -v\` — expected RED.
- [ ] Step 3: Implement safe parser and link audit; keep unknown negatives unknown.
- [ ] Step 4: Run tests; download **one modest verified corpus** such as Hadoop/HBase (not whole repo) on CI runner, record commit hash, SHA256, report CSV schema, orphan count; keep raw text out of git until reviewed.
- [ ] Step 5: Commit \`feat(data): validate real duplicate bug links and audit metadata\`.

### Task 3: Static retrieval baseline with rigorous labeling

**Files:**
- Create: \`src/productpulse/eval/duplicate_retrieval.py\`
- Create: \`tests/eval/test_duplicate_retrieval.py\`
- Create: \`scripts/run_duplicate_baseline.py\`
- Create: \`docs/evaluation/duplicate-benchmark-methodology.md\`.

**Interfaces:**
- \`make_query_gallery(positive_links, timestamps=None) -> QueryGallery\` with no leakage.
- \`evaluate_duplicate_retrieval(queries, index, gold) -> Metrics\` for Recall@K, MRR, coverage and missing-master counts.

- [ ] Step 1: Write failing tests for no-positive queries, master missing, leakage from future documents, family-disjoint split audit.
- [ ] Step 2: Run \`python -m pytest tests/eval/test_duplicate_retrieval.py -v\` — expected RED.
- [ ] Step 3: Implement TF-IDF lexical retrieval first, then optional dense model behind interface.
- [ ] Step 4: Run on verified corpus with manifest and confidence limits; do not report precision without adjudicated negatives.
- [ ] Step 5: Commit \`feat(eval): establish duplicate-link retrieval benchmark\`.

### Task 4: OrganizerAdapter onboarding template

**Files:**
- Create: \`src/productpulse/data/organizer_adapter.py\`
- Create: \`tests/data/test_organizer_adapter.py\`
- Create: \`configs/organizer_mapping.example.json\`
- Create: \`docs/data/organizer-onboarding.md\`.

**Interfaces:** \`convert_organizer_rows(rows: Iterable[dict], mapping: FieldMapping, provenance: str) -> Iterator[CanonicalTicketV1]\`.

- [ ] Step 1: Write failing tests for arbitrary column names, reordered CSV, missing optional fields, required identity/text, invalid timestamps, unknown labels not leaked.
- [ ] Step 2: Run \`python -m pytest tests/data/test_organizer_adapter.py -v\` — expected RED.
- [ ] Step 3: Implement mapping-driven adapter with allowlisted fields and immutable domain DTOs.
- [ ] Step 4: Run full tests and demo switching Zenodo → mock-organizer source without editing pipeline.
- [ ] Step 5: Commit \`feat(data): add configurable organizer source onboarding\`.

## Acceptance / stage gates

- Task 1: existing CI passes and new canonical contract tested on both Python 3.11/3.13.
- Task 2: source release pinned, original duplicate-link schema and link-quality statistics measured; no unsafe false-negative assumptions.
- Task 3: reproducible retrieval metrics on source-specific gold links, no future information leakage.
- Task 4: only adapter/config changes for new organizer-style CSV; benchmark and agent code unaffected.

**Note:** These are four independent review gates; architecture chosen does not imply all stages already implemented.
