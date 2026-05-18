# Summary

- Added Stage 15 data-path pipeline-stage evidence over existing Stage 9 records with `DataPipelineStage`, `DataPipelineStageContext`, and reserved measurement units.
- Added builders that produce existing `DataPathProfile` and `DataPathBenchmark` records from loader state, streaming plans, stage contexts, and reserved measurements.
- Added primitive fake data-quality probe evidence for missing fields, NaN/Inf, mask validity, label distribution, shape/dtype/device drift, and provenance anomalies.
- Added an integration flow tying Stage 9 data-path evidence to BatchOperation equivalence, field effects, replay/provenance, dtype/device, and mask/alignment diagnostics.

# Scientific And Contract Implications

- Stage 15 reuses `StreamingReadPlan`, `DataLoaderState`, `DataPathProfile`, `DataPathBenchmark`, and BatchOperation evidence instead of introducing a competing data abstraction.
- Records are primitive, deterministic, JSON-round-trippable, and threshold-free. No raw dataset benchmark, implicit cache, storage backend, auto-vectorizer, or heavy optional dependency is added.
- Data-quality probes inspect synthetic primitive field mappings and optional metadata only; default validation remains CPU-only and dependency-light.

# Validation

- Focused suite: `uv run pytest tests/contracts/test_data_path_records_contract.py tests/integration/test_stage9_data_path_flow.py tests/integration/test_stage15_data_path_probes_flow.py tests/contracts/test_batch_operations.py tests/integration/test_batch_operations_integration.py tests/package/test_import.py::test_stage_9_datapath_module_exports_only_code_backed_names tests/package/test_import.py::test_stage_5_datasource_names_are_not_parent_or_root_exports` - 17 passed
- Regression check: `uv run pytest tests/contracts/test_data_path_records_contract.py tests/integration/test_stage15_data_path_probes_flow.py` - 8 passed
- `make test-package` - 72 passed
- `make test-unit` - 794 passed
- `make test-contract` - 192 passed
- `make test-integration` - 32 passed
- `make test-summary` - package 72, unit 794, contract 192, integration 32; e2e and acceptance suites not present
- `make validate-pr` - passed
- `uv lock --check` - passed
- `git diff --check` - passed

# Assumptions And Residual Risk

- The new helper records are provisional public surface under `rphys.datasources.datapath`; later real adapters should populate the same primitive records rather than bypassing them.
- Device-transfer and queue evidence remains descriptive in this phase. No actual device movement, loader worker runtime, or performance threshold is implemented.
