---
name: synthesize-vision
description: Synthesize validated ideation material into a draft vision when Gate 5 currently passes and no blocking discovery remains unresolved.
metadata:
  schema_version: 1
  capability_class: reasoning
  default_autonomy: bounded-autonomous
  result_payload: vision-draft
  side_effects: propose-only
  contract_dependencies:
    - .agents/ideation/contracts/VISION_CONTRACT.md
    - .agents/ideation/workflow/WORKFLOW.md
    - .agents/ideation/state/ideation_state.md
    - .agents/ideation/skills/SKILL_CONTRACT.md
  skill_dependencies: []
---

# Synthesize Vision

## Purpose

Transform the current valid ideation material into a coherent `status: draft` vision that follows `VISION_CONTRACT.md` without using polished prose to conceal unresolved discovery.

## Invoke when

- Gate 5 has a current `PASS` or valid `PASS_WITH_UNCERTAINTY`;
- no blocking question, deficiency, invalid required gate, or pending consequential choice remains; and
- a vision draft must be created or substantively revised after valid upstream change.

## Do not invoke when

Do not synthesize before Gate 5 permits it, invent missing intent, mark the vision `candidate` or `approved`, or introduce downstream product-design detail as settled vision content.

## Preconditions and inputs

Read the current Gate 5 evaluation, all other required current gate records, valid decisions, evidence, assumptions, non-blocking uncertainties, boundaries, preferred direction, challenge findings, and the full vision contract.

## Method

1. Map authoritative source material to every required vision section.
2. Resolve wording-level coherence without changing consequential meaning.
3. Preserve critical assumptions, boundaries, and non-blocking uncertainty explicitly.
4. Keep the chosen direction specific enough to constrain design but free of premature requirements or architecture.
5. Set metadata to `status: draft` and an appropriate version; leave eligibility judgement to `validate-vision`.

## Output payload

Return `vision-draft` containing the complete proposed Markdown content, source-to-section mapping, assumptions carried forward, unresolved non-blocking questions, and any synthesis warning.

## State and artifact effects

Propose creation or update of `projects/<project-slug>/ideation/vision.md`, its fingerprint-bearing artifact record, `workflow.vision_status: draft`, and a concise history event. Deterministic tooling must write and verify the artifact.

## Escalation conditions

Escalate if synthesis exposes materially conflicting valid decisions or if coherent drafting would require choosing new intent, direction, scope, stakeholder priority, or trade-off. Return `blocked` for an unmet non-human prerequisite.

## Completion criteria

Every required section has substantive source-grounded content, the draft is internally coherent at vision level, critical assumptions and uncertainty are visible, no consequential content was invented, and no status beyond `draft` is claimed.
