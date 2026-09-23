# Ideation Runtime State

## Purpose

This file defines the authoritative runtime-state and persistence model for a normal ideation run.

It enables the ideation agent to recover across sessions, route from current deficiencies rather than a stale stage label, preserve human decisions, invalidate only materially affected work, and explain the basis of the current workflow state without persisting private or unnecessary speculative reasoning.

## Responsibility boundary

This file owns:

- the location and authority of project ideation state;
- the required state sections and record semantics;
- workflow, session, vision, and terminal status persistence;
- identifiers, dependencies, validity, and invalidation;
- interruption, checkpoint, resumption, and reopening behaviour; and
- the minimum audit history required for trustworthy recovery.

Other files own:

- workflow order, routing rules, and terminal behaviour: `../workflow/WORKFLOW.md`;
- gate meanings and evaluation criteria: `../workflow/GATES.md`;
- vision structure and artifact quality: `../contracts/VISION_CONTRACT.md`; and
- agent authority and operating posture: `../AGENT.md`.

This file persists those rules. It MUST NOT silently redefine them.

## Canonical state artifact

Each project MUST have exactly one current runtime-state artifact at:

`projects/<project-slug>/ideation/state.yaml`

The YAML record is the source of truth for runtime status, routing, record validity, and audit events. Narrative artifacts such as `vision.md` remain authoritative for their own substantive content and are referenced from state; they are not competing runtime-state stores.

Chat history, a previously displayed stage, and an unrecorded agent memory MUST NOT override the canonical state artifact.

A settled human decision's `authorization_id` MUST be backed by an approval evidence record at `projects/<project-slug>/ideation/approvals/<authorization_id>.json`. The tools layer writes it in the same commit as the change it authorizes. Evidence records are signed proof referenced from state, not a competing runtime-state store; their format and verification are defined in `../tools/README.md`.

The state record MUST be human-inspectable and deterministically parseable. A later machine-readable schema MAY enforce this contract, but schema absence does not weaken the requirements here.

## State model

The record MUST contain the following top-level sections:

| Section | Purpose |
|---|---|
| `schema_version` | Version of this state contract used by the record. |
| `project` | Stable project identity and current iteration. |
| `agent_provenance` | Exact reusable Ideation Agent repository commit governing the iteration. |
| `workflow` | Current run status and progression context. |
| `session` | Interruption and checkpoint information. |
| `routing` | Saved routing focus and the basis for selecting it. |
| `artifacts` | Versioned references to mutable project artifacts. |
| `decisions` | Consequential human decisions and their current validity. |
| `assumptions` | Provisional or validated assumptions and their risk. |
| `work_items` | Typed unresolved or resolved matters available to the router. |
| `evidence` | Evidence references and concise claim-level relevance. |
| `gate_evaluations` | Auditable gate outcomes, dependencies, and validity. |
| `finalization` | Approved-handoff or non-progressing closure checks. |
| `history` | Append-only consequential event log. |

Collections MAY be empty but MUST be present once the state is initialized. Records MUST use stable identifiers that are unique within the project. Cross-record relationships MUST use those identifiers rather than prose matching.

## Project and iteration identity

`project` MUST record:

- `project_id` and `project_slug`;
- `iteration` as a positive integer;
- `created_at` and `updated_at` timestamps;
- a monotonically increasing `revision`; and
- when applicable, the preceding iteration and the reason the current iteration was opened.

An `approved` or `not_progressing` iteration is immutable except for a corrective audit annotation that does not alter its substantive outcome. Reopening starts a new iteration in the same project. The new iteration MUST record why it was reopened and which earlier records or artifacts it inherits, revalidates, or supersedes.

## Agent provenance

`agent_provenance` MUST record the exact reusable Ideation Agent repository commit governing the current iteration as `repository_commit`. The value MUST be a full 40-character lowercase Git commit SHA.

This provenance identifies the reusable system version; it is not a project artifact and MUST NOT be represented in `artifacts`. A new iteration MUST record the agent commit that governs that iteration.

## Workflow, session, and vision status

### Workflow status

`workflow.status` MUST be exactly one of:

- `active`: ideation can continue;
- `deferred`: resumable, but paused pending a recorded condition, date, evidence, or decision;
- `approved`: terminal approved handoff; or
- `not_progressing`: terminal human-authorized closure without a handoff.

The state MAY record the normal spine location as orientation context, but it MUST NOT treat a stage label as the routing source of truth.

### Session status

`session.status` MUST be `active` or `paused`. It is operational and independent of `workflow.status`. A session pause does not defer or terminate the ideation run.

On pause, `session` MUST record the checkpoint time, concise resume summary, and any pending user interaction. State MUST be persisted after each consequential change rather than waiting for a graceful session end.

### Vision status

`workflow.vision_status` MUST be one of `not_started`, `draft`, `candidate`, or `approved`, matching the status in the current vision artifact when one exists.

A mismatch between state and the current artifact MUST be recorded as a blocking inconsistency until reconciled. A vision cannot be `approved` in a non-terminal active iteration, and `workflow.status: approved` is invalid unless all approved-handoff conditions in `WORKFLOW.md` are satisfied.

## Routing state and resumption

`routing` MUST record:

- `saved_focus_id`, referencing an open work item or pending gate action;
- a concise `selection_rationale`;
- the dependency and expected-value factors used to prioritize it;
- the smallest coherent next intervention;
- when the focus was selected; and
- whether human input, autonomous ideation, or blocked evidence gathering is required.

The saved focus is a recovery hint, not an authoritative instruction. At initialization and every resumption, the agent MUST:

1. validate the state structure and referenced artifact fingerprints;
2. detect material changes and record their impact;
3. check whether the saved focus remains open, unblocked, dependency-ready, and relevant;
4. reactivate deferred work items whose trigger or fallback review point has been reached;
5. identify current blocking deficiencies and invalid gate evaluations;
6. apply the dependency-first, expected-decision-value-second rule in `WORKFLOW.md`; and
7. replace or confirm the saved focus and record the new rationale.

The agent MUST NOT resume the saved focus unchanged merely because it was previously selected.

## Decisions

Each consequential decision MUST record:

- stable `id`, concise `question`, and `decision`;
- `authority`, normally `human` for matters reserved by `AGENT.md`;
- `status`: `settled`, `reconfirmation_required`, or `superseded`;
- concise rationale and material alternatives considered;
- explicit dependencies on evidence, assumptions, artifacts, or other records;
- affected gates or work items;
- decision-maker and timestamp; and
- superseding decision, when applicable.

A human decision MUST NOT be silently changed by the agent. If a material dependency changes, its status becomes `reconfirmation_required`. The prior decision remains visible, but it MUST NOT be treated as currently authoritative for affected progression until the human reconfirms or supersedes it.

## Assumptions

Each material assumption MUST record:

- stable `id` and concise proposition;
- `status`: `provisional`, `validated`, `rejected`, or `superseded`;
- origin and concise basis;
- materiality, risk, and confidence;
- validation method or disconfirming condition;
- explicit dependencies and affected records; and
- whether it is currently blocking, with a concise reason.

Blocking is risk- and materiality-based. An unresolved assumption MUST block affected progression when being wrong could invalidate a consequential decision, gate outcome, or coherent vision and the risk cannot safely be carried forward. Low-consequence assumptions MAY remain provisional when explicit and genuinely non-blocking.

## Routable work items

Deficiencies, questions, uncertainties, and escalations MUST use one typed `work_items` register so the router can compare them consistently.

Each item MUST record:

- stable `id`;
- `type`: `deficiency`, `question`, `uncertainty`, or `escalation`;
- concise title and description;
- `status`: `open`, `in_progress`, `deferred`, `resolved`, or `superseded`;
- materiality and whether it is blocking;
- origin and affected gate criteria or artifacts;
- prerequisite and downstream dependency identifiers;
- owner: `agent`, `human`, or `external_evidence`;
- smallest coherent next action;
- priority factors and concise rationale; and
- creation, update, and resolution metadata.

An escalation MUST state the smallest consequential human judgement required and the available options or trade-off. A non-blocking uncertainty MUST remain explicit but MUST NOT be routed ahead of blocking work merely because it is easy to investigate.

### Deferred items

A deferred item MUST include:

- why it was deferred;
- a specific reactivation trigger where one can be defined; and
- a fallback review point, such as a date or relevant gate boundary.

Reaching either condition causes reassessment, not automatic activation. The router MUST determine whether the item is still relevant, blocking, and dependency-ready.

## Evidence

Each material evidence record MUST include:

- stable `id`;
- the concise claim or question it bears on;
- source reference and retrieval or observation date;
- evidence type and provenance;
- concise relevance and limitations;
- confidence or quality assessment where useful; and
- identifiers of decisions, assumptions, work items, gates, or artifacts that rely on it.

The state SHOULD reference durable evidence artifacts rather than duplicate their full contents. Human preferences and agent inferences MUST NOT be labelled as evidence.

## Artifact references and fingerprints

Each mutable artifact reference MUST include:

- stable artifact identifier and role;
- repository-relative path;
- status;
- fingerprint algorithm and value;
- repository commit when available; and
- last verification timestamp.

The fingerprint MUST identify the artifact content, not merely its path or modification time. A content hash such as SHA-256 is preferred.

If a fingerprint changes, the agent MUST record a material-change event, identify records that explicitly depend on that artifact, and assess only those records and their dependants for invalidation. A changed artifact MUST NOT indiscriminately invalidate unrelated state.

## Gate-evaluation records

Every formal gate evaluation required by `GATES.md` MUST record:

- stable evaluation `id`, gate identifier, gate name, and gate class;
- evaluation timestamp and state revision;
- exactly one outcome: `PASS`, `PASS_WITH_UNCERTAINTY`, `FAIL`, or `ESCALATE`;
- pass criteria satisfied and unmet;
- material deficiencies and non-blocking uncertainties by record identifier;
- human judgement required and any decision made by record identifier;
- concise rationale;
- explicit dependencies on decisions, assumptions, evidence, artifacts, work items, and prior gate evaluations;
- `validity`: `current`, `re_evaluation_required`, or `superseded`;
- invalidation reason and triggering event, when applicable; and
- the evaluation that supersedes it, when applicable.

### Selective invalidation

When a material record changes, the agent MUST:

1. find current gate evaluations that explicitly depend on that record;
2. mark each affected evaluation `re_evaluation_required` and record why;
3. propagate invalidation to later evaluations that explicitly depend on an affected evaluation;
4. create or update the corresponding routable work item; and
5. preserve every evaluation for which no material dependency was affected.

An invalidated evaluation remains in the audit history. It MUST NOT be deleted, overwritten, or counted as a current valid gate result.

## Pending human decisions

Pending human input MUST be represented as an open `escalation` work item and, where it affects a gate, referenced by the gate evaluation. It MUST identify:

- why human authority is required;
- the recommendation and credible alternatives;
- material consequences or trade-offs;
- whether and what progression is blocked; and
- the smallest decision needed.

Silence, interruption, or an expired session MUST NOT be recorded as approval.

## Finalization and terminal invariants

`finalization` MUST contain explicit checks for the relevant terminal outcome.

For `approved`, it MUST record the eight approved-handoff conditions in `WORKFLOW.md`, including the authoritative approved vision reference and valid Gate 6 human approval. All checks MUST pass before `workflow.status` changes to `approved`.

For `not_progressing`, it MUST record the agent recommendation, explicit human decision, concise rationale, reconsideration conditions where relevant, and confirmation that no approved handoff exists.

Only an explicit human decision may authorize either final vision approval or `not_progressing` closure. Terminal transitions MUST append a consequential history event.

## Consequential event history

`history` is an append-only log of events needed to explain or reconstruct consequential state changes. It MUST include events for:

- consequential human decisions and later reconfirmation or supersession;
- material assumption or evidence changes;
- gate evaluation, invalidation, and supersession;
- material artifact changes;
- deferral, reframing, reopening, and terminal transitions;
- material routing-focus changes; and
- corrective state migrations or reconciliations.

Each event MUST include a stable `event_id`, timestamp, event type, actor, affected record identifiers, concise summary, resulting state revision, and related prior event where applicable.

The log MUST NOT contain private chain-of-thought, routine conversational exploration, redundant transcript text, or every mechanical field update. Concise decision-relevant rationale is sufficient.

## Persistence and consistency rules

The state update for a consequential event MUST atomically:

1. apply the authoritative snapshot change;
2. append its history event;
3. increment `project.revision`;
4. update timestamps and affected fingerprints; and
5. leave all cross-references resolvable.

If atomic replacement is unavailable, the agent MUST use the safest available write-and-verify mechanism and MUST NOT claim persistence until the written state has been read back or otherwise confirmed.

Derived summaries MAY be regenerated, but decisions, event history, terminal authorization, and superseded gate records MUST NOT be discarded merely to compact the file. Archival, if later needed, MUST preserve stable references and the ability to reconstruct the current state.

## Minimum YAML shape

The following illustrates structure, not a fully populated example:

```yaml
schema_version: 1
project:
  project_id: example
  project_slug: example
  iteration: 1
  revision: 1
  created_at: 2026-01-01T00:00:00Z
  updated_at: 2026-01-01T00:00:00Z

agent_provenance:
  repository_commit: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

workflow:
  status: active
  vision_status: not_started
  spine_context: orient_and_initialize

session:
  status: paused
  checkpointed_at: 2026-01-01T00:00:00Z
  resume_summary: Initial state created.
  pending_interaction_id: null

routing:
  saved_focus_id: null
  selection_rationale: null
  dependency_priority: null
  expected_decision_value: null
  next_intervention: null
  action_owner: null
  selected_at: null

artifacts: []
decisions: []
assumptions: []
work_items: []
evidence: []
gate_evaluations: []

finalization:
  outcome: null
  checks: []
  authorized_by_decision_id: null

history: []
```

Null values in the illustration mean not yet established. They MUST NOT be used to conceal a required unresolved item; material unknowns belong in `work_items` or `assumptions`.

## Completion criteria for this file

`ideation_state.md` is complete when:

1. one canonical, structured per-project state artifact and its authority are defined;
2. workflow, session, vision, deferred, and terminal statuses are unambiguous;
3. routing focus is persisted but revalidated on resumption;
4. decisions, assumptions, work items, evidence, artifacts, and gate evaluations have clear required semantics and lifecycles;
5. blocking and non-blocking matters are distinguishable;
6. dependencies support selective gate invalidation without requiring a full knowledge graph;
7. pending human decisions and human-only terminal authority are protected;
8. interruption, atomic persistence, reopening, and cross-session recovery are defined;
9. the audit model preserves consequential rationale without persisting chain-of-thought or routine exploration; and
10. the model is internally consistent with `AGENT.md`, `WORKFLOW.md`, `GATES.md`, and `VISION_CONTRACT.md`.
