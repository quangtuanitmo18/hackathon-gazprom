import { z } from "zod";
import type { BackendConfig } from "./api";

type EncryptedAuthToken = { reviewerAccessToken?: unknown; reviewerExpiresAt?: unknown } | null;

const ticketSchema=z.object({
  ticket_key:z.string(),source_system:z.string(),source_ticket_id:z.string(),
  product_id:z.string().nullable(),component_id:z.string().nullable(),
  reported_version:z.string().nullable(),error_codes:z.array(z.string()),
  body_redacted:z.string().nullable(),
}).strict();

const progressSchema=z.object({
  pair_id:z.string(),reviewer_ids:z.array(z.string()),
  status:z.enum(["awaiting_first_review","awaiting_second_review","ready_for_lead","disputed","uncertain","classified","approved"]),
}).strict();
const candidateSchema=z.object({
  ticket_key_a:z.string(),ticket_key_b:z.string(),rank:z.number().int().positive(),
  signals:z.array(z.enum(["lexical_overlap","same_product","same_component","shared_error_code"])),
}).strict().refine(x=>x.ticket_key_a!==x.ticket_key_b,{message:"invalid candidate pair"});

const approvalSchema=z.object({pair_id:z.string(),ticket_keys:z.tuple([z.string(),z.string()]),reviewer_ids:z.tuple([z.string(),z.string()])}).strict();
const voteSchema=z.object({
  ticket_key_a:z.string().min(1).max(512),
  ticket_key_b:z.string().min(1).max(512),
  label:z.enum(["same_incident","related_topic","different_incident","uncertain"]),
  rationale:z.string().trim().min(3).max(3000),
  operation_key:z.string().min(1).max(160),
}).strict().refine(x=>x.ticket_key_a!==x.ticket_key_b,{message:"cannot self-review",path:["ticket_key_b"]});
const approveSchema=z.object({
  ticket_key_a:z.string().min(1).max(512),
  ticket_key_b:z.string().min(1).max(512),
  reason:z.string().trim().min(3).max(3000),
  operation_key:z.string().min(1).max(160),
}).strict().refine(x=>x.ticket_key_a!==x.ticket_key_b,{message:"cannot self-approve",path:["ticket_key_b"]});

export type ReviewTicket=z.infer<typeof ticketSchema>;
export type ReviewProgress=z.infer<typeof progressSchema>;
export type ReviewInput=z.infer<typeof voteSchema>;
export type LeadInput=z.infer<typeof approveSchema>;
export type ReviewCandidate=z.infer<typeof candidateSchema>;
export type ReviewData={tickets:ReviewTicket[],reviews:ReviewProgress[],candidates:ReviewCandidate[]};
export class ReviewBffError extends Error {
  constructor(public readonly status:number,message:string){super(message);}
}

/** Separate auth mode gates: shared Basic auth can NEVER attest human independence. */
export function requireActiveReviewerAuth(
  mode:string|undefined,token:EncryptedAuthToken,now=Math.floor(Date.now()/1000)
):string {
  if(mode!=="oidc")throw new ReviewBffError(403,"OIDC reviewer login required");
  const access=token?.reviewerAccessToken;
  const expiry=token?.reviewerExpiresAt;
  if(typeof access!=="string"||access.length<5||typeof expiry!=="number")
    throw new ReviewBffError(401,"OIDC reviewer login required");
  if(expiry<=now+10)throw new ReviewBffError(401,"OIDC reviewer token expired; sign in again");
  return access;
}

/** Auth.js cookie blocks CSRF, but additionally reject cross-origin mutations. */
export function requireSameOriginPost(origin:string|null,expectedOrigin:string):void {
  // A malformed Origin is a FORBIDDEN request, never an unhandled URL error.
  if(!origin)throw new ReviewBffError(403,"invalid request origin");
  try{
    const expected=new URL(expectedOrigin).origin;
    const incoming=new URL(origin).origin;
    if(origin!==incoming||incoming!==expected)
      throw new ReviewBffError(403,"invalid request origin");
  }catch{
    throw new ReviewBffError(403,"invalid request origin");
  }
}

async function request<T>(
  config:BackendConfig,access:string,path:string,method:"GET"|"POST",parser:z.ZodType<T>,
  payload:unknown,transport:typeof fetch
):Promise<T>{
  const allowed=new Set(["/internal/v1/review-tickets","/internal/v1/review-candidates","/internal/v1/reviews","/internal/v1/reviews/approve"]);
  if(!allowed.has(path))throw new Error("review upstream path not allowlisted");
  const url=new URL(path,config.baseUrl);
  if(url.origin!==config.baseUrl)throw new Error("invalid backend origin");
  let response:Response;
  try {
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
  }catch{throw new ReviewBffError(503,"review upstream unavailable");}
  if(!response.ok)throw new ReviewBffError(response.status,"review upstream rejected request");
  let data:unknown;
  try{data=await response.json();}catch{throw new ReviewBffError(502,"invalid upstream JSON");}
  const parsed=parser.safeParse(data);
  if(!parsed.success)throw new ReviewBffError(502,"invalid upstream response");
  return parsed.data;
}
export async function fetchReviewerData(
  config:BackendConfig,access:string,transport:typeof fetch=fetch
):Promise<ReviewData>{
  const [tickets,reviews,candidates]=await Promise.all([
    request(config,access,"/internal/v1/review-tickets","GET",z.array(ticketSchema),undefined,transport),
    request(config,access,"/internal/v1/reviews","GET",z.array(progressSchema),undefined,transport),
    request(config,access,"/internal/v1/review-candidates","GET",z.array(candidateSchema),undefined,transport),
  ]);
  return {tickets,reviews,candidates};
}
export function submitReviewerAction(
  config:BackendConfig,access:string,action:"vote"|"approve",body:unknown,transport:typeof fetch=fetch
){
  if(action==="vote"){
    const p=voteSchema.safeParse(body);
    if(!p.success)return Promise.reject(new Error("invalid vote payload"));
    return request(config,access,"/internal/v1/reviews","POST",progressSchema,p.data,transport);
  }
  if(action==="approve"){
    const p=approveSchema.safeParse(body);
    if(!p.success)return Promise.reject(new Error("invalid lead approval payload"));
    return request(config,access,"/internal/v1/reviews/approve","POST",approvalSchema,p.data,transport);
  }
  return Promise.reject(new Error("invalid reviewer action"));
}
