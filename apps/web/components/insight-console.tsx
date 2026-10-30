"use client";

import {useCallback,useEffect,useMemo,useState} from "react";
import {ClipboardCheck,LockKeyhole,RefreshCw,ShieldAlert} from "lucide-react";
import type {InsightData,InsightProposal} from "@/lib/insight-bff";

type Action="approve"|"mock-publish";

export function InsightConsole({displayName}:{displayName:string}){
  const [data,setData]=useState<InsightData|null>(null);
  const [selected,setSelected]=useState<string>("");
  const [reason,setReason]=useState("");
  const [busy,setBusy]=useState(false);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState<string|null>(null);
  const [notice,setNotice]=useState<string|null>(null);
  const reload=useCallback(async()=>{
    setLoading(true);
    // Do not retain or render a previously approved draft after a failed refresh.
    setData(null);
    try{
      const r=await fetch("/api/insights",{cache:"no-store"});
      if(!r.ok)throw Error(`HTTP ${r.status}`);
      const result=await r.json() as InsightData;
      if(!Array.isArray(result.proposals)||!Array.isArray(result.tickets))
        throw Error("Некорректный ответ");
      setData(result);setError(null);
    }catch(e){setError("Предложения не удалось загрузить: "+String(e));}
    finally{setLoading(false);}
  },[]);
  useEffect(()=>{void reload();},[reload]);

  const current=useMemo(()=>data?.proposals.find(p=>p.proposal_id===selected)
    ??data?.proposals[0],[data,selected]);
  const hasEvidence=Boolean(current && current.evidence_ticket_keys.every(
    key=>data?.tickets.some(t=>t.ticket_key===key)
  ));
  const canAct=Boolean(current && hasEvidence && !busy && !loading &&
    reason.trim().length>=3 && reason.length<=2000);
  async function act(action:Action,p:InsightProposal){
    if(!canAct || p.proposal_id!==current?.proposal_id)return;
    if(action==="approve"&&p.approval_status!=="pending")return;
    if(action==="mock-publish"&&(p.approval_status!=="approved"||p.mock_issue_id))return;
    setBusy(true);setError(null);setNotice(null);
    const payload={
      problem_id:p.problem_id,
      expected_revision:p.revision,
      evidence_digest:p.evidence_digest,
      reason:reason.trim(),
      operation_key:crypto.randomUUID(),
    };
    try{
      const result=await fetch("/api/insights",{
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({action,payload}),
      });
      if(!result.ok)throw Error(`HTTP ${result.status}`);
      setReason("");
      await reload();
      setNotice(action==="approve"
        ?"Ведущий эксперт одобрил точную ревизию. Mock-публикация ещё НЕ выполнена."
        :"Создан только внутренний MOCK issue. Реальных уведомлений нет.");
    }catch(e){
      setData(null); // no stale green button after a mutation error
      setError("Операция отклонена: "+String(e)+". Обновите страницу.");
    }finally{setBusy(false);}
  }

  return <div className="review-console">
    <div className="review-toolbar">
      <span><LockKeyhole size={17}/> Сеанс Keycloak: <strong>{displayName}</strong></span>
      <button type="button" className="review-refresh" onClick={()=>void reload()}
        disabled={loading||busy}><RefreshCw size={15}/> Обновить</button>
    </div>
    {loading&&<div className="review-message">Загрузка предложений…</div>}
    {error&&<div className="failure-panel" role="alert">{error}</div>}
    {notice&&<div className="review-success" role="status">{notice}</div>}
    {!loading&&!error&&!data?.proposals.length&&
      <div className="candidate-empty">Нет явно объединённых и подтверждённых групп. Сходство BM25 или одобренная связь без merge не создают предложения.</div>}
    <section className="review-recommendations" aria-label="Предложения для проверки">
      <div className="surface-heading"><div>
        <h2>Проверяемые предложения</h2>
        <p>Каждое предложение связано с конкретной ревизией Problem и точными evidence ID.</p>
      </div><span className="section-count">{data?.proposals.length??0} предложений</span></div>
      <div className="candidate-items">
        {data?.proposals.map((p,i)=><button type="button"
          className="candidate-option" key={p.proposal_id}
          aria-label={`Предложение к проверке ${i+1}: ${p.problem_id}`}
          disabled={busy||loading}
          onClick={()=>{setSelected(p.proposal_id);setReason("");setError(null);setNotice(null);}}>
          <span className="candidate-index">{String(i+1).padStart(2,"0")}</span>
          <span className="candidate-content">
            <strong>{p.title}</strong>
            <small>{p.evidence_ticket_keys.length} подтверждённых участников · Revision {p.revision}
              {" · "}{p.mock_issue_id?"Mock-публикация выполнена":
                p.approval_status==="approved"?"Одобрено · не опубликовано":"Нужна оценка lead"}
            </small>
          </span><span className="candidate-rank">{p.problem_id}</span>
        </button>)}
      </div>
    </section>
    {current && hasEvidence && <section className="surface-panel review-form" aria-label="Проверка доказательств и разрешений">
      <div className="surface-heading"><div>
        <h2>{current.title}</h2>
        <p>{current.recommended_action}</p>
      </div><ClipboardCheck size={20}/></div>
      <div className="insight-facts">
        <div>Root cause: <strong>Не установлена</strong></div>
        <div>Владелец: <strong>Не назначен</strong></div>
        <div>Статус: <strong>{current.mock_issue_id?"Mock-only":current.approval_status}</strong></div>
        <div>Evidence digest: <code>{current.evidence_digest}</code></div>
      </div>
      <div className="insight-evidence">
        {current.evidence_ticket_keys.map(key=>{
          const t=data?.tickets.find(row=>row.ticket_key===key);
          return <article className="review-ticket" key={key}>
            <div className="review-ticket-title">Подтверждённый источник</div>
            <code>{key}</code>
            <div className="review-fields">
              <span>Система: <strong>{t?.source_system}</strong></span>
              <span>Продукт: <strong>{t?.product_id||"Не указан"}</strong></span>
              <span>Версия: <strong>{t?.reported_version||"Не указана"}</strong></span>
            </div>
            <div className="review-body">{t?.body_redacted||"Нет очищенного текста"}</div>
          </article>;
        })}
      </div>
      <div className="explanation"><ShieldAlert size={18}/>
        <p>Подтверждено только членство тикетов в Problem, но не причина и не полный масштаб. Система не отправляет сообщения и не создаёт реальные задачи.</p>
      </div>
      <label className="review-field">Причина решения ведущего эксперта
        <textarea value={reason} onChange={e=>setReason(e.target.value)}
          rows={2} maxLength={2000}
          placeholder="Проверил точную ревизию и ссылки на источники…"/>
      </label>
      <div className="insight-actions">
        <button type="button" className="review-submit"
          disabled={!canAct||current.approval_status!=="pending"}
          onClick={()=>void act("approve",current)}>
          Одобрить предложение (без публикации)
        </button>
        <button type="button" className="review-submit"
          disabled={!canAct||current.approval_status!=="approved"||Boolean(current.mock_issue_id)}
          onClick={()=>void act("mock-publish",current)}>
          Опубликовать ТОЛЬКО в mock tracker
        </button>
      </div>
      {current.mock_issue_id&&<p className="review-hint" role="status">
        Внутренний тестовый issue: <strong>{current.mock_issue_id}</strong>
      </p>}
      <p className="review-hint">Обе операции требуют подписанного токена productpulse_review_lead. Кнопки не обходят проверки backend.</p>
    </section>}
  </div>;
}
