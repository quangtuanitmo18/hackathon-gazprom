# Retrieval-Ranked Review Queue & PII/Secret Ingestion Guard — 2026-10-30

## Context
ProductPulse's Keycloak review UI selects from first 50 tickets, missing candidate ranking at scale. Existing audited offline BM25 implementation `src/productpulse/eval/retrieval_methods.py` provides deterministic Cyrillic tokenization. Existing `body_redacted` is merely a field name, not a sanitizer.

## Selected incremental architecture
1. **Real runtime candidate queue**, tenant-scoped PostgreSQL snapshot → deterministic BM25 ranking over redacted title/body + source metadata. Reuse existing BM25Index and tokenizer; no ad-hoc vector embedding service or LLM necessary for first production-esque evaluation loop. Build up to **500** currently registered tickets per scope and fail closed if more than 500 (never rank only arbitrary first N pretending complete). Return at most 30 **unordered unique pairs with ranks**, never a "same-incident" decision or root-cause claim. Exclude self-pairs, existing confirmed positives and same active Problem; skip zero lexical-overlap suggestions. Results remain static/transductive, not a causal time-safe evaluation. No golden edges leak as predictor features; existing human-review *state* can be used to avoid duplicate assignments but never for the score itself.
2. OIDC + service-token protected `GET /internal/v1/review-candidates` with explicit scope fixed by server. Introduce BFF same-origin `GET /api/review` with candidate array and UI selecting recommended pair. Manual selection retained as fallback.
3. **Ingress protection** using OSS **scrubadub** for common PII (email, phone, URLs etc.) plus narrow high-risk regex for credentials, Bearer tokens, PEM private key; redact `title` and `body_redacted` BEFORE persisting to PostgreSQL; use identical-safe placeholders. Reject unsafe IDs/provenance/error_codes rather than silently altering source-scoped identities. This is **best-effort pattern redaction**, not certified de-identification. No unsupported blanket claim regarding Russian names, addresses or rare PII.
4. To avoid log leaks, errors must contain no raw unredacted strings. Do not log input. Idempotent replay of raw same ticket must sanitize deterministically before comparing persisted CanonicalTicketV1.

## OSS alternatives
- Choose existing BM25Index (already implemented & tested in repo) over pulling a duplicate BM25 dependency solely for 500-item prototype; later evaluate Qdrant + sentence-transformers to enable dense/multilingual hybrid at scale, and Redis caching/async indexing once a real dataset warrants.
- Choose `scrubadub` (Apache-2.0, user-provided text pattern masking) rather than build broad PII recognition from scratch. Regex supplement only for developer credentials not reliably handled by generic PII tools. **Known risk:** Cyrillic proper names, Russian postal addresses and company-specific account IDs not reliably recognized; before external data use Presidio with validated Russian NER and human spot checks.

## Acceptance
- Tests RED→GREEN: queue Cyrillic lexical similarity, pairs only same tenant, no same problem, unique undirected pairs and sorted stability, first/second reviewer status and no score labels; bounded corpus >500 gives explicit error; no overlap gives empty queue; reviewer/lead auth enforced.
- Redaction: PII/secret input never appears in GET evidence, candidate API or PostgreSQL ticket snapshot; double ingest idempotent; pass through harmless technical tokens/error code/version; unsafe source IDs blocked; test both Python 3.11/3.13 and actual PostgreSQL 16.
- Frontend unit tests/BFF + Keycloak Chromium: recommended pair selected and human 2+1 review flow unaffected.
- Security: tenant fixed at server, individual OIDC subject required, server token never in browser, no automatic merge, no artificial incident precision/recall claim.

## Scope limits
No real dataset metric claim, no unbounded 100k corpus indexing, no fully assured Russian PII scrubber, no production SLA, no enterprise identity claims.
