#!/usr/bin/env python3
"""PreToolUse hook on mcp__MCP_Assist__memory_save (and handoff_save if matched).

Rejects (exit 2, stderr fed back to the model):
  - writes whose namespace does not start with dev/skill-transfer
  - payloads matching PHI-shaped patterns (defense in depth; fixtures are synthetic anyway)
Fail closed: unparsable input or missing namespace also blocks.
"""
import json, re, sys

ALLOWED_PREFIX = "dev/skill-transfer"

PHI_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "SSN-shaped"),
    (re.compile(r"\bMRN[:#\s]*\d{5,}\b", re.I), "MRN-shaped"),
    (re.compile(r"\b\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"), "US-phone-shaped"),
    (re.compile(r"\b(DOB|date of birth)[:\s]", re.I), "DOB-labelled"),
    (re.compile(r"\b\d{1,2}/\d{1,2}/(19|20)\d{2}\b"), "slash-date (use synthetic ISO dates)"),
]

def main() -> int:
    try:
        payload = json.load(sys.stdin)
        tool_input = payload.get("tool_input", {}) or {}
    except Exception as e:
        print(f"namespace_guard: cannot parse hook input ({e}) — blocking (fail closed)", file=sys.stderr)
        return 2

    ns = tool_input.get("namespace")
    if not isinstance(ns, str) or not ns.startswith(ALLOWED_PREFIX):
        print(f"namespace_guard: namespace {ns!r} not under {ALLOWED_PREFIX!r} — write blocked", file=sys.stderr)
        return 2

    blob = json.dumps(tool_input, ensure_ascii=False)
    for rx, label in PHI_PATTERNS:
        m = rx.search(blob)
        if m:
            print(f"namespace_guard: payload matches {label} pattern ({m.group(0)!r}) — write blocked; "
                  "store a reference, never PHI-shaped content", file=sys.stderr)
            return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
