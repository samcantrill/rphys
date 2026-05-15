# Phase 3 Execution Plan: SaveOperation Through Codec Save And Idempotency

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v8`
- Feature focus: side-effecting export saves through codecs
- Stage descriptor: Save/Export Ops And Derived DataSources
- Phase descriptor: SaveOperation Through Codec Save And Idempotency
- PR title: `Stage 8 Save/Export Ops And Derived DataSources - Phase 3: SaveOperation Through Codec Save And Idempotency`
- Branch: `agent/stage-8-p3-save-operation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-8-p3-save-operation`
- Phase execution plan path: `docs/roadmap/stage-8/phases/save-operation.md`
- Full plan: `docs/roadmap/stage-8/implementation-plan.md`
- Planning document: `docs/roadmap/stage-8/planning.md`
- Source phase: Phase 3
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

Add side-effecting `SaveOperation` as a public `OperationStep` implementation
that consumes `ExportSelection`, writes fields only through
`CodecRegistry.save(value, SaveContext(target=FieldRef, metadata_policy=...))`,
applies explicit write idempotency behavior, and returns typed
`RecordExportResult` evidence.

## Full-Plan Context

Phases 1 and 2 are merged. This phase owns codec saves and idempotency for write
materialization only. Link/copy execution, lineage helper behavior, and derived
datasource assembly remain out of scope for later phases.

## Scope Contract

`SaveOperation` must not broaden `SaveContext`, mutate datasource descriptors,
write manifests, serialize reports, add retry/resume workflow semantics, or
perform link/copy materialization. Per-field codec failures abort by default and
become failed-result evidence only under explicit `continue_on_field_error`.

## Implementation Steps

1. Add `SaveOperation` with side-effecting `OperationContract`.
2. Implement write-only idempotency behavior for fail, skip, replace, and write.
3. Preserve `CodecSaveResult` evidence in `FieldExportResult`.
4. Add unit/contract tests for pipeline forwarding, codec save context, and failure behavior.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/ops/test_export_save.py tests/contracts/test_export_codec_contract.py tests/contracts/test_export_operation_contract.py
uv run pytest tests/contracts/test_codec_contract.py
make test-unit
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
- Final phase execution plan: scope-complete for Phase 3.
- Implementation summary: added side-effecting `SaveOperation` that consumes
  `ExportSelection`, applies write idempotency, calls `CodecRegistry.save`
  through `SaveContext(target=FieldRef, metadata_policy=...)`, and returns
  typed `RecordExportResult` evidence.
- Implementation validation: targeted save/unit/contract tests, existing codec
  contract, `make test-unit`, `make test-contract`, `make test-package`,
  `make validate-pr`, `make test-summary`, and `git diff --check` passed
  locally.
- Pre-submit blocker gate: passed; no codec API broadening, datasource
  mutation, manifest writing, report serialization, link/copy execution,
  workflow retry/resume semantics, or derived assembly are present.
- PR preparation: pending.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
