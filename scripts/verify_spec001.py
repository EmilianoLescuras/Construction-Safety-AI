"""Verify the SPEC-001 acceptance criteria against the current state of
``datasets/v2_inbox/``.

This is the automated sign-off check for SPEC-001 (data correction). It is
run AFTER a human has corrected the 52 frames in Label Studio and exported
YOLO labels back over ``datasets/v2_inbox/labels/``. It does not trust a
verbal "done" — it measures.

Checks (all must pass):
  1. There are exactly 52 label files (one per frame).
  2. The total box count GREW vs the baseline recorded in REVIEW.md's
     header (we added missed hi-vis vests, not only deleted).
  3. REVIEW.md carries a filled "Changed" note for every one of the 52
     frames (proof each frame was actually reviewed by a human).

Exit code 0 = all pass; 1 = at least one fails (prints which).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INBOX = PROJECT_ROOT / "datasets" / "v2_inbox"
LBL_DIR = INBOX / "labels"
REVIEW = INBOX / "REVIEW.md"

EXPECTED_FRAMES = 52


def box_count(path: Path) -> int:
    return sum(1 for ln in path.read_text().splitlines() if ln.strip())


def parse_baseline(text: str) -> int | None:
    m = re.search(r"Baseline.*?(\d+)\s+boxes", text, re.IGNORECASE | re.DOTALL)
    return int(m.group(1)) if m else None


def review_rows(text: str) -> list[tuple[str, str]]:
    """Return (frame, changed_note) for each data row of the frame table."""
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            continue
        idx, frame, pseudo, changed = cells
        if idx in ("#", "---", ":---") or set(idx) <= set("-: "):
            continue  # header / separator
        if not idx.isdigit():
            continue
        rows.append((frame, changed))
    return rows


def main() -> int:
    failures: list[str] = []

    if not LBL_DIR.is_dir():
        print(f"FAIL: {LBL_DIR} does not exist")
        return 1
    if not REVIEW.is_file():
        print(f"FAIL: {REVIEW} does not exist")
        return 1

    review_text = REVIEW.read_text()

    # Check 1 — file count
    label_files = sorted(LBL_DIR.glob("*.txt"))
    n_files = len(label_files)
    c1 = n_files == EXPECTED_FRAMES
    print(f"[1] label files == {EXPECTED_FRAMES}: {n_files} -> "
          f"{'PASS' if c1 else 'FAIL'}")
    if not c1:
        failures.append(f"expected {EXPECTED_FRAMES} label files, found {n_files}")

    # Check 2 — box count grew vs baseline
    baseline = parse_baseline(review_text)
    total = sum(box_count(f) for f in label_files)
    if baseline is None:
        print("[2] box count grew: FAIL (could not parse baseline from REVIEW.md)")
        failures.append("baseline not found in REVIEW.md header")
    else:
        c2 = total > baseline
        print(f"[2] box count grew vs baseline {baseline}: now {total} -> "
              f"{'PASS' if c2 else 'FAIL'}")
        if not c2:
            failures.append(
                f"box count did not grow (baseline {baseline}, now {total})")

    # Check 3 — every frame has a filled Changed note
    rows = review_rows(review_text)
    filled = [(f, c) for f, c in rows if c]
    c3 = len(rows) >= EXPECTED_FRAMES and len(filled) == len(rows) and len(rows) > 0
    print(f"[3] REVIEW.md notes: {len(rows)} frame rows, {len(filled)} filled -> "
          f"{'PASS' if c3 else 'FAIL'}")
    if not c3:
        if len(rows) < EXPECTED_FRAMES:
            failures.append(
                f"REVIEW.md has {len(rows)} frame rows, need >= {EXPECTED_FRAMES}")
        unfilled = [f for f, c in rows if not c]
        if unfilled:
            failures.append(
                f"{len(unfilled)} frames have no Changed note: "
                f"{', '.join(unfilled[:5])}{' ...' if len(unfilled) > 5 else ''}")

    print()
    if failures:
        print("SPEC-001 NOT satisfied:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("SPEC-001 acceptance criteria: ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
