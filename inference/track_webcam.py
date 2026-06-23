"""Live webcam tracking with ByteTrack. Press 'q' to quit.

Usage:
    python inference/track_webcam.py
    python inference/track_webcam.py --camera 1 --save
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.inference import PROJECT_ROOT, load_model
from src.tracking import JsonlWriter, annotate_tracked_frame, track_frame, tracks_to_record

OUT_VIDEOS = PROJECT_ROOT / "outputs" / "videos"
OUT_LOGS = PROJECT_ROOT / "outputs" / "logs"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--model", type=Path, default=None)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--tracker", default="bytetrack.yaml")
    parser.add_argument("--save", action="store_true", help="Save annotated video and JSONL log")
    parser.add_argument("--video-out-dir", type=Path, default=OUT_VIDEOS)
    parser.add_argument("--log-out-dir", type=Path, default=OUT_LOGS)
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise SystemExit(f"Could not open camera index {args.camera}")
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480

    model = load_model(args.model)

    video_writer = None
    jsonl = None
    if args.save:
        video_dir = args.video_out_dir.expanduser().resolve()
        log_dir = args.log_out_dir.expanduser().resolve()
        video_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        vpath = video_dir / f"webcam_track_{stamp}.mp4"
        lpath = log_dir / f"webcam_track_{stamp}.jsonl"
        video_writer = cv2.VideoWriter(str(vpath), cv2.VideoWriter_fourcc(*"mp4v"), 20.0, (w, h))
        jsonl = JsonlWriter(lpath)
        print(f"[track-webcam] saving video -> {vpath}")
        print(f"[track-webcam] saving log   -> {lpath}")

    print("[track-webcam] streaming. Press 'q' to quit.")
    t_prev = time.time()
    fps = 0.0
    i = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[track-webcam] frame grab failed; exiting")
                break
            results = track_frame(model, frame, args.conf, args.iou, args.tracker, persist=True)
            res = results[0]
            annotated = annotate_tracked_frame(frame, res, model.names, conf_threshold=args.conf)

            now = time.time()
            dt = now - t_prev
            t_prev = now
            if dt > 0:
                fps = 0.9 * fps + 0.1 * (1.0 / dt) if fps else 1.0 / dt
            cv2.putText(annotated, f"{fps:.1f} fps", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(annotated, f"{fps:.1f} fps", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)

            if video_writer is not None:
                video_writer.write(annotated)
            if jsonl is not None:
                jsonl.write(tracks_to_record(i, now, res, model.names))
            cv2.imshow("Construction Safety AI — webcam tracking", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            i += 1
    finally:
        cap.release()
        if video_writer is not None:
            video_writer.release()
        if jsonl is not None:
            jsonl.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
