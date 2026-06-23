# GCP Cloud Run Deployment

Deploy the API + Frontend to [Cloud Run](https://cloud.google.com/run) with a
managed Postgres instance on Cloud SQL.

## Architecture

```
┌──────────┐     ┌──────────────┐     ┌────────────────┐
│  Users   │ ──► │  Cloud Run   │ ──► │  Cloud Run     │
│ (browser)│     │  Frontend    │     │  API           │
└──────────┘     │  (Next.js)   │     │  (FastAPI)     │
                 └──────────────┘     └────────┬───────┘
                                               │
                                       ┌───────▼───────┐
                                       │  Cloud SQL    │
                                       │  Postgres 16  │
                                       └───────────────┘

Evidence images → GCS bucket (out of scope of this minimal config).
```

## One-time setup

```bash
gcloud auth login
gcloud config set project <YOUR_PROJECT_ID>
gcloud services enable run.googleapis.com sqladmin.googleapis.com artifactregistry.googleapis.com

# Artifact Registry to host images
gcloud artifacts repositories create cs-images \
  --repository-format=docker \
  --location=us-central1
```

## Cloud SQL Postgres

```bash
gcloud sql instances create cs-db \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region=us-central1

gcloud sql databases create construction_safety --instance=cs-db
gcloud sql users create construction_safety \
  --instance=cs-db --password=<CHOOSE_A_STRONG_PASSWORD>
```

Note the connection name: `<PROJECT>:<REGION>:cs-db`.

## Build + push images

```bash
# From repo root
REGION=us-central1
PROJECT=<YOUR_PROJECT_ID>
REGISTRY="$REGION-docker.pkg.dev/$PROJECT/cs-images"

# API
docker build -f docker/api/Dockerfile -t $REGISTRY/cs-api:latest .
docker push $REGISTRY/cs-api:latest

# Frontend (note: NEXT_PUBLIC_API_URL must be the eventual Cloud Run URL of the API)
docker build -f docker/frontend/Dockerfile \
  --build-arg NEXT_PUBLIC_API_URL=https://cs-api-xxxxxxxxxx-uc.a.run.app \
  -t $REGISTRY/cs-frontend:latest frontend/
docker push $REGISTRY/cs-frontend:latest
```

## Deploy services

```bash
# API
gcloud run deploy cs-api \
  --image=$REGISTRY/cs-api:latest \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --add-cloudsql-instances=$PROJECT:$REGION:cs-db \
  --set-env-vars="DATABASE_URL=postgresql+psycopg2://construction_safety:<PASSWORD>@/construction_safety?host=/cloudsql/$PROJECT:$REGION:cs-db" \
  --port=8000 \
  --cpu=1 --memory=512Mi \
  --max-instances=3

# Frontend
gcloud run deploy cs-frontend \
  --image=$REGISTRY/cs-frontend:latest \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --port=3000 \
  --cpu=1 --memory=512Mi \
  --max-instances=3
```

## Two-pass deploy

The frontend bakes `NEXT_PUBLIC_API_URL` at build time, but you don't know the
API's Cloud Run URL until *after* the first deploy. The flow:

1. Deploy API once with placeholder frontend.
2. Copy the API URL Cloud Run prints.
3. Rebuild the frontend image with the real URL.
4. Re-deploy frontend.

## Database migrations

Cloud Run starts a fresh container per revision. Run alembic via Cloud Run
Jobs (one-shot):

```bash
gcloud run jobs create cs-migrate \
  --image=$REGISTRY/cs-api:latest \
  --region=$REGION \
  --add-cloudsql-instances=$PROJECT:$REGION:cs-db \
  --set-env-vars="DATABASE_URL=postgresql+psycopg2://construction_safety:<PASSWORD>@/construction_safety?host=/cloudsql/$PROJECT:$REGION:cs-db" \
  --command="alembic" \
  --args="upgrade,head"

gcloud run jobs execute cs-migrate --region=$REGION
```

## Cost estimate

Idle: ~$7/mo (Cloud SQL f1-micro). Cloud Run scales to zero, so API+Frontend
cost only when used (free tier: 2M req/mo).
