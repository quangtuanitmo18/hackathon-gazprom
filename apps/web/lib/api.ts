import { z } from "zod";

export type BackendConfig = { baseUrl: string; token: string };

const problemSchema = z.object({
  problem_id: z.string(),
  scope_id: z.string(),
  ticket_keys: z.array(z.string()),
  revision: z.number().int(),
  status: z.enum(["active", "merged"]),
  parent_id: z.string().nullable(),
  merged_into: z.string().nullable(),
}).strict();

const auditSchema = z.object({
  scope_id: z.string(),
  sequence: z.number().int(),
  kind: z.string(),
  actor: z.string(),
  operation_key: z.string(),
  occurred_at: z.string(),
  problem_ids: z.array(z.string()),
  ticket_keys: z.array(z.string()),
  reason: z.string(),
  revoked_pair_ids: z.array(z.string()),
}).strict();

export type Problem = z.infer<typeof problemSchema>;
export type AuditEvent = z.infer<typeof auditSchema>;

export class UpstreamError extends Error {
  constructor(readonly code: number) {
    super(`ProductPulse backend returned HTTP ${code}`);
    this.name = "UpstreamError";
  }
}

export function readBackendConfig(env: Record<string, string | undefined>): BackendConfig {
  const baseUrl = env.PRODUCTPULSE_BACKEND_URL;
  const token = env.PRODUCTPULSE_INTERNAL_TOKEN;
  if (!baseUrl || !token || token.length < 24) {
    throw new Error("PRODUCTPULSE_BACKEND_URL and PRODUCTPULSE_INTERNAL_TOKEN must be configured");
  }
  let parsed: URL;
  try { parsed = new URL(baseUrl); } catch { throw new Error("invalid PRODUCTPULSE_BACKEND_URL"); }
  if (!["http:", "https:"].includes(parsed.protocol) || parsed.username || parsed.password ||
      parsed.search || parsed.hash || (parsed.pathname !== "/" && parsed.pathname !== "")) {
    throw new Error("invalid PRODUCTPULSE_BACKEND_URL (credentials/query/path forbidden)");
  }
  return { baseUrl: parsed.origin, token };
}

async function requestJson<T>(
  path: string, parser: z.ZodType<T>,
  config: BackendConfig, transport: typeof fetch,
): Promise<T> {
  const url = new URL(path, config.baseUrl);
  if (url.origin !== config.baseUrl || !path.startsWith("/internal/v1/")) {
    throw new Error("invalid internal API path");
  }
  let response: Response;
  try {
    response = await transport(url.toString(), {
      method: "GET",
      cache: "no-store",
      headers: {
        "X-Internal-Token": config.token,
        "Cache-Control": "no-store",
        Accept: "application/json",
      },
      signal: AbortSignal.timeout(8000),
    });
  } catch {
    throw new UpstreamError(503);
  }
  if (!response.ok) throw new UpstreamError(response.status);
  let json: unknown;
  try { json = await response.json(); } catch { throw new Error("invalid upstream JSON"); }
  const parsed = parser.safeParse(json);
  if (!parsed.success) throw new Error("invalid upstream response schema");
  return parsed.data;
}

export function fetchProblems(config: BackendConfig, transport: typeof fetch = fetch) {
  return requestJson("/internal/v1/problems", z.array(problemSchema), config, transport);
}

export function fetchProblem(id: string, config: BackendConfig, transport: typeof fetch = fetch) {
  if (!/^PRB-[0-9]{6,}$/.test(id)) return Promise.reject(new Error("invalid problem ID"));
  return requestJson(`/internal/v1/problems/${encodeURIComponent(id)}`, problemSchema, config, transport);
}

export function fetchAudit(config: BackendConfig, transport: typeof fetch = fetch) {
  return requestJson("/internal/v1/audit", z.array(auditSchema), config, transport);
}
