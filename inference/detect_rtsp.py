"""Run YOLO inference on an RTSP camera stream. Press 'q' to quit.

Usage:
    python inference/detect_rtsp.py --url rtsp://user:pass@host:554/stream
    python inference/detect_rtsp.py                  # reads RTSP_URL_CAM1 from .env

The URL is read from ``--url`` if provided, otherwise from the env var
``RTSP_URL_CAM1`` (loaded from .env via python-dotenv).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.inference import PROJECT_ROOT, load_model, predict_and_annotate

OUT_DIR = PROJECT_ROOT / "outputs" / "videos"


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=None, help="RTSP URL (defaults to RTSP_URL_CAM1 env)")
    parser.add_argument("--model", type=Path, default=None)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--reconnect-on-drop", action="store_true",
                        help="On stream drop, reopen the URL instead of exiting")
    args = parser.parse_args()

    url = args.url or os.getenv("RTSP_URL_CAM1")
    if not url:
        raise SystemExit("No RTSP URL: pass --url or set RTSP_URL_CAM1 in .env")

    model = load_model(args.model)
    writer = None

    def open_stream() -> cv2.VideoCapture:
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            raise SystemExit(f"Could not open RTSP stream: {url}")
        return cap

    cap = open_stream()
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720

    if args.save:
        out_dir = args.out_dir.expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = out_dir / f"rtsp_{stamp}.mp4"
        writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), 20.0, (w, h))
        try:
            out_display = out_path.relative_to(PROJECT_ROOT)
        except ValueError:
            out_display = out_path
        print(f"[detect-rtsp] saving to {out_display}")

    print(f"[detect-rtsp] streaming {url}. Press 'q' to quit.")
    t_prev = time.time()
    fps = 0.0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[detect-rtsp] frame grab failed.")
                if args.reconnect_on_drop:
                    cap.release()
                    time.sleep(1.0)
                    cap = open_stream()
                    continue
                break

            annotated, _ = predict_and_annotate(model, frame, args.conf, args.iou)

            now = time.time()
            dt = now - t_prev
            t_prev = now
            if dt > 0:
                fps = 0.9 * fps + 0.1 * (1.0 / dt) if fps else 1.0 / dt
            cv2.putText(annotated, f"{fps:.1f} fps", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(annotated, f"{fps:.1f} fps", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)

            if writer is not None:
                writer.write(annotated)
            cv2.imshow("Construction Safety AI — RTSP", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
