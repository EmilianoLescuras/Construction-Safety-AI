# Project Specs — Construction Safety AI

A numbered, sequential plan to take the project from the current v1 demo
to a portfolio-grade, production-ready PPE compliance system.

Each spec is a self-contained ticket: goal, prerequisites, tasks,
acceptance criteria, out-of-scope. Work them **in order** — later specs
depend on earlier ones.

## Current state (as of 2026-06-25)

- v1 model: `yolov8n_construction_safety_e40_cache.pt` — mAP50 0.577 on
  the 19-class Roboflow set.
- Demo frontend: gallery + tracked sample video at `/demo`.
- v2 pipeline scaffolded: pseudo-labeling script + merged data yaml +
  `--data` override on `train.py`. Smoke test confirms infra works
  (`docs/experiments/v2_pipeline_smoke.md`).
- Known v1 weaknesses (documented in `docs/v2_roadmap.md`): pickup
  trucks misclassified as `sedan`, hi-vis long-sleeve shirts flagged as
  `NO-Safety Vest`.

## Spec index

| #  | Spec | Phase | Status |
|----|------|-------|--------|
| 01 | [Data correction pass](SPEC-001-data-correction.md) | Data | TODO |
| 02 | [Taxonomy update: pickup + hi-vis shirt](SPEC-002-taxonomy-update.md) | Data | TODO |
| 03 | [External data sourcing](SPEC-003-external-data.md) | Data | TODO |
| 04 | [v2 training run + comparison](SPEC-004-v2-training.md) | Model | TODO |
| 05 | [Evaluation harness + golden set](SPEC-005-eval-harness.md) | Eval | TODO |
| 06 | [Model promotion gate](SPEC-006-promotion-gate.md) | Eval | TODO |
| 07 | [Backbone upgrade yolov8n → yolov8s](SPEC-007-backbone-upgrade.md) | Model | TODO |
| 08 | [Active-learning loop](SPEC-008-active-learning.md) | MLOps | TODO |
| 09 | [API & deploy hardening](SPEC-009-api-hardening.md) | Infra | TODO |
| 10 | [Observability & alerting](SPEC-010-observability.md) | Infra | TODO |
| 11 | [Case study + portfolio writeup](SPEC-011-case-study.md) | Docs | TODO |

## Phases at a glance

```
Phase 1 — DATA            → specs 01, 02, 03
Phase 2 — MODEL           → specs 04, 07
Phase 3 — EVAL            → specs 05, 06   (run alongside phase 2)
Phase 4 — MLOPS / INFRA   → specs 08, 09, 10
Phase 5 — DELIVERY        → spec 11
```

## How to work a spec

1. Read the spec end-to-end before starting.
2. Open a branch named `spec/NN-short-name`.
3. Tick boxes in the "Tasks" section as you go (commit the file).
4. Match every "Acceptance criteria" item — if you can't, leave the spec
   open and document why.
5. PR title: `feat(specNN): <one line>`. Link the spec in the description.
6. Flip the row in this index from `TODO` → `DONE` in the merge commit.

## Definition of "finalized"

The project is **finalized** when:

- All specs 01–11 are `DONE`.
- v2 model beats v1 by ≥ 5pp mAP50 on the golden test set.
- A user can run `docker compose up` and detect non-compliance on a fresh
  video without touching code.
- `docs/specs/SPEC-011-case-study.md` deliverable is published.
