# SPEC-006 — Model Promotion Gate

**Phase:** Eval · **Depends on:** SPEC-005 · **Effort:** 4 hours

## Goal

Codify "what makes a model production-ready" as an executable check.
A model can only become the deployed model if it clears the gate.

## Prerequisites

- SPEC-005 complete (golden test + `evaluate.py` exist).

## Tasks

- [ ] Define gate thresholds in `config/promotion_gate.yaml`:
  ```yaml
  golden_set:
    mAP50_min: 0.62          # v1 baseline + 5pp headroom
    per_class:
      Person:    {AP50_min: 0.85}
      Hardhat:   {AP50_min: 0.70}
      Safety Vest: {AP50_min: 0.65}
      pickup:    {AP50_min: 0.40}
    p95_latency_ms_max: 80   # on MPS, imgsz 640
  ```
- [ ] Write `scripts/promote.py <weights.pt>`:
  - Runs `evaluate.py` on the golden set.
  - Compares to `promotion_gate.yaml`.
  - On pass: tag the MLflow run `production-candidate`, copy weights to
    `models/production/current.pt` (symlink), append row to
    `docs/model_registry.md`.
  - On fail: print the failing checks, exit 1, leave nothing changed.
- [ ] Wire the API/worker to load `models/production/current.pt` when
      present, falling back to v1.

## Acceptance criteria

- Running `promote.py` on a deliberately broken model exits non-zero and
  changes nothing.
- Running it on v1 produces a clear pass/fail line per criterion.
- `docs/model_registry.md` exists with v1 as the first entry.
- API picks up a freshly promoted model on next restart (no code change
  needed).

## Out of scope

- Canary rollout / traffic-splitting (deferred to v3).
- Automated rollback (deferred).
