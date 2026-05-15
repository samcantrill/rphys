# Phase 2 Execution Plan: OperationStep Selection Preflight

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v8`
- Feature focus: no-write export codec selection
- Stage descriptor: Save/Export Ops And Derived DataSources
- Phase descriptor: OperationStep Selection Preflight
- PR title: `Stage 8 Save/Export Ops And Derived DataSources - Phase 2: OperationStep Selection Preflight`
- Branch: `agent/stage-8-p2-selection-preflight`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-8-p2-selection-preflight`
- Phase execution plan path: `docs/roadmap/stage-8/phases/selection-preflight.md`
- Full plan: `docs/roadmap/stage-8/implementation-plan.md`
- Planning document: `docs/roadmap/stage-8/planning.md`
- Source phase: Phase 2
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

Add public no-write `CodecSelectionOperation` as an `OperationStep`
implementation. Selection validates requested runtime fields, deterministic
targets, codec support, schema requests, and metadata-save policy compatibility,
then returns typed in-memory selection evidence in `OperationResult.output`.

## Full-Plan Context

Phase 1 records are merged. This phase must not call codec `save`, write files,
link/copy resources, create manifests, scan output directories, or implement
`SaveOperation`. Phase 3 owns side-effecting saves.

## Scope Contract

`CodecSelectionOperation` is pure and returns `OperationResult`. It may call
`CodecRegistry.resolve_save` to prove a unique save-capable codec, but it must
not call `CodecRegistry.save` or codec `save`. Selection evidence is
process-local and is not a durable schema.

## Implementation Steps

1. Add minimal `RecordExportRequest`, `SelectedFieldExport`, and
   `ExportSelection` records under `rphys.ops.export`.
2. Implement `CodecSelectionOperation` with a pure `OperationContract`.
3. Add unit tests for no-write behavior and selection failures.
4. Add contract tests for `OperationStep`, `OperationPipeline`, and
   `OperationResult` compatibility.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/contracts/test_export_operation_contract.py tests/unit/rphys/ops/test_export_selection.py
uv run pytest tests/unit/rphys/ops/test_core.py tests/unit/rphys/ops/test_pipelines.py
make test-contract
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
- Final phase execution plan: scope-complete for Phase 2.
- Implementation summary: added `RecordExportRequest`,
  `SelectedFieldExport`, `ExportSelection`, and pure
  `CodecSelectionOperation` as a public `OperationStep` implementation.
- Implementation validation: targeted selection/unit contract tests,
  operation core/pipeline regressions, `make test-contract`,
  `make test-package`, `make validate-pr`, `make test-summary`, and
  `git diff --check` passed locally.
- Pre-submit blocker gate: passed; selection calls `CodecRegistry.resolve_save`
  only and does not call codec `save`, write files, link/copy resources, scan
  outputs, create manifests, or implement `SaveOperation`.
- PR preparation: pending.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
