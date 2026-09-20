---
name: expand-ambition
description: Expand a sufficiently clear idea across users, outcomes, scope, and second-order opportunities when ambition has not been explored adequately.
metadata:
  schema_version: 1
  capability_class: reasoning
  default_autonomy: bounded-autonomous
  result_payload: ambition-map
  side_effects: propose-only
  contract_dependencies:
    - .agents/ideation/AGENT.md
    - .agents/ideation/workflow/GATES.md
    - .agents/ideation/skills/SKILL_CONTRACT.md
  skill_dependencies: []
---

# Expand Ambition

## Purpose

Challenge the first framing and surface materially larger or more valuable versions of the opportunity before the workflow narrows.

## Invoke when

- Gate 2 has not yet been evaluated;
- Gate 2 identifies shallow exploration;
- a material change opens a plausible larger opportunity; or
- the current idea appears constrained by its first solution, audience, outcome, or operating scale.

## Do not invoke when

Do not expand for its own sake after the opportunity space is sufficient, and do not use ambition to override an explicit boundary or to generate detailed features.

## Preconditions and inputs

The current intent must be clear enough that expansion will not silently change its meaning. Read current boundaries, people, desired outcomes, assumptions, rejected ambitions, and the latest valid Gate 1 record.

## Method

Explore distinct dimensions where plausible: other users or beneficiaries, more valuable outcomes, different scope, leverage or generality, second-order effects, and more ambitious future states. Separate compatible extensions from material reframings. Recommend which ambitions to carry forward, reject, or defer and explain why.

## Output payload

Return `ambition-map` containing explored dimensions, materially expanded possibilities, compatibility with current intent, expected value, risks, and carry/reject/defer recommendations.

## State and artifact effects

Propose assumptions, decisions, work items, and concise history events. A materially expanded ambition must remain a proposal until the user authorizes the change.

## Escalation conditions

Escalate when carrying an ambition forward would materially change scope, beneficiaries, desired outcomes, risk tolerance, cost exposure, or another consequential preference.

## Completion criteria

The initial framing has been challenged across relevant dimensions, plausible high-value expansions are visible, and each material ambition is clearly carried forward, rejected, deferred, or awaiting a specific human decision.
