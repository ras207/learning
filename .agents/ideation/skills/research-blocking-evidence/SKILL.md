---
name: research-blocking-evidence
description: Research a narrowly scoped evidence gap only when that gap blocks a gate or prevents the router from identifying a safe next action.
metadata:
  schema_version: 1
  capability_class: evidence
  default_autonomy: bounded-autonomous
  result_payload: evidence-intervention
  side_effects: propose-only
  contract_dependencies:
    - .agents/ideation/AGENT.md
    - .agents/ideation/workflow/WORKFLOW.md
    - .agents/ideation/state/ideation_state.md
    - .agents/ideation/skills/SKILL_CONTRACT.md
  skill_dependencies: []
---

# Research Blocking Evidence

## Purpose

Resolve or narrow one blocking evidence gap through proportionate external or repository research, preserving provenance, limitations, and the distinction between evidence and inference.

## Invoke when

Invoke only when an open work item owned by `external_evidence` identifies a specific evidence gap that prevents a gate from validly passing or prevents safe routing.

## Do not invoke when

Do not research non-blocking curiosity, general background, an unresolved human preference, or a question that available project evidence already answers. Do not broaden the scope merely because tools are available.

## Preconditions and inputs

Require the blocking work-item identifier, exact claim or question, affected gate criterion or routing decision, consequence of error, existing evidence, proportional search scope, and permitted tools or sources.

## Method

1. Confirm that the need is evidential rather than a human judgement.
2. Define the smallest research question capable of unblocking progress.
3. Prefer authoritative and directly relevant sources; triangulate where consequence warrants it.
4. Record retrieval dates, provenance, relevance, limitations, and quality.
5. State whether the evidence resolves, narrows, contradicts, or fails to answer the blocking question.
6. Stop when the defined need is answered sufficiently or the evidence is unavailable.

## Output payload

Return `evidence-intervention` containing the scoped question, method, findings, source references, evidence quality, limitations, answer confidence, affected records, and any remaining gap.

## State and artifact effects

Propose evidence records, updates to the originating work item and assumptions, and any material-change assessment required. Do not label preference, inference, or source-free synthesis as evidence.

## Escalation conditions

Escalate only when evidence cannot resolve the blockage and progress then requires the user to accept risk, choose a value-laden interpretation, provide access, or change scope. Otherwise return `blocked` with the unavailable evidence stated.

## Completion criteria

The blocking question has been answered proportionately or its evidential limit is explicit; sources, provenance, relevance, limitations, confidence, and affected dependencies are recorded; and no unrelated research has been introduced.
