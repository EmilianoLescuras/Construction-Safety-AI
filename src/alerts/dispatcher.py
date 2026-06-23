"""Alert dispatcher — load configured sinks and fan out events."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from src.alerts.base import AlertContext, AlertSink
from src.alerts.console import ConsoleSink
from src.alerts.evidence import EvidenceConfig


SINK_REGISTRY: dict[str, type] = {"console": ConsoleSink}


def _maybe_register_telegram() -> None:
    try:
        from src.alerts.telegram import TelegramSink
        SINK_REGISTRY["telegram"] = TelegramSink
    except ImportError:
        pass


def _maybe_register_email() -> None:
    from src.alerts.email import EmailSink
    SINK_REGISTRY["email"] = EmailSink


_maybe_register_telegram()
_maybe_register_email()


@dataclass
class DispatchResult:
    sink: str
    success: bool
    error: str = ""


class AlertDispatcher:
    def __init__(self, sinks: list[AlertSink]) -> None:
        self.sinks = sinks

    @classmethod
    def from_config(cls, config: dict) -> "AlertDispatcher":
        sinks: list[AlertSink] = []
        for name, spec in (config.get("sinks", {}) or {}).items():
            if not spec.get("enabled"):
                continue
            klass = SINK_REGISTRY.get(name)
            if klass is None:
                print(f"[alerts] unknown sink '{name}' — skipping")
                continue
            try:
                sinks.append(klass(spec))
            except Exception as exc:
                print(f"[alerts] disabled sink '{name}': {exc}")
        return cls(sinks=sinks)

    def dispatch(self, ctx: AlertContext) -> list[DispatchResult]:
        results: list[DispatchResult] = []
        for sink in self.sinks:
            try:
                sink.send(ctx)
                results.append(DispatchResult(sink=sink.name, success=True))
            except Exception as exc:
                results.append(DispatchResult(sink=sink.name, success=False, error=str(exc)))
        return results

    def close(self) -> None:
        for sink in self.sinks:
            try:
                sink.close()
            except Exception:
                pass


def load_alerts_config(path: Path) -> tuple[dict, EvidenceConfig]:
    data = json.loads(path.read_text(encoding="utf-8"))
    ev = data.get("evidence", {}) or {}
    out_dir = Path(ev.get("out_dir", "outputs/images/evidence"))
    evidence_cfg = EvidenceConfig(
        enabled=bool(ev.get("enabled", True)),
        out_dir=out_dir,
        save_full_frame=bool(ev.get("save_full_frame", True)),
        save_crop=bool(ev.get("save_crop", True)),
        crop_padding=float(ev.get("crop_padding", 0.1)),
        annotate_full_frame=bool(ev.get("annotate_full_frame", True)),
    )
    return data, evidence_cfg
