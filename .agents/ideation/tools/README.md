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
- `ideation-tools reconcile` — determine an indeterminate transaction outcome from authoritative Git metadata and committed bytes;
- `ideation-tools request-approval`, `attach-approval`, `add-approver` and `verify-approvals` — the human approval commands described under [Human authorization](#human-authorization).

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

Direct persistence of a settled human decision, a reconfirmation, or an iteration reopening requires an action-specific authorization bound to:

- project and iteration;
- transaction ID; and
- the canonical hash of the exact authorized mutation (`auth.mutation_action_material`; rationale and summary are excluded).

Authorizations are single-use across distinct transactions. Deterministic consequences may rely on a previously persisted trusted human decision; they do not require the user to repeat the same approval. For example, approved finalization relies on a current Gate 6 evaluation that points to a settled human decision carrying trusted authorization provenance.

### Vision approval binding

The Gate 6 approval decision carries a `vision_fingerprint` field (`hashing.vision_content_fingerprint`: SHA-256 of `vision.md` with the header `status:` value blanked). Because it is part of the decision's patch, it is covered by the passkey signature. `INV-004` rejects any state in which Gate 6 is currently passing but no referenced approval decision has the current vision's fingerprint. The coordinator enforces this on every transaction, and `verify-approvals` enforces it on the committed files, so a `vision.md` edited outside the tools also fails CI. To revise an approved vision, invalidate Gate 6 in the same transaction and request a new approval.

### Trusted authorization provenance: passkey signatures

An authorization is trusted only when the human has signed its action hash with a registered passkey. The agent can prepare a request but cannot produce the signature.

| Piece | Location | Role |
|---|---|---|
| Approval page | `../approval-page/`, published by `.github/workflows/approval-page.yml` | Recomputes the action hash from the request, shows the signed fields separately from the agent's unsigned explanation, and signs the hash as the WebAuthn challenge after Face ID, fingerprint or device PIN. |
| Approvers | `../approvers.json` | WebAuthn `rp_id`, origin, page URL, and each approver's ES256 public key and fingerprint. |
| Signature check | `ideation_tools/passkey.py` | Registered credential, `webauthn.get`, challenge equals action hash, origin, `rpIdHash`, user-present and user-verified flags, and the ECDSA signature. The signature counter is not checked because synced passkeys report 0. |
| Verifier | `PasskeyApprovalVerifier` (`trust_mode: "passkey"`) | Verifies every authorization in the execution context and takes the approver's name from the verified key. It is the only verifier the CLI uses. |
| Evidence | `projects/<slug>/ideation/approvals/<authorization_id>.json` | Written in the same atomic commit as the change it authorizes. It holds the signed action, its hash, the approver, and the assertion, so anyone can re-verify it. |
| CI re-verification | `ideation-tools verify-approvals`, run by `.github/workflows/approvals-check.yml` | On every pull request and push to `main`, runs `main`'s checker against `main`'s `approvers.json`, reading the pull request's files as data only. |

`LocalHarnessVerifier` (`trust_mode: "local_harness"`) trusts whoever supplies the context. It remains only for tests; the CLI refuses it.

`authorization_id` may contain only letters, digits, `-` and `_`, because it names the evidence file.

### Approval flow

Every settled human decision, reconfirmation and iteration reopening follows this flow:

1. The agent builds the transaction, giving each mutation that needs approval an `authorization_id`, and runs:

   ```bash
   ideation-tools request-approval --transaction transaction.json
   ```

   Each request includes a `link` to the approval page. The page URL comes from `approvers.json`; `--page-url` overrides it.
2. The human opens the link, checks the signed fields, approves with Face ID or fingerprint, and pastes the approval code back.
3. The agent verifies the code and adds it to a `trust_mode: "passkey"` execution context:

   ```bash
   ideation-tools attach-approval --transaction transaction.json \
     --context execution-context.json --approval <code>
   ```

   On success this prints `Valid approval from <name> (<fingerprint>) for <authorization_id>`. On failure it exits with code 2 and leaves the context unchanged.
4. The agent applies the transaction with `ideation-tools apply`.

Every settled human decision requires this flow, including decisions made early in ideation. Batching several approvals into one signature is a planned follow-up, if the field test shows the flow is too frequent.

### Operator runbook

**Approve a change.** Open the link the agent gives you. Read the green "What you are approving" box, which is what your signature covers; the grey box is the agent's unsigned explanation. Approve only if the green box matches what you agreed. If the page shows a red error, do not approve.

**Approve the vision (Gate 6).** Read `vision.md` at the commit the agent links to, not a copy in chat. The green box shows a `vision_fingerprint`; your signature binds that exact text. The page does not yet show the vision itself (planned), so you rely on the agent's commit link for what you read. CI will reject any later change to the text you approved.

**Register a phone.** On the approval page, expand "Register this phone as an approver", enter your name, and confirm. Write down the fingerprint, stay on the page, copy the code, and give it to the agent. The agent runs:

```bash
ideation-tools add-approver --record <code>
```

and opens a pull request that changes only `approvers.json`. Merge it only if the pull request shows the fingerprint your phone displayed. A new key cannot be used in the same pull request that adds it, because CI trusts only `main`'s approvers.

**If you leave the registration screen before copying the code**, delete the new passkey for `ras207.github.io` from your phone's password manager and register again.

**Lose or replace a phone.** Register the replacement first. Re-verification checks all committed evidence against the current `approvers.json`, so removing a key makes CI fail for every approval that key signed. Until retired keys are supported, remove a lost phone's key only if no committed approval depends on it; otherwise keep it listed and rely on its Face ID, fingerprint or PIN protection. Re-approving the affected decisions does not help, because their history still references the old evidence.

**Repository settings that the protection depends on.** The `main` ruleset must require the `pytest` and `verify-approvals` checks and must have an empty bypass list. GitHub Pages must use GitHub Actions as its source.

### Limits and follow-ups

- Pull requests that change `tools/`, `approval-page/`, `approvers.json` or `.github/` change what is trusted. CI cannot judge them, so review them yourself. A CODEOWNERS rule to flag them is planned.
- Anyone who controls the approver's GitHub, Apple or Google account can act as the approver.
- The passkey belongs to the whole `ras207.github.io` domain, so any GitHub Pages site under that account can request it.
- Planned: retired keys, which stay valid for approvals committed to `main` before retirement but cannot sign new ones.
- Planned: show the candidate vision on the approval page and check its `vision_fingerprint` there, so the text read is guaranteed to be the text signed.
- Planned: bundle `schemas/` into the package so a non-editable install works; warn on the page before leaving an uncopied code; a `remove-approver` command; batch approvals.

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
- `schemas/approvers.schema.json`

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

### Install

Install into a virtual environment, from this directory:

```bash
python -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
```

Then run `.venv/bin/ideation-tools` and `.venv/bin/python -m pytest`, or activate the environment with `source .venv/bin/activate`. Omit `[test]` if you will not run the tests.

- Use a virtual environment. Installing into the system Python can fail: on Debian-based images pip cannot upgrade the system `cryptography` package to the required version.
- Keep `-e` (editable). The JSON schemas under `schemas/` are not yet packaged, so a non-editable install fails at the first command with `FileNotFoundError: .../schemas/...`.

### Test

```bash
.venv/bin/python -m pytest
```

The CLI uses `../approvers.json` by default; each command accepts `--approvers` to use another file. Execution contexts must use `trust_mode: "passkey"`.

Apply a normalized transaction:

```bash
ideation-tools apply \
  --repo /path/to/repo \
  --transaction transaction.json \
  --context execution-context.json
```

After an applied transaction, re-sync the checked-out files. The tools advance the branch without touching the working tree, so if the authorized branch is checked out, `state.yaml` and artifacts on disk still show the previous revision and Git lists them as changed:

```bash
git restore --source=HEAD --staged --worktree projects/<project-slug>/ideation
```

Until you do, read state with `git show HEAD:projects/<project-slug>/ideation/state.yaml`, not from disk. Never commit those files with Git directly: a commit of the stale copy would silently revert the transaction.

Validate and stage without mutation:

```bash
ideation-tools apply \
  --repo /path/to/repo \
  --transaction transaction.json \
  --context execution-context.json \
  --dry-run
```

Re-verify every committed human approval, as CI does:

```bash
ideation-tools verify-approvals --root /path/to/repo
```

It prints `ok` or `FAIL` for each project and exits with code 1 if any problem is found.

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
13. the execution-context verifier interface exists, and the CLI accepts only passkey-signed human authorizations whose evidence CI re-verifies;
14. automated tests cover success and deliberate failure injection across validation, concurrency conflicts, commit failure, verification interruption, reconciliation, authorization failures and invariant violations;
15. the implementation remains consistent with `AGENT.md`, `WORKFLOW.md`, `GATES.md`, `ideation_state.md` and the skills contracts; and
16. no material tooling decision remains that a future harness would otherwise need to invent.
