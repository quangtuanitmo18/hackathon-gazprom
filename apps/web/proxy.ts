import { NextRequest, NextResponse } from "next/server";
import { auth } from "./auth";
import { readAuthConfig, verifyBasicAuthorization } from "./lib/auth";

/** OIDC reviewer mode; session verified by Auth.js. */
const oidcProxy = auth((request) => {
  if (!request.auth) return NextResponse.redirect(new URL("/login", request.nextUrl.origin));
  return NextResponse.next();
});

/** Backward-compatible, strictly read-only Basic demo. */
function basicProxy(request: NextRequest) {
  let allowed = false;
  try {
    allowed = verifyBasicAuthorization(
      request.headers.get("authorization"),
      readAuthConfig(process.env),
    );
  } catch {
    return new NextResponse("Dashboard authentication is not configured", {
      status: 503, headers: { "Cache-Control": "no-store" },
    });
  }
  if (!allowed) {
    return new NextResponse("Authentication required", {
      status: 401,
      headers: {
        "WWW-Authenticate": 'Basic realm="ProductPulse Demo", charset="UTF-8"',
        "Cache-Control": "no-store",
      },
    });
  }
  return NextResponse.next();
}

// Auth.js OIDC is opt-in; existing read-only dashboard remains Basic.
export const proxy = process.env.PRODUCTPULSE_AUTH_MODE === "oidc" ? oidcProxy : basicProxy;
export const config = {
  matcher: ["/((?!api/auth|_next/static|_next/image|favicon.ico|healthz|login).*)"],
};
