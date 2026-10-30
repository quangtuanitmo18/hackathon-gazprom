import {NextRequest,NextResponse} from "next/server";
import {getToken} from "next-auth/jwt";
import {readBackendConfig} from "@/lib/api";
import {
  ReviewBffError,requireActiveReviewerAuth,requireSameOriginPost,
} from "@/lib/review-bff";
import {fetchInsightData,submitInsightAction} from "@/lib/insight-bff";

export const dynamic="force-dynamic";
export const runtime="nodejs";
const noCache={"Cache-Control":"no-store"};

async function credentials(req:NextRequest):Promise<string>{
  if(process.env.PRODUCTPULSE_AUTH_MODE!=="oidc")
    throw new ReviewBffError(403,"Individual Keycloak account required");
  if(!process.env.AUTH_SECRET)
    throw new ReviewBffError(503,"OIDC not configured");
  const token=await getToken({req,secret:process.env.AUTH_SECRET});
  return requireActiveReviewerAuth(process.env.PRODUCTPULSE_AUTH_MODE,token);
}
function fail(e:unknown){
  const status=e instanceof ReviewBffError?e.status:503;
  // No secrets, upstream text, or model content in errors.
  return NextResponse.json({error:"insight_action_unavailable",status},
    {status,headers:noCache});
}
export async function GET(req:NextRequest){
  try{
    if(req.nextUrl.search||req.nextUrl.hash)
      throw new ReviewBffError(422,"no custom query allowed");
    const access=await credentials(req);
    return NextResponse.json(await fetchInsightData(readBackendConfig(process.env),access),
      {headers:noCache});
  }catch(e){return fail(e);}
}
export async function POST(req:NextRequest){
  try{
    const access=await credentials(req);
    const expected=process.env.PRODUCTPULSE_PUBLIC_ORIGIN;
    if(!expected)throw new ReviewBffError(503,"public origin not configured");
    requireSameOriginPost(req.headers.get("origin"),expected);
    if(!req.headers.get("content-type")?.startsWith("application/json"))
      throw new ReviewBffError(415,"JSON required");
    const raw=await req.text();
    if(raw.length>12000)throw new ReviewBffError(413,"payload too large");
    let parsed:unknown;
    try{parsed=JSON.parse(raw);}catch{throw new ReviewBffError(400,"invalid JSON");}
    if(!parsed||Array.isArray(parsed)||typeof parsed!=="object")
      throw new ReviewBffError(422,"invalid insight request");
    const input=parsed as Record<string,unknown>;
    if((input.action!=="approve"&&input.action!=="mock-publish") ||
       Object.keys(input).some(k=>k!=="action"&&k!=="payload"))
      throw new ReviewBffError(422,"unknown insight action");
    const outcome=await submitInsightAction(
      readBackendConfig(process.env),access,input.action,input.payload
    );
    return NextResponse.json(outcome,{status:201,headers:noCache});
  }catch(e){return fail(e);}
}
