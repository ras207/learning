# Ideation Agent Bootstrap Session Protocol

## Purpose

This protocol governs interactive sessions used to build the reusable ideation agent itself.

It is distinct from a normal ideation run. A normal ideation run uses the reusable system to develop a project and MUST respect the write boundaries defined elsewhere in `.agents/ideation/`. A bootstrap session exists specifically to improve files beneath `.agents/ideation/` and therefore operates only when the user has explicitly asked to develop the ideation system.

The protocol is designed for short, repeated sessions that can begin from a scheduled ChatGPT task and be continued interactively on a phone.

## Authoritative state

At the start of every bootstrap session, read:

1. `.agents/ideation/bootstrap/BUILD_STATE.yaml`.
2. The file or workstream identified by `current_target`.
3. Any contract, completion criteria, workflow file, or other system file directly relevant to that target.
4. Relevant recent repository changes only when needed to understand the current design state.

`BUILD_STATE.yaml` is the authoritative record of bootstrap progress. Chat history may provide useful context but MUST NOT override repository state.

Do not ask the user to repeat a decision that is already clearly recorded in the repository.

## Session objective

Each session should make the maximum useful progress on the current target while preserving human control over consequential design choices.

A session does not need to complete a target. If important decisions remain unresolved at the end of the available interaction, leave the target as `in_design` and resume it in the next session.

## 1. Orient

Before asking a question:

1. Read the authoritative state and relevant target files.
2. Summarize internally what is already decided, what is provisional, and what remains unresolved.
3. Identify the highest-value unresolved decision for the current target.
4. Check whether explicit completion criteria exist for the target.

If no completion criteria exist and the target is substantial enough to require them, defining those criteria becomes part of the current design work before the target can be marked complete.

## 2. Assess unresolved decisions

Distinguish between:

- **Human judgement decisions**: choices about intent, boundaries, desired behaviour, trade-offs, risk tolerance, or product philosophy that should be resolved with the user.
- **Agent-resolvable implementation details**: low-consequence details that can be inferred from existing conventions, repository structure, or established engineering practice.
- **Unknowns requiring evidence**: questions that should be researched or inspected rather than answered by assumption.

Prioritize human judgement decisions in the interactive conversation. Resolve low-consequence implementation details independently where safe to do so, and explain consequential assumptions when they affect the draft.

## 3. Elicit

Ask one primary question at a time unless several tightly coupled questions are more efficient together.

Questions should:

- be concise enough to answer comfortably on a phone;
- explain why the decision matters when the significance is not obvious;
- present materially different options where useful;
- avoid false choices when a hybrid or alternative design is plausible;
- avoid asking for information that can be read from the repository;
- avoid prematurely translating an ambiguous preference into a system rule.

When the user's answer introduces a new ambiguity, resolve it before moving on if it could materially change the target design.

## 4. Challenge and expand

The agent is not a passive transcription layer.

Where useful, it should:

- challenge assumptions that create unnecessary constraints;
- identify edge cases and failure modes;
- surface meaningful alternatives;
- test whether a proposed rule works across the intended lifecycle of the ideation agent;
- identify tensions with decisions already recorded elsewhere in the system;
- push the design beyond the first obvious solution when a larger or more general design may better serve the stated intent.

Challenge should be proportionate. Do not prolong a session by manufacturing low-value objections after the relevant design space is sufficiently understood.

## 5. Maintain a live design model

Throughout the session, maintain a working distinction between:

- decisions that are settled for the current baseline;
- assumptions that are accepted provisionally;
- explicitly deferred questions;
- unresolved blockers;
- implementation details the agent may choose autonomously.

Do not persist speculative or intermediate reasoning into repository files unless it belongs in the target artifact or is needed as durable state.

## 6. Check sufficiency

Before drafting a target as complete, test whether:

1. Its purpose and scope are clear.
2. The material design decisions needed to implement or use it have been resolved or explicitly deferred.
3. Any required contract or completion criteria can be satisfied.
4. It is consistent with relevant files already accepted as part of the ideation system.
5. Important failure modes, edge cases, and hand-offs have been considered where relevant.
6. Remaining uncertainty is low enough that downstream work can proceed without silently inventing consequential design choices.

If these conditions are not met, continue the design conversation or leave the target `in_design` for the next session.

## 7. Synthesize

When there is sufficient context:

1. Draft or update the current target.
2. Preserve intentional existing content unless the new design explicitly supersedes it.
3. Keep the file focused on its stated responsibility rather than absorbing material that belongs elsewhere.
4. Use clear normative language for rules (`MUST`, `SHOULD`, `MAY`) where the distinction improves precision.
5. Record unresolved issues explicitly only when they genuinely need to remain open.

Do not modify unrelated files merely to make the repository look more complete.

## 8. Validate

Before proposing repository changes:

1. Re-read the resulting target document.
2. Check it against its contract or completion criteria.
3. Check for contradictions with relevant accepted system files.
4. Check that terminology and paths match the actual repository.
5. Check that no normal-run write boundary has accidentally been weakened.
6. Check whether the user made any decision during the session that the draft failed to encode.

If validation identifies a material problem, resolve it before opening the pull request where possible.

## 9. Update bootstrap state

When the target is complete, update `BUILD_STATE.yaml` in the same branch and pull request as the target change.

The state update should:

1. mark the completed target as `complete`;
2. advance `current_target` to the next appropriate item in `planned_sequence`;
3. set the next target's status to `in_design` where appropriate;
4. update notes only when they provide durable information needed by a later session.

Do not advance the target merely because a draft exists.

If the target remains incomplete, normally leave `current_target` unchanged. Persist additional bootstrap state only when doing so prevents meaningful context loss between sessions.

## 10. Git and pull-request behaviour

Follow the `git_policy` in `BUILD_STATE.yaml`.

For a completed target:

1. Start from the current base branch defined in `BUILD_STATE.yaml`.
2. Create a dedicated branch using the configured bootstrap branch prefix.
3. Make only changes needed for the current logical bootstrap step.
4. Use concise commits that describe the durable change made.
5. Include the corresponding `BUILD_STATE.yaml` update in the same pull request when the target advances.
6. Open a pull request into the configured base branch.
7. Do not merge the pull request automatically.

The pull request description should summarize:

- the target developed;
- the main design decisions encoded;
- any important alternatives considered;
- any unresolved or explicitly deferred issues;
- the next target recorded in bootstrap state.

The human review and merge is the ratification point. If the pull request is not merged, the authoritative state on the base branch remains unchanged.

## 11. End-of-session report

At the end of a session, tell the user concisely:

- what was decided;
- what was changed in the repository, if anything;
- whether the current target is complete or still in design;
- the pull request link or identifier if one was opened;
- what the next session should work on according to `BUILD_STATE.yaml`.

If no repository change was appropriate, say so rather than creating a low-value commit merely to record activity.

## Scheduled-session entry behaviour

When a scheduled task invokes this protocol, it should stop after orientation and the first high-value question unless no user input is required.

It should not attempt to finish a judgement-heavy target unattended. The scheduled run's purpose is to establish context, identify the next design decision, and begin the interactive session.

Once the user responds, continue through this protocol until the target is either complete or the interaction naturally stops.
