"""Build a continuous "demo reel" video from the gallery predictions.

Renders each annotated image for N seconds on a 1280x720 canvas with a
title overlay (VIOLATION / COMPLIANT badge + detected counts), then
encodes to H.264 baseline yuv420p via the imageio_ffmpeg binary so any
browser can play it inline.

Usage:
    python scripts/build_demo_reel.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GALLERY = PROJECT_ROOT / "outputs" / "demo_gallery"
OUT_DIR = PROJECT_ROOT / "frontend" / "public" / "demo"
OUT_VIDEO = OUT_DIR / "sample_run.mp4"

CANVAS_W, CANVAS_H = 1280, 720
FPS = 30
SECONDS_PER_IMAGE = 2.5
BACKGROUND = (24, 24, 27)  # zinc-900-ish in BGR


def letterbox(img, w: int, h: int):
    ih, iw = img.shape[:2]
    scale = min(w / iw, h / ih) * 0.92  # leave a small margin
    nw, nh = int(iw * scale), int(ih * scale)
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
    canvas = cv2.UMat(h, w, cv2.CV_8UC3) if False else None
    import numpy as np
    canvas = np.full((h, w, 3), BACKGROUND, dtype=np.uint8)
    x = (w - nw) // 2
    y = (h - nh) // 2
    canvas[y:y + nh, x:x + nw] = resized
    return canvas


def draw_overlay(canvas, item: dict, idx: int, total: int):
    status = item["status"]
    color = {
        "VIOLATION": (0, 38, 220),     # red BGR
        "COMPLIANT": (54, 163, 16),    # green BGR
        "NO-DETECTION": (110, 110, 110),
    }.get(status, (110, 110, 110))

    # Top header bar
    cv2.rectangle(canvas, (0, 0), (CANVAS_W, 56), (18, 18, 21), -1)
    cv2.putText(canvas, "Construction Safety AI  ·  Live Inference Demo",
                (20, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (235, 235, 235), 1, cv2.LINE_AA)
    progress = f"{idx}/{total}"
    (pw, _), _ = cv2.getTextSize(progress, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    cv2.putText(canvas, progress, (CANVAS_W - pw - 20, 36),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1, cv2.LINE_AA)

    # Status badge bottom-left
    label = f"  {status}  "
    (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    x1, y1 = 24, CANVAS_H - 80
    cv2.rectangle(canvas, (x1, y1), (x1 + lw + 16, y1 + lh + 24), color, -1)
    cv2.putText(canvas, label, (x1 + 8, y1 + lh + 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

    # Stats bottom-right
    stats = f"persons {item['persons']}   violations {item['violations']}   PPE OK {item['compliances']}"
    (sw, sh), _ = cv2.getTextSize(stats, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    cv2.rectangle(canvas, (CANVAS_W - sw - 40, CANVAS_H - 80),
                  (CANVAS_W - 24, CANVAS_H - 80 + sh + 24), (18, 18, 21), -1)
    cv2.putText(canvas, stats, (CANVAS_W - sw - 32, CANVAS_H - 80 + sh + 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (235, 235, 235), 1, cv2.LINE_AA)


def main() -> None:
    manifest_path = GALLERY / "manifest.json"
    if not manifest_path.exists():
        print(f"[reel] manifest missing — run scripts/build_demo_gallery.py first")
        sys.exit(1)
    manifest = json.loads(manifest_path.read_text())
    # Skip no-detection ones — they look broken in a reel
    items = [m for m in manifest["items"] if m["status"] != "NO-DETECTION"]
    print(f"[reel] building reel from {len(items)} clips "
          f"({SECONDS_PER_IMAGE}s each = {len(items) * SECONDS_PER_IMAGE:.0f}s total)")

    frames_per_clip = int(FPS * SECONDS_PER_IMAGE)
    tmp = Path(tempfile.mkdtemp(prefix="reel_"))
    raw_path = tmp / "raw.mp4"
    # Use cv2 to write a raw mp4 (mp4v), then ffmpeg-transcode to baseline H.264.
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(raw_path), fourcc, FPS, (CANVAS_W, CANVAS_H))
    if not writer.isOpened():
        print("[reel] failed to open VideoWriter")
        sys.exit(1)

    total = len(items)
    for i, item in enumerate(items, 1):
        pred = GALLERY / item["prediction"]
        img = cv2.imread(str(pred))
        if img is None:
            print(f"  [warn] missing {pred}")
            continue
        canvas = letterbox(img, CANVAS_W, CANVAS_H)
        draw_overlay(canvas, item, i, total)
        for _ in range(frames_per_clip):
            writer.write(canvas)
        print(f"  [{i:02d}/{total}] {item['status']:12s} {item['source_name']}")

    writer.release()
    print(f"[reel] raw mp4: {raw_path} ({raw_path.stat().st_size // 1024} KB)")

    # Transcode to H.264 baseline yuv420p for browser playback.
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        ff, "-y", "-i", str(raw_path),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-profile:v", "baseline", "-level", "3.1",
        "-movflags", "+faststart", "-an",
        str(OUT_VIDEO),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.rmtree(tmp)
    print(f"[reel] wrote {OUT_VIDEO} ({OUT_VIDEO.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
