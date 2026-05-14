# Phase 5 Execution Plan: DataSourceIndex Construction, Sidecar Entries, And SampleBuilder Bridge

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v5`
- Feature focus: datasource index construction and sidecar provenance
- Stage descriptor: DataSource Discovery, Views, Filters, Splits, And Indexes
- Phase descriptor: DataSourceIndex Construction, Sidecar Entries, And SampleBuilder Bridge
- PR title: `Stage 5 DataSource Discovery, Views, Filters, Splits, And Indexes - Phase 5: DataSourceIndex Construction, Sidecar Entries, And SampleBuilder Bridge`
- Branch: `agent/stage-5-p5-datasource-index-entries`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p5-datasource-index-entries`
- Phase execution plan path: `docs/roadmap/stage-5/phases/datasource-index-entries.md`
- Full plan: `docs/roadmap/stage-5/implementation-plan.md`
- Planning document: `docs/roadmap/stage-5/planning.md`
- Source phase: Phase 5 in `docs/roadmap/stage-5/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path due public index/sidecar contract and SampleBuilder bridge
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed 2026-05-14 in the implementation plan
- Blockers: none

## Objective

Finalize selected/split candidates into ordered lazy `DataSourceIndex` objects that yield pure `IndexItem`s while sidecar `DataSourceIndexEntry` records preserve identity, position, split/group/window/source provenance, and deterministic fingerprints.

## Scope Contract

`DataSourceIndex.__getitem__` and iteration return `IndexItem` objects only. Entry identity, fingerprints, split/group/source/window provenance, and metadata live on `entry_at(position)` and `entries`, not on `IndexItem.metadata`.

## Scientific Contract Notes

- Sampling and temporal alignment: only existing field-native `FieldIndex` windows are recorded; no seconds/alignment/spatial inference.
- Field roles, locators, schemas, and provenance: locator-to-`FieldView` mappings are preserved in items; provenance is recoverable from entries.
- Subject identity, splits, leakage, and grouping: Phase 4 assignments are copied into sidecar entries.
- Payloads and transforms: no payload loading, caching, or runtime operations are added.

## In-Scope Work

- `IndexPlan`, `IndexBuilder`, `IndexResult`, `IndexBuildReport`.
- `DataSourceIndex` and `DataSourceIndexEntry`.
- Item/entry access, stable positions, deterministic entry fingerprints, and `SampleBuilder` integration tests.

## Out-of-Scope Work

- Manifest codecs, composite indexes, cache/export/loaders, payload loading, seconds/spatial/alignment semantics, and identity inside `IndexItem.metadata`.

## Validation Commands

```sh
make test-unit
make test-contract
make test-integration
make test-package
git diff --check
```

## Refinement And Review Budget Status

- Phase execution plan refinement: manager-local expanded-path review completed
- Phase implementation refinement: not needed after targeted validation passed
- PR review: manager-local pre-submit review completed
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed manager-local draft.
- Final phase execution plan: completed with expanded-path review due public index/sidecar behavior.
- Implementation summary: implemented ordered item-yielding datasource indexes, sidecar entries, build reports/results, entry fingerprints, split/group provenance transfer, and SampleBuilder bridge coverage.
- Implementation validation: `make test-unit` passed with 355 tests; `make test-contract` passed with 48 tests; `make test-integration` passed with 2 tests; `make test-package` passed with 25 tests; `git diff --check` passed.
- Pre-submit blocker gate: passed; no manifest codec, composite index, payload loading, or `IndexItem.metadata` identity mutation.
- PR preparation: PR body drafted at `docs/roadmap/stage-5/phases/datasource-index-entries-pr-body.md`; PR #33 opened and verified against `develop`.
- Automated review: manager expanded-path review passed before PR submission; GitHub checks pending/not configured at open.
- Merge result: PR #33 squash-merged to `develop` at `fb9b7169cfb8d480ddbe7d43a0fb442d3e99fd55` on 2026-05-14.
- Cleanup: pending worktree and branch removal after metadata commit.
- Remaining blockers: none.
