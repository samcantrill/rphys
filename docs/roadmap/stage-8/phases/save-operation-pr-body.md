# Stage 8 Save/Export Ops And Derived DataSources - Phase 3: SaveOperation Through Codec Save And Idempotency

## Summary

- Added side-effecting `SaveOperation` as a public `OperationStep`
  implementation consuming `ExportSelection`.
- Saves selected fields only through
  `CodecRegistry.save(value, SaveContext(target=FieldRef, metadata_policy=...))`.
- Records typed `FieldExportResult` and `RecordExportResult` evidence for
  written, skipped, replaced, and failed outcomes.
- Implements fail-by-default existing-target behavior plus explicit skip,
  replace, and partial-field-failure continuation policy.

## Scientific And Contract Notes

- `SaveContext` remains datasource/export neutral. Source record provenance and
  codec save evidence are joined in export result records outside the codec
  layer.
- `SaveOperation` supports write materialization in this phase. Link/copy
  execution remains deferred to Phase 4 and fails loudly if requested here.
- Target existence checks are local-file-only idempotency checks used before
  codec writes; they are not fingerprint inputs, manifests, or output rescans.
- Default codec failures abort. Failed field result evidence is produced only
  under explicit `continue_on_field_error=True`.

## Validation

- `uv run pytest tests/unit/rphys/ops/test_export_save.py tests/contracts/test_export_codec_contract.py tests/contracts/test_export_operation_contract.py` passed: 13 tests.
- `uv run pytest tests/contracts/test_codec_contract.py` passed: 5 tests.
- `make test-unit` passed: 536 tests.
- `make test-contract` passed: 96 tests.
- `make test-package` passed: 34 tests.
- `make validate-pr` passed, including `uv lock --check`, suite summary, package build, and `git diff --check`.
- `make test-summary` passed overall: package 34, unit 536, contract 96, integration 11.

## Risks And Follow-Ups

- Local-file target existence checks are intentionally narrow for Phase 3.
  Phase 4 owns explicit link/copy local helpers, lineage behavior, and
  unsupported protocol failures.
- Phase 5 owns derived datasource assembly from successful export evidence.
