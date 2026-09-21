---
name: generate-alternatives
description: Generate materially different broad solution directions when the explored solution space is absent, narrow, or limited to cosmetic variants.
metadata:
  schema_version: 1
  capability_class: reasoning
  default_autonomy: bounded-autonomous
  result_payload: alternative-set
  side_effects: propose-only
  contract_dependencies:
    - .agents/ideation/AGENT.md
    - .agents/ideation/workflow/GATES.md
    - .agents/ideation/skills/SKILL_CONTRACT.md
  skill_dependencies: []
---

# Generate Alternatives

## Purpose

Create a set of broad directions that differ in consequential mechanism, scope, beneficiary model, delivery model, intervention level, operating model, or assumptions.

## Invoke when

- Gate 4 has not yet been satisfied;
- existing options are missing or superficial variants;
- a problem or ambition change invalidates the solution space; or
- a focused challenge shows that an important plausible region was omitted.

## Do not invoke when

Do not rank or select directions, generate detailed product features, or add options solely to reach an arbitrary count.

## Preconditions and inputs

Intent and the problem model must be adequate for divergent exploration. Read accepted ambitions, boundaries, people, assumptions, constraints, evidence, and already rejected or superseded alternatives.

## Method

1. Identify the dimensions along which approaches could differ materially.
2. Explore important plausible regions before elaborating familiar options.
3. Describe each direction at vision level: core mechanism, intended change, relevant people, major assumptions, and distinguishing boundaries.
4. Avoid evaluation language that prematurely anchors convergence.
5. Stop when further options would be redundant or materially lower value, not at a fixed count.

## Output payload

Return `alternative-set` containing the explored dimensions, materially distinct directions, distinguishing mechanisms, critical assumptions, boundary implications, and any credible region not explored with rationale.

## State and artifact effects

Propose alternative-related assumptions, work items, and history records. Do not select a preferred direction or alter a settled human decision.

## Escalation conditions

Escalate only if generating a meaningful direction requires choosing a consequential scope, beneficiary, risk tolerance, or boundary that the user has not expressed. Otherwise keep alternatives explicit without adopting them.

## Completion criteria

The important plausible regions of the solution space are represented by genuinely distinct directions, with enough definition for comparison and without premature feature design or convergence.
