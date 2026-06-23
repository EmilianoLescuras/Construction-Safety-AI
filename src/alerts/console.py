"""Console sink — prints alert headlines + evidence paths to stdout."""
from __future__ import annotations

from src.alerts.base import AlertContext, AlertSink


class ConsoleSink(AlertSink):
    name = "console"

    def __init__(self, _config: dict | None = None) -> None:
        return None

    def send(self, ctx: AlertContext) -> None:
        print(f"[ALERT] {ctx.headline()}")
        if ctx.full_frame_path is not None:
            print(f"         full  -> {ctx.full_frame_path}")
        if ctx.crop_path is not None:
            print(f"         crop  -> {ctx.crop_path}")
