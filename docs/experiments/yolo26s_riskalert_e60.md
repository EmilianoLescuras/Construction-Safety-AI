# Experiment — yolo26s_riskalert_e60 (YOLO26 vs YOLOv8)

_Generated 2026-06-29._

## Summary

Trained the riskalert 34-class task with **YOLO26** (`yolo26s.pt`) — the architecture the dataset is exported for — and compared it head-to-head with the **yolov8s** run on the same dataset/splits.

> ✅ **Clean comparison.** This YOLO26 run completed properly: **early-stopped at epoch 57** (patience 20; best epoch 37, no improvement after) — not a kill. yolov8s ran the full 60 (best epoch 36). Both models had their full shot.

## Results (same dataset, same splits)

| model | split | mAP50 | mAP50-95 | precision | recall |
|-------|-------|------:|---------:|----------:|-------:|
| yolov8s | val | 0.4148 | 0.2387 | 0.4884 | 0.3917 |
| yolov8s | test | 0.4123 | 0.2116 | 0.3631 | 0.4275 |
| yolo26s | val | 0.3542 | 0.2245 | 0.5774 | 0.3396 |
| yolo26s | test | 0.3529 | 0.2184 | 0.5919 | 0.3037 |

## Verdict (honest)

On this small, imbalanced 34-class set, **yolov8s wins on mAP50 and recall** (test mAP50 0.412 vs 0.353), while **YOLO26 is markedly more precise** (test precision 0.592 vs 0.363) at the cost of recall (0.304 vs 0.428); mAP50-95 is ≈ tied (0.218 vs 0.212).

- 'Newer' (YOLO26) did **not** mean better here — on ~712 images with 15 sparse classes, the lighter yolov8s generalises better at the mAP50 operating point. YOLO26's high precision / low recall suggests it's more conservative; it may shine with more data or longer schedule.
- **For deployment now, yolov8s is the better detector** on this dataset. Keep YOLO26 if you specifically want fewer false positives.

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

## Weights
- `models/yolo26s_riskalert_e60.pt` (epoch-37 best, 19M, completed run). Run: `inference/detect_image.py --source <img> --model models/yolo26s_riskalert_e60.pt`