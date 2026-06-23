# Railway Deployment

Single-command deploy of the full stack (Postgres + API + Frontend) to [Railway](https://railway.app).

## One-time setup

1. Create a Railway account and install the CLI:
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. From the repo root, link a project:
   ```bash
   railway init
   ```

## Deploy

Three services need to be created in Railway's UI (one click each):

### 1. Postgres
Use Railway's `Postgres` template. It will provision a managed Postgres and
expose `DATABASE_URL`, `PGHOST`, etc. as service variables.

### 2. API service
- **Source**: this GitHub repo, root directory `.`
- **Dockerfile path**: `docker/api/Dockerfile`
- **Variables**:
  - `DATABASE_URL` → bind to `${{Postgres.DATABASE_URL}}` (Railway syntax, but
    `psycopg2-binary` needs `postgresql+psycopg2://` so override with:
    `postgresql+psycopg2://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/${{Postgres.PGDATABASE}}`)
  - `PORT` → `8000`
- **Healthcheck**: `/health`

### 3. Frontend service
- **Source**: same repo, root directory `frontend`
- **Dockerfile path**: `docker/frontend/Dockerfile`
- **Build arg**: `NEXT_PUBLIC_API_URL` → the *public* URL Railway assigns to the
  API service (e.g. `https://cs-api-production.up.railway.app`).
  Set this in Railway → API service → Settings → Generate Domain first,
  then paste the URL into the frontend's build arg.
- **Variables**:
  - `PORT` → `3000`

## Caveats

- Evidence images: the production container has no `./outputs/` mount, so
  evidence saved during inference (run on the user's laptop or a worker
  service) needs to live somewhere durable. Railway has ephemeral filesystems
  by default — for production you'd swap `EvidenceConfig.out_dir` for an S3 /
  GCS / R2 bucket. Out of scope for this minimal config.
- The free Railway tier has resource limits; the API + Frontend + Postgres
  should fit comfortably (under 512MB each).

## Cost

At time of writing Railway has a $5/month starter credit; this stack uses ~$3/mo idle.
