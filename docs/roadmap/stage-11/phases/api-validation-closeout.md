# Phase 8 Execution Plan: API, Docs, Import Review, And Validation Closeout

## Metadata

- Status: final phase execution plan
- Roadmap stage: `v11`
- Feature focus: Stage 11 API, docs, import boundaries, and validation evidence
- Stage descriptor: Loss, Objective, And Metric Contracts
- Phase descriptor: API, Docs, Import Review, And Validation Closeout
- PR title: `Stage 11 Loss, Objective, And Metric Contracts - Phase 8: API, Docs, Import Review, And Validation Closeout`
- Branch: `agent/stage-11-loss-objective-metric-contracts-p8-api-validation-closeout`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p8-api-validation-closeout`
- Phase execution plan path: `docs/roadmap/stage-11/phases/api-validation-closeout.md`
- Full plan: `docs/roadmap/stage-11/implementation-plan.md`
- Planning document: `docs/roadmap/stage-11/planning.md`
- Source phase: Phase 8
- Base branch: `develop`
- Target branch: `develop`
- Workflow path: expanded path; manager-local refinement folded into this artifact
- Phase isolation: dedicated branch and worktree created from current `origin/develop`
- Plan quality gate: passed and current in the implementation plan
- Blockers: none

## Objective

Close Stage 11 by reviewing the public API, documentation, dependency
boundaries, rejected result names, examples, and final validation evidence
without adding new product behavior or concrete algorithms.

## Scope Contract

- Public names remain code-backed and scoped to package homes; root `rphys`
  exports stay empty for Stage 11.
- `rphys.collections`, `rphys.data`, `rphys.data.collections`,
  `rphys.losses`, `rphys.objectives`, and `rphys.metrics` import without
  optional backend/report/trainer/evaluator dependencies, including `torch` and
  `torchmetrics`.
- Stage 11 modules use package-local private helpers only; cross-package
  `_validation` imports are rejected by package tests.
- Rejected public metric table, aggregation, view-result, and view-state names
  remain absent.
- Documentation and docstrings record backend-neutral limits, grouping/view
  provenance, explicit failure behavior, and Stage 12/13 deferrals.
- No concrete metric/loss algorithms, trainer/evaluator lifecycle, distributed
  sync, dataframe/report schema, export behavior, or Stage 10 coupling enters
  the closeout.

## Validation Commands

```sh
uv --cache-dir /tmp/uv-cache run pytest tests/package/test_import.py tests/package/test_import_boundaries.py tests/unit/rphys/metrics/test_metric_observation_views.py tests/contracts/test_metric_observation_view_contract.py tests/integration/test_stage11_synthetic_contract_flow.py
UV_CACHE_DIR=/tmp/uv-cache make test-package
UV_CACHE_DIR=/tmp/uv-cache make test-unit
UV_CACHE_DIR=/tmp/uv-cache make test-contract
UV_CACHE_DIR=/tmp/uv-cache make test-integration
UV_CACHE_DIR=/tmp/uv-cache make test-summary
uv lock --check
git diff --check
UV_CACHE_DIR=/tmp/uv-cache make validate-pr
```

## Completion Notes

- Draft plan: completed manager-local.
- Final phase execution plan: completed.
- Implementation summary: reviewed Stage 11 API/import/doc surfaces, added
  direct `rphys.data` and `rphys.data.collections` Stage 11 import-boundary
  checks, added a cross-package private-helper import guard, and refined metric
  observation/view docstrings.
- Implementation validation: focused package/view tests, `make test-package`,
  `make test-unit`, `make test-contract`, `make test-integration`,
  `make test-summary`, `uv lock --check`, `git diff --check`, and
  `make validate-pr` passed.
- Pre-submit blocker gate: passed manager-local; no root re-exports,
  placeholder names, concrete algorithms, backend imports, evaluator/trainer
  lifecycle, distributed sync, report/dataframe schema, or export behavior was
  introduced.
- PR preparation: PR body drafted in
  `docs/roadmap/stage-11/phases/api-validation-closeout-pr-body.md`.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
