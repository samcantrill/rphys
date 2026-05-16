# Stage 11 Loss, Objective, And Metric Contracts - Phase 5: Sample Collections And Pre-Metric Views

## Summary

- Added `SampleCollection`, `SampleCollector`, `SampleCollectionViewPlan`,
  structural `SampleCollectionView`, and `PlannedSampleCollectionView`.
- Exported sample collection contracts from `rphys.data`.
- Added unit and contract tests for value iteration, entry metadata,
  fail-loud collection, explicit skip diagnostics, grouping, sorting, selected
  fields, fake stitching, and no source mutation.

## Scientific And Design Contract

- Sample collections iterate over `Sample` values while preserving
  `CollectionItem[Sample]` metadata/provenance for `subject_id`, `record_id`,
  `sample_id`, windows, splits, and source tracking.
- Collectors fail loudly by default; skipped samples require explicit policy and
  diagnostics.
- Pre-metric stitching is descriptor-driven and fake/injected only. No concrete
  physiological reconstruction, resampling, interpolation, filtering, datasource
  runner, evaluator, report, or export behavior was added.
- Views return `SampleCollection` snapshots, not a new view-result family.

## Validation

- `uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/data/test_sample_collections.py tests/contracts/test_sample_collection_contract.py tests/package/test_import.py tests/package/test_import_boundaries.py` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-unit` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-contract` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-package` passed.
- `git diff --check` passed.

## Residual Risk

- Stage 13 still owns evaluator runner policy, concrete reconstruction
  algorithms, report/dataframe adapters, and any first-class sample identity
  fields.
