"""Strict source mapping; intentionally no assumptions about actual vendor schema."""
from datetime import datetime, timezone
from .schema import CanonicalTicket


def _id(value: object) -> str:
    result = str(value).strip() if value is not None else ""
    if not result:
        raise ValueError("missing or blank id")
    return result


def _timestamp(value: object) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise ValueError("invalid timestamp")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def parse_zenodo_split(x_rows: list[dict], y_rows: list[dict], split: str) -> list[CanonicalTicket]:
    """Join input and labels by stable ID; never zip unordered rows."""
    if split not in ("train", "test"):
        raise ValueError("unsupported split")
    labels: dict[str, str] = {}
    for row in y_rows:
        key = _id(row.get("id"))
        if key in labels:
            raise ValueError("duplicate label id")
        labels[key] = str(row["label"])
    seen: set[str] = set()
    result: list[CanonicalTicket] = []
    for row in x_rows:
        key = _id(row.get("id"))
        if key in seen:
            raise ValueError("duplicate ticket id")
        seen.add(key)
        if key not in labels:
            raise ValueError("unmatched ticket id and label")
        text = str(row.get("text") or "").strip()
        if not text:
            raise ValueError("empty ticket text")
        result.append(CanonicalTicket("zenodo-7648117-"+split, key, text, None, labels[key], None))
    if seen != set(labels):
        raise ValueError("unmatched label ids")
    return result


def parse_mendeley_rows(rows: list[dict]) -> list[CanonicalTicket]:
    """Illustrative source adapter; mapping must be confirmed against downloaded v3."""
    seen: set[str] = set()
    result: list[CanonicalTicket] = []
    for row in rows:
        key = _id(row.get("issue_id"))
        if key in seen:
            raise ValueError("duplicate issue id")
        seen.add(key)
        text = str(row.get("description") or "").strip()
        if not text:
            raise ValueError("empty ticket text")
        created = _timestamp(row.get("created_at"))
        product = row.get("project_id")
        result.append(CanonicalTicket("mendeley-btm76zndnt-v3", key, text, created, None, str(product) if product is not None else None))
    return result
