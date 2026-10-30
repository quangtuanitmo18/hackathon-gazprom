# Предлагаемая Webneft taxonomy — 7 примеров из стр. 6 PDF

**Важно:** исходный PDF приводит *примеры отдельных обращений*, а не вручную размеченную ground truth для объединения инцидентов. Нельзя пометить №1+№2, №6+№7 как `same_incident=true` только по их похожей области.

| № PDF | Симптом (краткий пересказ, без персональных данных) | Business journey | Proposed issue class | Product-team possibility | Почему НЕ подтверждено |
|---|---|---|---|---|---|
| 1 | В оферте неверная ОПФ: ИП вместо ООО; изменить невозможно | `contract_onboarding` | `data_validation_or_prefill` | Проверить ОПФ и формы | Неизвестна причина: исходные поля, API либо UI |
| 2 | На втором шаге оферты кнопка «Далее» не реагирует после заполнения | `contract_onboarding` | `ui_navigation_failure` | Проверить переход/валидацию | То же journey, что №1, **но не доказан один дефект** |
| 3 | Автомобиль пропал из списка и не добавляется как уже существующий | `vehicle_management` | `state_visibility_inconsistency` | Проверить видимость/индекс записи | Нет данных о первопричине |
| 4 | Срочная смена контактного номера в заявке к запланированной отгрузке | `shipment_operation` | `service_request` | Маршрут к оператору по SLA, возможный UX review | **Не** обязательно bug; deadline требует оперативного человека |
| 5 | Электронная очередь недоступна: HTTP 404 или «время не существует» | `electronic_queue_booking` | `booking_failure` | Проверить booking flow и slot availability | Одна запись не доказывает систематичность |
| 6 | При регистрации компании сообщает о существующем договоре; нужна помощь с доступом | `account_access` | `existing_contract_access` | Улучшить путь восстановления доступа | **Не** автоматически извлекать/раскрывать пароль |
| 7 | Не приходит SMS-код для восстановления пароля | `account_access` | `sms_recovery_failure` | Проверить доставку OTP и UX | То же journey, что №6, но другая техническая цепочка |

## Три независимых уровня классификации

1. **`same_problem_candidate`**: пары со схожим *конкретным* симптомом; это гипотеза до разметки. Не делать transitive union `A~B` и `B~C` => `A~C`.
2. **`business_topic`**: группировка по пользовательскому пути и продуктовой области. Например, №1 и №2 оба `contract_onboarding`, но могут быть разными defects.
3. **`actionable_signal`**: recurring issue, recurring wish, usability friction, process bottleneck, access request или single urgent operational ticket. Требуется независимое подтверждение значимости, времени и получателя.

## Консервативные operational rules
- Отображать **фактическую** частоту только из уникальных source-ticket keys и `observed_at` (в demo времена указаны только когда специально сгенерированы). Не использовать 7 примеров как временной ряд.
- Отделять `source_created_at` (бизнес-время) от `ingested_at` (момент появления у агента).
- Отдельно считать организации/пользователей **лишь если псевдонимизация и законность позволяют**; никакие метрики «уникальных клиентов» из 7 примеров недоступны.
- Qwen может предложить тему и draft; точный count, provenance, route и решения approval/notification выполняются доверенным кодом.
- №4: не задерживать срочную заявку ради группировки AI. №6/7: запрет раскрывать пароль, SMS-коды, токены в prompt/output.
- Для всех семи: `label_status=proposed_unadjudicated`, `same_incident_ground_truth=null`, `root_cause=null`, `recurrence_status=unknown`.

## Для оценки
Нужны отдельно human-adjudicated пары `same_problem`, классы `topic`, классы `actionable`, `product_route`, временны́е метки, межэкспертное согласие и эталонные product decisions. Семь PDF-примеров не заменяют gold set.
