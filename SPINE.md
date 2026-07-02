# Spine integration (MCP_Assist)

Namespace: `dev/skill-transfer` (throwaway-style, isolated from production namespaces by
convention — remember isolation is soft). All writes carry a stable `event_id` (UUID) for
exactly-once semantics under retry/replay.

## Key scheme

```
run/<task_id>/<arm>/<rep>            kind=claim   — one run record per execution (schema below)
skillrel/<skill_name>/<version>      kind=claim   — a skill release: sha256 + repo provenance
task/<task_id>/<version>             kind=knowledge — task definition hash
referee/rubric/<version>             kind=knowledge — rubric artifact sha256
analysis/<date>                      kind=note    — interim findings
decision/<topic>                     kind=decision — design choices and rationale
```

Run outputs larger than ~2k tokens go to `artifact_put`; the run record references the returned
sha256 rather than embedding content.

## Run records are claims with provenance

Each run record is written with `kind="claim"` and a `meta` envelope carrying `repo`
(`aliomraniH/skill-transfer-experiment`), the `branch`/`repo_sha` the skill tree was synced from,
and `source_surface` (`claude-code-local` | `claude-code-web`). This makes every result
machine-checkable: `coord_reconcile` can later verify the recorded skill tree still corresponds to
a real commit, and a record whose provenance no longer resolves gets flagged instead of silently
trusted. The record body must validate against `schemas/run_record.schema.json` — fail closed:
an invalid record is not written, the run is marked invalid and re-executed.

## Freshness gate (before any scored run on the edge)

1. Compute local skill-tree hash: `git rev-parse HEAD` + per-skill `sha256sum` of each SKILL.md.
2. `memory_get` the latest `skillrel/*` entries for the skills in this arm.
3. `coord_reconcile` the namespace; require verdicts `current` on those release claims.
4. Any mismatch or `stale`/`unverifiable` verdict → abort the run, `git pull`, retry once, else
   surface to operator. Never run an arm on an unverified skill tree.

This is the selection-pressure loop: skill releases are claims about repo state, reconcile is the
staleness detector, and gap-closure scores are the fitness signal that drives the next revision.

## Buffered writes (spine outage tolerance)

The edge harness appends every intended spine write to a local journal
(`.runs/journal.ndjson`, one JSON object per line, including its `event_id`) *before* attempting
the network write. On `Session terminated` (-32600) or connector absence, the run continues; a
replay step re-submits journal entries until each is acknowledged. Same-`event_id` semantics make
replay safe. Distinguish the two known failure modes: `-32600` = wake/restart the Replit instance;
`No approval received` = client-side approval gate, fix in the local Claude Code permissions
(`mcp__MCP_Assist__*` allow rules), not on the server.

## Sessions

Each experimental batch opens a spine session (`session_create`, meta: date, operator, harness
version); each run appends a `session_append_event` with its `run_id`. `seq` orders events within
the batch only — cross-batch ordering comes from timestamps in the run records.
