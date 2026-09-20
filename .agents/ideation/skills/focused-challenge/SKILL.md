---
name: focused-challenge
description: Stress-test a material proposition or preferred direction when a specific concern exists or the mandatory pre-synthesis challenge is due.
metadata:
  schema_version: 1
  capability_class: assurance
  default_autonomy: bounded-autonomous
  result_payload: challenge-assessment
  side_effects: propose-only
  contract_dependencies:
    - .agents/ideation/AGENT.md
    - .agents/ideation/workflow/WORKFLOW.md
    - .agents/ideation/skills/SKILL_CONTRACT.md
  skill_dependencies: []
---

# Focused Challenge

## Purpose

Perform a deliberate, bounded stress test of a problem model, assumption, comparison, or preferred direction. This supplements the agent's continuous challenge posture and satisfies the focused pre-synthesis challenge required by `WORKFLOW.md`.

## Invoke when

- the preferred direction is approaching Gate 5;
- a material assumption, causal claim, contradiction, or failure mode needs concentrated testing;
- new evidence materially weakens a current conclusion; or
- the user requests a substantive challenge.

## Do not invoke when

Do not manufacture objections after the material design space is sufficiently understood, repeat a resolved challenge without new basis, or use challenge to override an informed human decision.

## Preconditions and inputs

Identify the proposition under test, its dependencies, supporting evidence and assumptions, stated intent and boundaries, credible alternatives, and prior challenge findings.

## Method

Test causal logic, critical assumptions, contradictions, failure modes, disconfirming evidence, boundary conflicts, and whether a credible alternative is materially stronger. Rank findings by consequence rather than volume. For the pre-synthesis invocation, cover every challenge dimension required by `WORKFLOW.md`.

## Output payload

Return `challenge-assessment` containing the proposition tested, strongest objections, failure modes, disconfirming conditions, unresolved contradictions, comparative challenge, severity, and recommended response.

## State and artifact effects

Propose new or updated assumptions, deficiencies, uncertainties, escalations, and change-impact work items. Do not invalidate records directly; use `assess-change-impact` where dependency effects require judgement.

## Escalation conditions

Escalate when the response requires accepting a consequential risk or trade-off, changing intent or scope, selecting a materially different direction, or reconfirming a human decision whose basis changed.

## Completion criteria

The strongest material challenge has been made proportionately, its consequence is explicit, required responses are identified, and no serious finding is softened or multiplied merely to support a preferred outcome.
