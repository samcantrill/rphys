# Phase 2 Execution Plan: Shared Collection, View, And Collector Contracts

## Metadata

- Status: final phase execution plan
- Roadmap stage: `v11`
- Feature focus: dependency-light collection, view, collector, and collector-result contracts
- Stage descriptor: Loss, Objective, And Metric Contracts
- Phase descriptor: Shared Collection, View, And Collector Contracts
- PR title: `Stage 11 Loss, Objective, And Metric Contracts - Phase 2: Shared Collection, View, And Collector Contracts`
- Branch: `agent/stage-11-loss-objective-metric-contracts-p2-collection-view-collector-contracts`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p2-collection-view-collector-contracts`
- Phase execution plan path: `docs/roadmap/stage-11/phases/collection-view-collector-contracts.md`
- Full plan: `docs/roadmap/stage-11/implementation-plan.md`
- Planning document: `docs/roadmap/stage-11/planning.md`
- Source phase: Phase 2
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after local validation, automated review, CI pass, and PR target verification
- Workflow path: expanded path; manager-local refinement folded into this artifact
- Phase isolation: dedicated branch and worktree created from current `origin/develop`
- Plan quality gate: passed and current in the implementation plan
- Blockers: none

## Objective

Implement the reusable collection vocabulary needed by later sample and metric
collection phases while keeping the shared module domain-neutral and
dependency-light.

## Scope Contract

- Add `rphys.collections` with structural `Collection`, `CollectionView`, and
  `Collector` protocols plus frozen `CollectionItem`, `CollectionContext`,
  `CollectionViewPlan`, and `CollectorResult` records.
- Add only central collection errors needed by this behavior.
- Collection iteration yields member values; `entries` preserves
  `CollectionItem` metadata/provenance.
- Views return collections and do not introduce a view-result class.
- Collectors return `CollectorResult` for materialization diagnostics only.
- Shared collection code must not import domain packages or optional numerical,
  dataframe, trainer, evaluator, datasource, export, or backend stacks.

## Scientific Contract Notes

- No sampling, temporal alignment, masking, filtering, normalization,
  aggregation, or physiological reconstruction algorithm is implemented.
- Metadata/provenance maps use string keys and are immutable shallow snapshots.
- `CollectorResult` fails loudly for invalid collection shape, count mismatch,
  skipped/rejected diagnostics without explicit policy, and malformed
  descriptor records.
- Accepted/rejected/skipped counts and item metadata remain inspectable for
  later leakage-sensitive grouping and sample/metric collection behavior.

## Implementation Steps

1. Add central collection error bases and import/package assertions.
2. Implement the shared protocols and frozen records in `rphys.collections`.
3. Add focused unit coverage for value iteration, entry metadata access,
   descriptor validation, immutable metadata, collector diagnostics, and
   fail-loud behavior.
4. Add contract coverage proving fake collectors and views compose without
   inheritance or operation wrappers.
5. Run required unit, contract, package, and whitespace validation.

## Validation Commands

Targeted development commands:

```sh
uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/test_collections.py tests/contracts/test_collection_contract.py tests/unit/rphys/test_errors.py tests/package/test_import.py tests/package/test_import_boundaries.py
UV_CACHE_DIR=/tmp/uv-cache make test-unit
UV_CACHE_DIR=/tmp/uv-cache make test-contract
UV_CACHE_DIR=/tmp/uv-cache make test-package
git diff --check
```

## Completion Notes

- Draft plan: completed manager-local.
- Final phase execution plan: completed.
- Implementation summary: added shared collection protocols/records and central
  collection validation errors.
- Implementation validation: focused tests passed; `make test-unit`,
  `make test-contract`, `make test-package`, and `git diff --check` passed.
- Pre-submit blocker gate: passed manager-local; no domain import leakage,
  root re-export, view-result family, operation-result duplication, or silent
  skip default was introduced.
- PR preparation: PR body drafted in
  `docs/roadmap/stage-11/phases/collection-view-collector-contracts-pr-body.md`.
- Automated review: passed manager-local; PR target/title verified and no
  remote checks were reported.
- Merge result: PR [#72](https://github.com/samcantrill/rphys/pull/72)
  squash merged to `develop` as `8652c96` on 2026-05-16.
- Cleanup: phase worktree pruned and local/remote phase branches deleted.
- Remaining blockers: none.
