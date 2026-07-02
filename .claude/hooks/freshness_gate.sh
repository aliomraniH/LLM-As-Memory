#!/usr/bin/env bash
# SessionStart hook — freshness gate (SPINE.md §Freshness gate).
# Scored *_skill runs export SKILL_ARM=1 and the harness must have written
# .runs/expected_skill_tree.json (repo_sha + per-skill sha256 fetched from the latest
# skillrel/* claims, reconciled `current`, BEFORE launch). Fail closed on any mismatch
# or missing expectation.
set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
EXPECT="$REPO_ROOT/.runs/expected_skill_tree.json"

if [[ "${SKILL_ARM:-0}" != "1" ]]; then
  exit 0   # not a scored *_skill run; gate does not apply
fi

if [[ ! -f "$EXPECT" ]]; then
  echo "freshness_gate: SKILL_ARM=1 but $EXPECT missing — run the spine freshness step first" >&2
  exit 2
fi

local_head="$(git -C "$REPO_ROOT" rev-parse HEAD)"
expected_head="$(python3 -c "import json;print(json.load(open('$EXPECT'))['repo_sha'])")"
if [[ "$local_head" != "$expected_head" ]]; then
  echo "freshness_gate: local HEAD $local_head != spine-recorded $expected_head — git pull and retry" >&2
  exit 2
fi

# Per-skill content hashes
fail=0
while IFS=$'\t' read -r name expected_sha; do
  f="$REPO_ROOT/skills/$name/SKILL.md"
  if [[ ! -f "$f" ]]; then echo "freshness_gate: missing skill $name" >&2; fail=1; continue; fi
  actual="$(sha256sum "$f" | cut -d' ' -f1)"
  if [[ "$actual" != "$expected_sha" ]]; then
    echo "freshness_gate: $name hash $actual != recorded $expected_sha" >&2; fail=1
  fi
done < <(python3 -c "
import json
d=json.load(open('$EXPECT'))
for k,v in d.get('skills',{}).items(): print(f'{k}\t{v}')")
exit $(( fail ? 2 : 0 ))
