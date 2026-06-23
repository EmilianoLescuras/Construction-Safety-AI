# DVC — Dataset & Model Versioning

[DVC](https://dvc.org/) is git-for-data. We use it to version-control two
asset types that are too large for git itself:

| Asset            | Path             | Size class | Why version it |
|------------------|------------------|------------|----------------|
| Roboflow dataset | `datasets/`      | ~MB-GB     | reproduce training runs against the same labels |
| Trained models   | `models/*.pt`    | ~10-50 MB  | reproduce inference; ship a specific checkpoint to prod |

## One-time setup (per developer)

```bash
# Install dvc with the local-storage extra (no cloud dep)
pip install "dvc>=3.50.0"

# From repo root
dvc init
git commit -m "chore(dvc): initialize"
```

`dvc init` creates `.dvc/` (config + cache layout) and a top-level `.dvcignore`.

## Track the dataset

```bash
# Move the dataset under DVC control. This:
#   1. moves contents into the DVC cache (.dvc/cache by default)
#   2. writes datasets.dvc — a tiny YAML pointer that git tracks
#   3. updates .gitignore to ignore the original directory
dvc add datasets/

git add datasets.dvc .gitignore
git commit -m "data: snapshot of dataset v1 (719 images, 19 classes)"
```

## Track the production model

```bash
dvc add models/yolov8n_construction_safety_e40_cache.pt
git add models/yolov8n_construction_safety_e40_cache.pt.dvc .gitignore
git commit -m "model: yolov8n e40 baseline (mAP50=0.577)"
```

## Storage backends

For a solo portfolio project, the local cache is enough — `dvc add` already
deduplicates by content hash. For multi-machine work or a real team, add a
remote:

```bash
# S3
dvc remote add -d origin s3://my-bucket/cs-dvc
dvc remote modify origin region us-east-1

# Or GCS
dvc remote add -d origin gs://my-bucket/cs-dvc

# Or just a Google Drive folder (zero infra)
dvc remote add -d origin gdrive://<folder-id>

# Push
dvc push
```

## Pulling data on a fresh clone

```bash
git clone <repo>
cd construction_safety_ai
pip install dvc
dvc pull   # downloads dataset + model from the configured remote
```

## Why we don't run `dvc init` in this repo automatically

It rewrites `.git/info/exclude`, creates `.dvc/`, and locks you into the DVC
workflow. That's a project-level decision the maintainer should make
explicitly — these docs prep the ground but stop short of pulling the
trigger. Run the commands above when you're ready.

## What `dvc status` looks like in practice

```
$ dvc status
datasets.dvc:
        changed outs:
                modified:           datasets

models/yolov8n_construction_safety_e40_cache.pt.dvc:
        not in cache:
                models/yolov8n_construction_safety_e40_cache.pt
```

Same mental model as `git status` — change → `dvc add` → commit the `.dvc` file → optionally `dvc push`.
