/**
 * Client wrapper around the FastAPI backend.
 * `NEXT_PUBLIC_API_URL` is read at build/runtime (defaults to localhost:8000).
 */
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type EvidenceFile = {
  id: number;
  kind: "full" | "crop";
  path: string;
};

export type AlertDispatch = {
  id: number;
  sink: string;
  success: boolean;
  error: string;
  dispatched_at: number;
};

export type ViolationEvent = {
  id: number;
  rule: string;
  person_id: number;
  frame: number;
  first_seen_ts: number;
  emitted_ts: number;
  duration_seconds: number;
  violation_class: string;
  violation_conf: number;
  person_bbox: [number, number, number, number];
  violation_bbox: [number, number, number, number];
  source: string | null;
  ingested_at: string;
  evidence_files: EvidenceFile[];
  dispatches: AlertDispatch[];
};

export type RuleCount = { rule: string; count: number };
export type PersonCount = { person_id: number; count: number };

export type StatsSummary = {
  total_events: number;
  total_dispatches: number;
  dispatch_success: number;
  dispatch_failed: number;
  by_rule: RuleCount[];
  top_persons: PersonCount[];
};

async function jsonFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store", ...init });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${body || res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export type EventFilters = {
  rule?: string;
  person_id?: number;
  since?: number;
  limit?: number;
  offset?: number;
};

function buildQuery(filters: EventFilters): string {
  const params = new URLSearchParams();
  if (filters.rule) params.set("rule", filters.rule);
  if (filters.person_id !== undefined)
    params.set("person_id", String(filters.person_id));
  if (filters.since !== undefined) params.set("since", String(filters.since));
  if (filters.limit !== undefined) params.set("limit", String(filters.limit));
  if (filters.offset !== undefined)
    params.set("offset", String(filters.offset));
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export const api = {
  health: () => jsonFetch<{ status: string }>("/health"),
  stats: () => jsonFetch<StatsSummary>("/stats/summary"),
  listEvents: (filters: EventFilters = {}) =>
    jsonFetch<ViolationEvent[]>(`/events${buildQuery(filters)}`),
  getEvent: (id: number) => jsonFetch<ViolationEvent>(`/events/${id}`),
  evidenceUrl: (id: number) => `${API_URL}/evidence/${id}`,
};
