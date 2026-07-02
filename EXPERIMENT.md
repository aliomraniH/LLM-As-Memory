# Experiment design

## 1. Arms (four, not two)

| Arm | Model | Skills |
|---|---|---|
| A1 `orch_bare`  | orchestrator (frontier, recorded per run) | none |
| A2 `orch_skill` | orchestrator | current skill tree |
| A3 `edge_bare`  | claude-opus-4-8 | none |
| A4 `edge_skill` | claude-opus-4-8 | current skill tree |

Interpretation matrix:

- A4 ≫ A3, A2 ≈ A1 → genuine distillation: skills encode orchestrator-specific knowledge the edge
  model lacked. The headline result.
- A4 ≫ A3 **and** A2 ≫ A1 → skills encode generally useful procedure (still valuable, different claim).
- A4 ≈ A3 → skill failed to transfer; inspect compliance data from hooks before concluding the
  knowledge is non-textual.
- A4 > A2 or A4 > A1 → over-closure; check for grader leakage or task overfitting in the skill.

"Bare" arms still get the task prompt and tool access — only the skill tree is absent. Keep
everything else (tools, MCP config, temperature/effort settings) identical within a task.

## 2. Task portfolio

Tasks live in `tasks/`, one directory each, defined by `task.yaml` (see `tasks/TASK_SCHEMA.md`).
Deliberate spread across the transfer spectrum:

- **T01–T04 procedural/knowledge (transfer expected):** structured extraction with domain
  conventions, multi-step MCP_Assist workflows (claim + provenance + reconcile), spec-conformant
  output formats, tool-sequence orchestration against fixtures.
- **T05–T08 mixed (partial transfer expected):** tasks needing both procedure and judgment.
- **T09–T10 fluid-reasoning controls (transfer NOT expected):** novel multi-hop reasoning with no
  stable procedure to encode. These are pre-registered predicted failures — write the prediction in
  the task.yaml `expected_transfer` field before running anything. A control that fails on schedule
  is what makes the positive results credible.

Minimum viable: 4 tasks (2 procedural, 1 mixed, 1 control). Reps: ≥5 per cell, 10 preferred.
Cost check before committing: `tasks × 4 arms × reps × mean tokens/run`.

## 3. Skill authorship protocol (the distillation loop)

1. Orchestrator runs the task bare (A1), succeeding traces are collected.
2. Orchestrator extracts the procedure from its own traces and compresses it into a SKILL.md
   (template in `skills/_template/`). No task-instance answers may appear in the skill — procedures
   and conventions only (leakage rule, checked at review).
3. Skill is committed; content hash recorded; edge syncs; A3/A4 run.
4. Failure analysis on A4 feeds skill revision v2. Each revision is a new point on the
   gap-closure-per-revision curve. Cap at 3 revisions per task to bound cost.

## 4. Scoring

**Tier 1 — deterministic (preferred, use whenever the task allows):** JSON-schema validation,
exact/set match against fixtures, executable test suites, spine-verifiable postconditions (did the
run produce a `claim` that `coord_reconcile` resolves `current`?). Deterministic graders live in
the task directory and are versioned with it.

**Tier 2 — referee (open-ended cells only):** GPT-5.5 per `referee/REFEREE.md`. Blind, position-
swapped, fail-closed structured output, agreement-sampled. The referee never decides tasks that a
deterministic grader can decide.

## 5. Threats to validity (and controls)

- **Self-preference:** cross-family referee; orchestrator never grades its own descendants.
- **Position/verbosity bias in referee:** position swap on every pairwise judgment; rubric scores
  substance dimensions, never length or polish.
- **Skill→grader leakage:** author and grader reviewed separately; skills may not reference
  fixture content; grep-audit skills against fixture strings before each revision lands.
- **Silent model drift:** model IDs pinned in harness config AND recorded from the API response in
  every run record; a mismatch aborts the run.
- **Skill staleness on edge:** freshness gate (SPINE.md) — runs refuse to start if the local skill
  hash disagrees with the repo HEAD recorded in the spine.
- **Spine outages mid-run:** local write buffer with idempotent `event_id` replay; a run without a
  confirmed run record is invalid and re-run.
- **Compliance vs. capability confound:** the Stop hook logs whether the skill's mandatory steps
  were actually executed; separate "didn't follow the skill" failures from "followed it and still
  failed" in analysis. This doubles as the probabilistic-compliance measurement we want anyway.

## 6. Pre-registration

Before the first scored run, commit: task list, expected_transfer predictions, rep counts, gap-
closure formula, and referee rubric hashes. Analysis deviations get documented in ANALYSIS.md, not
silently applied.
