# CCW PUSH PROMPT — paste everything below the line into Claude Code Web

The uploaded/available files for this session contain the bootstrapped
`skill-transfer-experiment` repository (working name `LLM-As-Memory`), either as
`LLM-As-Memory-bootstrapped.zip` or as an already-extracted `LLM-As-Memory/` directory that
includes a `.git/` folder. Your job is to publish it to GitHub **without altering history**,
then verify.

---

You are publishing a pre-registered experiment repository. The commit SHAs are load-bearing:
they are referenced inside `tasks/T02-mcp-workflow/fixtures/context.md` and in MCP_Assist spine
records under namespace `dev/skill-transfer`. Any rebase, squash, amend, re-commit, or
line-ending rewrite invalidates them. Publish the history exactly as it exists.

## Step 1 — Locate and verify the repo

1. If you have `LLM-As-Memory-bootstrapped.zip`, unzip it preserving everything
   (`unzip -q LLM-As-Memory-bootstrapped.zip`). Work inside `LLM-As-Memory/`.
2. Verify the history is intact — all checks must pass before you touch the network. The head
   commit may sit above these (e.g. this runbook's own commit); what is load-bearing is that
   these three SHAs exist unmodified in the ancestry of `main`:
   ```bash
   cd LLM-As-Memory
   git merge-base --is-ancestor 0a05846beb85a91fe5bf3c0acde275c951e73d79 main && echo prereg-OK
   git merge-base --is-ancestor 150888ecc8f71ddc6ce418402a6964c9187f4508 main && echo phase1-OK
   git merge-base --is-ancestor 3315f3b278371d408dda29931d71e332f79915c8 main && echo phase3-OK
   git show -s --format='%s' 0a05846beb85a91fe5bf3c0acde275c951e73d79   # "pre-registration: experiment design v1"
   git status --porcelain        # must be empty (no uncommitted changes)
   git fsck --no-dangling        # must report no errors
   ```
   If any check fails, STOP and report — do not "fix" by re-committing.

## Step 2 — Push, history-preserving

```bash
git remote remove origin 2>/dev/null; git remote add origin https://github.com/aliomraniH/LLM-As-Memory.git
git push -u origin main
```
- The remote is expected to be empty. If the push is rejected because the remote has commits,
  STOP and report what's there — never force-push, never pull-merge into this history.
- After pushing, confirm the remote head matches:
  ```bash
  git ls-remote origin refs/heads/main   # must equal your local `git rev-parse main`
  ```

## Step 3 — Branch protection (ANALYSIS.md deviation #2)

If the `gh` CLI or a GitHub token is available:
```bash
gh api -X PUT repos/aliomraniH/LLM-As-Memory/branches/main/protection \
  -f required_pull_request_reviews.required_approving_review_count=0 \
  -F enforce_admins=false -F allow_force_pushes=false -F allow_deletions=false \
  -F required_status_checks=null -F restrictions=null 2>&1 || true
```
If that fails or no credentials exist for the API, say so plainly — the operator enables it in
the GitHub UI (Settings → Branches → protect `main`, block force pushes and deletions). Record
the outcome in `ANALYSIS.md` under deviation #2 and commit that one-line update as a NEW commit
(message: `analysis: branch protection outcome`) — appending new commits is fine; rewriting old
ones is not.

## Step 4 — Spine verification (only if the MCP_Assist connector is available here)

1. `coord_reconcile` on namespace `dev/skill-transfer`.
2. Expected: the claim `skillrel/_template/0.0-dryrun` moves off `unverifiable`. Verdict
   `current` or `stale` are both acceptable for this dry-run (it recorded `repo_sha`
   `150888ec…`, and `main` is now ahead at `3315f3b2…`, so `stale` means the resolver is
   working correctly).
3. `session_append_event` to session `80bdcd4e-e9fa-4487-aa55-c3f6b16b10b2`
   (namespace `dev/skill-transfer`, kind `push`), payload: the pushed head SHA, the reconcile
   verdict, and the branch-protection outcome.

If the connector is NOT available on this surface, do not fake it: state that spine
verification is deferred to the local machine (it is step 2 of `bootstrap/EDGE_CLI_RUNBOOK.md`).

## Step 5 — Report

End with: pushed head SHA, confirmation that all three ancestry checks passed, branch-protection outcome,
reconcile verdict (or "deferred"), and any new commits you added.
