# Referee call assembly (built per judgment by harness/run.py)

Order of assembled content:

1. `referee/rubric.md` verbatim (its sha256 must equal the rubric hash pinned in the run record).
2. The task's `rubric_addendum.md`, if the file exists (correctness anchors only).
3. The task prompt, verbatim, under a `## Task specification` header.
4. Blinded payloads:

   ## Response A
   {payload_a}

   ## Response B
   {payload_b}

5. Output instruction, verbatim:

   Respond with JSON only, conforming to the RefereeJudgment schema provided below. No prose
   outside the JSON. {referee_output_schema_json}

## Position-swap rule

Every pairwise judgment is issued twice: once as assembled above, once with the contents of
{payload_a} and {payload_b} exchanged (headers stay "Response A"/"Response B"). Both verdicts are
recorded; preference is position_consistent only if its direction survives the swap.

## Blinding rule (applied before assembly)

Strip from both payloads: model names, arm labels, skill names/paths, spine keys and namespaces,
run ids, and any harness-known signature markers. The referee is never told which systems are
being compared.
