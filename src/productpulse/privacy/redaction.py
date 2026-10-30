"""Best-effort PII redaction BEFORE persistent ticket ingestion.

Uses Apache-2.0 OSS scrubadub for broad common PII classes. Supplemental
regex handles high-risk developer credentials; NOT certified Russian NER.
Never log raw text or put rejected input in exception messages.
"""
from __future__ import annotations

import re

import scrubadub

from productpulse.data.canonical import CanonicalTicketV1


class UnsafeIdentity(ValueError):
    """A source-scoped identity or metadata field may contain sensitive values."""


# Explicit private-key blocks first, including multiline keys.
_PRIVATE_KEY = re.compile(
    r"-----BEGIN (?:[A-Z0-9 ]* )?PRIVATE KEY-----.*?-----END (?:[A-Z0-9 ]* )?PRIVATE KEY-----",
    flags=re.IGNORECASE | re.DOTALL,
)
_BEARER = re.compile(r"(?i)\bBearer\s+[a-z0-9._~+/-]{8,}")
_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_-]?key|password|passwd|secret|client[_-]?secret|access[_-]?token)"
    r"\s*[:=]\s*(?:[\"']?)[^\s\"']{6,}"
)
_EMAIL = re.compile(r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}")


def redact_text(text: str) -> str:
    if not text:
        return text
    value = _PRIVATE_KEY.sub("{{SECRET}}", text)
    value = _BEARER.sub("Bearer {{SECRET}}", value)
    value = _ASSIGNMENT.sub(lambda m: f"{m.group(1)}={{SECRET}}", value)
    # scrubadub provides multiple detectors; we DO NOT claim support for
    # Russian names, organizations and local address patterns.
    return scrubadub.clean(value)


def sanitize_ticket(ticket: CanonicalTicketV1) -> CanonicalTicketV1:
    """Make a sanitized canonical copy while preserving source identity.

    Refuse identity/metadata where masking would change referential meaning.
    Persist only the returned copy. Never surface rejected raw input in logs.
    """
    identity_values = [
        ticket.source_system, ticket.source_ticket_id, ticket.provenance_id,
        ticket.product_id, ticket.component_id, ticket.reported_version,
        ticket.pseudonymous_user_id, *ticket.error_codes,
    ]
    for item in identity_values:
        if not item:
            continue
        if (_EMAIL.search(item) or _PRIVATE_KEY.search(item)
                or _BEARER.search(item) or _ASSIGNMENT.search(item)
                or redact_text(item) != item):
            raise UnsafeIdentity("sensitive content in source identity or metadata")
    title = redact_text(ticket.title) if ticket.title else ticket.title
    body = redact_text(ticket.body_redacted) if ticket.body_redacted else ticket.body_redacted
    return ticket.model_copy(update={"title":title,"body_redacted":body})
