# Ideation Skill Contract

## Purpose

This file defines the common contract for reusable capabilities used by the single ideation agent. A skill performs one independently invocable reasoning or assurance operation. It does not become a separate agent, acquire decision authority, choose its successor, or redefine the workflow, gates, vision contract, or runtime state.

## Authority and responsibility boundaries

The following files remain authoritative:

- agent role, judgement boundaries, and interaction posture: `../AGENT.md`;
- workflow order, invocation points, dynamic routing, and terminal behaviour: `../workflow/WORKFLOW.md`;
- gate criteria and outcomes: `../workflow/GATES.md`;
- vision structure and quality: `../contracts/VISION_CONTRACT.md`; and
- canonical runtime-state semantics: `../state/ideation_state.md`.

Skills MUST apply those contracts and MUST NOT restate them as competing rules. If a skill file conflicts with an authoritative contract, the authoritative contract wins and the conflict is a blocking system defect.

The agent MUST select a skill from the current deficiency and validated project state. A skill MUST NOT prescribe a fixed next skill. After every material result, the workflow recomputes the next action.

## Organization and naming

Each skill lives at:

`skills/<skill-name>/SKILL.md`

Names MUST use lowercase hyphenated verbs or verb phrases and MUST match the frontmatter `name`. Shared schemas live in `skills/schemas/`. `INDEX.md` is the authoritative skill registry.

## Required frontmatter

Every `SKILL.md` MUST begin with YAML frontmatter conforming to `schemas/skill-metadata.schema.json`.

Required fields are:

- `name`: stable skill identifier;
- `description`: concise capability and invocation cue;
- `metadata.schema_version`;
- `metadata.capability_class`;
- `metadata.default_autonomy`;
- `metadata.result_payload`;
- `metadata.side_effects`;
- `metadata.contract_dependencies`; and
- `metadata.skill_dependencies`.

`skill_dependencies` identifies only a genuine requirement for another skill's output. It MUST NOT encode the normal workflow sequence. Most dependencies should instead be expressed as state or artifact preconditions in the Markdown body.

## Required Markdown sections

Every skill file MUST define:

1. **Purpose** — the single capability and the result it exists to produce.
2. **Invoke when** — observable state, deficiency, or workflow conditions that make the skill relevant.
3. **Do not invoke when** — material exclusions that prevent likely misuse.
4. **Preconditions and inputs** — the minimum validated context needed for a sound invocation.
5. **Method** — capability-specific reasoning instructions, without reproducing general agent policy.
6. **Output payload** — the skill-specific content placed in the common result envelope.
7. **State and artifact effects** — permitted proposals and prohibited direct effects.
8. **Escalation conditions** — conditions under which human authority or evidence is required.
9. **Completion criteria** — observable conditions for a completed invocation.

Sections MAY be combined when clarity improves, but their semantics MUST remain explicit.

## Invocation and autonomy

Skills use bounded autonomy. `metadata.default_autonomy` declares the normal posture, while each body defines capability-specific escalation conditions.

A skill MAY autonomously analyse, generate, compare, challenge, recommend, or assess within its contract. It MUST return `escalation_required` before substituting agent judgement for a consequential human choice protected by `AGENT.md`.

The invocation is invalid if its preconditions are not satisfied. The skill should return `blocked` or `escalation_required` rather than manufacture missing inputs. Human silence is never approval.

## Common result envelope

Every invocation MUST return an object conforming to `schemas/skill-result.schema.json` with:

- identity and status;
- a concise decision-relevant summary;
- one skill-specific `payload` object;
- unresolved items;
- proposed state and artifact changes;
- an explicit human escalation when required;
- evidence references; and
- warnings.

The common status values are:

- `completed`: the invocation's completion criteria are satisfied;
- `partial`: useful output exists but the capability remains incomplete;
- `blocked`: progress requires an unmet prerequisite or unavailable evidence;
- `escalation_required`: progress requires consequential human judgement; and
- `failed`: execution did not produce a reliable result.

`completed` describes the skill invocation only. It does not imply that a gate passed, a vision is approved, or the workflow is complete.

## State and artifact mutation boundary

Generative skills MUST NOT directly mutate the canonical state record or claim that a proposed artifact was written. They MUST emit structured proposals for a deterministic mechanism to validate and apply.

Every state-change proposal MUST include:

- the operation and state section;
- the target record identifier when one exists;
- the expected project revision;
- the proposed patch;
- concise rationale; and
- explicit dependencies relevant to later invalidation.

Every artifact-change proposal MUST identify the artifact, repository-relative path, operation, expected fingerprint when updating, proposed content reference, and rationale.

The deterministic layer MUST validate schema, revision, references, write boundaries, atomic snapshot/history behaviour, and read-back success before persistence is claimed. Designing that executable layer is outside this workstream.

## Interaction with routing and gates

The router selects the smallest coherent eligible intervention from current state. Skills expose invocation conditions and preconditions; they do not own orchestration.

The gate-evaluation skill applies `GATES.md` and produces an evaluation proposal. Other skills MAY produce material that a gate later inspects, but MUST NOT claim a gate outcome unless they are `evaluate-gate`.

When a skill exposes a new deficiency, uncertainty, decision, assumption, or evidence item, it MUST propose the corresponding typed state record and dependencies. The workflow then reruns routing or the affected evaluation as required.

## Cross-cutting behaviours that are not standalone skills

The following remain cross-cutting obligations inherited from `AGENT.md` and `WORKFLOW.md`:

- proportionate challenge during ordinary work;
- focused, phone-suitable human interaction;
- recommendation plus credible alternatives for consequential decisions;
- epistemic separation of evidence, inference, assumption, preference, and uncertainty;
- preservation of valid prior work;
- tool and write-boundary discipline; and
- honest reporting of execution and persistence.

`focused-challenge` supplements rather than replaces continuous challenge. Reframing composes the affected reasoning skills. Orientation, checkpointing, deferral, stopping, reopening, finalization, and state persistence are workflow or state operations, not standalone generative skills.

## Research guard

Only `research-blocking-evidence` may initiate external research as an ideation capability. It is eligible only under the blocking-evidence conditions in `WORKFLOW.md`. Other skills MUST surface evidence gaps as work items rather than researching them automatically.

## Definition of a complete skill file

A skill file is complete when its metadata validates, its independent capability and boundaries are clear, invocation and exclusion conditions are discriminating, inputs and outputs are sufficient for routing, escalation protects human authority, proposed effects respect deterministic mutation boundaries, and its completion criteria can be tested without assuming a gate or workflow outcome.

## Completion criteria for the skills workstream

The skills workstream is complete when:

1. this shared contract defines responsibility, invocation, autonomy, inputs, outputs, escalation, mutation boundaries, and invocation completion;
2. `INDEX.md` registers all twelve accepted skills with selection cues and declarative dependencies;
3. every registered skill is independently invocable and conforms to the shared contract;
4. skill metadata and the common result envelope have deterministic schemas and validate;
5. blocked-only research and propose-only generative state effects are protected;
6. dynamic routing, interruption recovery, selective invalidation, reframing, deferral, stopping, and approved handoff are supported without lifecycle-specific skill duplication;
7. no skill duplicates or contradicts authority owned by the agent, workflow, gates, vision contract, or state model; and
8. no unresolved material design decision remains that later tooling would otherwise need to invent.
