# ANALYSIS — deviations and findings log

Pre-registration commit: `0a05846beb85a91fe5bf3c0acde275c951e73d79` on `main`
(message: "pre-registration: experiment design v1"). No pre-registered field
(task list, expected_transfer, reps, gap-closure formula, rubric hash) has changed since.

## Deviations from the bootstrap plan

1. **Repo name.** context.json originally named the repo `skill-transfer-experiment`; the actual
   GitHub repo provided by the operator is `aliomraniH/LLM-As-Memory` (created empty). context.json,
   SPINE.md, and harness/config.yaml were updated to the real name *before* the pre-registration
   commit. No pre-registered field affected.
2. **Branch protection** on `main` could not be enabled from the setup surface (no GitHub
   credentials in the sandbox). Enable it from the GitHub UI after first push; until then, treat
   force-pushes to main as a validity event.
   Outcome (2026-07-02, push surface): still not enabled — the push surface has no `gh` CLI and
   no branch-protection API access; operator must enable it in the GitHub UI (Settings →
   Branches → protect `main`, block force pushes and deletions).
3. **Push deferred.** Phase 0/1 commits were made in a sandboxed clone without push credentials.
   The operator pushes from a credentialed machine (commands in HANDOFF.md). Commit SHAs are
   preserved by pushing this clone's history as-is; the T02 fixture and spine seed records
   reference the pre-registration SHA above, so do not rebase or squash.
4. **Referee snapshot** left as `TODO-pin-snapshot` per PROMPTS_AND_SETTINGS.md; harness refuses
   referee cells until pinned.
5. **Headless tool permissions not pinned (harness 0.1.0 → 0.1.1).** `launch_edge` invoked
   `claude -p` with no `--allowedTools`, and the repo's `.claude/settings.json` allow-list contains
   only `mcp__MCP_Assist__*` — and is itself ignored in headless mode when the workspace is not
   trusted ("Ignoring N permissions.allow entries … this workspace has not been trusted"). The
   output channel (the model's `Write` to `{output_path}`) therefore depended on operator-level
   `~/.claude/settings.json`, which is unpinned and environment-dependent. Under these ambiguous
   conditions rep `T01/edge_bare/2` (and 3–5) scored 0.0: the model produced the correct extraction
   but its `Write` was denied (confirmed via `permission_denials` in the raw `claude -p` JSON), so no
   output file existed for the graders. Rep `T01/edge_bare/1` had scored 1.0 only because the
   operator environment happened to permit the write at that moment — the same unpinned dependency.
   Fix: `launch_edge` now pins `--allowedTools Read,Write` (harness **0.1.1**), granting the tools at
   the CLI independent of workspace trust. Grading is unchanged: a run that still produces no output
   file scores 0.0. **All `edge_bare` reps are re-run under 0.1.1** for a homogeneous baseline,
   superseding every 0.1.0 record (including `T01/edge_bare/1`); the spine's append-only history
   preserves the superseded 0.1.0 records.
6. **Grader interpreter (commit `c9db5d0`), same finding.** The deterministic-grader commands in
   `task.yaml` invoke `python`, which does not exist on this macOS host (only `python3`), so the
   first T01 smoke run crashed at the grading step. Fix: the grading loop maps a leading `python`
   token to `sys.executable`. This shipped just before the permissions fix and is part of the same
   "harness assumed an operator environment it did not pin" finding.
7. **Grading channel broken for T02 and T09 (harness 0.1.1 → 0.1.2).** The 0.1.1 re-run
   produced valid results only for T01; T02 and T09 were measuring broken plumbing, not the model.
   - **T09 — generated fixtures never reached the model.** `generate.py` wrote `problem.md` at the
     top level of the per-rep instance dir, but `launch_edge` lists inputs via
     `(task_dir/"fixtures").glob("*")`; with no `fixtures/` subdir the glob missed and the prompt
     fell back to a literal "(generated per rep …)" string with no real path. The model was told to
     solve `fixtures/problem.md` (nonexistent from cwd), never saw the instance, and wrote nothing.
     All 10 zeros were invalid. Fix: `generate.py` now writes `problem.md` into a `fixtures/`
     subdir; `instance.json` stays at the top level (it is grader ground truth and must never be
     listed among the model's inputs). Verified the glob resolves to exactly one file,
     `.runs/instances/<run_id>/fixtures/problem.md`.
   - **T02 — grader had three faults, each independently forcing 0.0.** (i) `check_spine.py` reads
     the run id from `sys.argv[1]`, but the grader command passed no argument → `IndexError`, whose
     crash the harness silently recorded as 0.0. (ii) The grader subprocess runs with `cwd=task_dir`,
     so its `SpineClient` resolved `settings/spine.env` relative to the task dir (not repo root) and
     could not authenticate → HTTP 401. (iii) Check 3 called `memory_list(prefix=…)`, an argument the
     server does not support, so the reconcile-verdict lookup could never succeed. Fixes: the grader
     command now passes `{run_id}` (harness substitutes it; `arm_runner.md` also surfaces the run id
     to the model); `spine_client.py` anchors `JOURNAL`/`ENV_FILE` to the repo root so the token
     resolves from any cwd; check 3 now does `memory_get` at `coord/_reconcile/<key>` and reads
     `value.state` (substring-matching "current" to tolerate the `<<<UNTRUSTED_DATA>>>…<<<END>>>`
     wrapper), with a `tags`-list fallback and defensive envelope-unwrapping applied to all reads.
   - **Graders now fail closed (harness 0.1.2).** A deterministic grader that exits nonzero or emits
     non-float stdout now aborts the run as INVALID (`sys.exit`) instead of being recorded as 0.0 —
     so a broken grader can never again masquerade as a genuine low score. (The graders themselves
     still return 0.0 gracefully for malformed/absent *model* output, which remains a real score.)
   - Task versions bumped: **T02 1.0 → 1.1**, **T09 1.0 → 1.1**. ALL `edge_bare` reps are re-run
     under harness **0.1.2** for a homogeneous baseline, superseding every 0.1.0/0.1.1 record
     (including the 0.1.2 T01 rep-1 smoke run produced on a dirty tree); the spine's append-only
     history preserves the superseded records.
8. **T01 answer key listed as model input (harness 0.1.2 → 0.1.3).** `launch_edge` listed every
   file in the task's `fixtures/` dir as an input path, and T01's `fixtures/` contains
   `expected.json` — the very key `match.py` grades against — while the model holds `Read`
   permission. The five 0.1.2 T01 `edge_bare` 1.0s are therefore unverifiable (the wrapper itself
   sanctioned reading the key) and are superseded. Fix: the fixture listing now excludes
   `expected.json` (grading keys are never model inputs; harness **0.1.3**), and the new
   `scripts/make_orch_prompt.py` — which assembles the blind orchestrator-arm wrapper with fixture
   *contents* inlined — applies the same exclusion (plus `instance.json` for T09). **T01
   `edge_bare` reps 1–5 re-run under 0.1.3.** T02 (`context.md` only) and T09 (generated
   `fixtures/problem.md` only) never exposed grading material; their 0.1.2 records stand.
9. **T01 edge_bare floor is a genuine 0.0/0.0 (harness 0.1.3) — and `schema_valid` is
   structurally unreachable.** With the answer key excluded, the bare model produces well-formed,
   sensible intake JSON but in *its own* nested convention (`patient: {last_name, first_name}`,
   `referring_provider: {…}`, `referral_reason: {…}` with a standard ICD-10 code like `I10`), while
   the graders demand the local *flat* convention (`patient_name`, `referring_provider` as a string,
   `referral_reason_code`) and a local reason-code enum (`HTN-UNCTRL`, …). Both live only in grader
   material (`intake.schema.json` / `expected.json`), so all five reps score `schema_valid 0.0` and
   `field_accuracy 0.0` — a real measurement (validate.py runs and returns 0.0 on
   "Additional properties are not allowed"), not an artifact. This is the correct uninflated
   high-transfer floor; the 0.1.2 1.0s were answer-key leakage.
   - **`schema_valid` is unreachable for every *compliant* arm, by construction.** The reason-code
     enum exists only in `intake.schema.json`/`expected.json`, and the distillation protocol
     (EXPERIMENT.md §3, `prompts/skill_distillation.md`) lets the skill author see only its own
     successful **A1** traces — never grader material — so no compliant skill can carry the codes,
     and no compliant arm can satisfy the enum. `schema_valid` is therefore expected ≈ 0 in **all**
     arms (bare and skill alike) and cannot discriminate transfer.
   - **`field_accuracy` is T01's discriminating metric.** It rewards matching the flat field
     naming/values the conventions skill *can* legitimately teach from A1 traces. `schema_valid` is
     retained for completeness but read as ≈ 0 everywhere by design, not as a transfer signal.
10. **A1 (`orch_bare`) executes headless through the edge launch path (harness 0.1.3 → 0.1.4).**
    A1 is now driven by `harness/run.py` via `claude -p` through the *same* `launch_edge` path as
    the A3 edge arm — same wrapper, same `--allowedTools Read,Write`, same `--max-turns`, same
    deterministic graders, same run-record assembly — with the arm resolving *only* the `--model`
    flag: `edge_*` → `models.edge` (`claude-opus-4-8`), `orch_*` → `models.orchestrator`. So A1 and
    A3 differ by exactly one variable, the orchestrator vs. edge model string. This **supersedes the
    manual web-paste recipe in `bootstrap/EDGE_CLI_RUNBOOK.md §5`** for A1. The orchestrator is
    pinned for this batch to **`claude-fable-5`** (confirmed by probing `claude -p "…" --model
    claude-fable-5 --output-format json`), so the existing model-mismatch abort now protects orch
    runs too. `scripts/make_orch_prompt.py` is retained as the web-surface contingency (blind
    fixture-content inlining) should headless execution be unavailable.
11. **T02 run-records are silently dropped by a spine event_id collision (harness defect, surfaced
    during the A1 `orch_bare` batch; harness 0.1.4).** `run.py` writes its run-record with
    `event_id = run_id`. T02 is the only task whose *measured* model itself writes to the spine
    (it records the pre-registration claim to `dev/skill-transfer-tasks` via `MCP_Assist`), and the
    `mcp-assist-memory` skill leads the model to use the handed-in `run_id` as *its* write's
    `event_id`. The spine enforces **global** event_id idempotency, so the model's in-run write
    consumes `event_id=<run_id>` first and the harness's post-run `memory_save` is deduped to the
    model's record and never stored. Compounding this, `SpineClient.call()` does **not** inspect
    the tool response's `isError`, so `write_with_journal` marks the journal `acked` and `run.py`
    exits 0 — a *phantom* acknowledgement (the expected exit-3 replay warning never fires).
    Evidence: `memory_history run/T02/orch_bare/1` is empty; re-saving the exact journaled record
    with `event_id==run_id` returns the model's `task-t02/prereg-commit/<run_id>` claim, while
    re-saving with a fresh uuid4 persists it (revision 1). Confirmed for all 5 T02 `orch_bare`
    reps; the same class of failure already hit the pre-registered **A3 `edge_bare` T02** set
    (only reps 1,2,4 persisted). **Consequence:** T02 `orch_bare` reps 2-5 have no acknowledged
    spine record and are INVALID per SPINE.md; rep 1 was manually recovered during diagnosis with
    a fresh event_id (a deviation from the pinned path, flagged for re-run). T01 (5/5) and T09
    (10/10) are unaffected and valid. **Decision pending (experiment owner):** whether to patch the
    harness (distinct valid-uuid event_id for the run-record + surface `isError` on writes; bump
    HARNESS_VERSION) and re-run T02 for A1 — and whether A3's T02 set must be re-collected for
    parity. No further harness change or re-run made until sanctioned.
12. **Resolution of #11 (harness 0.1.4 → 0.1.5).** Two fail-closed fixes: (a) `run.py` now writes
    its run-record under `event_id = uuid5(NAMESPACE_URL, "run-record:"+run_id)` — a valid,
    collision-free, replay-stable token distinct from the `run_id` the measured model reuses for
    its own spine writes; (b) `SpineClient.call()` raises `SpineUnavailable` on a tool response with
    `isError`, so a rejected/deduped write can no longer be marked `acked` (it stays pending and
    trips the exit-3 replay warning). Per the owner's decision, **T02 is re-collected for BOTH
    arms** under 0.1.5: `orch_bare` (A1, `claude-fable-5`) reps 1-5 and `edge_bare` (A3,
    `claude-opus-4-8`) reps 1-5 — superseding the pre-0.1.5 T02 records (A3's incomplete 3/5 set
    and the manually-recovered A1 rep 1). T01 and T09 records (0.1.4) are unaffected and retained.
13. **Second latent defect exposed by #12's isError fix: `artifact_put` was never uploading
    (harness 0.1.5 → 0.1.6).** The harness called `artifact_put` with `{"data": blob}`, but the
    spine tool's argument is `content_base64` (and it takes no `event_id`). Before #12 this errored
    silently — `call()` returned the error text, `isinstance(res, dict)` was False, so
    `output_artifact_sha256` was recorded `null` on *every* run to date (all arms/tasks). Once
    `call()` began raising on `isError`, that failure surfaced: the run's raw output blob was never
    stored, and the `except` branch journaled a permanently-invalid `artifact_put` replay entry
    (wrong arg + non-uuid `event_id`) that tripped the exit-3 replay gate. Fix: call
    `artifact_put` with `content_base64`, read `sha256` from the result, and make the spine-down
    fallback best-effort (record the local content sha256 — identical to the server's address, blob
    kept on disk at `out_path` — and do NOT journal it, since artifact upload is supplementary
    provenance and must not gate the run-record's acknowledgement). Verified: `artifact_put` now
    returns a sha256 and `artifact_get` retrieves the blob. Consequence for the T02 re-collection:
    `output_artifact_sha256` is now a real, retrievable content address for both re-run T02 arms
    (parity preserved between the compared A1/A3 T02 cells); the retained T01/T09 0.1.4 records keep
    their historical `null` (provenance-only field, not a scored metric).
14. **Third integrity gap: an API-errored launch was scored as a 0.0 (harness 0.1.6, guard added).**
    During the T02 re-collection, edge_bare reps 2-5 (`claude-opus-4-8`) hit HTTP 429 rate limits:
    the CLI returned `is_error=true, api_error_status=429` in <1-5s with 1-3 turns, the model did no
    work, and the empty output graded as `postcondition=0.0`. The launch path never inspected the
    CLI result's `is_error`/`api_error_status`, so these non-runs were recorded as `completed`
    measurements. Fix: `run.py` now aborts (sys.exit, no record, no score — same discipline as a
    grader crash) when the CLI result carries `is_error` or `api_error_status`. This does not change
    what any *successful* run records, so it is a same-version (0.1.6) integrity addition; the 5
    genuine orch_bare reps and the 1 genuine edge_bare rep (multi-minute, 20-30 turns, is_error
    false) already collected under 0.1.6 stand. edge_bare reps 2-5 are INVALID and re-run (spaced,
    with cooldown) to avoid the rate limit.

## Outcome

**skill-transfer-v1 concludes null by precondition.** The measured baselines (A1 orchestrator =
`claude-fable-5` vs A3 edge = `claude-opus-4-8`, 20 acknowledged reps per arm) never produced the
transfer-shaped gap the pre-registered hypothesis requires:

- **T01** (intake-conventions) — **0.0 / 0.0 on both arms** (schema_valid / field_accuracy): a
  double floor. Neither arm clears the local flat-schema + reason-code enum that lives only in
  grader material (see #9), so there are *no successful A1 traces* to distill — the distillation
  protocol (EXPERIMENT.md §3) therefore permits no skill to be authored for T01.
- **T02** (record-a-verifiable-claim) — **orchestrator 0.80 vs edge 1.0** (mean postcondition,
  n=5 each). The edge model sits *above* the orchestrator, so the gap_closure denominator
  (edge − orchestrator headroom) is **negative**: there is no orchestrator advantage for a skill
  to transfer downward. (The pre-registered A3 floor of 0.867 was an artifact of the pre-0.1.6
  event_id-collision bug that persisted only 3/5 edge records; the clean re-collection is 1.0.)
- **T09** (constraint-solver control) — **1.0 / 1.0 on both arms**: the control is saturated, so
  its prediction is trivially satisfied and carries no discriminating signal.

Across all three tasks the arms are either tied at a floor/ceiling or the edge model already leads;
none exhibits the "orchestrator succeeds where the edge model fails" precondition. **The
pre-registered hypothesis was never reached and remains open** — it needs a task pairing that
exposes a genuine orchestrator→edge capability gap.

**Reusable assets (carried forward, not retrofitted):**
- the **v0.1.6 harness** — arm-parity launch path, three fail-closed integrity fixes (event_id
  collision, `isError` surfacing, `artifact_put` upload) and the API-error abort;
- **fable-5's two perfect T02 traces** (`run/T02/orch_bare/2` = 09d9df3a, `.../5` = 73210209,
  postcondition 1.0) — distillation-ready if a future pairing needs them;
- the **pinned but dormant referee** `gpt-5.5-2026-04-23` (no referee cells were ever run);
- a possible **v2** — a haiku-class edge model and/or a T01b "conventions-handbook" task that puts
  the naming/enum conventions in-scope — but only as a **fresh pre-registration, never a retrofit**
  of skill-transfer-v1.

## Cross-family audit of the v1 report (post-hoc, no findings retrofitted)

On **2026-07-02** an adversarial, evidence-only audit of the standalone v1 final report was run by a
different model family — **GPT-5.5 (`gpt-5.5-2026-04-23`, temperature 0)** — because the report was
authored by `claude-fable-5`, which was also the measured orchestrator arm (disclosed conflict of
interest). The auditor credited only ground truth (this file, EXPERIMENT.md, the 40 baseline records
read back live from the spine, git log, harness-version history); the report was not allowed to
corroborate itself. Fail-closed structured output covering all 39 extracted claims + H1–H7 validated
on the first attempt. Full review: **`reviews/gpt55-audit-v1.md`** (raw JSON `reviews/gpt55-audit-v1.json`).
Verdicts: **16 SUPPORTED / 18 OVERCLAIMED / 0 UNSUPPORTED / 5 UNVERIFIABLE-FROM-EVIDENCE.**
Harshest verdict: the core measured result (no fable-5→opus-4-8 gap; T01 double-floor, T02 inversion,
T09 double-ceiling) is **SUPPORTED**, but the report's headline *narrative* is **OVERCLAIMED** — the
T02 inversion's attribution to a "provenance judgment style" (which sha was pinned), its "17–28
tool-use turns", and the benchmark-rank generalization are narrated, not decidable from the run records;
and the auditor flags that T01 and T09 cross-arm comparisons mix harness versions (edge vs orch) while
only T02 is homogeneous (both 0.1.6), with small n (5/5/10) and no statistical test.
