# Public Dataset Plan — Task 1 Verification Record

**Date:** 2026-10-30  
**Status:** implementation tested locally; actual public CSV integration **NOT YET VERIFIED**.  
**Feature branch:** feat/public-dataset-ingestion (stacked on docs/superpowers-productpulse-foundation).

## Implemented

- Canonical ticket schema with required fields and timezone-aware UTC dates (missing dates remain null).
- Zenodo split adapter: joins normalized id/text and id/label by ID; rejects duplicate, unmatched and unknown schemas; preserves author train/test split.
- Mendeley processed reporter_messages adapter (issue_id/text/issue_created); excludes outcome/status from classification truth.
- SHA-256 provenance manifest with declared source, license, byte count and filename, not raw ticket content.
- gitignore for raw/processed data and secrets, Python project metadata, CI workflow.

## Superpowers TDD — local evidence

1. RED 1: pytest tests/data/test_adapters.py tests/data/test_manifest.py -v -> 2 collection errors: ModuleNotFoundError: productpulse (source absent).
2. GREEN 1: same command -> 15 passed; full suite 15 passed.
3. RED 2: identifier canonicalization regression -> 1 failed (IDs not trimmed).
4. GREEN 2: pytest -q -> 16 passed.
5. RED 3: credentials-bearing provenance URL and numeric timestamp -> 2 failed (DID NOT RAISE).
6. GREEN 3: pytest -q -> **21 passed in 0.05s**, zero failed. python -m compileall -q src exit 0.
7. git check-ignore -v data/raw/placeholder.csv -> .gitignore:2:/data/raw/ (ignored).

This evidence is **local unit testing on artificial fixtures**, NOT real-dataset accuracy and NOT a statement about remote GitHub CI.

8. RED 4: nonfinite CSV identifiers/labels and numeric-string timestamp -> 3 tests failed before correction.
9. GREEN 4: full suite -> 21 passed in 0.05s; compileall exit 0.

## Limitations and remaining work

- Container cannot access external download hosts; Zenodo and Mendeley raw files were not downloaded or benchmarked.
- Actual Zenodo v2 CSV header and ID layout remain unverified; mapping currently accepts explicitly normalized id/text and id/label rows and fails closed on unknown schemas.
- Mendeley raw issues.csv has a different schema. This adapter accepts processed reporter_messages-style rows only; source timezone must be checked before replay.
- Structural validation does not itself remove PII; real data must be independently authorized and redacted.
- Source labels are not the target incident taxonomy, and there is no verified same-incident gold standard.
- GitHub Actions CI and Python 3.11 are pending remote verification.

## Next

Task 2: inspect Zenodo source headers in an authorized environment, preserve source train/test split, run majority and TF-IDF/logistic regression baseline, save run manifest and held-out Macro F1. Do not invent scores.
