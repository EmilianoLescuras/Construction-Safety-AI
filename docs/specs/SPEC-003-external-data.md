# SPEC-003 — External Data Sourcing

**Phase:** Data · **Depends on:** SPEC-002 · **Effort:** 2 days

## Goal

The 52 reviewed frames from SPEC-001 are not enough on their own. Pull
~500 additional labelled images from Roboflow Universe so the new
`pickup` class generalises and the sparse PPE classes (`Ladder`, `Mask`,
`Excavator`) get more support.

## Prerequisites

- SPEC-002 complete (final taxonomy decided).
- Roboflow account (free tier).

## Tasks

- [ ] Inventory: dump v1 per-class instance count to
      `docs/dataset_stats.md`. Identify classes with < 100 instances.
- [ ] For each sparse class, search Roboflow Universe and pick 1-2
      datasets. Document the URL + license + per-class count in
      `docs/external_sources.md`.
- [ ] Write `scripts/merge_datasets.py`:
  - Input: list of source dirs + per-source class map (their idx → ours).
  - Output: copies images + remapped labels into
    `datasets/v2_external/{images,labels}/`, with provenance manifest.
  - Skip duplicates (perceptual hash on images).
- [ ] Add `datasets/v2_external/` to `data_v2.yaml` train globs.
- [ ] Re-split: 80% to train, 20% appended to val (so val grows too).

## Acceptance criteria

- `docs/external_sources.md` lists every source dataset, URL, license,
  class mapping.
- Total train image count grew by ≥ 300.
- `scripts/merge_datasets.py` writes a `manifest.json` per merge with
  source provenance for every file.
- No license violations (CC-BY / CC0 only — no "academic only" data in
  a portfolio repo).

## Out of scope

- Synthetic data generation (deferred to v3).
- Re-training (SPEC-004).
