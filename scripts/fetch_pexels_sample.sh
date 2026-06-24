#!/usr/bin/env bash
# Download a free CC0 construction-site clip from Pexels for the demo reel.
#
# Pexels videos are royalty-free under the Pexels License (commercial use OK,
# attribution appreciated). The CDN exposes predictable per-resolution URLs
# under videos.pexels.com/video-files/<ID>/<ID>-<quality>_<w>_<h>_<fps>fps.mp4.
#
# We pick the SD (640x360) variant so the demo asset stays small enough to
# ship in the repo.
set -euo pipefail

VIDEO_ID="9227135"  # "Construction Workers Working" by Polina Tankilevitch
URL="https://videos.pexels.com/video-files/${VIDEO_ID}/${VIDEO_ID}-sd_640_360_30fps.mp4"
OUT="outputs/videos/pexels_construction_${VIDEO_ID}.mp4"

mkdir -p outputs/videos
echo "[fetch] downloading $URL"
curl -L --fail -o "$OUT" "$URL"
echo "[fetch] saved to $OUT ($(du -h "$OUT" | cut -f1))"
echo ""
echo "Next:"
echo "  python inference/track_video.py --source $OUT --conf 0.25"
echo "  # then re-encode the *_track.mp4 to H.264 baseline for the browser:"
echo "  ffmpeg -y -i outputs/videos/pexels_construction_${VIDEO_ID}_track.mp4 \\"
echo "    -c:v libx264 -pix_fmt yuv420p -profile:v baseline -movflags +faststart \\"
echo "    -an frontend/public/demo/sample_run.mp4"
