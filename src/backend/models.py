"""ORM models for ViolationEvents, EvidenceFiles, AlertDispatches."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backend.db import Base


class ViolationEvent(Base):
    __tablename__ = "violation_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    rule: Mapped[str] = mapped_column(String(64), index=True)
    person_id: Mapped[int] = mapped_column(Integer, index=True)
    frame: Mapped[int] = mapped_column(Integer)
    first_seen_ts: Mapped[float] = mapped_column(Float)
    emitted_ts: Mapped[float] = mapped_column(Float, index=True)
    duration_seconds: Mapped[float] = mapped_column(Float)

    violation_class: Mapped[str] = mapped_column(String(64))
    violation_conf: Mapped[float] = mapped_column(Float)
    person_bbox: Mapped[list[float]] = mapped_column(JSON)
    violation_bbox: Mapped[list[float]] = mapped_column(JSON)

    source: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    evidence_files: Mapped[list[EvidenceFile]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
    dispatches: Mapped[list[AlertDispatch]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("rule", "person_id", "frame", "source",
                         name="uq_event_rule_person_frame_source"),
        Index("ix_event_rule_emitted", "rule", "emitted_ts"),
    )


class EvidenceFile(Base):
    __tablename__ = "evidence_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("violation_events.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(16))  # "full" | "crop"
    path: Mapped[str] = mapped_column(String(512))

    event: Mapped[ViolationEvent] = relationship(back_populates="evidence_files")


class AlertDispatch(Base):
    __tablename__ = "alert_dispatches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("violation_events.id", ondelete="CASCADE"), index=True
    )
    sink: Mapped[str] = mapped_column(String(32), index=True)
    success: Mapped[bool] = mapped_column(Boolean, index=True)
    error: Mapped[str] = mapped_column(String(512), default="")
    dispatched_at: Mapped[float] = mapped_column(Float)

    event: Mapped[ViolationEvent] = relationship(back_populates="dispatches")
