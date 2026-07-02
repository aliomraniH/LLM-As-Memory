#!/usr/bin/env python3
"""Verifies a proposed assignment against the generated instance. Deterministic.
Usage: verify.py <output_path> <instance_path>. Prints 1.0 if fully valid else 0.0; exit 0."""
import json, pathlib, sys

def main() -> int:
    try:
        raw = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]; raw = raw[raw.find("{"):]
        got = json.loads(raw)["assignment"]
        inst = json.loads(pathlib.Path(sys.argv[2]).read_text())
    except Exception:
        print("0.0"); return 0
    slots, cap = set(inst["slots"]), inst["slot_capacity"]
    if set(got) != set(inst["meetings"]) or any(got[m] not in slots for m in got):
        print("0.0"); return 0
    counts = {}
    for s in got.values():
        counts[s] = counts.get(s, 0) + 1
    if any(v > cap for v in counts.values()):
        print("0.0"); return 0
    for c in inst["constraints"]:
        ok = (got[c["meeting"]] == c["slot"] if c["type"] == "fixed"
              else got[c["first"]] < got[c["second"]] if c["type"] == "before"
              else got[c["a"]] != got[c["b"]])
        if not ok:
            print("0.0"); return 0
    print("1.0")
    return 0

if __name__ == "__main__":
    sys.exit(main())
