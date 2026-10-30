import {test} from "node:test";
import assert from "node:assert/strict";
import {fetchInsightData, submitInsightAction} from "../lib/insight-bff";
import type {BackendConfig} from "../lib/api";

const config:BackendConfig={baseUrl:"http://127.0.0.1:8000",token:"ci-fake-service-token-32bytes-only"};
const access="signed-oidc-access-test-opaque";
const digest="a".repeat(64);
const proposal={
  proposal_id:"PRB-000001:v2",problem_id:"PRB-000001",scope_id:"test-scope",
  revision:2,evidence_ticket_keys:["synthetic1:a","synthetic1:b"],
  evidence_digest:digest,action_type:"investigate_regression",
  title:"Проверить повторяющуюся проблему PRB-000001 (2 обращения)",
  recommended_action:"Проверить воспроизведение и наличие регрессии; причина пока неизвестна.",
  root_cause_status:"unknown",owner_team_id:null,requires_human_review:true,
  approval_status:"pending",mock_issue_id:null,
};
const ticket=(key:string)=>({
  ticket_key:key,source_system:"synthetic",source_ticket_id:key,
  product_id:null,component_id:null,reported_version:null,error_codes:[],
  body_redacted:"Synthetic redacted text",
});
function transportFor(proposals:unknown=[proposal],tickets:unknown=[ticket("synthetic1:a"),ticket("synthetic1:b")]){
  const requests:{url:string,headers:Headers,method:string,body:unknown}[]=[];
  const transport=(async(input:RequestInfo|URL,init?:RequestInit)=>{
    const url=String(input);
    requests.push({url,headers:new Headers(init?.headers),method:init?.method||"GET",body:init?.body});
    const rows=url.includes("/insight-proposals")?proposals:tickets;
    return new Response(JSON.stringify(rows),{status:200,headers:{"Content-Type":"application/json"}});
  }) as typeof fetch;
  return {transport,requests};
}

test("server BFF retrieves scoped insight drafts with both credentials without leaking them",async()=>{
  const {transport,requests}=transportFor();
  const data=await fetchInsightData(config,access,transport);
  assert.equal(data.proposals.length,1);
  assert.equal(data.tickets.length,2);
  assert.deepEqual(data.proposals[0].evidence_ticket_keys,proposal.evidence_ticket_keys);
  assert.ok(requests.some(r=>r.url===config.baseUrl+"/internal/v1/insight-proposals"));
  for(const r of requests){
    assert.equal(r.headers.get("Authorization"),"Bearer "+access);
    assert.equal(r.headers.get("X-Internal-Token"),config.token);
    assert.equal(r.method,"GET");
  }
  assert.ok(!JSON.stringify(data).includes(access));
  assert.ok(!JSON.stringify(data).includes(config.token));
});

test("strict schema rejects fabricated root cause, owner, confidence, approval and issue",async()=>{
  for(const invalid of [
    {...proposal,confidence:0.9},
    {...proposal,root_cause_status:"confirmed"},
    {...proposal,owner_team_id:"secret-manager"},
    {...proposal,requires_human_review:false},
    {...proposal,evidence_ticket_keys:["synthetic1:a"]},
    {...proposal,evidence_digest:"wrong"},
    {...proposal,mock_issue_id:"JIRA-900"},
    {...proposal,approval_status:"not_approved"},
    {...proposal,revision:1},
  ]){
    const {transport}=transportFor([invalid]);
    await assert.rejects(fetchInsightData(config,access,transport),/invalid upstream/);
  }
});

test("missing evidence member fails closed, never renders a partially inspectable proposal",async()=>{
  const {transport}=transportFor([proposal],[ticket("synthetic1:a")]);
  await assert.rejects(fetchInsightData(config,access,transport),/evidence/);
});

test("insight list retrieves citation on page 2 and no empty success when upstream fails",async()=>{
  const {transport,requests}=transportFor();
  const paginated=(async(input:RequestInfo|URL,init?:RequestInit)=>{
    const u=String(input);
    if(u.includes("/insight-proposals"))return new Response(JSON.stringify([proposal]));
    if(u.includes("offset=50"))return new Response(JSON.stringify([ticket("synthetic1:b")]));
    return new Response(JSON.stringify([...Array.from({length:49},(_,i)=>ticket("other-"+i)),ticket("synthetic1:a")]));
  }) as typeof fetch;
  const data=await fetchInsightData(config,access,paginated);
  assert.equal(data.tickets.length,51);
  assert.equal(data.proposals.length,1);
  const bad=(async(input:RequestInfo|URL)=>String(input).includes("insight-proposals")?
    new Response("failure",{status:503}):new Response("[]")) as typeof fetch;
  await assert.rejects(fetchInsightData(config,access,bad),/upstream/);
  assert.ok(requests.length===0); // no accidental old transport used
});

test("POST approve uses trusted fixed route and exact validated payload",async()=>{
  const calls:{url?:string,body?:string,headers?:Headers}={};
  const mock=(async(input:RequestInfo|URL,init?:RequestInit)=>{
    calls.url=String(input);
    calls.body=String(init?.body);
    calls.headers=new Headers(init?.headers);
    return new Response(JSON.stringify({
      proposal_id:proposal.proposal_id,problem_id:proposal.problem_id,
      scope_id:proposal.scope_id,revision:proposal.revision,evidence_digest:digest,
      approved_by:"oidc:lead",reason:"Reviewed evidence independently",
    }),{status:201});
  }) as typeof fetch;
  const payload={problem_id:"PRB-000001",expected_revision:2,evidence_digest:digest,
                 reason:"Reviewed evidence independently",operation_key:"key-for-approval"};
  const row=await submitInsightAction(config,access,"approve",payload,mock);
  assert.equal(row.proposal_id,proposal.proposal_id);
  assert.equal(calls.url,config.baseUrl+"/internal/v1/insight-proposals/PRB-000001/approve");
  assert.equal(calls.headers?.get("X-Internal-Token"),config.token);
  assert.equal(calls.headers?.get("Authorization"),"Bearer "+access);
  assert.ok(!calls.body?.includes(config.token));
});

test("mock publish is separate exact path and forbidden until backend approval",async()=>{
  const payload={problem_id:"PRB-000001",expected_revision:2,evidence_digest:digest,
                 reason:"Test mock publish only",operation_key:"publish-key"};
  const paths:string[]=[];
  const refused=(async(input:RequestInfo|URL)=>{
    paths.push(String(input));return new Response("requires approval",{status:409});
  }) as typeof fetch;
  await assert.rejects(submitInsightAction(config,access,"mock-publish",payload,refused),/upstream/);
  assert.equal(paths[0],config.baseUrl+"/internal/v1/insight-proposals/PRB-000001/mock-publish");
});

test("forged paths, scope, giant/fake fields and invalid operations never reach backend",async()=>{
  let called=0;
  const no=(async()=>{called++;throw Error("unexpected network")}) as typeof fetch;
  const base={problem_id:"PRB-000001",expected_revision:2,evidence_digest:digest,
    reason:"Some explicit review reason",operation_key:"idempotent-action-key"};
  for(const bad of [
    {...base,problem_id:"../../admin"},
    {...base,problem_id:"PRB-000001/approve"},
    {...base,scope_id:"other"},
    {...base,owner_team_id:"admin"},
    {...base,evidence_digest:"ff"},
    {...base,expected_revision:0},
    {...base,reason:""},
    {...base,operation_key:""},
  ]){
    await assert.rejects(submitInsightAction(config,access,"approve",bad,no),/invalid/i);
  }
  await assert.rejects(submitInsightAction(config,access,"delete" as never,base,no),/invalid/i);
  assert.equal(called,0);
});
