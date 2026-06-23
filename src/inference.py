"""Shared inference utilities for the Construction Safety AI project.

Loads a YOLO model, runs prediction on a frame, and draws annotations with
a category-based color scheme:

- RED      : violations (NO-Hardhat, NO-Mask, NO-Safety Vest)
- GREEN    : compliance (Hardhat, Mask, Safety Vest, Gloves)
- YELLOW   : Person
- CYAN     : safety infrastructure (Safety Cone, Ladder)
- BLUE     : vehicles / machinery (Excavator, dump truck, sedan, ...)

Colors are in OpenCV BGR order.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = PROJECT_ROOT / "models" / "yolov8n_construction_safety_e40_cache.pt"

# BGR
RED = (0, 0, 255)
GREEN = (0, 200, 0)
YELLOW = (0, 220, 220)
CYAN = (220, 220, 0)
BLUE = (220, 100, 0)

CATEGORY_COLORS: dict[str, tuple[int, int, int]] = {
    "NO-Hardhat": RED,
    "NO-Mask": RED,
    "NO-Safety Vest": RED,
    "Hardhat": GREEN,
    "Mask": GREEN,
    "Safety Vest": GREEN,
    "Gloves": GREEN,
    "Person": YELLOW,
    "Safety Cone": CYAN,
    "Ladder": CYAN,
    "Excavator": BLUE,
    "machinery": BLUE,
    "dump truck": BLUE,
    "sedan": BLUE,
    "van": BLUE,
    "truck": BLUE,
    "trailer": BLUE,
    "vehicle": BLUE,
    "wheel loader": BLUE,
}


def load_model(model_path: Path | str | None = None):
    """Load a YOLO model. Defaults to the best baseline trained in Phase 4."""
    from ultralytics import YOLO

    path = Path(model_path) if model_path else DEFAULT_MODEL
    if not path.exists():
        raise FileNotFoundError(
            f"Model not found: {path}. Train one first via scripts/train.py."
        )
    return YOLO(str(path))


def annotate_frame(
    frame: np.ndarray,
    boxes: Iterable,
    class_names: list[str],
    conf_threshold: float = 0.0,
) -> np.ndarray:
    """Draw bounding boxes + labels on ``frame``. Returns a new annotated array.

    ``boxes`` is an Ultralytics ``Boxes`` object (results[0].boxes). We iterate
    via the underlying tensors so this also works on CPU/MPS/CUDA.
    """
    out = frame.copy()
    if boxes is None or len(boxes) == 0:
        return out

    xyxy = boxes.xyxy.cpu().numpy()
    confs = boxes.conf.cpu().numpy()
    clss = boxes.cls.cpu().numpy().astype(int)

    for (x1, y1, x2, y2), conf, cid in zip(xyxy, confs, clss):
        if conf < conf_threshold:
            continue
        name = class_names[cid]
        color = CATEGORY_COLORS.get(name, (200, 200, 200))
        p1 = (int(x1), int(y1))
        p2 = (int(x2), int(y2))
        cv2.rectangle(out, p1, p2, color, 2)

        label = f"{name} {conf:.2f}"
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        ty1 = max(0, p1[1] - th - baseline - 4)
        cv2.rectangle(out, (p1[0], ty1), (p1[0] + tw + 4, ty1 + th + baseline + 4), color, -1)
        cv2.putText(
            out,
            label,
            (p1[0] + 2, ty1 + th + 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
    return out


def predict_and_annotate(
    model,
    frame: np.ndarray,
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.45,
) -> tuple[np.ndarray, list]:
    """Run prediction on a single BGR frame and return (annotated_frame, results)."""
    results = model.predict(
        source=frame,
        conf=conf_threshold,
        iou=iou_threshold,
        verbose=False,
    )
    res = results[0]
    annotated = annotate_frame(frame, res.boxes, model.names, conf_threshold=conf_threshold)
    return annotated, results
