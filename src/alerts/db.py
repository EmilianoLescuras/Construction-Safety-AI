"""DbSink — persist ViolationEvents + EvidenceFiles + AlertDispatches.

This sink is treated specially by ``AlertDispatcher``: marked with
``is_audit_sink = True``, it runs first so the other sinks can record their
own ``AlertDispatch`` rows under the event's primary key.

Configured via ``alerts.json``:
    "db": {"enabled": true, "database_url": "sqlite:///outputs/...db"}

``database_url`` is optional — falls back to ``backend.config.settings``.
"""
from __future__ import annotations

import time

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from src.alerts.base import AlertContext, AlertSink
from src.backend import models
from src.backend.config import settings
from src.backend.db import _engine_kwargs


class DbSink(AlertSink):
    name = "db"
    is_audit_sink = True

    def __init__(self, config: dict | None = None) -> None:
        config = config or {}
        url = str(config.get("database_url") or settings.database_url)
        self._engine = create_engine(url, **_engine_kwargs(url))
        self._Session = sessionmaker(bind=self._engine, autoflush=False,
                                     autocommit=False, expire_on_commit=False)
        # Per-ctx cache so record_audit() can resolve event_id without re-querying.
        self._event_ids: dict[int, int] = {}

    def _event_key(self, ctx: AlertContext) -> tuple[str, int, int, str | None]:
        ev = ctx.event
        return (ev["rule"], int(ev["person_id"]), int(ev["frame"]), ctx.source)

    def _get_or_create_event(self, db: Session, ctx: AlertContext) -> int:
        ev = ctx.event
        stmt = select(models.ViolationEvent).where(
            models.ViolationEvent.rule == ev["rule"],
            models.ViolationEvent.person_id == int(ev["person_id"]),
            models.ViolationEvent.frame == int(ev["frame"]),
            models.ViolationEvent.source == ctx.source,
        )
        existing = db.execute(stmt).scalar_one_or_none()
        if existing is not None:
            return existing.id
        row = models.ViolationEvent(
            rule=ev["rule"],
            person_id=int(ev["person_id"]),
            frame=int(ev["frame"]),
            first_seen_ts=float(ev["first_seen_ts"]),
            emitted_ts=float(ev["emitted_ts"]),
            duration_seconds=float(ev["duration_seconds"]),
            violation_class=ev["violation_class"],
            violation_conf=float(ev["violation_conf"]),
            person_bbox=list(ev["person_bbox"]),
            violation_bbox=list(ev["violation_bbox"]),
            source=ctx.source,
        )
        db.add(row)
        db.flush()
        return row.id

    def _ensure_evidence(self, db: Session, event_id: int, ctx: AlertContext) -> None:
        for kind, path in (("full", ctx.full_frame_path), ("crop", ctx.crop_path)):
            if not path:
                continue
            p = str(path)
            already = db.execute(
                select(models.EvidenceFile).where(
                    models.EvidenceFile.event_id == event_id,
                    models.EvidenceFile.kind == kind,
                    models.EvidenceFile.path == p,
                )
            ).scalar_one_or_none()
            if already:
                continue
            db.add(models.EvidenceFile(event_id=event_id, kind=kind, path=p))

    def send(self, ctx: AlertContext) -> None:
        with self._Session() as db:
            event_id = self._get_or_create_event(db, ctx)
            self._ensure_evidence(db, event_id, ctx)
            db.commit()
        self._event_ids[id(ctx)] = event_id

    def record_audit(self, ctx: AlertContext, results: list) -> None:
        event_id = self._event_ids.pop(id(ctx), None)
        if event_id is None:
            return
        ts = time.time()
        with self._Session() as db:
            for r in results:
                db.add(models.AlertDispatch(
                    event_id=event_id,
                    sink=r.sink,
                    success=bool(r.success),
                    error=str(r.error or ""),
                    dispatched_at=ts,
                ))
            db.commit()

    def close(self) -> None:
        self._engine.dispose()
