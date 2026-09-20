---
name: evaluate-gate
description: Apply the authoritative gate criteria at a planned boundary or after material change and propose one auditable formal gate evaluation.
metadata:
  schema_version: 1
  capability_class: assurance
  default_autonomy: bounded-autonomous
  result_payload: gate-evaluation
  side_effects: propose-only
  contract_dependencies:
    - .agents/ideation/workflow/GATES.md
    - .agents/ideation/workflow/WORKFLOW.md
    - .agents/ideation/state/ideation_state.md
    - .agents/ideation/skills/SKILL_CONTRACT.md
  skill_dependencies: []
---

# Evaluate Gate

## Purpose

Evaluate exactly one gate against `GATES.md` using current valid evidence and state, producing one honest, structured outcome without changing gate criteria or deciding routing.

## Invoke when

- the workflow reaches a planned gate boundary;
- a material change requires an affected gate to be re-evaluated; or
- validation reveals that a required gate record is missing, stale, or internally inconsistent.

## Do not invoke when

Do not use this skill for informal progress commentary, to route a deficiency, to waive criteria, or to create a favourable outcome for a preferred direction.

## Preconditions and inputs

Identify the target gate and read its authoritative class, purpose, evidence, criteria, outcome conditions, and human authority. Read current valid decisions, assumptions, evidence, artifacts, work items, prior evaluations, state revision, and relevant skill results.

## Method

1. Test every pass criterion against current valid material.
2. Separate unmet criteria, blocking deficiencies, and explicit non-blocking uncertainty.
3. Use exactly one permitted outcome and apply its definition strictly.
4. Use `FAIL` only when further ideation can proceed without new consequential human judgement.
5. Use `ESCALATE` only when such judgement is required.
6. For Gate 6, require explicit human approval; never infer it.
7. Record dependencies sufficient for later selective invalidation.

## Output payload

Return `gate-evaluation` containing gate identity and class, outcome, criteria satisfied and unmet, deficiency identifiers, non-blocking uncertainties, human judgement required or made, rationale, dependencies, and proposed validity status.

## State and artifact effects

Propose one gate-evaluation record plus linked work items, escalation, and history event. Do not route the outcome, approve a vision, or erase a superseded evaluation.

## Escalation conditions

Return `escalation_required` with a proposed `ESCALATE` evaluation when the gate cannot progress without the smallest consequential human judgement defined by `GATES.md`.

## Completion criteria

All criteria were inspected, exactly one outcome follows the authoritative semantics, deficiencies and uncertainties are correctly classified and linked, human authority is protected, and dependency references support selective re-evaluation.
