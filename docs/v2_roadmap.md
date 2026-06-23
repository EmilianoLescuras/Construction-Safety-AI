# v2 Roadmap — Model Improvements

The v1 baseline (`yolov8n_construction_safety_e40_cache.pt`) hits **mAP50=0.577** /
recall=0.528 on the 19-class Roboflow set. Good enough to ship the
end-to-end stack as a portfolio demo; not good enough for real production
PPE compliance. v2 is about closing that gap.

## Hard limits of v1

| Class | AP50 | Notes |
|---|---|---|
| Person | high | well represented (1148 instances) |
| NO-Safety Vest | high | 582 instances, well captured |
| Hardhat, NO-Hardhat | medium | 574 / similar |
| **Trailer, van, sedan, machinery, Ladder** | **low** | <60 instances each — chronic underfitting |
| Original v0 EPP plan (boots, goggles, ear_protection, harness) | n/a | **not in dataset** — deferred from v0 |

## v2 work items

### 1. Vehicle taxonomy collapse  *(no new labels needed)*

The dataset has `vehicle`, `truck`, `dump truck`, `van`, `sedan`, `trailer`,
`wheel loader`, `machinery` — many of them sparse. Collapse to two classes
(`vehicle`, `heavy_machinery`) and retrain. Expected: per-class AP gains
from sample-size jumps, no impact on the rule engine (no vehicle rules).

**Estimated effort**: 30 min editing `config/data.yaml` + remapping label
files + one 40-epoch run.

### 2. Source additional labelled data for sparse PPE  *(needs labelling)*

For the 4 deferred EPP classes (boots, goggles, ear_protection, harness),
options ranked by cost:

| Approach | Cost | Quality | Time |
|---|---|---|---|
| Public datasets (Roboflow Universe search) | Free | varies | 1-2 days hunting |
| Synthetic data (Unity Perception, NVIDIA Replicator) | Compute only | medium | 1 week |
| Outsourced labelling (Scale AI, Surge AI) | $0.05-0.10/box | high | 1-2 weeks |
| In-house labelling (Roboflow / Label Studio) | Time | high | weeks |

Recommendation: start with Roboflow Universe — there's existing labelled
work for safety harnesses and goggles that can be combined with v1 via
class-mapping.

### 3. Upgrade backbone yolov8n → yolov8s  *(low effort, real cost)*

Only worth doing **after** the data work — bigger model on undersized data
overfits. v8s typically gives +3-5 mAP50 on construction PPE. Training time
~2-3× longer (45-60 min on the same M4 MPS).

### 4. Add active-learning loop  *(MLOps stretch)*

Hook into the deployed worker: every event with `0.4 < conf < 0.6` gets the
crop dumped to a "needs review" bucket. Bi-weekly batch labelling round
feeds back into the next training run. This is the realistic path to >0.8
mAP50 in a year.

## Concrete next-action checklist

When you're ready to start v2:

- [ ] Audit current per-class AP50 from `runs/detect/<name>/results.csv`
- [ ] Decide on taxonomy collapse for vehicles (yes/no)
- [ ] Search Roboflow Universe for `harness`, `goggles`, `boots`
- [ ] Merge new sources with v1 via `scripts/merge_datasets.py` (doesn't exist yet — write it)
- [ ] Bump `config/data.yaml` class count and remap label files
- [ ] Train v8s, log to MLflow (`--mlflow-experiment construction-safety-v2`)
- [ ] Compare against v1 in MLflow UI; promote if mAP50 improves >5pp

## Out of scope (deferred to v3)

- 3D pose-based PPE detection (full-skeleton rigs)
- Multi-camera person re-id (track the same worker across cameras)
- Anomaly detection on behavior (e.g., person near excavator swing radius)
