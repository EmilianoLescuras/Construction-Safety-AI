"""API smoke tests via FastAPI TestClient against an in-memory SQLite."""
from __future__ import annotations


def _event_payload(person_id: int = 1, frame: int = 30) -> dict:
    return {
        "rule": "vest",
        "person_id": person_id,
        "frame": frame,
        "first_seen_ts": 0.0,
        "emitted_ts": 3.0,
        "duration_seconds": 3.0,
        "violation_class": "NO-Safety Vest",
        "violation_conf": 0.85,
        "person_bbox": [100.0, 100.0, 200.0, 400.0],
        "violation_bbox": [125.0, 125.0, 175.0, 175.0],
    }


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_batch_ingest_and_list(client):
    payload = {
        "source": "test_video.mp4",
        "events": [_event_payload(person_id=1), _event_payload(person_id=2)],
    }
    r = client.post("/events/batch", json=payload)
    assert r.status_code == 201
    assert r.json() == {"inserted": 2, "skipped": 0}

    # Re-post the same payload — dedup kicks in.
    r2 = client.post("/events/batch", json=payload)
    assert r2.json() == {"inserted": 0, "skipped": 2}

    listed = client.get("/events").json()
    assert len(listed) == 2
    rules = {e["rule"] for e in listed}
    assert rules == {"vest"}


def test_get_event_404(client):
    r = client.get("/events/99999")
    assert r.status_code == 404


def test_filters_and_stats(client):
    client.post("/events/batch", json={
        "source": "v1.mp4",
        "events": [
            _event_payload(person_id=1, frame=10),
            _event_payload(person_id=2, frame=20),
            _event_payload(person_id=1, frame=30),
        ],
    })

    filtered = client.get("/events", params={"person_id": 1}).json()
    assert {e["person_id"] for e in filtered} == {1}
    assert len(filtered) == 2

    summary = client.get("/stats/summary").json()
    assert summary["total_events"] == 3
    by_rule = {b["rule"]: b["count"] for b in summary["by_rule"]}
    assert by_rule == {"vest": 3}
    top = {p["person_id"]: p["count"] for p in summary["top_persons"]}
    assert top == {1: 2, 2: 1}


def test_evidence_404_when_missing(client):
    r = client.get("/evidence/99999")
    assert r.status_code == 404
