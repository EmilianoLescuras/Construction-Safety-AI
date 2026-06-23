"""Run YOLO inference on a video file and write an annotated copy.

Usage:
    python inference/detect_video.py --source path/to/clip.mp4
    python inference/detect_video.py --source clip.mp4 --conf 0.4 --out-dir outputs/videos
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.inference import PROJECT_ROOT, load_model, predict_and_annotate

OUT_DIR = PROJECT_ROOT / "outputs" / "videos"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Video file")
    parser.add_argument("--model", type=Path, default=None)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--fourcc", default="mp4v", help="OpenCV VideoWriter FourCC")
    args = parser.parse_args()

    src = args.source.expanduser().resolve()
    if not src.is_file():
        raise SystemExit(f"Video not found: {src}")
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(src))
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {src}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    model = load_model(args.model)
    out_path = out_dir / f"{src.stem}_pred.mp4"
    writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*args.fourcc), fps, (w, h))

    try:
        out_display = out_path.relative_to(PROJECT_ROOT)
    except ValueError:
        out_display = out_path
    print(f"[detect-video] src={src.name} frames={n_frames} fps={fps:.1f} {w}x{h}")
    print(f"[detect-video] out={out_display}")

    t0 = time.time()
    i = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            annotated, _ = predict_and_annotate(model, frame, args.conf, args.iou)
            writer.write(annotated)
            i += 1
            if i % 50 == 0:
                elapsed = time.time() - t0
                eta = (elapsed / i) * (n_frames - i) if n_frames > 0 else 0
                print(f"  frame {i}/{n_frames or '?'}  {i / elapsed:.1f} fps  eta {eta:.1f}s")
    finally:
        cap.release()
        writer.release()

    dt = time.time() - t0
    print(f"[detect-video] Done. {i} frames in {dt:.1f}s ({i / dt:.1f} fps)")


if __name__ == "__main__":
    main()
