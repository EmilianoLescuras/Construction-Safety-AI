# SPEC-001 — Data Correction Review Log

**Baseline (pre-correction, 2026-06-26):** 52 label files, 197 boxes.

The acceptance bar (`docs/specs/SPEC-001-data-correction.md`): every frame reviewed by a human, total box count must GROW vs the baseline above (we add missed hi-vis vests, not only delete), and this file must carry one line per frame.

Correction rules for this pass (no new classes yet — that's SPEC-002):

- Fix `sedan` boxes that are actually pickups (leave them as `sedan` for now; just get the box right).
- Add `Safety Vest` boxes on workers in hi-vis long-sleeve shirts that v1 missed.
- Remove duplicate / nonsense boxes.

Fill the **Changed** column per frame after correcting it in Label Studio (e.g. `+2 vest, sedan box tightened`, or `ok, no change`).

| # | Frame | Pseudo boxes | Changed (fill in) |
|---|-------|-------------:|-------------------|
| 1 | user_recording_v2_f00000 | 6 | |
| 2 | user_recording_v2_f00015 | 7 | |
| 3 | user_recording_v2_f00030 | 7 | |
| 4 | user_recording_v2_f00045 | 7 | |
| 5 | user_recording_v2_f00060 | 6 | |
| 6 | user_recording_v2_f00075 | 7 | |
| 7 | user_recording_v2_f00090 | 7 | |
| 8 | user_recording_v2_f00105 | 7 | |
| 9 | user_recording_v2_f00120 | 7 | |
| 10 | user_recording_v2_f00135 | 8 | |
| 11 | user_recording_v2_f00150 | 7 | |
| 12 | user_recording_v2_f00165 | 10 | |
| 13 | user_recording_v2_f00180 | 10 | |
| 14 | user_recording_v2_f00195 | 10 | |
| 15 | user_recording_v2_f00210 | 1 | |
| 16 | user_recording_v2_f00225 | 2 | |
| 17 | user_recording_v2_f00240 | 2 | |
| 18 | user_recording_v2_f00255 | 1 | |
| 19 | user_recording_v2_f00270 | 3 | |
| 20 | user_recording_v2_f00285 | 3 | |
| 21 | user_recording_v2_f00300 | 3 | |
| 22 | user_recording_v2_f00315 | 2 | |
| 23 | user_recording_v2_f00330 | 1 | |
| 24 | user_recording_v2_f00345 | 1 | |
| 25 | user_recording_v2_f00360 | 1 | |
| 26 | user_recording_v2_f00375 | 0 | |
| 27 | user_recording_v2_f00390 | 2 | |
| 28 | user_recording_v2_f00405 | 2 | |
| 29 | user_recording_v2_f00420 | 2 | |
| 30 | user_recording_v2_f00435 | 2 | |
| 31 | user_recording_v2_f00450 | 2 | |
| 32 | user_recording_v2_f00465 | 2 | |
| 33 | user_recording_v2_f00480 | 3 | |
| 34 | user_recording_v2_f00495 | 5 | |
| 35 | user_recording_v2_f00510 | 4 | |
| 36 | user_recording_v2_f00525 | 4 | |
| 37 | user_recording_v2_f00540 | 4 | |
| 38 | user_recording_v2_f00555 | 1 | |
| 39 | user_recording_v2_f00570 | 0 | |
| 40 | user_recording_v2_f00585 | 1 | |
| 41 | user_recording_v2_f00600 | 1 | |
| 42 | user_recording_v2_f00615 | 1 | |
| 43 | user_recording_v2_f00630 | 2 | |
| 44 | user_recording_v2_f00645 | 2 | |
| 45 | user_recording_v2_f00660 | 3 | |
| 46 | user_recording_v2_f00675 | 4 | |
| 47 | user_recording_v2_f00690 | 4 | |
| 48 | user_recording_v2_f00705 | 4 | |
| 49 | user_recording_v2_f00720 | 4 | |
| 50 | user_recording_v2_f00735 | 4 | |
| 51 | user_recording_v2_f00750 | 4 | |
| 52 | user_recording_v2_f00765 | 4 | |
