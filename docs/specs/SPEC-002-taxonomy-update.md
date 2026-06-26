# SPEC-002 — Taxonomy Update: `pickup` + Hi-Vis Shirt

**Phase:** Data · **Depends on:** SPEC-001 · **Effort:** 4 hours

## Goal

Evolve the 19-class taxonomy to fix v1's two most visible production
errors:

1. Pickups misclassified as `sedan` (very common on LATAM/AR sites).
2. Hi-vis long-sleeve work shirts flagged as `NO-Safety Vest`.

## Prerequisites

- SPEC-001 complete (so we have clean labels to remap).

## Tasks

- [ ] Decide on the final class list. Recommended (20 classes):
  - Keep all 19 v1 classes **except** collapse `vehicle` → `sedan` (or
    drop `vehicle`, it's a noisy catch-all).
  - Add `pickup` as class index 19.
- [ ] Update `config/data_v2.yaml`: bump `nc`, add `pickup` to `names`.
- [ ] Write `scripts/remap_labels.py`:
  - Input: a YOLO label dir + an old→new class map.
  - Output: same dir with class ids rewritten.
  - Idempotent; dry-run flag.
- [ ] Run remap on `datasets/v2_inbox/labels/` (existing reviewed labels
      where a sedan→pickup change is needed).
- [ ] Update `Safety Vest` policy doc: a worker in a hi-vis long-sleeve
      shirt with reflective tape counts as compliant. Add 5-10
      reference photos to `docs/labelling_policy.md`.

## Acceptance criteria

- `config/data_v2.yaml` `nc` matches `len(names)`.
- `scripts/remap_labels.py` has unit tests for: empty file, file with
  unknown class id (skip), file with mixed remap targets.
- A round-trip (remap forward, then remap back) reproduces the original
  files byte-for-byte.
- `docs/labelling_policy.md` exists.

## Out of scope

- Sourcing pickup images from elsewhere (SPEC-003).
- Re-training (SPEC-004).
