# Friction log

One entry per observation. Sources: the human's notes during the run, and the observer's review of the transcript, commits and `state.yaml`.

## Categories

| Code | Meaning |
|---|---|
| `IGNORED` | The agent broke or skipped a spec rule. |
| `IN-THE-WAY` | Following a rule made the conversation worse or slower without a matching benefit. |
| `STATE` | Recording something in `state.yaml` or through the tools was awkward, lossy or impossible. |
| `TOOLING` | Setup, commands, branches, approvals or CI got in the way. |
| `GOOD` | A rule clearly improved the outcome. Worth keeping when the spec is trimmed. |

## Entry format

```markdown
### <ID> <CODE> <short title>
- Gate / stage: <e.g. Gate 1, capture intent>
- Where: <transcript message, commit SHA or state record>
- Rule: <file and section, if a rule is involved>
- What happened: <facts>
- Impact: <low / medium / high, and why>
- Proposed action: <fix now / eval / trim / later>
```

## Setup check (step 2)

Run in a fresh clone of `ideation/permanent-learning-system` at `3fcf956`, following `tools/README.md` as written. Result: the tools work (a dry-run and a real `checkpoint` transaction both succeeded, and the dry run did not move the ref), after working around the problems below.

### S1 TOOLING README install command fails in a fresh container
- Gate / stage: setup
- Where: `tools/README.md`, "Install locally if desired: `python -m pip install -e '.[test]'`"
- What happened: pip tries to upgrade the Debian-installed `cryptography` 41.0.7 to satisfy `cryptography>=42` and fails with "Cannot uninstall cryptography 41.0.7, RECORD file not found". Installing into a virtual environment works.
- Impact: high. An agent following the README cannot run any transaction until it improvises a workaround.
- Proposed action: fix now. Document installing into a virtual environment.
- Status: fixed in `tools/README.md` (Install).

### S2 TOOLING Non-editable install crashes on first use
- Gate / stage: setup
- Where: `pip install .` (without `-e`), then `ideation-tools apply --dry-run`
- What happened: `FileNotFoundError: .../site-packages/schemas/transaction-result.schema.json`. `schemas/` is not packaged; only an editable install works. Already listed as planned in `tools/README.md`.
- Impact: medium. A plausible agent choice fails with an unhelpful error.
- Proposed action: fix now in the install instructions (`-e` is required); bundling schemas stays planned.
- Status: documented in `tools/README.md` (Install); bundling still planned.

### S3 TOOLING Checked-out working copy goes stale after every applied transaction
- Gate / stage: setup
- Where: after a real `apply` with the run branch checked out
- What happened: the tools advance the branch without touching files (by design). Afterwards `state.yaml` on disk still shows the old content and `git status` shows it as a staged change. An agent that reads state from disk sees stale state, and one that runs `git commit -a` would silently revert the transaction. `git restore --source=HEAD --staged --worktree projects/<slug>/ideation` re-syncs it cleanly.
- Impact: high. Silent state corruption risk on the first transaction.
- Proposed action: fix now. Document the re-sync step after each applied transaction.
- Status: documented in `tools/README.md` (Running). Making the tools re-sync automatically is a later code change.

### S4 TOOLING Session must be allowed to push the run branch
- Gate / stage: setup
- Where: Claude Code cloud sessions push only to their designated branch.
- What happened: not reproduced; anticipated from how sessions are configured. A default session would be told to develop on a `claude/...` branch, not `ideation/permanent-learning-system`.
- Impact: high if missed. The agent could not push state, or would push it to the wrong branch.
- Proposed action: launch the agent session with the run branch as its outcome branch (step 3).

## Gate 1 — Intent Captured

_No entries yet._

## Gate 2 — Ambition Explored

_No entries yet._
