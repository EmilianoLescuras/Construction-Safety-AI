"""Train a YOLOv8 model on the Construction Safety v1 dataset.

Auto-detects device (mps on Apple Silicon, cuda:0 on CUDA, else cpu).
Writes Ultralytics run artifacts to ``runs/detect/<run_name>/`` (gitignored)
and copies the best checkpoint to ``models/<run_name>.pt`` (also gitignored).
A trimmed metrics summary is written to ``docs/experiments/<run_name>.md``
so the result is visible in git history without committing weights.

Usage:
    python scripts/train.py                            # defaults (yolov8n, 10 epochs)
    python scripts/train.py --model yolov8s.pt --epochs 80
    python scripts/train.py --run-name baseline_smoke --epochs 3
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_YAML = PROJECT_ROOT / "config" / "data.yaml"
MODELS_DIR = PROJECT_ROOT / "models"
RUNS_DIR = PROJECT_ROOT / "runs"
DOCS_DIR = PROJECT_ROOT / "docs" / "experiments"


def pick_device() -> str:
    import torch

    if torch.cuda.is_available():
        return "cuda:0"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def write_summary(run_name: str, args: argparse.Namespace, device: str, metrics: dict, run_dir: Path) -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out = DOCS_DIR / f"{run_name}.md"
    lines = [
        f"# Experiment: {run_name}",
        "",
        f"- Date: {datetime.now().isoformat(timespec='seconds')}",
        f"- Base model: `{args.model}`",
        f"- Epochs: {args.epochs}",
        f"- Image size: {args.imgsz}",
        f"- Batch: {args.batch}",
        f"- Device: `{device}`",
        f"- Data: `{DATA_YAML.relative_to(PROJECT_ROOT)}`",
        f"- Ultralytics run dir: `{run_dir.relative_to(PROJECT_ROOT)}` (gitignored)",
        "",
        "## Validation metrics",
        "",
        "```json",
        json.dumps(metrics, indent=2, default=str),
        "```",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="yolov8n.pt", help="Base weights (yolov8n.pt / yolov8s.pt / yolov8m.pt)")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--run-name", default=None, help="Run name (default: derived from model + epochs)")
    parser.add_argument("--device", default=None, help="Override device autodetect (mps / cuda:0 / cpu)")
    parser.add_argument("--patience", type=int, default=30, help="EarlyStopping patience (Ultralytics)")
    parser.add_argument(
        "--cache",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Cache images in RAM (--cache / --no-cache). Big speedup for small datasets.",
    )
    args = parser.parse_args()

    if not DATA_YAML.exists():
        raise SystemExit(f"Missing {DATA_YAML}. Run scripts/prepare_dataset.py first.")

    from ultralytics import YOLO

    device = args.device or pick_device()
    run_name = args.run_name or f"{Path(args.model).stem}_e{args.epochs}_b{args.batch}_baseline"

    print(f"[train] model={args.model} epochs={args.epochs} imgsz={args.imgsz} batch={args.batch} device={device}")
    print(f"[train] run_name={run_name}")
    print(f"[train] data={DATA_YAML}")

    model = YOLO(args.model)
    results = model.train(
        data=str(DATA_YAML),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        project=str(RUNS_DIR / "detect"),
        name=run_name,
        exist_ok=True,
        patience=args.patience,
        cache=args.cache,
        verbose=True,
    )

    run_dir = Path(results.save_dir)
    best_pt = run_dir / "weights" / "best.pt"

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    dest = MODELS_DIR / f"{run_name}.pt"
    if best_pt.exists():
        shutil.copy2(best_pt, dest)
        print(f"[train] Copied best weights → {dest.relative_to(PROJECT_ROOT)}")
    else:
        print(f"[train] WARNING: best.pt not found at {best_pt}")

    metrics_box = getattr(results, "box", None)
    metrics = {}
    if metrics_box is not None:
        metrics = {
            "precision": float(metrics_box.mp),
            "recall": float(metrics_box.mr),
            "mAP50": float(metrics_box.map50),
            "mAP50-95": float(metrics_box.map),
        }
        try:
            per_class = {}
            for cid, ap50 in zip(metrics_box.ap_class_index.tolist(), metrics_box.ap50.tolist()):
                per_class[int(cid)] = float(ap50)
            metrics["per_class_AP50"] = per_class
        except Exception:
            pass

    summary = write_summary(run_name, args, device, metrics, run_dir)
    print(f"[train] Summary → {summary.relative_to(PROJECT_ROOT)}")
    print("[train] Done.")


if __name__ == "__main__":
    main()
