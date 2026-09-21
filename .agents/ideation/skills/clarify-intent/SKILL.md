---
name: clarify-intent
description: Clarify a new, incomplete, contradictory, or materially ambiguous idea into an intent model without silently choosing consequential meaning.
metadata:
  schema_version: 1
  capability_class: reasoning
  default_autonomy: bounded-autonomous
  result_payload: intent-model
  side_effects: propose-only
  contract_dependencies:
    - .agents/ideation/AGENT.md
    - .agents/ideation/workflow/GATES.md
    - .agents/ideation/skills/SKILL_CONTRACT.md
  skill_dependencies: []
---

# Clarify Intent

## Purpose

Produce a sufficiently clear account of the user's starting intent, desired change, relevant people, and consequential boundaries without fixing the solution prematurely.

## Invoke when

- a run begins with an unstructured idea;
- Gate 1 has failed or escalated;
- current intent records are incomplete, contradictory, or invalidated; or
- a material change creates more than one plausible interpretation of what the user now wants.

## Do not invoke when

Do not use this skill merely because implementation detail is unknown, to expand ambition, or to replace a settled human decision. Use the affected downstream capability when intent remains valid.

## Preconditions and inputs

Read the user's available statements, current valid decisions and assumptions, relevant project context, open intent-related work items, and any prior Gate 1 evaluation. Distinguish missing information from a choice that belongs to the user.

## Method

1. Extract the trigger or motivation, desired change, relevant people, expressed boundaries, and proposed solution language.
2. Reframe solution language as intent only where the meaning remains supported.
3. Identify ambiguities that could lead to materially different exploration.
4. Resolve supported, reversible details autonomously.
5. Ask the smallest focused question when a consequential interpretation cannot be inferred safely.
6. Preserve rejected, deferred, or superseded intent explicitly rather than blending it into the current model.

## Output payload

Return `intent-model` containing the trigger, current intent, desired change, relevant people or stakeholders, expressed boundaries, solution commitments that are genuinely intentional, and remaining ambiguities with materiality.

## State and artifact effects

Propose decision, assumption, work-item, routing, and history updates as needed. Do not directly edit canonical state or create a vision artifact.

## Escalation conditions

Return `escalation_required` when materially different interpretations remain, stakeholder priorities conflict, or clarification would change the desired outcome, scope, beneficiary, or consequential boundary.

## Completion criteria

The invocation is complete when the core intent and desired change are understandable, relevant people are clear enough for exploration, consequential boundaries already expressed are visible, and no unresolved ambiguity would cause pursuit of a materially different idea.
