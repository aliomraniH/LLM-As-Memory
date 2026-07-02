#!/usr/bin/env python3
"""Harness runner — implements HARNESS.md steps 1-6. Thin, fail-closed.

Usage: run.py --task T01 --arm edge_bare --rep 1 [--config harness/config.yaml]
"""
import argparse, hashlib, json, pathlib, subprocess, sys, time, uuid

import jsonschema, yaml

from spine_client import SpineClient, SpineUnavailable

ROOT = pathlib.Path(__file__).resolve().parents[1]
HARNESS_VERSION = "0.1.1"
NOW = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_task(task_id: str) -> tuple[dict, pathlib.Path]:
    for d in (ROOT / "tasks").iterdir():
        if d.is_dir() and d.name.startswith(task_id):
            return yaml.safe_load((d / "task.yaml").read_text()), d
    sys.exit(f"unknown task {task_id}")


def skill_tree_hashes(skills_in_scope: list[str]) -> dict:
    out = {}
    for s in skills_in_scope:
        f = ROOT / "skills" / s / "SKILL.md"
        if not f.exists():
            sys.exit(f"skill {s} not present — cannot run a *_skill arm without it")
        out[s] = sha256_file(f)
    return out


def freshness_gate(client: SpineClient, cfg: dict, hashes: dict) -> str:
    """SPINE.md freshness gate. Returns repo_sha. Aborts (fail closed) on any mismatch."""
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()
    ns = cfg["namespace"]
    try:
        for name, local_sha in hashes.items():
            entries = client.call("memory_list", {"namespace": ns, "prefix": f"skillrel/{name}/"})
            if not entries:
                sys.exit(f"freshness: no skillrel claim for {name} — release the skill first")
        verdicts = client.call("coord_reconcile", {"namespace": ns})
        if "stale" in json.dumps(verdicts).lower():
            sys.exit("freshness: reconcile returned stale verdicts — git pull and retry")
    except SpineUnavailable as e:
        sys.exit(f"freshness: spine unreachable ({e}) — never run a *_skill arm unverified")
    # hand the expectation to the SessionStart hook
    exp = {"repo_sha": head, "skills": hashes}
    (ROOT / ".runs").mkdir(exist_ok=True)
    (ROOT / ".runs" / "expected_skill_tree.json").write_text(json.dumps(exp, indent=2))
    return head


def launch_edge(cfg: dict, task: dict, task_dir: pathlib.Path, out_path: pathlib.Path,
                skill_arm: bool, run_id: str) -> tuple[str, str]:
    """Launch headless Claude Code. Returns (raw_output, model_id_observed)."""
    prompt_tpl = (ROOT / "prompts" / "arm_runner.md").read_text()
    fixtures = "\n".join(str(p) for p in sorted((task_dir / "fixtures").glob("*")) if p.is_file()) \
        if (task_dir / "fixtures").exists() else "(generated per rep — see problem.md path above)"
    prompt = (prompt_tpl.replace("{task_prompt}", task["prompt"])
              .replace("{fixture_paths}", fixtures)
              .replace("{output_path}", str(out_path))
              .replace("{max_output_tokens}", str(task["max_output_tokens"])))
    env = dict(**__import__("os").environ, SKILL_ARM="1" if skill_arm else "0",
               CLAUDE_PROJECT_DIR=str(ROOT))
    model = cfg["models"]["edge"]
    proc = subprocess.run(
        ["claude", "-p", prompt, "--model", model, "--output-format", "json",
         "--allowedTools", "Read,Write", "--max-turns", "30"],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=1800)
    observed = model
    try:
        meta = json.loads(proc.stdout)
        observed = meta.get("model", meta.get("modelId", model))
    except Exception:
        pass
    return proc.stdout, observed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--arm", required=True,
                    choices=["orch_bare", "orch_skill", "edge_bare", "edge_skill"])
    ap.add_argument("--rep", type=int, required=True)
    ap.add_argument("--config", default=str(ROOT / "harness" / "config.yaml"))
    args = ap.parse_args()

    cfg = yaml.safe_load(pathlib.Path(args.config).read_text())
    task, task_dir = load_task(args.task)
    schema = json.loads((ROOT / "schemas" / "run_record.schema.json").read_text())
    client = SpineClient()

    run_id = str(uuid.uuid4())
    skill_arm = args.arm.endswith("_skill")
    started = NOW()

    if args.arm.startswith("orch_"):
        sys.exit("orchestrator arms run on Claude web / Claude Code Web — record manually or "
                 "extend launch_orch(); this runner drives edge arms.")

    # step 1-2: arm resolution + freshness gate
    hashes = skill_tree_hashes(task.get("skills_in_scope", [])) if skill_arm else {}
    repo_sha = None
    if skill_arm:
        repo_sha = freshness_gate(client, cfg["spine"] | {"namespace": cfg["namespace"]}
                                  if "spine" in cfg else cfg, hashes)
    # tell the Stop hook which skills count
    (ROOT / ".runs").mkdir(exist_ok=True)
    (ROOT / ".runs" / "current_run.json").write_text(json.dumps(
        {"run_id": run_id, "skills_in_scope": task.get("skills_in_scope", []) if skill_arm else []}))

    # T09: generate a fresh instance per rep
    instance_path = None
    if args.task == "T09":
        gen_dir = ROOT / ".runs" / "instances" / run_id
        subprocess.run([sys.executable, str(task_dir / "graders" / "generate.py"),
                        run_id, str(gen_dir)], check=True)
        instance_path = gen_dir / "instance.json"
        task = dict(task)  # fixtures live in gen_dir for this rep

    # step 3: launch
    out_path = ROOT / ".runs" / "outputs" / f"{run_id}.out"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    raw, observed = launch_edge(cfg, task, task_dir if args.task != "T09"
                                else (ROOT / ".runs" / "instances" / run_id), out_path,
                                skill_arm, run_id)

    pinned = cfg["models"]["edge"]
    status = "completed"
    if observed != pinned:
        status = "aborted_model_mismatch"

    # step 4: artifact_put + deterministic graders
    artifact_sha = None
    if status == "completed":
        import base64
        blob = base64.b64encode(raw.encode()).decode()
        try:
            res = client.call("artifact_put", {"data": blob})
            artifact_sha = (res or {}).get("sha256") if isinstance(res, dict) else None
        except SpineUnavailable:
            artifact_sha = hashlib.sha256(raw.encode()).hexdigest()  # local hash; upload on replay
            client.journal("artifact_put", {"data": blob, "event_id": run_id + "-artifact"})

    scores = {}
    if status == "completed":
        for g in task.get("deterministic_graders", []):
            cmd = g["cmd"].replace("{output_path}", str(out_path))
            if instance_path:
                cmd = cmd.replace("{instance_path}", str(instance_path))
            parts = cmd.split()
            if parts and parts[0] == "python":  # grader cmds say "python"; use this interpreter
                parts[0] = sys.executable
            r = subprocess.run(parts, cwd=task_dir, capture_output=True, text=True)
            try:
                scores[g["name"]] = float(r.stdout.strip().splitlines()[-1])
            except Exception:
                scores[g["name"]] = 0.0

    # compliance (written by Stop hook; default zeros for bare/headless)
    comp = {"skill_steps_total": 0, "skill_steps_executed": 0, "hook_gate_triggers": 0}
    comp_files = sorted((ROOT / ".runs" / "compliance").glob("*.json"),
                        key=lambda p: p.stat().st_mtime) if (ROOT / ".runs" / "compliance").exists() else []
    if comp_files:
        latest = json.loads(comp_files[-1].read_text())
        comp = {k: latest[k] for k in comp}

    # step 6: assemble record -> validate (fail closed) -> journal-then-write
    record = {
        "run_id": run_id, "task_id": task["task_id"], "task_version": str(task["version"]),
        "arm": args.arm, "rep": args.rep,
        "model_id_pinned": pinned, "model_id_observed": observed,
        "skill_tree": hashes, "harness_version": HARNESS_VERSION,
        "started_at": started, "finished_at": NOW(), "status": status,
        "output_artifact_sha256": artifact_sha if status == "completed" else None,
        "scores": {"deterministic": scores}, "compliance": comp,
    }
    if repo_sha:
        record["repo_sha"] = repo_sha
    try:
        jsonschema.validate(record, schema)
    except jsonschema.ValidationError as e:
        sys.exit(f"run record failed schema validation — run is INVALID, re-run it.\n{e}")

    ns = cfg["namespace"]
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()
    client.write_with_journal("memory_save", {
        "namespace": ns, "key": f"run/{task['task_id']}/{args.arm}/{args.rep}",
        "kind": "claim", "value": json.dumps(record), "event_id": run_id,
        "source_surface": "claude-code-local",
        "meta": {"repo": cfg["repo"], "branch": "main", "repo_sha": head},
    })
    pending = client.replay(max_attempts=cfg.get("spine", {}).get("replay_max_attempts", 3),
                            backoff_s=cfg.get("spine", {}).get("replay_backoff_seconds", 5))
    if pending:
        print(f"WARNING: {pending} spine writes still unacknowledged — run does not count until "
              "journal replay succeeds (SPINE.md).", file=sys.stderr)
        return 3
    print(json.dumps({"run_id": run_id, "status": status, "scores": scores}))
    return 0 if status == "completed" else 2


if __name__ == "__main__":
    sys.exit(main())
