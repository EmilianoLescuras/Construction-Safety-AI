"""Sink interface for alert dispatch.

Each sink receives an :class:`AlertContext` and decides what to do with it
(log, push to Telegram, send email, ...). Sinks must be self-contained —
the dispatcher catches any exception and reports it, so one sink failing
does not stop the rest.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AlertContext:
    """Everything a sink needs to render and dispatch one ViolationEvent."""
    event: dict
    full_frame_path: Path | None = None
    crop_path: Path | None = None
    source: str | None = None
    extra: dict = field(default_factory=dict)

    def headline(self) -> str:
        ev = self.event
        return (
            f"PPE violation — {ev['rule'].upper()}: "
            f"worker #{ev['person_id']} ({ev['violation_class']} "
            f"conf {ev['violation_conf']:.2f}, "
            f"{ev['duration_seconds']:.1f}s)"
        )

    def detail_markdown(self) -> str:
        ev = self.event
        lines = [
            f"*PPE Violation*  —  rule `{ev['rule']}`",
            f"*Worker ID*: `{ev['person_id']}`",
            f"*Class*: `{ev['violation_class']}`  (conf {ev['violation_conf']:.2f})",
            f"*Duration*: {ev['duration_seconds']:.2f}s "
            f"(first seen at {ev['first_seen_ts']:.2f}s, emitted at {ev['emitted_ts']:.2f}s)",
            f"*Frame*: {ev['frame']}",
        ]
        return "\n".join(lines)


class AlertSink(ABC):
    """Base class for an alert destination."""

    name: str = "base"

    @abstractmethod
    def send(self, ctx: AlertContext) -> None:
        """Dispatch the alert. Raise on failure; the dispatcher reports."""

    def close(self) -> None:
        """Release resources (override if needed)."""
        return None
