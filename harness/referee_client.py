#!/usr/bin/env python3
"""Cross-family referee client — implements referee/REFEREE.md and prompts/referee_call.md.

Scope guard: the referee grades ONLY cells deterministic graders cannot decide
(open-ended dimensions). T01/T02/T09 are fully deterministic; this client exists
for future open-ended tasks and for agreement sampling.

Fail-closed rules enforced here:
  - refuses to run until REFEREE_MODEL_SNAPSHOT is a dated snapshot (never a
    floating alias; config.yaml's TODO-pin-snapshot also refuses);
  - blinds both payloads before assembly (model names, arm labels, skill paths,
    spine keys/namespaces, run-id UUIDs);
  - every pairwise judgment runs twice with A/B swapped; preference counts only
    if its direction survives the swap, else it is a tie;
  - responses are parsed and validated against referee_output.schema.json; one
    retry with the validation error appended, then the judgment is INVALID and
    the cell re-queues — never coerced.

Usage:
  python3 harness/referee_client.py --selftest
  python3 harness/referee_client.py --task T01 --a out_a.txt --b out_b.txt
"""
import argparse, hashlib, json, os, pathlib, re, sys, urllib.error, urllib.request

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / "settings" / "openai_referee.env"
RUBRIC_PATH = ROOT / "referee" / "rubric.md"
SCHEMA = json.loads((ROOT / "referee" / "referee_output.schema.json").read_text())

_DATED = re.compile(r"\d{4}-\d{2}-\d{2}|\d{8}")
_FLOATING = ("latest", "auto", "preview", "TODO")

# Blinding rule (prompts/referee_call.md): strip identity before assembly.
_BLIND_PATTERNS = [
    r"\b(anthropic|claude|opus|sonnet|haiku|fable|mythos)[\w.-]*\b",
    r"\b(openai|gpt|gemini|google)[\w.-]*\b",
    r"\b(orch|edge)_(bare|skill)\b",
    r"\borch(estrator)?\b|\bedge model\b",
    r"\bskills?/[\w./-]+\b|\bSKILL\.md\b",
    r"\bdev/skill-transfer[\w-]*\b",
    r"\b(skillrel|task-t\d+|run|coord)/[\w./-]+\b",
    r"\bMCP_Assist\b|\bmcp__[\w]+\b",
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",  # run ids
]


class RefereeRefused(SystemExit):
    pass


def _env() -> dict:
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip("'\"")
    env.update({k: v for k, v in os.environ.items() if k in (
        "OPENAI_API_KEY", "OPENAI_BASE_URL", "REFEREE_MODEL_SNAPSHOT")})
    return env


def referee_config() -> tuple[str, str, str]:
    env = _env()
    model = env.get("REFEREE_MODEL_SNAPSHOT", "")
    if (not model or any(f.lower() in model.lower() for f in _FLOATING)
            or not _DATED.search(model)):
        raise RefereeRefused(
            f"referee refused: REFEREE_MODEL_SNAPSHOT={model!r} is not a dated snapshot. "
            "Pin an explicit dated gpt-5.5 snapshot in settings/openai_referee.env "
            "(and mirror it in harness/config.yaml models.referee).")
    key = env.get("OPENAI_API_KEY")
    if not key:
        raise RefereeRefused("referee refused: OPENAI_API_KEY missing "
                             "(settings/openai_referee.env, gitignored)")
    return model, key, env.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"


def rubric_sha256() -> str:
    return hashlib.sha256(RUBRIC_PATH.read_bytes()).hexdigest()


def blind(text: str, extra_markers: tuple = ()) -> str:
    for pat in _BLIND_PATTERNS:
        text = re.sub(pat, "[REDACTED]", text, flags=re.I)
    for marker in extra_markers:
        text = text.replace(marker, "[REDACTED]")
    return text


def assemble(task_prompt: str, payload_a: str, payload_b: str,
             task_dir: pathlib.Path | None = None) -> str:
    parts = [RUBRIC_PATH.read_text()]
    if task_dir is not None and (task_dir / "rubric_addendum.md").exists():
        parts.append((task_dir / "rubric_addendum.md").read_text())
    parts.append("## Task specification\n" + task_prompt.strip())
    parts.append("## Response A\n" + payload_a)
    parts.append("## Response B\n" + payload_b)
    parts.append("Respond with JSON only, conforming to the RefereeJudgment schema "
                 "provided below. No prose outside the JSON. " + json.dumps(SCHEMA))
    return "\n\n".join(parts)


def _chat(prompt: str, model: str, key: str, base: str) -> str:
    payload = {"model": model, "temperature": 0,
               "messages": [{"role": "user", "content": prompt}]}
    for attempt in (1, 2):
        req = urllib.request.Request(
            base.rstrip("/") + "/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                resp = json.loads(r.read().decode())
            return resp["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            # some snapshots reject explicit temperature; drop to provider minimum once
            if attempt == 1 and "temperature" in body:
                payload.pop("temperature", None)
                continue
            raise RuntimeError(f"referee API error {e.code}: {body[:300]}") from e
    raise RuntimeError("unreachable")


def _parse_validate(raw: str):
    body = raw.strip()
    if body.startswith("```"):
        body = re.sub(r"^```[a-z]*\n?|\n?```$", "", body)
    obj = json.loads(body)
    jsonschema.validate(obj, SCHEMA)
    return obj


def judge_once(prompt: str, model: str, key: str, base: str):
    """One judgment: parse -> validate -> one retry with the error appended -> None."""
    raw = _chat(prompt, model, key, base)
    try:
        return _parse_validate(raw)
    except Exception as e:
        retry = (prompt + "\n\nYour previous response failed validation and was discarded. "
                 f"Validation error: {e}\nRespond again with JSON only.")
        try:
            return _parse_validate(_chat(retry, model, key, base))
        except Exception:
            return None  # invalid judgment — cell re-queues; never coerced


def judge_pair(task_prompt: str, payload_a: str, payload_b: str,
               task_dir: pathlib.Path | None = None, extra_markers: tuple = ()) -> dict:
    """Full protocol: blind, judge, swap, judge again. Returns the judgment envelope."""
    model, key, base = referee_config()
    a, b = blind(payload_a, extra_markers), blind(payload_b, extra_markers)
    v1 = judge_once(assemble(task_prompt, a, b, task_dir), model, key, base)
    v2 = judge_once(assemble(task_prompt, b, a, task_dir), model, key, base)
    out = {"valid": v1 is not None and v2 is not None,
           "referee_model": model, "rubric_sha256": rubric_sha256(),
           "len_a": len(payload_a), "len_b": len(payload_b),
           "verdict": v1, "swapped_verdict": v2}
    if not out["valid"]:
        out["preference"] = None
        return out
    p1 = v1["preference"]
    p2 = {"A": "B", "B": "A", "tie": "tie"}[v2["preference"]]  # map swap back to payloads
    out["position_consistent"] = (p1 == p2)
    out["preference"] = p1 if out["position_consistent"] else "tie"
    return out


def _selftest() -> int:
    """Offline: schema round-trip, blinding, swap mapping. No network, no key."""
    sample = {"rubric_version": "1.0",
              "scores_a": {"correctness": 8, "completeness": 7,
                           "procedural_soundness": 9, "spec_conformance": 8},
              "scores_b": {"correctness": 5, "completeness": 6,
                           "procedural_soundness": 4, "spec_conformance": 5},
              "preference": "A",
              "rationale": "Response A satisfies the task specification on every rubric "
                           "dimension; Response B omits required fields and misorders steps."}
    jsonschema.validate(sample, SCHEMA)
    blinded = blind("claude-opus-4-8 ran edge_bare rep run/T01/edge_bare/1 via MCP_Assist "
                    "in dev/skill-transfer, run id 3817c5ba-e975-4bec-bd35-d728c80379de")
    assert "[REDACTED]" in blinded and "opus" not in blinded.lower() \
        and "edge_bare" not in blinded and "3817c5ba" not in blinded, blinded
    assert {"A": "B", "B": "A", "tie": "tie"}["A"] == "B"
    assert len(rubric_sha256()) == 64
    print("selftest OK — schema validates, blinding strips identity, swap maps, "
          f"rubric sha256 {rubric_sha256()[:12]}…")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--task")
    ap.add_argument("--a", help="file with blinded-candidate response A")
    ap.add_argument("--b", help="file with blinded-candidate response B")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if not (args.task and args.a and args.b):
        ap.error("--task, --a and --b are required (or use --selftest)")
    import yaml
    task_dir = next((d for d in (ROOT / "tasks").iterdir()
                     if d.is_dir() and d.name.startswith(args.task)), None)
    if task_dir is None:
        sys.exit(f"unknown task {args.task}")
    task = yaml.safe_load((task_dir / "task.yaml").read_text())
    result = judge_pair(task["prompt"],
                        pathlib.Path(args.a).read_text(),
                        pathlib.Path(args.b).read_text(), task_dir)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
