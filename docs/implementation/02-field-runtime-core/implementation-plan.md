# Stage 3 Implementation Plan: Field Runtime Core

Status: Phase 1 pre-submit blocker gate passed; PR creation pending
Roadmap slug: `field-runtime-core`
Master plan: `docs/implementation/02-field-runtime-core/master-plan.md`
Current phase: Phase 1 active
Current blocker: none

## Startup Preflight

- Preflight date: 2026-05-08
- Foreground checkout: `/home/samcantrill/work/rphys`
- Current branch: `main`
- Upstream branch: `origin/main`
- Git remote:
  - Fetch: `git@github.com:samcantrill/rphys.git`
  - Push: `git@github.com:samcantrill/rphys.git`
- Worktree root:
  - `/home/samcantrill/work/rphys-worktrees`
  - Exists: yes
  - Writable: yes
- Master-plan status:
  - Accepted.
  - Quality gate passed on 2026-05-08.
- Roadmap status:
  - `Field runtime core` moves to `implementing` now that Phase 1 branch/worktree setup has begun.
- Git status at preflight:
  - Dirty worktree with planning/workflow document changes already in progress.
  - No implementation phase branch or worktree has been created.
  - Pre-existing/unrelated untracked `docs/implementation/03-dataset-io-index-core/master-plan.md` is outside this work package and must not be modified by this package.
- GitHub authentication:
  - Sandboxed `gh auth status` reported an invalid token.
  - Escalated `gh auth status` passed for account `samcantrill`.
  - Token scopes reported by GitHub CLI: `admin:public_key`, `gist`, `read:org`, `repo`.
  - Git operations protocol reported by GitHub CLI: `ssh`.
  - Maintainer loaded `~/.ssh/id_ed25519` into temporary agent socket `/tmp/ssh-d7VZAWyTrTNv/agent.2475198`.
- Remote verification:
  - `gh repo view --json nameWithOwner,defaultBranchRef` passed and confirmed `samcantrill/rphys`, default branch `main`.
  - `git ls-remote --heads origin main` failed for SSH remote `git@github.com:samcantrill/rphys.git`.
  - Failure: `ssh_askpass: exec(/usr/bin/ssh-askpass): No such file or directory`; `git@github.com: Permission denied (publickey)`.
  - `gh auth setup-git` was run successfully, but SSH remote verification still failed with the same public-key error.
  - `SSH_AUTH_SOCK` is not set in this Codex process.
  - `ssh-add -l` failed with `Could not open a connection to your authentication agent.`
  - `ssh -o BatchMode=yes -T git@github.com` failed with `Permission denied (publickey)`.
  - After maintainer loaded the key into `/tmp/ssh-d7VZAWyTrTNv/agent.2475198`, escalated remote checks with that `SSH_AUTH_SOCK` passed:
    - `ssh -o BatchMode=yes -T git@github.com` authenticated as `samcantrill`.
    - `git ls-remote --heads origin main` returned `83b9e4c6c9638f5bff86b3bbf904e7353da7fa22 refs/heads/main`.
    - `git fetch --dry-run origin main` succeeded.
    - `git push --dry-run origin main:refs/heads/agent/field-runtime-core-preflight-auth-check` succeeded without writing a branch.
  - Current remote blocker: none.
- Phase 1 branch-start decision:
  - Local `main` is `5a45c7c754cae74466273abfd32e9d91fc44046e`.
  - Local `origin/main` is `83b9e4c6c9638f5bff86b3bbf904e7353da7fa22`.
  - `main` is ahead of `origin/main` by two local workflow/closeout commits.
  - The Phase 1 worktree was created from `origin/main` instead of local `main` so the Phase 1 PR does not include unrelated prior commits.
  - This is a documented Stage 3 setup deviation from "current main"; the branch still targets `main` and starts from the current remote base.

## Stage 3 Operating Rules

- Use one live implementation plan: this file.
- Implement one phase at a time.
- Start phase `n + 1` only after phase `n` is merged and the branch/worktree cleanup is complete.
- Use the standard comprehensive pathway for every phase under the accepted master plan.
- Use xhigh reasoning for Phase 1 where manager, planning, coding, or review settings are configurable.
- Maintainer standing approval is recorded for standard Stage 3 implementation subagents required by this workflow, including code review and scientific/workflow review agents. Do not pause only to re-ask for those routine standard-path review approvals.
- Human review is not a default merge gate.
- PRs target `main`.
- PR creation must use explicit base/head/title flags.
- Automatic squash merge is used after validation and pathway gates pass, when GitHub permits it.
- Stop for authentication, branch protection without available authority, repeated unresolved blockers, failing validation that cannot be fixed, conflicts, or a required change to accepted design decisions.

## Phase Ledger

| Phase | Slug | Status | Branch | Worktree | Pathway | Ownership | Required outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `keys-fields-and-docs` | implemented and validated; reviews pending | `agent/field-runtime-core-p1-keys-fields-and-docs` | `../rphys-worktrees/field-runtime-core-p1-keys-fields-and-docs` | standard, xhigh where configurable | `src/rphys/data/keys.py`, `src/rphys/data/fields.py`, `src/rphys/data/collation.py` for `CollatePolicy` only, `src/rphys/data/__init__.py`, runtime docs, key/field tests | `DataKey`, minimal `FieldSpec`, narrow `FieldValue`, `CollatePolicy.LIST`, initial docs, and public exports land. |
| 2 | `sample-batch-containers` | pending | `agent/field-runtime-core-p2-sample-batch-containers` | `../rphys-worktrees/field-runtime-core-p2-sample-batch-containers` | standard | `src/rphys/data/samples.py`, relevant exports, sample/batch tests | Mutable `Sample` and `Batch` field APIs land. |
| 3 | `objects-contracts-and-collation` | pending | `agent/field-runtime-core-p3-objects-contracts-and-collation` | `../rphys-worktrees/field-runtime-core-p3-objects-contracts-and-collation` | standard | `src/rphys/data/objects.py`, `src/rphys/data/contracts.py`, `src/rphys/data/collation.py` after Phase 1 merge, relevant tests | Backend-agnostic data object hooks, sample contracts, and explicit collation land. |
| 4 | `contract-validation-closeout` | pending | `agent/field-runtime-core-p4-contract-validation-closeout` | `../rphys-worktrees/field-runtime-core-p4-contract-validation-closeout` | standard | public import tests, dependency-boundary tests, public-contract docs, implementation ledger | Full validation, docs alignment, and boundary checks are reconciled. |

## Phase 1 Plan

- Status: pre-submit blocker gate passed; PR creation pending.
- Pathway decision:
  - Standard pathway.
  - Reason: Phase 1 introduces public runtime contracts, public imports, docs, dependency-boundary tests, and stability-label obligations.
  - xhigh reasoning should be used where configurable because this phase establishes foundational public contracts.
- Branch/worktree creation:
  - Branch created: `agent/field-runtime-core-p1-keys-fields-and-docs`.
  - Worktree created: `/home/samcantrill/work/rphys-worktrees/field-runtime-core-p1-keys-fields-and-docs`.
  - Branch start point: `origin/main` at `83b9e4c6c9638f5bff86b3bbf904e7353da7fa22`.
  - Reason for `origin/main` start point: local `main` is ahead by two prior workflow/closeout commits that should not be pulled into the Phase 1 PR by default.
  - Remote behavior has been verified with temporary SSH agent socket `/tmp/ssh-d7VZAWyTrTNv/agent.2475198`.
  - The accepted Phase 1 planning artifacts were copied into the phase worktree before code implementation began.
- Commit:
  - Phase implementation commit: `1d57d93` (`Add field runtime keys and values`).
  - Ledger status commit: `1a402ba` (`Record Phase 1 commit status`).
- Implementation summary:
  - Added `src/rphys/data/keys.py` with validated `DataKey(str)`, reserved namespace constants, custom-key validation, and value-based key semantics.
  - Added `src/rphys/data/fields.py` with minimal `FieldSpec` and identity-equality `FieldValue`.
  - Added `src/rphys/data/collation.py` with only `CollatePolicy.LIST`.
  - Updated `src/rphys/data/__init__.py` to export only Phase 1 runtime contracts.
  - Added `docs/data/runtime-core.md` and aligned public architecture docs with the now-code-backed `rphys.data` surface.
  - Added key/spec/value tests and updated import/docs tests for the Phase 1 public API and deferred future contracts.
- Validation evidence:
  - Initial `uv run pytest ...` failed before tests because the default uv cache path under `/home/samcantrill/.cache/uv` was read-only in the sandbox.
  - Reran with `UV_CACHE_DIR=/tmp/rphys-uv-cache`.
  - First environment population required network; sandboxed run failed on DNS while downloading `pygments`, then the escalated run populated the environment.
  - First targeted test run then found one local test assertion issue: package submodules appear as attributes after import, so the public export check now asserts `rphys.data.__all__`.
  - `UV_CACHE_DIR=/tmp/rphys-uv-cache uv run pytest tests/test_data_keys.py tests/test_field_specs_values.py tests/test_public_imports.py tests/test_dependency_boundaries.py` passed: 51 passed.
  - `UV_CACHE_DIR=/tmp/rphys-uv-cache uv run pytest tests/test_public_contract_docs.py` passed: 8 passed.
  - `UV_CACHE_DIR=/tmp/rphys-uv-cache uv lock --check` passed.
  - `git diff --check` passed.
  - `UV_CACHE_DIR=/tmp/rphys-uv-cache uv run pytest` passed: 62 passed.
  - After review follow-ups, `UV_CACHE_DIR=/tmp/rphys-uv-cache uv run pytest tests/test_field_specs_values.py tests/test_public_contract_docs.py` passed: 26 passed.
  - After staging all Phase 1 files, `git diff --cached --check` and `git diff --check` passed.
  - After review follow-ups, `UV_CACHE_DIR=/tmp/rphys-uv-cache uv run pytest tests/test_data_keys.py tests/test_field_specs_values.py tests/test_public_imports.py tests/test_dependency_boundaries.py tests/test_public_contract_docs.py` passed: 59 passed.
  - After review follow-ups, `UV_CACHE_DIR=/tmp/rphys-uv-cache uv run pytest` passed: 62 passed.
- Review summaries:
  - Code review completed. Findings: the branch had no committed diff because Phase 1 files were untracked, and `CollatePolicy.LIST` copy/deep-copy behavior lacked direct tests. Resolution: all Phase 1 files were staged, staged whitespace was checked, and `CollatePolicy.LIST` copy, deep-copy, equality, hash, and value construction assertions were added.
  - Scientific/workflow review completed. Findings: runtime docs overclaimed schema-token validation, and `CollatePolicy.LIST` copy/equality/hash behavior was under-tested. Resolution: runtime docs now describe the actual permissive schema rule, and the enum behavior tests were added.
- Pre-submit blocker gate:
  - Status: passed.
  - Diff scope: accepted Phase 1 files only: `src/rphys/data/keys.py`, `src/rphys/data/fields.py`, `src/rphys/data/collation.py`, `src/rphys/data/__init__.py`, runtime docs, public contract docs, roadmap/implementation ledger updates, and focused key/field/import/dependency/doc tests.
  - Future-phase exclusions verified: no `Sample`, `Batch`, `DataObjectBase`, `CollateContext`, `collate_samples`, IO refs, modality classes, or policies beyond `LIST`.
  - Review blockers: none unresolved after manager follow-up fixes.
  - Validation evidence: required targeted tests, public contract docs test, lock check, committed-diff whitespace check, and full suite passed after follow-up fixes.
  - Public PR summary is ready: Phase 1 adds validated field keys, minimal field specs, loaded field values, explicit `LIST` policy, runtime docs, and focused public-contract tests.
  - Residual risks: schema identifiers remain intentionally permissive strings after narrow non-string/blank/padded checks; richer schema grammar and scientific metadata are deferred to specialized specs, data objects, sample contracts, or later plans.
- Current local risks:
  - PR creation, target verification, remote checks, merge, and cleanup remain.
- Scope:
  - `DataKey`, reserved namespaces, custom key rule.
  - Minimal `FieldSpec`.
  - Narrow `FieldValue`.
  - `CollatePolicy` with only `LIST`.
  - Initial runtime docs and public exports.
- Out of scope:
  - `Sample`, `Batch`, `DataObjectBase`, `CollateContext`, `collate_samples`, IO refs, modality classes, and policies beyond `LIST`.
- Acceptance criteria:
  - Keys validate deterministically.
  - Field specs and values record only accepted narrow fields without hidden IO behavior or data-specific integration metadata.
  - `DataKey`, `FieldSpec`, `FieldValue`, and `CollatePolicy.LIST` have documented equality, hashability, copy/deep-copy, and serialization boundaries.
  - Public docs describe runtime/IO boundary and field metadata contract.
  - Public docs assign stability labels to each Phase 1 public API.
- Required validation:
  - `uv run pytest tests/test_data_keys.py tests/test_field_specs_values.py tests/test_public_imports.py tests/test_dependency_boundaries.py`
  - `uv lock --check`
  - `git diff --check`
  - `uv run pytest` before merge unless unavailable or unrelated failures are documented.
- Review gates:
  - Standard-path automated code review.
  - Standard-path automated scientific/workflow review.
  - Pre-submit blocker gate before PR creation.
- PR plan:
  - Base: `main`
  - Head: `agent/field-runtime-core-p1-keys-fields-and-docs`
  - Title: `Field runtime core - Phase 1: Keys, fields, and runtime docs`
  - Verify opened PR with `gh pr view <PR> --json baseRefName,headRefName,state,url,reviewDecision,statusCheckRollup`.

## Phase 2 Plan

- Status: pending Phase 1 merge and cleanup.
- Pathway decision: standard pathway.
- Scope:
  - `Sample`, `Batch`, field lookup/mutation, `require`, `shallow_copy`, `deep_copy`, metadata behavior, public exports, tests.
- Required validation:
  - `uv run pytest tests/test_samples_batches.py tests/test_data_keys.py tests/test_field_specs_values.py`
  - `git diff --check`
  - Full suite before merge unless unavailable or unrelated failures are documented.

## Phase 3 Plan

- Status: pending Phase 2 merge and cleanup.
- Pathway decision: standard pathway.
- Scope:
  - `DataObjectBase`, `SampleContract`, `CollateContext`, `collate_samples`, explicit list collation, deterministic metadata collation, and tests.
- Sequential handoff:
  - `src/rphys/data/collation.py` is intentionally reopened in Phase 3 after Phase 1 has merged and cleanup is complete.
  - Phase 3 must define concrete `CollateContext` fields before tests assert value-preserving copy/deep-copy behavior.
- Required validation:
  - `uv run pytest tests/test_data_objects.py tests/test_sample_contracts.py tests/test_collation.py tests/test_samples_batches.py`
  - `git diff --check`
  - Full suite before merge unless unavailable or unrelated failures are documented.

## Phase 4 Plan

- Status: pending Phase 3 merge and cleanup.
- Pathway decision: standard pathway.
- Scope:
  - Public import tests, dependency-boundary tests, public-contract docs, implementation ledger, and full-suite validation evidence.
- Required validation:
  - `uv run pytest tests/test_public_imports.py tests/test_dependency_boundaries.py tests/test_public_contract_docs.py tests/test_error_hierarchy.py`
  - `uv lock --check`
  - `uv run pytest`
  - `git diff --check`

## Budget Ledger

| Gate | Budget | Current use |
| --- | --- | --- |
| Startup preflight | manager-owned | Used once; passed after temporary SSH agent setup. |
| Phase planning | one manager/planner pass per phase | Manager setup pass used to create and document the Phase 1 branch/worktree; no implementation-planner pass started. |
| Phase coding | one coding-worker pass per phase | Manager-local implementation completed; coding-worker subagent pass not started. |
| Pre-submit blocker gate | one manager/PR-manager pass per phase | Completed for Phase 1; passed with no unresolved local blocker. |
| Standard code review | one code review per phase | Completed for Phase 1; follow-ups fixed by manager. |
| Standard scientific/workflow review | one science review per phase | Completed for Phase 1; follow-ups fixed by manager. |
| Blocker fixing | two cycles for same concrete blocker | No blocker-fixer subagent used; manager applied review follow-up fixes. |
| PR manager | one PR-manager pass plus remote-only blocker handling | Not started. |

## Blocker Log

### B1 - SSH Remote Authentication Unavailable To Codex Process

- Status: resolved for this session with temporary SSH agent socket.
- Detected: 2026-05-08 startup preflight.
- Evidence:
  - Sandboxed `gh auth status` failed, but escalated `gh auth status` passed for `samcantrill`.
  - `gh repo view --json nameWithOwner,defaultBranchRef` passed for `samcantrill/rphys`, default branch `main`.
  - `git ls-remote --heads origin main` failed before and after `gh auth setup-git`.
  - Failure text: `ssh_askpass: exec(/usr/bin/ssh-askpass): No such file or directory`; `git@github.com: Permission denied (publickey)`.
  - `SSH_AUTH_SOCK` is absent, `ssh-add -l` cannot contact an agent, and `ssh -o BatchMode=yes -T git@github.com` fails.
- Impact before resolution:
  - Could not verify remote behavior, push phase branch, open PR, inspect PR target/checks, merge, or clean remote branches.
  - Phase 1 branch/worktree creation was intentionally deferred until remote access was verified.
- Required maintainer decision:
  - None while `/tmp/ssh-d7VZAWyTrTNv/agent.2475198` remains available and loaded.
  - If the socket expires or Codex restarts without `SSH_AUTH_SOCK`, reload the key into an agent and record the new socket.
- Resume criteria:
  - Met on 2026-05-08.
  - `git ls-remote --heads origin main`, `git fetch --dry-run origin main`, and `git push --dry-run origin main:refs/heads/agent/field-runtime-core-preflight-auth-check` passed through the temporary agent socket.
