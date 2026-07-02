# KICKOFF PROMPT — paste this into Claude Code Web to start the project

You are initializing the **skill-transfer-experiment** repository. The scaffold in this directory
is the pre-registered design; your job is to turn it into a runnable experiment. Read, in order:
`README.md`, `EXPERIMENT.md`, `SPINE.md`, `bootstrap/context.json` (machine-readable facts —
treat it as ground truth for names, models, namespaces), and `bootstrap/PROMPTS_AND_SETTINGS.md`
(the exact artifacts you must produce).

## Your mission, in phases

**Phase 0 — Repo init.**
Create the GitHub repo `skill-transfer-experiment` under the owner given in context.json. Commit
the scaffold as-is on `main` with message `pre-registration: experiment design v1`. This commit is
the pre-registration snapshot — nothing in EXPERIMENT.md §6's pre-registered set may change after
it without a documented deviation in `ANALYSIS.md`. Enable branch protection on `main` if the plan
allows; otherwise note it in ANALYSIS.md.

**Phase 1 — Make the design executable.**
Produce every item in `bootstrap/PROMPTS_AND_SETTINGS.md` §Artifacts-to-prepare: the three hook
scripts, deterministic graders and synthetic fixtures for T01/T02/T09, the harness runner, and the
arm/referee prompt files. Constraints that override anything you might prefer:

- All fixtures are synthetic. No PHI, nothing patient-shaped enough to be mistaken for real data.
- Graders are deterministic — no LLM calls inside `graders/`.
- After writing T01 fixtures, populate `leakage_forbidden_strings` in its task.yaml from the
  expected-output values, and implement the grep-audit as a pre-commit check on `skills/`.
- Hooks are the enforcement tier: fail closed (nonzero exit blocks), never warn-and-continue.
- Do not author any capability skill yet (no `intake-extraction-conventions`). Skills are distilled
  from orchestrator traces AFTER baseline arms run — authoring one now inverts the protocol.

**Phase 2 — Spine seeding.**
If the MCP_Assist connector is available on this surface: run `coord_health` on the namespace from
context.json, `session_create` a bootstrap session, and write `decision/repo-initialized`
(kind=decision) plus one `skillrel/`-scheme dry-run entry with full provenance meta, then
`coord_reconcile` and confirm the verdict resolves. If the connector is NOT available here (Claude
Code Web sandboxes often lack custom MCP connectors), do not fake it: write the seeding steps to
`bootstrap/SPINE_SEED_CHECKLIST.md` for the local machine to execute, and say plainly that seeding
was deferred.

**Phase 3 — Handoff.**
Open a PR (or commit) titled `phase-1: executable harness` and produce `HANDOFF.md` at repo root:
what was built, what was deferred, exact commands the edge machine runs next (clone, skill
symlink, settings install, freshness gate, first `edge_bare` rep of T01). If the spine is
reachable, mirror HANDOFF.md via `handoff_save` under key `bootstrap` in the experiment namespace.

## Ground rules while you work

- Pin, never float: every model string you write into configs comes from context.json verbatim.
- Bare arms and skill arms may differ ONLY in skill-tree presence.
- If any instruction here conflicts with EXPERIMENT.md, EXPERIMENT.md wins; log the conflict in
  ANALYSIS.md rather than silently resolving it.
- When something is ambiguous, prefer the interpretation that keeps runs auditable (recorded,
  hashed, reconcilable) over the one that is merely convenient.

Begin with Phase 0. State your plan for each phase in one short paragraph before executing it.
