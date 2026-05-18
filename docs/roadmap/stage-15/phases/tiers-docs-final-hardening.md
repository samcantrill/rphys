# Phase 8 Execution Plan: Tiers, Documentation, And Final Hardening

## Metadata

- Status: implemented in isolated phase worktree; validation passed; ready for PR
- Roadmap stage: `v15`
- Feature focus: training performance profiling and data-path optimization
- Stage descriptor: Training Performance Profiling And Data-Path Optimization
- Phase descriptor: Tiers, Documentation, And Final Hardening
- PR title: `Stage 15 Training Performance Profiling And Data-Path Optimization - Phase 8: Tiers, Documentation, And Final Hardening`
- Branch: `agent/stage-15-training-profiling-p8-tiers-docs-final-hardening`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p8-tiers-docs-final-hardening`
- Full plan: `docs/roadmap/stage-15/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Dependencies: Phases 1 through 7 are merged into `develop`

## Objective

Close the Stage 15 public contract with descriptive experiment tiers, restart
snapshots, public examples, glossary updates, package export checks, and broad
validation. The new records are evidence only: downstream projects or `loom`
may orchestrate using them, but `rphys` does not schedule work, manage
artifacts, create dashboards, or define performance thresholds.

## In Scope

- `rphys.training.tiers` defines `ExperimentTierName`,
  `ExperimentTierSpec`, `RestartCompatibilityStatus`, `RestartState`, and
  `default_experiment_tiers()`.
- Standard tiers cover debug, smoke, signal, comparison, and full breadths
  while requiring the same execution path.
- `RestartState` links checkpoint identity to loader, materialization,
  data-path, profile, checkpoint, completion-marker, and compatibility
  evidence.
- Public training package exports and import-boundary tests include the tier
  module.
- Stage 15 examples cover Native, Lightning, data-path/probe, tier, and
  restart evidence.
- Glossary and test documentation clarify the public terms and boundaries.

## Out Of Scope

- No scheduler, workflow runtime, retry engine, job queue, cost dashboard,
  artifact store, storage backend, default checkpoint writer, or concrete
  optimized storage backend is introduced.
- No alternate fake-only debug path, machine-speed threshold, real dataset
  benchmark, mandatory Lightning/GPU/system probe, raw framework timeline,
  tensor capture, checkpoint payload schema, or artifact lifecycle is added.

## Validation Plan

- Focused tier/restart/package/import suite:
  `uv run pytest tests/unit/rphys/training/test_tiers.py tests/contracts/test_stage15_tier_restart_contract.py tests/package/test_import.py::test_stage_12_training_package_exports_only_code_backed_contract_names tests/package/test_import.py::test_stage_12_training_modules_export_only_code_backed_names tests/package/test_import_boundaries.py::test_stage_12_training_imports_do_not_load_frameworks_or_datasources`
- Broad closeout checks: `make test-package`, `make test-unit`,
  `make test-contract`, `make test-integration`, `make test-summary`,
  `make validate-pr`, `uv lock --check`, and `git diff --check`.
- Optional installed-Lightning acceptance remains environment-dependent; record
  absent or unsafe preflight evidence if unavailable.

## Validation Evidence

- Focused tier/restart/package/import suite passed:
  `uv run pytest tests/unit/rphys/training/test_tiers.py tests/contracts/test_stage15_tier_restart_contract.py tests/package/test_import.py::test_stage_12_training_package_exports_only_code_backed_contract_names tests/package/test_import.py::test_stage_12_training_modules_export_only_code_backed_names tests/package/test_import_boundaries.py::test_stage_12_training_imports_do_not_load_frameworks_or_datasources` - 10 passed.
- Optional installed-Lightning preflight:
  `uv run python -c 'from rphys.training.lightning import preflight_lightning_dependency; p=preflight_lightning_dependency(); print(p.status.value, p.package_name, p.version, p.reason)'` -
  reported `absent`, so real installed-Lightning acceptance was skipped
  without importing Lightning.
- `make test-package` - 72 passed.
- `make test-unit` - 808 passed.
- `make test-contract` - 195 passed.
- `make test-integration` - 32 passed.
- `make test-summary` - package 72, unit 808, contract 195, integration 32;
  e2e and acceptance suites not present.
- `make validate-pr` - passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv lock --check` - passed.
- `git diff --check` - passed.

## Implementation Notes

- `ExperimentTierSpec.same_execution_path` must be true. The record can
  describe smaller or larger scale, expected evidence, and fingerprints; it
  cannot describe a substitute fake path.
- `RestartState` requires a checkpoint ref or checkpoint ref id, at least one
  completion marker, and a compatibility note.
- Restart compatibility is explicit through `compatible`, `incompatible`,
  `ambiguous`, or `unavailable` status rather than inferred from file presence.
- Metadata and provenance remain primitive mappings so records can be inspected
  and serialized without pulling framework or storage dependencies into
  training imports.
