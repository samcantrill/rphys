# Phase 7 Execution Plan: Source-Aware CompositeDataSourceIndex

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v5`
- Feature focus: source-aware composite datasource indexes
- Stage descriptor: DataSource Discovery, Views, Filters, Splits, And Indexes
- Phase descriptor: Source-Aware CompositeDataSourceIndex
- PR title: `Stage 5 DataSource Discovery, Views, Filters, Splits, And Indexes - Phase 7: Source-Aware CompositeDataSourceIndex`
- Branch: `agent/stage-5-p7-composite-index`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p7-composite-index`
- Phase execution plan path: `docs/roadmap/stage-5/phases/composite-index.md`
- Full plan: `docs/roadmap/stage-5/implementation-plan.md`
- Planning document: `docs/roadmap/stage-5/planning.md`
- Source phase: Phase 7 in `docs/roadmap/stage-5/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed 2026-05-14 in the implementation plan
- Blockers: none

## Objective

Implement the single public Stage 5 combined-index type: source-aware `CompositeDataSourceIndex` with ordered flat item access, source/child provenance in sidecar entries, child-order-sensitive fingerprints, and manifest round trips through `DataSourceIndexCodec`.

## Scope Contract

Composite indexes return unchanged `IndexItem` objects for `__getitem__` and iteration. Source identity, child index identity, child index fingerprints, child local positions, global positions, child entry IDs, and optional child metadata stay in `DataSourceIndexEntry` sidecars and manifest children. Stage 5 does not expose a public `ConcatDataSourceIndex`.

## Out-of-Scope Work

Weighted sampling, batch planning, cache orchestration, nested multi-member `IndexItem`s, source identity stamped into `IndexItem.metadata`, and any separate public concat API.

## Validation Commands

```sh
make test-unit
make test-contract
make test-package
git diff --check
```

## Completion Notes

- Draft plan: completed manager-local draft.
- Final phase execution plan: completed with fast-path scope because DQ-8 was locked in planning.
- Implementation summary: implemented `CompositeDataSourceIndex`, source-aware `DataSourceIndexEntry` fields, composite child descriptors in `DataSourceIndexManifest`, codec round trips for composite indexes, child-order fingerprint behavior, and package boundaries excluding `ConcatDataSourceIndex`.
- Implementation validation: `make test-unit` passed with 364 tests; `make test-contract` passed with 52 tests; `make test-package` passed with 25 tests; `git diff --check` passed.
- Pre-submit blocker gate: passed; no public concat API, no source identity in `IndexItem.metadata`, and no sampler/cache/batch behavior.
- PR preparation: PR body drafted at `docs/roadmap/stage-5/phases/composite-index-pr-body.md`; PR pending.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending worktree and branch removal after metadata commit.
- Remaining blockers: none.
