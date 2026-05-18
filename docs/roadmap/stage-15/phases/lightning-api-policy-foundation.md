# Phase 6 Execution Plan: Lightning API And Policy Foundation

## Metadata

- Status: implemented in isolated phase worktree; validation passed; ready for PR
- Roadmap stage: `v15`
- Feature focus: training performance profiling and data-path optimization
- Stage descriptor: Training Performance Profiling And Data-Path Optimization
- Phase descriptor: Lightning API And Policy Foundation
- PR title: `Stage 15 Training Performance Profiling And Data-Path Optimization - Phase 6: Lightning API And Policy Foundation`
- Branch: `agent/stage-15-training-profiling-p6-lightning-api-policy-foundation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p6-lightning-api-policy-foundation`
- Full plan: `docs/roadmap/stage-15/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Dependencies: Phases 1 through 5 are merged into `develop`

## Objective

Add an optional Lightning integration foundation without making Lightning,
torch, CUDA/NVML, or profiler packages part of base training imports. This
phase introduces the public `rphys.training.lightning` surface, dependency
preflight before import, bounded public Trainer keyword arguments, shared
`TrainingEngine` delegation through `LightningTrainingEngine`, direct
LightningModule/DataModule entrypoints, and precision/compile/kernel policy
mapping evidence.

## Official Lightning And Security Evidence

Evidence was refreshed on 2026-05-18 before code work:

- Lightning Trainer stable docs for 2.6.1 show `Trainer` owns callbacks,
  checkpointing, precision, profiler, `fit(..., ckpt_path=...)`,
  `validate`, `test`, and `predict` public methods:
  https://lightning.ai/docs/pytorch/stable/common/trainer.html
- Lightning callback docs list public setup/teardown, exception, checkpoint,
  backward, and optimizer-step hooks for the Phase 7 bridge:
  https://lightning.ai/docs/pytorch/latest/extensions/callbacks.html
- GitHub security advisory `GHSA-w37p-236h-pfx3` was published on
  2026-04-30 and last updated on 2026-05-12. It marks PyTorch Lightning
  package versions `>=2.6.2` as affected, lists `2.6.1` as the patched
  version, identifies `2.6.2` and `2.6.3` as affected, and recommends
  deleting affected versions and pinning to `2.6.1`:
  https://github.com/Lightning-AI/pytorch-lightning/security/advisories/GHSA-w37p-236h-pfx3

Phase 6 therefore checks package metadata before importing `lightning.pytorch`
and blocks versions greater than `2.6.1` by default until the advisory is
refreshed.

## In Scope

- `src/rphys/training/lightning.py` defines dependency preflight records,
  `LightningTrainerConfig`, policy mapping records, direct LightningModule
  entrypoints, and `LightningTrainingEngine`.
- Fake-Lightning tests validate the API without installing or importing real
  Lightning.
- `PrecisionPolicy` maps onto public Lightning `Trainer(precision=...)` values
  where possible.
- `CompilePolicy` and `KernelPolicy` produce explicit unsupported evidence
  because Phase 6 uses public Trainer kwargs only and Lightning does not expose
  direct Trainer kwargs for those choices.
- Base `rphys.training` imports remain unchanged; Lightning-specific inputs
  stay under `rphys.training.lightning`.

## Out Of Scope

- No full callback/profiler/checkpoint/probe bridge. Phase 7 owns callback
  normalization, profiler spans, checkpoint retention/restart mapping, model
  probes, data probes, resource monitors, rank attribution, and async writer
  interaction.
- No Lightning or torch dependency is added to the package.
- No raw Lightning trainer state, raw Lightning profiler object, private loop
  state, checkpoint payload, or tensor capture is exposed as public rphys
  evidence.

## Validation Plan

- Focused fake-Lightning and policy tests:
  `uv run pytest tests/unit/rphys/training/test_lightning.py tests/unit/rphys/training/test_policies.py tests/package/test_import.py::test_stage_12_training_modules_export_only_code_backed_names tests/package/test_import_boundaries.py::test_stage_12_training_imports_do_not_load_frameworks_or_datasources`
- Package/import checks: `make test-package`
- Broader phase checks before PR: `make test-unit`, `make test-contract`,
  `make test-integration`, `make test-summary`, `make validate-pr`,
  `uv lock --check`, and `git diff --check`.

## Validation Evidence

- Focused fake-Lightning suite passed:
  `uv run pytest tests/unit/rphys/training/test_lightning.py tests/unit/rphys/training/test_policies.py tests/package/test_import.py::test_stage_12_training_modules_export_only_code_backed_names tests/package/test_import_boundaries.py::test_stage_12_training_imports_do_not_load_frameworks_or_datasources` - 12 passed.
- Optional installed-Lightning preflight:
  `uv run python -c 'from rphys.training.lightning import preflight_lightning_dependency; p=preflight_lightning_dependency(); print(p.status.value, p.package_name, p.version, p.reason)'` -
  reported `absent`, so real installed-Lightning smoke was skipped without
  importing Lightning.
- `make test-package` - 72 passed.
- `make test-unit` - 801 passed.
- `make test-contract` - 192 passed.
- `make test-integration` - 32 passed.
- `make test-summary` - package 72, unit 801, contract 192, integration 32;
  e2e and acceptance suites not present.
- `make validate-pr` - passed.
- `uv lock --check` - passed.
- `git diff --check` - passed.

## Implementation Notes

- `preflight_lightning_dependency()` reads package metadata for `lightning` and
  `pytorch-lightning` before import. Unsafe and absent dependencies produce
  shared `TrainingResult` failure evidence rather than importing and failing
  after arbitrary package code runs.
- `LightningTrainingEngine` can be used through `Trainer(engine=...)` and
  wraps an rphys `Learner` in a runtime-created LightningModule only after a
  safe preflight succeeds.
- Direct `fit_lightning_module`, `validate_lightning_module`,
  `test_lightning_module`, and `predict_lightning_module` entrypoints accept
  Lightning-native model/data inputs and return shared `TrainingResult`
  records.
- `LightningTrainerConfig` intentionally accepts only a bounded allowlist of
  public Trainer kwargs from the official Trainer docs.
