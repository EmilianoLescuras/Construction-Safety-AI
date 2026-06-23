"""Run the PPE rule engine over a tracking JSONL log and emit ViolationEvents.

Usage:
    python scripts/run_rules.py --tracks outputs/logs/<stem>_track.jsonl
    python scripts/run_rules.py --tracks <file> --rules config/rules.json --out <file>

Default outputs go to ``outputs/logs/<stem>_events.jsonl``.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.rule_engine import Config, RuleEngine
from src.tracking import JsonlWriter, iter_jsonl

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracks", type=Path, required=True, help="Input JSONL of tracked detections")
    parser.add_argument(
        "--rules", type=Path,
        default=PROJECT_ROOT / "config" / "rules.json",
        help="Rule configuration JSON",
    )
    parser.add_argument(
        "--out", type=Path, default=None,
        help="Output JSONL of ViolationEvents (default: outputs/logs/<stem>_events.jsonl)",
    )
    args = parser.parse_args()

    tracks_path = args.tracks.expanduser().resolve()
    if not tracks_path.is_file():
        raise SystemExit(f"Tracks file not found: {tracks_path}")

    cfg = Config.from_path(args.rules)
    out_path = args.out or (PROJECT_ROOT / "outputs" / "logs" / f"{tracks_path.stem.removesuffix('_track')}_events.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    engine = RuleEngine(config=cfg)
    counts: Counter = Counter()
    total_frames = 0

    print(f"[rules] tracks={tracks_path}")
    print(f"[rules] rules={args.rules}")
    print(f"[rules] enabled rules: {[r.name for r in cfg.rules if r.enabled]}")
    print(f"[rules] out={out_path}")

    with JsonlWriter(out_path) as writer:
        for rec in iter_jsonl(tracks_path):
            total_frames += 1
            for ev in engine.process_frame(rec):
                writer.write(ev)
                counts[ev["rule"]] += 1
                print(f"  [event] frame={ev['frame']:4d} ts={ev['emitted_ts']:.2f}s  "
                      f"person_id={ev['person_id']:3d}  rule={ev['rule']:8s}  "
                      f"dur={ev['duration_seconds']:.2f}s  ({ev['violation_class']} {ev['violation_conf']:.2f})")

    print(f"[rules] Done. Processed {total_frames} frames. Emitted {sum(counts.values())} events: "
          f"{dict(counts) or '{}'}")


if __name__ == "__main__":
    main()
