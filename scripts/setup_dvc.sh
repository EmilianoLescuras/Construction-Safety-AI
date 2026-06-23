#!/usr/bin/env bash
#
# Bootstrap DVC for this repo. Idempotent-ish: skips steps that already ran.
# See docs/dvc.md for the rationale.
#
# Usage:
#   bash scripts/setup_dvc.sh
#
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v dvc >/dev/null 2>&1; then
  echo "DVC not found. Install with: pip install 'dvc>=3.50.0'"
  exit 1
fi

if [[ ! -d .dvc ]]; then
  echo "[dvc] initializing"
  dvc init
fi

# Track dataset
if [[ -d datasets ]] && [[ ! -f datasets.dvc ]]; then
  echo "[dvc] adding datasets/"
  dvc add datasets/
fi

# Track every .pt under models/
shopt -s nullglob
for pt in models/*.pt; do
  if [[ ! -f "${pt}.dvc" ]]; then
    echo "[dvc] adding ${pt}"
    dvc add "${pt}"
  fi
done

echo
echo "[dvc] done. Next steps:"
echo "  git add .dvc .dvcignore datasets.dvc models/*.dvc .gitignore"
echo "  git commit -m 'chore(dvc): track dataset + models'"
echo "  (optional) dvc remote add -d origin <s3|gs|gdrive>://...  &&  dvc push"
