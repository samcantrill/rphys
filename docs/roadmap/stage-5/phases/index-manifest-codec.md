# Phase 6 Execution Plan: Manifest Codec, Durable Schema, Fingerprints, And Checksums

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v5`
- Feature focus: datasource index manifest codec
- Stage descriptor: DataSource Discovery, Views, Filters, Splits, And Indexes
- Phase descriptor: Manifest Codec, Durable Schema, Fingerprints, And Checksums
- PR title: `Stage 5 DataSource Discovery, Views, Filters, Splits, And Indexes - Phase 6: Manifest Codec, Durable Schema, Fingerprints, And Checksums`
- Branch: `agent/stage-5-p6-index-manifest-codec`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p6-index-manifest-codec`
- Phase execution plan path: `docs/roadmap/stage-5/phases/index-manifest-codec.md`
- Full plan: `docs/roadmap/stage-5/implementation-plan.md`
- Planning document: `docs/roadmap/stage-5/planning.md`
- Source phase: Phase 6 in `docs/roadmap/stage-5/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path due durable schema/persistence contract
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed 2026-05-14 in the implementation plan
- Blockers: none

## Objective

Persist and reload datasource indexes through the schema-versioned `rphys.datasource_index.v1` manifest, deterministic canonical JSON, content fingerprints, full-manifest checksums, and explicit rejection paths.

## Scope Contract

The codec is JSON-only and datasource-index-specific. It preserves exact `IndexItem` descriptor dictionaries and `DataSourceIndexEntry` sidecars. Content fingerprints are distinct from the full-manifest checksum. Unsupported schemas, ambiguous keys, entry fingerprint mismatches, content fingerprint mismatches, and checksum mismatches fail loudly.

## Out-of-Scope Work

Pickle, path normalization, migrations, cache/export/materialized-data manifests, backend canonicalization, and invalidation policy beyond datasource-index content fingerprints.

## Validation Commands

```sh
make test-unit
make test-contract
make test-package
git diff --check
```

## Completion Notes

- Draft plan: completed manager-local draft.
- Final phase execution plan: completed with expanded-path review due durable schema behavior.
- Implementation summary: implemented `DataSourceIndexManifest`, `DataSourceIndexCodec`, entry `from_dict`, deterministic JSON dumps/loads, file dump/load, fingerprints, checksums, and rejection tests.
- Implementation validation: `make test-unit` passed with 360 tests; `make test-contract` passed with 50 tests; `make test-package` passed with 25 tests; `git diff --check` passed.
- Pre-submit blocker gate: passed; no pickle, path normalization, cache/export manifest, or migration framework.
- PR preparation: PR body drafted at `docs/roadmap/stage-5/phases/index-manifest-codec-pr-body.md`; PR #34 opened and verified against `develop`.
- Automated review: manager expanded-path review passed before PR submission; GitHub checks pending/not configured at open.
- Merge result: PR #34 squash-merged to `develop` at `5cffb9fd3d4a853e8121eea56c655181a692898a` on 2026-05-14.
- Cleanup: pending worktree and branch removal after metadata commit.
- Remaining blockers: none.
