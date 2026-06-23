"""PPE compliance rule engine.

Consumes per-frame tracked-detection records (the JSONL contract from
``src/tracking.py``) and emits ``ViolationEvent`` dicts when a tracked
Person has been positively associated with a ``NO-*`` PPE detection for
at least ``min_violation_seconds``.

Design decisions:

- **Association**: PPE detections are linked to a Person track when the
  PPE bbox's center lies inside the Person bbox. When several Person
  bboxes contain the same center, the smallest-area Person is chosen
  (most nested → most specific).
- **Conservative policy**: a violation requires a positive ``NO-*``
  detection. The mere absence of a compliance detection (e.g., no
  ``Hardhat`` is detected on a Person) is NOT a violation — model recall
  is imperfect and false positives on real workers are costlier than
  missed violations.
- **Cooldown**: once an event is emitted for (person_id, rule), no new
  event for the same pair is emitted for ``cooldown_seconds`` after the
  emission timestamp. This avoids flooding alerts when a violation
  persists for minutes.

ViolationEvent schema (one JSON object per line in the output JSONL):

    {
      "event_type": "violation",
      "rule": "helmet",
      "person_id": 7,
      "first_seen_ts": 12.3,
      "emitted_ts": 15.4,
      "duration_seconds": 3.1,
      "frame": 154,
      "violation_class": "NO-Hardhat",
      "violation_conf": 0.91,
      "person_bbox": [x1, y1, x2, y2]
    }
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator


# ── Geometry helpers ─────────────────────────────────────────────────────────

def bbox_center(box: list[float]) -> tuple[float, float]:
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def bbox_area(box: list[float]) -> float:
    x1, y1, x2, y2 = box
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def point_in_box(pt: tuple[float, float], box: list[float]) -> bool:
    x, y = pt
    x1, y1, x2, y2 = box
    return x1 <= x <= x2 and y1 <= y <= y2


# ── Rule configuration ───────────────────────────────────────────────────────

@dataclass
class Rule:
    name: str
    enabled: bool
    violation_classes: tuple[str, ...]
    compliance_classes: tuple[str, ...]
    min_violation_seconds: float
    cooldown_seconds: float

    @classmethod
    def from_dict(cls, name: str, d: dict) -> "Rule":
        return cls(
            name=name,
            enabled=bool(d.get("enabled", True)),
            violation_classes=tuple(d.get("violation_classes", ())),
            compliance_classes=tuple(d.get("compliance_classes", ())),
            min_violation_seconds=float(d.get("min_violation_seconds", 3.0)),
            cooldown_seconds=float(d.get("cooldown_seconds", 30.0)),
        )


@dataclass
class Config:
    rules: list[Rule]
    person_class: str = "Person"
    min_person_conf: float = 0.3

    @classmethod
    def from_path(cls, path: Path | str) -> "Config":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        rules = [Rule.from_dict(name, r) for name, r in data.get("rules", {}).items()]
        assoc = data.get("association", {})
        return cls(
            rules=rules,
            person_class=str(assoc.get("person_class", "Person")),
            min_person_conf=float(assoc.get("min_person_conf", 0.3)),
        )


# ── Per-person state ─────────────────────────────────────────────────────────

@dataclass
class PersonRuleState:
    """Sliding state for a single (person_id, rule) pair."""
    first_seen_ts: float | None = None
    last_emit_ts: float | None = None


@dataclass
class RuleEngine:
    config: Config
    # state[person_id][rule_name] -> PersonRuleState
    _state: dict[int, dict[str, PersonRuleState]] = field(default_factory=dict)

    def _state_for(self, person_id: int, rule_name: str) -> PersonRuleState:
        return self._state.setdefault(person_id, {}).setdefault(rule_name, PersonRuleState())

    def process_frame(self, record: dict) -> list[dict]:
        """Update state from one frame record. Returns emitted ViolationEvents."""
        ts = float(record.get("ts", 0.0))
        frame_id = int(record.get("frame", 0))
        tracks = list(record.get("tracks", []))

        persons = [
            t for t in tracks
            if t.get("class") == self.config.person_class
            and int(t.get("id", -1)) >= 0
            and float(t.get("conf", 0.0)) >= self.config.min_person_conf
        ]
        persons.sort(key=lambda t: bbox_area(t["bbox"]))  # smallest-first

        def assign_to_person(det_box: list[float]) -> dict | None:
            c = bbox_center(det_box)
            for p in persons:
                if point_in_box(c, p["bbox"]):
                    return p
            return None

        events: list[dict] = []
        seen_pairs: set[tuple[int, str]] = set()

        for rule in self.config.rules:
            if not rule.enabled:
                continue

            for t in tracks:
                if t.get("class") not in rule.violation_classes:
                    continue
                owner = assign_to_person(t["bbox"])
                if owner is None:
                    continue
                pid = int(owner["id"])
                state = self._state_for(pid, rule.name)
                if state.first_seen_ts is None:
                    state.first_seen_ts = ts
                seen_pairs.add((pid, rule.name))

                duration = ts - state.first_seen_ts
                if duration < rule.min_violation_seconds:
                    continue
                if state.last_emit_ts is not None and (ts - state.last_emit_ts) < rule.cooldown_seconds:
                    continue

                events.append({
                    "event_type": "violation",
                    "rule": rule.name,
                    "person_id": pid,
                    "first_seen_ts": state.first_seen_ts,
                    "emitted_ts": ts,
                    "duration_seconds": round(duration, 3),
                    "frame": frame_id,
                    "violation_class": t["class"],
                    "violation_conf": float(t["conf"]),
                    "person_bbox": owner["bbox"],
                    "violation_bbox": t["bbox"],
                })
                state.last_emit_ts = ts

        # Clear first_seen for (person, rule) pairs that did NOT see a violation
        # this frame — the violation interval has been broken.
        for pid, per_rule in self._state.items():
            for rname, st in per_rule.items():
                if (pid, rname) not in seen_pairs:
                    st.first_seen_ts = None

        return events

    def process_records(self, records: Iterable[dict]) -> Iterator[dict]:
        for rec in records:
            yield from self.process_frame(rec)
