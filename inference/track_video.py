"""Track objects across a video file with ByteTrack and write outputs.

Outputs:
  - outputs/videos/<stem>_track.mp4   annotated video with persistent IDs
  - outputs/logs/<stem>_track.jsonl   one JSON record per frame (rule-engine ready)

Usage:
    python inference/track_video.py --source path/to/clip.mp4
    python inference/track_video.py --source clip.mp4 --conf 0.4 --classes 8,5,6,7
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.inference import PROJECT_ROOT, load_model
from src.tracking import JsonlWriter, annotate_tracked_frame, track_frame, tracks_to_record

OUT_VIDEOS = PROJECT_ROOT / "outputs" / "videos"
OUT_LOGS = PROJECT_ROOT / "outputs" / "logs"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Video file")
    parser.add_argument("--model", type=Path, default=None)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--tracker", default="bytetrack.yaml", help="Ultralytics tracker config")
    parser.add_argument("--video-out-dir", type=Path, default=OUT_VIDEOS)
    parser.add_argument("--log-out-dir", type=Path, default=OUT_LOGS)
    parser.add_argument("--fourcc", default="mp4v")
    args = parser.parse_args()

    src = args.source.expanduser().resolve()
    if not src.is_file():
        raise SystemExit(f"Video not found: {src}")
    video_out_dir = args.video_out_dir.expanduser().resolve()
    log_out_dir = args.log_out_dir.expanduser().resolve()
    video_out_dir.mkdir(parents=True, exist_ok=True)
    log_out_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(src))
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {src}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    model = load_model(args.model)
    video_out = video_out_dir / f"{src.stem}_track.mp4"
    log_out = log_out_dir / f"{src.stem}_track.jsonl"
    writer = cv2.VideoWriter(str(video_out), cv2.VideoWriter_fourcc(*args.fourcc), fps, (w, h))

    print(f"[track-video] src={src.name} frames={n_frames} fps={fps:.1f} {w}x{h}")
    print(f"[track-video] video out -> {video_out}")
    print(f"[track-video] log   out -> {log_out}")

    t_start = time.time()
    seen_ids: set[int] = set()
    i = 0
    try:
        with JsonlWriter(log_out) as jsonl:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                results = track_frame(model, frame, args.conf, args.iou, args.tracker, persist=True)
                res = results[0]
                annotated = annotate_tracked_frame(frame, res, model.names, conf_threshold=args.conf)
                writer.write(annotated)

                rec = tracks_to_record(i, time.time(), res, model.names)
                jsonl.write(rec)
                for t in rec["tracks"]:
                    if t["id"] >= 0:
                        seen_ids.add(t["id"])

                i += 1
                if i % 50 == 0:
                    elapsed = time.time() - t_start
                    eta = (elapsed / i) * (n_frames - i) if n_frames > 0 else 0
                    print(f"  frame {i}/{n_frames or '?'}  "
                          f"{i / elapsed:.1f} fps  unique_ids={len(seen_ids)}  eta {eta:.1f}s")
    finally:
        cap.release()
        writer.release()

    dt = time.time() - t_start
    print(f"[track-video] Done. {i} frames in {dt:.1f}s ({i / dt:.1f} fps), "
          f"unique track IDs = {len(seen_ids)}")


if __name__ == "__main__":
    main()
