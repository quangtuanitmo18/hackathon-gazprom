# Original Zenodo 7648117 CSV files — CC BY 4.0

**Source:** Leonardo Santiago Benitez Pereira, *Classification of IT Support Tickets* (2022), Zenodo v2, https://doi.org/10.5281/zenodo.7648117

**License:** Creative Commons Attribution 4.0 International (CC BY 4.0); original author retains attribution.

These four files are exact original downloaded publisher CSVs, with original train/test partitions and source IDs preserved; the GitHub Actions download process validates published file MD5 hashes.

**Not Gazprom Neft data.** Source documents describe the data as PII-redacted; do not regard this as proof that every sensitive string has been removed. Avoid publishing raw strings from the dataset in reports.

- `X_train.csv`: 1,572 records, columns `id,text`
- `y_train.csv`: 1,572 records, columns `id,category_truth`
- `X_test.csv`: 657 records, columns `id,text`
- `y_test.csv`: 657 records, columns `id,category_truth`

Do not join X/y by row position. Join by original `id` and use the author-provided holdout without training leakage. For exact MD5/SHA256 checksums and audit evidence see [upstream audit](../../../docs/data/source-audit.json) and [live adapter verification](../../../docs/data/live-adapter-compatibility.json).

Mendeley Help Desk Tickets v3 originals are intentionally not committed to git because they contain larger operational histories and potential sensitive information despite source masking. Downloadable temporary GitHub Actions artifacts and reproducible download scripts are provided instead.
