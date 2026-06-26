# SPEC-008 — Active-Learning Loop

**Phase:** MLOps · **Depends on:** SPEC-006 · **Effort:** 1 day

## Goal

Make the deployed system continuously improve itself. Every detection
with `0.4 < conf < 0.6` (the uncertainty zone) gets its crop dumped to
a "needs review" bucket. Bi-weekly batch labelling round feeds back
into the next training run.

## Prerequisites

- SPEC-006 complete (we have a production model serving traffic).

## Tasks

- [ ] In the worker, when a detection lands in the uncertainty band:
  - Save the cropped image to `outputs/review_bucket/<date>/<event_id>.jpg`.
  - Append a row to `outputs/review_bucket/index.parquet` with
    timestamp, model version, predicted class, confidence, bbox, event_id.
- [ ] Cap the bucket: keep at most 5000 most-recent crops (rotate).
- [ ] Add a CLI: `python scripts/review_bucket.py export --since YYYY-MM-DD`
      → produces a Label-Studio-ready import JSON.
- [ ] Document the labelling cadence in `docs/active_learning.md`:
  who/when reviews, how the labels flow back into `datasets/`.
- [ ] Add a metric to MLflow: % of inferences landing in the uncertainty
      band per day (the "review pressure" KPI).

## Acceptance criteria

- The worker writes to the bucket on every uncertain detection without
  blocking the main inference path (async or end-of-pipeline).
- Bucket export round-trips through Label Studio cleanly.
- A 24-hour stress run produces a bucket of < 1GB.
- `docs/active_learning.md` describes the human workflow end-to-end.

## Out of scope

- Automatic re-training trigger (still human-in-the-loop).
- Multi-reviewer consensus.
