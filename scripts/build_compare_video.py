"""Build a side-by-side comparison video: YOLOv8 vs YOLO26 on the riskalert
test images (same 34-class dataset — a fair, same-domain comparison).

Left panel  = yolov8s_riskalert_e60  (YOLOv8)
Right panel = yolo26s_riskalert_e60  (YOLO26)

Each test frame is run through both models, annotated with each model's own
boxes/labels, captioned, and concatenated horizontally. Encoded to H.264 /
yuv420p via the ffmpeg bundled with imageio-ffmpeg (no system ffmpeg needed)
so it plays in the browser <video> on the /demo page.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import imageio_ffmpeg
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_IMAGES = Path("/Users/nanolescuras/Downloads/riskalert-mining-pivot.yolov8/test/images")

LEFT_MODEL = PROJECT_ROOT / "models/yolov8s_riskalert_e60.pt"
RIGHT_MODEL = PROJECT_ROOT / "models/yolo26s_riskalert_e60.pt"
LEFT_LABEL = "YOLOv8  (riskalert e60)"
RIGHT_LABEL = "YOLO26  (riskalert e60)"

PANEL = 640
HEADER = 44


def caption(panel, text):
    """Stack a black header strip with white centered-ish text over a panel."""
    bar = panel[:HEADER].copy() * 0  # black strip same width
    cv2.putText(bar, text, (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (255, 255, 255), 2, cv2.LINE_AA)
    return cv2.vconcat([bar, panel])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--conf", type=float, default=0.35)
    ap.add_argument("--fps", type=float, default=2.0)
    ap.add_argument("--limit", type=int, default=0, help="0 = all test images")
    ap.add_argument("--out", default="frontend/public/demo/compare_v8_vs_yolo26.mp4")
    args = ap.parse_args()

    left = YOLO(str(LEFT_MODEL))
    right = YOLO(str(RIGHT_MODEL))

    imgs = sorted(TEST_IMAGES.glob("*.jpg"))
    if args.limit:
        imgs = imgs[: args.limit]
    if not imgs:
        raise SystemExit(f"No images in {TEST_IMAGES}")

    out = PROJECT_ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    W, H = PANEL * 2, PANEL + HEADER
    writer = imageio_ffmpeg.write_frames(
        str(out), (W, H), fps=args.fps, codec="libx264",
        pix_fmt_in="rgb24", pix_fmt_out="yuv420p", macro_block_size=1,
        output_params=["-crf", "23"],
    )
    writer.send(None)

    for i, p in enumerate(imgs, 1):
        im = cv2.imread(str(p))
        if im is None:
            continue
        im = cv2.resize(im, (PANEL, PANEL))
        la = left.predict(im, conf=args.conf, verbose=False)[0].plot()
        ra = right.predict(im, conf=args.conf, verbose=False)[0].plot()
        col_l = caption(la, LEFT_LABEL)
        col_r = caption(ra, RIGHT_LABEL)
        frame = cv2.hconcat([col_l, col_r])
        writer.send(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if i % 10 == 0:
            print(f"  {i}/{len(imgs)} frames")

    writer.close()
    print(f"[compare] wrote {len(imgs)} frames -> {out.relative_to(PROJECT_ROOT)}")
    print(f"[compare] size: {out.stat().st_size/1e6:.1f} MB")


if __name__ == "__main__":
    main()
