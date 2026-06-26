"""Convert YOLO pseudo-labels into a Label Studio import bundle.

Reads ``datasets/v2_inbox/{images,labels,classes.txt}`` and writes:

- ``datasets/v2_inbox/labelstudio_tasks.json`` — the import file. Each
  task points at one image and ships v1's pseudo-labels as
  ``predictions`` so the boxes are pre-drawn — your job is just to
  correct them.
- ``datasets/v2_inbox/labelstudio_config.xml`` — the labeling interface
  XML to paste into Label Studio's "Labeling setup".

Image URLs use Label Studio's local-files endpoint:
``/data/local-files/?d=<relative>``. Start the server with
``scripts/start_labelstudio.sh`` so the right env vars are set.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INBOX = PROJECT_ROOT / "datasets" / "v2_inbox"
IMG_DIR = INBOX / "images"
LBL_DIR = INBOX / "labels"
CLASSES_FILE = INBOX / "classes.txt"

PALETTE = [
    "#F94144", "#F3722C", "#F8961E", "#F9C74F", "#90BE6D",
    "#43AA8B", "#577590", "#277DA1", "#9D4EDD", "#FF6B6B",
    "#06D6A0", "#118AB2", "#073B4C", "#EF476F", "#FFD166",
    "#8338EC", "#3A86FF", "#FB5607", "#FFBE0B",
]


def build_labeling_config(classes: list[str]) -> str:
    labels = "\n    ".join(
        f'<Label value="{c}" background="{PALETTE[i % len(PALETTE)]}"/>'
        for i, c in enumerate(classes)
    )
    return (
        "<View>\n"
        '  <Image name="image" value="$image"/>\n'
        '  <RectangleLabels name="label" toName="image">\n'
        f"    {labels}\n"
        "  </RectangleLabels>\n"
        "</View>\n"
    )


def yolo_line_to_ls_result(line: str, classes: list[str]) -> dict | None:
    parts = line.strip().split()
    if len(parts) != 5:
        return None
    cid, cx, cy, w, h = parts
    cid = int(cid)
    if cid < 0 or cid >= len(classes):
        return None
    cx, cy, w, h = float(cx), float(cy), float(w), float(h)
    x_pct = (cx - w / 2) * 100
    y_pct = (cy - h / 2) * 100
    return {
        "from_name": "label",
        "to_name": "image",
        "type": "rectanglelabels",
        "value": {
            "x": x_pct,
            "y": y_pct,
            "width": w * 100,
            "height": h * 100,
            "rectanglelabels": [classes[cid]],
        },
    }


def main() -> None:
    if not CLASSES_FILE.exists():
        raise SystemExit(f"Missing {CLASSES_FILE}")
    classes = CLASSES_FILE.read_text().strip().splitlines()

    tasks: list[dict] = []
    skipped: list[str] = []

    for img_path in sorted(IMG_DIR.glob("*.jpg")):
        lbl_path = LBL_DIR / f"{img_path.stem}.txt"
        try:
            with Image.open(img_path) as im:
                w, h = im.size
        except Exception as e:
            skipped.append(f"{img_path.name}: {e}")
            continue

        results: list[dict] = []
        if lbl_path.exists():
            for line in lbl_path.read_text().splitlines():
                if not line.strip():
                    continue
                r = yolo_line_to_ls_result(line, classes)
                if r is None:
                    continue
                r["original_width"] = w
                r["original_height"] = h
                results.append(r)

        rel = img_path.relative_to(PROJECT_ROOT).as_posix()
        tasks.append({
            "data": {"image": f"/data/local-files/?d={rel}"},
            "predictions": [{
                "model_version": "yolov8n_v1_pseudo",
                "score": 0.5,
                "result": results,
            }],
        })

    tasks_out = INBOX / "labelstudio_tasks.json"
    tasks_out.write_text(json.dumps(tasks, indent=2))

    config_out = INBOX / "labelstudio_config.xml"
    config_out.write_text(build_labeling_config(classes))

    total_boxes = sum(len(t["predictions"][0]["result"]) for t in tasks)
    print(f"[ls-import] wrote {len(tasks)} tasks ({total_boxes} predicted boxes)")
    print(f"[ls-import]   → {tasks_out.relative_to(PROJECT_ROOT)}")
    print(f"[ls-import]   → {config_out.relative_to(PROJECT_ROOT)}")
    if skipped:
        print(f"[ls-import] skipped {len(skipped)} files:")
        for s in skipped[:5]:
            print(f"  - {s}")


if __name__ == "__main__":
    main()
