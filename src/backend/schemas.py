"""Pydantic schemas — request/response bodies for the API."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EvidenceFileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: Literal["full", "crop"]
    path: str


class AlertDispatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sink: str
    success: bool
    error: str
    dispatched_at: float


class ViolationEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rule: str
    person_id: int
    frame: int
    first_seen_ts: float
    emitted_ts: float
    duration_seconds: float
    violation_class: str
    violation_conf: float
    person_bbox: list[float]
    violation_bbox: list[float]
    source: str | None
    ingested_at: datetime
    evidence_files: list[EvidenceFileOut] = Field(default_factory=list)
    dispatches: list[AlertDispatchOut] = Field(default_factory=list)


class ViolationEventIn(BaseModel):
    rule: str
    person_id: int
    frame: int
    first_seen_ts: float
    emitted_ts: float
    duration_seconds: float
    violation_class: str
    violation_conf: float
    person_bbox: list[float]
    violation_bbox: list[float]


class BatchIngestRequest(BaseModel):
    source: str | None = None
    events: list[ViolationEventIn]


class BatchIngestResponse(BaseModel):
    inserted: int
    skipped: int


class RuleCount(BaseModel):
    rule: str
    count: int


class PersonCount(BaseModel):
    person_id: int
    count: int


class StatsSummary(BaseModel):
    total_events: int
    total_dispatches: int
    dispatch_success: int
    dispatch_failed: int
    by_rule: list[RuleCount]
    top_persons: list[PersonCount]
