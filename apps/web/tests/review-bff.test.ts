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
  assert.deepEqual(results,{tickets:[],reviews:[],candidates:[]});
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
