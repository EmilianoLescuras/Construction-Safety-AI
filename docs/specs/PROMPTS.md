# Spec Execution Prompts — Construction Safety AI

One self-contained prompt per spec (01→11). Paste a single block into a
Claude Code session (or hand it to a subagent) to drive that spec **to
completion with proof**. Work them strictly in order — later specs guard
on earlier ones being `DONE`.

> The governing rule of this file: **a spec is only "done" when every one
> of its acceptance criteria has been verified with reproducible evidence.**
> No criterion is taken on faith. Unmet work is never reported as complete.

---

## Common Operating Rules

Every prompt below assumes these. (When you run a prompt, the agent must
re-read this section and the next one from `docs/specs/PROMPTS.md` first.)

- **Repo:** `/Users/nanolescuras/construction_safety_ai/` — stays PRIVATE.
- **SmartMine** (`/Users/nanolescuras/SmartMine-Vision-AI/`) is a
  read-only reference. Copy ideas/modules from it; **never modify it.**
- **Commits:** small and frequent, after every meaningful change.
  **No `Co-Authored-By` trailer** (portfolio attribution).
- **Before any `git push`:** scan the staged diff for secrets
  (`api_key|secret|token|password|BEGIN .*PRIVATE KEY|aws_`) and confirm
  the repo is private. **Do not push unless the user explicitly asks** —
  committing locally is fine and expected.
- **Never commit:** model weights (`*.pt/onnx/engine`), datasets,
  `runs/`, `.env`, `node_modules/`, MLflow `mlruns/`.
- **CI must stay green.** If a spec touches code, run `ruff` + `pytest`
  locally before committing.

---

## Verification Protocol (the "done" gate — applies to EVERY spec)

This is the part that matters most. Follow it literally.

1. **Dependency guard first.** Before starting spec NN, open
   `docs/specs/README.md` and confirm every spec listed under
   "Depends on" is already `DONE`. If not, stop and say so — do not start.
2. **Read the spec end-to-end** (`docs/specs/SPEC-NN-*.md`) before doing
   anything. Re-read its "Acceptance criteria" — those are the contract.
3. **Produce a Verification Report before finishing.** It is a table:
   one row per acceptance criterion → the exact command/check you ran →
   its real output (paste the relevant snippet) → `PASS` / `FAIL`.
4. **DONE requires every row `PASS`.** If any row is `FAIL` or you cannot
   verify it, the spec is **not** done:
   - Leave the index row as `TODO` (or note it `IN PROGRESS` / `BLOCKED`).
   - Report exactly which criteria are unmet and why.
   - **Never describe unmet work as complete. Never tick a task box you
     did not actually finish.**
5. **Outcome criteria are not negotiable.** When a criterion is a result
   that may not happen (e.g. "v2 mAP50 ≥ v1 + 5pp"), and it doesn't:
   the spec is NOT done. Report the real numbers, follow the spec's own
   guidance (e.g. "regroup"), and stop. **Do not move thresholds,
   cherry-pick splits, change the eval set, or otherwise game a metric to
   force a pass.**
6. **No fabrication, ever.** Do not invent numbers, screenshots, file
   contents, or tool output. If a command fails, report the failure as-is.
7. **Human-only steps are handed off, not faked.** Some steps genuinely
   need a person (manual image labelling, creating a Roboflow/account,
   recording a screen capture, judging a dataset's license). For those:
   do everything around them, then **STOP and hand off with precise
   instructions.** When the human reports back, **verify the resulting
   artifacts** (counts, files, formats) before continuing — do not take
   "I did it" as proof.

**Completion protocol (only when all criteria PASS):**
- Tick the boxes in the spec's "Tasks" section that you genuinely did.
- Print the full Verification Report (all `PASS`).
- Secret-scan, confirm private, commit (`feat(specNN): …`, no
  `Co-Authored-By`). Do not push unless asked.
- Flip that spec's row in `docs/specs/README.md` from `TODO` → `DONE`
  **in the same commit** — and only because every criterion passed.

---

## SPEC-001 — Data Correction Pass

```
Execute SPEC-001 for Construction Safety AI.

First: re-read the "Common Operating Rules" and "Verification Protocol"
in docs/specs/PROMPTS.md, then read docs/specs/SPEC-001-data-correction.md
in full.

Context: the Label Studio tooling is already committed
(scripts/yolo_to_labelstudio.py, scripts/start_labelstudio.sh) and the
import bundle (datasets/v2_inbox/labelstudio_tasks.json = 52 tasks /
197 pre-drawn boxes) is generated. label-studio is installed in .venv.

Do this:
1. Snapshot the BASELINE before any human edits: count the total YOLO
   boxes currently in datasets/v2_inbox/labels/ (sum of lines across all
   .txt) and the number of label files. Record both numbers — this is
   the bar that "label count grew" is measured against. Save to
   datasets/v2_inbox/REVIEW.md as a header (do NOT commit datasets, but
   create the file).
2. This spec's core — correcting 52 frames in a labelling tool — is
   HUMAN work. Print the exact run procedure (start_labelstudio.sh →
   paste labelstudio_config.xml → import labelstudio_tasks.json →
   correct sedan→pickup boxes and add missed hi-vis vests → export YOLO
   over datasets/v2_inbox/labels/). Then STOP and hand off. Do not
   pretend the labelling happened.
3. AFTER the human exports, VERIFY (do not trust "done"):
   - All 52 label files still present.
   - Total box count GREW vs the baseline from step 1 (print before/after).
   - Every frame has a one-line entry in REVIEW.md (≥ 52 content lines).
   - Spot-check that labels actually changed (diff a few against the
     pseudo-labels).

Acceptance criteria → verify each, build the Verification Report:
- [ ] Every .txt in datasets/v2_inbox/labels/ reviewed by a human.
- [ ] Total label count grew (added vests, not only deletions).
- [ ] REVIEW.md exists with ≥ 1 line per reviewed frame.

Only when all three PASS: commit REVIEW.md + any tracked changes (labels
themselves stay gitignored under datasets/), flip SPEC-001 to DONE in
docs/specs/README.md. If the human hasn't labelled yet, leave it TODO and
report that it's blocked on the labelling pass.
```

---

## SPEC-002 — Taxonomy Update (`pickup` + hi-vis shirt)

```
Execute SPEC-002 for Construction Safety AI.

First: re-read "Common Operating Rules" + "Verification Protocol" in
docs/specs/PROMPTS.md. Dependency guard: confirm SPEC-001 is DONE in
docs/specs/README.md — if not, STOP. Then read
docs/specs/SPEC-002-taxonomy-update.md in full.

Do the work: decide the final class list (recommended: keep the 19,
collapse/drop noisy `vehicle`, add `pickup` as index 19 → 20 classes);
update config/data_v2.yaml; write scripts/remap_labels.py (idempotent,
--dry-run, old→new map); run it on datasets/v2_inbox/labels/ where
sedan→pickup applies; write docs/labelling_policy.md with the hi-vis
shirt policy + 5-10 reference photos.

Acceptance criteria → verify each with a real command, Verification Report:
- [ ] config/data_v2.yaml: nc == len(names). VERIFY by loading the yaml
      and asserting the equality; paste output.
- [ ] scripts/remap_labels.py has unit tests for: empty file, unknown
      class id (skipped), mixed remap targets. VERIFY: pytest runs them
      green; paste the pass line.
- [ ] Round-trip is byte-for-byte: remap forward then back reproduces the
      originals exactly. VERIFY with an actual script/test over a fixture
      and a real label dir (diff returns nothing); paste the diff result.
- [ ] docs/labelling_policy.md exists.

This spec is fully machine-verifiable — no human handoff. Do not mark DONE
unless the round-trip diff is genuinely empty and the 3 unit tests pass.
Run ruff + pytest, commit (feat(spec02): …), flip the index row to DONE.
```

---

## SPEC-003 — External Data Sourcing

```
Execute SPEC-003 for Construction Safety AI.

First: re-read "Common Operating Rules" + "Verification Protocol".
Dependency guard: SPEC-002 must be DONE — else STOP. Read
docs/specs/SPEC-003-external-data.md in full.

Agent-doable now: inventory v1 per-class instance counts to
docs/dataset_stats.md (identify classes < 100 instances); write
scripts/merge_datasets.py (inputs: source dirs + per-source class map;
output: copies images + remapped labels into datasets/v2_external/, skips
duplicates via perceptual hash, writes a provenance manifest.json per
merge); add datasets/v2_external/ to data_v2.yaml train globs; implement
the 80/20 re-split (20% appended to val).

HUMAN handoff: choosing/downloading Roboflow Universe datasets and
judging licenses (CC-BY / CC0 only) needs a person + a Roboflow account.
Print exactly which sparse classes need data and the documentation each
source must carry (URL, license, per-class count → docs/external_sources.md).
STOP for the human to fetch the data. Do NOT invent sources or counts.

Acceptance criteria → Verification Report (verify AFTER data is placed):
- [ ] docs/external_sources.md lists every source: URL, license, class
      mapping. VERIFY it's filled (not a template).
- [ ] Total train image count grew by ≥ 300. VERIFY by counting train
      images before/after; paste both numbers.
- [ ] merge_datasets.py wrote manifest.json with source provenance for
      EVERY file. VERIFY: count files vs manifest entries match.
- [ ] No license violations (CC-BY/CC0 only). VERIFY each license listed
      is CC-BY or CC0; flag anything else and refuse to merge it.

If the human hasn't sourced data yet, the script + docs scaffold can be
committed, but SPEC-003 stays TODO until the ≥300 and license criteria
genuinely hold. Do not flip to DONE on the scaffold alone.
```

---

## SPEC-004 — v2 Training Run + Comparison

```
Execute SPEC-004 for Construction Safety AI.

First: re-read "Common Operating Rules" + "Verification Protocol".
Dependency guard: SPEC-001, 002, 003 ALL DONE — else STOP. Read
docs/specs/SPEC-004-v2-training.md in full.

Do: (1) re-validate v1 weights on the NEW val split, record numbers in
docs/experiments/v1_on_v2_val.md — this is the bar to beat. (2) Train
exactly the command in the spec (yolov8n from v1 weights, 40 epochs,
data_v2.yaml, mlflow-experiment construction-safety-v2). This is a long
MPS job (~20-40 min) — run it for real, do not shortcut epochs. (3) Write
docs/experiments/v2_n_e40.md with the comparison table + per-class deltas
+ 3 real failure-case screenshots. (4) Promote weights → models/v2_n_e40.pt.

Acceptance criteria → Verification Report (these are OUTCOMES — be honest):
- [ ] v2 mAP50 ≥ v1 mAP50 + 0.05 on the SAME val split. Paste both numbers.
- [ ] pickup AP50 ≥ 0.40. Paste the per-class value.
- [ ] Safety Vest AP50 ≥ v1 + 3pp. Paste both.
- [ ] MLflow run logged with weights as artifact. VERIFY via mlflow run id
      + artifact listing.
- [ ] Experiment doc has: comparison table, per-class deltas, 3 failure
      screenshots that actually exist on disk.

CRITICAL: if the +5pp gate is NOT met, SPEC-004 is NOT done. Report the
real metrics, follow the spec's "regroup before SPEC-007" instruction, and
STOP. Do not change the val split, lower the threshold, or retrain
selectively to manufacture a pass. Only flip to DONE if every criterion
genuinely holds.
```

---

## SPEC-005 — Evaluation Harness + Golden Test Set

```
Execute SPEC-005 for Construction Safety AI.

First: re-read "Common Operating Rules" + "Verification Protocol".
Dependency guard: SPEC-001 DONE (may run in parallel with 002-004). Read
docs/specs/SPEC-005-eval-harness.md in full.

Do: move 100 hand-picked images from datasets/valid → datasets/golden_test/
(cover PPE compliance+violation, pickups+sedans, hi-vis shirts,
multi-worker, occlusion/distance/blur); write datasets/golden_test/README.md
with the selection rationale; ensure golden_test is excluded from every
train glob; write scripts/evaluate.py (loads any weights + golden set →
JSON of precision/recall/mAP50/mAP50-95/per-class AP50/confusion matrix +
latency p50/p95, plus a markdown report to
docs/experiments/<stem>_golden.md); add a pytest that runs evaluate.py on
a tiny fixture and asserts the JSON shape; evaluate v1 on the golden set
and commit the numbers as the baseline.

Acceptance criteria → Verification Report:
- [ ] datasets/golden_test/ has 100 images + matching labels, excluded
      from train globs. VERIFY count == 100 and that no train glob matches it.
- [ ] scripts/evaluate.py models/<w>.pt produces its report in < 2 min on
      MPS. VERIFY by timing the real run; paste the elapsed time.
- [ ] The pytest fixture test runs < 30s. VERIFY: time pytest; paste it.
- [ ] v1 golden-set numbers committed as baseline. VERIFY the doc exists
      with real numbers.

Do not flip to DONE unless the timing checks genuinely pass and the
golden set is truly 100 images held out of training.
```

---

## SPEC-006 — Model Promotion Gate

```
Execute SPEC-006 for Construction Safety AI.

First: re-read "Common Operating Rules" + "Verification Protocol".
Dependency guard: SPEC-005 DONE — else STOP. Read
docs/specs/SPEC-006-promotion-gate.md in full.

Do: write config/promotion_gate.yaml with the thresholds from the spec;
write scripts/promote.py <weights.pt> (runs evaluate.py on the golden set,
compares to the gate; on PASS: tag MLflow run production-candidate, copy
weights to models/production/current.pt as a symlink, append a row to
docs/model_registry.md; on FAIL: print failing checks, exit 1, change
NOTHING); wire the API/worker to load models/production/current.pt when
present, falling back to v1.

Acceptance criteria → Verification Report:
- [ ] promote.py on a deliberately BROKEN model exits non-zero AND changes
      nothing. VERIFY: craft/use a bad model, run it, assert exit code != 0
      and git status shows no changes to models/production or registry.
- [ ] promote.py on v1 prints a clear pass/fail line per criterion. Paste
      the output.
- [ ] docs/model_registry.md exists with v1 as the first entry.
- [ ] API picks up a freshly promoted model on next restart, no code
      change. VERIFY: promote, restart API, confirm it serves the new
      weights (log line / health field showing model path).

This is fully verifiable — no human handoff. The "changes nothing on fail"
property must be proven with a real before/after git status, not asserted.
```

---

## SPEC-007 — Backbone Upgrade (yolov8n → yolov8s)

```
Execute SPEC-007 for Construction Safety AI.

First: re-read "Common Operating Rules" + "Verification Protocol".
Dependency guard: SPEC-004 must be DONE *and have PASSED the gate* (a
bigger backbone on undersized data overfits — this spec is meaningless
otherwise). If SPEC-004 didn't clear the gate, STOP. Read
docs/specs/SPEC-007-backbone-upgrade.md in full.

Do: train exactly the spec command (yolov8s.pt, 60 epochs, patience 20,
data_v2.yaml, run-name v2_s_e60, experiment construction-safety-v2) — a
long MPS job (2-3× the n run), run it for real. Run evaluate.py on the
golden set. Compare vs v2_n_e40 in docs/experiments/v2_s_e60.md. Profile
inference latency (p50/p95/p99 at imgsz 640 on MPS and CPU). If gate
passes AND p95 ≤ 80ms on MPS → promote.py.

Acceptance criteria → Verification Report:
- [ ] v2_s_e60 mAP50 > v2_n_e40 mAP50 (any positive delta). Paste both.
- [ ] p95 latency under the gate budget on MPS. Paste the measured p95.
- [ ] Decision recorded in docs/experiments/v2_s_e60.md: promote, or stay
      on n with a stated reason (latency / marginal gain).

Honesty clause: "stay on n" is a legitimate, fully-acceptable outcome — if
s doesn't beat n or busts the latency budget, record that decision and
DON'T promote. The spec is DONE when the comparison + decision are real
and recorded, not only when s wins.
```

---

## SPEC-008 — Active-Learning Loop

```
Execute SPEC-008 for Construction Safety AI.

First: re-read "Common Operating Rules" + "Verification Protocol".
Dependency guard: SPEC-006 DONE — else STOP. Read
docs/specs/SPEC-008-active-learning.md in full.

Do: in the worker, on any detection with 0.4 < conf < 0.6, save the crop
to outputs/review_bucket/<date>/<event_id>.jpg and append a row to
outputs/review_bucket/index.parquet (ts, model_version, class, conf, bbox,
event_id); cap the bucket at 5000 most-recent crops (rotate); add
scripts/review_bucket.py export --since YYYY-MM-DD → Label-Studio import
JSON; write docs/active_learning.md (who/when reviews, how labels flow
back to datasets/); add an MLflow metric: % of inferences in the
uncertainty band per day.

Acceptance criteria → Verification Report:
- [ ] Worker writes to the bucket on every uncertain detection WITHOUT
      blocking the inference path. VERIFY: unit/integration test that an
      uncertain detection produces a crop + parquet row, and that the write
      is async/end-of-pipeline (show it doesn't sit on the hot path).
- [ ] Bucket export round-trips through Label Studio cleanly. VERIFY:
      export a sample, confirm the JSON imports (schema-valid) and maps
      back to YOLO.
- [ ] A 24h stress run yields < 1GB. A literal 24h run is impractical: run
      a SCALED stress test (e.g. N minutes at the real frame rate),
      measure bytes/crop and crop rate, and EXTRAPOLATE to 24h with the
      math shown. State clearly it's an extrapolation, not a real 24h run.
- [ ] docs/active_learning.md describes the human workflow end-to-end.

Do not claim a real 24h run you didn't do — show the scaled measurement
and the extrapolation explicitly.
```

---

## SPEC-009 — API & Deploy Hardening

```
Execute SPEC-009 for Construction Safety AI.

First: re-read "Common Operating Rules" + "Verification Protocol".
Dependency guard: SPEC-006 DONE — else STOP. Read
docs/specs/SPEC-009-api-hardening.md in full.

Do all six: X-API-Key middleware (keys from env, 401 on missing/invalid);
per-key rate limit via slowapi (60/min upload, 600/min read, 429 on
overflow); input validation (max upload size + MIME allowlist
mp4/mov/jpg/png, else 415); tight CORS allowlist from env (not *);
/healthz that returns 200 only if model loaded AND db reachable (503
otherwise); secrets out of docker-compose.yml into .env via env_file +
.env.example; tests tests/api/test_auth.py + tests/api/test_rate_limit.py.

Acceptance criteria → Verification Report (prove each with a real call):
- [ ] curl without X-API-Key → 401. Paste the status.
- [ ] 100 rapid valid-key requests trigger a 429 before the test ends.
      VERIFY via the rate-limit test; paste the 429.
- [ ] docker compose up with a required env var MISSING fails fast with a
      clear error. VERIFY by actually unsetting it and showing the failure.
- [ ] /healthz returns 503 when the model file is missing. VERIFY by
      pointing it at a missing path and showing 503.
- [ ] No new dependency heavier than slowapi. VERIFY the diff of
      requirements*.txt.

All machine-verifiable. Run ruff + pytest, ensure CI stays green. Don't
flip to DONE on code that compiles — flip it on the curl/pytest evidence.
```

---

## SPEC-010 — Observability & Alerting

```
Execute SPEC-010 for Construction Safety AI.

First: re-read "Common Operating Rules" + "Verification Protocol".
Dependency guard: SPEC-009 DONE — else STOP. Read
docs/specs/SPEC-010-observability.md in full.

Do: switch FastAPI + worker to JSON structured logs (fields ts, level,
request_id, event_id, model_version, latency_ms); add /metrics in
Prometheus format (inference_latency_seconds histogram by model_version,
inference_total{result}, detections_total{class},
compliance_violation_total{class}, review_bucket_size gauge); add
docker-compose.observability.yml (profile) wiring Prometheus + Grafana with
infra/grafana/dashboards/construction_safety.json; Prometheus alert rules
(p95>200ms 5min, error>5% 5min, no inference 10min business hours,
golden mAP50 drop ≥3pp nightly); docs/runbook.md with one section per alert.

Acceptance criteria → Verification Report:
- [ ] Tailing logs while hitting an endpoint shows ONE JSON line per
      request with ALL required fields. Paste a sample line.
- [ ] curl /metrics returns valid Prometheus output. VERIFY with
      promtool check / a parser, not just eyeballing.
- [ ] docker compose --profile obs up brings Prom + Grafana with the
      dashboard pre-loaded. VERIFY both containers healthy + dashboard
      present.
- [ ] Every alert in the rules file has a matching runbook section. VERIFY
      by listing alert names and grepping runbook headings — counts match.

Do not flip to DONE unless /metrics actually parses and every alert maps
to a runbook section (show the name-by-name match).
```

---

## SPEC-011 — Case Study + Portfolio Writeup (project finalization)

```
Execute SPEC-011 for Construction Safety AI — the finalization spec.

First: re-read "Common Operating Rules" + "Verification Protocol".
Dependency guard: SPECs 01-10 ALL DONE in docs/specs/README.md — else
STOP and list what's still open. Read docs/specs/SPEC-011-case-study.md in
full.

Agent-doable: rewrite top-level README.md as a case study (problem,
approach, v1-vs-final-v2 results table, stack mermaid diagram, "what's
hard" tradeoffs section, links to /demo + MLflow + docs/specs/); add the
"Hiring managers — start here" link at the very top; generate
docs/case_study.pdf (one page).

CRITICAL on the results table: every number must match the LATEST
models/production/current.pt evaluation on the golden set. Re-run
evaluate.py and copy the real numbers. Do not reuse stale or invented figures.

HUMAN handoff: the 60-90s screen capture of /demo
(docs/screenshots/case_study.mp4) must be recorded by a person. Print the
exact recording script (upload → detection → violation flagged). STOP for
the human to record. Then VERIFY the file plays in GitHub markdown preview
(H.264 / yuv420p, reasonable size) — do not claim the video exists until
the file is on disk and validated.

Acceptance criteria → Verification Report:
- [ ] A first-time reader understands what the project does + the results
      without leaving the README. (Self-review against this bar.)
- [ ] Results table numbers MATCH the current production model's golden
      eval. VERIFY: re-run evaluate.py, diff the table values against it.
- [ ] The 60-90s capture plays in GitHub markdown preview. VERIFY codec +
      that the file exists.
- [ ] No broken links, no "TODO" left in README. VERIFY: link-check the
      README and grep for "TODO" → zero hits.

Only when all four PASS: flip SPEC-011 to DONE. Per docs/specs/README.md,
the project is FINALIZED only when (a) all specs 01-11 DONE, (b) v2 beats
v1 by ≥5pp mAP50 on the golden set, (c) `docker compose up` detects
non-compliance on a fresh video without code changes, (d) this case study
is published. Verify all four finalization conditions before declaring the
project finalized — do not declare it on spec-11 alone.
```

---

## Quick reference — run order & what's blocked on a human

| Spec | Agent can fully verify? | Needs a human for |
|------|-------------------------|-------------------|
| 001  | Verify yes, do no       | Manual labelling of 52 frames |
| 002  | **Yes, fully**          | — |
| 003  | Verify yes, do partial  | Sourcing + license vetting of Roboflow data |
| 004  | **Yes, fully**          | — (long compute run) |
| 005  | **Yes, fully**          | — |
| 006  | **Yes, fully**          | — |
| 007  | **Yes, fully**          | — (long compute run) |
| 008  | **Yes, fully**          | — |
| 009  | **Yes, fully**          | — |
| 010  | **Yes, fully**          | — |
| 011  | Verify yes, do partial  | Recording the 60-90s demo video |
