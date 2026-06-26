# SPEC-001 — Data Correction Pass

**Phase:** Data · **Depends on:** none · **Effort:** 1 day

## Goal

Turn the 52 pseudo-labelled frames in `datasets/v2_inbox/` into
ground-truth labels by manually correcting them in a labelling tool.
This is the prerequisite for *any* real v2 improvement — fine-tuning on
uncorrected pseudo-labels just reinforces v1's existing biases (proven
by `docs/experiments/v2_pipeline_smoke.md`).

## Prerequisites

- `datasets/v2_inbox/{images,labels}` populated (already done — see
  `scripts/pseudo_label_video.py`).
- Label Studio or Roboflow workspace.

## Tasks

- [ ] Pick a tool: Label Studio (local) **or** Roboflow (cloud). Both
      accept YOLO format and `classes.txt`.
- [ ] Import `datasets/v2_inbox/` as a new project.
- [ ] Review every frame. For each one:
  - [ ] Fix `sedan` boxes that are actually pickups (don't add new class
        yet — that's SPEC-002).
  - [ ] Add `Safety Vest` boxes around workers in hi-vis long-sleeve
        shirts that v1 missed.
  - [ ] Remove duplicate / nonsense boxes.
- [ ] Export back to YOLO format, overwriting `datasets/v2_inbox/labels/`.
- [ ] Add a one-line entry per frame to `datasets/v2_inbox/REVIEW.md`
      noting what was changed.

## Acceptance criteria

- Every `.txt` file in `datasets/v2_inbox/labels/` has been opened and
  reviewed by a human.
- Total label count grew (we added missed hi-vis vests, didn't only
  delete).
- `REVIEW.md` exists with at least one line per reviewed frame.

## Out of scope

- Adding new classes (SPEC-002).
- Sourcing more images (SPEC-003).
- Re-training (SPEC-004).
