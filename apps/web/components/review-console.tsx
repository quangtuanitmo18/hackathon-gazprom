"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { ClipboardCheck, LockKeyhole, RefreshCw, ShieldAlert, ShieldCheck } from "lucide-react";
import type { ReviewData, ReviewProgress, ReviewTicket } from "@/lib/review-bff";

type Label="same_incident"|"related_topic"|"different_incident"|"uncertain";
const options:{value:Label;label:string;description:string}[]=[
  {value:"same_incident",label:"Одна техническая проблема",description:"Подтверждена общая причина сбоя"},
  {value:"related_topic",label:"Связанная тема",description:"Одна тема, но связь причин не доказана"},
  {value:"different_incident",label:"Разные инциденты",description:"Разные причины или контекст"},
  {value:"uncertain",label:"Недостаточно данных",description:"Нужны новые логи или воспроизведение"},
];
const statusText:Record<ReviewProgress["status"],string>={
  awaiting_first_review:"Ожидается первая оценка",
  awaiting_second_review:"Ожидается второй эксперт",
  ready_for_lead:"Ожидает ведущего эксперта",
  disputed:"Расхождение оценок",
  uncertain:"Недостаточно данных",
  classified:"Оценка завершена без связи",
  approved:"Связь подтверждена ведущим экспертом",
};

function pairId(a:string,b:string){return JSON.stringify([a,b].sort());}

function TicketPanel({ticket,label}:{ticket:ReviewTicket|undefined,label:string}){
  return <div className="review-ticket">
    <div className="review-ticket-title">{label}</div>
    {!ticket?<div className="empty-state">Выберите обращение</div>:<>
      <code>{ticket.ticket_key}</code>
      <div className="review-fields">
        <span>Продукт: <strong>{ticket.product_id||"Не указан"}</strong></span>
        <span>Компонент: <strong>{ticket.component_id||"Не указан"}</strong></span>
        <span>Версия: <strong>{ticket.reported_version||"Не указана"}</strong></span>
      </div>
      <div className="review-body">{ticket.body_redacted||"Нет очищенного текста обращения"}</div>
      <div className="review-error-codes">{ticket.error_codes.length?ticket.error_codes.join(", "):"Коды ошибок не указаны"}</div>
    </>}
  </div>;
}

export function ReviewConsole({displayName}:{displayName:string}){
  const [data,setData]=useState<ReviewData|null>(null);
  const [first,setFirst]=useState("");
  const [second,setSecond]=useState("");
  const [label,setLabel]=useState<Label>("uncertain");
  const [rationale,setRationale]=useState("");
  const [reason,setReason]=useState("");
  const [busy,setBusy]=useState(false);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState<string|null>(null);
  const [success,setSuccess]=useState<string|null>(null);
  const reload=useCallback(async()=>{
    setLoading(true);
    try{
      const resp=await fetch("/api/review",{cache:"no-store"});
      if(!resp.ok)throw Error(`HTTP ${resp.status}`);
      const payload=await resp.json() as ReviewData;
      if(!Array.isArray(payload.tickets)||!Array.isArray(payload.reviews)||
        !Array.isArray(payload.candidates)||!Array.isArray(payload.activity))
        throw Error("Некорректные данные");
      setData(payload);setError(null);
    }catch(e){
      // A malformed/partial/unauthorized refresh must not leave stale pair
      // suggestions clickable behind an error banner.
      setData(null);
      setError(`Не удалось загрузить данные: ${String(e)}`);
    }
    finally{setLoading(false);}
  },[]);
  useEffect(()=>{void reload()},[reload]);
  const a=data?.tickets.find(t=>t.ticket_key===first);
  const b=data?.tickets.find(t=>t.ticket_key===second);
  const pair=useMemo(()=>first&&second&&first!==second?pairId(first,second):null,[first,second]);
  const progress=pair?data?.reviews.find(r=>r.pair_id===pair):undefined;
  // Selecting a different pair resets stale free-text decisions. The reviewer
  // must consciously inspect both redacted evidence panels before voting.
  const choosePair=(aKey:string,bKey:string)=>{
    if(busy||loading)return;
    if(aKey===bKey || !data?.tickets.some(t=>t.ticket_key===aKey) ||
       !data.tickets.some(t=>t.ticket_key===bKey)){
      setError("Доказательства пары недоступны. Обновите страницу.");return;
    }
    setFirst(aKey);setSecond(bKey);
    setLabel("uncertain");setRationale("");setReason("");
    setError(null);setSuccess(null);
  };
  const canVote=Boolean(a&&b&&first!==second&&!busy&&rationale.trim().length>=3);
  const canApprove=Boolean(progress?.status==="ready_for_lead"&&a&&b&&reason.trim().length>=3&&!busy);
  async function act(action:"vote"|"approve"){
    if(!a||!b||a.ticket_key===b.ticket_key||busy)return;
    setBusy(true);setError(null);setSuccess(null);
    const payload=action==="vote"
      ? {ticket_key_a:first,ticket_key_b:second,label,rationale,operation_key:crypto.randomUUID()}
      : {ticket_key_a:first,ticket_key_b:second,reason,operation_key:crypto.randomUUID()};
    try{
      const resp=await fetch("/api/review",{
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({action,payload}),
      });
      if(!resp.ok)throw Error(`HTTP ${resp.status}`);
      setSuccess(action==="vote"?"Решение записано. Для подтверждения нужен ещё один независимый эксперт и ведущий.":"Подтверждение ведущего эксперта записано; проблемы не объединены автоматически.");
      await reload();
    }catch(e){setError(`Операция отклонена: ${String(e)}. Проверьте роль, предыдущие решения или состояние пары.`);}
    finally{setBusy(false);}
  }
  return <div className="review-console">
    <div className="review-toolbar">
      <span><ShieldCheck size={17}/> Личный вход: <strong>{displayName}</strong></span>
      <button type="button" className="review-refresh" onClick={()=>void reload()} disabled={busy||loading}><RefreshCw size={15}/> Обновить</button>
    </div>
    {loading&&<div className="review-message">Загрузка обращений и статусов…</div>}
    {error&&<div className="failure-panel" role="alert">{error}</div>}
    {success&&<div className="review-success" role="status">{success}</div>}
    <section className="review-recommendations" aria-label="Ранняя активность — не подтверждено">
      <div className="surface-heading">
        <div>
          <h2>Ранняя активность — не подтверждено</h2>
          <p>Пары по сходству текста и времени обращения. Это гипотезы для проверки, а не обнаруженные инциденты.</p>
        </div>
        <span className="section-count">{data?.activity?.length??0} пар для проверки</span>
      </div>
      {data?.activity?.length ? (
        <div className="candidate-items">
          {data.activity.map((item,i)=>(
            <button
              type="button"
              key={item.ticket_key_a+"|"+item.ticket_key_b}
              className="candidate-option"
              aria-label={`Ранняя пара ${i+1}: открыть доказательства`}
              onClick={()=>choosePair(item.ticket_key_a,item.ticket_key_b)}
              disabled={busy||loading}
            >
              <span className="candidate-index">{String(i+1).padStart(2,"0")}</span>
              <span className="candidate-content">
                <strong>{item.ticket_key_a} ↔ {item.ticket_key_b}</strong>
                <small>{item.recent_pattern==="both_current"
                  ?"Оба обращения в текущем окне"
                  :"Новое обращение и обращение из предыдущего окна"}
                  {" · "}BM25 rank #{item.rank} · покрытие истории не подтверждено
                </small>
                <small>UTC: {new Date(item.created_at_a).toLocaleString("ru-RU",{timeZone:"UTC"})}
                  {" ↔ "}{new Date(item.created_at_b).toLocaleString("ru-RU",{timeZone:"UTC"})}
                </small>
                <small>Лексические признаки: {item.signals.join(", ")}</small>
              </span>
              <span className="candidate-rank">Не инцидент · без автооповещения</span>
            </button>
          ))}
        </div>
      ) : !loading&&!error&&(
        <div className="candidate-empty">
          Нет неподтверждённых пар в текущем временном окне. Это не означает, что в системе нет инцидентов.
        </div>
      )}
    </section>
    <section className="review-recommendations" aria-label="Рекомендованные пары">
      <div className="surface-heading">
        <div>
          <h2>Рекомендованные пары</h2>
          <p>BM25: лексическое сходство для очереди экспертов, не вероятность общего root cause</p>
        </div>
        <span className="section-count">{data?.candidates.length??0} кандидатов</span>
      </div>
      {data?.candidates.length ? (
        <div className="candidate-items">
          {data.candidates.slice(0,10).map((candidate,i)=>(
            <button
              type="button"
              key={candidate.ticket_key_a+"|"+candidate.ticket_key_b}
              className="candidate-option"
              aria-label={`Предложение ${i+1}: выбрать пару тикетов`}
              onClick={()=>choosePair(candidate.ticket_key_a,candidate.ticket_key_b)}
              disabled={busy||loading}
            >
              <span className="candidate-index">{String(i+1).padStart(2,"0")}</span>
              <span className="candidate-content">
                <strong>{candidate.ticket_key_a} ↔ {candidate.ticket_key_b}</strong>
                <small>
                  {candidate.signals.map(signal=>({
                    lexical_overlap:"Общие термины",same_product:"Один продукт",
                    same_component:"Один компонент",shared_error_code:"Общий код ошибки",
                  })[signal]||signal).join(" · ")}
                </small>
              </span>
              <span className="candidate-rank">BM25 rank #{candidate.rank}</span>
            </button>
          ))}
        </div>
      ) : (
        <div className="candidate-empty">
          Система пока не нашла пар с пересечением терминов. Можно выбрать тикеты вручную ниже.
        </div>
      )}
    </section>
    <div className="review-selectors">
      <label>Обращение A <select value={first} onChange={e=>setFirst(e.target.value)} aria-label="Первое обращение">
        <option value="">Выберите тикет…</option>
        {data?.tickets.map(t=><option key={t.ticket_key} value={t.ticket_key}>{t.source_system}: {t.source_ticket_id}</option>)}
      </select></label>
      <label>Обращение B <select value={second} onChange={e=>setSecond(e.target.value)} aria-label="Второе обращение">
        <option value="">Выберите тикет…</option>
        {data?.tickets.map(t=><option key={t.ticket_key} value={t.ticket_key}>{t.source_system}: {t.source_ticket_id}</option>)}
      </select></label>
    </div>
    <div className="review-tickets"><TicketPanel ticket={a} label="Доказательства A"/><TicketPanel ticket={b} label="Доказательства B"/></div>
    <div className="review-state">
      <ClipboardCheck size={18}/><div><strong>{progress?statusText[progress.status]:"Пара ещё не оценена"}</strong>
        <p>{progress?.reviewer_ids.length||0} независимых оценок зарегистрировано · При споре автоматического подтверждения нет</p></div>
    </div>
    <section className="surface-panel review-form">
      <div className="surface-heading"><div><h2>Моя независимая оценка</h2><p>Решение фиксируется под проверенным OIDC subject; чужие оценки не раскрываются заранее.</p></div><LockKeyhole size={19}/></div>
      <div className="review-options">{options.map(o=><label key={o.value} className="review-choice">
        <input type="radio" checked={label===o.value} onChange={()=>setLabel(o.value)} name="pair-label"/>
        <span><strong>{o.label}</strong><small>{o.description}</small></span></label>)}</div>
      <label className="review-field">Обоснование по фактам
        <textarea rows={3} value={rationale} onChange={e=>setRationale(e.target.value)} maxLength={3000}
          placeholder="Например: совпадают стек ошибки, версия и воспроизведение; общая причина подтверждена…" />
      </label>
      <button className="review-submit" type="button" onClick={()=>void act("vote")} disabled={!canVote}>Отправить независимую оценку</button>
    </section>
    <section className="surface-panel review-form">
      <div className="surface-heading"><div><h2>Подтверждение ведущего эксперта</h2><p>Только третья независимая личность с ролью productpulse_review_lead</p></div><ShieldAlert size={19}/></div>
      <label className="review-field">Причина подтверждения
        <textarea rows={2} value={reason} onChange={e=>setReason(e.target.value)} maxLength={3000}
          placeholder="Проверил журнал, воспроизведение и независимость выводов…" />
      </label>
      <button className="review-submit" type="button" onClick={()=>void act("approve")} disabled={!canApprove}>Подтвердить связь (без автоматического merge)</button>
      {progress?.status!=="ready_for_lead"&&<p className="review-hint">Кнопка доступна только при двух согласованных оценках same_incident.</p>}
    </section>
    <div className="explanation"><ShieldCheck size={17}/><p>Этот интерфейс не вычисляет точность AI и не создаёт Jira-задачи. Текст предполагается очищенным при загрузке; до работы с реальными данными необходимо проверить процесс редактирования PII и секретов.</p></div>
  </div>;
}
