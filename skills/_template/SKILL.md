---
name: skill-name-here
description: >-
  What this skill does AND when to trigger it. Written pushy (skills undertrigger): list concrete
  user phrasings and contexts. This field is the only always-in-context surface — everything
  needed for triggering lives here, nothing needed for triggering lives below.
# --- experiment provenance (stripped on any production export) ---
x_experiment:
  skill_version: "1.0"
  distilled_from: "orchestrator traces, task T__, runs <run_ids>"
  authored_by_model: "<exact orchestrator model id>"
  target_task_ids: [T__]
  leakage_reviewed: false      # flip true only after grep-audit vs fixture strings
---

# Skill title

One-paragraph statement of intent: what capability this encodes, and the single most important
principle a model should hold while executing it.

## Procedure

Number the steps. Mark steps that MUST always occur with `[MANDATORY]` — the edge Stop hook counts
these markers against executed steps to produce the compliance measurement, so use the marker
honestly and sparingly. Everything else is guidance the model may adapt.

1. [MANDATORY] …
2. …
3. [MANDATORY] …

## Conventions

Domain conventions distilled from the orchestrator's traces: naming, formats, orderings, defaults.
State them as rules with a one-line rationale each — rationale is what lets a smaller model apply
the rule to unseen variants instead of pattern-matching the examples.

## Failure modes and degradations

What goes wrong when this procedure is misapplied, and the checkable symptom of each. This section
is where revision learning lands: every A4 failure analyzed in EXPERIMENT.md §3 should add or
sharpen an entry here.

## Hard leakage rule

No task-instance answers, fixture values, or expected-output content may appear anywhere in this
file. Procedures and conventions only. Violations invalidate every run that used this skill.
