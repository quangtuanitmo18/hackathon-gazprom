#!/usr/bin/env python3
"""Validate one pinned real GitBugs corpus and duplicate-link index.

Only aggregate facts/checksums and the small numeric-link CSV may be published.
Original bug reports are kept only in gitignored workspace (possible PII).
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from productpulse.data.gitbugs import normalize_positive_links

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "gitbugs-hadoop"
AUDIT = ROOT / "docs" / "data" / "gitbugs-hadoop-audit.json"
PUBLIC = ROOT / "datasets" / "public" / "gitbugs-hadoop"
PIN = "eadf2d6794990a1aaa26d0ae15391f29f8969301"
BASE = f"https://raw.githubusercontent.com/av9ash/gitbugs/{PIN}/hadoop"
URLS = {
    "reports": f"{BASE}/hadoop_bugs.csv",
    "links": f"{BASE}/hadoop_bugs-combined.csv",
}
MAX_DOWNLOAD = 15 * 1024 * 1024
csv.field_size_limit(sys.maxsize)


def fetch(url: str, name: str) -> dict:
    RAW.mkdir(parents=True, exist_ok=True)
    target = RAW / name
    request = urllib.request.Request(
        url, headers={"User-Agent": "ProductPulse-Research-Audit/1.0"}
    )
    digest = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(request, timeout=90) as response, target.open("wb") as out:
        while chunk := response.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_DOWNLOAD:
                raise ValueError("upstream data exceeds safe download limit")
            digest.update(chunk)
            out.write(chunk)
    if size == 0:
        raise ValueError("upstream data was empty")
    return {"path": target, "sha256": digest.hexdigest(), "bytes": size}


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames or []
        rows = list(reader)
    if not fields:
        raise ValueError(f"no columns in {path.name}")
    return fields, rows


def find_issue_id_column(headers: list[str]) -> str:
    choices = {"issueid", "id"}
    matches = [
        h for h in headers if re.sub(r"[^a-z0-9]", "", h.lower()) in choices
    ]
    if len(matches) != 1:
        raise ValueError(f"ambiguous or missing issue ID header: {headers}")
    return matches[0]


def run() -> dict:
    source = {}
    for kind, url in URLS.items():
        file = fetch(url, kind + ".csv")
        fields, rows = read_csv(file["path"])
        source[kind] = {
            "file": file, "columns": fields, "rows": len(rows),
            "data": rows, "url": url,
        }

    report_cols = source["reports"]["columns"]
    id_col = find_issue_id_column(report_cols)
    ids: set[str] = set()
    missing_id = duplicate_id = 0
    potential_email_rows = 0
    for row in source["reports"]["data"]:
        value = str(row.get(id_col) or "").strip()
        if not value or not value.isascii() or not value.isdigit():
            missing_id += 1
            continue
        if value in ids:
            duplicate_id += 1
        ids.add(value)
        # Aggregate email-pattern count only; raw report bodies stay gitignored.
        if any(
            re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", str(v or ""))
            for v in row.values()
        ):
            potential_email_rows += 1

    link_cols = source["links"]["columns"]
    if not {"Issue id", "Duplicate id"}.issubset(link_cols):
        raise ValueError(f"unexpected GitBugs Hadoop link fields: {link_cols}")

    summary = normalize_positive_links(source["links"]["data"], ids)
    result = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": "GitBugs: Hadoop issue reports and duplicate links",
        "repo": "https://github.com/av9ash/gitbugs",
        "source_commit": PIN,
        "license_as_stated_by_author": "CC-BY-4.0",
        "reports": {
            "url": URLS["reports"], "sha256": source["reports"]["file"]["sha256"],
            "bytes": source["reports"]["file"]["bytes"],
            "rows": source["reports"]["rows"], "columns": report_cols,
            "id_column": id_col, "distinct_ids": len(ids),
            "invalid_ids": missing_id, "repeated_ids": duplicate_id,
            "rows_with_possible_email_pattern": potential_email_rows,
            "raw_report_text_published_in_git": False,
        },
        "links": {
            "url": URLS["links"], "sha256": source["links"]["file"]["sha256"],
            "bytes": source["links"]["file"]["bytes"],
            "rows": source["links"]["rows"], "columns": link_cols,
            "valid_unique_positive_pairs": len(summary.positives),
            "orphan_edges": summary.orphan_count,
            "self_links": summary.self_link_count,
            "invalid_rows": summary.malformed_count,
            "duplicate_or_reciprocal_edges": summary.reciprocal_or_repeated,
            "unlabeled_rows": summary.unlabeled_count,
            "index_validated": summary.link_index_validated,
            "missing_edge_means_negative": False,
        },
        "limitations": [
            "Duplicate-of is issue-tracker label, not guaranteed same root cause or support incident.",
            "No unlinked report is treated as a confirmed negative pair.",
            "Source may contain PII, therefore full reports are not committed to public Git.",
            "Temporal input must not include eventual resolution or duplicate-of outcomes.",
        ],
    }
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "reports": result["reports"]["rows"],
        "reported_ids": len(ids),
        "duplicate_map_rows": result["links"]["rows"],
        "verified_pairs": len(summary.positives),
        "orphan": summary.orphan_count,
        "invalid_rows": summary.malformed_count,
        "source_sha256": result["reports"]["sha256"],
    }, indent=2))

    if len(ids) < 20 or len(summary.positives) == 0 or missing_id or duplicate_id:
        raise ValueError("source audit failed critical ID/link coverage gate")
    # The relation file contains only numeric issue IDs; checked by parser.
    if summary.malformed_count > 0:
        raise ValueError("invalid link mapping rows: do not publish")
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "duplicate-links.csv").write_bytes(source["links"]["file"]["path"].read_bytes())
    return result


if __name__ == "__main__":
    run()
