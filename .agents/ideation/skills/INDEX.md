# Ideation Skill Index

## Purpose

This is the authoritative registry of reusable skills available to the single ideation agent. Skill selection is deficiency-driven. The order below groups related capabilities; it is not an execution sequence.

All skills conform to `SKILL_CONTRACT.md`. They return the common result envelope, propose rather than apply mutations, and inherit authority boundaries from `../AGENT.md`.

## Registry

| Skill | Class | Invoke when | Primary payload | Material precondition |
|---|---|---|---|---|
| [`clarify-intent`](clarify-intent/SKILL.md) | reasoning | Core intent is new, incomplete, contradictory, or materially ambiguous. | Intent model and remaining ambiguities. | Available user statements and current valid decisions. |
| [`expand-ambition`](expand-ambition/SKILL.md) | reasoning | The initial framing needs systematic expansion or Gate 2 has a deficiency. | Ambition options and carry/reject/defer recommendations. | Intent is sufficiently clear to expand without changing its meaning silently. |
| [`model-problem`](model-problem/SKILL.md) | reasoning | A solution-independent diagnosis is missing, weak, or invalidated. | Problem or opportunity model. | Relevant intent, people, boundaries, evidence, and assumptions are available. |
| [`generate-alternatives`](generate-alternatives/SKILL.md) | reasoning | The solution space is absent, narrow, or composed of cosmetic variants. | Materially distinct direction set. | Intent and problem model are adequate for divergent exploration. |
| [`compare-and-converge`](compare-and-converge/SKILL.md) | reasoning | Credible directions exist and their trade-offs or preferred direction need assessment. | Comparison, recommendation, and decision requirement. | Materially distinct alternatives and evaluation context exist. |
| [`focused-challenge`](focused-challenge/SKILL.md) | assurance | A material concern needs stress-testing or the mandatory pre-Gate-5 challenge is due. | Challenge findings and required responses. | A defined proposition, model, or preferred direction can be challenged. |
| [`research-blocking-evidence`](research-blocking-evidence/SKILL.md) | evidence | An open evidence gap blocks a gate or safe routing decision. | Evidence findings, provenance, limitations, and remaining gap. | A specific blocking evidence work item exists. |
| [`assess-change-impact`](assess-change-impact/SKILL.md) | assurance | A decision, assumption, evidence item, artifact, or preference may have changed materially. | Materiality and dependency-impact assessment. | Old and new basis plus current dependency references are available. |
| [`select-next-intervention`](select-next-intervention/SKILL.md) | routing | A run starts or resumes, or a material result requires routing to be recomputed. | Proposed routing focus and rationale. | Canonical state and referenced fingerprints have been deterministically validated. |
| [`evaluate-gate`](evaluate-gate/SKILL.md) | assurance | A planned boundary or material change requires formal gate evaluation. | One structured gate-evaluation proposal. | The target gate, current evidence, and relevant valid state are known. |
| [`synthesize-vision`](synthesize-vision/SKILL.md) | reasoning | Valid Gate 5 permits a draft vision to be created or substantively revised. | Draft vision and source mapping. | Gate 5 is current and passing; no blocking discovery remains. |
| [`validate-vision`](validate-vision/SKILL.md) | assurance | A draft or candidate vision must be tested against the vision contract. | Contract test results, deficiencies, and candidate eligibility. | A current vision artifact and authoritative contract are available. |

## Declarative dependency model

Skills do not form a fixed chain and MUST NOT call a successor. Eligibility is determined from current state and the preconditions above.

Direct `skill_dependencies` are intentionally empty in the baseline. Capabilities depend on valid state or artifacts, not proof that a particular earlier skill ran. For example, `synthesize-vision` requires a current passing Gate 5 evaluation, regardless of which interventions produced the underlying material.

## Composition for lifecycle cases

| Case | Composition |
|---|---|
| New run | Workflow initialization, then `select-next-intervention`; commonly routes to `clarify-intent`. |
| Interrupted run | Deterministic state and fingerprint validation, `assess-change-impact` if anything changed, then `select-next-intervention`. |
| Gate failure | Record the deficiency, then `select-next-intervention` chooses the smallest eligible reasoning, evidence, or assurance skill. |
| Selective re-evaluation | `assess-change-impact` proposes targeted invalidations; deterministic application preserves unaffected records; `evaluate-gate` reassesses only affected gates. |
| Reframe | Reuse the affected content skills, assess the change, and reroute; do not invoke a generic restart skill. |
| Defer | Workflow records a trigger and fallback review point; no standalone skill is required. |
| Stop | Agent recommends with rationale; only the human authorizes `not_progressing`; deterministic finalization records it. |
| Approved handoff | `synthesize-vision`, `validate-vision`, Gate 6 through `evaluate-gate`, then deterministic workflow finalization. |

## Excluded standalone skills

The baseline deliberately has no skills for asking questions, generic decision support, ordinary challenge, state mutation, checkpointing, deferral, stopping, reopening, or finalization. These are cross-cutting agent behaviours, workflow/state operations, or compositions of the registered capabilities.
