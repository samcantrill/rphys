# Phase 1 Execution Plan: Public Boundary, Errors, And Private Synthetic Fixture Scaffold

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v5`
- Feature focus: datasource public boundary and private fixture scaffold
- Stage descriptor: DataSource Discovery, Views, Filters, Splits, And Indexes
- Phase descriptor: Public Boundary, Errors, And Private Synthetic Fixture Scaffold
- PR title: `Stage 5 DataSource Discovery, Views, Filters, Splits, And Indexes - Phase 1: Public Boundary, Errors, And Private Synthetic Fixture Scaffold`
- Branch: `agent/stage-5-p1-public-boundary-errors-fixtures`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p1-public-boundary-errors-fixtures`
- Phase execution plan path: `docs/roadmap/stage-5/phases/public-boundary-errors-fixtures.md`
- Full plan: `docs/roadmap/stage-5/implementation-plan.md`
- Planning document: `docs/roadmap/stage-5/planning.md`
- Source phase: Phase 1 in `docs/roadmap/stage-5/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed 2026-05-14 in the implementation plan
- Draft pass: manager-local draft
- Refine pass: not needed on fast path
- Setup limitations: no subagent delegation was used in this session
- Blockers: none

## Objective

Establish Stage 5 datasource module homes and boundary tests without adding unimplemented public behavior, broad re-exports, root exports, public synthetic datasources, or final index/composite APIs.

## Full-Plan Context

This phase only prepares the import boundary for later adapter, validation, filtering, splitting, index, manifest, and composite phases. Phases 2 through 8 own all functional behavior, public data records, manifests, integration examples, and final documentation hardening.

## Source Phase Summary

- Goal: create Stage 5 module homes and private diagnostic/test-support scaffold.
- Required scope: importable submodules, conservative `rphys.datasources` parent exports, package import-boundary tests, and private `tests/support` fixture location.
- Required checkpoints: no public placeholder names, no root exports, no public synthetic helpers, no `rphys.datasets`, and no public concat API.
- Acceptance criteria: lightweight submodule imports, existing Stage 3 descriptor exports preserved, and EX-6 negative import checks pass.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: `rphys.datasources.__init__` currently re-exports only Stage 3 descriptor names; `rphys.errors` already has Stage 3 datasource errors.
- Existing tests or harness behavior: package tests protect `__all__`, root exports, optional dependency import cost, and source-tree boundary.
- Import-boundary or dependency constraints: new modules must import no heavy optional packages and must not import runtime builders or test support from package code.

## Phase Isolation State

- Control checkout dirty-state review: only unrelated untracked `docs/roadmap/stage-6/planning.md` remains outside this worktree.
- Dedicated branch/worktree status: created from current `develop` at `/home/samcantrill/work/rphys-worktrees/stage-5-p1-public-boundary-errors-fixtures`.
- Current `develop` base: includes PR #28 Stage 5 planning artifacts.
- Earlier phase dependency status: no earlier Stage 5 implementation phase exists.
- Push/PR infrastructure status: GitHub auth and fetch verified before phase start.
- Stop condition if isolation cannot be maintained: stop before PR submission and record the blocker in this artifact and the implementation plan.

## In-Scope Work

- Add importable Stage 5 datasource submodules with empty `__all__` and boundary docstrings.
- Preserve the current parent-package descriptor exports.
- Add package/import-boundary tests for submodule-first policy and private synthetic fixture boundaries.
- Add a private `tests/support/synthetic_datasources.py` scaffold with no public package exposure.

## Out-of-Scope Work

- Adapter specs, scan results, validation reports, filters, views, candidates, groups, splits, indexes, manifests, composite indexes, and sample-builder integration.
- New public error names without public behavior that raises them.
- Root exports, broad `rphys.datasources` parent re-exports, public fake datasource APIs, `rphys.datasets`, public helper modules, or `ConcatDataSourceIndex`.

## Assumptions

- Empty public surfaces on importable Stage 5 submodules are acceptable because the modules are behavior-backed only by import-boundary policy in this phase.
- Concrete Stage 5 error classes should be added in later phases alongside behavior that raises them.

## Scope Contract

The only public behavior added is that `rphys.datasources.adapters`, `validation`, `filters`, `splits`, and `indexes` are importable lightweight submodules with no public objects yet. Parent and root exports remain unchanged.

## Scientific Contract Notes

- Sampling and temporal alignment: unchanged.
- Field roles, locators, schemas, and provenance: unchanged.
- Masking, filtering, normalization, and aggregation order: unchanged.
- Subject identity, splits, leakage, and grouping: unchanged.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: unchanged.

## Design Impact

- Maintainability: later phases get explicit module homes without overloading descriptor modules.
- Extensibility: future public objects can be added only when backed by behavior and tests.
- Lightweight import policy: new modules must not import heavy optional dependencies.
- Source-tree boundaries: private test support remains under `tests/support`.

## Future Compatibility

Later stages can promote selected names additively from submodules after behavior stabilizes. This phase intentionally avoids public helpers, registries, synthetic datasource APIs, and concat naming.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Re-export Stage 5 names from `rphys.datasources` immediately | Would create public placeholders before behavior exists. |
| Add a public synthetic datasource module | Would make test fixtures part of the reusable library contract. |
| Add Stage 5 concrete errors now | No public Phase 1 behavior needs to raise them. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Stage 5 submodules initially expose empty `__all__` | Preserves submodule-first import policy without placeholders. | A later phase implements public behavior in that submodule. |

## Reviewability

- Expected PR size and shape: small boundary-only PR with module homes, package tests, and a phase artifact.
- Files and areas to inspect: `src/rphys/datasources`, `tests/package`, `tests/support`, and this plan.
- Scope-control checks: no parent/root export expansion, no new behavior records, no public synthetic fixture, no concat API.

## Implementation Steps

1. Add lightweight Stage 5 datasource submodule homes with empty public surfaces.
2. Add private synthetic datasource support module scaffold.
3. Extend package import-boundary tests for Stage 5 submodule-first policy and negative public/private checks.
4. Run targeted package validation and whitespace checks.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: submodules import, parent/root exports remain conservative, no public synthetic/concat/helper exports, no heavy optional imports.

### Unit Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no new public behavior or errors are implemented in this phase.

### Contract Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: public contracts begin in Phase 2.

### Integration Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: synthetic vertical slice belongs to later phases.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no end-to-end behavior exists yet.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no real datasource or optional dependency behavior exists.

## Risks

- Empty modules could be mistaken for placeholders; tests constrain them to import-boundary behavior only.
- Future phases could accidentally promote helper or synthetic names; package tests add explicit guardrails.

## Validation Commands

Targeted development commands:

```sh
make test-package
git diff --check
```

Final PR-preparation commands:

```sh
make test-package
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: module homes, package tests, private support scaffold.
- Tests to run with each slice: `make test-package`.
- Decisions the executor must not revisit: no root exports, no parent Stage 5 re-exports, no public synthetic datasource, no public concat API.
- Conditions that require stopping for the manager: any need to add functional adapter/filter/split/index behavior in Phase 1.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed manager-local draft.
- Final phase execution plan: completed on fast path; refinement not needed.
- Implementation summary: added dependency-light Stage 5 datasource submodule homes, package boundary tests, and private synthetic fixture scaffold.
- Implementation validation: `make test-package` passed with 25 tests; `git diff --check` passed.
- Refinement summary: not needed; targeted validation passed and no coverage obligation is missing for Phase 1.
- Pre-submit blocker gate: passed; no root exports, parent Stage 5 re-exports, public synthetic fixture, public concat API, or unimplemented public placeholder names are present.
- PR preparation: PR body drafted at `docs/roadmap/stage-5/phases/public-boundary-errors-fixtures-pr-body.md`; PR #29 opened and verified against `develop`.
- Automated review: manager review passed before PR submission; GitHub checks pending/not configured at open.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
