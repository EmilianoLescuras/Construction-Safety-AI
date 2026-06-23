"""Dispatcher tests — audit-sink ordering + DbSink dedup behavior."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.alerts.base import AlertContext, AlertSink
from src.alerts.db import DbSink
from src.alerts.dispatcher import AlertDispatcher, DispatchResult
from src.backend import models
from src.backend.db import Base


@pytest.fixture
def db_url(tmp_path) -> str:
    """File-based SQLite under tmp_path so DbSink and the verification session
    share the same database.

    In-memory SQLite is per-connection-private, so we cannot use ``sqlite://``
    here — DbSink builds its own engine from the URL we hand it, and we need
    a second session to read back what it wrote.
    """
    db_path = tmp_path / "test.db"
    url = f"sqlite:///{db_path}"

    # Build schema once.
    engine = create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    engine.dispose()

    # Repoint the backend module-level SessionLocal at the same file so the
    # verification queries below go through the same path DbSink writes to.
    from src.backend import db as backend_db
    original_engine = backend_db.engine
    original_sessionmaker = backend_db.SessionLocal
    backend_db.engine = create_engine(url, connect_args={"check_same_thread": False})
    backend_db.SessionLocal = sessionmaker(
        bind=backend_db.engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    yield url
    backend_db.engine.dispose()
    backend_db.engine = original_engine
    backend_db.SessionLocal = original_sessionmaker


def _event_dict(person_id: int = 1, frame: int = 30) -> dict:
    return {
        "event_type": "violation",
        "rule": "vest",
        "person_id": person_id,
        "first_seen_ts": 0.0,
        "emitted_ts": 3.0,
        "duration_seconds": 3.0,
        "frame": frame,
        "violation_class": "NO-Safety Vest",
        "violation_conf": 0.85,
        "person_bbox": [100.0, 100.0, 200.0, 400.0],
        "violation_bbox": [125.0, 125.0, 175.0, 175.0],
    }


class _RecordingSink(AlertSink):
    name = "recorder"

    def __init__(self) -> None:
        self.calls: list[AlertContext] = []

    def send(self, ctx: AlertContext) -> None:
        self.calls.append(ctx)


class _FailingSink(AlertSink):
    name = "boom"

    def send(self, ctx: AlertContext) -> None:
        raise RuntimeError("kaboom")


def test_dispatcher_isolates_failing_sink_and_returns_per_sink_results():
    rec = _RecordingSink()
    boom = _FailingSink()
    dispatcher = AlertDispatcher(sinks=[rec, boom])
    results = dispatcher.dispatch(AlertContext(event=_event_dict()))
    assert len(rec.calls) == 1
    assert {r.sink for r in results} == {"recorder", "boom"}
    by_name = {r.sink: r for r in results}
    assert by_name["recorder"].success is True
    assert by_name["boom"].success is False
    assert "kaboom" in by_name["boom"].error


def test_dbsink_persists_event_evidence_and_dispatches(db_url, tmp_path):
    full = tmp_path / "full.jpg"
    crop = tmp_path / "crop.jpg"
    full.write_bytes(b"fake")
    crop.write_bytes(b"fake")

    db_sink = DbSink({"database_url": db_url})
    recorder = _RecordingSink()
    failing = _FailingSink()
    dispatcher = AlertDispatcher(sinks=[db_sink, recorder, failing])

    ctx = AlertContext(
        event=_event_dict(),
        full_frame_path=full,
        crop_path=crop,
        source="test_source",
    )
    results = dispatcher.dispatch(ctx)

    assert {r.sink for r in results} == {"db", "recorder", "boom"}

    from src.backend.db import SessionLocal
    with SessionLocal() as db:
        events = db.query(models.ViolationEvent).all()
        assert len(events) == 1
        ev_row = events[0]
        assert ev_row.source == "test_source"
        assert ev_row.person_id == 1

        evidence_rows = db.query(models.EvidenceFile).filter_by(event_id=ev_row.id).all()
        kinds = {e.kind for e in evidence_rows}
        assert kinds == {"full", "crop"}

        dispatch_rows = db.query(models.AlertDispatch).filter_by(event_id=ev_row.id).all()
        sinks = {d.sink: d for d in dispatch_rows}
        # All three sinks (including db itself) recorded.
        assert set(sinks) == {"db", "recorder", "boom"}
        assert sinks["db"].success is True
        assert sinks["recorder"].success is True
        assert sinks["boom"].success is False


def test_dbsink_dedup_on_same_event_key(db_url, tmp_path):
    """Second dispatch with same (rule, person_id, frame, source) reuses the row
    but still records a new AlertDispatch."""
    full = tmp_path / "full.jpg"
    full.write_bytes(b"fake")
    db_sink = DbSink({"database_url": db_url})
    dispatcher = AlertDispatcher(sinks=[db_sink])

    ev = _event_dict()
    ctx1 = AlertContext(event=ev, full_frame_path=full, source="dup_src")
    ctx2 = AlertContext(event=ev, full_frame_path=full, source="dup_src")
    dispatcher.dispatch(ctx1)
    dispatcher.dispatch(ctx2)

    from src.backend.db import SessionLocal
    with SessionLocal() as db:
        assert db.query(models.ViolationEvent).count() == 1
        # Same evidence path → deduped to one row.
        assert db.query(models.EvidenceFile).count() == 1
        # But each dispatch is logged separately.
        assert db.query(models.AlertDispatch).count() == 2


def test_dispatcher_records_audit_after_regular_sinks_succeed():
    """Audit sink must see DispatchResults for *all* prior sinks, not just itself."""
    captured: list[list[DispatchResult]] = []

    class FakeAudit(AlertSink):
        name = "audit"
        is_audit_sink = True

        def send(self, ctx: AlertContext) -> None:
            pass

        def record_audit(self, ctx, results):
            captured.append(list(results))

    audit = FakeAudit()
    recorder = _RecordingSink()
    dispatcher = AlertDispatcher(sinks=[recorder, audit])  # audit listed second
    dispatcher.dispatch(AlertContext(event=_event_dict()))

    assert len(captured) == 1
    sink_names = [r.sink for r in captured[0]]
    # Audit sinks run first (so the row exists), regulars after.
    assert sink_names == ["audit", "recorder"]
