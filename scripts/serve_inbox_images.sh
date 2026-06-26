#!/usr/bin/env bash
# Serve the project tree over plain HTTP so Label Studio can load the
# v2_inbox frames via absolute URLs (http://localhost:8082/datasets/...).
#
# This sidesteps Label Studio's local-files endpoint, which is finicky on
# LS >= 1.23 (legacy-token auth disabled, document-root resolution quirks).
# Generate the matching tasks file with:
#   .venv/bin/python scripts/yolo_to_labelstudio.py --http-base http://localhost:8082
#
# Leave this running in its own terminal while you label, then Ctrl-C it.
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${IMG_PORT:-8082}"
# Use the CORS-enabled server (plain http.server lacks the
# Access-Control-Allow-Origin header Label Studio's canvas loader needs).
exec .venv/bin/python scripts/serve_inbox_images.py --port "$PORT" --bind 127.0.0.1
