---
name: select-next-intervention
description: Select the smallest coherent next intervention from validated current state at initialization, resumption, or after a material workflow result.
metadata:
  schema_version: 1
  capability_class: routing
  default_autonomy: bounded-autonomous
  result_payload: routing-selection
  side_effects: propose-only
  contract_dependencies:
    - .agents/ideation/AGENT.md
    - .agents/ideation/workflow/WORKFLOW.md
    - .agents/ideation/state/ideation_state.md
    - .agents/ideation/skills/INDEX.md
    - .agents/ideation/skills/SKILL_CONTRACT.md
  skill_dependencies: []
---

# Select Next Intervention

## Purpose

Apply the workflow's dependency-first, expected-decision-value-second routing rule to current state and propose one saved focus and smallest coherent next intervention.

## Invoke when

- a new state has been initialized;
- a paused or deferred run resumes;
- a skill, gate evaluation, human decision, or material-change assessment alters the state; or
- the saved focus is closed, blocked, invalid, or no longer highest priority.

## Do not invoke when

Do not use stale or unvalidated state, treat a spine label as the routing source of truth, or let an individual skill select its successor.

## Preconditions and inputs

Canonical state structure and artifact fingerprints must have been deterministically validated. Read open and deferred work items, current and invalid gate evaluations, dependencies, materiality, blocking status, owners, reactivation conditions, saved focus, and the skill registry.

## Method

1. Revalidate the saved focus rather than trusting it.
2. Reassess deferred items whose trigger or fallback review point was reached.
3. Identify current blocking deficiencies, invalid evaluations, and pending escalations.
4. Prioritize the earliest causal deficiency blocking the greatest dependent work.
5. Break equally foundational ties by expected decision value.
6. Select the smallest coherent eligible intervention and its owner.
7. Preserve unaffected work and explain why lower-priority items were not selected.

## Output payload

Return `routing-selection` containing selected focus identifier, causal deficiency, priority factors, eligibility check, selected skill or human/evidence action, smallest intervention, expected result, and rationale.

## State and artifact effects

Propose routing focus, action owner, selection time, intervention, and concise material history change where required. Do not execute the selected skill within the same invocation.

## Escalation conditions

Select an existing or proposed human escalation when progress depends on consequential judgement. Escalate a routing ambiguity only if priorities depend on an unexpressed human value; ordinary tie-breaking remains autonomous.

## Completion criteria

One eligible next focus is justified by current dependencies and expected decision value, the intervention is the smallest coherent one, the action owner is explicit, saved focus was revalidated, and no fixed stage or successor rule was substituted for current state.
