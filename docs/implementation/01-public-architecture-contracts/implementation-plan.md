# Implementation Plan: Public Architecture Contracts

Status: local implementation complete; PR/merge workflow blocked
Roadmap item: `docs/roadmap/index.md`
Master plan: `docs/implementation/01-public-architecture-contracts/master-plan.md`
Roadmap slug: `public-architecture-contracts`
Plan number: `01`
Current phase: Phase 4 `contract-validation` completed locally
Blockers: GitHub CLI authentication is invalid for `samcantrill`; PR creation, automated PR review/merge gates, and branch cleanup require refreshed auth. Local implementation was completed in the foreground checkout because the repository already contained uncommitted workflow/planning-file moves.

## Operating Rules

- Implement phases strictly in master-plan order.
- Start phase `n + 1` only after phase `n` has merged and branch/worktree cleanup is complete.
- Human review is not a merge gate.
- Merge automatically when validation and selected pathway gates pass.
- If branch protection blocks solely on human review and available authority permits, approve, admin-merge, or otherwise force merge only after automated gates pass.
- Do not merge known failing validation, wrong-target PRs, unresolved conflicts, unresolved implementation/review blockers, or changes outside the accepted plan.
- Record pathway decisions, validation, review summaries, PR facts, merge results, blockers, and cleanup in this file.

## Phase Index

| Phase | Slug | Status | Branch | Worktree | Pathway | Merge State | Blockers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `contract-docs-and-policy` | completed locally | `agent/public-architecture-contracts-p1-contract-docs-and-policy` | `../rphys-worktrees/public-architecture-contracts-p1-contract-docs-and-policy` | fast | blocked, no PR | GitHub auth invalid; phase branch/worktree not created |
| 2 | `repository-tooling-scaffold` | completed locally | `agent/public-architecture-contracts-p2-repository-tooling-scaffold` | `../rphys-worktrees/public-architecture-contracts-p2-repository-tooling-scaffold` | standard | blocked, no PR | GitHub auth invalid; automated review/merge gates pending |
| 3 | `package-and-error-skeleton` | completed locally | `agent/public-architecture-contracts-p3-package-and-error-skeleton` | `../rphys-worktrees/public-architecture-contracts-p3-package-and-error-skeleton` | standard | blocked, no PR | GitHub auth invalid; automated review/merge gates pending |
| 4 | `contract-validation` | completed locally | `agent/public-architecture-contracts-p4-contract-validation` | `../rphys-worktrees/public-architecture-contracts-p4-contract-validation` | fast | blocked, no PR | GitHub auth invalid; phase branch/worktree not created |

## Shared Validation

- Run the narrowest phase-specific checks first.
- Run `git diff --check` for every phase.
- Run full `uv run pytest` once package tooling and tests exist.
- Record any unavailable command with the exact reason.
- Do not introduce raw datasets; no fixtures are needed for this package.

## Phase 1: Contract Docs And Policy

Status: completed locally; PR/merge blocked
Pathway: fast
Branch: `agent/public-architecture-contracts-p1-contract-docs-and-policy`
Worktree: `../rphys-worktrees/public-architecture-contracts-p1-contract-docs-and-policy`

### Scope

- Goal: land the public architecture contract before tooling or code hardens public behavior.
- Files/modules owned:
  - `docs/architecture/public-contracts.md`
  - `README.md` link only if useful.
  - `docs/roadmap/index.md` implementation note only if needed.
- Out of scope:
  - `pyproject.toml`, `.python-version`, `uv.lock`, `Makefile`, `CONTRIBUTING.md`, `LICENSE`.
  - `src/rphys/**`, `tests/**`, package imports, dependencies, registries, recipes, stages, or runtime behavior.
- Public interfaces allowed to change: documentation policy and ownership text only.
- Scientific/workflow contracts: docs must require later public scientific components to document units, shapes, dtypes, coordinate frames, sampling rates, temporal alignment, leakage risks, failure behavior, and validation tests.

### Plan

- Draft `docs/architecture/public-contracts.md`.
- Document first-wave stable homes and future/provisional modules.
- Document API labels, code-backed docs policy, strict `loom` boundary, `_target_` extension rule, limited registry policy, optional dependency categories, uv/Python policy, rights status, and scientific-contract obligations.
- Mention that `FieldRef`, `TemporalIndexSlice`, and `FieldView` are future `rphys.io` concepts.
- Add only necessary discoverability links.

### Pathway Decision

- Selected pathway: fast.
- Rationale: no code, package metadata, tests, public imports, dependencies, or scientific runtime behavior change.
- Criteria that force standard pathway: adding package code, tests, tooling metadata, dependency metadata, public import paths, or changing accepted module ownership/API labels/error naming/extension policy.

### Validation

| Command | Result | Evidence |
| --- | --- | --- |
| `git diff --check` | passed | No whitespace errors after local implementation. |
| Manual link review for touched docs | passed | `README.md` links to `docs/architecture/public-contracts.md`; touched docs paths resolve locally. |

### Review Or Checklist Summary

- Fast-path checklist:
  - Docs-only: passed for Phase 1 owned files.
  - No public import/API changes: passed for Phase 1.
  - No scientific runtime behavior: passed.
  - Accepted decisions preserved: passed.
- Unresolved blockers: GitHub auth invalid for PR creation/merge.

### PR And Merge

- PR: not opened; `gh auth status` reports invalid token for `samcantrill`.
- Base branch: `main`
- Head branch: `agent/public-architecture-contracts-p1-contract-docs-and-policy`
- Checks: local `git diff --check` passed.
- Merge command: not run.
- Merge result: blocked by GitHub auth and uncreated phase branch/worktree.
- Branch cleanup: not applicable; branch was not created.
- Worktree cleanup: not applicable; worktree was not created.

### Phase Notes

- Implementation summary: Added `docs/architecture/public-contracts.md` covering API labels, first-wave homes, deferred modules, future `rphys.io` concepts, errors, code-backed docs, scientific obligations, `loom` boundary, `_target_` extension policy, registry limits, optional dependency policy, uv/Python policy, and all-rights-reserved status. Added a README discoverability link.
- Commits: none; local uncommitted implementation.
- Assumptions and risks: Local implementation did not use isolated phase worktrees because the foreground checkout already contained uncommitted planning/workflow moves and GitHub auth was invalid.
- Follow-up: Refresh GitHub auth before PR creation or merge.

## Phase 2: Repository Tooling Scaffold

Status: completed locally; PR/merge blocked
Pathway: standard
Branch: `agent/public-architecture-contracts-p2-repository-tooling-scaffold`
Worktree: `../rphys-worktrees/public-architecture-contracts-p2-repository-tooling-scaffold`

### Scope

- Goal: establish uv-managed package metadata, Python 3.12 baseline, command wrappers, contributor guidance, and temporary rights status.
- Files/modules owned:
  - `pyproject.toml`
  - `.python-version`
  - `uv.lock`
  - `Makefile`
  - `CONTRIBUTING.md`
  - `LICENSE`
- Out of scope:
  - `src/rphys/**`, `tests/**`, CI workflows, release automation, docs site tooling, pre-commit hooks, real public license terms, or future module homes.
- Public interfaces allowed to change: repository command surface and project metadata only.
- Scientific/workflow contracts: contributor docs must preserve scientific-contract expectations and no-raw-datasets rule.

### Plan

- Add `pyproject.toml` with `requires-python = ">=3.12"`.
- Add build system exactly:
  - `requires = ["uv_build>=0.11.6,<0.12"]`
  - `build-backend = "uv_build"`
- Keep base dependencies empty or minimal.
- Use uv dependency groups for local tools.
- Omit `license` and `license-files` metadata until a real license is selected.
- Add classifier `Private :: Do Not Upload`.
- Add `.python-version` with `3.12`.
- Generate and commit `uv.lock`.
- Add thin Makefile targets such as `sync`, `lock`, `lock-check`, `test`, `check`, and `diff-check`.
- Add `CONTRIBUTING.md`.
- Add temporary all-rights-reserved `LICENSE` placeholder granting no public permission.

### Pathway Decision

- Selected pathway: standard.
- Rationale: changes package metadata, lockfile behavior, dependency workflow, command surface, and rights metadata.
- Criteria that force standard pathway: already met.

### Validation

| Command | Result | Evidence |
| --- | --- | --- |
| `uv sync` | passed | Created `.venv`, built editable `rphys==0.0.0`, installed pytest stack. Required escalated cache access. |
| `uv lock --check` | passed | `Resolved 7 packages in 1ms`. Required escalated cache access. |
| `make lock-check` | passed | Wrapper ran `uv lock --check`; `Resolved 7 packages in 1ms`. Required escalated cache access. |
| `git diff --check` | passed | No whitespace errors after local implementation. |

### Review Or Checklist Summary

- Automated code review: pending before merge because PR workflow is blocked.
- Automated scientific/workflow review: pending before merge because PR workflow is blocked.
- Unresolved blockers: GitHub auth invalid for PR creation/merge.

### PR And Merge

- PR: not opened; `gh auth status` reports invalid token for `samcantrill`.
- Base branch: `main`
- Head branch: `agent/public-architecture-contracts-p2-repository-tooling-scaffold`
- Checks: local `uv sync`, `uv lock --check`, `make lock-check`, and `git diff --check` passed.
- Merge command: not run.
- Merge result: blocked by GitHub auth and uncreated phase branch/worktree.
- Branch cleanup: not applicable; branch was not created.
- Worktree cleanup: not applicable; worktree was not created.

### Phase Notes

- Implementation summary: Added `pyproject.toml`, `.python-version`, `uv.lock`, `Makefile`, `CONTRIBUTING.md`, and a temporary all-rights-reserved `LICENSE`. Package metadata uses Python `>=3.12`, `uv_build>=0.11.6,<0.12`, empty runtime dependencies, a dev dependency group for `pytest`, no license metadata, and `Private :: Do Not Upload`.
- Commits: none; local uncommitted implementation.
- Assumptions and risks: `pytest>=8.0` resolved to `pytest==9.0.3` in `uv.lock`. The rights placeholder grants no public permission and must be replaced before publication/distribution.
- Follow-up: Run standard automated review gates before any merge.

## Phase 3: Package And Error Skeleton

Status: completed locally; PR/merge blocked
Pathway: standard
Branch: `agent/public-architecture-contracts-p3-package-and-error-skeleton`
Worktree: `../rphys-worktrees/public-architecture-contracts-p3-package-and-error-skeleton`

### Scope

- Goal: create the minimal importable `rphys` package skeleton and broad errors.
- Files/modules owned:
  - `src/rphys/__init__.py`
  - `src/rphys/errors.py`
  - `src/rphys/data/__init__.py`
  - `src/rphys/io/__init__.py`
  - `src/rphys/datasets/__init__.py`
  - `src/rphys/transforms/__init__.py`
- Out of scope:
  - Persistent tests except ad hoc validation evidence.
  - Concrete runtime/domain classes.
  - Future module homes for `methods`, `training`, `losses`, `evaluation`, `analysis`, `recipes`, `stages`, `ops`, `models`, or `testing`.
  - Optional dependency imports and generic `loom` machinery.
- Public interfaces allowed to change: first-wave module homes and broad errors.
- Scientific/workflow contracts: module docstrings may orient ownership but must not promise shapes, units, sampling behavior, or signatures that are deferred.

### Plan

- Add lightweight `src/rphys/__init__.py`.
- Add `src/rphys/errors.py` with `RemotePhysError`, `RemotePhysDataError`, `RemotePhysIOError`, `RemotePhysDatasetError`, `RemotePhysTransformError`, `RemotePhysTrainingError`, and `RemotePhysEvaluationError`.
- Add docstring-only first-wave module homes.
- Avoid broad re-exports that imply unavailable behavior.
- Run import and error inheritance smoke checks.
- Record manual export inventory confirming no stable placeholder domain exports.

### Pathway Decision

- Selected pathway: standard.
- Rationale: creates public import paths and public error classes.
- Criteria that force standard pathway: already met.

### Validation

| Command | Result | Evidence |
| --- | --- | --- |
| `uv sync` | passed | Created `.venv`, built editable `rphys==0.0.0`, installed pytest stack. Required escalated cache access. |
| `uv run python -c "import rphys, rphys.errors, rphys.data, rphys.io, rphys.datasets, rphys.transforms"` | passed | Import smoke check completed with no output. Required escalated cache access. |
| `uv run python -c "from rphys.errors import RemotePhysError, RemotePhysDataError, RemotePhysIOError, RemotePhysDatasetError, RemotePhysTransformError, RemotePhysTrainingError, RemotePhysEvaluationError; assert issubclass(RemotePhysDataError, RemotePhysError); assert issubclass(RemotePhysIOError, RemotePhysError); assert issubclass(RemotePhysDatasetError, RemotePhysError); assert issubclass(RemotePhysTransformError, RemotePhysError); assert issubclass(RemotePhysTrainingError, RemotePhysError); assert issubclass(RemotePhysEvaluationError, RemotePhysError)"` | passed | Error inheritance smoke check completed with no output. Required escalated cache access. |
| `git diff --check` | passed | No whitespace errors after local implementation. |

### Review Or Checklist Summary

- Automated code review: pending before merge because PR workflow is blocked.
- Automated scientific/workflow review: pending before merge because PR workflow is blocked.
- Unresolved blockers: GitHub auth invalid for PR creation/merge.

### PR And Merge

- PR: not opened; `gh auth status` reports invalid token for `samcantrill`.
- Base branch: `main`
- Head branch: `agent/public-architecture-contracts-p3-package-and-error-skeleton`
- Checks: local `uv sync`, import smoke checks, error inheritance smoke check, and `git diff --check` passed.
- Merge command: not run.
- Merge result: blocked by GitHub auth and uncreated phase branch/worktree.
- Branch cleanup: not applicable; branch was not created.
- Worktree cleanup: not applicable; worktree was not created.

### Phase Notes

- Implementation summary: Added minimal `src/rphys` package skeleton, broad `RemotePhys*Error` hierarchy, and first-wave `data`, `io`, `datasets`, and `transforms` module homes with docstrings and no placeholder exports.
- Commits: none; local uncommitted implementation.
- Assumptions and risks: Public imports now exist for first-wave homes only. Deferred module homes remain absent.
- Follow-up: Run standard automated review gates before any merge.

## Phase 4: Contract Validation

Status: completed locally; PR/merge blocked
Pathway: fast
Branch: `agent/public-architecture-contracts-p4-contract-validation`
Worktree: `../rphys-worktrees/public-architecture-contracts-p4-contract-validation`

### Scope

- Goal: add persistent tests/checks enforcing the accepted architecture contract.
- Files/modules owned:
  - `tests/test_public_imports.py`
  - `tests/test_error_hierarchy.py`
  - `tests/test_public_contract_docs.py`
  - `tests/test_dependency_boundaries.py`
- Out of scope:
  - Runtime behavior, future module homes, optional dependency suites, generic machinery, or broad package changes.
  - Source/tooling/docs changes except narrow blocker fixes required to satisfy accepted Phase 1-3 behavior.
- Public interfaces allowed to change: no intended public runtime interface changes.
- Scientific/workflow contracts: docs-policy tests should preserve required future scientific documentation obligations.

### Plan

- Add import tests for first-wave modules and deferred module absence.
- Add error hierarchy tests.
- Add docs-policy tests for API labels, `loom` boundary, `_target_`, registry limits, optional dependency policy, uv/Python policy, code-backed docs policy, and rights status.
- Add dependency-boundary/search tests for generic workflow infrastructure, heavy optional import leakage, and stable placeholder exports.
- Run focused tests, lock check, diff check, and full suite.

### Pathway Decision

- Selected pathway: fast.
- Rationale: validation-only changes do not add public runtime behavior.
- Criteria that force standard pathway: public runtime API changes, package metadata changes beyond missing test support, changed docs policy, concrete domain behavior, future module homes, dependencies, CI, registries, or generic workflow machinery.

### Validation

| Command | Result | Evidence |
| --- | --- | --- |
| `uv run pytest tests/test_public_imports.py tests/test_error_hierarchy.py tests/test_public_contract_docs.py tests/test_dependency_boundaries.py` | passed | 17 tests passed in 0.03s after fixing overly exact doc assertions. Required escalated cache access. |
| `uv lock --check` | passed | `Resolved 7 packages in 1ms`. Required escalated cache access. |
| `uv run pytest` | passed | Full suite: 17 tests passed in 0.03s. Required escalated cache access. |
| `git diff --check` | passed | No whitespace errors after local implementation. |

### Review Or Checklist Summary

- Fast-path checklist:
  - Tests/checks only: passed for Phase 4 owned files.
  - No public runtime behavior: passed.
  - No future module homes: passed.
  - No heavy dependencies: passed.
  - Accepted decisions preserved: passed.
- Unresolved blockers: GitHub auth invalid for PR creation/merge.

### PR And Merge

- PR: not opened; `gh auth status` reports invalid token for `samcantrill`.
- Base branch: `main`
- Head branch: `agent/public-architecture-contracts-p4-contract-validation`
- Checks: local targeted pytest, `uv lock --check`, full pytest, `git diff --check`, and `make check` passed.
- Merge command: not run.
- Merge result: blocked by GitHub auth and uncreated phase branch/worktree.
- Branch cleanup: not applicable; branch was not created.
- Worktree cleanup: not applicable; worktree was not created.

### Phase Notes

- Implementation summary: Added persistent contract tests for public imports, error hierarchy, public contract docs, dependency metadata, heavy optional import boundaries, deferred module absence, generic `loom` infrastructure absence, and placeholder export absence.
- Commits: none; local uncommitted implementation.
- Assumptions and risks: Tests validate the scaffold contract but do not replace standard review for Phase 2/3 before merge.
- Follow-up: Refresh GitHub auth, create the planned PR flow or decide whether to commit this local scaffold directly, and run pending standard review gates before merge.
