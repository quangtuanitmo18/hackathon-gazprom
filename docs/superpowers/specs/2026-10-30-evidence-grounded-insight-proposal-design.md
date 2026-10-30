# Phase 22 — Evidence-grounded Insight Proposal Agent (design)

**Статус:** proposal, awaiting independent review; Draft PR stacked on #21. Без merge, deploy и внешних writes.

## Задача и границы
Преобразовать **явно вручную merged** (complete-link + lead-approved) активные Problems в предложение для команды продукта. Непроверенные BM25 пары и approved-but-unmerged пары **никогда** не создают Proposal. Нельзя выдумывать root cause, product owner, confidence, происхождение и эффект. Сигналы Phases 19–21 не гарантируют полноту истории и не доказывают статистическую значимость.

## Проектный выбор
- **Детерминированный agent/controller, с ограниченным model adapter (optional, no provider credentials)**: read trusted Problem -> prepare evidence ID allowlist -> optionally parse strict JSON model suggestion (action enum only) -> validate/fallback -> draft -> separate signed Human Approval -> explicit simulated tracker publication. Для безопасного MVP без реального LLM используются те же этапы и deterministic fallback, а не скрытый автозапрос к AI.
- Ни LangGraph, ни новый broker/ORM не нужны для этой короткой линейной цепочки. При асинхронной эксплуатации можно ввести durable orchestration, но не в этом PR.
- **No free-form model summary/claim**: action_type из фиксированного перечня, evidence IDs должны совпадать с подтверждённым Problem; root_cause_status=unknown, owner_team_id=null, title/action собираются из проверенного шаблона. Модель не получает сырые тикеты и не может указывать собственные ссылки/URL/команды; prompt injection не меняет policy.
- Использовать уже имеющийся JSONB transactional `ProblemRegistry` для `ProposalApproval` и `MockIssue` (пара tenant/problem/revision + evidence digest) и audit, без внешней Jira. Прототип ограничен масштабом JSONB/5000-ticket cap, это не production issue tracker.

## API
- `GET /internal/v1/insight-proposals`: service token + tenant-matched signed reviewer OIDC; только confirmed active Problems >=2. No state change; returns typed grounded drafts `proposal_id`, `problem_id`, `scope_id`, `revision`, `evidence_ticket_keys`, `evidence_digest`, `action_type`, `title`, `recommended_action`, `root_cause_status=unknown`, `owner_team_id=null`, `requires_human_review=true`, `approval_status=pending|approved`, `mock_issue_id` only after explicit publish.
- `POST /internal/v1/insight-proposals/{problem_id}/approve`: service token + tenant-matched `productpulse_review_lead` JWT. Request {expected_revision, evidence_digest, reason, operation_key}. Check trusted snapshot, expected revision, digest, active multi-member membership, lead identity. Write auditable approval in a transaction. No mock publish.
- `POST /internal/v1/insight-proposals/{problem_id}/mock-publish`: same lead role; requires approval for identical active revision+digest; explicit operation_key+reason. Persist **internal mock issue only**, idempotent `scope:problem_id:insight_published:revision`, audit once; never issue network requests.

## Invariants and security
- Scope never from request, no attacker-controlled issue URL/action/body accepted.
- Deterministic `evidence_digest` derived from scope, Problem ID, revision and sorted member IDs, preventing stale consent reuse after split/remerge.
- Source tickets may contain instructions; model input is only trusted structured IDs / metadata, not ticket text. Model draft schema strict; unrecognized evidence, fabricated fields/root cause, unsafe JSON => safe fixed recommendation. Cannot exceed evidence allowlist.
- Approval is not event of publication; mock publication requires second explicit action and authenticated lead. Reusing operation_key with modified data fails, safe exact retries return identical mock issue; approval invalid after revision change/split.
- No PII in proposal/audit beyond source-scoped ticket keys, which can still be sensitive in real datasets. No accuracy/ROI claims.
- Tests include unauthorized JWT/scope, no unverified pair, stale revision/evidence, malformed/hostile model outputs, approve vs publish separation, idempotency/retry/rollback + persisted PostgreSQL audit.

## Tradeoffs
- Dynamic read-only drafts are NOT persisted immutable authored narrative; deterministic action chosen at generation and revalidated on publish. This keeps scope bounded; a future editorial API must freeze explicit human-edited title/action and hash revision.
- No live provider integration, dashboard approval UI, real tracker writes or production DLP. These are separate reviewed increments.
