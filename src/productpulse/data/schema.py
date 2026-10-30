"""Canonical, privacy-minimized ticket contract for offline dataset research."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CanonicalTicket:
    source: str
    source_id: str
    text_redacted: str
    created_at: datetime | None
    source_label: str | None
    product_id: str | None
