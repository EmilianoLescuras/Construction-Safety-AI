"""Dispatch alerts for a batch of ViolationEvents.

Reads an events JSONL (produced by ``scripts/run_rules.py``) and a source
video. For each event, seeks to the event's frame, renders evidence images,
and fans the event out through all enabled sinks (console / telegram /
email — configured in ``config/alerts.json`` + .env).

A per-dispatch audit log is written to
``outputs/logs/<stem>_alerts_audit.jsonl``.

Usage:
    python scripts/run_alerts.py --events outputs/logs/<stem>_events.jsonl \\
                                 --video /path/to/source.mp4
    python scripts/run_alerts.py --events <file> --no-video         # skip evidence
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import cv2
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.alerts.base import AlertContext
from src.alerts.dispatcher import AlertDispatcher, load_alerts_config
from src.alerts.evidence import save_evidence
from src.tracking import JsonlWriter, iter_jsonl


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True, help="Input events JSONL")
    parser.add_argument("--video", type=Path, default=None,
                        help="Source video for evidence cropping (optional)")
    parser.add_argument("--config", type=Path,
                        default=PROJECT_ROOT / "config" / "alerts.json")
    parser.add_argument("--audit-out", type=Path, default=None,
                        help="Output audit JSONL (default: derived from events name)")
    parser.add_argument("--no-video", action="store_true", help="Skip evidence even if --video set")
    parser.add_argument("--source", type=str, default=None,
                        help="Source tag stored on DB rows (default: events filename)")
    args = parser.parse_args()

    events_path = args.events.expanduser().resolve()
    if not events_path.is_file():
        raise SystemExit(f"Events file not found: {events_path}")
    cfg, evidence_cfg = load_alerts_config(args.config)
    source_tag = args.source or events_path.name

    audit_path = args.audit_out or (PROJECT_ROOT / "outputs" / "logs"
                                    / f"{events_path.stem.removesuffix('_events')}_alerts_audit.jsonl")
    audit_path.parent.mkdir(parents=True, exist_ok=True)

    cap = None
    if args.video and not args.no_video:
        vpath = args.video.expanduser().resolve()
        if not vpath.is_file():
            raise SystemExit(f"Video not found: {vpath}")
        cap = cv2.VideoCapture(str(vpath))
        if not cap.isOpened():
            raise SystemExit(f"Could not open video: {vpath}")

    dispatcher = AlertDispatcher.from_config(cfg)
    print(f"[alerts] events={events_path}")
    print(f"[alerts] active sinks: {[s.name for s in dispatcher.sinks] or '(none)'}")
    print(f"[alerts] audit -> {audit_path}")
    if cap is not None:
        print(f"[alerts] evidence -> {evidence_cfg.out_dir}/<rule>/")

    n_events = 0
    n_success = 0
    n_failed = 0
    try:
        with JsonlWriter(audit_path) as audit:
            for event in iter_jsonl(events_path):
                n_events += 1
                frame = None
                if cap is not None:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, int(event["frame"]))
                    ok, frame = cap.read()
                    if not ok:
                        frame = None

                full_path = crop_path = None
                if frame is not None and evidence_cfg.enabled:
                    full_path, crop_path = save_evidence(frame, event, evidence_cfg, PROJECT_ROOT)

                ctx = AlertContext(event=event, full_frame_path=full_path,
                                   crop_path=crop_path, source=source_tag)
                results = dispatcher.dispatch(ctx)
                for r in results:
                    if r.success:
                        n_success += 1
                    else:
                        n_failed += 1
                        print(f"  [warn] sink={r.sink} failed: {r.error}")
                audit.write({
                    "ts": time.time(),
                    "event": {k: event[k] for k in ("rule", "person_id", "frame", "emitted_ts")},
                    "evidence": {
                        "full": str(full_path) if full_path else None,
                        "crop": str(crop_path) if crop_path else None,
                    },
                    "dispatch": [r.__dict__ for r in results],
                })
    finally:
        if cap is not None:
            cap.release()
        dispatcher.close()

    print(f"[alerts] Done. events={n_events} dispatches ok={n_success} failed={n_failed}")


if __name__ == "__main__":
    main()
