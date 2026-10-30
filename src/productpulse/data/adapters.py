"""Explicit adapters for Zenodo split pairs and Mendeley reporter messages.

The source publishers may change their CSV columns. We intentionally fail
closed instead of guessing indexes, categories or timestamps. These adapters
consume parsed rows; file decoding and controlled access happen upstream.
"""

from collections.abc import Mapping
from math import isfinite
from typing import Any

from productpulse.data.schema import CanonicalTicket


def _require_fields(row: Mapping[str, Any], fields: set[str], source: str) -> None:
    missing = sorted(fields - set(row))
    if missing:
        raise ValueError(f"{source}: missing required fields: {', '.join(missing)}")


def _required_id(value: Any, source: str) -> str:
    if value is None or isinstance(value, bool) or (
        isinstance(value, float) and not isfinite(value)
    ):
        raise ValueError(f"{source}: invalid blank ID")
    value = str(value).strip()
    if not value:
        raise ValueError(f"{source}: invalid blank ID")
    return value


def _required_text(value: Any, source: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{source}: empty or missing text")
    return value


def _index_unique(rows: list[dict], source: str, *, id_column: str) -> dict[str, dict]:
    indexed: dict[str, dict] = {}
    for row in rows:
        _require_fields(row, {id_column}, source)
        identifier = _required_id(row[id_column], source)
        if identifier in indexed:
            raise ValueError(f"{source}: duplicate source ID {identifier}")
        indexed[identifier] = row
    return indexed


def parse_zenodo_split(
    x_rows: list[dict], y_rows: list[dict], split: str
) -> list[CanonicalTicket]:
    """Join Zenodo X/y on source id, preserving original X order and split.

    This v0 adapter uses explicit normalized keys: id/text and id/label.
    A source-schema mapping must be inspected against the actual CSV headers
    before claiming compatibility with the original downloadable files.
    """
    if split not in {"train", "test"}:
        raise ValueError("split must be the author-provided train or test")
    x_by_id = _index_unique(x_rows, "Zenodo X", id_column="id")
    y_by_id = _index_unique(y_rows, "Zenodo y", id_column="id")
    for row in x_rows:
        _require_fields(row, {"text"}, "Zenodo X")
    for row in y_rows:
        _require_fields(row, {"label"}, "Zenodo y")
    if x_by_id.keys() != y_by_id.keys():
        raise ValueError("Zenodo X/y unmatched source IDs; refusing positional alignment")
    records = []
    for identifier, x in x_by_id.items():
        label = y_by_id[identifier]["label"]
        if label is None or (isinstance(label, float) and not isfinite(label)) or not str(label).strip():
            raise ValueError(f"Zenodo y: missing or invalid label for source ID {identifier}")
        records.append(
            CanonicalTicket(
                source="zenodo-it-support-v2",
                source_id=identifier,
                text_redacted=_required_text(x["text"], "Zenodo X"),
                source_label=str(label).strip(),
                split=split,
            )
        )
    return records


def parse_mendeley_rows(rows: list[dict]) -> list[CanonicalTicket]:
    """Map the processed *reporter_messages* view; NOT raw issues.csv.

    issue_type/status/resolution are source metadata, not supervised intent
    labels; product id is only taken when issue_proj is actually present.
    """
    indexed = _index_unique(rows, "Mendeley reporter_messages", id_column="issue_id")
    records = []
    for identifier, row in indexed.items():
        _require_fields(row, {"text"}, "Mendeley reporter_messages")
        product = row.get("issue_proj")
        records.append(
            CanonicalTicket(
                source="mendeley-help-desk-v3-reporter-messages",
                source_id=identifier,
                text_redacted=_required_text(row["text"], "Mendeley reporter_messages"),
                created_at=row.get("issue_created") or None,
                product_id=str(product).strip() if product is not None and str(product).strip() else None,
            )
        )
    return records
