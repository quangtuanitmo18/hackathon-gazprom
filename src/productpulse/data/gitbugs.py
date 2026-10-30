"""Conservative duplicate-link parsing for the GitBugs research corpus.

Missing links are unknown labels; nothing in this module manufactures
negative pairs or assumes links prove a common underlying root cause.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from collections.abc import Iterable, Mapping

_TOKEN = re.compile(r"""(?:[0-9]+|'[0-9]+'|"[0-9]+")\Z""")
_LIMIT = 20000


def parse_duplicate_ids(raw: str | None) -> tuple[str, ...]:
    """Accept numeric ID or comma-separated numeric IDs, optionally list-like.

    This is a strict parser for the inspected GitBugs mapping format, not a
    general Python literal parser. It never runs code or calls eval().
    """
    if raw is None:
        return ()
    if not isinstance(raw, str):
        raise ValueError("duplicate ID field must be a string")
    value = raw.strip()
    if not value or value == "[]":
        return ()
    if len(value) > _LIMIT:
        raise ValueError("duplicate mapping too large")
    if value.startswith("["):
        if not value.endswith("]"):
            raise ValueError("malformed list-shaped duplicate field")
        value = value[1:-1].strip()
        if not value:
            return ()
    elif value.endswith("]"):
        raise ValueError("malformed duplicate field")
    items: list[str] = []
    for token in value.split(","):
        token = token.strip()
        if not _TOKEN.fullmatch(token):
            raise ValueError("duplicate field contains invalid token")
        if token.startswith(("'", '"')):
            token = token[1:-1]
        items.append(token)
    return tuple(items)


@dataclass(frozen=True)
class DuplicateLinkAudit:
    positives: frozenset[tuple[str, str]]
    reciprocal_or_repeated: int
    orphan_count: int
    self_link_count: int
    malformed_count: int
    unlabeled_count: int
    link_index_validated: bool


def normalize_positive_links(
    rows: Iterable[Mapping[str, object]],
    available_ids: set[str] | None,
) -> DuplicateLinkAudit:
    """Normalize positive relations and audit broken source links.

    Both endpoints must be present in available_ids when an index is supplied.
    Duplicate-of direction is not used to infer root cause or missing negatives.
    """
    links: set[tuple[str, str]] = set()
    repeated = orphans = self_links = malformed = unlabeled = 0
    for row in rows:
        try:
            raw_source = row.get("Issue id")
            if raw_source is None:
                raise ValueError("missing Issue id")
            source = str(raw_source).strip()
            if not source.isascii() or not source.isdigit():
                raise ValueError("invalid source id")
            targets = parse_duplicate_ids(
                row.get("Duplicate id", row.get("Duplicates"))  # type: ignore[arg-type]
            )
        except ValueError:
            malformed += 1
            continue
        if not targets:
            unlabeled += 1
            continue
        for target in targets:
            if source == target:
                self_links += 1
                continue
            if available_ids is not None and (
                source not in available_ids or target not in available_ids
            ):
                orphans += 1
                continue
            # Numeric order without int() conversion limits; preserve source IDs as strings.
            def numeric_key(value: str) -> tuple[int, str, str]:
                normalized = value.lstrip("0") or "0"
                return (len(normalized), normalized, value)

            pair = tuple(sorted((source, target), key=numeric_key))
            if pair in links:
                repeated += 1
            links.add(pair)
    return DuplicateLinkAudit(
        positives=frozenset(links),
        reciprocal_or_repeated=repeated,
        orphan_count=orphans,
        self_link_count=self_links,
        malformed_count=malformed,
        unlabeled_count=unlabeled,
        link_index_validated=available_ids is not None,
    )
