#!/usr/bin/env python3
"""Download upstream datasets, verify checksums and publish non-sensitive audit metadata.

Raw source files must remain gitignored. For public GitHub, only machine-readable
aggregate audit reports are committed; originals go to time-limited Actions artifacts.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw"
REPORT = ROOT / "docs/data/source-audit.json"
ZENODO = {
    "X_train.csv": "0a79f0c2f95fcdb407f24b2c0ad7f7d1",
    "X_test.csv": "02328c4e09a78a41acb22ce17e6e0312",
    "y_train.csv": "90876921486a26a67bc1976da87305d9",
    "y_test.csv": "2f054c0e3d8cbbbd76adf30d13a7710a",
}
USER_AGENT = "ProductPulseAI-Research-Validator/1.0 (public reproducibility; contact: GitHub issues)"
MAX_BYTES = 110_000_000
csv.field_size_limit(sys.maxsize)


def download(url: str, target: Path, limit: int = MAX_BYTES) -> dict:
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=100) as response, target.open("wb") as output:
                sha = hashlib.sha256()
                md5 = hashlib.md5()
                size = 0
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > limit:
                        raise ValueError(f"source exceeds {limit} bytes")
                    sha.update(chunk)
                    md5.update(chunk)
                    output.write(chunk)
            if size == 0:
                raise ValueError("download empty")
            return {"bytes": size, "sha256": sha.hexdigest(), "md5": md5.hexdigest()}
        except (OSError, ValueError, urllib.error.URLError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            target.unlink(missing_ok=True)
            if attempt < 2:
                time.sleep(attempt + 2)
    raise RuntimeError(f"download failed ({url}): {last_error}")


def csv_audit(path: Path) -> dict:
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames or []
        if not headers:
            raise ValueError(f"CSV has no header: {path.name}")
        total = 0
        blank = Counter()
        sample_ids = []
        label_dist = Counter()
        placeholders = 0
        potential_emails = 0
        for row in reader:
            total += 1
            for k in headers:
                v = str(row.get(k) or "").strip()
                if not v:
                    blank[k] += 1
            if total <= 5:
                # IDs only, not source message texts.
                for k in ("id", "issue_id", "issue_num"):
                    if k in row:
                        sample_ids.append(str(row[k])[:25])
                        break
            for k in ("label", "class", "category"):
                if k in row and row[k]:
                    label_dist[str(row[k])[:80]] += 1
                    break
            text = str(row.get("text") or row.get("description") or "")
            placeholders += len(re.findall(r"\[(?:NAME|EMAIL|ADDRESS|USERNAME|COMPANY|PASSWORD|AWS_ACCESS_KEY|PHONE|LOCATION)\]", text))
            potential_emails += len(re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text))
    return {
        "columns": headers, "rows": total, "blank_by_column": dict(blank),
        "first_ids": sample_ids, "label_distribution": dict(label_dist),
        "masked_placeholder_mentions": placeholders,
        "unmasked_email_pattern_matches": potential_emails,
    }


def zenodo() -> dict:
    record = {"source": "https://zenodo.org/records/7648117", "license": "CC-BY-4.0",
              "files": {}, "status": "success"}
    for filename, expected_md5 in ZENODO.items():
        path = RAW / "zenodo" / filename
        url = f"https://zenodo.org/records/7648117/files/{filename}?download=1"
        try:
            info = download(url, path)
            if info["md5"] != expected_md5:
                raise ValueError(f"checksum mismatch {filename}: got {info['md5']}, expected {expected_md5}")
            record["files"][filename] = {**info, "expected_md5": expected_md5, **csv_audit(path)}
        except Exception as err:
            record["files"][filename] = {"status": "failed", "error": str(err)[:450]}
            record["status"] = "incomplete"
    # source IDs are join keys, NEVER zip rows according to position.
    try:
        for split in ("train", "test"):
            x = RAW / "zenodo" / f"X_{split}.csv"
            y = RAW / "zenodo" / f"y_{split}.csv"
            with x.open(encoding="utf-8-sig", newline="") as xf, y.open(encoding="utf-8-sig", newline="") as yf:
                xr = list(csv.DictReader(xf))
                yr = list(csv.DictReader(yf))
            if not xr or not yr:
                raise ValueError("empty split")
            if "id" not in xr[0] or "id" not in yr[0]:
                raise ValueError("source X/y does not expose 'id'")
            xids = [r["id"] for r in xr]
            yids = [r["id"] for r in yr]
            if len(set(xids)) != len(xids) or len(set(yids)) != len(yids):
                raise ValueError("nonunique original ID")
            if set(xids) != set(yids):
                raise ValueError("X/y ID mismatch")
            record.setdefault("split_integrity", {})[split] = {
                "x_rows": len(xr), "y_rows": len(yr),
                "join_key": "id", "id_sets_match": True,
                "x_headers": list(xr[0]), "y_headers": list(yr[0])
            }
    except Exception as exc:
        record["split_integrity_error"] = str(exc)[:450]
        record["status"] = "incomplete"
    return record


def mendeley() -> dict:
    base = "https://data.mendeley.com/public-api/datasets/btm76zndnt"
    listing_url = f"{base}/files?folder_id=root&version=3"
    record = {"source": "https://data.mendeley.com/datasets/btm76zndnt/3",
              "listing_url": listing_url, "license": "CC-BY-4.0",
              "files": {}, "status": "success"}
    try:
        req = urllib.request.Request(listing_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=40) as res:
            listing = json.load(res)
        if isinstance(listing, dict):
            listing = listing.get("files") or listing.get("items") or listing.get("results") or []
        if not isinstance(listing, list):
            raise ValueError("unexpected listing shape")
        record["available_files"] = [str(x.get("filename", "")) for x in listing]
        desired = ("issues.csv", "issues_change_history.csv", "FEATURES.md", "EXAMPLE.md", "sample_utterances.csv")
        for filename in desired:
            matches = [x for x in listing if x.get("filename") == filename]
            if len(matches) != 1:
                record["files"][filename] = {"status": "not_available", "matches": len(matches)}
                record["status"] = "incomplete"
                continue
            details = matches[0].get("content_details") or {}
            url = details.get("download_url")
            if not url:
                raise ValueError(f"{filename}: no content_details.download_url")
            path = RAW / "mendeley" / filename
            try:
                info = download(url, path)
                record["files"][filename] = {**info, **(csv_audit(path) if filename.endswith(".csv") else {})}
            except Exception as exc:
                record["files"][filename] = {"status": "failed", "error": str(exc)[:450]}
                record["status"] = "incomplete"
    except Exception as exc:
        record["listing_error"] = f"{type(exc).__name__}: {exc}"[:450]
        record["status"] = "incomplete"
    return record


def main() -> int:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "validation_method": "download-originals+verify-zenodo-md5+aggregate-csv-schema",
        "privacy_note": "Only aggregate metadata is committed; raw files remain gitignored and only in ephemeral CI workspace.",
        "sources": {"zenodo": zenodo(), "mendeley": mendeley()},
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "zenodo_status": report["sources"]["zenodo"]["status"],
        "zenodo_rows": {k:v.get("rows") for k,v in report["sources"]["zenodo"]["files"].items()},
        "zenodo_splits": report["sources"]["zenodo"].get("split_integrity"),
        "mendeley_status": report["sources"]["mendeley"]["status"],
        "mendeley_rows": {k:v.get("rows") for k,v in report["sources"]["mendeley"]["files"].items()},
        "mendeley_error": report["sources"]["mendeley"].get("listing_error"),
        "audit_report": str(REPORT),
    }, indent=2))
    return 0 if all(s["status"] == "success" for s in report["sources"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
