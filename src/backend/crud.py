"""Database query helpers — kept small and focused."""
from __future__ import annotations

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from src.backend import models, schemas


def get_event(db: Session, event_id: int) -> models.ViolationEvent | None:
    stmt = (
        select(models.ViolationEvent)
        .options(
            selectinload(models.ViolationEvent.evidence_files),
            selectinload(models.ViolationEvent.dispatches),
        )
        .where(models.ViolationEvent.id == event_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def list_events(
    db: Session,
    *,
    rule: str | None = None,
    person_id: int | None = None,
    since_ts: float | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[models.ViolationEvent]:
    stmt = (
        select(models.ViolationEvent)
        .options(
            selectinload(models.ViolationEvent.evidence_files),
            selectinload(models.ViolationEvent.dispatches),
        )
        .order_by(desc(models.ViolationEvent.emitted_ts), desc(models.ViolationEvent.id))
        .limit(limit)
        .offset(offset)
    )
    if rule:
        stmt = stmt.where(models.ViolationEvent.rule == rule)
    if person_id is not None:
        stmt = stmt.where(models.ViolationEvent.person_id == person_id)
    if since_ts is not None:
        stmt = stmt.where(models.ViolationEvent.emitted_ts >= since_ts)
    return list(db.execute(stmt).scalars().all())


def insert_events(
    db: Session, events: list[schemas.ViolationEventIn], source: str | None
) -> tuple[int, int, list[models.ViolationEvent]]:
    """Bulk insert, skipping (rule, person_id, frame, source) duplicates."""
    inserted_models: list[models.ViolationEvent] = []
    skipped = 0
    for ev in events:
        exists_stmt = select(models.ViolationEvent.id).where(
            models.ViolationEvent.rule == ev.rule,
            models.ViolationEvent.person_id == ev.person_id,
            models.ViolationEvent.frame == ev.frame,
            models.ViolationEvent.source == source,
        )
        if db.execute(exists_stmt).first():
            skipped += 1
            continue
        m = models.ViolationEvent(**ev.model_dump(), source=source)
        db.add(m)
        inserted_models.append(m)
    db.commit()
    for m in inserted_models:
        db.refresh(m)
    return len(inserted_models), skipped, inserted_models


def summary(db: Session) -> schemas.StatsSummary:
    total_events = db.execute(select(func.count(models.ViolationEvent.id))).scalar_one()
    total_dispatches = db.execute(select(func.count(models.AlertDispatch.id))).scalar_one()
    success = db.execute(
        select(func.count(models.AlertDispatch.id)).where(models.AlertDispatch.success.is_(True))
    ).scalar_one()
    failed = db.execute(
        select(func.count(models.AlertDispatch.id)).where(models.AlertDispatch.success.is_(False))
    ).scalar_one()

    by_rule = db.execute(
        select(models.ViolationEvent.rule, func.count(models.ViolationEvent.id))
        .group_by(models.ViolationEvent.rule)
        .order_by(desc(func.count(models.ViolationEvent.id)))
    ).all()

    top_persons = db.execute(
        select(models.ViolationEvent.person_id, func.count(models.ViolationEvent.id))
        .group_by(models.ViolationEvent.person_id)
        .order_by(desc(func.count(models.ViolationEvent.id)))
        .limit(10)
    ).all()

    return schemas.StatsSummary(
        total_events=total_events,
        total_dispatches=total_dispatches,
        dispatch_success=success,
        dispatch_failed=failed,
        by_rule=[schemas.RuleCount(rule=r, count=c) for r, c in by_rule],
        top_persons=[schemas.PersonCount(person_id=p, count=c) for p, c in top_persons],
    )
