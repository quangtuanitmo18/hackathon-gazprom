import { createHash, timingSafeEqual } from "node:crypto";

export type AuthConfig = { username: string; password: string };

export function readAuthConfig(env: Record<string, string | undefined>): AuthConfig {
  const username = env.DASHBOARD_USERNAME;
  const password = env.DASHBOARD_PASSWORD;
  if (!username?.trim() || username.includes(":")) {
    throw new Error("DASHBOARD_USERNAME must be configured without ':'");
  }
  if (!password || password.length < 16) {
    throw new Error("DASHBOARD_PASSWORD must be a high-entropy configured secret (>=16 characters)");
  }
  return { username, password };
}

function digest(value: string): Buffer {
  return createHash("sha256").update(value, "utf8").digest();
}

/** Demo-only Basic Auth credential verification. Never use without HTTPS. */
export function verifyBasicAuthorization(
  authorization: string | null | undefined,
  expected: AuthConfig,
): boolean {
  if (!authorization || authorization.length > 4096) return false;
  const match = /^Basic ([A-Za-z0-9+/]+={0,2})$/i.exec(authorization);
  if (!match || match[1].length % 4 !== 0) return false;
  let decoded: string;
  try {
    const raw = Buffer.from(match[1], "base64");
    if (raw.toString("base64") !== match[1]) return false;
    decoded = new TextDecoder("utf-8", { fatal: true }).decode(raw);
  } catch {
    return false;
  }
  const index = decoded.indexOf(":");
  if (index <= 0) return false;
  const user = decoded.slice(0, index);
  const pass = decoded.slice(index + 1);
  const sameUser = timingSafeEqual(digest(user), digest(expected.username));
  const samePassword = timingSafeEqual(digest(pass), digest(expected.password));
  return sameUser && samePassword;
}
