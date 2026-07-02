# EDGE CLI RUNBOOK — commands and prompts for Claude Code on the local machine

Run these after Claude Code Web has pushed `main` (head `3315f3b2…`). Two kinds of content
below: **shell commands** you run yourself, and **paste-able prompts** for interactive Claude
Code sessions. Scored runs never happen interactively — they go through `harness/run.py`
(headless `claude -p`) so arms stay identical.

---

## 1. One-time setup (shell)

```bash
# clone + deps
git clone https://github.com/aliomraniH/LLM-As-Memory.git && cd LLM-As-Memory
pip install -r requirements.txt

# enforcement tier: leakage audit on every commit
git config core.hooksPath .githooks

# skill sync (edge loads skills from ~/.claude/skills; _template excluded)
mkdir -p ~/.claude/skills
for d in skills/*/; do
  [ "$(basename "$d")" = "_template" ] || ln -sfn "$PWD/$d" ~/.claude/skills/"$(basename "$d")"
done
# (no capability skills exist yet — the loop is a no-op until the first distillation lands)

# MCP_Assist connector — the name must be exactly MCP_Assist or the allow rules
# (mcp__MCP_Assist__*) in .claude/settings.json won't match
claude mcp add --transport http MCP_Assist https://mcp-assist-memory.replit.app/mcp

# verify hooks + settings are picked up from the repo's .claude/
claude config list 2>/dev/null | head -5 || true
```

## 2. Verification pass (shell)

```bash
# spine reachable from this machine, namespace healthy
python3 - <<'EOF'
import sys; sys.path.insert(0, "harness")
from spine_client import SpineClient
c = SpineClient()
print("coord_health:", c.call("coord_health", {"namespace": "dev/skill-transfer"}))
print("reconcile:  ", c.call("coord_reconcile", {"namespace": "dev/skill-transfer"}))
EOF

# hooks fail closed (expect exit 2 on both)
echo '{"tool_input":{"namespace":"prod/x","key":"k","value":"v"}}' \
  | python3 .claude/hooks/namespace_guard.py; echo "guard exit=$? (want 2)"
SKILL_ARM=1 bash .claude/hooks/freshness_gate.sh; echo "gate exit=$? (want 2)"

# leakage audit clean
python3 scripts/leakage_audit.py && echo "leakage audit clean"
```

If the spine call fails: `-32600 Session terminated` → open the Replit instance to wake it,
retry; `No approval received` → your local allow rules, check `.claude/settings.json` is the
one from this repo; `HTTP 401 Unauthorized` → the server requires auth: copy
`settings/spine.env.example` to `settings/spine.env`, set `SPINE_AUTH_TOKEN`, and re-add the
connector with `--header "Authorization: Bearer <token>"`. Journaled writes replay
automatically on the next run.

## 3. Interactive session bootstrap (paste into `claude` in the repo root)

> Read bootstrap/EDGE_CLI_RUNBOOK.md and HANDOFF.md. Then, using the MCP_Assist tools:
> load the handoff under key `bootstrap` in namespace `dev/skill-transfer`, run `coord_health`
> and `coord_reconcile` on that namespace, and summarize: what state the experiment is in,
> which claims are current/stale/unverifiable, and what the next scored action is. Do not
> write anything to the spine in this session, and do not author any skill — baselines have
> not run yet.

Use this at the start of any working session to re-sync context across surfaces.

## 4. Baseline batch — edge_bare (shell)

Pre-registered reps: T01×5, T02×5, T09×10. Run them headless via the harness only:

```bash
# smoke: one rep first, inspect the record before batching
python3 harness/run.py --task T01 --arm edge_bare --rep 1

# then the full bare baseline
for r in 2 3 4 5;               do python3 harness/run.py --task T01 --arm edge_bare --rep $r; done
for r in 1 2 3 4 5;             do python3 harness/run.py --task T02 --arm edge_bare --rep $r; done
for r in 1 2 3 4 5 6 7 8 9 10;  do python3 harness/run.py --task T09 --arm edge_bare --rep $r; done

# every run must end acknowledged; if any printed the unacknowledged-writes warning:
python3 - <<'EOF'
import sys; sys.path.insert(0, "harness")
from spine_client import SpineClient
print("still pending:", SpineClient().replay())
EOF
```

A run without an acknowledged spine record does not count — re-run it (hard rule).

## 5. Orchestrator baselines (A1) — paste into Claude web / Claude Code Web, once per rep

> Record the exact model identifier you are running as first. Then complete the following
> task exactly as specified, writing your final answer and nothing else in a single fenced
> block at the end.
>
> [paste the `prompt:` field from tasks/<task>/task.yaml verbatim, plus the fixture file
> contents]

Grade the transcript locally with the same graders
(`python3 tasks/T01-structured-extraction/graders/validate.py <saved_output>` etc.), assemble
the run record by hand or with the prompt in §6, and write it under
`run/<task>/orch_bare/<rep>` with a fresh UUID `event_id`. Keep the wrapper identical across
reps; never mention arms, skills, or grading inside it.

## 6. Interactive record-keeping prompt (paste into `claude` after manual/orch runs)

> I have a completed orchestrator run to record. Here is the run data: [task_id, rep,
> model string reported by the surface, ISO timestamps, grader scores, path to raw output].
> Validate a run record against schemas/run_record.schema.json (status "completed",
> arm "orch_bare", empty skill_tree, compliance zeros). If it validates: artifact_put the
> raw output, then memory_save the record under run/<task_id>/orch_bare/<rep> in namespace
> dev/skill-transfer with kind=claim, event_id = the run_id, and meta carrying
> repo=aliomraniH/LLM-As-Memory, branch=main, and the current HEAD sha. If validation fails,
> stop and show me the error — never write an invalid record.

## 7. After baselines — distillation loop (orchestrator surface, not here)

Only once A1 and A3 are complete for a task: give the orchestrator
`prompts/skill_distillation.md` plus its own successful A1 traces. When a skill lands in
`skills/`, on this machine:

```bash
git pull
python3 scripts/leakage_audit.py            # must be clean
sha256sum skills/<name>/SKILL.md            # goes into the skillrel claim
```

Then paste into `claude`:

> Release skill <name> v<version>: memory_save a claim under skillrel/<name>/<version> in
> namespace dev/skill-transfer, value describing the release, meta carrying
> repo=aliomraniH/LLM-As-Memory, branch=main, repo_sha=<current HEAD>, and
> skill_sha256=<the hash>. Use a fresh UUID event_id. Then coord_reconcile and report the
> verdict — the release is only usable for edge_skill arms if it reconciles current.

Only after a `current` verdict, run the skill arms:

```bash
python3 harness/run.py --task T01 --arm edge_skill --rep 1   # freshness gate now applies
```

Between revisions, use `prompts/failure_analysis.md` on the A4 records (revision cap: 3).

## 8. Blocked-until list

- Referee cells: blocked until `harness/config.yaml` referee is a dated snapshot (not
  `TODO-pin-snapshot`) and `settings/openai_referee.env` exists (gitignored).
- edge_skill / orch_skill arms: blocked until a skillrel claim reconciles `current`.
- Any skill authoring: blocked until that task's A1 and A3 baselines are recorded.
