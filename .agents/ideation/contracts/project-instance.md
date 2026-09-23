# Ideation Project Instance Contract

## Purpose

This contract defines the minimum durable structure for a real project operated on by the reusable Ideation Agent.

It deliberately preserves the v0.1 canonical runtime-state model in `../state/ideation_state.md`. The first real field test should exercise that architecture before physical separation of durable knowledge and operational state is reconsidered.

## Ownership boundary

`.agents/ideation/` owns reusable ideation behaviour, contracts, skills, workflow, schemas and deterministic tools.

`projects/<project-slug>/` owns information and artifacts specific to one idea. Project-specific content MUST NOT be written back into reusable agent definitions.

## Minimum seed

A new project begins with exactly one human-authored seed artifact:

`projects/<project-slug>/PROJECT.md`

The seed MUST contain:
- a stable project ID/slug; and
- the user's free-form initial idea.

No structured problem statement, user definition, solution, assumptions, constraints or evidence are required before ideation begins. The agent is responsible for eliciting and structuring these through the workflow.

## Canonical v0.1 structure

After deterministic initialization, the minimum project structure is:

```text
projects/<project-slug>/
├── PROJECT.md
└── ideation/
    └── state.yaml
```

The tools layer adds `ideation/approvals/` when the first human approval is committed. It holds approval evidence referenced from state, as defined in `../state/ideation_state.md`.

`projects/<project-slug>/ideation/state.yaml` remains the single canonical state artifact defined by `../state/ideation_state.md`. In v0.1 it contains both durable ideation knowledge and operational workflow state.

This physical unification is intentional for the first field test. A conceptual distinction between durable knowledge and runtime state MAY be maintained, but implementations MUST NOT introduce a second competing canonical store.

## Initialization

Initialization MUST be deterministic.

Given a valid minimal seed and trusted execution context, the initializer MUST:
1. verify the project slug and seed location;
2. refuse initialization when canonical ideation state already exists;
3. create schema-valid revision-1 state using the existing state contract;
4. set project identity and iteration to 1;
5. record the reusable Ideation Agent fingerprint/provenance;
6. initialize workflow at `orient_and_initialize`, with no substantive ideation decisions invented;
7. preserve the seed as the authoritative initial human input; and
8. commit initialization only through the deterministic tools layer on an authorized non-protected branch, using a `trust_mode: "passkey"` execution context.

Initialization is mechanical. It MUST NOT infer a problem definition, intended user, solution, ambition, evidence or consequential decision from the seed.

## Agent provenance

Each project MUST retain enough provenance to identify the reusable Ideation Agent version used for an iteration.

For v0.1, the provenance requirement is satisfied by recording a repository commit SHA/fingerprint in canonical state or an artifact reference created by the deterministic initializer. Copying the reusable agent into the project is prohibited.

## Iterations and reopening

A project is durable across its lifetime. Material reopening of an approved or not-progressing idea starts a new ideation iteration in the same project, using the reopening semantics in `../state/ideation_state.md`.

Previous terminal iterations and approved outputs remain immutable. Inherited knowledge MUST be explicitly revalidated or superseded where material dependencies changed.

The v0.1 canonical state path remains unchanged across iterations; iteration identity and history are represented inside the canonical state contract. A future version MAY physically separate iteration state only through an explicit contract/schema migration.

## Outputs

Synthesized handoff outputs are immutable and explicitly versioned once approved. A downstream consumer MUST be able to identify the exact approved VISION and the agent/project iteration that produced it.

Draft working artifacts MAY remain mutable where existing workflow/tool contracts permit. Approval MUST NOT overwrite a previously approved handoff artifact.

## Evaluation boundary

Field-test observations evaluate the reusable agent, not the idea. They belong under:

`.agents/ideation/evaluation/runs/<run-id>/`

Evaluation records MUST reference the project, iteration and agent fingerprint they observed. They MUST NOT become canonical project knowledge merely because they arose during a project run.

## First-field-test rule

The first real run is intended to test the accepted v0.1 architecture. Therefore:
- preserve the unified canonical state model;
- do not add a parallel project ICM/state store;
- record observed deficiencies rather than redesigning around them during the run unless they block safe progress; and
- use those observations to inform a later v0.2 decision.

## Completion criteria

This contract is satisfied when:
1. a project can begin from only project ID/slug plus a free-form idea;
2. reusable agent definitions and project-specific state are cleanly separated;
3. initialization is deterministic and creates schema-valid canonical state without qualitative inference;
4. the existing unified v0.1 state contract remains authoritative;
5. agent provenance is recoverable without copying the agent;
6. reopening preserves project identity and prior terminal history;
7. approved outputs have stable immutable identities; and
8. field-test evidence is stored with the reusable agent rather than mixed into project knowledge.
