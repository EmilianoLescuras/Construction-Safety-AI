# SPEC-009 — API & Deploy Hardening

**Phase:** Infra · **Depends on:** SPEC-006 · **Effort:** 1 day

## Goal

Make the FastAPI service safe to expose beyond `localhost`. Right now
it's an open inference endpoint — fine for demos, not fine for a
portfolio that shows real engineering judgement.

## Prerequisites

- SPEC-006 complete (the API serves a real promoted model).

## Tasks

- [ ] **Auth.** Add API key middleware (header `X-API-Key`). Keys read
      from env at startup; reject missing/invalid with 401. Document in
      `docs/api.md`.
- [ ] **Rate limit.** Per-key sliding window (e.g. `slowapi`): 60
      req/min for upload, 600/min for read-only. 429 on overflow.
- [ ] **Input validation.** Max upload size, MIME-type allowlist
      (mp4/mov/jpg/png), reject otherwise with 415.
- [ ] **CORS.** Tight allowlist via env var, not `*`.
- [ ] **Healthcheck.** `GET /healthz` returns 200 only if model loaded
      AND db reachable. Used by docker `healthcheck:`.
- [ ] **Secrets.** No keys in `docker-compose.yml`. Pull from `.env`
      via `env_file:`. Add `.env.example` template.
- [ ] **Tests.** Add `tests/api/test_auth.py`,
      `tests/api/test_rate_limit.py`. Both must pass in CI.

## Acceptance criteria

- `curl` without `X-API-Key` returns 401.
- 100 rapid requests with a valid key trigger a 429 before the test
  finishes.
- `docker compose up` with a missing required env var fails fast with a
  clear error.
- `/healthz` returns 503 if the model file is missing.
- No new dependency bigger than `slowapi`.

## Out of scope

- OAuth / OIDC (overkill).
- Per-tenant quotas.
- WAF / DDoS protection (handle at edge if it ever ships publicly).
