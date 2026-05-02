// Thin client for the AtlasMind API gateway.

import { z } from "zod";

const API_URL = process.env.ATLASMIND_API_URL ?? "";

export const RunRequestSchema = z.object({
  scope: z.object({
    country: z.string().length(3).optional(),
    region: z.string().optional(),
    sector: z.string().optional(),
    theme: z.string().optional(),
    horizon_months: z.number().int().min(1).max(120).default(24),
  }),
  depth: z.enum(["standard", "deep"]).default("standard"),
});

export type RunRequest = z.infer<typeof RunRequestSchema>;

export async function submitRun(req: RunRequest, idToken: string): Promise<{ run_id: string }> {
  const res = await fetch(`${API_URL}/runs`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify(RunRequestSchema.parse(req)),
  });
  if (!res.ok) throw new Error(`submitRun failed: ${res.status}`);
  return res.json();
}

export async function getRun(runId: string, idToken: string): Promise<unknown> {
  const res = await fetch(`${API_URL}/runs/${runId}`, {
    headers: { authorization: `Bearer ${idToken}` },
  });
  if (!res.ok) throw new Error(`getRun failed: ${res.status}`);
  return res.json();
}
