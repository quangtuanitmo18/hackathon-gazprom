# Отчёт о проверке исходных публичных датасетов

**Дата проверки:** 2026-10-30 (UTC)  
**Статус:** **VERIFIED ORIGINALS + LIVE ADAPTER COMPATIBILITY**. Это не benchmark качества AI и не данные «Газпром нефти».  
**GitHub Actions:** https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41036933273  
**Machine-readable evidence:** [source-audit.json](source-audit.json), [live-adapter-compatibility.json](live-adapter-compatibility.json)

## 1. Zenodo: Classification of IT Support Tickets (v2)

- DOI: https://doi.org/10.5281/zenodo.7648117
- Author: Leonardo Santiago Benitez Pereira; license indicated CC BY 4.0; attribution maintained.
- **Original files available inside this repository:** [datasets/public/zenodo-7648117](../../datasets/public/zenodo-7648117/README.md).
- Exact original MD5 verified against published Zenodo file checksums for **all four** files.

| File | Exact bytes | Rows | Original header | SHA-256 |
|---|---:|---:|---|---|
| X_train.csv | 215030 | 1572 | `id,text` | `789712f97fb472544eeb82d8f5a142ed46e0bf254c6c34ac53a9f1575a9d460e` |
| y_train.csv | 27838 | 1572 | `id,category_truth` | `cb851ff4d5e792886504b3040bcc85a5dbf94514d31293eddd6d69fcb7278d53` |
| X_test.csv | 164490 | 657 | `id,text` | `4b808bc32c57f063960a3a4e7a4a30769c96be8143649aadc86835f4cb9763e5` |
| y_test.csv | 11131 | 657 | `id,category_truth` | `2b10db5e2f071e649efb3d40dd007ec62bc661f35b4afaf44117a00865760f94` |

**Real-source validation:** IDs on X/y match within both splits; the corrected Zenodo adapter parses **1572 + 657** actual records, not just test fixtures. Exactly seven label classes present. The authored split is kept; no shuffle or arbitrary train/test re-split.

Label counts:

| Label | Train | Test |
|---|---:|---:|
| Fileservice | 546 | 138 |
| Support general | 541 | 221 |
| Software | 164 | 58 |
| EOL | 45 | 58 |
| O365 | 127 | 92 |
| Active Directory | 84 | 49 |
| Computer-Services | 65 | 41 |

**Caution:** publisher describes PII redaction; machine check found zero unmasked email-pattern matches but that does NOT constitute a complete privacy audit. Category labels do not mean 'same incident'. Dataset languages are mostly EN/DE/PT/ES, not a Russian domain benchmark.

## 2. Mendeley: Help Desk Tickets v3

- DOI: https://doi.org/10.17632/btm76zndnt.3
- Author: Mohammad Abdellatif; CC BY 4.0.
- Raw data downloaded and analyzed in GitHub Actions; not stored in public git history due to size and potential contextual sensitivity.
- An original-source download artifact `licensed-upstream-datasets-cc-by-4` is available from the workflow run (short retention, current setting 3 days). For longer-term reproducibility use `python scripts/datasets/verify_sources.py`.

| Original file | Rows | Original schema details |
|---|---:|---|
| issues.csv | **66691** | `id`, `issue_proj`, `issue_created`, `issue_type`, `issue_status`, workflow step durations etc. |
| issues_change_history.csv | **257508** | `id`, `issueid`, `field`, `value`, `created`, `change_group_id` |
| sample_utterances.csv | **30104** | `issueid`, `id`, `comment_seq`, `utr_seq`, `author`, `created`, `actionbody`, `author_role` |
| FEATURES.md, EXAMPLE.md | Verified download/checksums | Documentation |

- All history and utterance issue references match records in `issues.csv`: **0 orphan issueids** on both relationships.
- All 66691 original issue rows parse through a distinct **metadata-only** adapter, preserving original timestamps as raw strings until timezone semantics are confirmed.
- **Important:** `issues.csv` does **not** contain the original ticket text required for text classification. The `reporter_messages` processed view is separate; `sample_utterances.csv` contains text for only a study subset.
- Original issue type and resolution are **not** ground-truth labels for our proposed `incident/how_to/feature_request` taxonomy.

## 3. TDD evidence and caveats

The actual Zenodo schema differs from the initial adapter: `category_truth` rather than `label`. GitHub Actions showed a test failure against the original schema (**21 passed, 1 failed**), then after the fix the Python suite passed on 3.11 and 3.13. The original Mendeley `issues.csv` differs from the processed `reporter_messages` mirror and gets its own metadata adapter; this adapter was also introduced with a failing test before implementation.

**Verification commands:**
```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python scripts/datasets/verify_sources.py
python scripts/datasets/validate_live_adapters.py
sha256sum datasets/public/zenodo-7648117/*.csv
```

The source download is run on GitHub Actions because local sandbox networking is restricted; inspect the workflow run and committed JSON evidence for fresh results. **No ML F1, clustering accuracy, business time savings or ROI has been measured.**

## 4. Correct next step

Run TF-IDF + Logistic Regression on Zenodo author-provided holdout with a majority-class baseline and full evaluation manifest, **without fitting on test labels**. Use Mendeley for operational timeline/process profiling; do not join it with Zenodo labels as if from the same population. For incident clustering, first create independently annotated `same_incident` pairs with hard negatives.
