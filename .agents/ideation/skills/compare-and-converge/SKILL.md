---
name: compare-and-converge
description: Compare credible broad directions and recommend convergence when alternatives exist but their trade-offs or preferred direction are unresolved.
metadata:
  schema_version: 1
  capability_class: reasoning
  default_autonomy: bounded-autonomous
  result_payload: direction-comparison
  side_effects: propose-only
  contract_dependencies:
    - .agents/ideation/AGENT.md
    - .agents/ideation/workflow/GATES.md
    - .agents/ideation/skills/SKILL_CONTRACT.md
  skill_dependencies: []
---

# Compare and Converge

## Purpose

Compare materially different directions on consequential benefits, risks, assumptions, constraints, dependencies, reversibility, and trade-offs; recommend a preferred broad direction without taking a reserved human decision.

## Invoke when

- credible alternatives exist and need structured comparison;
- Gate 4 lacks a visible basis for later convergence;
- Gate 5 lacks an explicit preferred direction or resolved trade-off; or
- new evidence or challenge findings alter the relative strength of directions.

## Do not invoke when

Do not use this skill to compensate for an inadequate alternative set, to make a consequential choice on the user's behalf, or to define downstream product requirements.

## Preconditions and inputs

Read the current alternative set, intent, problem model, ambitions, boundaries, evidence, assumptions, constraints, challenge findings, and prior relevant human decisions.

## Method

1. Compare directions on criteria that matter to the actual intent rather than generic scoring dimensions.
2. Make dominant trade-offs, dependencies, and disconfirming conditions explicit.
3. Distinguish evidence-backed differences from assumption-driven judgements.
4. Recommend the strongest direction and explain why credible alternatives are weaker.
5. Identify the smallest remaining consequential decision, if any.

## Output payload

Return `direction-comparison` containing evaluation criteria, comparison findings, preferred-direction recommendation, rationale, consequential trade-offs, assumptions, rejected directions with reasons, and any human decision required.

## State and artifact effects

Propose comparison findings, assumptions, work items, and decision records only after the human has actually decided. A recommendation is not a settled decision.

## Escalation conditions

Return `escalation_required` when materially viable directions depend on user values, stakeholder priority, scope, risk tolerance, or acceptance of a consequential trade-off not already expressed.

## Completion criteria

Credible directions have been compared on decision-relevant consequences, a recommendation and basis are explicit, and any remaining human choice is narrowly framed with credible alternatives and trade-offs.
