#!/usr/bin/env bash
# Start Label Studio on http://localhost:8081 with local-files serving
# enabled, rooted at the project directory so the LS tasks file (which
# uses paths like ``/data/local-files/?d=datasets/v2_inbox/images/...``)
# resolves correctly.
#
# First run: sign up at http://localhost:8081 — the very first account
# created becomes admin. Then follow docs/specs/SPEC-001-data-correction.md
# step "Create the project".

set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${LS_PORT:-8081}"
DATA_DIR="${LS_DATA_DIR:-$HOME/Library/Application Support/label-studio}"

export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
export LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT="$PWD"

echo "[label-studio] root=$PWD"
echo "[label-studio] data=$DATA_DIR"
echo "[label-studio] port=$PORT"
echo "[label-studio] starting → http://localhost:$PORT"

exec .venv/bin/label-studio start \
    --port "$PORT" \
    --data-dir "$DATA_DIR" \
    --no-browser
