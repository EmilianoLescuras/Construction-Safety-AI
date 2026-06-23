"""Load Phase 7 events JSONL (and optional Phase 8 audit JSONL) into the DB.

Idempotent: events deduped by (rule, person_id, frame, source). Re-running
the same files updates dispatches/evidence under the existing event rows.

Usage:
    python scripts/load_events_to_db.py --events outputs/logs/<stem>_events.jsonl
    python scripts/load_events_to_db.py --events <events.jsonl> \\
                                        --audit outputs/logs/<stem>_alerts_audit.jsonl
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend import crud, models, schemas  # noqa: E402
from src.backend.db import SessionLocal  # noqa: E402
from src.tracking import iter_jsonl  # noqa: E402


def _load_events(db, events_path: Path, source: str) -> dict[tuple, int]:
    """Insert events, return {(rule, person_id, frame): event_id}."""
    raw = list(iter_jsonl(events_path))
    payload = [
        schemas.ViolationEventIn(
            rule=ev["rule"],
            person_id=ev["person_id"],
            frame=ev["frame"],
            first_seen_ts=ev["first_seen_ts"],
            emitted_ts=ev["emitted_ts"],
            duration_seconds=ev["duration_seconds"],
            violation_class=ev["violation_class"],
            violation_conf=ev["violation_conf"],
            person_bbox=ev["person_bbox"],
            violation_bbox=ev["violation_bbox"],
        )
        for ev in raw
    ]
    inserted, skipped, inserted_models = crud.insert_events(db, payload, source)
    print(f"[loader] events: inserted={inserted} skipped(dup)={skipped}")

    index: dict[tuple, int] = {}
    for m in inserted_models:
        index[(m.rule, m.person_id, m.frame)] = m.id
    if skipped:
        for ev in raw:
            key = (ev["rule"], ev["person_id"], ev["frame"])
            if key in index:
                continue
            existing = db.query(models.ViolationEvent).filter_by(
                rule=ev["rule"], person_id=ev["person_id"], frame=ev["frame"], source=source
            ).first()
            if existing:
                index[key] = existing.id
    return index


def _load_audit(db, audit_path: Path, event_index: dict[tuple, int]) -> None:
    n_evidence = n_dispatch = orphans = 0
    for row in iter_jsonl(audit_path):
        ev = row["event"]
        key = (ev["rule"], ev["person_id"], ev["frame"])
        event_id = event_index.get(key)
        if event_id is None:
            orphans += 1
            continue

        ev_files = row.get("evidence", {}) or {}
        for kind in ("full", "crop"):
            path = ev_files.get(kind)
            if not path:
                continue
            already = db.query(models.EvidenceFile).filter_by(
                event_id=event_id, kind=kind, path=path
            ).first()
            if already:
                continue
            db.add(models.EvidenceFile(event_id=event_id, kind=kind, path=path))
            n_evidence += 1

        for d in row.get("dispatch", []) or []:
            already = db.query(models.AlertDispatch).filter_by(
                event_id=event_id, sink=d["sink"], dispatched_at=row["ts"]
            ).first()
            if already:
                continue
            db.add(models.AlertDispatch(
                event_id=event_id,
                sink=d["sink"],
                success=bool(d.get("success")),
                error=d.get("error", "") or "",
                dispatched_at=float(row["ts"]),
            ))
            n_dispatch += 1
    db.commit()
    print(f"[loader] audit: evidence+={n_evidence} dispatch+={n_dispatch} orphans={orphans}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--audit", type=Path, default=None,
                        help="optional alerts audit JSONL")
    parser.add_argument("--source", type=str, default=None,
                        help="source tag (default: events filename)")
    args = parser.parse_args()

    events_path = args.events.expanduser().resolve()
    if not events_path.is_file():
        raise SystemExit(f"events file not found: {events_path}")
    source = args.source or events_path.name

    with SessionLocal() as db:
        index = _load_events(db, events_path, source)
        if args.audit:
            audit_path = args.audit.expanduser().resolve()
            if not audit_path.is_file():
                raise SystemExit(f"audit file not found: {audit_path}")
            _load_audit(db, audit_path, index)

    print("[loader] done.")


if __name__ == "__main__":
    main()
