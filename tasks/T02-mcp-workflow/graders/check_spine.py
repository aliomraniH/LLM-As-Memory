#!/usr/bin/env python3
"""Tier-1 postcondition grader for T02. Deterministic, no LLM calls.
Reads back the run's spine entry via the harness SpineClient and checks:
  1) kind == "claim"
  2) meta carries repo AND (branch or pr) AND a sha field
  3) latest coord/_reconcile verdict for the key is "current"
Usage: check_spine.py <run_id>   (key = task-t02/prereg-commit/<run_id>)
Prints score 0.0-1.0 (each check ~1/3), exit 0."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "harness"))
from spine_client import SpineClient  # noqa: E402

NS = "dev/skill-transfer-tasks"

def main() -> int:
    run_id = sys.argv[1]
    key = f"task-t02/prereg-commit/{run_id}"
    c = SpineClient()
    score = 0.0
    entry = c.call("memory_get", {"namespace": NS, "key": key})
    if entry:
        if entry.get("kind") == "claim":
            score += 1/3
        meta = entry.get("meta") or {}
        if meta.get("repo") and (meta.get("branch") or meta.get("pr")) and any(
                k for k in meta if "sha" in k.lower()):
            score += 1/3
        verdicts = c.call("memory_list", {"namespace": NS, "prefix": f"coord/_reconcile/{key}"}) or []
        latest = verdicts[0] if verdicts else None
        if latest and "current" in json.dumps(latest).lower():
            score += 1/3
    print(f"{score:.4f}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
