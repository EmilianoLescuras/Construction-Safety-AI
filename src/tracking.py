"""Multi-object tracking utilities (ByteTrack via Ultralytics).

Wraps ``YOLO.track(persist=True)`` so each call updates the same tracker state.
Provides annotation that mirrors ``src/inference.py`` color coding but also
includes the persistent track ID returned by ByteTrack.

Outputs a JSONL record per frame for downstream consumption (Phase 7 rule
engine), with one entry per tracked detection:

    {"frame": 0, "ts": 1719000000.123, "tracks": [
        {"id": 7, "class": "Person", "conf": 0.91, "bbox": [x1, y1, x2, y2]},
        ...
    ]}
"""
from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from src.colors import CATEGORY_COLORS


def track_frame(
    model,
    frame,
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.45,
    tracker: str = "bytetrack.yaml",
    persist: bool = True,
):
    """Run tracking on a single frame. State is kept across calls when persist=True."""
    return model.track(
        source=frame,
        conf=conf_threshold,
        iou=iou_threshold,
        tracker=tracker,
        persist=persist,
        verbose=False,
    )


def annotate_tracked_frame(
    frame,
    result,
    class_names: list[str],
    conf_threshold: float = 0.0,
):
    """Draw color-coded bboxes + 'ID:<n> Class 0.XX' labels."""
    import cv2
    import numpy as np

    out = frame.copy()
    boxes = getattr(result, "boxes", None)
    if boxes is None or len(boxes) == 0:
        return out

    xyxy = boxes.xyxy.cpu().numpy()
    confs = boxes.conf.cpu().numpy()
    clss = boxes.cls.cpu().numpy().astype(int)
    ids = (
        boxes.id.cpu().numpy().astype(int)
        if boxes.id is not None
        else np.full(len(xyxy), -1, dtype=int)
    )

    for (x1, y1, x2, y2), conf, cid, tid in zip(xyxy, confs, clss, ids, strict=False):
        if conf < conf_threshold:
            continue
        name = class_names[cid]
        color = CATEGORY_COLORS.get(name, (200, 200, 200))
        p1 = (int(x1), int(y1))
        p2 = (int(x2), int(y2))
        cv2.rectangle(out, p1, p2, color, 2)

        tid_str = f"ID:{tid} " if tid >= 0 else ""
        label = f"{tid_str}{name} {conf:.2f}"
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


def tracks_to_record(frame_id: int, ts: float, result, class_names: list[str]) -> dict:
    """Serializable per-frame snapshot of all tracked objects."""
    import numpy as np

    record: dict = {"frame": frame_id, "ts": ts, "tracks": []}
    boxes = getattr(result, "boxes", None)
    if boxes is None or len(boxes) == 0:
        return record

    xyxy = boxes.xyxy.cpu().numpy()
    confs = boxes.conf.cpu().numpy()
    clss = boxes.cls.cpu().numpy().astype(int)
    ids = (
        boxes.id.cpu().numpy().astype(int)
        if boxes.id is not None
        else np.full(len(xyxy), -1, dtype=int)
    )

    for (x1, y1, x2, y2), conf, cid, tid in zip(xyxy, confs, clss, ids, strict=False):
        record["tracks"].append({
            "id": int(tid),
            "class": class_names[cid],
            "class_id": int(cid),
            "conf": float(conf),
            "bbox": [float(x1), float(y1), float(x2), float(y2)],
        })
    return record


class JsonlWriter:
    """Append-only JSONL writer (one JSON object per line)."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("w", encoding="utf-8")

    def write(self, record: dict) -> None:
        self._fh.write(json.dumps(record) + "\n")

    def close(self) -> None:
        if not self._fh.closed:
            self._fh.close()

    def __enter__(self) -> JsonlWriter:
        return self

    def __exit__(self, *_exc) -> None:
        self.close()


def iter_jsonl(path: Path) -> Iterable[dict]:
    """Helper for downstream code (rule engine, dashboard) to read the log."""
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)
