# Experiment — yolo26s_riskalert_e60 (YOLO26)

_Generated 2026-06-28._

## Summary

Re-trained the riskalert 34-class task with the **YOLO26** architecture (`yolo26s.pt`) — the model family the user actually wanted (the dataset is exported in YOLO26 format). Compared against the earlier **yolov8s** run on the same dataset/splits.

> ⚠️ **Not a fair comparison yet.** YOLO26 training was **killed at epoch 39/60** (external kill, no crash in log — the Mac most likely slept). Its `best.pt` is epoch 37. The yolov8s baseline ran the **full 60 epochs**. So YOLO26 is handicapped here; a full 60-epoch run is needed to conclude.

## YOLO26 vs YOLOv8 (same dataset, same splits)

| model | split | mAP50 | mAP50-95 | precision | recall |
|-------|-------|------:|---------:|----------:|-------:|
| yolov8s (full 60ep) | val | 0.4148 | 0.2387 | 0.4884 | 0.3917 |
| yolov8s (full 60ep) | test | 0.4123 | 0.2116 | 0.3631 | 0.4275 |
| yolo26s (cut @39ep) | val | 0.3542 | 0.2245 | 0.5774 | 0.3396 |
| yolo26s (cut @39ep) | test | 0.3529 | 0.2184 | 0.5919 | 0.3037 |

**Read (test split):** YOLO26 mAP50 0.3529 vs v8 0.4123 (v8 ahead), but YOLO26 precision 0.5919 vs 0.3631 (much higher) and mAP50-95 0.2184 vs 0.2116 (≈ tied). YOLO26 trades recall for precision here. Given YOLO26 stopped 21 epochs early, the mAP50 gap is likely partly undertraining.

## Per-class AP50 — test split (YOLO26)

| class | AP50 |
|-------|-----:|
| RODILLO | 0.9539 |
| MOTONIVELADORA | 0.9521 |
| RETRO_EXCAVADORA | 0.9125 |
| CAMIONETA | 0.8329 |
| EXCAVADORA | 0.6477 |
| VOLQUETE | 0.4970 |
| PERSONA_CON_RESPIRADOR | 0.4950 |
| VIA_CON_MURO_SEGURIDAD | 0.4871 |
| PERSONA_ROPA_CINTA_REFLECTIVA | 0.4553 |
| CARGADOR_FRONTAL | 0.3993 |
| CONOS_DELIMITADORES | 0.3688 |
| CISTERNA_AGUA | 0.2896 |
| PERSONA_SIN_ROPA_CINTA_REFLECTIVA | 0.2234 |
| PERSONA_SIN_CASCO | 0.1851 |
| PERSONA_CON_CASCO | 0.1666 |
| VIA_BUEN_ESTADO | 0.1244 |
| PERSONA_CON_GUANTES | 0.0527 |
| PERSONA_SIN_LENTES | 0.0468 |
| TRACTOR | 0.0169 |
| PERSONA | 0.0087 |
| PERSONA_CON_LENTES | 0.0000 |
| PERSONA_SIN_GUANTES | 0.0000 |
| VIA_SIN_MURO_SEGURIDAD | 0.0000 |

## Decision / next

- **Inconclusive** until YOLO26 finishes a full 60-epoch run. Both runs (v8 and 26) have died ~1h in — the machine is sleeping mid-training despite `caffeinate` (likely lid closed on battery).
- To get a clean YOLO26 number: re-run to 60 epochs with the lid OPEN + plugged in, or lower `--epochs` to ~35 so it finishes inside the awake window.
- Weights: `models/yolo26s_riskalert_e60.pt` (epoch-37 best, usable).
- Run it: `inference/detect_image.py --source <img> --model models/yolo26s_riskalert_e60.pt`
