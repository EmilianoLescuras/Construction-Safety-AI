"""Extract frames from a video and write YOLO-format pseudo-labels using v1.

This is the **honest** path to a v2 fine-tune:

1. v1 predicts on every Nth frame and writes a label file (one .txt per
   image, YOLO format) into ``datasets/v2_inbox/labels/``.
2. The matching frame is saved to ``datasets/v2_inbox/images/``.
3. You **must** open these in Label Studio / Roboflow / CVAT and:
   - Fix mislabeled classes (e.g. ``sedan`` → new class ``pickup``).
   - Add the labels v1 misses (e.g. hi-vis long-sleeve shirts as
     ``Safety Vest``).
   - Add new classes by editing ``config/data.yaml``.
4. Then ``scripts/train.py`` mixes the corrected v2_inbox with the
   original train/valid splits for the actual fine-tune.

What this script does NOT do:
- It does not "train v2 from this video". You cannot train YOLO on raw
  pixels — you need labels. v1's labels are a starting point, not truth.
- It does not add new classes by itself. v1 only knows the 19 classes
  it was trained on.
- It does not guarantee improvements. Fine-tuning on uncorrected
  pseudo-labels reinforces v1's mistakes.

Usage:
    python scripts/pseudo_label_video.py \\
      --source outputs/videos/user_recording_v2.mp4 \\
      --stride 10 --conf 0.40
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.inference import PROJECT_ROOT, load_model

INBOX = PROJECT_ROOT / "datasets" / "v2_inbox"


def to_yolo(bbox_xyxy, img_w: int, img_h: int) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = bbox_xyxy
    cx = (x1 + x2) / 2 / img_w
    cy = (y1 + y2) / 2 / img_h
    w = (x2 - x1) / img_w
    h = (y2 - y1) / img_h
    return cx, cy, w, h


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--stride", type=int, default=10,
                        help="Sample every N frames (default 10 → ~3fps from a 30fps clip)")
    parser.add_argument("--conf", type=float, default=0.40)
    parser.add_argument("--out", type=Path, default=INBOX)
    args = parser.parse_args()

    src = args.source.expanduser().resolve()
    if not src.exists():
        sys.exit(f"Source not found: {src}")

    out_root = args.out.expanduser().resolve()
    img_dir = out_root / "images"
    lbl_dir = out_root / "labels"
    if out_root.exists():
        shutil.rmtree(out_root)
    img_dir.mkdir(parents=True)
    lbl_dir.mkdir(parents=True)

    model = load_model(None)
    class_names = model.names if isinstance(model.names, list) else list(model.names.values())
    (out_root / "classes.txt").write_text("\n".join(class_names))

    cap = cv2.VideoCapture(str(src))
    if not cap.isOpened():
        sys.exit(f"Could not open {src}")
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    stem = src.stem
    written = 0
    frame_idx = 0
    summary: list[dict] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_idx % args.stride == 0:
            h, w = frame.shape[:2]
            results = model.predict(source=frame, conf=args.conf, iou=0.45, verbose=False)
            boxes = results[0].boxes
            lines = []
            n_boxes = 0
            if boxes is not None and len(boxes) > 0:
                xyxy = boxes.xyxy.cpu().numpy()
                clss = boxes.cls.cpu().numpy().astype(int)
                for bbox, cid in zip(xyxy, clss, strict=False):
                    cx, cy, bw, bh = to_yolo(bbox, w, h)
                    lines.append(f"{cid} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
                    n_boxes += 1
            name = f"{stem}_f{frame_idx:05d}"
            cv2.imwrite(str(img_dir / f"{name}.jpg"), frame)
            (lbl_dir / f"{name}.txt").write_text("\n".join(lines))
            summary.append({"frame": frame_idx, "boxes": n_boxes})
            written += 1
        frame_idx += 1
    cap.release()

    manifest = {
        "source": str(src.relative_to(PROJECT_ROOT)) if str(src).startswith(str(PROJECT_ROOT)) else str(src),
        "total_frames": total,
        "fps": fps,
        "stride": args.stride,
        "conf_threshold": args.conf,
        "extracted": written,
        "classes": class_names,
        "samples": summary[:5],
    }
    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2))

    boxes_total = sum(s["boxes"] for s in summary)
    print(f"[pseudo-label] wrote {written} frames + labels to {out_root}")
    print(f"[pseudo-label] {boxes_total} boxes total (avg {boxes_total / max(written, 1):.1f} per frame)")
    print(f"[pseudo-label] classes.txt has {len(class_names)} entries")
    print()
    print("NEXT STEPS")
    print("  1. Review the labels in Label Studio:")
    print("     pip install label-studio && label-studio start")
    print("  2. Or upload to Roboflow as a new annotation project.")
    print("  3. Fix v1 mistakes — especially:")
    print("     - 'sedan' boxes that are actually pickups → new class 'pickup'")
    print("     - Workers in hi-vis shirts unlabeled → add 'Safety Vest' boxes")
    print("  4. When done, merge into the train split and run scripts/train.py")


if __name__ == "__main__":
    main()
