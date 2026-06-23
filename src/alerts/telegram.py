"""Telegram sink — posts alerts to a chat via the Bot API.

Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in the environment
(loaded from .env). Uses ``sendPhoto`` when a crop is available, else
``sendMessage``.
"""
from __future__ import annotations

import os

import httpx

from src.alerts.base import AlertContext, AlertSink

API_BASE = "https://api.telegram.org"


class TelegramSink(AlertSink):
    name = "telegram"

    def __init__(self, config: dict | None = None) -> None:
        config = config or {}
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        if not token or not chat_id:
            raise RuntimeError(
                "TelegramSink requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars"
            )
        self._token = token
        self._chat_id = chat_id
        self._send_photo = bool(config.get("send_photo", True))
        self._parse_mode = str(config.get("parse_mode", "Markdown"))
        self._client = httpx.Client(timeout=15.0)

    def _url(self, method: str) -> str:
        return f"{API_BASE}/bot{self._token}/{method}"

    def send(self, ctx: AlertContext) -> None:
        text = ctx.detail_markdown()
        if self._send_photo and ctx.crop_path and ctx.crop_path.exists():
            with ctx.crop_path.open("rb") as fh:
                r = self._client.post(
                    self._url("sendPhoto"),
                    data={
                        "chat_id": self._chat_id,
                        "caption": text,
                        "parse_mode": self._parse_mode,
                    },
                    files={"photo": (ctx.crop_path.name, fh, "image/jpeg")},
                )
        else:
            r = self._client.post(
                self._url("sendMessage"),
                data={
                    "chat_id": self._chat_id,
                    "text": text,
                    "parse_mode": self._parse_mode,
                },
            )
        if r.status_code >= 400:
            raise RuntimeError(f"Telegram API {r.status_code}: {r.text[:200]}")

    def close(self) -> None:
        self._client.close()
