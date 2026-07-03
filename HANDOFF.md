# HANDOFF — skill-transfer-v1 CONCLUDED (null by precondition)

Spine session: `80bdcd4e-e9fa-4487-aa55-c3f6b16b10b2` in namespace `dev/skill-transfer`.
Mirrored via `handoff_save` under key `bootstrap`. Terminal state — no further runs in this
experiment. Full reasoning in `ANALYSIS.md` (deviations #1–#14, `## Outcome`).

## Verdict

**skill-transfer-v1 concludes null by precondition.** No task pairing exposed the
"orchestrator succeeds where the edge model fails" gap the pre-registered hypothesis requires, so
no capability skill was authored and no skill/referee cells were ever run. The hypothesis was
never reached and **remains open** for a future pairing with a real gap.

## Measured baselines (per-task means, 20 acknowledged reps per arm)

| task | metric | A1 orchestrator (`claude-fable-5`) | A3 edge (`claude-opus-4-8`) | reading |
|------|--------|:---:|:---:|---------|
| T01 | schema_valid / field_accuracy | 0.0 / 0.0 | 0.0 / 0.0 | double floor — no successful A1 traces, protocol permits no skill |
| T02 | postcondition | 0.80 (n=5) | 1.0 (n=5) | edge above orchestrator — gap_closure denominator negative |
| T09 | solution_valid | 1.0 (n=10) | 1.0 (given) | control saturated — prediction trivially satisfied |

All A1 records acknowledged on the spine (`run/{T01,T02,T09}/orch_bare/*`); A3 T02
re-collected under the fixed harness (`run/T02/edge_bare/1..5`). T01/T09 are harness 0.1.4;
T02 (both arms) is harness 0.1.6. `coord_reconcile` marks the run records `stale` only because
`main` HEAD advanced past each record's `repo_sha` during the 0.1.4→0.1.6 harness patches — a
repo_sha lag, **not** an invalidation; each was `current` at collection time.

## Harness state — v0.1.6

Three fail-closed integrity fixes landed after the A1 batch exposed them (all logged in
ANALYSIS.md #11–#14; arm-parity launch path otherwise byte-identical between edge and orch):
1. run-record `event_id = uuid5(run_id)` — distinct from the `run_id` the measured model reuses
   for its own spine writes (global event_id idempotency was silently dropping T02 records);
2. `SpineClient.call()` raises on tool-level `isError` — a rejected/deduped write can no longer be
   phantom-acked;
3. `artifact_put` uploads via `content_base64` (was `data`, silently null); plus an abort on CLI
   `is_error`/`api_error_status` so a rate-limited non-run is never scored.

## Reusable assets (carry forward as a FRESH pre-registration, never a retrofit)

- the **v0.1.6 harness** (arm-parity launch, fail-closed graders/writes);
- **fable-5's two perfect T02 traces** — `run/T02/orch_bare/2` (09d9df3a), `.../5` (73210209),
  postcondition 1.0 — distillation-ready;
- the **pinned dormant referee** `gpt-5.5-2026-04-23` (never exercised);
- a possible **v2**: haiku-class edge model and/or a **T01b conventions-handbook** task that puts
  the naming/enum conventions in-scope, to create a genuine orchestrator→edge gap.

## Constraints preserved throughout

No `*_skill` arm run, no skill authored, no task/grader/fixture modified; measured runs saw only
the harness-built prompt; no grader crash recorded as a score; no rebase/force-push;
`settings/*.env`, `.runs/`, `.DS_Store` never committed.
