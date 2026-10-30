import { test } from "node:test";
import assert from "node:assert/strict";
import { publicReviewerSession, validateOidcModeConfig } from "../lib/oidc-config";

test("public session never exposes Keycloak access or refresh token",()=>{
  const session={user:{name:"Reviewer A",email:"reviewer@example.org"},expires:"2026-10-30T15:00:00Z"};
  const token={reviewerAccessToken:"ACCESS-SUPER-SECRET",reviewerRefreshToken:"REFRESH-SUPER-SECRET",reviewerExpiresAt:1888000000};
  const visible=publicReviewerSession(session,token);
  assert.deepEqual(visible,session);
  assert.ok(!JSON.stringify(visible).includes("ACCESS-SUPER-SECRET"));
  assert.ok(!JSON.stringify(visible).includes("REFRESH-SUPER-SECRET"));
});
test("OIDC mode rejects absent/partial Keycloak configuration",()=>{
  assert.throws(()=>validateOidcModeConfig({PRODUCTPULSE_AUTH_MODE:"oidc"}),/AUTH_/);
  assert.throws(()=>validateOidcModeConfig({PRODUCTPULSE_AUTH_MODE:"oidc",AUTH_SECRET:"short"}),/AUTH_/);
});
test("Basic dashboard mode remains read-only and needs no Keycloak config",()=>{
  assert.doesNotThrow(()=>validateOidcModeConfig({PRODUCTPULSE_AUTH_MODE:"basic"}));
});
