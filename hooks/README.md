# Edge hooks (the deterministic tier)

Skills carry procedure (probabilistic compliance); these hooks carry gates (deterministic).
Three scripts to implement (referenced from settings.example.json):

- freshness_gate.sh   (SessionStart) — compare local skill hashes + repo HEAD against the latest
  skillrel/* claims in the spine; nonzero exit blocks the session for *_skill scored runs.
- namespace_guard.py  (PreToolUse on memory_save) — reject writes whose namespace is not
  dev/skill-transfer* ; reject any payload matching PHI-shaped patterns (defense in depth even
  though all fixtures are synthetic).
- compliance_counter.py (Stop) — parse the transcript for [MANDATORY] step execution vs. the
  skill's declared count; emit {skill_steps_total, skill_steps_executed, hook_gate_triggers} for
  the run record. This is the measurement of prompt-tier compliance the experiment wants.
