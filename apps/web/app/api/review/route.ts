import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { readBackendConfig } from "@/lib/api";
import {
  ReviewBffError, fetchReviewerData, requireActiveReviewerAuth,
  requireSameOriginPost, submitReviewerAction,
} from "@/lib/review-bff";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";
const noCache = { "Cache-Control": "no-store" };

async function credentials(request: NextRequest): Promise<string> {
  if (process.env.PRODUCTPULSE_AUTH_MODE !== "oidc")
    throw new ReviewBffError(403, "Review writes require individual OIDC login");
  if (!process.env.AUTH_SECRET) throw new ReviewBffError(503, "OIDC not configured");
  const token = await getToken({ req: request, secret: process.env.AUTH_SECRET });
  return requireActiveReviewerAuth(process.env.PRODUCTPULSE_AUTH_MODE,token);
}
function failure(error:unknown){
  const status = error instanceof ReviewBffError ? error.status : 503;
  // Only stable error message; never echo upstream content or tokens.
  return NextResponse.json({error:"review_action_unavailable",status}, {
    status, headers:noCache,
  });
}
export async function GET(request: NextRequest) {
  try {
    const access=await credentials(request);
    const data=await fetchReviewerData(readBackendConfig(process.env),access);
    return NextResponse.json(data,{headers:noCache});
  }catch(e){return failure(e);}
}
export async function POST(request: NextRequest){
  try{
    const access=await credentials(request);
    const expected=process.env.PRODUCTPULSE_PUBLIC_ORIGIN;
    if(!expected)throw new ReviewBffError(503,"public origin not configured");
    requireSameOriginPost(request.headers.get("origin"),expected);
    if(!request.headers.get("content-type")?.startsWith("application/json"))
      throw new ReviewBffError(415,"JSON required");
    const text=await request.text();
    if(text.length>12_000)throw new ReviewBffError(413,"payload too large");
    let parsed:unknown;
    try{parsed=JSON.parse(text);}catch{throw new ReviewBffError(400,"invalid request JSON");}
    if(!parsed||typeof parsed!=="object"||Array.isArray(parsed))
      throw new ReviewBffError(400,"invalid review request");
    const record=parsed as Record<string,unknown>;
    const action=record.action;
    if(action!=="vote"&&action!=="approve"||Object.keys(record).some(k=>k!=="action"&&k!=="payload"))
      throw new ReviewBffError(422,"unknown reviewer action");
    const result=await submitReviewerAction(
      readBackendConfig(process.env),access,action,record.payload
    );
    return NextResponse.json(result,{status:201,headers:noCache});
  }catch(e){return failure(e);}
}
