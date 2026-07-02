# Task definition schema

Each task is a directory `tasks/Tnn-slug/` containing:

```
task.yaml        — definition (below)
fixtures/        — inputs the run receives (synthetic only, no PHI, no real patient-shaped data)
graders/         — deterministic graders: executable scripts and/or expected-output files
rubric_addendum.md (optional) — task-specific correctness anchors for the referee
```

## task.yaml fields

```yaml
task_id: T01              # matches directory prefix
version: "1.0"            # bump on any change to prompt, fixtures, or graders
title: one line
category: procedural | mixed | reasoning-control
expected_transfer: high | partial | none   # PRE-REGISTERED before first scored run
prompt: |
  The exact prompt given to the model. Identical across all four arms.
skills_in_scope:          # which skills the *_skill arms load for this task
  - extraction-conventions
tools_in_scope:           # identical across arms; MCP_Assist always included if used at all
  - MCP_Assist
deterministic_graders:
  - name: schema_valid
    cmd: "python graders/validate.py {output_path}"   # exit 0/1 + numeric score on stdout
  - name: field_match
    cmd: "python graders/match.py {output_path} fixtures/expected.json"
referee_dimensions: []    # empty when deterministic tier fully decides the task
reps: 5
max_output_tokens: 4000   # cost control
leakage_forbidden_strings: []  # fixture strings that must never appear in any skill file
```

Rules:
- The prompt never mentions skills, arms, or the experiment.
- Grader scripts are deterministic (no LLM calls) and versioned with the task.
- `expected_transfer` for `reasoning-control` tasks must be `none` — that's the point of them.
