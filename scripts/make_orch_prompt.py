#!/usr/bin/env python3
"""Assemble the blind orchestrator-arm wrapper (A1/A2) for one rep.

Usage:
    python3 scripts/make_orch_prompt.py T01              # mints a fresh run_id
    python3 scripts/make_orch_prompt.py T09 --run-id <uuid>

Prints the paste-ready prompt on stdout and the run_id on stderr. The prompt is
pasted into a FRESH orchestrator session (Claude web / Claude Code Web) with no
other context — never into a session that has seen this repo, the graders, or
the experiment design (EXPERIMENT.md blindness rule). For T09 the per-rep
instance is generated here, seeded by the run_id, exactly as the edge harness
does.

Grading keys (expected.json, instance.json) are never included.
"""
import argparse, pathlib, subprocess, sys, uuid

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

WRAPPER = """Record the exact model identifier you are running as, on your first line. \
Then complete the following task exactly as specified, writing your final answer, \
and nothing else, in a single fenced code block at the end.

{task_prompt}

Your run id (use it wherever the task requires a run id): {run_id}
Keep your final answer within {max_output_tokens} tokens.

Input files are provided below.

{fixtures}"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()
    run_id = args.run_id or str(uuid.uuid4())

    task_dir = next((d for d in (ROOT / "tasks").iterdir()
                     if d.is_dir() and d.name.startswith(args.task)), None)
    if task_dir is None:
        sys.exit(f"unknown task {args.task}")
    task = yaml.safe_load((task_dir / "task.yaml").read_text())

    if args.task == "T09":
        gen_dir = ROOT / ".runs" / "instances" / run_id
        subprocess.run([sys.executable, str(task_dir / "graders" / "generate.py"),
                        run_id, str(gen_dir)], check=True)
        fixture_dir = gen_dir / "fixtures"
    else:
        fixture_dir = task_dir / "fixtures"

    files = [p for p in sorted(fixture_dir.glob("*"))
             if p.is_file() and p.name not in ("expected.json", "instance.json")] \
        if fixture_dir.exists() else []
    fixtures = "\n\n".join(f"--- {p.name} ---\n{p.read_text().rstrip()}" for p in files) \
        or "(this task has no input files)"

    print(f"run_id: {run_id}", file=sys.stderr)
    print(WRAPPER.format(task_prompt=task["prompt"].strip(), run_id=run_id,
                         max_output_tokens=task["max_output_tokens"], fixtures=fixtures))
    return 0


if __name__ == "__main__":
    sys.exit(main())
