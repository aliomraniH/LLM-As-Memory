#!/usr/bin/env python3
"""Generates a fresh solvable scheduling CSP per rep, seeded by run_id. Deterministic per seed.
Usage: generate.py <run_id> <out_dir>   -> writes problem.md + instance.json
Instance: N meetings into S slots; constraints: fixed-slot, before(a,b), not-same-slot(a,b),
capacity per slot. Solvability guaranteed by generating from a hidden valid assignment."""
import hashlib, json, random, sys, pathlib

def main() -> int:
    run_id, out_dir = sys.argv[1], pathlib.Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    seed = int(hashlib.sha256(run_id.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    n_meet, n_slot, cap = 8, 5, 2
    names = [f"M{i+1}" for i in range(n_meet)]
    # hidden valid assignment respecting capacity
    slots_pool = [s for s in range(n_slot) for _ in range(cap)]
    rng.shuffle(slots_pool)
    hidden = {m: slots_pool[i] for i, m in enumerate(names)}
    cons = []
    # fixed
    for m in rng.sample(names, 2):
        cons.append({"type": "fixed", "meeting": m, "slot": hidden[m]})
    # before
    tries = 0
    while sum(c["type"] == "before" for c in cons) < 4 and tries < 100:
        a, b = rng.sample(names, 2); tries += 1
        if hidden[a] < hidden[b]:
            cons.append({"type": "before", "first": a, "second": b})
    # not-same-slot
    tries = 0
    while sum(c["type"] == "not_same_slot" for c in cons) < 3 and tries < 100:
        a, b = rng.sample(names, 2); tries += 1
        if hidden[a] != hidden[b]:
            cons.append({"type": "not_same_slot", "a": a, "b": b})
    inst = {"run_id": run_id, "meetings": names, "slots": list(range(n_slot)),
            "slot_capacity": cap, "constraints": cons}
    (out_dir / "instance.json").write_text(json.dumps(inst, indent=2))
    lines = [f"# Scheduling problem (instance {run_id[:8]})", "",
             f"Assign each of {n_meet} meetings ({', '.join(names)}) to one of {n_slot} time slots",
             f"(numbered 0-{n_slot-1}). At most {cap} meetings per slot.", "", "Constraints:"]
    for c in cons:
        if c["type"] == "fixed":
            lines.append(f"- {c['meeting']} must be in slot {c['slot']}.")
        elif c["type"] == "before":
            lines.append(f"- {c['first']} must be in a strictly earlier slot than {c['second']}.")
        else:
            lines.append(f"- {c['a']} and {c['b']} must not share a slot.")
    lines += ["", 'Output JSON only: {"assignment": {"M1": <slot>, ...}}']
    (out_dir / "problem.md").write_text("\n".join(lines))
    print(str(out_dir / "problem.md"))
    return 0

if __name__ == "__main__":
    sys.exit(main())
