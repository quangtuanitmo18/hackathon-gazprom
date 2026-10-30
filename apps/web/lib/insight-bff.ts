import {z} from "zod";
import type {BackendConfig} from "./api";
import {ReviewBffError} from "./review-bff";

/** No model-authored incident claims enter the browser unvalidated. */
const problemId=z.string().regex(/^PRB-[0-9]{6,}$/);
const digest=z.string().regex(/^[a-f0-9]{64}$/);
const evidenceKey=z.string().min(1).max(512);
const ticketSchema=z.object({
  ticket_key:evidenceKey,source_system:z.string(),source_ticket_id:z.string(),
  product_id:z.string().nullable(),component_id:z.string().nullable(),
  reported_version:z.string().nullable(),error_codes:z.array(z.string()),
  body_redacted:z.string().nullable(),
}).strict();
const proposalSchema=z.object({
  proposal_id:z.string().min(1),
  problem_id:problemId,scope_id:z.string().min(1),
  revision:z.number().int().min(2),
  evidence_ticket_keys:z.array(evidenceKey).min(2).max(5000),
  evidence_digest:digest,
  action_type:z.enum(["investigate_regression","improve_diagnostics","review_documentation"]),
  title:z.string().min(1).max(250),
  recommended_action:z.string().min(1).max(2000),
  root_cause_status:z.literal("unknown"),
  owner_team_id:z.null(),
  requires_human_review:z.literal(true),
  approval_status:z.enum(["pending","approved"]),
  mock_issue_id:z.union([z.null(),z.string().regex(/^MOCK-PRB-[0-9]{6,}-R[0-9]+$/)]),
}).strict().superRefine((p,ctx)=>{
  if(p.proposal_id!==p.problem_id+":v"+p.revision)
    ctx.addIssue({code:"custom",message:"proposal identity revision mismatch"});
  if(new Set(p.evidence_ticket_keys).size!==p.evidence_ticket_keys.length)
    ctx.addIssue({code:"custom",message:"duplicate evidence"});
  if(p.mock_issue_id&&p.approval_status!=="approved")
    ctx.addIssue({code:"custom",message:"mock issue without lead approval"});
});
const approvalSchema=z.object({
  proposal_id:z.string(),problem_id:problemId,scope_id:z.string(),
  revision:z.number().int().min(2),evidence_digest:digest,
  approved_by:z.string().min(1),reason:z.string(),
}).strict();
const mockIssueSchema=z.object({
  mock_issue_id:z.string().regex(/^MOCK-PRB-[0-9]{6,}-R[0-9]+$/),
  proposal_id:z.string(),problem_id:problemId,scope_id:z.string(),
  revision:z.number().int().min(2),evidence_digest:digest,
  created_by:z.string().min(1),reason:z.string(),
}).strict();
const actionSchema=z.object({
  problem_id:problemId,
  expected_revision:z.number().int().min(2),
  evidence_digest:digest,
  reason:z.string().trim().min(3).max(2000),
  operation_key:z.string().min(1).max(160),
}).strict();

export type InsightProposal=z.infer<typeof proposalSchema>;
export type InsightTicket=z.infer<typeof ticketSchema>;
export type InsightData={proposals:InsightProposal[],tickets:InsightTicket[]};
export type InsightAction=z.infer<typeof actionSchema>;

async function upstream<T>(
  config:BackendConfig,access:string,path:string,
  method:"GET"|"POST",parser:z.ZodType<T>,payload:unknown,
  transport:typeof fetch,
):Promise<T>{
  // The dynamic suffix is checked against the trusted action schema BEFORE
  // this helper is called. Never accept a caller-controlled URL/host.
  if(!/^\/internal\/v1\/insight-proposals(?:\/PRB-[0-9]{6,}\/\b(?:approve|mock-publish))?$/.test(path)
     && !/^\/internal\/v1\/review-tickets\?limit=50&offset=(?:0|[1-9][0-9]*)$/.test(path))
    throw new Error("insight upstream path not allowlisted");
  const url=new URL(path,config.baseUrl);
  if(url.origin!==config.baseUrl||url.hash||url.username||url.password)
    throw new Error("insight upstream origin mismatch");
  let response:Response;
  try{
    response=await transport(url.toString(),{
      method,cache:"no-store",redirect:"error",
      headers:{
        "Authorization":"Bearer "+access,
        "X-Internal-Token":config.token,
        "Content-Type":"application/json",
        "Accept":"application/json",
        "Cache-Control":"no-store",
      },
      ...(method==="POST"?{body:JSON.stringify(payload)}:{}),
      signal:AbortSignal.timeout(8000),
    });
  }catch{throw new ReviewBffError(503,"insight upstream unavailable");}
  if(!response.ok)throw new ReviewBffError(response.status,"insight upstream rejected request");
  let json:unknown;
  try{json=await response.json();}catch{throw new ReviewBffError(502,"invalid upstream JSON");}
  const result=parser.safeParse(json);
  if(!result.success)throw new ReviewBffError(502,"invalid upstream response");
  return result.data;
}

export async function fetchInsightData(
  config:BackendConfig,access:string,transport:typeof fetch=fetch,
):Promise<InsightData>{
  const proposals=await upstream(config,access,"/internal/v1/insight-proposals",
    "GET",z.array(proposalSchema).max(5000),undefined,transport);
  const tickets:InsightTicket[]=[];
  for(let offset=0;offset<=500;offset+=50){
    const page=await upstream(config,access,
      `/internal/v1/review-tickets?limit=50&offset=${offset}`,
      "GET",z.array(ticketSchema).max(50),undefined,transport);
    if(offset===500&&page.length)throw new ReviewBffError(503,"insight evidence capacity exceeded");
    tickets.push(...page);
    if(page.length<50)break;
  }
  const available=new Set(tickets.map(t=>t.ticket_key));
  if(available.size!==tickets.length)
    throw new ReviewBffError(502,"duplicate insight evidence identity");
  const ids=new Set<string>();
  for(const p of proposals){
    if(ids.has(p.proposal_id)||
       p.evidence_ticket_keys.some(key=>!available.has(key)))
      throw new ReviewBffError(502,"missing or duplicate insight evidence");
    ids.add(p.proposal_id);
  }
  return {proposals,tickets};
}

export async function submitInsightAction(
  config:BackendConfig,access:string,
  action:"approve"|"mock-publish",body:unknown,transport:typeof fetch=fetch,
){
  if(action!=="approve"&&action!=="mock-publish")
    throw new Error("invalid insight action");
  const validated=actionSchema.safeParse(body);
  if(!validated.success)throw new Error("invalid insight action payload");
  const payload=validated.data;
  return upstream(config,access,
    `/internal/v1/insight-proposals/${payload.problem_id}/${action}`,
    "POST",action==="approve"?approvalSchema:mockIssueSchema,{
      expected_revision:payload.expected_revision,
      evidence_digest:payload.evidence_digest,
      reason:payload.reason,
      operation_key:payload.operation_key,
    },transport);
}
