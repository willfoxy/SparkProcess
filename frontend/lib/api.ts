import type { SessionDetail, SessionSummary } from "@/types";

// When NEXT_PUBLIC_API_URL is set (Vercel / any external backend) the client
// calls the backend directly — this is required for SSE (EventSource) because
// Vercel's rewrite proxy buffers the stream.  In local dev without the var set,
// we fall back to the Next.js rewrite (/api → localhost:8000).
const BASE =
  process.env.NEXT_PUBLIC_API_URL
    ? `${process.env.NEXT_PUBLIC_API_URL}/api`
    : "/api";

export async function createSession(brief: string, organization = ""): Promise<SessionSummary> {
  const res = await fetch(`${BASE}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ brief, organization }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getSessions(): Promise<SessionSummary[]> {
  const res = await fetch(`${BASE}/sessions`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getSession(sessionId: string): Promise<SessionDetail> {
  const res = await fetch(`${BASE}/sessions/${sessionId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<void> {
  await fetch(`${BASE}/sessions/${sessionId}`, { method: "DELETE" });
}

export function openEventStream(sessionId: string): EventSource {
  return new EventSource(`${BASE}/sessions/${sessionId}/stream`);
}
