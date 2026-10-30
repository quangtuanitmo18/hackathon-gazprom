"""Privacy guard: use OSS PII detector; no secrets or mail in persisted snapshot."""
from productpulse.data.canonical import CanonicalTicketV1
from productpulse.privacy.redaction import sanitize_ticket, UnsafeIdentity

def ticket(text,**extra):
    return CanonicalTicketV1(source_system="synthetic",source_ticket_id="RU-10",
                             provenance_id="fixture",body_redacted=text,**extra)

def test_email_and_bearer_secret_are_removed_before_storage():
    t=ticket("Свяжитесь с alex@example.com. Authorization: Bearer abcDEF123456789.secret.token")
    clean=sanitize_ticket(t)
    assert "alex@example.com" not in (clean.body_redacted or "")
    assert "abcDEF123456789" not in (clean.body_redacted or "")
    assert "Свяжитесь" in (clean.body_redacted or "")
    assert "{{" in (clean.body_redacted or "")

def test_secret_assignment_and_private_key_redaction():
    t=ticket("Ошибка: api_key=sk_1234567890abcdef\n-----BEGIN PRIVATE KEY-----\naBc123SECRET\n-----END PRIVATE KEY-----")
    clean=sanitize_ticket(t)
    result=clean.body_redacted or ""
    assert "sk_1234567890abcdef" not in result
    assert "aBc123SECRET" not in result
    assert "BEGIN PRIVATE KEY" not in result
    assert "{{SECRET}}" in result

def test_redact_title_and_preserve_technical_context():
    clean=sanitize_ticket(ticket("Ошибка HTTP 403 в ERP версии 2.1",title="Письмо alex@example.com"))
    assert "alex@example.com" not in clean.title
    assert "HTTP 403" in clean.body_redacted
    assert "2.1" in clean.body_redacted

def test_repeat_ingest_is_deterministically_sanitized():
    t=ticket("Пользователь john@example.net не может войти HTTP 403")
    first=sanitize_ticket(t)
    second=sanitize_ticket(t)
    assert first==second
    assert sanitize_ticket(first)==first

def test_source_ids_rejected_not_mangled_silently():
    t=ticket("Обычный сбой",title="Вход",source_ticket_id="user@example.com") if False else None
    bad=CanonicalTicketV1(source_system="synthetic",source_ticket_id="user@example.com",
                           provenance_id="fixture",body_redacted="Ошибка сервера")
    try:sanitize_ticket(bad)
    except UnsafeIdentity:pass
    else:raise AssertionError("PII in source ticket id accepted")

def test_raw_technical_logs_without_pii_remain_useful():
    t=ticket("Ошибки в POST /api/v1/erp: HTTP 403; trace_id=1234abcd, версия 2.1")
    clean=sanitize_ticket(t)
    assert "HTTP 403" in clean.body_redacted
    assert "2.1" in clean.body_redacted
