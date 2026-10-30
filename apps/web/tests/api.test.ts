import { test } from "node:test";
import assert from "node:assert/strict";
import { fetchProblems, fetchAudit, fetchProblem, readBackendConfig, UpstreamError } from "../lib/api";

const config = {baseUrl:"http://127.0.0.1:8000", token:"private-server-only-test-token"};
const sample = {
  problem_id:"PRB-000001", scope_id:"demo", revision:1, status:"active",
  ticket_keys:["4:demo1:1"], parent_id:null, merged_into:null
};
function stub(body: unknown, code=200, record: {url?:string,headers?:Headers}={}) {
  return (async (input: URL | RequestInfo, init?: RequestInit) => {
    record.url = String(input);
    record.headers = new Headers(init?.headers);
    return new Response(JSON.stringify(body), {status:code, headers:{"Content-Type":"application/json"}});
  }) as typeof fetch;
}

test("backend credentials never appear in URL, only private upstream header",async()=>{
  const request: {url?:string,headers?:Headers}={};
  assert.deepEqual(await fetchProblems(config, stub([sample], 200, request)),[sample]);
  assert.equal(request.url,"http://127.0.0.1:8000/internal/v1/problems");
  assert.equal(request.headers?.get("X-Internal-Token"),config.token);
  assert.equal(request.headers?.get("Cache-Control"),"no-store");
});

test("audit and exact Problem detail are parsed and source scoped",async()=>{
  const record: {url?:string,headers?:Headers}={};
  const problem=await fetchProblem("PRB-000001",config,stub(sample,200,record));
  assert.equal(problem.problem_id,"PRB-000001");
  assert.equal(record.url,"http://127.0.0.1:8000/internal/v1/problems/PRB-000001");
  assert.deepEqual(await fetchAudit(config,stub([])),[]);
});

test("untrusted Problem ID cannot affect URL origin or add path fragments",async()=>{
  const record: {url?:string,headers?:Headers}={};
  await assert.rejects(fetchProblem("https://evil.test/path",config,stub(sample,200,record)),/invalid problem ID/);
  await assert.rejects(fetchProblem("../admin",config,stub(sample,200,record)),/invalid problem ID/);
  assert.equal(record.url,undefined);
});

test("non-200 upstream response throws, never invents zero counts",async()=>{
  await assert.rejects(fetchProblems(config,stub({},503)),UpstreamError);
  await assert.rejects(fetchProblem("PRB-000001",config,stub({},404)),UpstreamError);
});

test("invalid JSON schema is rejected, not silently accepted",async()=>{
  await assert.rejects(fetchProblems(config,stub([{...sample,revision:"bad"}])),/invalid upstream/);
});

test("empty list is a valid empty state",async()=>{
  assert.deepEqual(await fetchProblems(config,stub([])),[]);
});

test("backend configuration must not contain credentials in URL",()=>{
  assert.throws(()=>readBackendConfig({}),/PRODUCTPULSE_/);
  assert.throws(()=>readBackendConfig({
    PRODUCTPULSE_BACKEND_URL:"https://user:pass@api.test",
    PRODUCTPULSE_INTERNAL_TOKEN:"very-long-secret"
  }),/URL/);
  assert.deepEqual(readBackendConfig({
    PRODUCTPULSE_BACKEND_URL:config.baseUrl,
    PRODUCTPULSE_INTERNAL_TOKEN:config.token,
  }),config);
});
