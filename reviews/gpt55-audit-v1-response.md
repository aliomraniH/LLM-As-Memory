# Response to the cross-family audit (gpt-5.5-2026-04-23)

Author: claude-fable-5 (the report's author and the measured orchestrator arm —
same disclosed conflict; this response corrects rather than defends).
Audit: `reviews/gpt55-audit-v1.md` (verdicts: 16 SUPPORTED / 18 OVERCLAIMED /
0 UNSUPPORTED / 5 UNVERIFIABLE over 39 claims). The corrected report artifact
carries these changes; this file is the durable record of what changed and why.

## Accepted without reservation

- **Small n, no statistical testing** (confound 1). Correct. All v1 comparisons
  are directional; the T02 inversion (0.80 vs 1.00, n=5/arm) is three subcheck
  misses vs zero and is not statistically established. The report now says so.
- **Non-homogeneous harness versions on T01/T09 cross-arm comparisons**
  (confounds 2–3). Correct: T01 edge=0.1.3 vs orch=0.1.4; T09 edge=0.1.2 vs
  orch=0.1.4; only T02 is cross-arm homogeneous at 0.1.6. Both affected tasks
  are ties at floor/ceiling and the wrapper was functionally unchanged across
  those bumps, but the caveat now appears wherever "identical wrapper" was
  stated as a blanket claim.
- **Numeric imprecision.** "Six harness versions" → seven (0.1.0→0.1.6);
  "roughly half of all launches" and "destroyed 40%" were unquantified
  narrative → replaced with what the evidence supports ("a substantial share,
  not formally tallied"; "only 3 of 5 edge T02 records had actually persisted").
- **The defect taxonomy is post-hoc** and "every one was found by interrogating
  a suspicious number" was overclaimed (some defects fell out of later
  fail-closed fixes). Reworded.
- **Implications I1–I3 are extrapolations** beyond the measured pairing/suite.
  They are now labeled as recommendations motivated by, not established by,
  the data.
- **"Null by precondition" can hide a sensitivity problem.** The auditor is
  right that the suite left one small-n informative task (T02) with T01 at
  floor and T09 at ceiling. The report now carries this as a design lesson:
  the suite failed to instantiate the intended high-transfer condition.
- **H1/H2/H4–H7 predictions are not data-derived thresholds.** Correct; they
  are pre-registered bets for v2, now explicitly labeled as such.

## Corrected after post-audit verification (new evidence, not rebuttal)

**F2/N1/H3 failure attribution.** The auditor correctly ruled "every fable miss
was the same provenance judgment call" undecidable from the run records — the
evidence pack did not include the task-scratch namespace where the measured
models write their T02 claims. Read back post-audit from
`dev/skill-transfer-tasks` (`task-t02/prereg-commit/<run_id>` and paired
`coord/_reconcile/...` records):

| rep | run_id | score | model's `meta.repo_sha` |
|---|---|---|---|
| 1 | 29a876c1 | 0.6667 | `0a05846b…` (historical fact commit) |
| 2 | 09d9df3a | 1.0 | `94c6fb3b…` (live head at run time) |
| 3 | 95f6f792 | 0.6667 | `0a05846b…` (historical) |
| 4 | ffd4ded2 | 0.6667 | `0a05846b…` (historical) |
| 5 | 73210209 | 1.0 | `94c6fb3b…` (live head) |

5/5 consistent: every miss pinned the historical sha; every success pinned the
live head. The attribution stands **as a cited observation**; the report now
carries this table. The *causal generalization* ("frontier models
systematically prefer semantic fidelity") remains a hypothesis (H3) — and the
first cross-tier probe (web-bench-v2a) found haiku/sonnet/opus all pinning
operationally, narrowing H3 to a fable-specific or settings question.

## Removed as unverifiable

- The "17–28 tool-use turns" detail in F2 (operator-reported CLI metadata, not
  independently re-verified from archived artifacts).
- "Every silent failure was caught by interrogating every zero" (process
  narration; softened to what is documented).

## Unchanged, per the audit's own findings

The core empirical result — no positive orchestrator-over-edge gap on the
measured suite (T01 double floor, T02 inverted, T09 double ceiling), hence the
pre-registered hypothesis untested — was SUPPORTED, as were the phantom-ack
mechanism (L5/F5), the T01 structural-unobservability diagnosis (L3/F3), and
the arm-parity launch design (L6).
