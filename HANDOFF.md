# HANDOFF — bootstrap complete (Phases 0–2), edge machine next

Spine session: `80bdcd4e-e9fa-4487-aa55-c3f6b16b10b2` in namespace `dev/skill-transfer`.
Mirrored via `handoff_save` under key `bootstrap`.

## What was built

- **Phase 0** — scaffold committed to `main` as the pre-registration snapshot:
  `0a05846beb85a91fe5bf3c0acde275c951e73d79` ("pre-registration: experiment design v1").
  Repo is `aliomraniH/LLM-As-Memory` (name deviation logged in ANALYSIS.md).
- **Phase 1** (`150888e`, "phase-1: executable harness"):
  - `prompts/` — arm_runner (blind, verified zero experiment-revealing content), referee_call
    assembly recipe, skill_distillation, failure_analysis.
  - `.claude/settings.json` + hooks: `freshness_gate.sh` (SessionStart), `namespace_guard.py`
    (PreToolUse on memory_save/handoff_save), `compliance_counter.py` (Stop). All tested to fail
    closed with deliberate violations.
  - T01: 3 synthetic referral fixtures, `expected.json`, schema + `validate.py` + `match.py`
    graders (verified: perfect output → 1.0/1.0, corrupted → 0.0/0.9);
    `leakage_forbidden_strings` populated (17 strings) and grep-audit wired as a pre-commit hook
    (`git config core.hooksPath .githooks`) — tested to block a deliberate leak.
  - T02: `fixtures/context.md` pins the pre-registration commit as the fact to record;
    `graders/check_spine.py` postcondition grader.
  - T09: `generate.py` (fresh solvable instance per rep, seeded by run_id; solvability
    brute-force-verified) + `verify.py`.
  - `harness/run.py` + `harness/spine_client.py` — arm resolution → freshness gate → `claude -p`
    launch → artifact_put + graders → record assembly → schema validation (fail closed) →
    journal-then-write with idempotent event_id replay (replay convergence and exactly-once
    tested with a mocked transport). `harness/config.yaml` instantiated; referee left as
    `TODO-pin-snapshot` — harness must refuse referee cells until pinned.
  - `settings/openai_referee.env.example`; real env files gitignored. No keys or PHI in the repo.
- **Phase 2** — spine seeded: `coord_health` clean (entry_count was 0), bootstrap session
  created, `decision/repo-initialized` written, `skillrel/_template/0.0-dryrun` claim written
  with full provenance envelope, `coord_reconcile` run. Verdict: **unverifiable — could not
  resolve branch head**, which is correct: remote `main` is still empty. `resolver_enabled: true`,
  so the claim resolves as soon as the push lands.

## Deferred / open

1. **Push.** This clone has no credentials. Push preserving history (SHAs are pinned in the T02
   fixture and spine records — do not rebase or squash).
2. **Re-reconcile after push** — expect the dry-run claim to leave `unverifiable`. If it verdicts
   `stale` rather than `current` because `main` has moved past the recorded `repo_sha`, that is
   the resolver comparing branch head to the claim's SHA — acceptable for the dry-run; real
   `skillrel/*` releases should be written at the release commit and re-reconciled immediately.
3. **Branch protection** on `main` (GitHub UI) — see ANALYSIS.md deviation #2.
4. **Referee snapshot** — pin a dated gpt-5.5 snapshot + third-family agreement judge in
   `harness/config.yaml` and `settings/openai_referee.env` before any referee cells.
5. **No capability skills exist yet** — by design. Baselines (A1/A3) run first; distillation
   follows EXPERIMENT.md §3 using `prompts/skill_distillation.md`.

## Edge machine — exact next commands

```bash
git clone https://github.com/aliomraniH/LLM-As-Memory.git && cd LLM-As-Memory
pip install -r requirements.txt
git config core.hooksPath .githooks                 # leakage audit on commit
mkdir -p ~/.claude/skills                            # sync skills (excluding _template)
for d in skills/*/; do [ "$(basename $d)" = "_template" ] || ln -s "$PWD/$d" ~/.claude/skills/; done
# .claude/settings.json ships in-repo (hooks + mcp__MCP_Assist__* allow rules);
# configure the MCP_Assist connector at https://mcp-assist-memory.replit.app/mcp as "MCP_Assist"
python3 - <<'EOF'                                    # spine reachability check
import sys; sys.path.insert(0,"harness")
from spine_client import SpineClient
print(SpineClient().call("coord_health", {"namespace": "dev/skill-transfer"}))
EOF
# first scored rep (bare arm — no freshness gate applies, no skills loaded):
python3 harness/run.py --task T01 --arm edge_bare --rep 1
```

Known spine failure modes: `-32600 Session terminated` → wake/restart the Replit instance, then
journal replay picks up; `No approval received` → local Claude Code allow rules
(`mcp__MCP_Assist__*`), not the server.
