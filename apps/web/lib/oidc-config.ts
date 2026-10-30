/** OIDC-specific config and intentionally safe browser session projection. */
export function validateOidcModeConfig(env:Record<string,string|undefined>):void {
  if(env.PRODUCTPULSE_AUTH_MODE!=="oidc")return;
  if((env.AUTH_SECRET||"").length<32)throw new Error("AUTH_SECRET must be >=32 characters in OIDC mode");
  if(!env.AUTH_KEYCLOAK_ID||!env.AUTH_KEYCLOAK_SECRET)
    throw new Error("AUTH_KEYCLOAK_ID and AUTH_KEYCLOAK_SECRET required");
  const issuer=env.AUTH_KEYCLOAK_ISSUER;
  if(!issuer||!/^https:\/\//.test(issuer))throw new Error("AUTH_KEYCLOAK_ISSUER must use HTTPS");
  const origin=env.PRODUCTPULSE_PUBLIC_ORIGIN;
  if(!origin||!/^https:\/\//.test(origin) && !/^http:\/\/localhost(:\d+)?$/.test(origin))
    throw new Error("PRODUCTPULSE_PUBLIC_ORIGIN must be HTTPS (or localhost for dev)");
  if(new URL(origin).origin!==origin)throw new Error("PRODUCTPULSE_PUBLIC_ORIGIN must be a bare origin");
}

/** Auth.js session callback: NEVER propagate access or refresh tokens. */
export function publicReviewerSession<S extends {user?:unknown;expires:string}>(
  session:S, _serverOnlyToken:unknown
):S {
  return session;
}
