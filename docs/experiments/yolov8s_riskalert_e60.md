# Experiment — yolov8s_riskalert_e60

_Generated 2026-06-28._

## Summary

First model on the **34-class riskalert-mining** dataset (the 2026-06-28 pivot — see `docs/pivot_2026-06-28.md`). yolov8s, **full 60 epochs**, trained from `yolov8s.pt` base weights on `config/data_riskalert.yaml`.

> No comparison to the old construction v1/v2 models: different taxonomy (34 vs 19 classes, Spanish vs English) — the numbers are not comparable. This is the new baseline for the riskalert task.

## Setup
- Base: `yolov8s.pt` · 60 epochs (completed) · imgsz 640 · batch 16 · cache RAM · MPS (M4)
- Data: `config/data_riskalert.yaml` (train 498 / val 142 / test 72, 34 classes)
- Best epoch: 36 (by val mAP50). Weights: `models/yolov8s_riskalert_e60.pt`
- Eval: `ultralytics .val()` on val and test.

## Global metrics (real)

| split | mAP50 | mAP50-95 | precision | recall |
|-------|------:|---------:|----------:|-------:|
| val | 0.4148 | 0.2387 | 0.4884 | 0.3917 |
| test | 0.4123 | 0.2116 | 0.3631 | 0.4275 |

**Honest read:** mAP50 ≈ 0.41 on both splits — well below the old 19-class construction model (~0.55–0.61), as expected: nearly double the classes, heavy imbalance, and 15 sparse classes (<20 instances, see `docs/dataset_stats_riskalert.md`). Performance is highly polarised by class.

## Per-class AP50 — test split

| class | AP50 |
|-------|-----:|
| PERSONA_CON_RESPIRADOR | 0.9950 |
| RETRO_EXCAVADORA | 0.9950 |
| VIA_BUEN_ESTADO | 0.9950 |
| RODILLO | 0.9261 |
| MOTONIVELADORA | 0.8645 |
| CAMIONETA | 0.8252 |
| CISTERNA_AGUA | 0.6179 |
| CONOS_DELIMITADORES | 0.5836 |
| EXCAVADORA | 0.5151 |
| PERSONA_ROPA_CINTA_REFLECTIVA | 0.4874 |
| VOLQUETE | 0.4461 |
| PERSONA_SIN_ROPA_CINTA_REFLECTIVA | 0.3668 |
| PERSONA_CON_CASCO | 0.3088 |
| PERSONA_SIN_CASCO | 0.1733 |
| PERSONA_SIN_LENTES | 0.1467 |
| VIA_CON_MURO_SEGURIDAD | 0.1082 |
| PERSONA_CON_GUANTES | 0.0688 |
| CARGADOR_FRONTAL | 0.0605 |
| PERSONA | 0.0000 |
| PERSONA_CON_LENTES | 0.0000 |
| PERSONA_SIN_GUANTES | 0.0000 |
| TRACTOR | 0.0000 |
| VIA_SIN_MURO_SEGURIDAD | 0.0000 |

## Takeaways / next
- **Strong classes** (AP50 ≥ 0.8): heavy machinery + a few PPE/road classes are learned well.
- **Zero-AP classes** are mostly the sparse ones — they need more labelled data before they detect at all (data problem, not model).
- Options to improve: source more data for sparse classes, or collapse rare/over-specific classes (e.g. some `VIA_*`) into coarser buckets.
- To run it: `inference/detect_image.py --source <img> --model models/yolov8s_riskalert_e60.pt`
