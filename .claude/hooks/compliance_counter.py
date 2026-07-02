#!/usr/bin/env python3
"""Stop hook — measures prompt-tier compliance (EXPERIMENT.md §5, hooks/README.md).

Contract:
  - skill_steps_total  = count of "[MANDATORY]" markers across SKILL.md files named in
                         .runs/current_run.json {"skills_in_scope": [...]} (0 for bare arms /
                         when the file or list is absent).
  - skill_steps_executed = count of distinct "[MANDATORY-DONE:<n>]" markers emitted by the
                         assistant in the transcript (the distillation prompt requires skills to
                         instruct executors to emit these).
  - hook_gate_triggers = lines in .runs/hook_gate.log for this session (guards append on block).
Emits JSON to .runs/compliance/<session_id>.json. Never blocks (exit 0) — it measures.
"""
import json, os, re, sys, pathlib

def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    session_id = payload.get("session_id", "unknown")
    transcript_path = payload.get("transcript_path")

    repo = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    runs = repo / ".runs"
    runs.joinpath("compliance").mkdir(parents=True, exist_ok=True)

    total = 0
    cur = runs / "current_run.json"
    if cur.exists():
        try:
            skills = json.loads(cur.read_text()).get("skills_in_scope", [])
            for s in skills:
                f = repo / "skills" / s / "SKILL.md"
                if f.exists():
                    total += f.read_text(encoding="utf-8").count("[MANDATORY]")
        except Exception:
            pass

    executed = set()
    if transcript_path and os.path.exists(transcript_path):
        rx = re.compile(r"\[MANDATORY-DONE:(\d+)\]")
        with open(transcript_path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("type") != "assistant":
                    continue
                for m in rx.finditer(json.dumps(obj)):
                    executed.add(m.group(1))

    gate_log = runs / "hook_gate.log"
    triggers = 0
    if gate_log.exists():
        triggers = sum(1 for l in gate_log.read_text().splitlines() if session_id in l)

    out = {
        "session_id": session_id,
        "skill_steps_total": total,
        "skill_steps_executed": min(len(executed), total) if total else len(executed),
        "hook_gate_triggers": triggers,
    }
    (runs / "compliance" / f"{session_id}.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out))
    return 0

if __name__ == "__main__":
    sys.exit(main())
