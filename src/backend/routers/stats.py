"""Routes: aggregate stats."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.backend import crud, schemas
from src.backend.db import get_db

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=schemas.StatsSummary)
def summary(db: Session = Depends(get_db)):
    return crud.summary(db)
