# SPEC-010 — Observability & Alerting

**Phase:** Infra · **Depends on:** SPEC-009 · **Effort:** 1 day

## Goal

Operating the system without metrics is flying blind. Add structured
logs, Prometheus-format metrics, and a small set of alerts that page
when the system is actually broken (not when it's merely noisy).

## Prerequisites

- SPEC-009 complete (API is hardened — alerts only make sense once auth
  filters out probe traffic).

## Tasks

- [ ] **Structured logs.** Switch FastAPI + worker to JSON log format.
      Required fields: `ts`, `level`, `request_id`, `event_id`,
      `model_version`, `latency_ms`.
- [ ] **Metrics endpoint.** `/metrics` exposes Prometheus format with:
  - `inference_latency_seconds` (histogram, by model_version)
  - `inference_total{result="ok|error"}` (counter)
  - `detections_total{class}` (counter)
  - `compliance_violation_total{class}` (counter)
  - `review_bucket_size` (gauge)
- [ ] **Local dashboard.** Add `docker-compose.observability.yml`
      (profile) wiring Prometheus + a single Grafana dashboard JSON in
      `infra/grafana/dashboards/construction_safety.json`.
- [ ] **Alerts (Prometheus rules).** Page when:
  - p95 latency > 200ms for 5min
  - error rate > 5% for 5min
  - no inference in 10min during business hours (worker dead)
  - golden-set mAP50 dropped by ≥ 3pp in the latest nightly eval
- [ ] **Runbook.** `docs/runbook.md` — one page per alert: what it
      means, first three things to check, escalation.

## Acceptance criteria

- Hitting an endpoint and tailing logs shows one JSON line per request
  with all required fields.
- `curl /metrics` returns valid Prometheus output.
- `docker compose --profile obs up` brings up Prom + Grafana with the
  dashboard pre-loaded.
- Each alert in the rules file has a matching runbook section.

## Out of scope

- Distributed tracing (overkill at this scale).
- Hosted observability (Datadog / New Relic) — local stack only.
