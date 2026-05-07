# Execution Playbook: Public Architecture Contracts Phase 3 Package And Error Skeleton

Status: ready for phase implementation planning
Master plan: `docs/implementation/public-architecture-contracts/master-plan.md`
Roadmap item: `docs/roadmap/index.md`
Branch: `agent/public-architecture-contracts-p3-package-and-error-skeleton`
Worktree: `../rphys-worktrees/public-architecture-contracts-p3-package-and-error-skeleton`
Phase notes: `docs/implementation/public-architecture-contracts/phase-3-package-and-error-skeleton/phase-notes.md`
Public PR body: `docs/implementation/public-architecture-contracts/phase-3-package-and-error-skeleton/pr-body.md`
Quality gate: Stage 1 accepted; Stage 2 accepted; master-plan quality gate passed
Blockers: GitHub auth is invalid for `samcantrill`, blocking PR creation and merge until re-authenticated

## Compact Context Capsule

Goal: create the minimal importable `rphys` package skeleton that matches Phase 1 policy and Phase 2 uv metadata.

Accepted decisions: importable first-wave homes are `rphys`, `rphys.errors`, `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`; broad error root is `RemotePhysError`; broad family errors are acceptable now; concrete data, IO, dataset, transform, learning, and evaluation behavior is deferred.

Constraints: no placeholder domain classes, no future module homes, no runtime logic, no heavy optional dependency imports, no `loom` generic machinery.

## Ownership

- Files/modules owned by this phase:
  - `src/rphys/__init__.py`
  - `src/rphys/errors.py`
  - `src/rphys/data/__init__.py`
  - `src/rphys/io/__init__.py`
  - `src/rphys/datasets/__init__.py`
  - `src/rphys/transforms/__init__.py`
- Files/modules explicitly out of scope:
  - `tests/**` except ad hoc validation commands recorded in phase notes.
  - `pyproject.toml`, `.python-version`, `uv.lock`, `Makefile`, `CONTRIBUTING.md`, `LICENSE` except narrow blocker fixes from Phase 2.
  - Future module homes for `methods`, `training`, `losses`, `evaluation`, `analysis`, `recipes`, `stages`, `ops`, `models`, or `testing`.
  - Runtime class/function implementations for data, IO, datasets, transforms, methods, training, losses, metrics, or evaluation.
- Public interfaces allowed to change:
  - New importable first-wave module homes.
  - New broad error classes in `rphys.errors`.
- Other active branches/worktrees to avoid:
  - Phase 1 docs, Phase 2 tooling, and Phase 4 validation worktrees unless merged into current base.

## Current Source And Harness Findings

- Existing files that constrain this phase: Phase 1 policy doc should exist before this phase; Phase 2 uv tooling should exist before validation commands run.
- Existing tests or harness behavior: persistent tests are Phase 4; this phase uses ad hoc `uv run python -c ...` import and inheritance checks.
- Import-boundary or dependency constraints: base imports must avoid torch, video, signal, training, analysis, and generic workflow stacks.
- Scientific contract constraints: module docstrings can orient ownership but must not promise concrete scientific behavior, shapes, units, or signatures that are deferred.
- GitHub status: `gh auth status` reports an invalid token for `samcantrill`; record this and do not attempt PR creation until fixed.

## Scope Contract

This phase creates only executable public homes and broad error bases:

- `rphys` package marker with concise docstring and no broad domain re-exports.
- `rphys.errors` with:
  - `RemotePhysError`
  - `RemotePhysDataError`
  - `RemotePhysIOError`
  - `RemotePhysDatasetError`
  - `RemotePhysTransformError`
  - `RemotePhysTrainingError`
  - `RemotePhysEvaluationError`
- Empty or docstring-only first-wave module homes for `data`, `io`, `datasets`, and `transforms`.

It must not create stable or provisional placeholder classes such as `DataKey`, `Sample`, `DatasetRef`, `FieldRef`, `TemporalIndexSlice`, `FieldView`, `SampleTransform`, method, loss, metric, model, recipe, stage, or testing objects.

## Tasks

- Add minimal `src/rphys/__init__.py` with package docstring and conservative `__all__`, if any.
- Add `src/rphys/errors.py` with broad error hierarchy and readable docstrings.
- Add first-wave module home `__init__.py` files with ownership docstrings only.
- Avoid importing optional stacks or `loom` from base modules unless a real accepted need exists.
- Run ad hoc import checks for first-wave homes.
- Run ad hoc error inheritance assertions.
- Record manual export inventory showing no stable placeholder runtime/domain exports.

## Pathway Eligibility

- Recommended pathway: standard.
- Fast-path rationale, if applicable: not recommended. This phase creates public import paths and public error classes.
- Criteria that would force standard pathway:
  - Already met by public interface creation.
  - Any change to public module homes, error names, or import behavior.

## Implementation Plan Output

- Detailed implementation plan path: `docs/implementation/public-architecture-contracts/phase-3-package-and-error-skeleton/implementation-plan.md`
- Fast-path checklist path, if used: `docs/implementation/public-architecture-contracts/phase-3-package-and-error-skeleton/fast-path-checklist.md`

## Expected Commits

- Planning/handoff documents.
- Package module homes and errors.
- Ad hoc validation evidence and phase notes.
- Review fixes and cleanup.

## Design Impact

- Maintainability: stable module homes exist without premature concrete signatures.
- Extensibility: later behavior packages can add concrete APIs under accepted owners.
- Scientific workflow safety: no scientific behavior is exposed before shape/unit/failure contracts are reviewed.
- Source-tree boundaries: code stays under `src/rphys` first-wave homes only.

## Future Compatibility

Later packages can implement data containers, IO references, datasets, transforms, methods, training, losses, and evaluation under their owning accepted plans. Error subclasses can be added under the broad family bases without renaming the root.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Create all v3 module homes now | Empty future modules would look importable and stable too early. |
| Add `NotImplementedError` placeholders for future classes | Accepted plan forbids treating placeholders as stable and prefers no placeholders. |
| Put lazy IO reference concepts under `rphys.data` | Stage 1 accepted future `rphys.io` ownership. |
| Name the root error `RPhysError` | Maintainer accepted `RemotePhysError`. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Importable module homes have little functionality | The package intentionally validates homes before behavior | Owning runtime packages add concrete behavior |
| Broad error hierarchy lacks detailed package-specific errors | Detailed failure modes belong with concrete behavior | Later packages define specific exceptions |

## Reviewability

- Expected PR size and shape: small code PR with package marker, one error module, and four module-home files.
- Files and areas to inspect: error names and inheritance, module docstrings, `__all__` contents, and import side effects.
- Scope-control checks: verify no future modules, placeholder domain classes, runtime behavior, optional stack imports, or generic workflow machinery were added.

## Verification

- Phase-specific commands:
  - `uv sync`
  - `uv run python -c "import rphys, rphys.errors, rphys.data, rphys.io, rphys.datasets, rphys.transforms"`
  - `uv run python -c "from rphys.errors import RemotePhysError, RemotePhysDataError, RemotePhysIOError, RemotePhysDatasetError, RemotePhysTransformError, RemotePhysTrainingError, RemotePhysEvaluationError; assert issubclass(RemotePhysDataError, RemotePhysError); assert issubclass(RemotePhysIOError, RemotePhysError); assert issubclass(RemotePhysDatasetError, RemotePhysError); assert issubclass(RemotePhysTransformError, RemotePhysError); assert issubclass(RemotePhysTrainingError, RemotePhysError); assert issubclass(RemotePhysEvaluationError, RemotePhysError)"`
  - `git diff --check`
- Full-suite command:
  - `uv run pytest` if tests exist after previous phases; otherwise record as unavailable/not applicable.
- Expected evidence to record:
  - Import command output.
  - Error inheritance assertion output.
  - Manual export inventory showing no stable placeholder runtime/domain exports.
  - Confirmation that base imports do not require optional stacks.

### Suite Obligations

- Package: ad hoc import smoke checks.
- Unit: ad hoc error hierarchy assertions.
- Contract: manual placeholder/export review.
- Integration: editable install/import through uv.
- E2E: not required.
- Opt-in: not required.

## Review Focus

- Standard pathway code review: public imports are minimal, error hierarchy is broad/readable, no over-specific behavior, no unrelated tooling/docs churn.
- Standard pathway scientific/workflow review: no scientific runtime behavior is implied without contracts; generic workflow machinery remains in `loom`.
- Fast-path manager checklist: not applicable by default.

## Stop Conditions

- GitHub auth remains invalid when PR creation or merge is required.
- Import checks cannot pass without adding future modules, placeholder classes, heavy dependencies, or generic workflow machinery.
- Error naming needs to change from `RemotePhysError` or broad family names.
- A dependency on `loom` or optional stacks becomes necessary for import-only skeleton behavior.
- Existing Phase 2 tooling is missing or broken in a way that cannot be fixed narrowly.

## Budget Status

- Implementation blocker cycles used: 0 of 2.
- Code review: pending standard pathway.
- Scientific/workflow review: pending standard pathway.
- Fast-path checklist: not applicable by default.
- Pre-submit blocker gate: pending.

## Completion Notes

- Implementation summary: pending.
- Validation summary: pending.
- Review summary: pending.
- PR preparation: blocked until `gh auth status` succeeds.
- Merge and cleanup: pending.
- Remaining blockers: GitHub auth invalid for `samcantrill`.
