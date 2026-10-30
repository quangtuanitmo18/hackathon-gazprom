import { test } from "node:test";
import assert from "node:assert/strict";
import {
  requireActiveReviewerAuth, requireSameOriginPost,
  fetchReviewerData, submitReviewerAction,
} from "../lib/review-bff";
import type { BackendConfig } from "../lib/api";

const cfg:BackendConfig={baseUrl:"http://127.0.0.1:8000",token:"super-long-internal-bff-secret-only"};
const now=1800000000;
const jwt={reviewerAccessToken:"signed-opaque-OIDC-access-token",reviewerExpiresAt:now+300};

test("shared Basic mode cannot sign or submit human reviews",()=>{
  assert.throws(()=>requireActiveReviewerAuth("basic",jwt,now),/OIDC/);
  assert.throws(()=>requireActiveReviewerAuth(undefined,jwt,now),/OIDC/);
});
test("missing and expired encrypted JWT access token denied",()=>{
  assert.throws(()=>requireActiveReviewerAuth("oidc",null,now),/OIDC/);
  assert.throws(()=>requireActiveReviewerAuth("oidc",{...jwt,reviewerExpiresAt:now-1},now),/expired/);
  assert.equal(requireActiveReviewerAuth("oidc",jwt,now),jwt.reviewerAccessToken);
});
test("reject foreign Origin even when valid encrypted session exists",()=>{
  assert.throws(()=>requireSameOriginPost("https://evil.test","https://review.example.org"),/origin/);
  assert.throws(()=>requireSameOriginPost(null,"https://review.example.org"),/origin/);
  assert.doesNotThrow(()=>requireSameOriginPost("https://review.example.org","https://review.example.org"));
});
test("fetch scoped evidence forwards both tokens privately to fixed upstream origin",async()=>{
  const record:{url?:string,auth?:string,service?:string}={};
  const transport=(async(input:RequestInfo|URL,init?:RequestInit)=>{
    record.url=String(input);
    const h=new Headers(init?.headers);
    record.auth=h.get("Authorization")||undefined;
    record.service=h.get("X-Internal-Token")||undefined;
    return new Response(JSON.stringify([]),{status:200,headers:{"Content-Type":"application/json"}});
  }) as typeof fetch;
  const results=await fetchReviewerData(cfg,jwt.reviewerAccessToken,transport);
  assert.deepEqual(results,{tickets:[],reviews:[],candidates:[],activity:[]});
  assert.equal(record.auth,"Bearer "+jwt.reviewerAccessToken);
  assert.equal(record.service,cfg.token);
  assert.ok(record.url?.startsWith(cfg.baseUrl+"/internal/v1/"));
});
test("mutating review uses allowlisted path and only BFF-provided OIDC token",async()=>{
  const record:{url?:string,body?:string,service?:string}={};
  const transport=(async(input:RequestInfo|URL,init?:RequestInit)=>{
    record.url=String(input);record.body=String(init?.body);
    record.service=new Headers(init?.headers).get("X-Internal-Token")||undefined;
    return new Response(JSON.stringify({pair_id:"a",status:"awaiting_second_review",reviewer_ids:["oidc:reviewer"]}),
      {status:201,headers:{"Content-Type":"application/json"}});
  }) as typeof fetch;
  await submitReviewerAction(cfg,jwt.reviewerAccessToken,"vote",{
    ticket_key_a:"synthetic1:a",ticket_key_b:"synthetic1:b",
    label:"same_incident",rationale:"Compared independent logs",operation_key:"abcd-1234",
  },transport);
  assert.equal(record.url,cfg.baseUrl+"/internal/v1/reviews");
  assert.equal(record.service,cfg.token);
  assert.ok(!record.body?.includes(cfg.token));
});
test("wrong action and malformed payload are not forwarded",async()=>{
  let calls=0;const transport=(async()=>{calls++;throw Error("called")}) as typeof fetch;
  await assert.rejects(submitReviewerAction(cfg,jwt.reviewerAccessToken,"merge" as never,{},transport),/action/);
  await assert.rejects(submitReviewerAction(cfg,jwt.reviewerAccessToken,"vote",{reviewer_id:"forged"},transport),/invalid/);
  assert.equal(calls,0);
});
test("upstream error cannot be silently represented as successful human vote",async()=>{
  const transport=(async()=>new Response("error",{status:503})) as typeof fetch;
  await assert.rejects(fetchReviewerData(cfg,jwt.reviewerAccessToken,transport),/upstream/);
});

test("malformed Origin is denied with 403 rather than internal error",()=>{
  assert.throws(()=>requireSameOriginPost("not a URL","https://review.example.org"),(e:unknown)=>{
    assert.equal((e as {status:number}).status,403);
    return true;
  });
});

test("server validates candidate queue schema, never accepts fabricated confidence",async()=>{
  const fake={ticket_key_a:"synthetic1:a",ticket_key_b:"synthetic1:b",rank:1,signals:["lexical_overlap"]};
  const transport=(async(input:RequestInfo|URL)=>{
    const url=String(input);
    return new Response(JSON.stringify(url.includes("review-candidates")?[fake]:[]),
      {status:200,headers:{"Content-Type":"application/json"}});
  }) as typeof fetch;
  const results=await fetchReviewerData(cfg,jwt.reviewerAccessToken,transport);
  assert.equal(results.candidates.length,1);
  assert.deepEqual(results.candidates[0],fake);
  const fabricated=(async(input:RequestInfo|URL)=>{
    const url=String(input);
    return new Response(JSON.stringify(url.includes("review-candidates")?[{...fake,confidence:0.99}]:[]),
      {status:200,headers:{"Content-Type":"application/json"}});
  }) as typeof fetch;
  await assert.rejects(fetchReviewerData(cfg,jwt.reviewerAccessToken,fabricated),/invalid upstream/);
});

test("reviewer evidence fetches beyond first 50 so ranked pair remains selectable",async()=>{
  const makeTicket=(i:number)=>({
    ticket_key:"synthetic"+i,source_system:"synthetic",source_ticket_id:String(i),
    product_id:"erp",component_id:"auth",reported_version:"2.1",
    error_codes:[],body_redacted:"Synthetic HTTP 403",
  });
  const seen:string[]=[];
  const transport=(async(input:RequestInfo|URL)=>{
    const url=String(input);seen.push(url);
    const body=url.includes("/review-tickets")
      ? (url.includes("offset=50")?[makeTicket(51)]:Array.from({length:50},(_,i)=>makeTicket(i+1)))
      : [];
    return new Response(JSON.stringify(body),{status:200,headers:{"Content-Type":"application/json"}});
  }) as typeof fetch;
  const data=await fetchReviewerData(cfg,jwt.reviewerAccessToken,transport);
  assert.equal(data.tickets.length,51);
  assert.ok(data.tickets.some(t=>t.ticket_key==="synthetic51"));
  assert.ok(seen.some(url=>url.includes("offset=50")));
});

const earlyPair={
  ticket_key_a:"synthetic1:a",ticket_key_b:"synthetic1:b",
  created_at_a:"2026-10-30T14:00:00Z",created_at_b:"2026-10-30T14:10:00Z",
  as_of:"2026-10-30T15:00:00Z",window_hours:24,
  recent_pattern:"both_current",current_member_count:2,previous_member_count:0,
  rank:1,signals:["lexical_overlap","same_product"],
  evidence_type:"lexical_candidate",coverage_status:"unknown_coverage",
  eligible_for_alert:false,
};
const evidence=(id:string)=>({
  ticket_key:id,source_system:"synthetic",source_ticket_id:id,
  product_id:null,component_id:null,reported_version:null,error_codes:[],
  body_redacted:"Synthetic redacted test",
});

test("BFF fetches activity via allowlisted server-only URL, keeps both credentials secret",async()=>{
  const requested:string[]=[];
  const transport=(async(input:RequestInfo|URL,init?:RequestInit)=>{
    const url=String(input);requested.push(url);
    const h=new Headers(init?.headers);
    assert.equal(h.get("Authorization"),"Bearer "+jwt.reviewerAccessToken);
    assert.equal(h.get("X-Internal-Token"),cfg.token);
    assert.equal(init?.cache,"no-store");
    const body=url.includes("/unverified-activity")?[earlyPair]:
      url.includes("/review-tickets")?[evidence(earlyPair.ticket_key_a),evidence(earlyPair.ticket_key_b)]:[];
    return new Response(JSON.stringify(body),{status:200});
  }) as typeof fetch;
  const data=await fetchReviewerData(cfg,jwt.reviewerAccessToken,transport);
  assert.equal(data.activity.length,1);
  assert.equal(data.activity[0].recent_pattern,"both_current");
  assert.equal(data.activity[0].eligible_for_alert,false);
  assert.ok(requested.some(u=>u===cfg.baseUrl+"/internal/v1/unverified-activity"));
  assert.ok(!JSON.stringify(data).includes(cfg.token));
  assert.ok(!JSON.stringify(data).includes(jwt.reviewerAccessToken));
});

test("BFF refuses invented confidence, alert flags, incident IDs, timestamps and extra properties",async()=>{
  for(const bad of [
    {...earlyPair,confidence:0.91},
    {...earlyPair,eligible_for_alert:true},
    {...earlyPair,incident_id:"fabricated"},
    {...earlyPair,created_at_a:"today"},
    {...earlyPair,ticket_key_b:earlyPair.ticket_key_a},
    {...earlyPair,recent_pattern:"confirmed"},
  ]){
    const transport=(async(input:RequestInfo|URL)=>{
      const url=String(input);
      const body=url.includes("/unverified-activity")?[bad]:
        url.includes("/review-tickets")?[evidence(earlyPair.ticket_key_a),evidence(earlyPair.ticket_key_b)]:[];
      return new Response(JSON.stringify(body),{status:200});
    }) as typeof fetch;
    await assert.rejects(
      fetchReviewerData(cfg,jwt.reviewerAccessToken,transport),
      /invalid upstream response/
    );
  }
});

test("BFF fails closed when early pair lacks either evidence record across pages",async()=>{
  const transport=(async(input:RequestInfo|URL)=>{
    const url=String(input);
    const body=url.includes("/unverified-activity")?[earlyPair]:
      url.includes("/review-tickets")?[evidence(earlyPair.ticket_key_a)]:[];
    return new Response(JSON.stringify(body),{status:200});
  }) as typeof fetch;
  await assert.rejects(fetchReviewerData(cfg,jwt.reviewerAccessToken,transport),/evidence|invalid/i);
});

test("BFF resolves early activity ticket on page 2, after complete paginated evidence retrieval",async()=>{
  const seen:string[]=[];
  const transport=(async(input:RequestInfo|URL)=>{
    const url=String(input);seen.push(url);
    const body=url.includes("/unverified-activity")?[earlyPair]:
      url.includes("/review-tickets")?
        (url.includes("offset=50")?[evidence(earlyPair.ticket_key_b)]:
          [...Array.from({length:49},(_,i)=>evidence("other-"+i)),evidence(earlyPair.ticket_key_a)]):[];
    return new Response(JSON.stringify(body),{status:200});
  }) as typeof fetch;
  const data=await fetchReviewerData(cfg,jwt.reviewerAccessToken,transport);
  assert.equal(data.tickets.length,51);
  assert.equal(data.activity.length,1);
  assert.ok(seen.some(url=>url.endsWith("/review-tickets?limit=50&offset=50")));
});

test("BFF never silently hides a failed early-activity service as empty result",async()=>{
  const transport=(async(input:RequestInfo|URL)=>{
    return String(input).includes("/unverified-activity")?
      new Response("upstream failure",{status:503}):
      new Response("[]",{status:200});
  }) as typeof fetch;
  await assert.rejects(fetchReviewerData(cfg,jwt.reviewerAccessToken,transport),/upstream/);
});
