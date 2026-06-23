"""Rule engine tests — synthetic frame records, no model inference."""
from __future__ import annotations

from src.rule_engine import Config, Rule, RuleEngine


def _rule(name: str = "vest") -> Rule:
    return Rule(
        name=name,
        enabled=True,
        violation_classes=("NO-Safety Vest",),
        compliance_classes=("Safety Vest",),
        min_violation_seconds=3.0,
        cooldown_seconds=30.0,
    )


def _engine() -> RuleEngine:
    return RuleEngine(config=Config(rules=[_rule()]))


def _frame(ts: float, frame: int, tracks: list[dict]) -> dict:
    return {"ts": ts, "frame": frame, "tracks": tracks}


# Person bbox: a tall rectangle in the middle of the image.
PERSON_BBOX = [100.0, 100.0, 200.0, 400.0]
PERSON_TRACK = {"id": 1, "class": "Person", "class_id": 0, "conf": 0.9, "bbox": PERSON_BBOX}
# Violation bbox center (150, 150) is inside the person bbox.
VEST_TRACK = {
    "id": 2, "class": "NO-Safety Vest", "class_id": 5, "conf": 0.85,
    "bbox": [125.0, 125.0, 175.0, 175.0],
}


def test_no_event_below_min_duration():
    eng = _engine()
    out = eng.process_frame(_frame(ts=0.0, frame=0, tracks=[PERSON_TRACK, VEST_TRACK]))
    assert out == []
    out = eng.process_frame(_frame(ts=2.9, frame=1, tracks=[PERSON_TRACK, VEST_TRACK]))
    assert out == []


def test_event_emits_at_threshold():
    eng = _engine()
    eng.process_frame(_frame(ts=0.0, frame=0, tracks=[PERSON_TRACK, VEST_TRACK]))
    out = eng.process_frame(_frame(ts=3.0, frame=30, tracks=[PERSON_TRACK, VEST_TRACK]))
    assert len(out) == 1
    ev = out[0]
    assert ev["rule"] == "vest"
    assert ev["person_id"] == 1
    assert ev["frame"] == 30
    assert ev["violation_class"] == "NO-Safety Vest"
    assert ev["duration_seconds"] == 3.0


def test_cooldown_suppresses_subsequent_emissions():
    eng = _engine()
    eng.process_frame(_frame(ts=0.0, frame=0, tracks=[PERSON_TRACK, VEST_TRACK]))
    eng.process_frame(_frame(ts=3.0, frame=30, tracks=[PERSON_TRACK, VEST_TRACK]))  # emits
    out = eng.process_frame(_frame(ts=4.0, frame=40, tracks=[PERSON_TRACK, VEST_TRACK]))
    assert out == []  # within 30s cooldown


def test_broken_interval_resets_first_seen():
    eng = _engine()
    eng.process_frame(_frame(ts=0.0, frame=0, tracks=[PERSON_TRACK, VEST_TRACK]))
    eng.process_frame(_frame(ts=1.0, frame=10, tracks=[PERSON_TRACK]))  # no violation
    # 4s after the *original* first seen, but interval was broken → no event yet.
    out = eng.process_frame(_frame(ts=4.0, frame=40, tracks=[PERSON_TRACK, VEST_TRACK]))
    assert out == []


def test_violation_outside_person_box_is_ignored():
    eng = _engine()
    stray_vest = {**VEST_TRACK, "bbox": [500.0, 500.0, 540.0, 540.0]}  # far from person
    eng.process_frame(_frame(ts=0.0, frame=0, tracks=[PERSON_TRACK, stray_vest]))
    out = eng.process_frame(_frame(ts=5.0, frame=50, tracks=[PERSON_TRACK, stray_vest]))
    assert out == []


def test_smallest_person_wins_when_nested():
    """If two persons contain the same violation center, the smaller wins."""
    big_person = {**PERSON_TRACK, "id": 1, "bbox": [50.0, 50.0, 300.0, 500.0]}
    small_person = {**PERSON_TRACK, "id": 2, "bbox": [120.0, 120.0, 180.0, 200.0]}
    eng = _engine()
    eng.process_frame(_frame(ts=0.0, frame=0, tracks=[big_person, small_person, VEST_TRACK]))
    out = eng.process_frame(_frame(ts=3.0, frame=30, tracks=[big_person, small_person, VEST_TRACK]))
    assert len(out) == 1
    assert out[0]["person_id"] == 2  # smaller (nested) person wins


def test_disabled_rule_emits_nothing():
    rule = _rule()
    rule.enabled = False
    eng = RuleEngine(config=Config(rules=[rule]))
    eng.process_frame(_frame(ts=0.0, frame=0, tracks=[PERSON_TRACK, VEST_TRACK]))
    out = eng.process_frame(_frame(ts=10.0, frame=100, tracks=[PERSON_TRACK, VEST_TRACK]))
    assert out == []
