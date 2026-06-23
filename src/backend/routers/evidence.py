"""Routes: serve evidence image files by EvidenceFile id."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.backend import models
from src.backend.db import get_db
from src.backend.paths import resolve_evidence_path

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("/{evidence_id}")
def get_evidence(evidence_id: int, db: Session = Depends(get_db)):
    ef = db.get(models.EvidenceFile, evidence_id)
    if ef is None:
        raise HTTPException(status_code=404, detail="evidence not found")
    path = resolve_evidence_path(ef.path)
    if not path.is_file():
        raise HTTPException(status_code=410, detail=f"file gone: {path}")
    return FileResponse(path)
