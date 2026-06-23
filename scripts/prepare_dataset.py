"""Prepare the Construction Safety v1 dataset for training.

Creates symlinks from the project's ``datasets/{train,valid,test}/`` to the
external source directory and writes ``config/data.yaml`` with absolute paths
that Ultralytics YOLO can consume directly.

Idempotent: re-running removes the existing symlinks and recreates them.

Usage:
    python scripts/prepare_dataset.py
    python scripts/prepare_dataset.py --source "/path/to/dataset"
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = Path.home() / "Downloads" / "Construction safety.v1i.yolov8"
SPLITS = ("train", "valid", "test")

CLASSES = [
    "Excavator",
    "Gloves",
    "Hardhat",
    "Ladder",
    "Mask",
    "NO-Hardhat",
    "NO-Mask",
    "NO-Safety Vest",
    "Person",
    "Safety Cone",
    "Safety Vest",
    "dump truck",
    "machinery",
    "sedan",
    "trailer",
    "truck",
    "van",
    "vehicle",
    "wheel loader",
]


def link_split(source_split: Path, target_split: Path) -> tuple[int, int]:
    """Symlink ``images/`` and ``labels/`` from source to target. Returns (n_images, n_labels)."""
    if not source_split.is_dir():
        raise FileNotFoundError(f"Source split not found: {source_split}")

    target_split.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for sub in ("images", "labels"):
        src = source_split / sub
        if not src.is_dir():
            raise FileNotFoundError(f"Missing subdirectory: {src}")
        dst = target_split / sub
        if dst.is_symlink() or dst.exists():
            dst.unlink()
        dst.symlink_to(src.resolve(), target_is_directory=True)
        counts[sub] = sum(1 for _ in src.iterdir())
    return counts["images"], counts["labels"]


def write_data_yaml(config_path: Path) -> None:
    data = {
        "path": str(PROJECT_ROOT / "datasets"),
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "nc": len(CLASSES),
        "names": CLASSES,
    }
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Source dataset directory (default: {DEFAULT_SOURCE})",
    )
    args = parser.parse_args()

    source: Path = args.source.expanduser().resolve()
    if not source.is_dir():
        raise SystemExit(f"Source dataset directory not found: {source}")

    print(f"Source: {source}")
    print(f"Target: {PROJECT_ROOT / 'datasets'}")

    for split in SPLITS:
        n_images, n_labels = link_split(source / split, PROJECT_ROOT / "datasets" / split)
        print(f"  [{split:5s}] images={n_images:4d} labels={n_labels:4d}")
        assert n_images == n_labels, f"Image/label mismatch in {split}"

    config_path = PROJECT_ROOT / "config" / "data.yaml"
    write_data_yaml(config_path)
    print(f"Wrote: {config_path}")
    print(f"Classes ({len(CLASSES)}): {CLASSES}")


if __name__ == "__main__":
    main()
