# Harness design

The harness is a thin runner, not a framework. Per run:

1. Resolve arm config (model, skills on/off) from config.yaml.
2. Freshness gate (SPINE.md) for *_skill arms on the edge.
3. Launch the model surface:
   - edge arms: `claude -p` (headless Claude Code) with `--model claude-opus-4-8`, settings dir
     pointing at the experiment's `.claude/` (hooks installed), skill tree present or absent per arm.
   - orchestrator arms: run on Claude Code Web / API with the recorded frontier model; skill
     presence toggled the same way.
4. Capture full output; `artifact_put`; run deterministic graders from the task dir.
5. Queue referee cells (pairwise, blinded, both positions) if the task declares referee dimensions.
6. Assemble run record -> validate against schemas/run_record.schema.json -> journal -> spine write
   (buffered replay on failure, same event_id).

Invariants:
- model_id_observed from the API response must equal model_id_pinned or the run aborts.
- A run without an acknowledged spine record does not count; re-run it.
- Bare arms and skill arms differ ONLY in skill-tree presence. Same tools, same settings, same
  prompt, same fixtures.
- Referee batching happens after all cells of a task complete, so blinding pools are full.
