# Stage 8 Save/Export Ops And Derived DataSources - Phase 1: Export Primitives, Layout, Policy, And Result Records

## Summary

- Added `rphys.ops.export` data-only Stage 8 records for export specs, targets,
  output layouts, policies, outcomes, field/record/export results, and
  in-memory reports.
- Implemented deterministic target `FieldRef` derivation and stable
  schema-versioned export fingerprints over approved primitive inputs.
- Added focused unit, contract, and package import checks for idempotency
  vocabulary, result/report aggregation, no root exports, no shorthand aliases,
  and no public report serialization helpers.

## Scientific And Contract Notes

- Target identity is explicit and inspectable from source datasource/record/field
  identity, export id, layout version, target root, and the export spec
  fingerprint.
- Fingerprints include requested fields, codec/schema requests,
  metadata-save policy, layout version, resource suffix, and output options.
  They exclude target roots/resources, existence checks, timestamps, codec
  registry identity/order, Python object identity, and workflow/runtime state.
- Reports remain typed in-memory evidence only. No `to_dict`, JSON, report-file
  schema, cache key, materialization manifest, selection operation, save
  operation, link/copy helper, or derived datasource assembly is introduced.

## Validation

- `uv run pytest tests/unit/rphys/ops/test_export_layout.py tests/unit/rphys/ops/test_export_policy.py tests/unit/rphys/ops/test_export_results.py` passed: 16 tests.
- `uv run pytest tests/contracts/test_export_result_contract.py` passed: 1 test.
- `make test-package` passed: 34 tests.
- `make validate-pr` passed, including `uv lock --check`, suite summary, package build, and `git diff --check`.
- `make test-summary` passed overall: package 34, unit 519, contract 92, integration 11.

## Risks And Follow-Ups

- `ExportSpec.codec_requests` is recorded as primitive request identity; Phase 2
  owns the concrete no-write codec-selection checks against `CodecRegistry`.
- Phase 3 owns side-effecting save execution and partial-failure policy
  behavior. Phase 4 owns private local link/copy helpers. Phase 5 owns derived
  datasource assembly.
