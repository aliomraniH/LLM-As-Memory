#!/usr/bin/env python3
"""Tier-1 grader: field-level accuracy in [0,1]. Deterministic, no LLM calls.
Usage: match.py <output_path> <expected_json>. Records aligned by patient_name;
scalars exact-match after normalization; medications scored by greedy best matching."""
import json, pathlib, sys

def norm(v):
    if isinstance(v, str):
        return " ".join(v.lower().split())
    return v

def med_sim(a, b):
    keys = ["name", "dose_value", "dose_unit", "route", "frequency"]
    return sum(norm(a.get(k)) == norm(b.get(k)) for k in keys) / len(keys)

def score_record(got, exp):
    scalar_keys = ["patient_name", "date_of_birth", "referral_date", "referring_provider",
                   "referring_organization", "referral_reason_code", "referral_reason_text", "urgency"]
    pts, total = 0.0, 0.0
    for k in scalar_keys:
        total += 1
        pts += 1 if norm(got.get(k)) == norm(exp.get(k)) else 0
    exp_meds, got_meds = exp.get("medications", []), list(got.get("medications", []) or [])
    for em in exp_meds:
        total += 1
        if not got_meds:
            continue
        sims = [med_sim(gm, em) for gm in got_meds]
        best_i = max(range(len(sims)), key=sims.__getitem__)
        pts += sims[best_i]
        got_meds.pop(best_i)
    return pts / total if total else 0.0

def main() -> int:
    try:
        raw = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]; raw = raw[raw.find("["):]
        got = json.loads(raw)
        exp = json.loads(pathlib.Path(sys.argv[2]).read_text())
    except Exception:
        print("0.0"); return 0
    if not isinstance(got, list):
        print("0.0"); return 0
    by_name = { norm(r.get("patient_name")): r for r in got if isinstance(r, dict) }
    scores = [score_record(by_name.get(norm(e["patient_name"]), {}) , e) for e in exp]
    print(f"{sum(scores)/len(scores):.4f}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
