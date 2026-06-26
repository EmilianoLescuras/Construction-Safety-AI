# SPEC-005 — Evaluation Harness + Golden Test Set

**Phase:** Eval · **Depends on:** SPEC-001 (can run in parallel with 002–004) · **Effort:** 1 day

## Goal

Replace ad-hoc validation with a reproducible evaluation harness. Carve
out a **golden test set** that never participates in training and acts
as the single source of truth for "is the model better?".

## Prerequisites

- A reviewed labelled pool (SPEC-001).

## Tasks

- [ ] Move 100 hand-picked images from `datasets/valid` →
      `datasets/golden_test/`. Pick images that exercise:
  - PPE compliance + violation (mix of both)
  - Pickups + sedans (taxonomy stress)
  - Hi-vis shirts (false-positive stress)
  - Multi-worker scenes (tracking stress)
  - Edge cases: occlusion, distance, motion blur
- [ ] Document selection rationale in `datasets/golden_test/README.md`.
- [ ] Write `scripts/evaluate.py`:
  - Loads any weights + the golden set.
  - Outputs JSON: precision, recall, mAP50, mAP50-95, per-class AP50,
    confusion matrix, latency p50/p95 on the target device.
  - Writes a markdown report to `docs/experiments/<weights_stem>_golden.md`.
- [ ] Add a pytest that runs `evaluate.py` on a tiny fixture and asserts
      the JSON shape.

## Acceptance criteria

- `datasets/golden_test/` exists with 100 images + labels, ignored from
  any train glob.
- `scripts/evaluate.py models/<w>.pt` produces a report in under 2
  minutes on MPS.
- The pytest fixture test runs in CI in under 30s.
- v1 evaluated on golden set → numbers committed as the baseline.

## Out of scope

- Promotion logic (SPEC-006).
- Continuous eval on every commit (deferred).
