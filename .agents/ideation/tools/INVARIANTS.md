# Deterministic invariant registry

The registry below identifies machine-checkable policy enforced by the tools layer. Stable IDs are implemented in `ideation_tools/invariants.py`. The Markdown system contracts remain authoritative for the meaning behind each rule.

| ID | Invariant |
|---|---|
| `INV-001` | An approved handoff has no unresolved blocking work item. |
| `INV-002` | An approved handoff has no open human escalation. |
| `INV-003` | An approved handoff has current passing evaluations for all six required gates. |
| `INV-004` | A current passing Gate 6 evaluation is backed by a settled human approval decision with trusted authorization provenance whose `vision_fingerprint` matches the current `vision.md`. |
| `INV-005` | An approved workflow has `vision_status: approved` and the committed vision artifact declares `status: approved`. |
| `INV-006` | A `not_progressing` terminal state does not expose an approved vision handoff. |
| `INV-007` | A terminal workflow status has a matching `finalization.outcome`. |
| `INV-008` | `not_progressing` is backed by a settled human closure decision with trusted authorization provenance. |

"Trusted authorization provenance" in `INV-004` and `INV-008` means the decision's `authorization_id` is backed by passkey-signed approval evidence that `ideation-tools verify-approvals` accepts. The invariants check that the `authorization_id` exists; `verify-approvals` checks the evidence behind it, in CI and on demand. See "Human authorization" in `README.md`.

The coordinator also applies deterministic execution-policy checks that are not state invariants, including schema validity, project identity, protected-ref refusal, project write boundaries, expected state revision, artifact fingerprints, immutable content hashes, transaction idempotency, and exact human-authorization bindings.

Adding an invariant requires:

1. a stable ID and description here;
2. deterministic validator code;
3. tests demonstrating both acceptance and rejection; and
4. confirmation that the rule is grounded in an authoritative ideation-system contract rather than a new qualitative judgement invented by the tools layer.
