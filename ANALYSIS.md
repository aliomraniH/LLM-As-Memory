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
