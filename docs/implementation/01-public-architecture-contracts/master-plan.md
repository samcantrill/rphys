# Master Plan: Public Architecture Contracts

Status: accepted
Roadmap item: `docs/roadmap/index.md`
Roadmap slug: `public-architecture-contracts`
Plan number: `01`
Planning notes: `docs/implementation/01-public-architecture-contracts/planning-notes.md`
Implementation plan: `docs/implementation/01-public-architecture-contracts/implementation-plan.md`
Quality gate: passed
Stage 3 status: local implementation complete; PR/merge workflow blocked
Blocker: GitHub CLI authentication is invalid for `samcantrill`, blocking PR creation, automated PR review/merge gates, and merge until refreshed.

## Summary

This work package establishes the first public architecture contract for `rphys`: the package boundary, first-wave public module homes, API stability labels, broad `RemotePhys*Error` hierarchy, uv/Python 3.12 project tooling, temporary all-rights-reserved status, extension policy, optional dependency policy, and persistent validation gates.

The implementation is intentionally thin. It creates policy, tooling, importable module homes, broad errors, and tests. It does not implement field containers, dataset references, lazy IO behavior, transforms, materialization, methods, training, losses, metrics, evaluation, analysis, recipes, or stages.

## Behavior Model

- User-visible behavior:
  - Users can import `rphys`, `rphys.errors`, `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`.
  - Users can import broad error base classes from `rphys.errors`.
  - Users can read a public contract document describing API labels, module ownership, extension policy, registry policy, optional dependency policy, scientific-contract expectations, and the `loom`/`rphys` boundary.
- Agent-visible behavior:
  - Stage 3 uses `implementation-plan.md` as the live ledger.
  - Phases run sequentially. Phase `n + 1` starts only after phase `n` is merged and branch/worktree cleanup is complete.
  - Human review is not a merge gate. PRs merge automatically after automated validation and pathway gates pass; approval/admin/force merge is allowed only for human-review-only branch protection.
- Unsupported behavior:
  - No runtime data, IO, dataset, transform, learning, evaluation, analysis, recipe, or stage workflow is provided by this package.
  - No future module homes beyond the first stable wave are created.
  - No generic workflow/config/execution machinery is implemented in `rphys`.
- Stop behavior:
  - Stop if implementation requires concrete domain behavior, heavy base dependencies, future module homes, changed accepted design decisions, unresolved validation failures, unresolved conflicts, or merge authority that is unavailable.

## Goals

- Establish stable first-wave module homes: `rphys.data`, `rphys.io`, `rphys.datasets`, `rphys.transforms`, and `rphys.errors`.
- Define API labels: stable, provisional, private/internal.
- Define broad error bases under readable `RemotePhys*Error` names.
- Document the one-way dependency boundary: `rphys` may depend on `loom`; `loom` must not depend on `rphys`.
- Document `_target_` import paths as the default extension mechanism and limit registries to symbolic-name uses.
- Keep base imports lightweight and optional stacks out of the core package.
- Establish uv-managed project metadata, Python 3.12 baseline, command wrappers, and contributor guidance.
- Make the temporary rights status explicit until a real license is selected.
- Add persistent tests/checks for imports, errors, docs policy, dependency boundaries, and forbidden placeholders.

## Non-Goals

- `DataKey`, `FieldSpec`, `FieldValue`, data object traversal, `Sample`, `Batch`, or collation.
- `DatasetRef`, `RecordRef`, `FieldRef`, `TemporalIndexSlice`, `FieldView`, codecs, adapters, indexes, or sample builders.
- Transform, augmentation, check, pipeline, exporter, or materialization behavior.
- Methods, models, learners, trainers, losses, predictions, metrics, evaluation, analysis reports, recipes, or stages.
- Generic `loom` machinery inside `rphys`.
- Generated API documentation tooling.
- Heavy optional dependencies, real backend package lists, CI workflows, release automation, or a selected public license.

## Design Decisions

| Decision | Status | Rationale | Validation obligation | Residual risk |
| --- | --- | --- | --- | --- |
| Thin contract skeleton before runtime behavior | accepted | Locks public homes and policy without freezing concrete signatures. | Import smoke tests and placeholder absence checks. | Later packages still need detailed API review. |
| First stable module wave is `data`, `io`, `datasets`, `transforms`, and `errors` | accepted | Smallest useful spine for later field, IO, dataset, and transform work. | Docs and imports must match this inventory. | Users may expect learning/evaluation modules; docs must state deferral. |
| Do not create future module homes now | accepted | Empty importable modules can look stable before behavior exists. | Tests should reject deferred modules if they appear early. | Later work must add them deliberately. |
| Stable/provisional/private labels | accepted | Compatibility promises need explicit language. | Contract docs define obligations; tests check stable imports only. | Later package reviews must enforce the labels. |
| Code-backed docs | accepted | Handwritten API signatures drift. | Public docs explain policy and link to code/API reference when available. | Docs tooling remains deferred. |
| Root error is `RemotePhysError` | accepted | Readable and avoids abbreviation ambiguity. | Error hierarchy tests. | Later detailed errors must remain under broad bases. |
| `rphys.io` owns lazy external field access concepts | accepted | Lazy references are IO concerns, not in-memory data container concerns. | Contract docs and later dataset/IO plan must preserve ownership. | Exact signatures remain deferred. |
| Strict `loom`/`rphys` dependency direction | accepted | Prevents cycles and duplicate generic workflow engines. | Docs and local static/search checks. | Cross-repo enforcement is deferred. |
| `_target_` paths by default, limited registries | accepted | User extension code should not need global registration. | Docs check extension and registry policy. | Future plugin discovery may add optional mechanisms. |
| uv, Python 3.12, committed `uv.lock` | accepted | Gives one modern environment/package workflow for maintainers and agents. | `uv sync`, `uv lock --check`, Makefile wrapper checks. | Build backend may need revisit for future native extensions. |
| All rights reserved placeholder | accepted | No real license has been selected. | Metadata and docs checks prevent accidental public license signals. | Must be revisited before publication or distribution. |
| Four sequential phases | accepted | Docs, tooling, code skeleton, and validation are separate review surfaces. | Implementation plan tracks phase status and merge results. | Phase 4 may expose small blocker fixes in earlier outputs. |

## Structure

- `docs/architecture/public-contracts.md`: public architecture contract and stability policy.
- `pyproject.toml`, `.python-version`, `uv.lock`: uv project metadata and reproducible development environment.
- `Makefile`: thin wrappers around uv/check commands.
- `CONTRIBUTING.md`: contributor setup, dependency policy, testing, API labels, scientific-contract expectations, no-raw-datasets rule, and temporary rights status.
- `LICENSE`: temporary all-rights-reserved placeholder.
- `src/rphys/__init__.py`: lightweight package marker.
- `src/rphys/errors.py`: broad `RemotePhys*Error` hierarchy.
- `src/rphys/data/__init__.py`, `src/rphys/io/__init__.py`, `src/rphys/datasets/__init__.py`, `src/rphys/transforms/__init__.py`: first-wave module homes with docstrings only.
- `tests/test_public_imports.py`, `tests/test_error_hierarchy.py`, `tests/test_public_contract_docs.py`, `tests/test_dependency_boundaries.py`: persistent contract validation.

## Public Interfaces

- Stable imports after this package:
  - `rphys`
  - `rphys.errors`
  - `rphys.data`
  - `rphys.io`
  - `rphys.datasets`
  - `rphys.transforms`
- Stable broad errors:
  - `RemotePhysError`
  - `RemotePhysDataError`
  - `RemotePhysIOError`
  - `RemotePhysDatasetError`
  - `RemotePhysTransformError`
  - `RemotePhysTrainingError`
  - `RemotePhysEvaluationError`
- Stable repository workflow:
  - uv-managed project metadata.
  - Python baseline `>=3.12`.
  - committed `uv.lock`.
  - Makefile wrappers for common uv/test/check commands.

## Implementation Phases

| Phase | Slug | Pathway default | Branch | Worktree | Outcome |
| --- | --- | --- | --- | --- | --- |
| 1 | `contract-docs-and-policy` | fast eligible | `agent/public-architecture-contracts-p1-contract-docs-and-policy` | `../rphys-worktrees/public-architecture-contracts-p1-contract-docs-and-policy` | Public contract policy doc lands before code/tooling. |
| 2 | `repository-tooling-scaffold` | standard | `agent/public-architecture-contracts-p2-repository-tooling-scaffold` | `../rphys-worktrees/public-architecture-contracts-p2-repository-tooling-scaffold` | uv/Python/tooling/contributor/rights scaffold. |
| 3 | `package-and-error-skeleton` | standard | `agent/public-architecture-contracts-p3-package-and-error-skeleton` | `../rphys-worktrees/public-architecture-contracts-p3-package-and-error-skeleton` | Minimal importable package and broad errors. |
| 4 | `contract-validation` | fast eligible | `agent/public-architecture-contracts-p4-contract-validation` | `../rphys-worktrees/public-architecture-contracts-p4-contract-validation` | Persistent contract tests and boundary checks. |

Phase execution rule: implement one phase at a time. Phase `n + 1` may start only after phase `n` has merged and branch/worktree cleanup is complete.

## Validation

- Phase 1:
  - `git diff --check`
  - Manual link review for touched docs.
- Phase 2:
  - `uv sync`
  - `uv lock --check`
  - `make lock-check`
  - `git diff --check`
- Phase 3:
  - `uv run python -c "import rphys, rphys.errors, rphys.data, rphys.io, rphys.datasets, rphys.transforms"`
  - `uv run python -c "from rphys.errors import RemotePhysError, RemotePhysDataError, RemotePhysIOError, RemotePhysDatasetError, RemotePhysTransformError, RemotePhysTrainingError, RemotePhysEvaluationError; assert issubclass(RemotePhysDataError, RemotePhysError); assert issubclass(RemotePhysIOError, RemotePhysError); assert issubclass(RemotePhysDatasetError, RemotePhysError); assert issubclass(RemotePhysTransformError, RemotePhysError); assert issubclass(RemotePhysTrainingError, RemotePhysError); assert issubclass(RemotePhysEvaluationError, RemotePhysError)"`
  - `git diff --check`
- Phase 4:
  - `uv run pytest tests/test_public_imports.py tests/test_error_hierarchy.py tests/test_public_contract_docs.py tests/test_dependency_boundaries.py`
  - `uv lock --check`
  - `uv run pytest`
  - `git diff --check`

## Review And Merge Policy

- Human review is not a default merge gate.
- Standard phases use automated code review and automated scientific/workflow review.
- Fast phases use the manager checklist unless risk surfaces; then switch to standard pathway.
- Merge automatically when validation and selected pathway gates pass.
- If branch protection blocks solely on human review and available authority permits, approve, admin-merge, or otherwise force merge only after automated gates pass.
- Do not merge known failing validation, wrong-target PRs, unresolved conflicts, unresolved implementation/review blockers, or changes outside this accepted plan.

## Quality Gate

- Initial review: completed. One blocking issue was found: the architecture refactor-risk gate needed to be recorded clearly.
- Refinement: completed. The plan now records uv build backend metadata, private no-upload classifier, omitted license metadata while rights are unresolved, and architecture refactor-risk handling.
- Architecture refactor-risk review: completed. No blocking findings remain. Key checks covered module ownership, dependency direction, extension points, optional dependencies, deferred decisions, and future API/refactor risk against `docs/rphys_architecture_plan_v3.md`.
- Confirmation review: completed. No blocking findings remain.
- Gate result: passed.
- Accepted risks:
  - Optional extras remain category-level until concrete backends exist.
  - Cross-repo `loom` dependency enforcement remains documented until a shared check exists.
  - Temporary rights placeholder must be replaced before publication, distribution, or external reuse.
  - Later behavior packages need their own API and scientific-contract reviews.
