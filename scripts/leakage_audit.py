#!/usr/bin/env python3
"""Grep-audit: no leakage_forbidden_strings from any task.yaml may appear in skills/.
Exit 0 clean, exit 1 on any hit (fail closed). Wired as pre-commit via .githooks/."""
import pathlib, re, sys

def forbidden_strings():
    out = []
    for ty in pathlib.Path("tasks").glob("*/task.yaml"):
        in_block = False
        for line in ty.read_text().splitlines():
            if line.startswith("leakage_forbidden_strings:"):
                in_block = "[" not in line
                continue
            if in_block:
                m = re.match(r'\s+-\s+"(.*)"\s*$', line)
                if m:
                    out.append((str(ty), m.group(1)))
                else:
                    in_block = False
    return out

def main() -> int:
    skills = pathlib.Path("skills")
    if not skills.exists():
        return 0
    hits = 0
    for _, s in forbidden_strings():
        for f in skills.rglob("*"):
            if f.is_file() and "_template" not in f.parts:
                if s.lower() in f.read_text(encoding="utf-8", errors="replace").lower():
                    print(f"LEAKAGE: {s!r} found in {f}", file=sys.stderr)
                    hits += 1
    return 1 if hits else 0

if __name__ == "__main__":
    sys.exit(main())
