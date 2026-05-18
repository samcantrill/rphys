# Summary

- Added optional `rphys.training.lightning` public surface with metadata-only Lightning preflight before importing `lightning.pytorch`.
- Added bounded `LightningTrainerConfig`, direct LightningModule/DataModule entrypoints, and `LightningTrainingEngine` for the shared `Trainer(engine=...)` path.
- Added precision/compile/kernel policy mapping evidence: precision maps to public Lightning `Trainer(precision=...)`; compile and kernel policies record explicit unsupported state for the Phase 6 public-Trainer boundary.
- Added fake-Lightning tests and package import checks proving base training imports do not load Lightning, torch, CUDA/NVML, or profiler stacks.

# Scientific And Contract Implications

- Outputs stay shared `TrainingResult`/`TrainingProfile` records; no Lightning-specific result family is introduced.
- Lightning-specific inputs are isolated to `rphys.training.lightning`; parent `rphys.training` exports remain unchanged.
- Security preflight is intentionally conservative after `GHSA-w37p-236h-pfx3`: versions greater than `2.6.1` are blocked by default until official advisory evidence is refreshed.
- Compile/kernel requests are preserved as policy evidence instead of silently pretending Lightning exposes public Trainer settings for them.

# Validation

- Focused suite: `uv run pytest tests/unit/rphys/training/test_lightning.py tests/unit/rphys/training/test_policies.py tests/package/test_import.py::test_stage_12_training_modules_export_only_code_backed_names tests/package/test_import_boundaries.py::test_stage_12_training_imports_do_not_load_frameworks_or_datasources` - 12 passed
- Optional installed-Lightning preflight - reported `absent`; real installed-Lightning smoke skipped without importing Lightning
- `make test-package` - 72 passed
- `make test-unit` - 801 passed
- `make test-contract` - 192 passed
- `make test-integration` - 32 passed
- `make test-summary` - package 72, unit 801, contract 192, integration 32; e2e and acceptance suites not present
- `make validate-pr` - passed
- `uv lock --check` - passed
- `git diff --check` - passed

# Assumptions And Residual Risk

- Phase 6 intentionally stops before callback/profiler/checkpoint/probe bridge work; Phase 7 owns those translations.
- The current advisory still marks `>=2.6.2` affected and `2.6.1` patched. The allowlist should be refreshed before running a future installed-Lightning acceptance against later versions.
