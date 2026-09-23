# Vision Contract

This file defines the required structure and quality standard for vision artifacts produced by the ideation agent. It is part of the ideation system definition, not a generated project artifact.

During a normal ideation run, this file is read-only. Generated visions must be written to `projects/<project-slug>/ideation/vision.md`.

A generated vision should begin with:

```yaml
status: draft
version: 0.1
```

## 1. Vision statement

A concise description of the future state this idea is intended to create.

It should communicate:
- what is being created or changed;
- for whom;
- and the important outcome it enables.

The statement should describe the intent rather than the implementation.

### Completion standard

A reader unfamiliar with the ideation process should be able to understand the essence of the idea without reading the rest of the document.

---

## 2. Problem or opportunity

Describe the underlying problem, unmet need or opportunity that justifies pursuing the idea.

Explain:
- what happens today;
- why the current situation is inadequate;
- who experiences the problem or opportunity;
- and why it is worth addressing.

Do not define the problem purely in terms of the proposed solution.

### Completion standard

The problem should be sufficiently clear that alternative solutions could plausibly be proposed for it.

---

## 3. People and stakeholders

Identify the people, organisations or systems whose needs, interests or constraints materially shape the vision.

Use the following categories where relevant:

### Primary users

The people who will directly interact with the eventual product, service or system.

### Other beneficiaries

People or groups who receive meaningful value from the outcome without necessarily interacting with the system directly.

### Critical stakeholders

People, organisations or functions whose constraints, approval, trust or participation materially affect whether the vision can succeed.

Not every idea requires all three categories.

### Completion standard

It should be clear whose needs should take priority when later design trade-offs arise and which stakeholders materially constrain the solution space.

---

## 4. Desired change

Describe what should become meaningfully different if the vision succeeds.

Focus on changes in outcomes, capabilities, behaviour or experience rather than product features.

### Completion standard

There should be a clear contrast between the current state and the desired future state.

---

## 5. Chosen direction and rationale

Describe the broad direction selected during ideation and why it is preferred.

Capture the essential concept without specifying detailed product functionality.

Where materially different directions were considered, briefly explain why the chosen direction is preferable. Include consequential behavioural boundaries where they materially define what the system should or should not do.

### Completion standard

The direction should be specific enough to constrain downstream design while leaving meaningful solution-design freedom.

---

## 6. Guiding principles

Record the small number of principles that should govern future design decisions.

Each principle should represent a meaningful preference or constraint rather than a generic statement of quality.

### Completion standard

The principles should be useful for resolving future trade-offs.

---

## 7. Boundaries and non-goals

State what the vision deliberately does not attempt to solve.

Capture important scope boundaries, excluded users, excluded outcomes or intentionally deferred ambitions where these prevent likely misunderstanding.

### Completion standard

A downstream team should be able to recognise significant proposals that fall outside the intended vision.

---

## 8. Critical assumptions

State the assumptions on which the viability or desirability of the vision materially depends.

For each assumption, make clear what is currently believed but not yet established.

Do not include trivial or low-consequence assumptions.

### Completion standard

The major things that would undermine the vision if proven false should be visible.

---

## 9. Success looks like

Describe the observable conditions that would indicate the vision has achieved its intended purpose.

Where relevant, distinguish between:
- **Outcome success:** the meaningful change experienced by users or beneficiaries; and
- **Essential capability success:** the core capability the product, service or system must reliably provide for that outcome to be possible.

These need not yet be formal product metrics or targets. Avoid treating implementation outputs such as features shipped or screens built as success in themselves.

### Completion standard

It should be possible to imagine observing the future state and judging whether the vision has broadly succeeded and whether its essential capability exists.

---

## 10. Unresolved questions

Record material questions that remain open at the end of ideation.

Classify each as either:

**Non-blocking:** can appropriately be resolved during product design, research or implementation.

**Blocking:** prevents the vision from being considered complete.

An approved vision must contain no blocking unresolved questions.

---

# Artifact completion contract

A generated `vision.md` may move from `draft` to `candidate` when every required section contains substantive content and the resulting vision satisfies the following quality conditions:

| Test | Required condition |
|---|---|
| Problem clarity | The underlying problem or opportunity is understandable independently of the proposed solution. |
| User clarity | The primary users or beneficiaries and their relevant priorities are identifiable. |
| Outcome clarity | The desired change is explicit. |
| Direction clarity | A coherent broad direction has been chosen. |
| Assumptions | Critical assumptions are visible. |
| Boundaries | Important non-goals and scope boundaries are explicit. |
| Success | The intended outcome and, where relevant, essential capability are recognisable. |
| Coherence | The sections do not materially contradict one another. |
| Uncertainty | Remaining uncertainty is explicit and no blocking question remains unresolved. |

Process-assurance requirements such as whether alternatives were adequately explored, assumptions were sufficiently challenged, and the required human gates were passed are defined separately in `../workflow/GATES.md`.

A generated `vision.md` may move from `candidate` to `approved` only through explicit human approval.

The human approves one exact text. Its identity is the vision fingerprint: the SHA-256 of `vision.md` with the value of the first header `status:` line blanked, where the header is every line before the first Markdown heading. Changing `status: candidate` to `status: approved` therefore keeps the fingerprint; any other change, including whitespace or line endings, does not. After approval, only the status value may change. Any other edit produces a new candidate that needs a new approval. The fingerprint is computed by `vision_content_fingerprint` in `../tools/ideation_tools/hashing.py`.

The ideation agent must not approve its own vision.

# Scope boundary

A completed `vision.md` defines **what should exist, why it should exist, whom it should serve and what successful change looks like**.

It should not normally define:
- detailed features or requirements;
- interface layouts;
- user journeys;
- technical architecture;
- data models;
- APIs;
- implementation plans;
- engineering choices;
- delivery milestones.

Those belong to downstream product-design and implementation workflows.

# Definition of done

The vision artifact is complete when:

> A coherent vision clearly defines the problem, relevant people and stakeholders, desired change, chosen direction, governing principles, boundaries, critical assumptions and meaning of success; no unresolved question prevents commitment to that direction; and the human has explicitly approved the vision.

At that point:

```yaml
status: approved
```

and the document becomes the authoritative handoff from ideation to product design.
