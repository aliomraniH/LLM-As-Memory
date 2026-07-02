# PROMPTS_AND_SETTINGS — artifacts Claude Code Web must prepare

This file enumerates every prompt and settings artifact the experiment needs, with the invariants
each must satisfy. context.json supplies all concrete values (models, repo, namespace); nothing in
this file should be edited to add values — edit context.json instead.

## Artifacts to prepare

### 1. Run prompts (`prompts/`)

- `prompts/arm_runner.md` — the wrapper prompt for every scored run. Contents: the task's
  `prompt` field verbatim, the fixture paths, the output contract (where to write, token cap).
  MUST NOT mention: the experiment, arms, skills, other models, or grading. Identical bytes across
  all four arms of a task — arm differences live in launch flags and skill-tree presence only.
- `prompts/referee_call.md` — assembled per judgment by the harness: `referee/rubric.md` + the
  task's `rubric_addendum.md` (if any) + blinded Response A/B + the JSON-only output instruction
  referencing `referee/referee_output.schema.json`. Include the position-swapped variant
  assembly rule (same content, A/B payloads exchanged).
- `prompts/skill_distillation.md` — the prompt the orchestrator receives when authoring a skill
  from its own successful traces (EXPERIMENT.md §3). Must embed the leakage rule (no fixture or
  answer content), require the `skills/_template/SKILL.md` structure including `x_experiment`
  frontmatter, and require `[MANDATORY]` markers only on steps whose omission should count as
  non-compliance.
- `prompts/failure_analysis.md` — the prompt for analyzing A4 failures between skill revisions:
  classify each failure as {didn't-follow-skill | followed-and-failed | grader-issue}, using the
  compliance counts from run records, before proposing skill edits.

### 2. Settings (`settings/` and `.claude/`)

- `.claude/settings.json` for the edge machine — from `hooks/settings.example.json`, with hook
  script paths made real. Include the `mcp__MCP_Assist__*` allow rules exactly as listed
  (permissionMode does not auto-approve MCP tools).
- `.claude/hooks/freshness_gate.sh`, `.claude/hooks/namespace_guard.py`,
  `.claude/hooks/compliance_counter.py` — behavior specified in `hooks/README.md`. Fail closed.
- `harness/config.yaml` — instantiated from `harness/config.example.yaml` with context.json
  values. The referee model MUST be a dated snapshot string; if only a floating alias is known at
  prep time, leave the field as `"TODO-pin-snapshot"` and make the harness refuse to run referee
  cells until it is pinned.
- `settings/openai_referee.env.example` — env var names for the referee API key and base URL.
  Never commit real keys; add the real filename to `.gitignore`.

### 3. Graders and fixtures (`tasks/*/`)

- T01: three synthetic referral documents (`fixtures/doc{1,2,3}.md`), `fixtures/expected.json`,
  `graders/validate.py` (JSON Schema check), `graders/match.py` (field-level accuracy in [0,1]).
- T02: `fixtures/context.md` naming a real PR/merge in the repo from context.json (use the
  pre-registration commit itself once it exists), `graders/check_spine.py` (reads back the entry:
  kind=claim, meta carries repo+pr/branch+sha, latest reconcile verdict is `current`).
- T09: `graders/generate.py` (fresh solvable instance per rep, seeded by run_id),
  `graders/verify.py` (checks a proposed solution against the generated instance's constraints).

### 4. Harness runner (`harness/run.py`)

Implements HARNESS.md steps 1–6 exactly: arm resolution → freshness gate → surface launch
(`claude -p --model <edge model>` for edge arms) → artifact_put + deterministic graders → referee
queue → run-record assembly, schema validation (fail closed), journal-then-write with idempotent
`event_id` replay. Abort statuses come from `schemas/run_record.schema.json`'s `status` enum.

## Invariants checklist (verify before declaring Phase 1 done)

- [ ] arm_runner.md contains zero experiment-revealing content
- [ ] every model string in configs matches context.json byte-for-byte
- [ ] leakage_forbidden_strings populated for T01; grep-audit wired as pre-commit on skills/
- [ ] hooks exit nonzero on violation (tested with a deliberate violation each)
- [ ] a run record that fails schema validation is never written to the spine
- [ ] journal replay with a duplicated event_id produces exactly one spine entry
- [ ] no real API keys, tokens, or PHI-shaped strings anywhere in the repo
