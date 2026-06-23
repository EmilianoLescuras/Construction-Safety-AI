"""Build a demo gallery: pick N test images, run YOLO, write a manifest.

Outputs into ``outputs/demo_gallery/``:

- ``originals/<stem>.jpg`` — copy of the source image (resized to max 960px wide)
- ``predictions/<stem>.jpg`` — annotated frame
- ``manifest.json`` — list of items with detected classes, compliance label, dims

Usage:
    python scripts/build_demo_gallery.py --source datasets/test/images --n 24
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.inference import PROJECT_ROOT, load_model, predict_and_annotate

VIOLATION_CLASSES = {"NO-Hardhat", "NO-Mask", "NO-Safety Vest"}
COMPLIANCE_CLASSES = {"Hardhat", "Mask", "Safety Vest", "Gloves"}
PERSON_CLASS = "Person"

OUT_ROOT = PROJECT_ROOT / "outputs" / "demo_gallery"


def resize_max_width(img, max_w: int):
    h, w = img.shape[:2]
    if w <= max_w:
        return img
    new_h = int(h * (max_w / w))
    return cv2.resize(img, (max_w, new_h), interpolation=cv2.INTER_AREA)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=PROJECT_ROOT / "datasets" / "test" / "images")
    parser.add_argument("--n", type=int, default=24)
    parser.add_argument("--conf", type=float, default=0.30)
    parser.add_argument("--max-width", type=int, default=960)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=OUT_ROOT)
    args = parser.parse_args()

    src_dir = args.source.expanduser().resolve()
    if not src_dir.is_dir():
        raise SystemExit(f"Not a directory: {src_dir}")

    out_root = args.out.expanduser().resolve()
    originals_dir = out_root / "originals"
    preds_dir = out_root / "predictions"

    # Clean previous run
    if out_root.exists():
        shutil.rmtree(out_root)
    originals_dir.mkdir(parents=True)
    preds_dir.mkdir(parents=True)

    all_imgs = sorted(p for p in src_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if not all_imgs:
        raise SystemExit(f"No images in {src_dir}")

    rng = random.Random(args.seed)
    picks = rng.sample(all_imgs, min(args.n, len(all_imgs)))

    model = load_model(None)
    class_names = model.names if isinstance(model.names, list) else list(model.names.values())

    manifest: list[dict] = []
    for i, img_path in enumerate(picks, 1):
        frame = cv2.imread(str(img_path))
        if frame is None:
            print(f"  [warn] skip {img_path.name}")
            continue
        frame = resize_max_width(frame, args.max_width)

        annotated, results = predict_and_annotate(model, frame, args.conf, 0.45)
        boxes = results[0].boxes

        detected: dict[str, int] = {}
        if boxes is not None and len(boxes) > 0:
            clss = boxes.cls.cpu().numpy().astype(int)
            for cid in clss:
                name = class_names[cid]
                detected[name] = detected.get(name, 0) + 1

        violations = sum(detected.get(c, 0) for c in VIOLATION_CLASSES)
        compliances = sum(detected.get(c, 0) for c in COMPLIANCE_CLASSES)
        persons = detected.get(PERSON_CLASS, 0)
        status = "VIOLATION" if violations > 0 else ("COMPLIANT" if (compliances > 0 or persons > 0) else "NO-DETECTION")

        stem = f"img_{i:02d}"
        orig_out = originals_dir / f"{stem}.jpg"
        pred_out = preds_dir / f"{stem}.jpg"
        cv2.imwrite(str(orig_out), frame)
        cv2.imwrite(str(pred_out), annotated)

        h, w = frame.shape[:2]
        manifest.append({
            "id": stem,
            "original": f"originals/{stem}.jpg",
            "prediction": f"predictions/{stem}.jpg",
            "width": w,
            "height": h,
            "status": status,
            "persons": persons,
            "violations": violations,
            "compliances": compliances,
            "detected": detected,
            "source_name": img_path.name,
        })
        print(f"  [{i:02d}] {status:12s} v={violations} c={compliances} p={persons} {img_path.name}")

    # Sort so violations come first (more impactful in the gallery)
    manifest.sort(key=lambda x: (x["status"] != "VIOLATION", -x["violations"]))

    manifest_path = out_root / "manifest.json"
    manifest_path.write_text(json.dumps({"items": manifest}, indent=2))
    print(f"\n[demo] wrote {len(manifest)} items to {out_root}")
    print(f"[demo] manifest: {manifest_path}")
    print(f"[demo] summary: "
          f"violations={sum(1 for m in manifest if m['status']=='VIOLATION')} "
          f"compliant={sum(1 for m in manifest if m['status']=='COMPLIANT')} "
          f"none={sum(1 for m in manifest if m['status']=='NO-DETECTION')}")


if __name__ == "__main__":
    main()
