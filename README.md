# skill-transfer-experiment

Can versioned skill files (SKILL.md) transfer capability from a frontier orchestrator model to a
smaller edge model — measurably, with provenance, verified through a coordination spine?

**Hypothesis.** Skills authored by the orchestrator model (distilled from its own successful task
traces) close a meaningful fraction of the performance gap between the edge model (Claude Opus 4.8,
local via Claude Code) and the orchestrator model on procedural/knowledge tasks — and close ~none of
the gap on fluid-reasoning control tasks.

**Primary metric.** Gap closure per task:

```
gap_closure = (score(edge+skills) − score(edge_bare)) / (score(orch_bare) − score(edge_bare))
```

Reported per task with confidence intervals over ≥5 reps per cell. Secondary: learning curve of
gap closure across skill revisions (v1, v2, …).

## Roles

| Role | Model | Surface | Notes |
|---|---|---|---|
| Orchestrator / skill author | frontier Anthropic model (record exact ID per run) | Claude web + Claude Code Web | Authors skills from its own traces; manages this repo |
| Edge agent | `claude-opus-4-8` (pinned) | Claude Code, local machine | Runs tasks per arm; syncs skills via `git pull` |
| Referee | `gpt-5.5` via OpenAI API (pin dated snapshot, not `chat-latest`) | harness script | Cross-family judge for open-ended cells only |
| Spine | MCP_Assist (`mcp-assist-memory`) | both surfaces | Run records, skill-freshness verification, artifacts |

Model availability is volatile right now — record the exact orchestrator model string in every run
record and treat the strong-arm slot as swappable. Results remain interpretable as long as every
record pins the model that produced it.

## Layout

```
EXPERIMENT.md            Design: arms, tasks, metrics, threats to validity
SPINE.md                 Namespace scheme, run-record keys, freshness verification
tasks/                   Task definitions (one dir per task: task.yaml + fixtures + graders)
skills/                  The evolving skill library (synced to edge ~/.claude/skills/)
skills/_template/        Canonical SKILL.md template with provenance frontmatter
referee/                 Referee protocol, rubric, fail-closed output schema
schemas/run_record.schema.json   Spine run-record contract
harness/                 Runner design + arm-matrix config
hooks/                   Claude Code hooks for the edge machine (enforcement tier)
```

## Quickstart (edge machine)

1. `git clone` this repo; symlink or copy `skills/` → `~/.claude/skills/` (excluding `_template`).
2. Install `hooks/settings.example.json` → `.claude/settings.json` (adjust paths).
3. Configure MCP_Assist connector; verify `coord_health` on namespace `dev/skill-transfer`.
4. Run freshness check (SPINE.md §Freshness) — refuse to run arms on a stale skill tree.
5. Execute arms per `harness/config.example.yaml`; every run writes a run record (buffered +
   idempotent replay if the spine connector drops).

## Ground rules

- No PHI anywhere in this repo, in task fixtures, or in spine writes. Synthetic data only.
- Skills carry procedure (probabilistic); hooks carry gates (deterministic). Never rely on a
  SKILL.md sentence for anything that must always happen.
- Every run record pins: model ID, skill content hashes, harness version, task version.
