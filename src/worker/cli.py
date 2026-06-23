"""Worker CLI entrypoint.

Examples::

    # Local dry-run (no API):
    python -m src.worker.cli --source outputs/videos/synth_helmet_30.mp4 \\
        --rules config/rules.json --dry-run

    # Against a running API:
    python -m src.worker.cli --source clip.mp4 --rules config/rules.json \\
        --api-url http://localhost:8000
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.inference import load_model  # noqa: E402
from src.rule_engine import Config  # noqa: E402
from src.worker.api_client import ApiClient  # noqa: E402
from src.worker.pipeline import run_video  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Video file path")
    parser.add_argument("--rules", type=Path, required=True, help="rules.json")
    parser.add_argument("--model", type=Path, default=None)
    parser.add_argument("--api-url", default=os.environ.get("CS_API_URL"),
                        help="API base URL (default: $CS_API_URL)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip API calls; log events to stdout")
    parser.add_argument("--source-label", default=None,
                        help="Override the 'source' field on events (default: filename)")
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--tracker", default="bytetrack.yaml")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    log = logging.getLogger("worker")

    rules = Config.from_path(args.rules)
    log.info("loaded %d rules from %s", len(rules.rules), args.rules)

    model = load_model(args.model)
    log.info("loaded model: %s", getattr(model, "ckpt_path", "<default>"))

    api_url = None if args.dry_run else args.api_url
    with ApiClient(api_url) as api:
        if api_url and not api.healthy():
            log.warning("API at %s is unhealthy; events will fail to post", api_url)

        stats = run_video(
            video_path=args.source.expanduser().resolve(),
            model=model,
            rules_config=rules,
            api=api,
            source_label=args.source_label,
            conf=args.conf,
            iou=args.iou,
            tracker=args.tracker,
            batch_size=args.batch_size,
        )

    log.info(
        "done. frames=%d  unique_ids=%d  emitted=%d  posted=%d  batches=%d  seconds=%.1f",
        stats.frames, stats.unique_ids, stats.events_emitted,
        stats.events_posted, stats.posted_batches, stats.seconds,
    )


if __name__ == "__main__":
    main()
