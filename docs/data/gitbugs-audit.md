# GitBugs Hadoop — проверка реальных duplicate links

**Проверено:** 2026-10-30; [успешный GitHub Actions run](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41039308963)  
**Статус:** ORIGINAL SOURCE VALIDATED; это **не** accuracy/precision/recall модели и не данные «Газпром нефти».

## Источник и права

- [av9ash/gitbugs](https://github.com/av9ash/gitbugs), pinned commit \`eadf2d6794990a1aaa26d0ae15391f29f8969301\`.
- Автор указывает лицензию CC BY 4.0; обязательна атрибуция: Patil, A. (2025), *GitBugs: Bug Reports for Duplicate Detection, Retrieval Augmented Generation, Triage, and More*, arXiv:2504.09651.
- \`hadoop_bugs.csv\` и \`hadoop_bugs-combined.csv\` проверены по SHA-256 и исходной схеме.
- [Числовые связи duplicate](../../datasets/public/gitbugs-hadoop/duplicate-links.csv) опубликованы в нашем репозитории с атрибуцией. Полные тексты bug reports **не публикуются** из-за возможных персональных данных.

## Измеренные факты

| Источник | Rows | Columns / заметки |
|---|---:|---|
| \`hadoop_bugs.csv\` | **2503** | \`Summary\`, \`Issue id\`, \`Status\`, \`Priority\`, \`Resolution\`, \`Created\`, \`Resolved\`, \`Affects Version/s\`, \`Description\` |
| \`hadoop_bugs-combined.csv\` | **126** | \`Issue id\`, \`Duplicate id\` |
| Unique unordered positive pairs | **66** | Проверены по индексу из 2503 ID |
| Repeated / reciprocal positive edges | **61** | Лишние связи не превращаются в новые случаи |
| Missing target or source IDs | **0** | Нет orphan edges |
| Invalid mapping rows | **0** | Все строки распарсены |
| Raw report rows matching email regex | **48** | Поэтому не коммитим оригинальные описания в публичный GitHub |

Checksums:

- Reports SHA-256: \`a04ac6238c39afaf97b9ffb2a416c1318dd85672a31e9a6dd74f64e199b77358\`.
- Mappings SHA-256: \`5d9978c8aaeb65fcaf2386fdd796a9023931dd4b66e3c5751f111db6624b6dc0\`.
- [Machine-readable audit](gitbugs-hadoop-audit.json).

**Interpretation:** 66 normalized source-labeled positive pairs are useful for checking candidate retrieval. They do **not** establish 2437 verified negatives; absence of a duplicate link means \`unknown\`. They are issue tracker duplicates, not necessarily the same underlying technical incident seen by support. Grouping F1 and precision require additional adjudication.

## Reproduce

\`\`\`bash
python -m pip install -e ".[dev]"
python -m pytest -q
python scripts/datasets/audit_gitbugs.py
\`\`\`

Original files are downloaded from a pinned public GitHub commit into gitignored \`data/raw/gitbugs-hadoop\`. The script checks report IDs, normalizes reciprocal pairs, writes an aggregate audit, and copies **only** numeric-ID mapping file into \`datasets/public/gitbugs-hadoop/\`.

Next implementation: static/historical duplicate retrieval benchmark (TF-IDF/BM25 baseline) on these 2503 reports with source-labeled positives, then adjudicated hard negatives; do not use eventual \`Resolution\` or duplicate labels as model features.
