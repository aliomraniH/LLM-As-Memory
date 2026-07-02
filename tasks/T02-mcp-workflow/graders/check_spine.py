#!/usr/bin/env python3
"""Tier-1 postcondition grader for T02. Deterministic, no LLM calls.
Reads back the run's spine entry via the harness SpineClient and checks:
  1) kind == "claim"
  2) meta carries repo AND (branch or pr) AND a sha field
  3) latest coord/_reconcile verdict for the key is "current"
Usage: check_spine.py <run_id>   (key = task-t02/prereg-commit/<run_id>)
Prints score 0.0-1.0 (each check ~1/3), exit 0.

The spine may return the entry directly or under a {"result": ...} envelope, and
untrusted string fields arrive wrapped in <<<UNTRUSTED_DATA>>>...<<<END>>> sentinels;
both are handled defensively (a hidden envelope would silently break checks 1 & 2 too)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "harness"))
from spine_client import SpineClient  # noqa: E402

NS = "dev/skill-transfer-tasks"


def unwrap(e):
    """If the entry is carried under a `result` key, return that; else use as-is."""
    if isinstance(e, dict) and "result" in e and "kind" not in e:
        return e["result"]
    return e


def main() -> int:
    run_id = sys.argv[1]
    key = f"task-t02/prereg-commit/{run_id}"
    c = SpineClient()
    score = 0.0
    entry = unwrap(c.call("memory_get", {"namespace": NS, "key": key}))
    if isinstance(entry, dict):
        # 1) kind == "claim" (tolerate a sentinel-wrapped value)
        if "claim" in str(entry.get("kind", "")).lower():
            score += 1/3
        # 2) provenance: repo AND (branch or pr) AND some *sha* field
        meta = entry.get("meta") or {}
        if meta.get("repo") and (meta.get("branch") or meta.get("pr")) and any(
                k for k in meta if "sha" in k.lower()):
            score += 1/3
        # 3) reconcile verdict is "current" — read value.state (scoped), fall back to tags
        verdict = unwrap(c.call("memory_get", {"namespace": NS, "key": f"coord/_reconcile/{key}"}))
        if isinstance(verdict, dict):
            val = verdict.get("value") or {}
            state = val.get("state") if isinstance(val, dict) else None
            if state is not None:
                if "current" in str(state).lower():
                    score += 1/3
            elif any("current" in str(t).lower() for t in (verdict.get("tags") or [])):
                score += 1/3
    print(f"{score:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
