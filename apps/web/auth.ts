import NextAuth from "next-auth";
import Keycloak from "next-auth/providers/keycloak";
import { publicReviewerSession, validateOidcModeConfig } from "./lib/oidc-config";

/**
 * Keycloak users authenticate with Authorization Code OIDC via Auth.js.
 * OAuth access token is in an encrypted, HttpOnly Auth.js JWT cookie only.
 * Public `/api/auth/session` NEVER receives OAuth tokens.
 */
const oidcEnabled = process.env.PRODUCTPULSE_AUTH_MODE === "oidc";
if (oidcEnabled) validateOidcModeConfig(process.env);

export const { handlers, auth, signIn, signOut } = NextAuth({
  session: { strategy: "jwt", maxAge: 900 },
  providers: oidcEnabled ? [
    Keycloak({
      issuer: process.env.AUTH_KEYCLOAK_ISSUER,
      clientId: process.env.AUTH_KEYCLOAK_ID,
      clientSecret: process.env.AUTH_KEYCLOAK_SECRET,
    }),
  ] : [],
  callbacks: {
    async jwt({ token, account }) {
      if (account) {
        if (!account.access_token || !account.expires_at)
          throw new Error("OIDC provider did not supply access token and expiry");
        token.reviewerAccessToken = account.access_token;
        token.reviewerExpiresAt = account.expires_at;
      }
      return token;
    },
    async session({ session, token }) {
      // NEVER copy token.reviewerAccessToken into this browser-visible session.
      return publicReviewerSession(session, token);
    },
  },
});

declare module "next-auth/jwt" {
  interface JWT {
    reviewerAccessToken?: string;
    reviewerExpiresAt?: number;
  }
}
