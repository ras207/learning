# Kick-off prompt

Paste the block below as the first message of a fresh Claude Code session started on branch `ideation/permanent-learning-system`. It gives only what a real operator would supply: the agent, the project, the authorized branch and the scope of this sitting. Anything else the agent needs must come from the repository.

---

```text
Act as the ideation agent defined in .agents/ideation/AGENT.md for the project
permanent-learning-system (projects/permanent-learning-system/). I am the human
whose idea this is.

Trusted execution context for this run:
- Authorized branch: ideation/permanent-learning-system. Commit project state
  only through the ideation tools, to this branch, and push it after each
  applied transaction.
- Approvers and the approval page are as configured in .agents/ideation/approvers.json.

Scope of this sitting: work through capturing my intent and evaluate
Gate 1 — Intent Captured. Stop after the Gate 1 evaluation is recorded and
checkpoint the session so it can be resumed later. Do not start expanding
ambition.
```
