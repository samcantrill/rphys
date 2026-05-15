# Stage 8 Save/Export Ops And Derived DataSources - Phase 2: OperationStep Selection Preflight

## Summary

- Added `RecordExportRequest`, `SelectedFieldExport`, and `ExportSelection`
  as typed in-memory request/selection records under `rphys.ops.export`.
- Added pure `CodecSelectionOperation` as a public `OperationStep`
  implementation returning `OperationResult.output`.
- Validates requested field presence, deterministic target derivation,
  schema request compatibility, metadata-save policy support, codec request
  matching, and unique save-capable codec resolution without writing.

## Scientific And Contract Notes

- Selection is preflight/planning only: it calls `CodecRegistry.resolve_save`
  and never calls codec `save`, link/copy helpers, manifest writers, datasource
  scans, or filesystem writes.
- Selection evidence records source fields, loaded `FieldValue`s, target
  `FieldRef`s, metadata policy, and diagnostic codec names. It is not a durable
  wire schema.
- `OperationPipeline([selection, downstream])` forwards `.output` normally,
  preserving the Stage 7 `OperationStep`/`OperationResult` contract.

## Validation

- `uv run pytest tests/contracts/test_export_operation_contract.py tests/unit/rphys/ops/test_export_selection.py` passed: 10 tests.
- `uv run pytest tests/unit/rphys/ops/test_core.py tests/unit/rphys/ops/test_pipelines.py` passed: 40 tests.
- `make test-contract` passed: 94 tests.
- `make test-package` passed: 34 tests.
- `make validate-pr` passed, including `uv lock --check`, suite summary, package build, and `git diff --check`.
- `make test-summary` passed overall: package 34, unit 527, contract 94, integration 11.

## Risks And Follow-Ups

- `codec_name` is diagnostic in-memory evidence, not a durable codec registry
  schema.
- Phase 3 owns `SaveOperation`, actual codec save calls, idempotency checks
  against filesystem state, and partial-failure behavior.
