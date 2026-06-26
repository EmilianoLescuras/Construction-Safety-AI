# SPEC-011 — Case Study + Portfolio Writeup

**Phase:** Delivery · **Depends on:** all prior specs · **Effort:** 1 day

## Goal

Ship the project as a portfolio-grade case study. The repo is the
evidence; this spec is the *story* that lets a recruiter or hiring
manager understand what was built in 5 minutes.

## Prerequisites

- SPECs 01-10 done. (You can draft this earlier, but don't publish until
  the numbers are real.)

## Tasks

- [ ] Rewrite top-level `README.md` with the case-study structure:
  - Problem statement (PPE compliance, the business value of detection).
  - Approach (data → model → eval → deploy, with one line per phase).
  - Results table: v1 vs final v2 on the golden set (mAP50, per-class
    AP50 for the headline classes, p95 latency).
  - 3 annotated screenshots / GIFs showing real detection.
  - Stack diagram (mermaid in markdown).
  - "What's hard about this" — one short section on tradeoffs (n vs s
    backbone, pseudo-label pitfalls — link the smoke-test doc).
  - Links: `/demo` page, MLflow runs export, this `docs/specs/`
    directory.
- [ ] Record a 60-90s screen capture of `/demo` end-to-end (upload →
      detection → violation flagged). Save to `docs/screenshots/case_study.mp4`.
- [ ] Push the demo MP4 + a small subset of MLflow run data to the
      public-facing demo (not weights — weights stay private).
- [ ] Add a "Hiring managers — start here" link at the very top of the
      README pointing to the case study section.
- [ ] One-page PDF version (`docs/case_study.pdf`) for sharing in a
      cover-letter context.

## Acceptance criteria

- A reader who has never seen the repo understands what it does and
  what the results are without leaving the README.
- The results table cites numbers that match the latest
  `models/production/current.pt` evaluation.
- The 60-90s capture plays correctly in GitHub's markdown preview.
- No broken links, no "TODO" left in the README.

## Out of scope

- Blog post / Medium article (separate deliverable).
- Translating the README to Spanish (separate spec if you want it).

## Definition of project finalized

When this spec is `DONE`, the project is **finalized** per the
top-level `docs/specs/README.md` criteria.
