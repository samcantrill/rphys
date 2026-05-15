# Stage 8 Save/Export Ops And Derived DataSources - Phase 4: Link/Copy Lineage And Private Local Helpers

## Summary

- Added private local-file link/copy helpers inside `rphys.ops.export`.
- Routed `SaveOperation` link/copy materialization policies through those
  helpers.
- Preserved ordered source and target `ResourceRef` lineage in
  `FieldExportResult`.
- Added fail-loud behavior for one-to-one lineage mismatches, unsupported
  protocols, cross-protocol link/copy, missing source paths, and symlink failure
  without explicit fallback.

## Scientific And Contract Notes

- Link/copy outcomes are distinct from codec writes. New link/copy operations
  count as `linked` or `copied`; explicit symlink-to-copy fallback counts as
  `copied`, not `linked`.
- Helper implementation is private and local-filesystem-only. No public storage
  adapter/protocol, cloud/object storage claim, codec context change, or hidden
  fallback is introduced.
- Source/target lineage is public result evidence and does not rely on target
  files being rescanned later.

## Validation

- `uv run pytest tests/unit/rphys/ops/test_export_lineage.py tests/unit/rphys/ops/test_export_local_links.py` passed: 8 tests.
- `make test-package` passed: 34 tests.
- `make test-unit` passed: 544 tests.
- `make validate-pr` passed, including `uv lock --check`, suite summary, package build, and `git diff --check`.
- `make test-summary` passed overall: package 34, unit 544, contract 96, integration 11.

## Risks And Follow-Ups

- Local symlink support is platform-dependent. Tests include explicit fallback
  behavior by forcing symlink failure.
- Phase 5 owns descriptor-only derived datasource assembly from successful
  export results.
