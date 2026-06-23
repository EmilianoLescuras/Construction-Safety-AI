"""Thin client for posting violation events to the backend API."""
from __future__ import annotations

import logging
from dataclasses import asdict, is_dataclass
from typing import Any

import httpx

log = logging.getLogger(__name__)


class ApiClient:
    """POSTs events to /events/batch and uploads evidence images.

    Falls back to a no-op when ``base_url`` is None (useful for dry runs).
    """

    def __init__(self, base_url: str | None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/") if base_url else None
        self.timeout = timeout
        self._http = httpx.Client(timeout=timeout) if base_url else None

    def healthy(self) -> bool:
        if not self._http or not self.base_url:
            return False
        try:
            r = self._http.get(f"{self.base_url}/health")
            return r.status_code == 200
        except httpx.HTTPError as e:
            log.warning("api health check failed: %s", e)
            return False

    def post_events(self, events: list[Any], source: str | None = None) -> dict:
        if not self._http or not self.base_url:
            log.info("[dry-run] would POST %d events (source=%s)", len(events), source)
            return {"inserted": 0, "skipped": len(events), "dry_run": True}

        payload = {
            "source": source,
            "events": [asdict(e) if is_dataclass(e) else e for e in events],
        }
        r = self._http.post(f"{self.base_url}/events/batch", json=payload)
        r.raise_for_status()
        return r.json()

    def close(self) -> None:
        if self._http:
            self._http.close()

    def __enter__(self) -> ApiClient:
        return self

    def __exit__(self, *_exc) -> None:
        self.close()
