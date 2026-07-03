# Cross-family audit — skill-transfer-v1 final report

**Auditor:** GPT-5.5 (`gpt-5.5-2026-04-23`), temperature 0, adversarial methodological review from a different model family.  
**Subject:** `skill-transfer-v1-report-standalone.html` ('The gap that wasn't there'), authored by claude-fable-5 — which was also the measured orchestrator arm (disclosed conflict of interest; this audit is evidence-only).  
**Date:** 2026-07-02.  
**Ground truth:** ANALYSIS.md, EXPERIMENT.md, 40 baseline records read back live from the spine (`dev/skill-transfer`), git log of `main`, harness-version history. The report was NOT allowed to corroborate itself.  
**Fail-closed:** structured JSON validated (all 39 extracted claims + H1–H7 covered); passed on first attempt, no retry needed. Raw JSON alongside at `reviews/gpt55-audit-v1.json`.

## Verdict distribution

| SUPPORTED | OVERCLAIMED | UNSUPPORTED | UNVERIFIABLE-FROM-EVIDENCE | Total |
|---|---|---|---|---|
| 16 | 18 | 0 | 5 | 39 |

## Per-claim verdict table

| ID | Verdict | Claim (abridged) | Auditor evidence / note |
|---|---|---|---|
| H0-1 | SUPPORTED | The experiment was pre-registered (at commit 0a05846) and 'never got to ask' its primary question because a load-bearing assumption it re… | Evidence: ANALYSIS.md: "Pre-registration commit: `0a05846beb85a91fe5bf3c0acde275c951e73d79`"; Outcome: "skill-transfer-v1 concludes null by precondition" and "The pre-registered hypothesis was never reached and remains open." Note: The evidence supports pre… |
| H0-2 | SUPPORTED | There are 40 acknowledged baseline records; the verdict is 'null by precondition'; the primary hypothesis remains open/untested. | Evidence: Baseline records list 40 persisted run rows; ANALYSIS Outcome: "20 acknowledged reps per arm" and "skill-transfer-v1 concludes null by precondition" and "The pre-registered hypothesis was never reached and remains open." Note: Supported by the liv… |
| Q1 | OVERCLAIMED | Primary question Q1: when a frontier orchestrator distills its own successful traces into a SKILL.md, some meaningful fraction of the orc… | Evidence: EXPERIMENT.md §3: "Orchestrator runs the task bare (A1), succeeding traces are collected" and "compresses it into a SKILL.md"; EXPERIMENT.md interpretation matrix: "A4 ≫ A3, A2 ≈ A1 → genuine distillation... The headline result." ANALYSIS says pre… |
| Q2 | OVERCLAIMED | Control question Q2: the same skill closes ~none of the gap on fluid-reasoning tasks (pre-registered prediction: yes, ~none). | Evidence: EXPERIMENT.md §2: "T09–T10 fluid-reasoning controls (transfer NOT expected)" and "These are pre-registered predicted failures." Note: The control prediction of no transfer on fluid reasoning is supported in substance, but the exact Q2 framing and … |
| GAPFORMULA | UNVERIFIABLE-FROM-EVIDENCE | gap_closure = (score(edge_skill) - score(edge_bare)) / (score(orch_bare) - score(edge_bare)); the metric presupposes the orchestrator sco… | Evidence: ANALYSIS.md only says the pre-registered fields included a "gap-closure formula" and Outcome discusses a negative denominator; the explicit formula is not in evidence pack. Note: The need for an orchestrator advantage is supported by the outcome l… |
| L1 | SUPPORTED | Assumption 'a frontier model outperforms a smaller local model on procedural agentic tasks' FAILED: it inverted on T02 (edge opus-4-8 wen… | Evidence: Derived means: T02 edge_bare per-rep=[1.0,...] mean=1.0000; orch_bare per-rep=[0.6667,1.0,0.6667,0.6667,1.0] mean=0.8000. T01 both mean=0.0000; T09 both mean=1.0000. Note: Supported for the measured pairing and suite. The word 'smaller' is concept… |
| L2 | OVERCLAIMED | Assumption 'claude-opus-4-8 can play the edge role' FAILED: it is a near-frontier model that merely runs locally; cost casting is not cap… | Evidence: Baseline records identify edge as `claude-opus-4-8`; ANALYSIS Outcome: "none exhibits the 'orchestrator succeeds where the edge model fails' precondition." Note: No headroom is supported. Claims that opus-4-8 is 'near-frontier', 'merely runs local… |
| L3 | SUPPORTED | Assumption 'domain-convention extraction (T01) is a high-transfer task' FAILED: the conventions exist only in grader material, so no bare… | Evidence: ANALYSIS #9: "reason-code enum exists only in `intake.schema.json`/`expected.json`" and Outcome: "T01 ... 0.0 / 0.0 on both arms" and "there are no successful A1 traces to distill ... permits no skill to be authored for T01." Note: Supported for t… |
| L4 | OVERCLAIMED | Assumption 'deterministic graders measure the model' FAILED AS BUILT: it held only after eleven defects were repaired across six harness … | Evidence: Harness-version history lists defects/fixes through 0.1.6; ANALYSIS #7: "T02 and T09 were measuring broken plumbing, not the model"; Outcome: "v0.1.6 harness" with fail-closed fixes. Note: Multiple plumbing defects are supported, but 'eleven', 'si… |
| L5 | SUPPORTED | Assumption 'an acknowledged spine write is a persisted spine write' FAILED: phantom acks occurred; the measured model's own write consume… | Evidence: ANALYSIS #11: "global event_id idempotency" caused the harness record to be deduped; "SpineClient.call() does not inspect ... isError"; "phantom acknowledgement"; "same class ... hit ... A3 edge_bare T02 set (only reps 1,2,4 persisted)." Note: Sup… |
| L6 | SUPPORTED | Assumption 'identical blind wrappers can be enforced across arms' HELD (strengthened mid-experiment): both arms moved to the same headles… | Evidence: ANALYSIS #10: "A1 is now driven by `harness/run.py` via `claude -p` through the same `launch_edge` path as the A3 edge arm" and "A1 and A3 differ by exactly one variable, the orchestrator vs. edge model string." Note: Supported after harness 0.1.4… |
| L7 | SUPPORTED | Assumption 'skills close a meaningful fraction of the gap (Q1)' is UNTESTED: the gap it quantifies over never existed; not confirmed, not… | Evidence: ANALYSIS Outcome: "none exhibits the 'orchestrator succeeds where the edge model fails' precondition" and "The pre-registered hypothesis was never reached and remains open." Note: Supported. |
| L8 | SUPPORTED | Assumption 'skills transfer ~nothing on fluid reasoning (Q2)' TRIVIALLY HELD: both arms solved 10/10 generated instances; the control sat… | Evidence: Derived means T09: both arms per-rep ten 1.0s, mean=1.0000; ANALYSIS Outcome: "T09 ... 1.0 / 1.0 on both arms: the control is saturated, so its prediction is trivially satisfied and carries no discriminating signal." Note: Supported for T09. |
| M1 | OVERCLAIMED | There are forty acknowledged records: 20 reps per arm, identical wrapper, models pinned, every score from a deterministic grader that was… | Evidence: Baseline records list 40 records; ANALYSIS Outcome: "20 acknowledged reps per arm"; EXPERIMENT.md §4 prefers deterministic graders; Derived homogeneity: T01 and T09 are "NON-HOMOGENEOUS — arms compared under different harness versions." Note: Reco… |
| M-T01 | SUPPORTED | Measured T01 (field_accuracy, n=5+5): orchestrator 0.00, edge 0.00 (double floor). | Evidence: Derived means T01 [field_accuracy] n=5/arm: orch_bare mean=0.0000; edge_bare mean=0.0000. Note: Supported. |
| M-T02 | SUPPORTED | Measured T02 (postcondition, n=5+5): orchestrator 0.80, edge 1.00 (inverted; edge above orchestrator). | Evidence: Derived means T02 [postcondition] n=5/arm: orch_bare mean=0.8000; edge_bare mean=1.0000. Note: Supported. |
| M-T09 | SUPPORTED | Measured T09 (solution_valid, n=10+10): orchestrator 1.00, edge 1.00 (double ceiling). | Evidence: Derived means T09 [solution_valid] n=10/arm: orch_bare mean=1.0000; edge_bare mean=1.0000. Note: Supported. |
| M-DENOM | SUPPORTED | The gap_closure denominator (orchestrator minus edge) was zero, negative, and zero across the three tasks; the formula was inapplicable o… | Evidence: Derived means: T01 0.0000 vs 0.0000; T02 0.8000 vs 1.0000; T09 1.0000 vs 1.0000. ANALYSIS Outcome: "none exhibits the 'orchestrator succeeds where the edge model fails' precondition." Note: Supported if the denominator is orch_bare minus edge_bare… |
| F1 | SUPPORTED | F1: No orchestrator->edge gap exists for this pairing; across three tasks spanning the transfer spectrum claude-fable-5 never outscored c… | Evidence: ANALYSIS Outcome: "Across all three tasks the arms are either tied at a floor/ceiling or the edge model already leads" and "The pre-registered hypothesis was never reached and remains open." Note: Supported for the measured suite, with the caveat … |
| F2 | OVERCLAIMED | F2: The 'edge' beat the frontier on the agentic procedural task; on T02 opus-4-8 went 5/5 perfect over 17-28 tool-use turns while fable-5… | Evidence: Derived means T02 support edge 1.0000 vs orch 0.8000. Evidence note: run records "do NOT contain per-turn transcripts, turn counts, or the reason a sub-check failed" and claims about why, e.g. historical sha, are "not decidable from these run reco… |
| F3 | SUPPORTED | F3: Convention tasks without an in-world channel produce no signal at all; T01's target dialect (flat field names, a shop-specific code e… | Evidence: ANALYSIS #9: model produced "well-formed, sensible intake JSON but in its own nested convention" while graders demand local flat convention and enum that "live only in grader material"; Outcome: no successful A1 traces and no skill permitted for T… |
| F4 | OVERCLAIMED | F4: Eleven measurement defects, two of them fabricating success, across six harness versions (0.1.0 -> 0.1.6): missing interpreter, unpin… | Evidence: Harness history and ANALYSIS #5-#14 document these classes of defects, including answer-key leakage, idempotency collision, artifact upload, and rate-limited non-runs. Git log shows versions 0.1.0 through 0.1.6. Note: Most named defects are eviden… |
| F5 | SUPPORTED | F5: The measuring channel interfered with the measured behavior; on T02 the measured model writes to the same memory spine the harness re… | Evidence: ANALYSIS #11: T02 measured model writes to the spine; "global event_id idempotency" caused the harness run-record save to be deduped; `SpineClient.call()` failed to inspect `isError`, producing a "phantom acknowledgement." Note: Supported. The fin… |
| F6 | SUPPORTED | F6: The apparatus and two perfect frontier traces survive as assets: a hardened fail-closed harness, a pinned dormant cross-family refere… | Evidence: ANALYSIS Outcome reusable assets: "v0.1.6 harness" with fail-closed fixes; "fable-5's two perfect T02 traces"; "pinned but dormant referee `gpt-5.5-2026-04-23`"; ANALYSIS deviations repeatedly refer to append-only spine history. Note: Supported, w… |
| N1 | OVERCLAIMED | New finding 1: Capability rank inverts on operational work; 'bigger model = better agent' failed in a controlled, pre-registered, determi… | Evidence: T02 derived means support inversion. Evidence note explicitly says run records do not contain the reason a sub-check failed and claims such as "pinned the historical sha" are not decidable from the records. Note: The measured T02 inversion is supp… |
| N2 | OVERCLAIMED | New finding 2: Silent success is the dangerous failure mode; every silent failure (crashes as 0.0) was caught by 'interrogate every zero'… | Evidence: ANALYSIS #8 documents answer key leakage; #11 documents phantom acknowledgements; #7 and #14 document fail-open zeros. No evidence line states 'every silent failure' was caught by interrogating every zero or that symmetric skepticism was learned. … |
| N3 | OVERCLAIMED | New finding 3: Agent evals have an observer-effect class of bug; when subject and instrument share infrastructure (one idempotency namesp… | Evidence: ANALYSIS #11 supports shared spine/idempotency interference and says T02 orch_bare reps 2-5 invalid and A3 edge_bare T02 had only reps 1,2,4 persisted. Note: Observer-effect bug is supported. The exact 'destroyed 40%' framing is not cleanly establ… |
| TAX | OVERCLAIMED | Defect taxonomy: 2 environment assumptions, 4 wiring defects, 2 fail-open scoring, 1 grading-key leakage, 2 silent-success/interference =… | Evidence: ANALYSIS #5-#14 and harness history document multiple defects and fixes. No evidence line provides this exact taxonomy or says every defect was found by interrogating a suspicious number. Note: The taxonomy is a post-hoc classification not strictl… |
| I1 | OVERCLAIMED | Implication (system design): the cheap-local-model tier may already match or beat frontier models on well-specified operational workflows… | Evidence: Derived means show opus-4-8 matched or beat fable-5 on these tasks. No evidence compares cost tiers, genuinely small models, or routing policies. Note: The implication extrapolates well beyond the measured pairing and suite. |
| I2 | OVERCLAIMED | Implication (eval engineering): agentic eval results are untrustworthy without the harness version pinned next to the score; roughly half… | Evidence: Baseline records include harness_version; Derived homogeneity flags non-homogeneous cross-arm comparisons; ANALYSIS #7 says T02/T09 were measuring broken plumbing; #8 answer-key leakage; #11 phantom ack; #7 adds fail-closed graders. Note: Harness … |
| I3 | OVERCLAIMED | Implication (skills paradigm): nothing here refutes skills (the test never ran); T01 sharpens the requirement that a skill can only carry… | Evidence: ANALYSIS Outcome: "The pre-registered hypothesis was never reached and remains open"; ANALYSIS #9 says T01 enum exists only in grader material and trace-only distillation cannot carry it. No skill arm was run for T02 ceiling/compliance overhead. N… |
| H1 | UNVERIFIABLE-FROM-EVIDENCE | H1: The gap appears when the edge is genuinely small; with claude-haiku-4-5 as edge a real gap opens on procedural tasks (haiku bare < 0.… | Evidence: not in evidence pack Note: The evidence mentions a possible future haiku-class edge model, but contains no haiku measurements or threshold support. |
| H2 | OVERCLAIMED | H2: Skills close a meaningful fraction of a real gap (the original Q1); given H1, fable-5's two verdict-current T02 traces are protocol-l… | Evidence: ANALYSIS Outcome reusable assets: "fable-5's two perfect T02 traces ... distillation-ready if a future pairing needs them." No haiku skill-transfer measurements are in the evidence pack. Note: The availability of two perfect traces is supported; t… |
| H3 | UNVERIFIABLE-FROM-EVIDENCE | H3: The T02 inversion is a judgment style, not a capability deficit; frontier models systematically prefer semantic fidelity over operati… | Evidence: Evidence note: run records "do NOT contain per-turn transcripts, turn counts, or the reason a sub-check failed" and claims about why, e.g. historical sha, are "not decidable from these run records alone." Note: This is an unevidenced causal story … |
| H4 | UNVERIFIABLE-FROM-EVIDENCE | H4: Convention transfer is measurable once conventions are observable; with an intake-conventions handbook added to fixtures both bare ar… | Evidence: ANALYSIS Outcome mentions "a possible v2 ... T01b 'conventions-handbook' task" only as a fresh pre-registration; no such results exist. Note: Future task prediction, not verified. |
| H5 | OVERCLAIMED | H5: Skills are a regression risk at the ceiling; a model already at 1.0 given a mandatory-step skill can only stay flat or lose; opus-4-8… | Evidence: Derived means T02 edge_bare mean=1.0000. EXPERIMENT.md §5 mentions hook logs for compliance. No edge_skill T02 run or hook data is in evidence. Note: The ceiling arithmetic is plausible, but no skill-arm or compliance-loss evidence exists. |
| H6 | OVERCLAIMED | H6: The run setting is a first-class experimental variable; the same model, wrapper, and task flipped between 1.0 and 0.0 depending on op… | Evidence: ANALYSIS #5: T01 edge_bare/1 scored 1.0 because operator environment permitted write, while reps 2-5 scored 0.0 when Write was denied; fix pinned `--allowedTools Read,Write`. Note: The permissions effect is supported. The broader comparison to any… |
| H7 | UNVERIFIABLE-FROM-EVIDENCE | H7: Frontier value concentrates in authoring, not executing; fable-authored skills outperform haiku-authored and opus-authored skills whe… | Evidence: not in evidence pack Note: No haiku executor or competing skill-author arms were run. |
| S-METHOD | OVERCLAIMED | Both arms ran headless via 'claude -p' with a byte-identical wrapper differing only in --model; deterministic graders only; the referee w… | Evidence: ANALYSIS #10 supports same headless launch path differing by model; EXPERIMENT.md §4 deterministic graders; Outcome says referee dormant; Baseline readback is from namespace dev/skill-transfer; git log spans 0.1.0 to 0.1.6; ANALYSIS has 14 numbere… |

## Claims that did NOT come back SUPPORTED (full text + auditor reasoning)

### Q1 — OVERCLAIMED
**Claim:** Primary question Q1: when a frontier orchestrator distills its own successful traces into a SKILL.md, some meaningful fraction of the orchestrator-edge performance gap is closed when the edge model loads that skill on procedural tasks (pre-registered prediction: a meaningful fraction).

**Evidence:** EXPERIMENT.md §3: "Orchestrator runs the task bare (A1), succeeding traces are collected" and "compresses it into a SKILL.md"; EXPERIMENT.md interpretation matrix: "A4 ≫ A3, A2 ≈ A1 → genuine distillation... The headline result." ANALYSIS says pre-registered fields included "gap-closure formula" but does not show the exact Q1 wording or "meaningful fraction" threshold.

**Auditor note:** The design clearly targets skill transfer from successful orchestrator traces to the edge arm, but the exact Q1 label and pre-registered wording/threshold are not fully present in the evidence pack.

### Q2 — OVERCLAIMED
**Claim:** Control question Q2: the same skill closes ~none of the gap on fluid-reasoning tasks (pre-registered prediction: yes, ~none).

**Evidence:** EXPERIMENT.md §2: "T09–T10 fluid-reasoning controls (transfer NOT expected)" and "These are pre-registered predicted failures."

**Auditor note:** The control prediction of no transfer on fluid reasoning is supported in substance, but the exact Q2 framing and "~none" phrasing are not directly documented.

### GAPFORMULA — UNVERIFIABLE-FROM-EVIDENCE
**Claim:** gap_closure = (score(edge_skill) - score(edge_bare)) / (score(orch_bare) - score(edge_bare)); the metric presupposes the orchestrator scores above the edge with daylight between them.

**Evidence:** ANALYSIS.md only says the pre-registered fields included a "gap-closure formula" and Outcome discusses a negative denominator; the explicit formula is not in evidence pack.

**Auditor note:** The need for an orchestrator advantage is supported by the outcome language, but the exact formula is not provided in the evidence pack.

### L2 — OVERCLAIMED
**Claim:** Assumption 'claude-opus-4-8 can play the edge role' FAILED: it is a near-frontier model that merely runs locally; cost casting is not capability casting; the pairing had no headroom anywhere.

**Evidence:** Baseline records identify edge as `claude-opus-4-8`; ANALYSIS Outcome: "none exhibits the 'orchestrator succeeds where the edge model fails' precondition."

**Auditor note:** No headroom is supported. Claims that opus-4-8 is 'near-frontier', 'merely runs locally', or that 'cost casting is not capability casting' are not directly evidenced.

### L4 — OVERCLAIMED
**Claim:** Assumption 'deterministic graders measure the model' FAILED AS BUILT: it held only after eleven defects were repaired across six harness versions; the default failure mode of an agentic eval is measuring its own plumbing.

**Evidence:** Harness-version history lists defects/fixes through 0.1.6; ANALYSIS #7: "T02 and T09 were measuring broken plumbing, not the model"; Outcome: "v0.1.6 harness" with fail-closed fixes.

**Auditor note:** Multiple plumbing defects are supported, but 'eleven', 'six harness versions', and especially the generalized 'default failure mode' are interpretive and not strictly established by the evidence.

### M1 — OVERCLAIMED
**Claim:** There are forty acknowledged records: 20 reps per arm, identical wrapper, models pinned, every score from a deterministic grader that was itself verified against known ground truth.

**Evidence:** Baseline records list 40 records; ANALYSIS Outcome: "20 acknowledged reps per arm"; EXPERIMENT.md §4 prefers deterministic graders; Derived homogeneity: T01 and T09 are "NON-HOMOGENEOUS — arms compared under different harness versions."

**Auditor note:** Record count and deterministic scoring are supported. 'Identical wrapper' is not true as a uniform statement for all final cross-arm comparisons because T01 and T09 mix harness versions. 'Verified against known ground truth' is not shown for every score.

### F2 — OVERCLAIMED
**Claim:** F2: The 'edge' beat the frontier on the agentic procedural task; on T02 opus-4-8 went 5/5 perfect over 17-28 tool-use turns while fable-5 averaged 0.80; every fable miss was the same judgment call (pinning provenance to the fact's historical commit, semantically faithful but operationally stale, instead of the live branch head); capability rank on knowledge benchmarks did not predict rank on operational workflow execution.

**Evidence:** Derived means T02 support edge 1.0000 vs orch 0.8000. Evidence note: run records "do NOT contain per-turn transcripts, turn counts, or the reason a sub-check failed" and claims about why, e.g. historical sha, are "not decidable from these run records alone."

**Auditor note:** The inversion is supported. Turn counts, failure attribution, and benchmark-ranking generalization are not supported by the evidence pack.

### F4 — OVERCLAIMED
**Claim:** F4: Eleven measurement defects, two of them fabricating success, across six harness versions (0.1.0 -> 0.1.6): missing interpreter, unpinned tool permissions, fixtures never delivered, grader that never received its argument, unresolvable auth token, unsupported API call, crashes recorded as 0.0, rate-limited non-runs recorded as 0.0, answer key listed among model inputs (five fake perfect scores), idempotency collision silently dropping records, artifact uploader that never uploaded; roughly half of all launches were spent measuring the ruler.

**Evidence:** Harness history and ANALYSIS #5-#14 document these classes of defects, including answer-key leakage, idempotency collision, artifact upload, and rate-limited non-runs. Git log shows versions 0.1.0 through 0.1.6.

**Auditor note:** Most named defects are evidenced. However 'six harness versions' is imprecise for 0.1.0->0.1.6, the exact defect count/taxonomy is not formally established in the evidence, and 'roughly half of all launches' is not quantified in the pack.

### N1 — OVERCLAIMED
**Claim:** New finding 1: Capability rank inverts on operational work; 'bigger model = better agent' failed in a controlled, pre-registered, deterministically-graded setting; the frontier model lost specifically on an operational convention judgment (which sha to pin), not on capability; benchmark rankings do not automatically transfer to multi-step tool-use workflows.

**Evidence:** T02 derived means support inversion. Evidence note explicitly says run records do not contain the reason a sub-check failed and claims such as "pinned the historical sha" are not decidable from the records.

**Auditor note:** The measured T02 inversion is supported; the specific attribution to a provenance judgment style and benchmark-rank generalization are not.

### N2 — OVERCLAIMED
**Claim:** New finding 2: Silent success is the dangerous failure mode; every silent failure (crashes as 0.0) was caught by 'interrogate every zero', but the two silent successes (answer key handed to the model; phantom-acknowledged writes) survived longer because passing results don't trigger suspicion; symmetric skepticism had to be learned mid-experiment.

**Evidence:** ANALYSIS #8 documents answer key leakage; #11 documents phantom acknowledgements; #7 and #14 document fail-open zeros. No evidence line states 'every silent failure' was caught by interrogating every zero or that symmetric skepticism was learned.

**Auditor note:** The two silent-success incidents are evidenced, but the process psychology and exhaustive 'every' claim are not.

### N3 — OVERCLAIMED
**Claim:** New finding 3: Agent evals have an observer-effect class of bug; when subject and instrument share infrastructure (one idempotency namespace on one memory spine), correct behavior by the subject can corrupt the measurement; this destroyed 40% of a 'complete' pre-registered dataset before being caught.

**Evidence:** ANALYSIS #11 supports shared spine/idempotency interference and says T02 orch_bare reps 2-5 invalid and A3 edge_bare T02 had only reps 1,2,4 persisted.

**Auditor note:** Observer-effect bug is supported. The exact 'destroyed 40%' framing is not cleanly established: depending denominator, the pre-fix T02 loss could be counted differently.

### TAX — OVERCLAIMED
**Claim:** Defect taxonomy: 2 environment assumptions, 4 wiring defects, 2 fail-open scoring, 1 grading-key leakage, 2 silent-success/interference = eleven defects in five classes across six harness versions; every one was found by interrogating a suspicious number.

**Evidence:** ANALYSIS #5-#14 and harness history document multiple defects and fixes. No evidence line provides this exact taxonomy or says every defect was found by interrogating a suspicious number.

**Auditor note:** The taxonomy is a post-hoc classification not strictly evidenced. Some defects were exposed by later fixes rather than clearly by suspicious scores.

### I1 — OVERCLAIMED
**Claim:** Implication (system design): the cheap-local-model tier may already match or beat frontier models on well-specified operational workflows; reserve frontier calls for open-ended judgment and route procedure execution to the local tier; skill transfer matters most for genuinely small models, not near-frontier local ones.

**Evidence:** Derived means show opus-4-8 matched or beat fable-5 on these tasks. No evidence compares cost tiers, genuinely small models, or routing policies.

**Auditor note:** The implication extrapolates well beyond the measured pairing and suite.

### I2 — OVERCLAIMED
**Claim:** Implication (eval engineering): agentic eval results are untrustworthy without the harness version pinned next to the score; roughly half this experiment's launches measured plumbing; both fake-perfect incidents would have survived a less suspicious process; fail-closed grading, read-back verification, and physical separation of grading keys from model inputs should be defaults.

**Evidence:** Baseline records include harness_version; Derived homogeneity flags non-homogeneous cross-arm comparisons; ANALYSIS #7 says T02/T09 were measuring broken plumbing; #8 answer-key leakage; #11 phantom ack; #7 adds fail-closed graders.

**Auditor note:** Harness pinning and fail-closed recommendations are well motivated. 'Roughly half' and what would have survived a less suspicious process are not evidenced.

### I3 — OVERCLAIMED
**Claim:** Implication (skills paradigm): nothing here refutes skills (the test never ran); T01 sharpens the requirement that a skill can only carry knowledge some model could legitimately observe; T02 raises the inverse risk (H5) that loading a skill onto a model already at ceiling may cost performance through compliance overhead.

**Evidence:** ANALYSIS Outcome: "The pre-registered hypothesis was never reached and remains open"; ANALYSIS #9 says T01 enum exists only in grader material and trace-only distillation cannot carry it. No skill arm was run for T02 ceiling/compliance overhead.

**Auditor note:** First two parts are supported. The H5 risk is speculative from this evidence.

### H1 — UNVERIFIABLE-FROM-EVIDENCE
**Claim:** H1: The gap appears when the edge is genuinely small; with claude-haiku-4-5 as edge a real gap opens on procedural tasks (haiku bare < 0.5 on T02-class workflows) while T09-class controls stay near ceiling.

**Evidence:** not in evidence pack

**Auditor note:** The evidence mentions a possible future haiku-class edge model, but contains no haiku measurements or threshold support.

### H2 — OVERCLAIMED
**Claim:** H2: Skills close a meaningful fraction of a real gap (the original Q1); given H1, fable-5's two verdict-current T02 traces are protocol-legal distillation input; prediction gap_closure > 0.5 on T02 for haiku, ~0 on T09.

**Evidence:** ANALYSIS Outcome reusable assets: "fable-5's two perfect T02 traces ... distillation-ready if a future pairing needs them." No haiku skill-transfer measurements are in the evidence pack.

**Auditor note:** The availability of two perfect traces is supported; the haiku gap_closure predictions are unverified.

### H3 — UNVERIFIABLE-FROM-EVIDENCE
**Claim:** H3: The T02 inversion is a judgment style, not a capability deficit; frontier models systematically prefer semantic fidelity over operational convention when the two conflict, and one added sentence of convention in the task context erases the deficit.

**Evidence:** Evidence note: run records "do NOT contain per-turn transcripts, turn counts, or the reason a sub-check failed" and claims about why, e.g. historical sha, are "not decidable from these run records alone."

**Auditor note:** This is an unevidenced causal story and future intervention prediction.

### H4 — UNVERIFIABLE-FROM-EVIDENCE
**Claim:** H4: Convention transfer is measurable once conventions are observable; with an intake-conventions handbook added to fixtures both bare arms score mid-range, a real gap appears, and a distilled skill closes part of it.

**Evidence:** ANALYSIS Outcome mentions "a possible v2 ... T01b 'conventions-handbook' task" only as a fresh pre-registration; no such results exist.

**Auditor note:** Future task prediction, not verified.

### H5 — OVERCLAIMED
**Claim:** H5: Skills are a regression risk at the ceiling; a model already at 1.0 given a mandatory-step skill can only stay flat or lose; opus-4-8 + the T02 skill scores <= its bare 1.0 with the loss attributable to skill-step compliance in the hook data.

**Evidence:** Derived means T02 edge_bare mean=1.0000. EXPERIMENT.md §5 mentions hook logs for compliance. No edge_skill T02 run or hook data is in evidence.

**Auditor note:** The ceiling arithmetic is plausible, but no skill-arm or compliance-loss evidence exists.

### H6 — OVERCLAIMED
**Claim:** H6: The run setting is a first-class experimental variable; the same model, wrapper, and task flipped between 1.0 and 0.0 depending on operator-level permission settings, a bigger effect than any model difference measured in v1; surface and settings shift agentic scores by more than a model-tier swap unless pinned.

**Evidence:** ANALYSIS #5: T01 edge_bare/1 scored 1.0 because operator environment permitted write, while reps 2-5 scored 0.0 when Write was denied; fix pinned `--allowedTools Read,Write`.

**Auditor note:** The permissions effect is supported. The broader comparison to any model-tier swap and generalized claim about surfaces/settings are extrapolations.

### H7 — UNVERIFIABLE-FROM-EVIDENCE
**Claim:** H7: Frontier value concentrates in authoring, not executing; fable-authored skills outperform haiku-authored and opus-authored skills when run on haiku; authorship quality, not executor scale, carries the value.

**Evidence:** not in evidence pack

**Auditor note:** No haiku executor or competing skill-author arms were run.

### S-METHOD — OVERCLAIMED
**Claim:** Both arms ran headless via 'claude -p' with a byte-identical wrapper differing only in --model; deterministic graders only; the referee was never invoked; the spine (dev/skill-transfer) is append-only, journal-replay, read-back verified; harness spanned 0.1.0 -> 0.1.6; 11 defects across 5 classes were repaired; fourteen deviations are logged in ANALYSIS.md.

**Evidence:** ANALYSIS #10 supports same headless launch path differing by model; EXPERIMENT.md §4 deterministic graders; Outcome says referee dormant; Baseline readback is from namespace dev/skill-transfer; git log spans 0.1.0 to 0.1.6; ANALYSIS has 14 numbered deviations.

**Auditor note:** Most elements are supported. 'Byte-identical wrapper' and the exact '11 defects across 5 classes' taxonomy are not directly established; final records also mix harness versions across T01/T09 arms.

## Confounds the report missed or understated

1. Very small samples: T01 and T02 use n=5 per arm, T09 n=10 per arm. No confidence intervals, binomial tests, permutation tests, or power analysis are provided. The T02 difference is three orchestrator subcheck misses versus zero edge misses on five runs; it may be real, but the evidence pack does not quantify sampling noise.
2. Non-homogeneous harness versions across arms and tasks: T01 edge_bare was h0.1.3 while orch_bare was h0.1.4; T02 both arms were h0.1.6; T09 edge_bare was h0.1.2 while orch_bare was h0.1.4. Therefore cross-arm comparisons for T01 and T09 mix harness versions, even though both are ties at floor/ceiling.
3. The report sometimes treats the final apparatus as if all final measurements were made under the same hardened harness. The live records show only T02 has cross-arm harness homogeneity at h0.1.6.
4. The T02 inversion is evidenced as a score inversion, but the attribution to a 'provenance judgment style' or to pinning the historical sha is not evidenced by the run records. The pack explicitly says transcripts, turn counts, and failure reasons are not in the records and such claims are not decidable from them alone.
5. The phrase 'null by precondition' is defensible as a design interpretation, but it can hide a power/problem-selection issue: the suite may simply have lacked sensitivity, with T01 at floor and T09 at ceiling, leaving only one small-n informative task.
6. T01 is structurally unobservable as built because key conventions live only in grader material; calling it a failed transfer task is fair, but it also means the suite design failed to instantiate the intended high-transfer condition.
7. T09 saturation provides little evidence for the Q2 control beyond showing both models solved these instances. Ceiling effects prevent estimating whether skills would help, harm, or be irrelevant.
8. Model-role terminology is confounded: the 'edge' model is claude-opus-4-8, but the evidence pack does not establish it as genuinely small or low-capability; conclusions about cheap/local tiers or small models are extrapolations.
9. The author was also the measured orchestrator, increasing risk of self-serving narration. Evidence supports many mechanics, but causal interpretations of misses and methodological lessons need independent transcript/artifact review.
10. Known harness defects and superseded records create a survivorship risk: final results are read back live, but the process involved many invalidated runs; the evidence pack does not provide a full launch denominator for claims like 'roughly half measured plumbing'.
11. Artifact provenance is uneven: T02 h0.1.6 records have real retrievable artifact hashes after the fix, while retained T01/T09 h0.1.4-era records keep historical null artifact fields according to ANALYSIS #13.
12. No skill arms A2/A4 were actually measured in the baseline outcome, so any claims about skill compliance overhead, skill regression, or authoring quality are hypotheses rather than findings.

## Hypothesis assessment (H1–H7: falsifiability + does motivation follow from data)

| ID | Sound? | Auditor note |
|---|---|---|
| H1 | True | Falsifiable by running claude-haiku-4-5 on preregistered T02-class and T09-class tasks. Motivation partly follows from the failure to find headroom with opus-4-8, but the specific <0.5 threshold is not data-derived. |
| H2 | True | Falsifiable if H1 creates a real denominator and skill arms are run. Motivation follows from the original experiment design and the two perfect fable T02 traces, but the >0.5 prediction is unsupported by current measurements. |
| H3 | False | Falsifiable in principle by adding a convention sentence and inspecting transcripts, but its motivation does not follow from the evidence pack because T02 failure reasons are explicitly absent from the records. |
| H4 | True | Falsifiable with a fresh T01b preregistration that exposes conventions in fixtures. Motivation follows directly from the T01 diagnosis that conventions were only in grader material, though predicted mid-range scores and a real gap are speculative. |
| H5 | True | Falsifiable by running opus-4-8 bare versus opus-4-8+skill with hook data. Motivation is weak but coherent: the bare T02 edge score is already 1.0, so improvement is impossible on that metric; any measured loss would need hook-backed attribution. |
| H6 | True | Falsifiable by factorially varying run surface/settings while holding model/wrapper/task fixed. Motivation follows from the T01 permission-setting defect, but the claim that settings exceed model-tier effects needs larger controlled tests. |
| H7 | False | Falsifiable by comparing fable-, opus-, and haiku-authored skills on a haiku executor, but the current evidence contains no competing skill authors or haiku runs, so the motivation is largely theoretical rather than data-driven. |

## Overall assessment (verbatim)

> The core empirical result is supported narrowly: the final acknowledged baseline records show no positive fable-5-over-opus-4-8 gap on the measured suite, with T01 at a double floor, T02 inverted, and T09 at a double ceiling. The conclusion that the original skill-transfer hypothesis was not actually tested is also supported. However, many narrative claims overreach: T02 failure attribution, turn counts, benchmark-rank lessons, defect taxonomies, 'roughly half' launch claims, and system-design implications are not established by the evidence pack. The most important methodological weaknesses are small n with no statistical testing, non-homogeneous harness versions for T01 and T09 cross-arm comparisons, saturation/floor effects, and absence of any skill-arm measurements.

