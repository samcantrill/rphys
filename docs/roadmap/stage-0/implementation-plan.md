# Roadmap Stage 0 Implementation Plan

Status: approved
Roadmap version: `v0`
Planning document: `docs/roadmap/stage-0/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: complete
Blockers: none

## Summary

- Goal: implement the Milestone 0 repository skeleton and governance baseline that unlocks Milestone 1 without adding domain behavior.
- Approved behavior: planned package homes, broad base error hierarchy, lightweight imports, minimal public API governance, rights-status metadata guardrails, no generic workflow/artifact runtime, and balanced README orientation.
- Key design constraints: root `rphys.__all__` stays empty; no root error re-exports; planned package homes expose empty `__all__`; `rphys.errors` depends only on the standard library; no optional extras or runtime dependencies are added; specific semantic error subclasses are deferred.
- Examples covered: namespace smoke path, structured base error diagnostics, lightweight import guardrail, private metadata guardrail, no workflow/artifact runtime boundary, and README handoff.
- Source phase shaping: three approved phases in `docs/roadmap/stage-0/planning.md`.
- Source plan quality gate: passed with no blockers.
- Out of scope: Milestone 1 naming/data validators, specific semantic error subclasses, datasources, IO, ops, transforms, models, losses, metrics, training, evaluation, analysis, optional dependency matrix, workflow runtime, artifact runtime, and final license selection.

## Implementation Workflow State

- Implementation-plan quality gate: approved
- Review pass: not started
- Refinement pass: not started
- Confirmation review: not started
- Automatic merge mode: enabled
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `core-skeleton-errors` | merged | `agent/stage-0-p1-core-skeleton-errors` | [#2](https://github.com/samcantrill/rphys/pull/2) | `src/rphys/**`, error unit tests, focused import tests | Add planned package homes and base error hierarchy. | `make test-package`, `make test-unit` | Namespace smoke path; structured base error diagnostics. |
| 2 | `governance-guardrails` | merged | `agent/stage-0-p2-governance-guardrails` | [#3](https://github.com/samcantrill/rphys/pull/3) | `tests/package/**`, metadata/import-boundary checks | Make import, API, metadata, and no-runtime guardrails executable. | `make test-package`, `uv lock --check` | Lightweight import guardrail; private metadata guardrail; no-runtime boundary. |
| 3 | `readme-final-validation` | merged | `agent/stage-0-p3-readme-final-validation` | [#4](https://github.com/samcantrill/rphys/pull/4) | `README.md`, final validation evidence | Add compact README governance handoff and run final checks. | `make test-package`, `make test-unit`, `uv lock --check`, `git diff --check` | Balanced README handoff; final validation. |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None. | passed plan quality gate | No action required. | resolved |

## Phase 1: Core Skeleton And Base Errors

Status: merged
Slug: `core-skeleton-errors`
Branch: `agent/stage-0-p1-core-skeleton-errors`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-0-p1-core-skeleton-errors`
PR: [#2](https://github.com/samcantrill/rphys/pull/2)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: create the importable skeleton and broad error hierarchy that later milestones can build on.
- Files/modules owned: `src/rphys/__init__.py`, `src/rphys/errors.py`, planned package `__init__.py` files under `src/rphys`, focused error tests under `tests/unit/rphys`, and focused import checks in `tests/package/test_import.py`.
- Behavior implemented: planned namespace imports, empty namespace `__all__`, broad `RemotePhys*Error` classes, `RemotePhysError(message: str, **context: object)` with copied `.context`, `.message`, normal `args`, and normal exception chaining.
- Decisions applied: DD-1, DD-2, DD-3, DD-4.
- Examples or demos covered: M1 package-home smoke path; structured base error diagnostics.
- Out of scope: README governance expansion, metadata guardrail tests beyond what is needed for this phase, no-runtime negative tests, optional extras, specific semantic error subclasses, and domain behavior.
- Dependencies: approved planning document and current `develop`.

### Tasks

- Add `src/rphys/errors.py` with `RemotePhysError` and all broad roadmap category subclasses.
- Ensure `rphys.errors.__all__` lists only the broad public error classes.
- Keep `src/rphys/__init__.py` lightweight and keep root `__all__` empty.
- Add planned package homes with concise docstrings and empty `__all__`.
- Add or update focused tests for planned namespace imports, root import behavior, broad error imports, subclass relationships, and error context behavior.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Verify root/package imports and initial public surface. | yes |
| `make test-unit` | Verify `RemotePhysError` context behavior and subclass inheritance. | yes |
| `git diff --check` | Catch whitespace issues in new files. | yes |

### Acceptance Evidence

- Behavior evidence: imports pass for `rphys`, `rphys.errors`, and all planned package homes.
- Design-decision evidence: root has no error re-exports; package homes have empty `__all__`; errors use approved context shape.
- Example/demo evidence: namespace smoke and structured error examples are covered by tests.
- Documentation evidence: docstrings avoid claiming stable domain APIs.
- Scientific contract evidence: no scientific operation is introduced.

### Phase Workflow State

- Phase execution plan: recorded in `docs/roadmap/stage-0/phases/core-skeleton-errors.md`
- Planning/refinement budget: one focused pass
- Implementation/refinement budget: one implementation pass plus one blocker-fix pass if tests expose gaps
- PR review budget: one review pass
- Blocker-resolution budget: stop for maintainer input if package homes or public error names need redesign
- Pre-submit blocker gate: package/unit tests pass
- Merge record: recorded in `docs/roadmap/stage-0/phases/core-skeleton-errors-merge-record.md`

### Risks And Stop Conditions

- Risks: visible empty package names create mild compatibility expectations; broad error names become public before full module behavior exists.
- Stop conditions: implementation requires root re-exports, specific semantic subclasses, optional dependencies, or domain behavior to satisfy tests.
- Assumptions: docstrings and empty `__all__` are sufficient to signal namespace-only package homes.

### Completion Summary

- Implementation: added planned package homes with empty `__all__`, broad `RemotePhysError` hierarchy, focused package import tests, and source-mirrored unit tests for error context behavior.
- Validation: `make test-package` passed; `make test-unit` passed; `git diff --check` passed.
- PR: [#2](https://github.com/samcantrill/rphys/pull/2), base `develop`, head `agent/stage-0-p1-core-skeleton-errors`.
- Merge: squash-merged to `develop` at `f8c5038` on 2026-05-12; GitHub reported no configured status checks.
- Follow-up: Phase 2 should harden metadata, import-boundary, public API, and no-runtime guardrails.

## Phase 2: Governance Guardrail Tests

Status: merged
Slug: `governance-guardrails`
Branch: `agent/stage-0-p2-governance-guardrails`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-0-p2-governance-guardrails`
PR: [#3](https://github.com/samcantrill/rphys/pull/3)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: make Stage 0 governance executable through focused package tests.
- Files/modules owned: `tests/package/test_import.py`, optional new package tests such as `tests/package/test_metadata.py` or `tests/package/test_boundaries.py`, and test-only helper constants inside those files.
- Behavior implemented: tests for lightweight imports, runtime dependency emptiness, private/no-license metadata, intentional public API surface, and absence of generic workflow/artifact runtime packages.
- Decisions applied: DD-5 and DD-6, plus validation obligations from DD-1 and DD-4.
- Examples or demos covered: lightweight import guardrail, private package metadata guardrail, no workflow/artifact runtime boundary.
- Out of scope: changing runtime dependencies, selecting a license, adding optional extras, changing README prose except for critical assertions if needed.
- Dependencies: Phase 1 import paths and `rphys.errors` exist.

### Tasks

- Add a short heavy optional-stack import boundary check for `torch`, `numpy`, `cv2`, `av`, `scipy`, `pandas`, and `matplotlib`.
- Prefer a fresh-interpreter or otherwise isolated import check so pytest imports do not mask import side effects.
- Add package metadata checks using `tomllib`: runtime dependencies are empty, no open-source license metadata is advertised, and the private classifier remains.
- Add checks that `LICENSE` still states all rights reserved.
- Add checks for root and namespace `__all__` values and absence of root error re-exports.
- Add negative import-spec checks for `rphys.stages`, `rphys.workflow`, `rphys.workflows`, and `rphys.artifacts`.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Verify package governance guardrails. | yes |
| `uv lock --check` | Confirm guardrail work did not change dependency resolution. | yes |
| `git diff --check` | Catch whitespace issues. | yes |

### Acceptance Evidence

- Behavior evidence: tests fail if obvious optional stacks load from core imports or forbidden runtime packages appear.
- Design-decision evidence: tests enforce empty root surface, empty namespace surfaces, and metadata policy.
- Example/demo evidence: lightweight import, metadata, and no-runtime examples are executable.
- Documentation evidence: none required beyond current policy references unless tests assert README text.
- Scientific contract evidence: no scientific operation is introduced.

### Phase Workflow State

- Phase execution plan: recorded in `docs/roadmap/stage-0/phases/governance-guardrails.md`
- Planning/refinement budget: one focused pass
- Implementation/refinement budget: one implementation pass plus one blocker-fix pass if isolation checks are brittle
- PR review budget: one review pass
- Blocker-resolution budget: stop for maintainer input if metadata policy must change
- Pre-submit blocker gate: package tests and lock check pass
- Merge record: recorded in `docs/roadmap/stage-0/phases/governance-guardrails-merge-record.md`

### Risks And Stop Conditions

- Risks: import-boundary checks can become brittle if path setup is ad hoc; metadata assertions must be updated deliberately when licensing or dependency policy changes.
- Stop conditions: tests require adding optional dependencies, empty extras, or broad forbidden-name lists beyond the approved short list.
- Assumptions: current private/no-license status and empty runtime dependencies remain correct for Stage 0.

### Completion Summary

- Implementation: added fresh-interpreter optional-stack import checks, metadata/private-rights checks, `LICENSE` rights-status checks, and no workflow/artifact runtime negative checks.
- Validation: `make test-package` passed; `uv lock --check` passed; `git diff --check` passed.
- PR: [#3](https://github.com/samcantrill/rphys/pull/3), base `develop`, head `agent/stage-0-p2-governance-guardrails`.
- Merge: squash-merged to `develop` at `c504d56` on 2026-05-12; GitHub reported no configured status checks.
- Follow-up: Phase 3 should align README handoff and run final focused validation.

## Phase 3: README Handoff And Final Validation

Status: merged
Slug: `readme-final-validation`
Branch: `agent/stage-0-p3-readme-final-validation`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-0-p3-readme-final-validation`
PR: [#4](https://github.com/samcantrill/rphys/pull/4)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: align user-facing repository guidance with the implemented Stage 0 skeleton and record final validation evidence.
- Files/modules owned: `README.md` and final validation notes in PR/phase handoff artifacts.
- Behavior implemented: concise README orientation for rebuild status, canonical roadmap, API stability rule, lightweight dependency policy, private rights status, and orchestration boundary.
- Decisions applied: DD-7 and final validation obligations from the approved validation strategy.
- Examples or demos covered: balanced README handoff and final Stage 0 validation.
- Out of scope: long architecture guide, duplicated roadmap detail, final license selection, optional dependency matrix, M1 domain contracts.
- Dependencies: Phases 1 and 2 complete.

### Tasks

- Update README with compact governance/status sections that point to `docs/roadmap.md` as canonical.
- State that imports are intentionally lightweight and public API stability requires documented and tested contracts.
- State current rights status consistently with `LICENSE` and package metadata.
- State that workflow orchestration and generic artifact/runtime concerns belong downstream or in `loom`, not in `rphys`.
- Run final required checks and record any skipped broader validation with rationale.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Verify package/API/metadata/import-boundary guardrails. | yes |
| `make test-unit` | Verify base error behavior. | yes |
| `uv lock --check` | Verify lockfile remains current. | yes |
| `git diff --check` | Verify whitespace cleanliness. | yes |
| `make validate-pr` | Optional broader validation if implementation touches shared tooling or packaging beyond the approved scope. | no |

### Acceptance Evidence

- Behavior evidence: final focused checks pass.
- Design-decision evidence: README remains concise and points to roadmap for detailed policy.
- Example/demo evidence: README handoff is present and validation examples remain covered.
- Documentation evidence: README aligns with roadmap, `LICENSE`, and package metadata.
- Scientific contract evidence: no scientific operation or workflow runtime is introduced.

### Phase Workflow State

- Phase execution plan: recorded in `docs/roadmap/stage-0/phases/readme-final-validation.md`
- Planning/refinement budget: one focused pass
- Implementation/refinement budget: one docs/final-validation pass plus one blocker-fix pass if checks fail
- PR review budget: one review pass
- Blocker-resolution budget: stop for maintainer input if README needs to duplicate or change roadmap policy
- Pre-submit blocker gate: required final checks pass or residual risks are recorded
- Merge record: recorded in `docs/roadmap/stage-0/phases/readme-final-validation-merge-record.md`

### Risks And Stop Conditions

- Risks: README can drift from roadmap policy; final validation may reveal guardrail brittleness from prior phases.
- Stop conditions: README changes require new product/scientific policy, final license selection, or implementation of M1 behavior.
- Assumptions: README should remain a concise handoff, not a second source of architectural truth.

### Completion Summary

- Implementation: updated `README.md` with compact Milestone 0 status, API/import governance, orchestration boundary, and current rights status.
- Validation: `make test-package`, `make test-unit`, `uv lock --check`, `git diff --check`, `make test-summary`, and `make validate-pr` passed locally before PR preparation.
- PR: [#4](https://github.com/samcantrill/rphys/pull/4), base `develop`, head `agent/stage-0-p3-readme-final-validation`.
- Merge: squash-merged to `develop` at `eaf9c62` on 2026-05-12; GitHub reported no configured status checks.
- Follow-up: keep README concise and defer detailed policy changes to `docs/roadmap.md`.

## Cross-Phase Validation

- Full relevant test command: `make test-package`, `make test-unit`, `uv lock --check`, `git diff --check`.
- Docs/template checks: README review for compact governance orientation and consistency with `docs/roadmap.md`, `LICENSE`, and `pyproject.toml`.
- Scientific/workflow contract checks: confirm no scientific operations and no generic workflow/artifact runtime packages are introduced.
- Example/demo checks: package namespace smoke, structured base error diagnostics, lightweight import guardrail, private metadata guardrail, no-runtime boundary, and README handoff are covered by tests or review.
- Manual review focus: public API surface, broad error class names, error context constructor, import side effects, metadata assertions, and README drift.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| No readiness blockers found. | note | Phase shaping, plan quality gate, design decisions, examples, and validation are approved and traceable. | resolved |
| Empty namespace imports and broad error class names create mild compatibility expectations. | concern | Accepted in planning; mitigated with empty `__all__`, concise docstrings, and no domain behavior. | accepted |
| Metadata and README guardrails require future intentional updates. | concern | Accepted in planning; revisit on license selection, optional dependency groups, or roadmap policy changes. | accepted |

Gate result:

- Status: pass
- Review evidence: all phases map to approved planning requirements, decisions, examples, validation rows, assumptions, and deferrals.
- Accepted risks: visible namespace package names, public broad error class names, metadata test maintenance, README drift.
- Revisit triggers: package boundary changes, license selection, optional dependency groups, public root re-export proposal, or pressure to add domain behavior in Stage 0.

## Final Approval

- Approval status: approved on 2026-05-12
- Approved scope: three-phase Milestone 0 implementation covering core skeleton/base errors, governance guardrail tests, and README handoff/final validation.
- Accepted risks: empty namespace package compatibility expectations; broad error class API compatibility; metadata test maintenance; README drift.
- Deferred items: specific semantic error subclasses, M1 naming/data behavior, domain components, optional dependency matrix, workflow/artifact runtime, final license selection.
