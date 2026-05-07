# Execution Playbook: Public Architecture Contracts Phase 4 Contract Validation

Status: ready for phase implementation planning
Master plan: `docs/implementation/public-architecture-contracts/master-plan.md`
Roadmap item: `docs/roadmap/index.md`
Branch: `agent/public-architecture-contracts-p4-contract-validation`
Worktree: `../rphys-worktrees/public-architecture-contracts-p4-contract-validation`
Phase notes: `docs/implementation/public-architecture-contracts/phase-4-contract-validation/phase-notes.md`
Public PR body: `docs/implementation/public-architecture-contracts/phase-4-contract-validation/pr-body.md`
Quality gate: Stage 1 accepted; Stage 2 accepted; master-plan quality gate passed
Blockers: GitHub auth is invalid for `samcantrill`, blocking PR creation and merge until re-authenticated

## Compact Context Capsule

Goal: add persistent tests and checks that enforce the accepted public architecture contract after docs, tooling, and package skeleton phases have landed.

Accepted decisions: tests must cover first-wave imports, broad `RemotePhys*Error` hierarchy, docs-policy obligations, dependency boundaries, no generic `loom` infrastructure in `rphys`, no future module homes, and no stable placeholder domain exports.

Constraints: this phase is tests/checks-first. Runtime code changes are out of scope except narrowly scoped blocker fixes required to make accepted Phase 2 or Phase 3 behavior match the plan.

## Ownership

- Files/modules owned by this phase:
  - `tests/test_public_imports.py`
  - `tests/test_error_hierarchy.py`
  - `tests/test_public_contract_docs.py`
  - `tests/test_dependency_boundaries.py`
- Files/modules explicitly out of scope:
  - `src/rphys/**` except narrow blocker fixes for accepted skeleton defects.
  - `pyproject.toml`, `uv.lock`, `Makefile` except narrow test dependency or command fixes if Phase 2 omitted required pytest support.
  - `docs/architecture/public-contracts.md` except narrow blocker fixes if required accepted policy text is missing.
  - Future module homes and runtime/domain behavior.
- Public interfaces allowed to change:
  - No intended public runtime interface changes.
  - Tests become persistent repository contract checks.
- Other active branches/worktrees to avoid:
  - Earlier phase worktrees unless merged into the current base.

## Current Source And Harness Findings

- Existing files that constrain this phase: Phase 1 policy doc, Phase 2 uv tooling, and Phase 3 package/error skeleton should already exist.
- Existing tests or harness behavior: this phase creates the focused tests named by the master plan and runs them through `uv run pytest`.
- Import-boundary or dependency constraints: tests must fail if base imports require heavy optional stacks or if generic workflow infrastructure is introduced into `rphys`.
- Scientific contract constraints: docs-policy tests should ensure later scientific components must document units, shapes, dtypes, coordinate frames, sampling rates, temporal alignment, leakage risks, failure behavior, and validation tests.
- GitHub status: `gh auth status` reports an invalid token for `samcantrill`; record this and do not attempt PR creation until fixed.

## Scope Contract

This phase turns accepted contracts into persistent checks:

- Import checks for `rphys`, `rphys.errors`, `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`.
- Error hierarchy checks for broad `RemotePhys*Error` classes.
- Docs-policy checks for API labels, `loom` boundary, `_target_`, registry limits, optional dependency policy, uv/Python 3.12 policy, code-backed docs policy, and temporary rights status.
- Dependency/search checks that reject generic workflow infrastructure in `rphys`.
- Export checks that reject stable placeholders for `DataKey`, `Sample`, `DatasetRef`, `FieldRef`, transforms, methods, losses, metrics, models, recipes, stages, or testing modules.

No new runtime behavior, future module homes, fixtures, optional dependency suites, or generic machinery.

## Tasks

- Add `tests/test_public_imports.py` for first-wave module importability and future module absence.
- Add `tests/test_error_hierarchy.py` for broad error imports, inheritance, and normal `Exception` behavior.
- Add `tests/test_public_contract_docs.py` for accepted policy keywords and required deferrals.
- Add `tests/test_dependency_boundaries.py` for no generic workflow infrastructure, no stable placeholder exports, and no heavy optional import leakage.
- Run focused pytest command.
- Run `uv lock --check` and `git diff --check`.
- Run full suite with `uv run pytest` and record evidence or explain any pre-existing unrelated failure.
- Record any narrow blocker fix separately in phase notes.

## Pathway Eligibility

- Recommended pathway: fast, only if limited to tests/checks and narrow non-runtime blocker fixes.
- Fast-path rationale, if applicable: validation-only changes do not add public runtime behavior when the previous phases are already merged and accepted.
- Criteria that would force standard pathway:
  - Any new or changed public runtime API.
  - Changes to package metadata beyond missing test support.
  - Reopening accepted docs policy.
  - Adding concrete domain behavior, future module homes, dependencies, CI, registry implementations, or generic workflow machinery.

## Implementation Plan Output

- Detailed implementation plan path: `docs/implementation/public-architecture-contracts/phase-4-contract-validation/implementation-plan.md`
- Fast-path checklist path, if used: `docs/implementation/public-architecture-contracts/phase-4-contract-validation/fast-path-checklist.md`

## Expected Commits

- Planning/checklist documents.
- Focused tests/checks.
- Narrow blocker fixes, if any.
- Validation evidence and phase notes.
- Cleanup after review/checklist.

## Design Impact

- Maintainability: accepted policy becomes executable checks instead of relying on memory.
- Extensibility: future packages get guardrails for adding stable behavior under the right owners.
- Scientific workflow safety: docs-policy tests preserve scientific contract obligations before behavior packages expand.
- Source-tree boundaries: tests enforce that `rphys` stays domain-specific and lightweight.

## Future Compatibility

Later packages can extend these tests when they add concrete stable behavior. Cross-repo enforcement that `loom` never imports `rphys` remains future work until both repos can be checked together.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Manual review only | The package is meant to create persistent architecture contracts. |
| Broad fixtures or synthetic data now | No runtime data behavior exists in this package. |
| Tests that require optional stacks | Base import contract must stay lightweight. |
| Cross-repo `loom` enforcement now | Current package can enforce only local non-duplication and documented direction. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Cross-repo `loom` dependency check remains manual/documented | `loom` is a separate repo/workspace concern | Shared CI or workspace check becomes available |
| Docs-policy tests may be keyword-based | No docs tooling is selected yet | Generated docs or structured policy metadata exists |
| Optional dependency leakage checks are lightweight | No optional backends are implemented yet | Adding real optional extras or backend modules |

## Reviewability

- Expected PR size and shape: mostly focused tests/checks, with small blocker fixes only if needed.
- Files and areas to inspect: test assertions, forbidden-name lists, docs-policy expectations, and any non-test changes.
- Scope-control checks: verify no runtime behavior, future module homes, optional stack dependencies, or generic workflow machinery were added.

## Verification

- Phase-specific commands:
  - `uv run pytest tests/test_public_imports.py tests/test_error_hierarchy.py tests/test_public_contract_docs.py tests/test_dependency_boundaries.py`
  - `uv lock --check`
  - `git diff --check`
- Full-suite command:
  - `uv run pytest`
- Expected evidence to record:
  - Focused pytest output.
  - Full-suite output.
  - `uv lock --check` output.
  - `git diff --check` output.
  - Search/check evidence that no generic workflow infrastructure and no stable placeholders exist.

### Suite Obligations

- Package: first-wave import smoke tests.
- Unit: error hierarchy tests.
- Contract: docs-policy, placeholder absence, future module absence, and dependency-boundary checks.
- Integration: editable install plus full `uv run pytest`.
- E2E: not required.
- Opt-in: not required.

## Review Focus

- Standard pathway code review: required only if fast-path criteria fail; inspect any non-test changes closely.
- Standard pathway scientific/workflow review: required only if tests or fixes affect scientific/workflow policy.
- Fast-path manager checklist: tests/checks only, no runtime behavior, no dependencies beyond test support, accepted design unchanged, focused and full suites recorded.

## Stop Conditions

- GitHub auth remains invalid when PR creation or merge is required.
- Tests cannot be written without changing accepted design decisions.
- Passing tests requires adding concrete domain behavior, stable placeholders, future module homes, heavy dependencies, or generic workflow infrastructure.
- A required docs-policy assertion conflicts with Phase 1 policy text in a way that reopens accepted decisions.
- Full-suite failures appear unrelated and cannot be isolated safely.

## Budget Status

- Implementation blocker cycles used: 0 of 2.
- Code review: not started; required if standard pathway is selected.
- Scientific/workflow review: not started; required if standard pathway is selected.
- Fast-path checklist: pending pathway decision.
- Pre-submit blocker gate: pending.

## Completion Notes

- Implementation summary: pending.
- Validation summary: pending.
- Review summary: pending.
- PR preparation: blocked until `gh auth status` succeeds.
- Merge and cleanup: pending.
- Remaining blockers: GitHub auth invalid for `samcantrill`.
