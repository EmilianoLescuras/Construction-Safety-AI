"""Run YOLO inference on a single image or a directory of images.

Usage:
    python inference/detect_image.py --source path/to/image.jpg
    python inference/detect_image.py --source path/to/dir/ --conf 0.4
    python inference/detect_image.py --source datasets/test/images --model models/<name>.pt

Outputs are written to ``outputs/images/predictions/`` with a ``_pred`` suffix.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.inference import PROJECT_ROOT, load_model, predict_and_annotate

OUT_DIR = PROJECT_ROOT / "outputs" / "images" / "predictions"
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def iter_images(source: Path) -> list[Path]:
    if source.is_file():
        if source.suffix.lower() not in IMG_EXTS:
            raise SystemExit(f"Not an image: {source}")
        return [source]
    if source.is_dir():
        return sorted(p for p in source.iterdir() if p.suffix.lower() in IMG_EXTS)
    raise SystemExit(f"Source not found: {source}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Image file or directory")
    parser.add_argument("--model", type=Path, default=None, help="Path to .pt weights (default: best baseline)")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    images = iter_images(args.source.expanduser().resolve())
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    model = load_model(args.model)
    try:
        out_display = out_dir.relative_to(PROJECT_ROOT)
    except ValueError:
        out_display = out_dir
    print(f"[detect-image] model={Path(model.ckpt_path).name if model.ckpt_path else 'inline'} "
          f"images={len(images)} out={out_display}")

    for img_path in images:
        frame = cv2.imread(str(img_path))
        if frame is None:
            print(f"  [warn] could not read {img_path}")
            continue
        annotated, results = predict_and_annotate(model, frame, args.conf, args.iou)
        out_path = out_dir / f"{img_path.stem}_pred{img_path.suffix}"
        cv2.imwrite(str(out_path), annotated)
        n = len(results[0].boxes) if results[0].boxes is not None else 0
        print(f"  {img_path.name:60s} -> {n:3d} detections")

    print(f"[detect-image] Done. Wrote {len(images)} files to {out_dir}")


if __name__ == "__main__":
    main()
