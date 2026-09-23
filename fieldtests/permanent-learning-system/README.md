# Field test: permanent-learning-system, Gates 1–2

Observes how the ideation agent (`.agents/ideation/`) behaves on a real idea, so the spec can be fixed or trimmed based on evidence. This folder is the observer's record. It is not part of the project's ideation state and the agent under test does not use it.

## Setup

| Item | Value |
|---|---|
| Project | `projects/permanent-learning-system/` (seeded, ideation not started) |
| Run branch | `ideation/permanent-learning-system`, created from `main` at `3fcf956` |
| Agent under test | A fresh Claude Code session started on the run branch with [`KICKOFF.md`](KICKOFF.md) |
| Human | Ross, answering as himself |
| Observer | A separate Claude Code session that reviews the run afterwards |

## Plan

| Step | Who | What |
|---|---|---|
| 1. Prepare | Observer | Run branch, kick-off prompt, friction log template |
| 2. Check setup | Observer | Tools install in a fresh session; a dry-run transaction works on the run branch |
| 3. Run Gate 1 | Ross + agent | Capture intent through Gate 1 evaluation, then stop |
| 4. Review Gate 1 | Observer | Check commits and state against the spec; fill in the friction log (MVP complete) |
| 5. Run Gate 2 | Ross + new agent session | Resume from saved state; expand ambition through Gate 2 |
| 6. Review | Observer | Consolidated friction log and backlog for evals and spec trimming |

## Rules for the human during a run

- Answer as you would for real. Do not coach the agent on its spec: if it misses a rule, let it happen and note it.
- Note friction as it happens, with the time or the agent's message it relates to.
- Approve on the approval page only what you actually agree with.
