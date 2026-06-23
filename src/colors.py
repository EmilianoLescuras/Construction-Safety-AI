"""Color palette for annotated overlays — stdlib-only so this module can be
imported from contexts that don't have OpenCV installed (the slim API
container, the test runner)."""
from __future__ import annotations

# BGR — drawn through OpenCV when present.
RED = (0, 0, 255)
GREEN = (0, 200, 0)
YELLOW = (0, 220, 220)
CYAN = (220, 220, 0)
BLUE = (220, 100, 0)

CATEGORY_COLORS: dict[str, tuple[int, int, int]] = {
    "NO-Hardhat": RED,
    "NO-Mask": RED,
    "NO-Safety Vest": RED,
    "Hardhat": GREEN,
    "Mask": GREEN,
    "Safety Vest": GREEN,
    "Gloves": GREEN,
    "Person": YELLOW,
    "Safety Cone": CYAN,
    "Ladder": CYAN,
    "Excavator": BLUE,
    "machinery": BLUE,
    "dump truck": BLUE,
    "sedan": BLUE,
    "van": BLUE,
    "truck": BLUE,
    "trailer": BLUE,
    "vehicle": BLUE,
    "wheel loader": BLUE,
}
