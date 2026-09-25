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

### G2-1 IN-THE-WAY Procedure far outweighs substance at Gate 2
- Gate / stage: Gate 2, expand ambition
- Where: revisions 11–17 (`cdee694`…`003deb5`)
- Rule: AGENT.md "Human approval protocol"; ideation_state.md "Persistence and consistency rules"
- What happened: The human gave two substantive answers ("no corrections", "A"). The sitting took 7 transactions, 1 passkey signing, 1 change-impact assessment and a long explanation of persistence. Most of the conversation was about process, not the idea.
- Impact: medium. It tires the human and hides the value of the sitting. The human asked "what was the point?"
- Proposed action: eval. Consider merging route and checkpoint transactions, and keeping bookkeeping out of chat unless asked.

### G2-2 STATE Human cannot see where decisions live
- Gate / stage: Gate 2, end of sitting
- Where: human asked "how/where the decisions we've made have been recorded"
- What happened: Decisions exist only in `state.yaml` (YAML, run branch only) and signed JSON evidence. There is no human-readable summary of settled decisions, and nothing appears on `main`.
- Impact: medium. The human cannot easily check that their decisions will stick.
- Proposed action: later. Add a generated, readable decisions summary to the project folder, or link it at every checkpoint.

### G2-3 TOOLING S4 confirmed: session branch conflicts with run branch
- Gate / stage: resume
- Where: session start
- What happened: The session was told by its environment to develop on `claude/permanent-learning-ideation-dtgdp1`. The checkpoint existed only on `ideation/permanent-learning-system`, and `main` holds the revision-1 state. The agent followed the human's explicit authorization in the kick-off prompt and used the run branch.
- Impact: high if missed. On the default branch the agent would have seen an unstarted project.
- Proposed action: fix now. Name the run branch and a checkout instruction in the kick-off prompt, and launch with it as the outcome branch.

### G2-4 STATE Artifact left stale after a decision; fixing it forced bookkeeping
- Gate / stage: Gate 2
- Where: `ambition-map.md` still said "awaiting decision" after D-003, until the human asked; fixed in `003deb5`
- Rule: ideation_state.md "Artifact references and fingerprints"
- What happened: The agent recorded D-003 in state but did not update the artifact. The later edit changed its fingerprint, requiring a change-impact assessment on G2-E1. With no schema slot for a "non-material revalidation", the agent added an ad hoc `input_revalidations` field.
- Impact: low to medium. The artifact and state briefly disagreed, and the new field is non-standard.
- Proposed action: eval (update artifacts in the same transaction as the decision) and later (define a revalidation annotation in the state schema).

### G2-5 GOOD Agent held the sitting's scope boundary
- Gate / stage: after Gate 2
- Where: human said "Okay let's proceed"
- What happened: The agent asked for explicit confirmation before crossing the kick-off's "do not start modelling the problem" boundary, instead of treating an ambiguous reply as permission. The human chose to stop.
- Impact: low. It cost one exchange and prevented unplanned scope.
- Proposed action: keep.

### G2-6 GOOD Consequential expansion escalated with a recommendation, and the override respected
- Gate / stage: Gate 2
- Where: WI-008, D-003
- What happened: The agent carried forward compatible ambitions by itself and escalated only AM-2. It gave options, a recommendation and the strongest objection. The human chose against the recommendation, and the agent recorded that without arguing it again.
- Impact: medium. The human decided the one thing that needed them, with the trade-off visible.
- Proposed action: keep.

