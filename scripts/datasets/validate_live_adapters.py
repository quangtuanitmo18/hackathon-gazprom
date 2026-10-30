#!/usr/bin/env python3
"""Exercise product adapters against the actual downloaded publisher CSV files.

Requires scripts/datasets/verify_sources.py first. Outputs only aggregate safe
information; no customer text, names, reporter identifiers or source rows.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from productpulse.data.adapters import parse_mendeley_issues, parse_zenodo_split

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw"
OUT = ROOT / "docs/data/live-adapter-compatibility.json"


def rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="", errors="replace") as file:
        return list(csv.DictReader(file))


def main() -> int:
    result = {"verified_at_utc": datetime.now(timezone.utc).isoformat(),
              "source": "original publisher CSVs, not mock rows",
              "zenodo": {}, "mendeley": {}, "success": False}
    for split, n in (("train", 1572), ("test", 657)):
        x = rows(RAW/"zenodo"/f"X_{split}.csv")
        y = rows(RAW/"zenodo"/f"y_{split}.csv")
        data = parse_zenodo_split(x, y, split)
        assert len(data) == n, f"Unexpected Zenodo {split} size"
        assert all(t.text_redacted and t.source_label is not None for t in data)
        result["zenodo"][split] = {
            "count": len(data),
            "labels": dict(Counter(t.source_label for t in data)),
            "source_split": split, "schema": {"X": list(x[0]), "y": list(y[0])},
        }

    issues = rows(RAW/"mendeley"/"issues.csv")
    parsed = parse_mendeley_issues(issues)
    assert len(parsed) == len(issues) == 66691
    ids = {v.source_id for v in parsed}
    assert len(ids) == len(parsed)
    result["mendeley"] = {
        "issue_count": len(parsed),
        "projects_nonnull": sum(v.project_id is not None for v in parsed),
        "created_at_nonnull": sum(v.created_at_raw is not None for v in parsed),
        "timestamp_timezone_note": "Source issue_created retained as raw string, timezone semantics unknown",
        "text_available_in_issues_csv": False,
    }
    history = rows(RAW/"mendeley"/"issues_change_history.csv")
    utterances = rows(RAW/"mendeley"/"sample_utterances.csv")
    result["mendeley"]["history_events"] = len(history)
    result["mendeley"]["history_orphan_issueids"] = sum(r["issueid"].strip() not in ids for r in history)
    result["mendeley"]["utterance_rows"] = len(utterances)
    result["mendeley"]["utterances_orphan_issueids"] = sum(r["issueid"].strip() not in ids for r in utterances)
    result["mendeley"]["utterance_author_roles"] = dict(Counter(r.get("author_role", "<missing>") for r in utterances))
    result["success"] = True
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
