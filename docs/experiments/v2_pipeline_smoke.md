# Experiment: v2_pipeline_smoke

- Date: 2026-06-25T23:27:39
- Base model: `models/yolov8n_construction_safety_e40_cache.pt` (v1)
- Epochs: 5
- Image size: 640
- Batch: 16
- Device: `mps`
- Data: `config/data_v2.yaml` (original train + 52 pseudo-labelled frames from user-recorded clip)
- Ultralytics run dir: `runs/detect/v2_pipeline_smoke` (gitignored)

## What this run proved (and didn't)

This is a **pipeline smoke test**, not a model improvement. The goal was
to verify the v2 fine-tune scaffold end-to-end: pseudo-label generation
→ merged data yaml → resumed training from v1 checkpoint → validation
report → MLflow logging path.

Side-by-side against the v1 baseline on the **same** validation split
(114 images, 729 instances):

| Metric        | v1 baseline | v2 pipeline_smoke | Δ        |
|---------------|-------------|-------------------|----------|
| mAP50         | 0.577       | 0.575             | −0.002   |
| mAP50-95      | 0.405       | 0.394             | −0.011   |
| Precision     | 0.695       | 0.664             | −0.031   |
| Recall        | 0.528       | 0.525             | −0.003   |

**Why it didn't improve**: the 52 added frames came with labels v1
predicted itself, so the gradient signal is mostly "agree with what you
already think." Worse, slight overfitting to one camera viewpoint
nudged precision down 3pp. This is the **expected** behaviour for
uncorrected pseudo-labels — confirming the warning in
`scripts/pseudo_label_video.py`.

## What a real v2 needs

1. Manually correct the pseudo-labels in `datasets/v2_inbox/labels/`:
   - Re-class `sedan` boxes that are actually pickups → new class `pickup`
     (requires bumping `nc` to 20 and adding the name in `data_v2.yaml`).
   - Add `Safety Vest` boxes around workers wearing hi-vis long-sleeve
     shirts that v1 missed.
2. Source ~300 additional pickup samples from Roboflow Universe so the
   new class actually generalises.
3. Re-run with `--epochs 40` (not 5) for a proper fit.

## Validation metrics

```json
{
  "precision": 0.6635073118215348,
  "recall": 0.5245201335666133,
  "mAP50": 0.5753835254794016,
  "mAP50-95": 0.3940968129286489,
  "per_class_AP50": {
    "0": 0.7324857142857144,
    "1": 0.3977843822843823,
    "2": 0.7197810865103972,
    "3": 0.5911209931443395,
    "4": 0.8502777777777778,
    "5": 0.5630255042941,
    "6": 0.4307777511420431,
    "7": 0.5942773899109222,
    "8": 0.749837420939542,
    "9": 0.8134871691802915,
    "10": 0.7131078632034029,
    "11": 0.672017681253788,
    "12": 0.5651994870457313,
    "13": 0.14630047155909226,
    "14": 0.995,
    "15": 0.3352140672782875,
    "16": 0.363695652173913,
    "17": 0.17402510314996855,
    "18": 0.5248714689749356
  }
}
```
