# Inference Worker Service

`src/worker/` runs the full detection → tracking → rules pipeline on a video
source and POSTs the resulting violation events to the deployed API.

## Why separate from the API?

The API container is **slim** — no torch, no opencv, no ultralytics. That's
intentional:

- Faster cold starts on Cloud Run / Railway.
- Smaller image size (~150MB vs ~3GB).
- API can be deployed serverless; the worker only runs when there's a video
  to process.

The worker is **fat** — a single ~3GB container with the full ML stack.
You run it on the host where the cameras / video files live.

## Local usage (without Docker)

```bash
# Dry-run (no API calls)
python -m src.worker.cli \
  --source outputs/videos/your_clip.mp4 \
  --rules config/rules.json \
  --dry-run

# Against the local API
python -m src.worker.cli \
  --source outputs/videos/your_clip.mp4 \
  --rules config/rules.json \
  --api-url http://localhost:8000
```

## Docker usage

The `worker` service is opt-in (profile-gated) so it doesn't auto-start with
the rest of the stack:

```bash
# Build the worker image once
docker compose --profile worker build worker

# Run a job. The container talks to the api service over the internal network
# (CS_API_URL=http://api:8000 by default).
docker compose --profile worker run --rm worker \
  --source /app/outputs/videos/your_clip.mp4 \
  --rules /app/config/rules.json
```

## Posting to a remote API

```bash
docker compose --profile worker run --rm \
  -e CS_API_URL=https://cs-api-prod.up.railway.app \
  worker --source /app/outputs/videos/your_clip.mp4 \
         --rules /app/config/rules.json
```

## Event flow

```
video → YOLO.track() → tracks_to_record() → RuleEngine.process_frame()
     → batch of 25 events → ApiClient.post_events() → POST /events/batch
     → API dedups on (rule, person_id, frame, source) and persists
```

Evidence images are **not** uploaded by the worker in this minimal
implementation — they're written locally. For a real production worker the
evidence pipeline would need to either:
1. Upload images to S3/GCS and store the URL in the DB, or
2. Run a separate evidence-upload step that the API offers.

## Limitations

- Single-video, single-process. For multiple cameras, run multiple worker
  containers in parallel (each with its own `--source` and `--source-label`).
- No retry/backoff on API failures — failed batches are logged and lost.
  Real production would queue events to disk and retry.
