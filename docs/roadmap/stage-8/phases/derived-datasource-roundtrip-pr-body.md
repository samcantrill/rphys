# Stage 8 Save/Export Ops And Derived DataSources - Phase 5: Descriptor-Only Derived Datasource Assembly And Final Synthetic Round Trip

## Summary

- Added descriptor-only `rphys.datasources.derived` with
  `DerivedDataSourceAssembly` and `DerivedDataSourceBuilder`.
- Assembled derived `DataSourceRef` and ordered `RecordRef`s from successful
  `FieldExportResult` evidence without scanning output directories.
- Preserved source descriptor provenance and actual exported target resources,
  including codec-returned resources.
- Added the final synthetic vertical slice from source datasource/sample export
  through save, derived datasource assembly, index construction, and lazy sample
  reload.

## Scientific And Contract Notes

- Derived assembly is descriptor-only. It does not save fields, execute export
  operations, write manifests, reuse `DataSourceIndexManifest`, or inspect
  output directories.
- Failed field exports are excluded from derived records. Explicit skipped
  fields are treated as usable existing-target evidence because the target
  resource was intentionally not rewritten.
- Source descriptors remain immutable evidence; derived records carry explicit
  `derived.source_datasource_id`, `derived.source_record_id`, and
  `derived.field_count` metadata.
- Prediction-like outputs remain ordinary exported fields and reload through
  the existing `IndexBuilder` and `SampleBuilder` path.

## Validation

- `uv run pytest tests/unit/rphys/datasources/test_derived.py tests/integration/test_stage8_export_derived_datasource_flow.py` passed: 9 tests.
- `uv run pytest tests/integration/test_stage5_synthetic_datasource_flow.py` passed: 1 test.
- `make test-integration` passed: 12 tests.
- `make test-package` passed: 35 tests.
- `make test` passed: 695 tests.
- `rg -n "SaveOp|CodecSelectionOp|to_dict|JSON|DataSourceIndexManifest|report file" docs src tests` produced only existing descriptor/index serialization, existing roadmap deferrals, and full-name operation references/shorthand substrings; no new forbidden Stage 8 surface was added.
- `make validate-pr` passed, including `uv lock --check`, suite summary,
  package build, and `git diff --check`.
- `make test-summary` passed overall: package 35, unit 552, contract 96,
  integration 12.
- `git diff --check` passed.

## Risks And Follow-Ups

- Stage 8 still defers durable derived datasource manifest schemas and any
  cross-process derived manifest file interchange until Stage 9/15 or
  downstream pressure requires it.
- Storage adapter protocols, cache/materialization manifests, prediction
  runners, evaluation metrics, and analysis reports remain out of scope.
