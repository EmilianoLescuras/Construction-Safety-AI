# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `Makefile` with self-documenting dev targets (install, lint, test, api, frontend, migrate, up, down).
- CI, license, and Python-version badges in the README.
- YOLOv8-vs-YOLO26 side-by-side comparison video, featured in the README Live demo.

## [0.2.0] — 2026-06-28 — v2 dataset & demo polish

### Changed
- Pivoted the class schema from the 19-class construction dataset to a
  34-class riskalert-mining config (`config/data.yaml`).
- YOLOv8s v2 backbone beats the v1 baseline on both validation and test.

### Added
- Pseudo-labeling pipeline and v2 fine-tune scaffold.
- Label Studio import + CORS-enabled frame server for data correction (spec01).
- 11-spec roadmap from v1 demo to production finalization.
- `/demo` frontend page with a real tracked construction clip and image gallery.

## [0.1.0] — 2026-06-23 — Portfolio-ready end-to-end platform

### Added
- **Phase 1–6:** project scaffold, dataset prep + EDA, YOLOv8n baseline and
  40-epoch training, image/video/webcam/RTSP inference, ByteTrack tracking with
  JSONL logs.
- **Phase 7–8:** declarative PPE rule engine emitting `ViolationEvent`s,
  pluggable alert sinks with evidence capture and a dispatcher.
- **Phase 9–10:** FastAPI + SQLAlchemy + Alembic persistence layer, DbSink audit
  sink, and a Next.js dashboard.
- **Phase 11:** Docker Compose end-to-end stack + GitHub Actions CI.
- **Phase 12:** MLflow training tracking, relative evidence paths, pytest suite
  (rule engine + dispatcher + API), and a Playwright e2e suite.
- Deploy configs (Railway + GCP Cloud Run), inference worker service,
  portfolio README, MIT license, and DVC + v2 roadmap docs.

[Unreleased]: https://github.com/EmilianoLescuras/Construction-Safety-AI/compare/main...HEAD
