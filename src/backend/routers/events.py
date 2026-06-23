"""Routes: list / get / batch-ingest ViolationEvents."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.backend import crud, schemas
from src.backend.db import get_db

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[schemas.ViolationEventOut])
def list_events(
    rule: str | None = Query(default=None),
    person_id: int | None = Query(default=None),
    since: float | None = Query(default=None, description="emitted_ts lower bound"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return crud.list_events(
        db, rule=rule, person_id=person_id, since_ts=since, limit=limit, offset=offset
    )


@router.get("/{event_id}", response_model=schemas.ViolationEventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    ev = crud.get_event(db, event_id)
    if ev is None:
        raise HTTPException(status_code=404, detail="event not found")
    return ev


@router.post("/batch", response_model=schemas.BatchIngestResponse, status_code=201)
def batch_ingest(req: schemas.BatchIngestRequest, db: Session = Depends(get_db)):
    inserted, skipped, _ = crud.insert_events(db, req.events, req.source)
    return schemas.BatchIngestResponse(inserted=inserted, skipped=skipped)
