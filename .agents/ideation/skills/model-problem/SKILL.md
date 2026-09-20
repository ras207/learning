---
name: model-problem
description: Build or repair a solution-independent model of the problem or opportunity when diagnosis is missing, weak, contradictory, or invalidated.
metadata:
  schema_version: 1
  capability_class: reasoning
  default_autonomy: bounded-autonomous
  result_payload: problem-model
  side_effects: propose-only
  contract_dependencies:
    - .agents/ideation/AGENT.md
    - .agents/ideation/workflow/GATES.md
    - .agents/ideation/skills/SKILL_CONTRACT.md
  skill_dependencies: []
---

# Model Problem

## Purpose

Produce a solution-independent account of the problem or opportunity, who or what it affects, its important mechanisms, current approaches, and why the current state is inadequate.

## Invoke when

- Gate 3 is pending, failed, or invalidated;
- the problem is defined mainly as absence of the proposed solution;
- causal or contextual mechanisms are too weak for alternative generation; or
- evidence, assumptions, current approaches, or affected people are materially unclear.

## Do not invoke when

Do not use this skill to select a solution, conduct unguarded research, or relitigate a problem model whose relevant conclusions remain valid.

## Preconditions and inputs

Read current intent, accepted ambitions, people and stakeholder records, evidence, assumptions, boundaries, current approaches, relevant work items, and the latest Gate 3 evaluation if one exists.

## Method

1. State the problem or opportunity without relying on the proposed solution.
2. Identify affected people or systems and the nature of the impact.
3. Map the important causes, mechanisms, incentives, or contextual drivers at the depth needed for direction exploration.
4. Describe relevant workarounds, substitutes, or existing approaches and their inadequacy.
5. Label each material proposition as evidence, inference, or assumption.
6. Surface a blocking evidence gap rather than researching it automatically.

## Output payload

Return `problem-model` containing the solution-independent definition, affected parties, mechanisms, current approaches, inadequacy, evidence links, assumptions, contradictions, and unresolved diagnostic questions.

## State and artifact effects

Propose evidence, assumption, work-item, routing, and history changes. Do not present agent inference as evidence or directly mutate state.

## Escalation conditions

Escalate when choosing the problem worth solving, the priority beneficiary, or the acceptable interpretation depends on a consequential human value judgement. Use `blocked` for a required external evidence gap.

## Completion criteria

The diagnosis is solution-independent, affected parties and material mechanisms are clear enough to guide alternatives, current approaches and inadequacy are explicit, and important assumptions and evidence gaps are visible.
