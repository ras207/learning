# Ideation Workflow Gates

## Purpose

This file defines the gate system used to assure the quality of ideation before the workflow makes consequential commitments or hands an approved vision to product design.

Gates evaluate whether the current ideation state is sufficiently strong to proceed. They do not themselves define the sequence of workflow stages or the persistence format for project state.

## Responsibility boundary

This file owns:

- the purpose and classification of each gate;
- the criteria used to evaluate each gate;
- the evidence the evaluator should inspect;
- the permitted gate outcomes;
- the conditions for `PASS_WITH_UNCERTAINTY`, `FAIL`, and `ESCALATE`;
- the human decision authority associated with each gate; and
- the minimum structured evaluation record each gate must produce.

`.agents/ideation/workflow/WORKFLOW.md` owns when gates are invoked and what the workflow does next.

`.agents/ideation/state/ideation_state.md` owns how gate-evaluation records are persisted.

`.agents/ideation/contracts/VISION_CONTRACT.md` owns the required structure and quality standard for the generated vision artifact.

## Gate model

The ideation workflow uses two gate classes.

### Hard gates

A hard gate protects consequential intent, an explicit human decision, or the validity and coherence required for downstream work.

The workflow MUST NOT progress beyond a hard gate with an unresolved blocking deficiency.

A hard gate MAY return `PASS_WITH_UNCERTAINTY` only when the gate's substantive purpose has been met, the remaining uncertainty is explicit and non-blocking, and proceeding will not require downstream work to invent consequential intent.

### Advisory gates

An advisory gate is intended to improve exploration quality without creating unnecessary rigidity.

An advisory gate MAY permit progression with recorded uncertainty. It becomes blocking when a deficiency is material enough that making the next consequential commitment would be unsafe, poorly informed, or dependent on unexamined assumptions.

Advisory therefore does not mean optional. It means the gate normally tolerates non-blocking uncertainty and does not require a stop merely because exploration could continue indefinitely.

## Gate outcomes

Every gate evaluation MUST produce exactly one of the following outcomes.

### `PASS`

The gate's substantive purpose is satisfied and no material uncertainty remains that needs to be carried forward.

### `PASS_WITH_UNCERTAINTY`

The gate's substantive purpose is satisfied, but one or more explicit uncertainties remain.

This outcome MUST be used only when:

- the remaining uncertainty is genuinely non-blocking;
- the uncertainty is recorded explicitly;
- the uncertainty does not conceal an unmet pass criterion; and
- downstream work will not need to invent consequential intent or silently assume a material trade-off.

`PASS_WITH_UNCERTAINTY` MUST NOT be used as a convenience to waive weak or incomplete work.

### `FAIL`

The gate criteria are not met, but the agent can identify what additional ideation work is required without needing a new human judgement.

A `FAIL` MUST identify the material deficiency. It MUST NOT hard-code a return stage. The workflow should decide dynamically where to resume based on the deficiency and current project state.

### `ESCALATE`

Progress depends on human judgement, clarification, choice, or acceptance of a consequential trade-off.

Uncertainty alone does not justify escalation. The deciding factor is that the agent would otherwise need to substitute its judgement for the user's on a consequential matter.

## Required gate-evaluation record

Every gate evaluation MUST leave an explicit, auditable record. The record MUST contain at least:

- gate identifier and name;
- outcome;
- pass criteria satisfied;
- pass criteria unmet, if any;
- material deficiency, if any;
- explicit non-blocking uncertainty, if any;
- human judgement or decision required, if any;
- human judgement or decision made, if any; and
- a concise rationale for the outcome.

The persistence schema for this record belongs in `ideation_state.md`.

## Gate 1 — Intent Captured

**Classification:** Hard.

### Purpose

Establish that the user's starting intent is understood well enough to explore without the agent prematurely fixing the solution or inventing consequential intent.

### Evidence to inspect

The evaluator should inspect the user's stated idea, clarifications already provided, and the current ideation state for evidence of:

- the trigger or motivation for the idea;
- what the user currently wants to create, change, or explore;
- relevant users, beneficiaries, or stakeholders already identified;
- the desired outcome or change;
- consequential preferences or boundaries already expressed; and
- material uncertainties that remain.

### Pass criteria

The gate may pass when:

- the core intent is understandable;
- the desired outcome is sufficiently clear to guide exploration;
- relevant people or beneficiaries are clear enough for the current stage;
- no unresolved ambiguity would cause the agent to pursue a materially different interpretation of the idea; and
- material remaining uncertainty is visible rather than silently assumed away.

The agent MAY pass this gate without asking for explicit confirmation when the user's intent is already explicit and materially unambiguous.

### `PASS_WITH_UNCERTAINTY`

Permitted when details remain unknown but those unknowns do not materially affect the core problem, desired outcome, relevant people, or intended direction of exploration.

### `FAIL`

Use when the intent is too incomplete or internally inconsistent to support coherent exploration, but the missing information can be developed through further ideation work without requiring the user to choose between consequential interpretations.

### `ESCALATE`

Use when the agent would otherwise need to infer, reinterpret, or choose between materially different meanings of the user's intent.

### Human authority

The user owns consequential intent. Explicit confirmation is required only when the agent would otherwise substitute its judgement for the user's.

## Gate 2 — Ambition Explored

**Classification:** Advisory.

### Purpose

Push beyond the first framing of the idea and test whether a more valuable or more general opportunity exists before the workflow narrows prematurely.

### Evidence to inspect

The evaluator should inspect whether the exploration has systematically considered, where relevant:

- broader or different users and beneficiaries;
- larger or more valuable outcomes;
- wider or differently bounded scope;
- second-order opportunities or effects;
- more ambitious versions of the idea; and
- which expanded possibilities are worth carrying forward, rejecting, or deferring.

### Pass criteria

The gate may pass when:

- the initial framing has been challenged rather than merely restated;
- materially broader possibilities have been surfaced where plausible;
- the exploration has considered multiple dimensions of ambition rather than only feature expansion; and
- the ambitions worth carrying forward are distinguishable from those that should be rejected or deferred.

### `PASS_WITH_UNCERTAINTY`

Permitted when the opportunity space has been explored sufficiently for the current stage but some non-blocking questions remain about the eventual scale or scope.

### `FAIL`

Use when the ambition exploration is materially too shallow to support the next consequential commitment safely, but the agent can continue expanding or testing the opportunity autonomously.

### `ESCALATE`

Use when adopting an ambition would materially change the idea's scope, intended beneficiaries, desired outcomes, or risk profile and the user has not already expressed that preference.

### Human authority

The agent may carry forward clearly compatible ambitions autonomously. The user retains authority over consequential expansion of the idea.

## Gate 3 — Problem Understood

**Classification:** Hard.

### Purpose

Ensure the workflow understands the underlying problem or opportunity deeply enough to explore solutions without merely optimizing the initial proposed solution.

### Evidence to inspect

The evaluator should inspect whether the ideation state establishes:

- a solution-independent problem or opportunity definition;
- who is affected and how;
- relevant causes, mechanisms, or drivers;
- current workarounds, substitutes, or existing approaches;
- why the current situation or existing approaches are inadequate; and
- which parts of the diagnosis are supported by evidence versus still assumed.

### Pass criteria

The gate may pass when:

- the problem can be explained independently of the proposed solution;
- the affected people or systems and the nature of the impact are clear;
- the important causal or contextual mechanisms are understood well enough to guide solution exploration;
- current workarounds or alternatives are understood where relevant;
- the inadequacy of the current state is explicit; and
- important assumptions in the diagnosis are visible.

### `PASS_WITH_UNCERTAINTY`

Permitted when parts of the causal diagnosis remain hypothetical, provided those hypotheses are explicit and the uncertainty does not make subsequent solution exploration unsafe or misleading.

### `FAIL`

Use when the problem model is too weak, solution-dependent, contradictory, or assumption-heavy to support meaningful alternatives, but the agent can identify further analysis or exploration that should resolve the deficiency.

### `ESCALATE`

Use when a material ambiguity in the problem definition depends on the user's values, priorities, intended beneficiaries, or judgement about what problem is actually worth solving.

### Human authority

The agent may assess problem sufficiency. The user retains authority over consequential choices about which problem, outcome, or stakeholder priority the ideation process should ultimately serve.

## Gate 4 — Alternatives Explored

**Classification:** Advisory.

### Purpose

Ensure the workflow has explored materially different solution directions and made their consequential trade-offs visible before converging.

### Evidence to inspect

The evaluator should inspect whether alternatives differ meaningfully in one or more of:

- underlying mechanism;
- assumptions;
- scope;
- user or beneficiary model;
- delivery model;
- degree of intervention;
- operating model; or
- other dimensions that materially change the shape of the solution.

The evaluator should also inspect the comparison between credible alternatives, including where relevant:

- benefits and expected upside;
- risks and likely failure modes;
- critical assumptions;
- constraints;
- reversibility;
- dependencies; and
- consequential trade-offs.

### Pass criteria

The gate may pass when:

- the solution space contains materially different approaches rather than superficial variants;
- there is no fixed minimum count, but the important plausible regions of the solution space have been explored;
- the credible alternatives have been compared on consequential trade-offs; and
- the basis for later convergence is visible.

### `PASS_WITH_UNCERTAINTY`

Permitted when the important solution space has been explored sufficiently but some non-blocking uncertainty remains about the relative strength or feasibility of alternatives.

### `FAIL`

Use when the exploration is materially too narrow, alternatives are not genuinely distinct, or trade-offs are insufficiently examined to support the next commitment safely.

### `ESCALATE`

Use when further progression requires the user to choose between materially different value judgements, scope choices, risk tolerances, or trade-offs that cannot safely be inferred.

### Human authority

The agent owns breadth and quality of exploration. The user owns consequential preferences between materially different directions when those preferences are not already explicit.

## Gate 5 — Ready for Synthesis

**Classification:** Hard.

### Purpose

Determine whether ideation has produced enough coherent, resolved material to synthesize a candidate vision without using drafting as a substitute for unresolved discovery.

### Evidence to inspect

The evaluator MUST inspect:

- the chosen broad direction;
- consequential trade-offs and whether they have been resolved or consciously accepted;
- blocking and non-blocking uncertainties;
- the outputs of earlier required gates; and
- the current ideation material against the substantive requirements of `VISION_CONTRACT.md`.

### Pass criteria

The gate may pass when:

- a coherent broad direction is explicit;
- consequential trade-offs are resolved or consciously accepted;
- no blocking uncertainty remains;
- earlier required gates contain no unresolved blocking deficiency; and
- there is enough substantive material to populate every required section of the vision contract without silently inventing consequential content.

### `PASS_WITH_UNCERTAINTY`

Permitted only when remaining uncertainties are non-blocking, explicitly recorded, and compatible with a coherent candidate vision under the vision contract.

### `FAIL`

Use when the ideation material is not yet sufficient for synthesis but the agent can identify and undertake the additional ideation work required.

### `ESCALATE`

Use when materially different viable directions remain and choosing among them requires user judgement, or when an unresolved consequential trade-off requires explicit human acceptance.

### Human authority

Explicit human confirmation is not required merely because this is a hard gate. It is required when materially different viable directions remain or another consequential choice has not already been expressed by the user.

## Gate 6 — Vision Approved

**Classification:** Hard.

### Purpose

Ratify the completed vision as the authoritative handoff from ideation to product design.

### Evidence to inspect

Before requesting approval, the evaluator MUST verify that:

- the candidate vision satisfies `VISION_CONTRACT.md`;
- all blocking unresolved questions in the vision are cleared;
- all required earlier gates have valid evaluation records; and
- no earlier gate contains an unresolved blocking deficiency.

### Pass criteria

This gate passes only when:

- the artifact and process-assurance checks above are satisfied; and
- the user explicitly approves the candidate vision.

The agent MUST NOT approve its own vision.

### `PASS_WITH_UNCERTAINTY`

This outcome MAY be used only if the vision contract permits the remaining uncertainty, all such uncertainty is explicitly non-blocking, and the user explicitly approves the vision with that uncertainty visible.

### `FAIL`

Use when the artifact or required process assurance is not valid and the agent can identify what work is needed before approval can properly be requested.

### `ESCALATE`

Use when the vision is otherwise eligible for approval and explicit human approval is required, or when approval depends on a consequential unresolved human judgement.

### Human authority

Final vision approval is always an explicit human decision.

## Failure and resumption behaviour

A gate that does not pass MUST identify the deficiency that prevents progression.

This file does not define fixed loop-back routes. The workflow MUST decide dynamically where to resume based on:

- the gate that was evaluated;
- the identified deficiency;
- the current ideation state;
- previously satisfied work that should be preserved; and
- the smallest coherent intervention likely to resolve the deficiency.

The workflow SHOULD avoid repeating already-satisfied work merely because an earlier stage label appears to match the deficiency.

## Completion criteria for this file

`GATES.md` is complete when:

1. the purpose and scope of the gate system are explicit;
2. hard and advisory gate behaviour are defined;
3. `PASS`, `PASS_WITH_UNCERTAINTY`, `FAIL`, and `ESCALATE` are defined;
4. the required structured gate-evaluation record is defined;
5. all six gates specify their purpose, classification, pass criteria, evidence, outcome conditions, and human authority;
6. failures identify deficiencies while routing remains the responsibility of the workflow;
7. the file is internally consistent with `VISION_CONTRACT.md` and the responsibility boundaries with `WORKFLOW.md` and `ideation_state.md`; and
8. no unresolved material design decision remains that downstream workflow design would otherwise need to invent.
