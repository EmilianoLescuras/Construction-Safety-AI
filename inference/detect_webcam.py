"""Run YOLO inference on a live webcam. Press 'q' to quit.

Usage:
    python inference/detect_webcam.py
    python inference/detect_webcam.py --camera 1 --conf 0.4
    python inference/detect_webcam.py --save        # also write the session to outputs/videos/

Note: macOS asks for camera permission the first time. Grant it to your terminal.
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.inference import PROJECT_ROOT, load_model, predict_and_annotate

OUT_DIR = PROJECT_ROOT / "outputs" / "videos"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0, help="Webcam index (default 0)")
    parser.add_argument("--model", type=Path, default=None)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--save", action="store_true", help="Save the session to outputs/videos/")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise SystemExit(f"Could not open camera index {args.camera}")
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480

    model = load_model(args.model)

    writer = None
    if args.save:
        out_dir = args.out_dir.expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = out_dir / f"webcam_{stamp}.mp4"
        writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), 20.0, (w, h))
        try:
            out_display = out_path.relative_to(PROJECT_ROOT)
        except ValueError:
            out_display = out_path
        print(f"[detect-webcam] saving to {out_display}")

    print("[detect-webcam] streaming. Press 'q' to quit.")
    t_prev = time.time()
    fps = 0.0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[detect-webcam] frame grab failed; exiting")
                break
            annotated, _ = predict_and_annotate(model, frame, args.conf, args.iou)

            now = time.time()
            dt = now - t_prev
            t_prev = now
            if dt > 0:
                fps = 0.9 * fps + 0.1 * (1.0 / dt) if fps else 1.0 / dt
            cv2.putText(
                annotated, f"{fps:.1f} fps", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3, cv2.LINE_AA,
            )
            cv2.putText(
                annotated, f"{fps:.1f} fps", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA,
            )

            if writer is not None:
                writer.write(annotated)
            cv2.imshow("Construction Safety AI — webcam", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
