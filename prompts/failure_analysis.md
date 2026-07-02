# A4 failure analysis prompt (run between skill revisions, per EXPERIMENT.md §3)

Attached: the edge_skill (A4) run records and graded outputs for task {task_id}, skill
{skill_name} v{skill_version}, plus each run's compliance counts
({skill_steps_executed}/{skill_steps_total}, hook_gate_triggers).

For every failed or under-scored run, classify the failure as exactly one of:

- didnt-follow-skill — compliance counts show mandatory steps skipped; the failure is plausibly
  attributable to the skipped step(s). Name the step(s).
- followed-and-failed — all mandatory steps executed, output still wrong. This is the signal that
  the skill's content (not compliance) is deficient. Name the deficient convention or missing
  failure-mode entry.
- grader-issue — the output is defensibly correct and the grader mis-scored it. Do not edit the
  skill for these; file the grader fix separately.

Rules:
- Use the compliance counts first; do not infer non-compliance from output quality alone.
- Only followed-and-failed cases justify skill edits. Propose edits as additions/sharpenings to
  the skill's "Failure modes and degradations" section or its Conventions — never as new
  [MANDATORY] steps unless omission of that exact step caused ≥2 independent failures.
- Respect the leakage rule in every proposed edit.
- Output: a table (run_id, class, evidence, proposed action), then the unified diff of the skill
  file if any edit is justified. Revision cap is 3 per task — say plainly if this failure set does
  not justify spending a revision.
