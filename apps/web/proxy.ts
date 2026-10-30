import { NextRequest, NextResponse } from "next/server";
import { readAuthConfig, verifyBasicAuthorization } from "./lib/auth";

/**
 * Demo-only auth boundary. On the open internet replace with OIDC and RBAC.
 * Never expose the backend X-Internal-Token to the browser.
 */
export function proxy(request: NextRequest) {
  let allowed = false;
  try {
    allowed = verifyBasicAuthorization(
      request.headers.get("authorization"),
      readAuthConfig(process.env),
    );
  } catch {
    // Fail closed if auth config is absent or invalid.
    return new NextResponse("Dashboard authentication is not configured", {
      status: 503,
      headers: { "Cache-Control": "no-store" },
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

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|healthz).*)"],
};
