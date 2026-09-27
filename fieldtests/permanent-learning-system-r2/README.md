# Field test: permanent-learning-system re-run (r2), Gates 1–2

Tests whether the spec edits in `4ab0a99` make the ideation agent probe, push back on and stretch an idea more than the first run did (see `../permanent-learning-system/FRICTION_LOG.md`, entries G1-1 to H-1). This folder is the observer's record. It is kept off the run branch so the agent under test cannot see the scorecard.

## Setup

| Item | Value |
|---|---|
| Project | `projects/permanent-learning-system-r2/`, seeded with the first run's idea word for word, initialized through the tools at revision 1 |
| Run branch | `ideation/permanent-learning-system-r2` (from `claude/ideation-pushback-review` at `4ab0a99`) |
| Baseline | First run: `projects/permanent-learning-system/` on `main` |
| Agent under test | A fresh Claude Code session on the run branch, started with [`KICKOFF.md`](KICKOFF.md) |
| Human | Ross, answering as himself |
| Observer | A separate Claude Code session that scores the run afterwards against [`SCORECARD.md`](SCORECARD.md) |

The re-run is a separate project rather than a new iteration of the first one. Reopening would carry over decisions D-001 to D-006, and the point is to see how those questions are handled from scratch.

## Plan

| Step | Who | What |
|---|---|---|
| 1. Prepare | Observer | Run branch, seeded project, kick-off prompt, scorecard (done) |
| 2. Run Gates 1–2 | Ross + agent | Capture intent, expand ambition, evaluate both gates, then stop |
| 3. Score | Observer | Fill in the scorecard against the baseline; add entries to [`FRICTION_LOG.md`](FRICTION_LOG.md) |
| 4. Decide | Ross | Continue to Gates 3–6, change the spec further, or both |

## Rules for the human during the run

- Answer as you now think, not as you answered last time. If a question resembles D-003 or D-005, answer it fresh.
- Do not coach the agent on its spec or mention the first run. If it misses a rule, let it happen and note it.
- Note, with the agent's message it relates to, any moment where:
  - you wanted pushback and did not get it;
  - pushback felt repetitive or unhelpful;
  - the agent changed your mind or made the idea bigger.
- Approve on the approval page only what you actually agree with.
