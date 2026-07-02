- arm_runner.md — wrapper for every scored run; assembled by harness/run.py by substituting the
  {braced} variables. Identical bytes across all four arms of a task; arm differences live only in
  launch flags and skill-tree presence. It must never mention the experiment, arms, skills, other
  models, or grading.
- referee_call.md — assembly recipe for referee judgments (blinding + position swap rules inside).
- skill_distillation.md — given to the orchestrator when authoring a skill from its own traces.
- failure_analysis.md — given between skill revisions to classify A4 failures.
