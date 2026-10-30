# Phase 21 — UI очереди неподтверждённой активности

**Статус:** предложено, без независимого approval. Наследует Draft PR #20 и #19. Нельзя merge/deploy без review.

## Problem / Goal
Новый внутренний `GET /internal/v1/unverified-activity` доступен в API, но reviewer видит только исходный `review-candidates`. Интегрировать отдельный блок **ранних непроверенных** пар в существующий Next.js reviewer console и обеспечить доступ к обоим доказательствам из PostgreSQL.

## Decisions
- Переиспользовать существующие Auth.js Keycloak OIDC session, серверный BFF `/api/review`, API allowlist, валидацию Zod, пагинацию `/review-tickets` (50× до 500), React console и стили. **Не** создавать второй клиент API, новую библиотеку или отдельную систему авторизации.
- BFF обращается по allowlisted `/internal/v1/unverified-activity` **только** из Node.js server, с `X-Internal-Token` и Bearer из зашифрованного Auth.js JWT; браузер получает только строгую публичную форму candidate.
- Строгий Zod (extra: reject) для `ticket_key_a/b`, `created_at_a/b`, `as_of`, `window_hours`, `recent_pattern`, 1/2 member counts, BM25 rank / categorical signals, literals `evidence_type=lexical_candidate`, `coverage_status=unknown_coverage`, `eligible_for_alert=false`. Проверять ссылочную целостность: оба ticket ID должны существовать в успешно прочитанных sanitized evidence pages; иначе **502**, не изображать кликабельный фантом.
- UI: отдельная секция **Ранняя активность — не подтверждено**, простая навигация «выбрать пару», время источников, краткий статус окна и видимые `не инцидент / не автоматическое уведомление`. Никаких «обнаружен инцидент», процентов/оценок confidence, Jira write.
- Existing `review-candidates` сохраняется — глобальная shortlist без окна; эти две очереди нельзя объединять/суммировать как число инцидентов. Клик только выбирает оба элемента в текущем независимом reviewer form.
- Ошибка upstream/invalid schema/partial evidence → fail closed, status 502/503; не маскировать как пустой список.
- E2E: seed двумя синтетическими русскими тикетами с корректным UTC event-time, показать раннюю пару на реальном Keycloak + PostgreSQL + Chromium, выбрать её, выполнить две независимые оценки и approval третьим аккаунтом; подтвердить отсутствие automatic merge и утечки токенов. Синтетические тесты не подтверждают качество инцидентного детектора.

## Limitations / alternatives
- Отдельный React dashboard для нового API отвергнут как дублирование auth и pipeline.
- `created_at` — event time, **не** `ingested_at`. Нет честного TTAI/replay, нет source coverage, нет статистического significance. Автоуведомления отключены.
- У существующего sanitizer ограниченная поддержка русских PII, бизнес-секретов; до реальных данных нужен DLP и проверенная политика retention.

## Approval
Product scope: backend + UI + E2E, один Draft PR. Независимый reviewer и решение владельца до merge.
