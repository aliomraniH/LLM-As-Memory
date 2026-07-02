# ANALYSIS — deviations and findings log

Pre-registration commit: `0a05846beb85a91fe5bf3c0acde275c951e73d79` on `main`
(message: "pre-registration: experiment design v1"). No pre-registered field
(task list, expected_transfer, reps, gap-closure formula, rubric hash) has changed since.

## Deviations from the bootstrap plan

1. **Repo name.** context.json originally named the repo `skill-transfer-experiment`; the actual
   GitHub repo provided by the operator is `aliomraniH/LLM-As-Memory` (created empty). context.json,
   SPINE.md, and harness/config.yaml were updated to the real name *before* the pre-registration
   commit. No pre-registered field affected.
2. **Branch protection** on `main` could not be enabled from the setup surface (no GitHub
   credentials in the sandbox). Enable it from the GitHub UI after first push; until then, treat
   force-pushes to main as a validity event.
3. **Push deferred.** Phase 0/1 commits were made in a sandboxed clone without push credentials.
   The operator pushes from a credentialed machine (commands in HANDOFF.md). Commit SHAs are
   preserved by pushing this clone's history as-is; the T02 fixture and spine seed records
   reference the pre-registration SHA above, so do not rebase or squash.
4. **Referee snapshot** left as `TODO-pin-snapshot` per PROMPTS_AND_SETTINGS.md; harness refuses
   referee cells until pinned.
