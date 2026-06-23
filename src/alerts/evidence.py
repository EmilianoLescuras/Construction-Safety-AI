"""Render and save evidence images for a violation event.

Two artifacts may be produced per event:

- ``<stem>_full.jpg``  — the full frame (optionally with bbox + label overlay).
- ``<stem>_crop.jpg``  — a padded crop around the Person + violation bbox union.

Both are written under ``outputs/images/evidence/<rule>/`` by default; sinks
receive their absolute paths via :class:`AlertContext` and can attach or
upload them.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.inference import CATEGORY_COLORS


@dataclass
class EvidenceConfig:
    enabled: bool = True
    out_dir: Path = Path("outputs/images/evidence")
    save_full_frame: bool = True
    save_crop: bool = True
    crop_padding: float = 0.1
    annotate_full_frame: bool = True


def _annotate(frame: np.ndarray, event: dict) -> np.ndarray:
    out = frame.copy()
    pbb = event.get("person_bbox")
    vbb = event.get("violation_bbox")
    person_color = CATEGORY_COLORS.get("Person", (0, 220, 220))
    violation_color = CATEGORY_COLORS.get(event["violation_class"], (0, 0, 255))

    if pbb:
        p1 = (int(pbb[0]), int(pbb[1]))
        p2 = (int(pbb[2]), int(pbb[3]))
        cv2.rectangle(out, p1, p2, person_color, 2)
        plabel = f"ID:{event['person_id']}"
        cv2.putText(out, plabel, (p1[0], max(0, p1[1] - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, person_color, 2, cv2.LINE_AA)
    if vbb:
        p1 = (int(vbb[0]), int(vbb[1]))
        p2 = (int(vbb[2]), int(vbb[3]))
        cv2.rectangle(out, p1, p2, violation_color, 2)
        vlabel = f"{event['violation_class']} {event['violation_conf']:.2f}"
        cv2.putText(out, vlabel, (p1[0], min(out.shape[0] - 4, p2[1] + 18)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, violation_color, 2, cv2.LINE_AA)
    return out


def _crop_with_padding(frame: np.ndarray, boxes: list[list[float]], pad: float) -> np.ndarray:
    h, w = frame.shape[:2]
    xs = [b[0] for b in boxes] + [b[2] for b in boxes]
    ys = [b[1] for b in boxes] + [b[3] for b in boxes]
    x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
    pw = (x2 - x1) * pad
    ph = (y2 - y1) * pad
    x1 = max(0, int(x1 - pw))
    y1 = max(0, int(y1 - ph))
    x2 = min(w, int(x2 + pw))
    y2 = min(h, int(y2 + ph))
    return frame[y1:y2, x1:x2]


def save_evidence(
    frame: np.ndarray,
    event: dict,
    config: EvidenceConfig,
    project_root: Path,
) -> tuple[Path | None, Path | None]:
    """Write evidence images for one event. Returns (full_path, crop_path)."""
    if not config.enabled or frame is None:
        return (None, None)

    out_dir = config.out_dir
    if not out_dir.is_absolute():
        out_dir = (project_root / out_dir).resolve()
    out_dir = out_dir / event["rule"]
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = f"event_{event['rule']}_p{event['person_id']}_f{event['frame']:06d}"

    full_path: Path | None = None
    crop_path: Path | None = None

    if config.save_full_frame:
        img = _annotate(frame, event) if config.annotate_full_frame else frame
        full_path = out_dir / f"{stem}_full.jpg"
        cv2.imwrite(str(full_path), img)

    if config.save_crop:
        boxes = [b for b in (event.get("person_bbox"), event.get("violation_bbox")) if b]
        if boxes:
            crop = _crop_with_padding(frame, boxes, config.crop_padding)
            if crop.size > 0:
                crop_path = out_dir / f"{stem}_crop.jpg"
                cv2.imwrite(str(crop_path), crop)

    return (full_path, crop_path)
