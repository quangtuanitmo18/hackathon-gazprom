import Link from "next/link";
import { ArrowLeft, ClipboardCheck, Clock3, GitMerge, Layers3, Tag } from "lucide-react";
import { notFound } from "next/navigation";
import { fetchProblem, readBackendConfig, UpstreamError } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function ProblemDetail({
  params,
}: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let problem;
  try {
    problem = await fetchProblem(id, readBackendConfig(process.env));
  } catch (error) {
    if (error instanceof UpstreamError && error.code === 404 || error instanceof Error && error.message === "invalid problem ID") notFound();
    return (
      <section className="content-stack">
        <h1>Данные недоступны</h1>
        <div className="failure-panel" role="alert">Не удалось получить актуальную информацию о проблеме. Попробуйте позже.</div>
        <Link href="/" className="back-link"><ArrowLeft size={16}/>К списку проблем</Link>
      </section>
    );
  }
  return (
    <section className="content-stack">
      <Link href="/" className="back-link"><ArrowLeft size={16}/>Реестр проблем</Link>
      <div className="eyebrow">PROBLEM REGISTRY / КАРТОЧКА</div>
      <div className="section-heading">
        <div><h1>{problem.problem_id}</h1><p className="lead">Подтверждённая структура группы обращений и её происхождение.</p></div>
        <span className="status-pill"><span className="pulse-dot"/>{problem.status === "active" ? "Активна" : "Объединена"}</span>
      </div>
      <div className="detail-grid">
        <div className="detail-card"><Tag size={18}/><span>Область данных</span><strong>{problem.scope_id}</strong></div>
        <div className="detail-card"><Layers3 size={18}/><span>Обращений в группе</span><strong>{problem.ticket_keys.length}</strong></div>
        <div className="detail-card"><Clock3 size={18}/><span>Ревизия реестра</span><strong>v{problem.revision}</strong></div>
      </div>
      <section className="surface-panel">
        <div className="surface-heading"><div><h2>Связанные обращения</h2><p>Оригинальные идентификаторы с пространством источника</p></div><ClipboardCheck size={20}/></div>
        {problem.ticket_keys.length ? (
          <div className="ticket-list">{problem.ticket_keys.map((key,i) => (
            <div key={key} className="ticket-row"><span className="ticket-index">{String(i+1).padStart(2,"0")}</span><code>{key}</code><span className="ticket-tag">Source ID</span></div>
          ))}</div>
        ) : <div className="empty-state">Обращения отсутствуют.</div>}
      </section>
      <section className="surface-panel">
        <div className="surface-heading"><div><h2>История структуры</h2><p>Идентификаторы групп и их происхождение</p></div><GitMerge size={20}/></div>
        <div className="metadata-list">
          <div><span>Основная группа</span><strong>{problem.problem_id}</strong></div>
          <div><span>Родительская группа</span><strong>{problem.parent_id ?? "Не указана"}</strong></div>
          <div><span>Объединена с</span><strong>{problem.merged_into ?? "—"}</strong></div>
        </div>
      </section>
      <div className="explanation"><ClipboardCheck size={17}/><p>Этот экран не показывает текст тикета, диагноз или доказательства root cause: текущий API пока предоставляет только структуру реестра. Для экспертного подтверждения потребуется отдельный защищённый review-интерфейс.</p></div>
    </section>
  );
}
