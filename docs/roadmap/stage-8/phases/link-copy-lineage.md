# Phase 4 Execution Plan: Link/Copy Lineage And Private Local Helpers

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v8`
- Feature focus: explicit link/copy outcomes and lineage
- Stage descriptor: Save/Export Ops And Derived DataSources
- Phase descriptor: Link/Copy Lineage And Private Local Helpers
- PR title: `Stage 8 Save/Export Ops And Derived DataSources - Phase 4: Link/Copy Lineage And Private Local Helpers`
- Branch: `agent/stage-8-p4-link-copy-lineage`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-8-p4-link-copy-lineage`
- Phase execution plan path: `docs/roadmap/stage-8/phases/link-copy-lineage.md`
- Full plan: `docs/roadmap/stage-8/implementation-plan.md`
- Planning document: `docs/roadmap/stage-8/planning.md`
- Source phase: Phase 4
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: dedicated branch/worktree/PR to `develop`
- Plan quality gate: passed in implementation plan review
- Draft pass: manager-local fast path
- Refine pass: not needed unless targeted validation exposes a blocker
- Setup limitations: existing unrelated control-checkout `docs/roadmap.md` changes were not copied
- Blockers: none

## Objective

Implement explicit local-file link/copy materialization under the export
operation path, preserving ordered source/target `ResourceRef` lineage in
`FieldExportResult` while keeping helpers private and rejecting unsupported
storage behavior loudly.

## Full-Plan Context

Phases 1 through 3 are merged. This phase extends `SaveOperation` for link/copy
policy behavior only. It must not expose storage adapter protocols, cloud/object
storage support, codec-only hidden link/copy, or derived datasource assembly.

## Scope Contract

Link/copy requires one-to-one ordered source and target resources, local file
protocol on both sides, and explicit fallback when symlink creation fails.
Silent symlink-to-copy fallback is not allowed. Fallback results count as
copied, not linked.

## Implementation Steps

1. Add private local link/copy helpers inside `rphys.ops.export`.
2. Route `SaveOperation` link/copy materialization through those helpers.
3. Preserve public lineage evidence in `FieldExportResult`.
4. Add unit/package tests for outcomes, lineage, fallback, unsupported protocols, and private helpers.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/ops/test_export_lineage.py tests/unit/rphys/ops/test_export_local_links.py
make test-package
make test-unit
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Completion Notes

- Draft plan: completed manager-local fast path.
- Final phase execution plan: scope-complete for Phase 4.
- Implementation summary: added private local-file link/copy helpers and routed
  `SaveOperation` link/copy policies through them while preserving public
  ordered source/target `ResourceRef` lineage in `FieldExportResult`.
- Implementation validation: targeted lineage/local-link tests,
  `make test-package`, `make test-unit`, `make validate-pr`,
  `make test-summary`, and `git diff --check` passed locally.
- Pre-submit blocker gate: passed; helpers remain private, unsupported and
  cross-protocol behavior fails loudly, symlink fallback is explicit, and no
  public storage adapter/protocol or derived assembly is present.
- PR preparation: pending.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
