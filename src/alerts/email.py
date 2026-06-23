"""Email sink — SMTP via stdlib.

Requires SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, ALERT_EMAIL_FROM,
and ALERT_EMAIL_TO in the environment (loaded from .env).
"""
from __future__ import annotations

import mimetypes
import os
import smtplib
from email.message import EmailMessage

from src.alerts.base import AlertContext, AlertSink


class EmailSink(AlertSink):
    name = "email"

    def __init__(self, config: dict | None = None) -> None:
        config = config or {}
        required = ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD",
                    "ALERT_EMAIL_FROM", "ALERT_EMAIL_TO")
        missing = [k for k in required if not os.getenv(k, "").strip()]
        if missing:
            raise RuntimeError(f"EmailSink missing env vars: {missing}")
        self._host = os.environ["SMTP_HOST"]
        self._port = int(os.environ["SMTP_PORT"])
        self._user = os.environ["SMTP_USER"]
        self._password = os.environ["SMTP_PASSWORD"]
        self._from = os.environ["ALERT_EMAIL_FROM"]
        self._to = [a.strip() for a in os.environ["ALERT_EMAIL_TO"].split(",") if a.strip()]
        self._subject_prefix = str(config.get("subject_prefix", "[Construction Safety AI]"))
        self._attach_evidence = bool(config.get("attach_evidence", True))

    def send(self, ctx: AlertContext) -> None:
        msg = EmailMessage()
        msg["From"] = self._from
        msg["To"] = ", ".join(self._to)
        msg["Subject"] = f"{self._subject_prefix} {ctx.headline()}"
        body = ctx.detail_markdown().replace("*", "")
        msg.set_content(body)

        if self._attach_evidence:
            for p in (ctx.crop_path, ctx.full_frame_path):
                if p and p.exists():
                    ctype, _ = mimetypes.guess_type(str(p))
                    maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
                    msg.add_attachment(p.read_bytes(), maintype=maintype, subtype=subtype,
                                       filename=p.name)

        with smtplib.SMTP(self._host, self._port) as s:
            s.starttls()
            s.login(self._user, self._password)
            s.send_message(msg)
