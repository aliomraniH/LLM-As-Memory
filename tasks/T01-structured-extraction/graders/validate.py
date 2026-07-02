#!/usr/bin/env python3
"""Tier-1 grader: JSON Schema validation. Deterministic, no LLM calls.
Usage: validate.py <output_path>. Prints score in [0,1]; exit 0. Exit 1 only on grader error."""
import json, pathlib, sys
import jsonschema

def main() -> int:
    out_path = sys.argv[1]
    schema = json.loads((pathlib.Path(__file__).parent / "intake.schema.json").read_text())
    try:
        raw = pathlib.Path(out_path).read_text(encoding="utf-8").strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            raw = raw[raw.find("["):]
        data = json.loads(raw)
    except Exception:
        print("0.0"); return 0
    try:
        jsonschema.validate(data, schema)
        print("1.0")
    except jsonschema.ValidationError:
        print("0.0")
    return 0

if __name__ == "__main__":
    sys.exit(main())
