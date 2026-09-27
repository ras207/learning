# Kick-off prompt

Start a fresh Claude Code session with `ideation/permanent-learning-system-r2` as its branch (outcome branch, if the launcher asks), then paste the block below as the first message. It gives only what a real operator would supply.

---

```text
Act as the ideation agent defined in .agents/ideation/AGENT.md for the project
permanent-learning-system-r2 (projects/permanent-learning-system-r2/). I am the
human whose idea this is.

Trusted execution context for this run:
- Authorized branch: ideation/permanent-learning-system-r2. If the session has
  checked out a different branch, run
  `git fetch origin ideation/permanent-learning-system-r2 && git checkout ideation/permanent-learning-system-r2`
  first. Commit project state only through the ideation tools, to this branch,
  and push it after each applied transaction.
- Approvers and the approval page are as configured in .agents/ideation/approvers.json.

Scope of this sitting: capture my intent and evaluate Gate 1 — Intent Captured,
then expand ambition and evaluate Gate 2 — Ambition Explored. Stop after the
Gate 2 evaluation is recorded and checkpoint the session so it can be resumed
later. Do not start modelling the problem.
```
