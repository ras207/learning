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
| `SHALLOW` | The spec was followed, but the idea was probed, challenged or stretched less than it should have been. |

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

### G1-1 SHALLOW Gate 1 passed on the seed alone; purpose was deferred
- Gate / stage: Gate 1, clarify intent
- Where: `intent-model.md` ("No further clarification from the user was available in this sitting. Everything below comes from the seed."); WI-003 in `state.yaml`
- Rule: `skills/clarify-intent` Method 4–5 ("Resolve supported, reversible details autonomously"; "Ask the smallest focused question when a consequential interpretation cannot be inferred safely"); AGENT.md "Human decision authority" (infer when well supported)
- What happened: The agent wrote the intent model without asking the human anything. What the capability is *for* and why now (WI-003) was classed as "not material to Gate 1" and deferred. It was answered only during problem modelling (`13e0431`), after ambition had been expanded and D-003 settled.
- Impact: high. Gate 2 widened and narrowed the idea without knowing its purpose. The later contradictions (G3-1, G5-1) follow from this ordering.
- Proposed action: fix now. Gate 1 cannot pass without a conversation, and purpose and why-now must be asked about directly.

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

### G2-7 SHALLOW Ambition was expanded by the agent, not with the human
- Gate / stage: Gate 2, expand ambition
- Where: `ambition-map.md`; human input for the sitting was "no corrections" and "A" (G2-1)
- Rule: `skills/expand-ambition` Method (the agent explores dimensions and recommends carry, reject or defer)
- What happened: The agent wrote the whole map, ten possibilities across five dimensions, and classified each itself. The human was asked about one item only (AM-2). The human was never asked what bigger version of the idea they had in mind, or pushed on why they had not gone further.
- Impact: medium to high. The expansion reads as thorough, but the human's own ambition was never drawn out or stretched, so it did not grow in the human's mind.
- Proposed action: fix now. Start expansion with open questions and pushback on the human's answers before the agent writes the map.

## Gate 3 — Problem Modelled

Entries for Gates 3–6 come from the observer's review of commits and artifacts after the run, plus the human's feedback on 2026-09-27. No live notes were taken for these gates.

### G3-1 SHALLOW New purpose that conflicted with D-003 was absorbed, not raised
- Gate / stage: Gate 3, model problem
- Where: `13e0431`; `problem-model.md` sections 1 and C6 ("The business is what capability is *for*, not something the system pursues")
- Rule: AGENT.md "Challenge" ("MUST NOT ... repeatedly relitigate an explicit informed decision without new material evidence")
- What happened: At Gate 3 the human stated their purpose: sell insight, run a policy-advice business, and become a respected advisor. D-003 ("capability, not results") had been decided at Gate 2 without that purpose on the table. The agent reconciled the two itself in constraint C6 instead of asking whether D-003 still held. The spec allows re-raising a decision when there is new material evidence, and this was new material evidence.
- Impact: high. A decision made without the relevant facts shaped the rest of the run. The human now says they would probably answer D-003 differently.
- Proposed action: fix now. Add a tension check: when a later human statement conflicts with an earlier decision, the agent must put the conflict to the human.

### G3-2 SHALLOW Seed breadth narrowed by agent inference
- Gate / stage: Gate 3, model problem
- Where: `problem-model.md` section 3 observation labelled **[inference]** ("The targets form one coherent trajectory, not a set of scattered interests"); `vision.md`
- What happened: The seed named "economics, technology, AI, business and other interests" and "creative work". The problem model framed the targets as one trajectory, and the vision covers economics, AI and policy advice only. Creative work and other interests do not appear, and there is no record that the human was asked whether to narrow.
- Impact: medium. The narrowing may be right, but it was the agent's choice rather than the human's, which contributes to the vision feeling narrow and safe.
- Proposed action: fix now. Treat dropping part of the seed as a material scope change that needs the human's explicit choice.

## Gates 4–5 — Alternatives, Convergence and Challenge

### G5-1 SHALLOW Focused challenge fenced off the human's decisions
- Gate / stage: pre-Gate-5 focused challenge
- Where: `5670306`; `focused-challenge.md` ("This challenge tests the direction; it does not reopen D-005"; F2 "is not relitigated here")
- Rule: `skills/focused-challenge` "Do not invoke when" (do not "override an informed human decision"); AGENT.md "Challenge"
- What happened: The top-severity finding, F2, was that the ten-year aim of being a respected advisor cannot be evidenced without other people's judgement. The agent recorded it as an accepted trade-off and turned it into a non-goal ("Capability, not reputation"). The challenge only hardened the chosen direction (separate assessor, world-checkable evidence). It never asked the human whether the direction was right given F2.
- Impact: high. The one step designed for pushback was not allowed to push back on the choices that mattered most. The human says they would probably answer D-005 differently.
- Proposed action: fix now. The challenge must put high-severity findings against human decisions back to the human as a reconfirmation question, while still not arguing the same point twice.

### G5-2 GOOD Recommendations and strongest objections were given at each decision
- Gate / stage: Gates 2 and 4–5
- Where: D-003, D-005 (`a956660`)
- What happened: Each option menu came with a recommendation and a trade-off. The human says the menu format works for them; the problem was the lack of follow-up pushback (G3-1, G5-1), not the format.
- Impact: medium.
- Proposed action: keep the option menus with recommendations.

## Gate 6 — Vision Approved

### G6-1 SHALLOW Vision approved without a check against the seed
- Gate / stage: Gate 6, synthesize and approve vision
- Where: `c36675a`, `2c2eb32`; `vision.md` section 7 (eight non-goals)
- Rule: `skills/validate-vision`; `contracts/VISION_CONTRACT.md`
- What happened: Validation checked the vision against the contract and the recorded decisions. Nothing compared the vision with the original seed, or asked the human whether it was bolder, more valuable or narrower than what they started with. The vision passed with eight non-goals, most of them protective.
- Impact: medium to high. The human approved it, then felt afterwards that it was narrow and safe.
- Proposed action: eval. Before approval, show a seed-versus-vision comparison (what grew, what was dropped and who decided) and ask the human directly whether the vision is more valuable than the seed.

## Overall — the human's assessment after the run

### H-1 SHALLOW The process did not make the idea more valuable
- Gate / stage: whole run
- Where: the human's feedback, 2026-09-27
- What happened: The human feels the vision ended up narrow and safe, and is not sure the process made it more valuable than the seed. They do not mind answering menus, but there was not enough pushback. They would probably answer D-003 and D-005 differently if they had been properly challenged.
- Root cause (observer): The spec makes the agent involve the human as little as possible ("smallest question", infer when safe, one question at a time, do not relitigate). Collaboration was treated as authority over decisions, not as thinking together. The agent followed the spec faithfully. About 13 of 132 commits carry human input.
- Impact: high. This is the agent's core purpose ("broaden, interrogate, ... challenge").
- Proposed action: fix now with three spec edits (G1-1, G2-7, G3-1/G5-1), then re-run Gates 1–2 on this idea on a fresh branch and compare.

