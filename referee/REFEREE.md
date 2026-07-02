# Referee protocol

The referee exists to remove self-preference from an Anthropic-vs-Anthropic comparison: neither
the orchestrator nor the edge model may grade outputs in this experiment. The referee is a
**cross-family** frontier model called via API from the harness.

- **Model:** `gpt-5.5` (OpenAI API, generally available since 2026-04). Pin an explicit dated
  snapshot string in `harness/config.example.yaml`; never use a floating alias like `chat-latest`
  — a silent referee upgrade mid-experiment invalidates cross-batch comparability.
- **Fallback / agreement family:** a third family (e.g. current Gemini frontier) used only for
  agreement sampling, and as primary if GPT-5.5 becomes unavailable (re-run all referee cells,
  never mix referees within a batch).

## Scope

The referee grades **only** cells that deterministic graders cannot decide (open-ended prose,
judgment-quality dimensions). If a task has any deterministic tier, that tier is authoritative for
what it measures; the referee supplements, never overrides.

## Blinding and bias controls

1. **Identity blinding.** Outputs are stripped of model names, arm labels, skill references, spine
   keys, and any signature phrasing markers the harness knows about. The referee sees "Response A"
   and "Response B" plus the task prompt and rubric — nothing else. It is never told which models
   are in the experiment.
2. **Position swap.** Every pairwise judgment runs twice with A/B order swapped. Both scores are
   recorded (`score`, `swapped_score`); a pair is `position_consistent` only if the preference
   direction survives the swap. Inconsistent pairs count as ties.
3. **Length discipline.** The rubric scores substance dimensions only (correctness, completeness
   against the task spec, procedural soundness). It explicitly instructs that length and polish are
   not merits. Harness additionally records output lengths so length–score correlation can be
   audited post hoc.
4. **No self-descendants rule.** The referee never evaluates skill files, never sees them, and is
   never asked "did this follow the skill" — compliance is measured by hooks, not the judge.

## Structured output, fail closed

The referee must respond with JSON only, validated against `referee_output.schema.json`
(same fail-closed pattern as the curator validator): parse → validate → on any failure, one
retry with the validation error appended → on second failure, the judgment is marked invalid and
the cell is re-queued. Invalid judgments are never coerced or hand-fixed.

## Pinning and provenance

The rubric (`rubric.md`, per-task addenda allowed) is content-hashed; the hash is stored in the
spine under `referee/rubric/<version>` and embedded in every run record. Full referee transcripts
(both positions) are stored via `artifact_put`; the run record carries `verdict_artifact_sha256`.
A referee judgment without a resolvable rubric hash and transcript artifact is treated as
unverifiable, mirroring `coord_reconcile` semantics.

## Agreement sampling (is the rubric real?)

On a random 20% of referee-graded cells, the second-family judge grades the same blinded pair
under the identical rubric. Compute inter-rater agreement (Cohen's kappa on preference direction)
per batch. Kappa < 0.4 means the rubric is under-specified — stop, tighten the rubric, re-run that
batch's referee cells. Low agreement is a rubric bug, not noise to average away.

## Temperature / effort

Referee calls run at the lowest available variance settings (temperature 0 or provider minimum,
fixed reasoning-effort setting), recorded in config. Judgment reproducibility is checked once per
batch by re-running one cell and confirming an identical verdict.
