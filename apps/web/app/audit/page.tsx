import { ClipboardList, Clock3, LockKeyhole } from "lucide-react";
import { fetchAudit, readBackendConfig } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function AuditPage() {
  let events;
  try { events = await fetchAudit(readBackendConfig(process.env)); }
  catch {
    return (
      <section className="content-stack"><div className="eyebrow">AUDIT / ЖУРНАЛ</div><h1>Журнал изменений</h1>
        <div className="failure-panel" role="alert">Не удалось загрузить журнал. История не подменяется пустым списком.</div></section>
    );
  }
  return (
    <section className="content-stack">
      <div className="eyebrow">AUDIT / ЖУРНАЛ СОБЫТИЙ</div>
      <div className="section-heading"><div><h1>Журнал изменений</h1><p className="lead">События регистрации, подтверждения и корректировки групп.</p></div><span className="section-count">{events.length} событий</span></div>
      <div className="surface-panel">
        <div className="surface-heading"><div><h2>Хронология операций</h2><p>Сортировка по последовательности, установленной в PostgreSQL</p></div><ClipboardList size={20}/></div>
        {events.length ? (
          <div className="audit-list">{events.map(event=>(
            <article key={event.sequence} className="audit-event">
              <div className="audit-mark"><Clock3 size={17}/></div>
              <div className="audit-content">
                <div className="audit-line"><strong>{event.kind}</strong><span>#{event.sequence}</span></div>
                <p>{event.reason || "Системное событие без пояснения"}</p>
                <div className="audit-meta"><span>Инициатор: {event.actor}</span><span>Операция: {event.operation_key}</span><span>{event.occurred_at}</span></div>
              </div>
            </article>
          ))}</div>
        ) : <div className="empty-state"><LockKeyhole size={26}/><strong>Записей ещё нет</strong><span>После регистрации обращений появятся события реестра.</span></div>}
      </div>
      <div className="explanation"><LockKeyhole size={17}/><p>Журнал ведётся в приложении с сохранением в PostgreSQL. Это не неизменяемый WORM-архив: администраторам базы данных необходима отдельная политика ограничений и аудита.</p></div>
    </section>
  );
}
