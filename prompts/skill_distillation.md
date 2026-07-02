# Skill distillation prompt (given to the orchestrator, per EXPERIMENT.md §3)

You are distilling a skill from your own successful task traces. Attached are {n} successful runs
of task {task_id} (your own outputs with tool calls). Author a single SKILL.md that transfers the
procedure and conventions you used to a smaller model.

Hard rules — violating any of these invalidates every run that uses the skill:

1. LEAKAGE: no task-instance answers, fixture values, or expected-output content may appear in
   the skill. Procedures and conventions only. Your output will be grep-audited against the
   task's `leakage_forbidden_strings`; do not paraphrase-around fixture values either.
2. STRUCTURE: use `skills/_template/SKILL.md` exactly — frontmatter `name`, pushy `description`,
   `x_experiment` provenance block (fill `distilled_from`, `authored_by_model`,
   `target_task_ids`; leave `leakage_reviewed: false`), then Procedure / Conventions /
   Failure modes / Hard leakage rule sections.
3. [MANDATORY] markers: mark ONLY steps whose omission should count as non-compliance in the
   measurement. The Stop hook counts these; a step you mark must be objectively checkable in a
   transcript. Instruct the executor to emit `[MANDATORY-DONE:<step_number>]` on a line by itself
   immediately after completing each such step — this is how compliance is counted.
4. Rationale over examples: state each convention as a rule plus a one-line why. Do not include
   worked examples derived from fixtures.
5. Write for a smaller model: short imperative steps, no reliance on implicit context.
