# Experiment — yolov8s_construction_safety_e60

_Generated 2026-06-26._

## Summary

Upgraded the backbone **yolov8n → yolov8s** on the existing 19-class, 717-image dataset (`config/data.yaml`), to get a stronger detector without any new labelling.

> ⚠️ **Training was cut short at epoch 41/60** (the process was killed externally — no crash/OOM in the log; most likely the machine slept when the lid was closed despite `caffeinate`). YOLO's `best.pt` is the best checkpoint up to that point: **epoch 36, val mAP50 0.6059**. `models/yolov8s_construction_safety_e60.pt` is that checkpoint. Even unfinished, it already beats v1 on every metric — see below.

## Setup

- Base: `yolov8s.pt` · imgsz 640 · batch 16 · cache RAM · device MPS (M4)
- Data: `config/data.yaml` (train 521 / val 114 / test 82, 19 classes)
- Baseline: `models/yolov8n_construction_safety_e40_cache.pt` (v1)
- Both models evaluated with `ultralytics .val()` on the **same** val and test splits.

## Global comparison (real numbers)

| split | metric | v1 (n, e40) | v2 (s, e36) | Δ |
|-------|--------|------------:|------------:|----:|
| val | mAP50 | 0.5754 | 0.6087 | +0.0333 |
| val | mAP50-95 | 0.4056 | 0.4291 | +0.0235 |
| val | precision | 0.6612 | 0.8139 | +0.1527 |
| val | recall | 0.5346 | 0.5367 | +0.0021 |
| test | mAP50 | 0.5025 | 0.5498 | +0.0473 |
| test | mAP50-95 | 0.3548 | 0.3995 | +0.0447 |
| test | precision | 0.6839 | 0.7355 | +0.0516 |
| test | recall | 0.4548 | 0.5272 | +0.0724 |

**Takeaway:** v2 wins on both splits. The gains are biggest on the held-out **test** set — mAP50 **+0.0473**, recall **+0.0724** — and precision jumps markedly on val (**+0.153**). v2 is the better model.

## Per-class AP50 — test split

| class | v1 | v2 | Δ |
|-------|---:|---:|----:|
| Excavator | 0.7210 | 0.8606 | +0.1396 |
| Gloves | 0.1417 | 0.2309 | +0.0892 |
| Hardhat | 0.7365 | 0.7882 | +0.0517 |
| Ladder | 0.7950 | 0.8476 | +0.0526 |
| Mask | 0.6906 | 0.7383 | +0.0477 |
| NO-Hardhat | 0.4105 | 0.5006 | +0.0901 |
| NO-Mask | 0.2697 | 0.5534 | +0.2837 |
| NO-Safety Vest | 0.5750 | 0.6068 | +0.0318 |
| Person | 0.7555 | 0.7702 | +0.0147 |
| Safety Cone | 0.3681 | 0.3902 | +0.0221 |
| Safety Vest | 0.7301 | 0.7870 | +0.0569 |
| dump truck | 0.8222 | 0.7136 | -0.1086 |
| machinery | 0.2876 | 0.1771 | -0.1105 |
| sedan | 0.0000 | 0.0000 | +0.0000 |
| trailer | 0.9950 | 0.9950 | +0.0000 |
| truck | 0.1237 | 0.2475 | +0.1238 |
| van | 0.0108 | 0.0429 | +0.0321 |
| vehicle | 0.4109 | 0.4513 | +0.0404 |
| wheel loader | 0.7030 | 0.7450 | +0.0420 |

## Decision

- **Use v2 (`models/yolov8s_construction_safety_e60.pt`) as the current best model.** It beats v1 on mAP50, mAP50-95, precision and recall across val and test.
- Training stopped at epoch 41/60; resuming from `runs/detect/yolov8s_construction_safety_e60/weights/last.pt` (Ultralytics `resume=True`) could add a small further gain, but metrics were already plateauing (~0.60 val mAP50). Optional, not required.
- To run it: `inference/detect_image.py --source <img> --model models/yolov8s_construction_safety_e60.pt`
