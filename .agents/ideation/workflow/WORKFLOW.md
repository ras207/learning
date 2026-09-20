# Ideation Workflow

## Purpose

This file defines how a normal ideation run progresses from an initial idea to an approved vision. It owns the normal progression spine, gate invocation, outcome routing, dynamic resumption, synthesis, approval, and workflow completion.

It does not redefine:

- gate semantics or criteria, which belong to `.agents/ideation/workflow/GATES.md`;
- the vision structure and quality standard, which belong to `.agents/ideation/contracts/VISION_CONTRACT.md`;
- the persistence schema for runtime state and gate records, which belongs to `.agents/ideation/state/ideation_state.md`; or
- the overall agent role and authority, which belongs to `.agents/ideation/AGENT.md`.

## Project scope and output location

Each ideation run operates on a specific project identified by `<project-slug>`.

All generated or mutable project artifacts MUST remain beneath:

`projects/<project-slug>/ideation/`

The generated vision artifact MUST be written to:

`projects/<project-slug>/ideation/vision.md`

Before beginning or resuming substantive ideation, the workflow MUST read:

1. `.agents/ideation/AGENT.md`;
2. this workflow;
3. `.agents/ideation/workflow/GATES.md`;
4. `.agents/ideation/contracts/VISION_CONTRACT.md`; and
5. the current project ideation state and relevant project artifacts, when they exist.

The workflow MUST NOT write to `.agents/ideation/` during a normal ideation run. Files beneath that path may be modified only when the user explicitly asks to change the reusable ideation system.

## Operating model

The workflow uses a fixed progression spine with dynamic routing.

The spine provides a clear normal order and planned gate boundaries. It is not a rigid waterfall. Gate deficiencies, new evidence, contradictions, or consequential human decisions may require a targeted intervention outside the normal forward sequence.

The workflow MUST preserve valid prior work where possible. It MUST NOT restart a whole stage merely because a deficiency resembles an earlier stage label.

Challenge is a continuous behaviour across the workflow. The preferred direction MUST also receive a focused pre-synthesis challenge before Gate 5.

## Normal progression spine

### 1. Orient and initialize

Determine whether the run is new or resumed.

For a new run:

- confirm or establish the project slug;
- inspect any existing project context that the user has made available;
- initialize project ideation state according to the state definition; and
- capture the initial idea without prematurely narrowing it.

For a resumed run:

- read the persisted project state and artifacts;
- distinguish settled decisions, provisional assumptions, deferred questions, blocking deficiencies, and pending human decisions;
- identify any material change since the last valid gate evaluation; and
- recompute the next action rather than trusting a stale stage label.

### 2. Capture intent

Develop a sufficiently clear understanding of the user's starting intent, desired outcome, relevant people, and consequential boundaries without fixing the solution prematurely.

Evaluate Gate 1 — Intent Captured at the end of this stage.

### 3. Expand ambition

Challenge the initial framing and explore whether broader users, outcomes, scope, or second-order opportunities would create materially greater value.

Distinguish ambitions that should be carried forward from those rejected or deferred.

Evaluate Gate 2 — Ambition Explored at the end of this stage.

### 4. Understand the problem or opportunity

Develop a solution-independent account of the problem or opportunity, affected people or systems, important mechanisms, current approaches, and why the current state is inadequate.

Keep evidence and assumptions distinguishable.

Evaluate Gate 3 — Problem Understood at the end of this stage.

### 5. Explore alternatives

Explore materially different directions rather than superficial variants. Compare credible alternatives on consequential benefits, risks, assumptions, constraints, dependencies, reversibility, and trade-offs.

Evaluate Gate 4 — Alternatives Explored at the end of this stage.

### 6. Converge and challenge the preferred direction

Identify the preferred broad direction and make the basis for convergence explicit.

Before Gate 5, conduct a focused challenge that:

- tests critical assumptions and causal logic;
- seeks contradictions with the stated intent, problem model, boundaries, and desired outcomes;
- examines important failure modes and disconfirming possibilities;
- checks whether a credible alternative remains materially stronger; and
- makes unresolved consequential trade-offs visible.

Resolve or explicitly accept consequential trade-offs that require human judgement.

Evaluate Gate 5 — Ready for Synthesis at the end of this stage.

### 7. Synthesize and validate a candidate vision

Once Gate 5 passes:

1. read `.agents/ideation/contracts/VISION_CONTRACT.md`;
2. synthesize the current ideation state into `projects/<project-slug>/ideation/vision.md`;
3. set the vision status to `candidate`;
4. validate every required section and artifact-quality condition in the contract;
5. verify that no blocking unresolved question remains; and
6. confirm that all required earlier gate records remain valid.

Drafting MUST NOT be used to conceal unresolved discovery or silently invent consequential intent.

If validation exposes a deficiency, do not request final approval. Route the deficiency through the dynamic resumption process.

### 8. Obtain explicit human approval

Present the candidate vision with consequential trade-offs, assumptions, boundaries, and remaining non-blocking uncertainty visible.

Evaluate Gate 6 — Vision Approved.

The agent MUST NOT approve its own vision. Gate 6 can pass only through explicit human approval and satisfaction of the artifact and process-assurance requirements in `GATES.md`.

If the user requests a substantive change, update the relevant state, invalidate affected gate evaluations, and resume dynamically before seeking approval again.

### 9. Finalize the handoff

Gate 6 approval is necessary but does not by itself complete the workflow.

After Gate 6 passes, the workflow MUST:

1. confirm that all six required gate records are current and contain no unresolved blocking deficiency;
2. confirm that no human escalation remains open;
3. confirm that the vision still satisfies `VISION_CONTRACT.md`;
4. change the vision status from `candidate` to `approved`;
5. preserve explicit non-blocking uncertainties and critical assumptions for downstream work;
6. record the ideation workflow as complete in project state; and
7. declare the approved vision the authoritative handoff to product design.

This finalization step is not a seventh gate and MUST NOT override or waive a gate result.

If finalization reveals a substantive defect, the workflow remains incomplete and MUST resume through dynamic routing. A substantive change to the vision after approval invalidates Gate 6 and requires renewed human approval. The expected metadata change from `candidate` to `approved` does not itself require renewed approval.

## Gate invocation and re-evaluation

The workflow MUST formally evaluate each gate at its planned boundary.

It MUST also evaluate or re-evaluate a gate when a material change could affect that gate's criteria, evidence, or outcome. A material change includes:

- new evidence that challenges a prior conclusion;
- a changed user preference, boundary, intended beneficiary, or desired outcome;
- a contradiction within the project state or vision;
- a changed assumption with consequential downstream effects; or
- a substantive revision to the preferred direction or candidate vision.

When a material change occurs, the workflow MUST:

1. identify which gate criteria and evidence are affected;
2. mark affected evaluations as requiring re-evaluation;
3. identify downstream evaluations that materially depend on the changed conclusion;
4. preserve evaluations and work that remain valid; and
5. re-evaluate only the affected gate and dependent downstream gates.

A later gate MUST NOT remain treated as valid when its rationale materially depends on an invalidated earlier conclusion.

## Outcome routing

Gate outcomes are defined in `GATES.md`. The workflow routes them as follows.

### `PASS`

Record the evaluation and proceed to the next appropriate point in the normal spine.

### `PASS_WITH_UNCERTAINTY`

Record each explicit non-blocking uncertainty and proceed.

The workflow MAY resolve such uncertainty later if it becomes blocking because of a material change. It MUST NOT treat this outcome as permission to ignore an unmet pass criterion.

### `FAIL`

Record the identified deficiency and invoke dynamic deficiency routing.

A `FAIL` means additional ideation work can be undertaken without a new consequential human judgement. The workflow MUST NOT hard-code a return stage.

### `ESCALATE`

Pause progression at the consequential decision boundary and ask the user for the smallest clear judgement, clarification, choice, or trade-off acceptance needed to proceed.

The workflow MUST make the relevant options, consequences, and existing evidence visible. It MUST NOT choose on the user's behalf.

After the user decides, update the project state and re-evaluate the affected gate.

## Dynamic deficiency routing

When one or more deficiencies exist, the workflow MUST select the next intervention from the current state rather than from a fixed loop-back table.

The router MUST:

1. identify the causal deficiency behind each failed or invalidated criterion;
2. classify what is needed as further autonomous ideation, blocked evidence gathering, or human judgement;
3. trace which current and downstream conclusions depend on each deficiency;
4. prioritize the earliest causal deficiency that invalidates or blocks the greatest amount of downstream work;
5. when deficiencies are equally foundational, prioritize the intervention with the greatest expected decision value;
6. select the smallest coherent intervention likely to resolve the chosen deficiency;
7. preserve unaffected decisions, evidence, artifacts, and gate evaluations;
8. perform the intervention or request the required human decision;
9. update the project state; and
10. re-evaluate the affected gate and any materially dependent downstream gates.

After re-evaluation, the workflow MUST recompute the next action from the whole current state. It SHOULD return to forward progression only when no higher-priority blocking deficiency remains.

## Research and evidence gathering

Research is not a routine stage in the workflow.

The workflow MAY initiate research only when progress is blocked because an evidence gap prevents a gate from validly passing or prevents the router from identifying a safe next action.

Research MUST be:

- scoped to the blocking uncertainty;
- proportionate to the consequence of being wrong;
- connected to a specific gate criterion or routing decision; and
- recorded distinctly from assumptions and human preferences.

The workflow MUST NOT research a merely non-blocking uncertainty automatically. It should record and carry that uncertainty forward.

If required evidence cannot be obtained, the workflow MUST record the blockage and explain what cannot safely proceed. It MUST use `ESCALATE` only if progress then depends on human judgement, clarification, choice, or acceptance of a consequential trade-off.

## Human interaction

The workflow SHOULD ask one primary question or decision at a time unless several questions are tightly coupled and materially more efficient together.

It SHOULD:

- explain why a consequential decision matters;
- present materially different options and their trade-offs where useful;
- avoid asking for information already available in project state or repository context;
- distinguish evidence questions from value judgements; and
- challenge the user's framing proportionately rather than acting as a passive transcription layer.

The user retains authority over consequential intent, ambition, stakeholder priorities, scope, risk tolerance, trade-offs, direction, and final approval.

## Interruption and resumption

A run may pause before the workflow is complete.

Before pausing where persistence is available, the workflow SHOULD preserve enough state to recover:

- the current valid and invalidated gate evaluations;
- settled decisions and provisional assumptions;
- explicit non-blocking uncertainties;
- unresolved deficiencies and their dependencies;
- pending human decisions;
- the current candidate vision status, if one exists; and
- the router's current focus and rationale.

On resumption, the workflow MUST repeat orientation, check for material changes, and recompute the next action. It MUST NOT rely on chat history or a previously recorded stage label as the sole source of truth.

## Workflow completion criteria

The ideation workflow is complete only when:

1. `projects/<project-slug>/ideation/vision.md` exists and has `status: approved`;
2. the vision satisfies `.agents/ideation/contracts/VISION_CONTRACT.md`;
3. all six required gate-evaluation records are current and valid;
4. Gate 6 records explicit human approval;
5. no unresolved blocking question, blocking deficiency, invalidated required gate, or pending human escalation remains;
6. every remaining uncertainty is explicit and genuinely non-blocking;
7. mandatory finalization has been completed and recorded in project state; and
8. the approved vision is identified as the authoritative handoff to product design.

Until all eight conditions are satisfied, the workflow MUST remain incomplete.

## Completion criteria for this file

`WORKFLOW.md` is complete when:

1. its responsibility boundaries and project write boundary are explicit;
2. the fixed progression spine and all six planned gate boundaries are defined;
3. continuous challenge and the focused pre-synthesis challenge are defined;
4. gate invocation, material-change detection, and dependency-aware re-evaluation are defined;
5. all four gate outcomes have unambiguous routing behaviour;
6. dynamic deficiency routing preserves valid work and prioritizes dependency before expected decision value;
7. research is limited to evidence gaps that block progress;
8. synthesis, explicit human approval, and mandatory finalization are defined;
9. interruption, resumption, and workflow completion are defined; and
10. the file is internally consistent with `GATES.md`, `VISION_CONTRACT.md`, and the responsibility boundary of `ideation_state.md`.
