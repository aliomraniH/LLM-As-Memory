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
