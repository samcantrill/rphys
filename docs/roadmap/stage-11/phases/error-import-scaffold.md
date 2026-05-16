# Phase 1 Execution Plan: Error And Import Scaffold

## Metadata

- Status: final phase execution plan
- Roadmap stage: `v11`
- Feature focus: dependency-light broad error bases and import-boundary scaffold
- Stage descriptor: Loss, Objective, And Metric Contracts
- Phase descriptor: Error And Import Scaffold
- PR title: `Stage 11 Loss, Objective, And Metric Contracts - Phase 1: Error And Import Scaffold`
- Branch: `agent/stage-11-loss-objective-metric-contracts-p1-error-import-scaffold`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p1-error-import-scaffold`
- Phase execution plan path: `docs/roadmap/stage-11/phases/error-import-scaffold.md`
- Full plan: `docs/roadmap/stage-11/implementation-plan.md`
- Planning document: `docs/roadmap/stage-11/planning.md`
- Source phase: Phase 1
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after local validation, automated review, CI pass, and PR target verification
- Workflow path: fast path
- Phase isolation: dedicated branch and worktree created from current `origin/develop`
- Plan quality gate: passed and current in the implementation plan
- Draft pass: manager-local
- Refine pass: not needed
- Setup limitations: none
- Blockers: none

## Objective

Establish the central loss, objective, and metric broad error bases while
keeping the package homes lightweight and empty until later phases add
code-backed public contracts.

## Scope Contract

- Add `RemotePhysLossError`, `RemotePhysObjectiveError`, and
  `RemotePhysMetricError` in `rphys.errors` only.
- Do not add package-local duplicate broad errors.
- Do not export loss, objective, or metric contract names before implementation.
- Keep root `rphys` re-exports unchanged.
- Extend import-boundary coverage to include direct Stage 11 package imports
  and the `torchmetrics` optional-dependency sentinel.

## Scientific Contract Notes

- No numerical, sampling, masking, filtering, normalization, grouping, or
  aggregation behavior is implemented in this phase.
- The broad errors are ready to carry primitive context for later contract
  validation without claiming backend behavior.

## Implementation Steps

1. Add the three broad central error bases and include them in `__all__`.
2. Update package and unit tests that assert the public error surface.
3. Extend import-boundary tests for direct Stage 11 package imports and
   optional dependency leakage.
4. Run focused package/error validation plus whitespace checks before PR.

## Test Plan

- Package suite: required, `make test-package`.
- Unit suite: focused error unit tests, `uv run pytest tests/unit/rphys/test_errors.py`.
- Contract/integration/e2e/acceptance suites: deferred; no contract behavior
  exists in this phase.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/test_errors.py tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
git diff --check
```

Final PR-preparation commands:

```sh
make test-package
git diff --check
```

## Completion Notes

- Draft plan: completed manager-local.
- Final phase execution plan: completed.
- Implementation summary: added central `RemotePhysLossError`,
  `RemotePhysObjectiveError`, and `RemotePhysMetricError`; extended package and
  unit error surface tests; added direct Stage 11 package import-boundary
  coverage including `torchmetrics`.
- Implementation validation: `uv --cache-dir /tmp/uv-cache run pytest
  tests/unit/rphys/test_errors.py tests/package/test_import.py
  tests/package/test_import_boundaries.py` passed; `UV_CACHE_DIR=/tmp/uv-cache
  make test-package` passed; `git diff --check` passed.
- Pre-submit blocker gate: passed manager-local; no root re-export, placeholder
  package export, package-local duplicate error base, or forbidden dependency
  import found.
- PR preparation: PR body drafted in
  `docs/roadmap/stage-11/phases/error-import-scaffold-pr-body.md`.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
