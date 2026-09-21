---
name: validate-vision
description: Validate a draft or candidate vision semantically against the vision contract and report deficiencies before candidate status or approval.
metadata:
  schema_version: 1
  capability_class: assurance
  default_autonomy: bounded-autonomous
  result_payload: vision-validation
  side_effects: propose-only
  contract_dependencies:
    - .agents/ideation/contracts/VISION_CONTRACT.md
    - .agents/ideation/workflow/GATES.md
    - .agents/ideation/workflow/WORKFLOW.md
    - .agents/ideation/state/ideation_state.md
    - .agents/ideation/skills/SKILL_CONTRACT.md
  skill_dependencies: []
---

# Validate Vision

## Purpose

Independently test a current vision artifact for required structure, substantive quality, coherence, uncertainty handling, scope discipline, and consistency with valid ideation state.

## Invoke when

- a new or revised draft must be assessed for `candidate` eligibility;
- a candidate must be rechecked before Gate 6 or finalization;
- a material change or fingerprint mismatch may have invalidated prior validation; or
- Gate 5 or Gate 6 exposes an artifact-quality deficiency.

## Do not invoke when

Do not author missing content silently, substitute for process gate evaluation, approve the vision, or treat structural presence as proof of substantive quality.

## Preconditions and inputs

Read the full current vision, verified fingerprint, `VISION_CONTRACT.md`, current valid decisions and assumptions, non-blocking uncertainties, required gate records, and any previous validation findings. Deterministic structural checks should be available or their absence recorded.

## Method

1. Check metadata and every required section structurally.
2. Test every artifact quality condition in the vision contract substantively.
3. Compare consequential content with current valid state and identify contradictions or unsupported additions.
4. Check that implementation detail has not displaced vision-level reasoning.
5. Confirm that all remaining questions are explicit and genuinely non-blocking.
6. Separate repairable drafting defects from upstream discovery, decision, or evidence deficiencies.

## Output payload

Return `vision-validation` containing structural results, section assessments, quality-condition results, state-consistency findings, scope violations, blocking deficiencies, non-blocking warnings, and `candidate_eligible`.

## State and artifact effects

Propose work items and, only when all checks pass, the state and metadata transition from `draft` to `candidate`. Deterministic tooling must apply and verify any status or artifact change. Never propose `approved` without Gate 6 and finalization.

## Escalation conditions

Escalate when a defect can be resolved only by a new consequential human judgement. Route evidence or ideation deficiencies through their appropriate work items rather than asking the user to approve weak content.

## Completion criteria

Every contract requirement and quality condition has an explicit result, inconsistencies and scope violations are visible, deficiencies are correctly routed, and candidate eligibility is asserted only when no blocking artifact or upstream issue remains.
