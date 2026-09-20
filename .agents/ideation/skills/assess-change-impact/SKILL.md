---
name: assess-change-impact
description: Assess whether a changed record or artifact is material and identify only the dependent conclusions that require invalidation or reconfirmation.
metadata:
  schema_version: 1
  capability_class: assurance
  default_autonomy: bounded-autonomous
  result_payload: change-impact-assessment
  side_effects: propose-only
  contract_dependencies:
    - .agents/ideation/workflow/WORKFLOW.md
    - .agents/ideation/state/ideation_state.md
    - .agents/ideation/skills/SKILL_CONTRACT.md
  skill_dependencies: []
---

# Assess Change Impact

## Purpose

Judge the materiality of a changed decision, assumption, evidence record, artifact, preference, or external fact and propose selective dependency-driven invalidation without rerunning unaffected work.

## Invoke when

- a validated fingerprint differs;
- evidence, an assumption, or a user preference changes;
- a contradiction is discovered;
- a settled human decision's basis may have changed; or
- substantive vision or direction edits could affect current gate evaluations.

## Do not invoke when

Do not use for purely mechanical metadata changes already defined as immaterial, routine state persistence, or selection of the next intervention.

## Preconditions and inputs

Read the old and new basis, changed record or artifact identifier, current explicit dependencies, current gate evaluations, affected work items, and the relevant materiality standard.

## Method

1. Describe the change without conflating it with its consequence.
2. Assess whether it could alter a consequential decision, assumption status, artifact coherence, gate criterion, or downstream rationale.
3. Traverse only explicit dependencies and their dependent evaluations.
4. Preserve records with no material dependency.
5. Identify human decisions requiring reconfirmation rather than silently changing them.
6. Propose the smallest set of invalidations and new or updated work items.

## Output payload

Return `change-impact-assessment` containing materiality, changed identifiers, directly affected records, dependent gate evaluations, preserved records, reconfirmation needs, proposed invalidations, and rationale.

## State and artifact effects

Propose `re_evaluation_required`, `reconfirmation_required`, work-item, and history changes. Deterministic machinery must apply dependency traversal results and verify references atomically.

## Escalation conditions

Escalate when judging the consequence requires a human value decision or when a changed basis makes a settled human decision require reconfirmation. Ambiguous dependencies are a blocking state defect, not permission to invalidate everything.

## Completion criteria

Materiality is explicit, every proposed invalidation has a traceable dependency basis, unaffected work is preserved, reconfirmation needs are visible, and the assessment does not choose the next intervention.
