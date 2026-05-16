# Phase 5 Execution Plan: Sample Collections And Pre-Metric Views

## Metadata

- Status: final phase execution plan
- Roadmap stage: `v11`
- Feature focus: sample collection snapshots, collectors, and descriptor-driven views
- Stage descriptor: Loss, Objective, And Metric Contracts
- Phase descriptor: Sample Collections And Pre-Metric Views
- PR title: `Stage 11 Loss, Objective, And Metric Contracts - Phase 5: Sample Collections And Pre-Metric Views`
- Branch: `agent/stage-11-loss-objective-metric-contracts-p5-sample-collection-views`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p5-sample-collection-views`
- Phase execution plan path: `docs/roadmap/stage-11/phases/sample-collection-views.md`
- Full plan: `docs/roadmap/stage-11/implementation-plan.md`
- Planning document: `docs/roadmap/stage-11/planning.md`
- Source phase: Phase 5
- Base branch: `develop`
- Target branch: `develop`
- Workflow path: expanded path; manager-local refinement folded into this artifact
- Phase isolation: dedicated branch and worktree created from current `origin/develop`
- Plan quality gate: passed and current in the implementation plan
- Blockers: none

## Objective

Implement sample collection snapshots, collector diagnostics, and pre-metric
collection views for grouping, sorting, field selection, and fake/injected
stitching without datasource runners or concrete reconstruction algorithms.

## Scope Contract

- `SampleCollection` iterates over `Sample` values while preserving
  `CollectionItem[Sample]` entry metadata/provenance.
- `SampleCollector` materializes iterables or existing collections into
  `CollectorResult[SampleCollection]`; invalid/missing metadata fails loudly
  unless an explicit skip policy is configured.
- `SampleCollectionViewPlan` records group keys, sort keys, selected fields,
  stitch policy, missing-window policy, overlap policy, metadata, and
  provenance.
- `PlannedSampleCollectionView` returns `SampleCollection` snapshots and only
  supports identity behavior or injected fake stitch behavior.
- No datasource scans, lazy IO, evaluator runners, reports, exports, or
  concrete resampling/interpolation/filtering/physiological reconstruction
  algorithms are introduced.

## Validation Commands

```sh
uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/data/test_sample_collections.py tests/contracts/test_sample_collection_contract.py tests/package/test_import.py tests/package/test_import_boundaries.py
UV_CACHE_DIR=/tmp/uv-cache make test-unit
UV_CACHE_DIR=/tmp/uv-cache make test-contract
UV_CACHE_DIR=/tmp/uv-cache make test-package
git diff --check
```

## Completion Notes

- Draft plan: completed manager-local.
- Final phase execution plan: completed.
- Implementation summary: added sample collection snapshots, collector
  behavior, view plans, planned view execution, data exports, and tests for
  grouping/sorting/selection/fake stitching.
- Implementation validation: focused tests passed; `make test-unit`,
  `make test-contract`, `make test-package`, and `git diff --check` passed.
- Pre-submit blocker gate: passed manager-local; no datasource/evaluator/report
  scope, concrete algorithms, hidden mutation, or silent filtering default was
  introduced.
- PR preparation: PR body drafted in
  `docs/roadmap/stage-11/phases/sample-collection-views-pr-body.md`.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
