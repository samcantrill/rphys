# Phase 5 Execution Plan: Data-Path Pipeline Probes And Batch Evidence

## Metadata

- Status: implemented in isolated phase worktree; validation passed; ready for PR
- Roadmap stage: `v15`
- Feature focus: training performance profiling and data-path optimization
- Stage descriptor: Training Performance Profiling And Data-Path Optimization
- Phase descriptor: Data-Path Pipeline Probes And Batch Evidence
- PR title: `Stage 15 Training Performance Profiling And Data-Path Optimization - Phase 5: Data-Path Pipeline Probes And Batch Evidence`
- Branch: `agent/stage-15-training-profiling-p5-datapath-pipeline-probes-batch-evidence`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p5-datapath-pipeline-probes-batch-evidence`
- Full plan: `docs/roadmap/stage-15/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Dependencies: Phases 1 through 4 are merged into `develop`

## Objective

Extend Stage 15 profiling beyond the native training loop by adding
dependency-light data-path evidence over existing Stage 9 records and existing
BatchOperation contracts. This phase records where data-path observations came
from, which stable pipeline stage produced them, which reserved measurement
keys and units apply, what synthetic data-quality probes observed, and how
BatchOperation equivalence/replay/provenance/dtype/device/mask evidence is
attached to data-path profiles.

## In Scope

- `src/rphys/datasources/datapath.py` owns new provisional data-path evidence:
  `DataPipelineStage`, `DataPipelineStageContext`, reserved measurement units,
  profile/benchmark builders, data-quality issue records, and a deterministic
  fake data-quality probe.
- Reuse `StreamingReadPlan`, `DataLoaderState`, `DataPathProfile`, and
  `DataPathBenchmark`; do not add a second benchmark/profile family.
- Keep records primitive, JSON-round-trippable, threshold-free, and compatible
  with Stage 9 source/cache/prepared/materialization evidence.
- Validate BatchOperation equivalence, field effects, replay/provenance,
  dtype/device, and mask/alignment evidence through Stage 15 integration tests.

## Out Of Scope

- No raw dataset benchmark, machine-speed threshold, implicit cache,
  optimized storage backend, auto-vectorizer, workflow runtime, torch/Lightning
  dependency, or concrete device-transfer implementation.
- No training-core import from datasource modules and no new parent-package
  datasource exports.

## Validation Plan

- Focused data-path and batch tests:
  `uv run pytest tests/contracts/test_data_path_records_contract.py tests/integration/test_stage9_data_path_flow.py tests/integration/test_stage15_data_path_probes_flow.py tests/contracts/test_batch_operations.py tests/integration/test_batch_operations_integration.py`
- Package/import checks: `make test-package`
- Broader phase checks before PR: `make test-unit`, `make test-contract`,
  `make test-integration`, `make test-summary`, `make validate-pr`,
  `uv lock --check`, and `git diff --check`.

## Validation Evidence

- Focused suite passed: `uv run pytest tests/contracts/test_data_path_records_contract.py tests/integration/test_stage9_data_path_flow.py tests/integration/test_stage15_data_path_probes_flow.py tests/contracts/test_batch_operations.py tests/integration/test_batch_operations_integration.py tests/package/test_import.py::test_stage_9_datapath_module_exports_only_code_backed_names tests/package/test_import.py::test_stage_5_datasource_names_are_not_parent_or_root_exports` - 17 passed.
- Regression check passed after shape-drift serialization fix: `uv run pytest tests/contracts/test_data_path_records_contract.py tests/integration/test_stage15_data_path_probes_flow.py` - 8 passed.
- `make test-package` - 72 passed.
- `make test-unit` - 794 passed.
- `make test-contract` - 192 passed.
- `make test-integration` - 32 passed.
- `make test-summary` - package 72, unit 794, contract 192, integration 32; e2e and acceptance suites not present.
- `make validate-pr` - passed.
- `uv lock --check` - passed.
- `git diff --check` - passed.

## Implementation Notes

- `DataPipelineStage` mirrors Stage 15 training probe stage strings where the
  data-path and training hook vocabularies overlap; queue-wait remains a
  data-path-only diagnostic stage.
- `DataPipelineStageContext` records fingerprints and attribution only. It
  references Stage 9 objects by their primitive fingerprints and never owns
  sample loading, cache lookup, prepared reading, or device transfer.
- `FakeDataQualityProbe` inspects primitive field mappings and optional field
  metadata, so default tests remain CPU-only and dependency-light.
