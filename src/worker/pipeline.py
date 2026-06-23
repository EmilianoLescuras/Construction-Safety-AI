"""End-to-end inference pipeline orchestrator.

Runs detect → track → rules on a single video source and forwards the emitted
violation events to the API in batches.

This module intentionally has no Click/argparse — it's the library that the
CLI (``cli.py``) drives.
"""
from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from src.rule_engine import Config, RuleEngine
from src.tracking import track_frame, tracks_to_record
from src.worker.api_client import ApiClient

log = logging.getLogger(__name__)


@dataclass
class WorkerStats:
    frames: int = 0
    unique_ids: int = 0
    events_emitted: int = 0
    events_posted: int = 0
    seconds: float = 0.0
    posted_batches: int = 0
    batch_results: list[dict] = field(default_factory=list)


def run_video(
    video_path: Path,
    model,
    rules_config: Config,
    api: ApiClient,
    source_label: str | None = None,
    conf: float = 0.25,
    iou: float = 0.45,
    tracker: str = "bytetrack.yaml",
    batch_size: int = 25,
    progress_every: int = 50,
) -> WorkerStats:
    """Process a video end-to-end, posting events to the API in batches."""
    import cv2

    if not video_path.is_file():
        raise FileNotFoundError(f"video not found: {video_path}")

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"could not open video: {video_path}")

    engine = RuleEngine(rules_config)
    stats = WorkerStats()
    seen: set[int] = set()
    pending: list[dict] = []
    source = source_label or video_path.name
    t0 = time.time()

    try:
        i = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            results = track_frame(model, frame, conf, iou, tracker, persist=True)
            res = results[0]
            video_ts = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            rec = tracks_to_record(i, video_ts, res, model.names)
            for t in rec["tracks"]:
                if t["id"] >= 0:
                    seen.add(t["id"])

            for ev in engine.process_frame(rec):
                pending.append(_to_event_in(ev))
                stats.events_emitted += 1

            if len(pending) >= batch_size:
                result = api.post_events(pending, source=source)
                stats.batch_results.append(result)
                stats.events_posted += result.get("inserted", 0)
                stats.posted_batches += 1
                pending.clear()

            i += 1
            if i % progress_every == 0:
                elapsed = time.time() - t0
                log.info(
                    "frame %d  fps=%.1f  ids=%d  events=%d",
                    i, i / max(elapsed, 0.001), len(seen), stats.events_emitted,
                )
    finally:
        cap.release()
        if pending:
            result = api.post_events(pending, source=source)
            stats.batch_results.append(result)
            stats.events_posted += result.get("inserted", 0)
            stats.posted_batches += 1

    stats.frames = i
    stats.unique_ids = len(seen)
    stats.seconds = time.time() - t0
    return stats


def _to_event_in(ev: dict) -> dict:
    """Strip rule-engine fields to the API's ViolationEventIn schema."""
    return {
        "rule": ev["rule"],
        "person_id": ev["person_id"],
        "frame": ev["frame"],
        "first_seen_ts": ev["first_seen_ts"],
        "emitted_ts": ev["emitted_ts"],
        "duration_seconds": ev["duration_seconds"],
        "violation_class": ev["violation_class"],
        "violation_conf": ev["violation_conf"],
        "person_bbox": ev["person_bbox"],
        "violation_bbox": ev["violation_bbox"],
    }


def iter_records_only(video_path: Path, model, conf=0.25, iou=0.45,
                      tracker="bytetrack.yaml") -> Iterator[dict]:
    """Helper for tests/debug: yield per-frame tracking records without rules."""
    import cv2

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"could not open video: {video_path}")
    i = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            res = track_frame(model, frame, conf, iou, tracker, persist=True)[0]
            ts = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            yield tracks_to_record(i, ts, res, model.names)
            i += 1
    finally:
        cap.release()
