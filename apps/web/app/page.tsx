import { ArrowDownRight, Database, ShieldCheck, Ticket } from "lucide-react";
import { ProblemTable } from "@/components/problem-table";
import { fetchProblems, readBackendConfig } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function Dashboard() {
  let problems;
  try {
    problems = await fetchProblems(readBackendConfig(process.env));
  } catch {
    return (
      <section className="content-stack">
        <div className="eyebrow">INBOX / СИСТЕМНОЕ СОСТОЯНИЕ</div>
        <h1>Обзор проблем</h1>
        <p className="lead">Достоверные данные о проблемах из ProductPulse Registry.</p>
        <div className="failure-panel" role="alert">
          <h2>Не удалось загрузить данные</h2>
          <p>Сервис ProductPulse недоступен или возвращает некорректный ответ. Мы не показываем нулевую статистику вместо ошибки.</p>
        </div>
      </section>
    );
  }
  const ticketCount = problems.reduce((sum, p) => sum + p.ticket_keys.length, 0);
  const multiTicket = problems.filter(p => p.ticket_keys.length > 1).length;
  return (
    <section className="content-stack">
      <div className="eyebrow">INCIDENT OPERATIONS / ОБЗОР</div>
      <div className="section-heading">
        <div><h1>Обзор проблем</h1><p className="lead">Единое пространство для анализа обращений и подтверждённых связей.</p></div>
        <div className="live-indicator"><span className="pulse-dot"/>Данные из PostgreSQL</div>
      </div>
      <div className="stat-grid">
        <div className="stat-card"><div className="stat-icon"><Database size={18}/></div><span>Активные группы</span><strong>{problems.length}</strong><small>Текущее состояние реестра</small></div>
        <div className="stat-card"><div className="stat-icon"><Ticket size={18}/></div><span>Связанные обращения</span><strong>{ticketCount}</strong><small>Уникальные записи в группах</small></div>
        <div className="stat-card"><div className="stat-icon"><ShieldCheck size={18}/></div><span>Группы с несколькими тикетами</span><strong>{multiTicket}</strong><small>Слияние требует ручного подтверждения</small></div>
      </div>
      <div className="section-title"><div><h2>Реестр проблем</h2><p>Реальные записи, без подстановки демонстрационных значений</p></div><span className="section-count">{problems.length} записей</span></div>
      <ProblemTable problems={problems}/>
      <div className="explanation"><ArrowDownRight size={17}/><p><strong>Как интерпретировать данные:</strong> одиночный тикет создаёт начальную запись. Это ещё не доказательство повторяющегося сбоя. Объединение разных обращений возможно только после независимой экспертной проверки.</p></div>
    </section>
  );
}
