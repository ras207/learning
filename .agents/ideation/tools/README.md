# Ideation deterministic tools

## Purpose

This directory implements the deterministic execution layer for the reusable ideation agent. Generative skills and workflow logic propose substantive changes; this layer validates, stages, commits and verifies canonical mutations without making qualitative ideation judgements.

The coordinator is the sole write authority for canonical ideation state and project artifacts. Skills and the agent MUST NOT bypass it.

## Architecture

The baseline uses **one transaction coordinator plus narrow deterministic primitives**.

Project initialization:

- `ideation_tools.project_init.build_initialization_transaction` deterministically constructs the existing canonical revision-1 state for a minimal-seed project. It performs no qualitative interpretation of `PROJECT.md` and records the reusable agent Git fingerprint as provenance.
- The authoritative project-instance contract is `../contracts/project-instance.md`.
- v0.1 intentionally preserves `projects/<project-slug>/ideation/state.yaml` as the unified canonical state artifact for the first real field test.

Public execution surface:

- `ideation-tools apply` — execute one normalized transaction, or run the identical preflight/staging path with `--dry-run`;
- `ideation-tools reconcile` — determine an indeterminate transaction outcome from authoritative Git metadata and committed bytes.

Internal primitives are implemented in `ideation_tools/primitives.py`:

| Primitive | Responsibility |
|---|---|
| `validate_transaction` | Validate the normalized transaction schema. |
| `validate_state_snapshot` | Validate canonical state structure and identifiers. |
| `validate_policy_invariants` | Enforce machine-checkable workflow/state invariants. |
| `validate_write_boundary` | Prevent writes outside the current project's ideation directory. |
| `fingerprint_artifact` | Compute SHA-256 content fingerprints. |
| `stage_state_change` | Apply one typed domain mutation to a prospective state snapshot. |
| `stage_artifact_change` | Resolve immutable content-addressed payload bytes and verify their hash. |
| `commit_transaction` | Ask the selected persistence backend to create and atomically advance one transaction commit. |
| `verify_transaction` | Read back and verify committed bytes before success is reported. |

The coordinator composes these primitives through the required lifecycle:

`preflight -> stage -> commit -> verify`

A dry run executes `preflight -> stage` and stops before any ref advancement.

## Transaction boundary

Every canonical mutation passes through one normalized transaction proposal, regardless of whether its source is a skill result or a workflow operation.

One transaction represents exactly one originating source event. That event MAY contain multiple coupled state and artifact mutations that must succeed together. Multiple independent skill results or workflow events MUST NOT be batched into one transaction.

Normalization is deterministic and provenance-preserving. A normalized transaction records its source identity and content hash; normalization MUST NOT silently alter substantive proposals.

## Atomicity and optimistic concurrency

The baseline persistence backend is Git. One canonical transaction maps to one Git commit.

The local Git backend:

- operates independently of the developer working tree;
- reads from the expected base commit;
- uses a temporary Git index and plumbing commands to construct the prospective tree;
- creates a commit without checking out or staging user files; and
- advances only the trusted `authorized_ref` with `git update-ref <ref> <new> <expected-old>`.

The ref update is the atomic persistence boundary. If the expected ref SHA, state revision, or expected artifact fingerprint is stale, the entire transaction returns `conflict` and no canonical ref is advanced.

If the configured backend cannot provide equivalent atomic commit semantics, the transaction MUST be refused. A future backend MAY use compensating rollback only when restoration is itself deterministic and read-back verified.

## Branch authority

The coordinator never creates or chooses a branch. Trusted execution context supplies an already-authorized ref and expected head SHA.

The transaction proposal cannot authorize its own destination. The baseline coordinator also refuses protected refs `refs/heads/main` and `refs/heads/master`.

## Mutation model

State changes use typed domain operations rather than arbitrary YAML/JSON patch programs. Supported baseline operations are:

- `initialize`
- `create`
- `update`
- `resolve`
- `supersede`
- `invalidate`
- `reconfirm`
- `checkpoint`
- `finalize_approved`
- `finalize_not_progressing`
- `reopen_iteration`
- `migrate`

Callers propose substantive changes and rationale. The coordinator owns deterministic bookkeeping, including revision increments, timestamps, artifact fingerprints, transaction metadata, and the transaction history-event envelope.

## Immutable artifact payloads

Artifact proposals refer to immutable content using `sha256:<digest>` references. The trusted execution context identifies a content-addressed payload store. Preflight verifies that the resolved bytes match the declared digest; the exact validated bytes are then staged and committed.

An update also requires the expected fingerprint of the currently committed artifact. A mismatch causes `conflict`.

## Human authorization

A transaction cannot self-attest that a consequential human decision occurred.

Trusted execution context is validated separately from the transaction and is supplied by a pluggable verifier. The v0.1 `LocalHarnessVerifier` treats the local invoking harness as the trust boundary. Future remote backends can introduce signed authorization without changing transaction semantics.

Direct persistence of a settled human decision or reconfirmation requires an action-specific authorization bound to:

- project and iteration;
- transaction ID; and
- the canonical hash of the exact authorized mutation.

Authorizations are single-use across distinct transactions. Deterministic consequences may rely on a previously persisted trusted human decision; they do not require the user to repeat the same approval. For example, approved finalization relies on a current Gate 6 evaluation that points to a settled human decision carrying trusted authorization provenance.

## Deterministic invariant enforcement

Machine-checkable policy is enforced during staging through the stable invariant registry documented in `INVARIANTS.md` and implemented in `ideation_tools/invariants.py`.

The tools layer enforces explicit rules; it does not interpret qualitative vision quality, choose product direction, or replace human judgement. Semantic reasoning remains with the agent, skills, gates and contracts.

## Idempotency

Each normalized transaction has a stable `transaction_id` and canonical transaction-content hash.

- Replaying an already committed transaction with identical content returns the verified prior result without another mutation.
- Reusing the same transaction ID for different content is rejected.

Git commit metadata records transaction identity, transaction hash, expected base SHA, resulting state revision, and a hash manifest for every file changed by the transaction.

## Verification and reconciliation

Success is reported only after post-commit read-back verifies the ref and every changed file.

If the ref may have advanced but verification is interrupted or inconclusive, the result is `reconciliation_required`; success or failure is not guessed. Before later writes, the coordinator verifies transaction metadata and committed file hashes at the current ref. The explicit `reconcile` command can also recover the result from Git alone.

Git metadata and committed bytes are authoritative for reconciliation. Any local journal is optional diagnostics and MUST NOT be required for correctness.

## Result statuses

The coordinator returns exactly one of:

- `validated` — dry-run preflight/staging passed; nothing was committed;
- `applied` — commit and read-back verification succeeded, or an identical prior transaction was verified;
- `rejected` — schema, authorization, write-boundary, invariant, or other deterministic validation failed;
- `conflict` — expected state revision, artifact fingerprint, or ref head is stale;
- `reconciliation_required` — commit outcome cannot yet be conclusively verified;
- `failed` — execution failed before any canonical ref mutation and reconciliation is unnecessary.

## Schemas

The deterministic contract surface is:

- `schemas/ideation-state.schema.json`
- `schemas/transaction-proposal.schema.json`
- `schemas/execution-context.schema.json`
- `schemas/transaction-result.schema.json`

The Markdown system contracts remain authoritative for semantic meaning. Schemas enforce the portions that are deterministic.

## Schema evolution

State schema evolution permits only explicit, deterministic version-to-version migrations registered in `ideation_tools/migrations.py`. Best-effort interpretation is prohibited. Because v0.1 introduces schema version 1 and no historical machine schema exists, the baseline registry intentionally contains no historical migration; adding version 2 requires an explicit `1 -> 2` migration before older state may be upgraded.

A migration is itself an auditable source event and must use the same transaction coordinator for canonical persistence.

## Persistence backend interface

`ideation_tools/backends/base.py` defines the backend contract. v0.1 implements only `LocalGitBackend`.

A future GitHub API backend may implement the same interface, provided it preserves:

- trusted-ref authorization;
- expected-head optimistic concurrency;
- whole-transaction atomicity;
- immutable committed bytes;
- transaction metadata sufficient for idempotency and reconciliation; and
- deterministic read-back verification.

## Running

From this directory:

```bash
python -m pytest
```

Install locally if desired:

```bash
python -m pip install -e '.[test]'
```

Apply a normalized transaction:

```bash
ideation-tools apply \
  --repo /path/to/repo \
  --transaction transaction.json \
  --context execution-context.json
```

Validate and stage without mutation:

```bash
ideation-tools apply \
  --repo /path/to/repo \
  --transaction transaction.json \
  --context execution-context.json \
  --dry-run
```

## Completion criteria

The tools workstream is complete when:

1. the coordinator and internal primitive architecture are documented;
2. state, transaction proposal, execution context and transaction result schemas validate;
3. the Python package and coordinator CLI are implemented;
4. one-source-event transactions normalize deterministically with preserved provenance;
5. typed domain mutations, deterministic bookkeeping, invariant enforcement and action-bound human authorization work;
6. optimistic concurrency and trusted authorized-ref checks work;
7. dry-run uses the same preflight/staging path as real execution;
8. the local Git backend performs working-tree-independent atomic commits;
9. immutable artifact payloads and fingerprints are verified;
10. idempotent replay and conflicting transaction-ID reuse behave correctly;
11. post-commit uncertainty produces `reconciliation_required` and can be reconciled from Git metadata;
12. deterministic schema migration machinery exists and best-effort migration is prohibited;
13. the execution-context verifier interface exists with the trusted-local-harness baseline;
14. automated tests cover success and deliberate failure injection across validation, concurrency conflicts, commit failure, verification interruption, reconciliation, authorization failures and invariant violations;
15. the implementation remains consistent with `AGENT.md`, `WORKFLOW.md`, `GATES.md`, `ideation_state.md` and the skills contracts; and
16. no material tooling decision remains that a future harness would otherwise need to invent.
