# Deployment

Two ready-to-go targets:

| Target | Best for | Setup time | Cost (idle) |
|---|---|---|---|
| [`railway/`](railway/README.md) | Quick demo, portfolio link | ~10 min | ~$3/mo |
| [`gcp/`](gcp/README.md) | Production-grade, Cloud Build CI/CD | ~30 min | ~$7/mo |

Both deploy: Postgres + FastAPI backend + Next.js frontend.

## What's NOT included

- **Evidence storage**: evidence images are written to the local filesystem by
  the inference pipeline. For real production you'd swap
  `EvidenceConfig.out_dir` for an S3/GCS bucket and store the bucket key in
  the DB instead of a filesystem path. The portable-path helper
  `src/backend/paths.py` already abstracts this — only `save_evidence()` and
  the `/evidence/{id}` route would need updating.
- **Inference worker**: the deployed stack only persists + serves events.
  Actual video processing runs in the worker service (see `src/worker/`) which
  is meant to run on a host with GPU/CPU + camera or video files. The worker
  POSTs events to the deployed API.
