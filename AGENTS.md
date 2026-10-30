# Agent / contributor instructions

Этот файл — проектная политика для людей и кодовых агентов. Приоритет: официальное ТЗ и требования команды → утверждённый design spec → implementation plan → рабочие соглашения.

## Superpowers workflow (обязательный)

1. **Brainstorm before features:** зафиксировать цели, non-goals, ограничения, сравнить альтернативы. Если требуются существенные пользовательские решения — получить согласование.
2. **Design before code:** спецификация в docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md; явно помечать assumptions/decisions и статус approval.
3. **Plan before implementation:** план в docs/superpowers/plans/YYYY-MM-DD-<feature>.md, связанный с design spec; точные файлы, интерфейсы, небольшие задачи, негативные тесты и команды проверки.
4. **Isolated branch:** не писать непосредственно в main. Для локального исполнителя применять superpowers:using-git-worktrees, если доступно. Pull Request — обязательный review gate.
5. **TDD:** сначала тест на требование или отказ (RED), минимальная реализация (GREEN), затем рефакторинг; фиксировать реальные команды и их вывод. Синтетические demo-данные не являются evidence performance.
6. **Verification before completion:** нельзя утверждать «всё работает» без свежих команд build/test/lint и результатов. Для documentation-only PR проверять ссылки/пути/статус утверждения и отсутствие неподтверждённых заявлений.
7. **Review:** самостоятельная проверка — минимальный порог; приветствуется независимый reviewer. Critical/Important issues закрыть до merge.

См. установленные skills Superpowers: brainstorming, writing-plans, test-driven-development, executing-plans, verification-before-completion, requesting-code-review, finishing-a-development-branch.

## Working agreements

- Главный язык бизнес-документации: **русский**; имена кода, API и технические интерфейсы — английский.
- Один Pull Request = одна проверяемая цель; к нему прикладывать test evidence, risks и ссылку на decision/spec.
- Не хранить реальные тикеты, ФИО, email, ключи, токены, корпоративные логи или закрытые датасеты в GitHub.
- В model outputs разделять **symptom**, **suspected cause** и **confirmed cause**.
- Любое утверждение вида «AI снизил трудозатраты на X%» требует ссылку на фактический experiment run; до этого писать «цель» или «сценарная оценка».
- При выборе метрик отдельно считать false merges, missed incidents, false alerts, human review и долю abstentions.
- Для сравнения моделей использовать фиксированный holdout; не оценивать на тренировочных или синтетически сгенерированных клонах.
- Корпоративная интеграция по умолчанию mock/read-only. Внешние write-effects только через policy + audit + approval.
- Для изменений архитектуры создавать ADR/decision log entry; не удалять старые решения молча.
- Не объявлять self-hosted/on-prem развертывание «готовым» без инфраструктурной проверки.

## Definition of Done

- У задачи есть сценарий успеха и отказа, воспроизводимая проверка.
- Все указанные тесты выполнены и их результаты сохранены.
- Инварианты данных, права доступа и failure modes проверены.
- Документация/ADR актуальны; PR описывает ограничения.
- Reviewer одобрил PR; merge только после review.
