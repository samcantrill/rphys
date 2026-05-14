## Summary

- Add canonical `rphys.data.sample_builders` with `SampleBuildContext`,
  `SampleBuilder`, `SampleFieldProvenance`, and `SampleProbeResult`.
- Build all, subset, and one requested lazy `SampleField` handles from one
  `IndexItem`, with atomic missing-request validation, optional eager loading,
  `build_one` exactly-one input validation, and probe without load.
- Preserve builder-side provenance on built handles while keeping
  `LoadContext` datasource-neutral and package imports lightweight.

## Scientific Contract

- Role-qualified `FieldLocator`s are preserved in request order and are not
  collapsed into intrinsic `DataKey`s.
- `IndexItem.record`, item metadata, `FieldView.field_index`,
  `FieldRef.metadata`, schema, and ordered resources stay inspectable through
  builder/probe/handle provenance without adding record or item fields to codec
  contexts.
- Unsupported indexed views still fail through codec registry typed errors; no
  hidden full-load fallback, datasource scan, cache, split, member, alignment,
  fingerprint, or export semantics are added.

## Validation

- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_sample_builders.py tests/unit/rphys/data/test_sample_fields.py tests/contracts/test_lazy_sample_builder_contract.py tests/contracts/test_lazy_sample_field_contract.py tests/package/test_import.py tests/package/test_import_boundaries.py`
  - 51 passed
- `make test-package`
  - 22 passed
- `make test-unit`
  - 309 passed
- `make test-contract`
  - 38 passed
- `make validate-pr`
  - lock check passed
  - package 22, unit 310, contract 38, integration 1 passed
  - build passed
  - `git diff --check` passed
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_sample_builders.py tests/contracts/test_lazy_sample_builder_contract.py`
  - 16 passed after review fix
- `make test-summary`
  - package 22, unit 310, contract 38, integration 1 passed
- `git diff --check origin/develop...HEAD`
  - passed

## Residual Risk

- No integration vertical slice was added; focused unit and contract coverage
  directly exercises the `IndexItem` -> `CodecRegistry` -> `SampleField` ->
  `Sample` bridge.
- Phase 5 still owns closeout docs/examples and final validation hardening.
