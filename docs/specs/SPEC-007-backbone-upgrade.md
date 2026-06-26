# SPEC-007 — Backbone Upgrade yolov8n → yolov8s

**Phase:** Model · **Depends on:** SPEC-004 (passed gate) · **Effort:** 4 hours

## Goal

Only after the data work is done, swap the n backbone for s. Expected
+3-5 mAP50 on the same data (per `docs/v2_roadmap.md` §3). Training
time roughly 2-3× longer on the same M4 MPS.

## Prerequisites

- SPEC-004 passed (v2_n_e40 cleared the promotion gate). Bigger model on
  undersized data overfits — this spec is meaningless without that.

## Tasks

- [ ] Train:
      ```
      python scripts/train.py \
        --model yolov8s.pt \
        --data config/data_v2.yaml \
        --epochs 60 --batch 16 --imgsz 640 --patience 20 \
        --run-name v2_s_e60 \
        --mlflow-experiment construction-safety-v2
      ```
- [ ] Run `evaluate.py` on the golden set.
- [ ] Compare against v2_n_e40 in `docs/experiments/v2_s_e60.md`.
- [ ] Profile inference: end-to-end latency at imgsz 640 on MPS, CPU,
      and (if you have CUDA later) cuda:0. Record p50/p95/p99.
- [ ] If gate passes AND p95 latency ≤ 80ms on MPS → `promote.py`.

## Acceptance criteria

- v2_s_e60 mAP50 > v2_n_e40 mAP50 (any positive delta).
- p95 latency still under the gate's budget on MPS.
- Decision recorded in `docs/experiments/v2_s_e60.md`: promote or stay
  on the n model. If "stay on n", say why (latency, marginal gain, etc.).

## Out of scope

- yolov8m / yolov8l (overkill for this dataset size).
- Quantisation / ONNX export (deferred).
