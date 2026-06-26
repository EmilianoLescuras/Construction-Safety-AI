# SPEC-004 — v2 Training Run + Side-by-Side Comparison

**Phase:** Model · **Depends on:** SPEC-001, 002, 003 · **Effort:** 4 hours

## Goal

Train the first **honest** v2: yolov8n on the corrected + expanded
dataset, full 40 epochs, log to MLflow. Beat v1 by ≥ 5pp mAP50 (the gate
defined in `docs/v2_roadmap.md`) — if not, regroup before SPEC-007
(backbone upgrade).

## Prerequisites

- SPEC-001/002/003 complete.
- v1 weights present at `models/yolov8n_construction_safety_e40_cache.pt`.

## Tasks

- [ ] Run baseline freshness check: re-validate v1 on the **new** val
      split and record numbers in `docs/experiments/v1_on_v2_val.md`.
      (Some metric drop is expected — that's the bar to beat.)
- [ ] Train:
      ```
      python scripts/train.py \
        --model models/yolov8n_construction_safety_e40_cache.pt \
        --data config/data_v2.yaml \
        --epochs 40 --batch 16 --imgsz 640 \
        --run-name v2_n_e40 \
        --mlflow-experiment construction-safety-v2
      ```
- [ ] Generate `docs/experiments/v2_n_e40.md` with the same comparison
      table format as `v2_pipeline_smoke.md`.
- [ ] Promote weights → `models/v2_n_e40.pt` (script already does this).

## Acceptance criteria

- v2 mAP50 ≥ v1 mAP50 + 0.05 on the same val split.
- Per-class AP50 for `pickup` ≥ 0.40 (new class actually learned).
- Per-class AP50 for `Safety Vest` ≥ v1 + 3pp (hi-vis shirt fix worked).
- MLflow run logged with weights as artifact.
- Experiment doc has: comparison table, per-class deltas, 3 sample
  failure cases with screenshots.

## Out of scope

- Backbone change (SPEC-007).
- Eval harness (SPEC-005).
