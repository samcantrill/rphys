# Phase 7 Execution Plan: Lightning Observability, Checkpoint, And Probe Bridges

## Metadata

- Status: implemented in isolated phase worktree; validation passed; ready for PR
- Roadmap stage: `v15`
- Feature focus: training performance profiling and data-path optimization
- Stage descriptor: Training Performance Profiling And Data-Path Optimization
- Phase descriptor: Lightning Observability, Checkpoint, And Probe Bridges
- PR title: `Stage 15 Training Performance Profiling And Data-Path Optimization - Phase 7: Lightning Observability, Checkpoint, And Probe Bridges`
- Branch: `agent/stage-15-training-profiling-p7-lightning-observability-checkpoint-bridges`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p7-lightning-observability-checkpoint-bridges`
- Full plan: `docs/roadmap/stage-15/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Dependencies: Phases 1 through 6 are merged into `develop`

## Objective

Normalize Lightning lifecycle, profiler, checkpoint, rank, model/data probe,
resource monitor, and async writer behavior into shared rphys records without
adding Lightning, torch, CUDA/NVML, or system profiler imports to base
training modules. The bridge remains isolated under
`rphys.training.lightning` and returns shared `TrainingResult` and
`TrainingProfile` evidence instead of a Lightning-specific result family.

## Official Lightning And Security Evidence

Evidence was refreshed on 2026-05-18 before Phase 7 code work:

- Lightning Trainer 2.6.1 docs expose public `Trainer` methods and
  `ckpt_path` behavior, including checkpoint callback discovery:
  https://lightning.ai/docs/pytorch/stable/api/lightning.pytorch.trainer.trainer.Trainer.html
- Lightning callback docs list public lifecycle, exception, checkpoint,
  backward, batch, and optimizer-step hooks:
  https://lightning.ai/docs/pytorch/latest/extensions/callbacks.html
- Lightning `ModelCheckpoint` 2.6.1 docs expose public kwargs for
  `monitor`, `mode`, `save_top_k`, `save_last`, `save_on_exception`,
  `every_n_train_steps`, `every_n_epochs`, and `train_time_interval`:
  https://lightning.ai/docs/pytorch/stable/api/lightning.pytorch.callbacks.ModelCheckpoint.html
- Lightning `Profiler` 2.6.1 docs expose public `setup`, `start`, `stop`,
  `teardown`, `describe`, and `profile(action_name)` behavior:
  https://lightning.ai/docs/pytorch/stable/api/lightning.pytorch.profilers.Profiler.html
- GitHub security advisory `GHSA-w37p-236h-pfx3` remains the active
  dependency blocker for unsafe Lightning package versions; Phase 7 keeps the
  Phase 6 metadata-only preflight and blocks versions greater than `2.6.1` by
  default:
  https://github.com/Lightning-AI/pytorch-lightning/security/advisories/GHSA-w37p-236h-pfx3

## In Scope

- `LightningBridgeConfig` carries engine-neutral bridge components from a
  `TrainingPlan` or direct Lightning entrypoint: resource monitors, profile
  writers, training probes, checkpoint catalog, restore/save/prune policies,
  restart selector, and run/timeline/rank/device attribution.
- `LightningBridgeCallback` translates public Lightning callbacks into
  shared `TrainingEvent`, `ProfileSpanSummary`, resource trace, monitor
  lifecycle, writer result, probe result, and checkpoint result records.
- `LightningProfilerBridge` provides a minimal public-profiler-compatible
  object that records profiler setup/teardown decisions and action spans.
- `map_lightning_checkpoint_policies()` maps rphys checkpoint cadence and
  retention policies onto public `ModelCheckpoint` kwargs where Lightning
  supports them.
- Restart selectors resolve against `CheckpointCatalog` and pass the selected
  checkpoint through public Lightning `ckpt_path` behavior.
- Recency retention that Lightning does not implement directly is recorded as
  rphys pruner evidence instead of pretending `ModelCheckpoint` owns it.
- Fake-Lightning tests validate the adapter without importing real Lightning.

## Out Of Scope

- No Lightning, torch, CUDA/NVML, or system-profiler dependency is added.
- No raw Lightning timeline, private trainer state, callback internals,
  optimizer state, tensors, batches, checkpoint payloads, or framework objects
  are exposed as public rphys evidence.
- No broad distributed strategy parity or private DDP state parsing is added.
- No artifact store, default checkpoint writer, storage backend, workflow
  runtime, scheduler, or automatic tuning layer is introduced.

## Validation Plan

- Focused fake-Lightning and policy suite:
  `uv run pytest tests/unit/rphys/training/test_lightning.py tests/unit/rphys/training/test_policies.py tests/package/test_import.py::test_stage_12_training_modules_export_only_code_backed_names tests/package/test_import_boundaries.py::test_stage_12_training_imports_do_not_load_frameworks_or_datasources`
- Optional installed-Lightning preflight when safe, without importing unsafe
  versions.
- Package/import checks: `make test-package`
- Broader phase checks before PR: `make test-unit`, `make test-contract`,
  `make test-integration`, `make test-summary`, `make validate-pr`,
  `uv lock --check`, and `git diff --check`.

## Validation Evidence

- Focused fake-Lightning bridge suite passed:
  `uv run pytest tests/unit/rphys/training/test_lightning.py tests/unit/rphys/training/test_policies.py tests/package/test_import.py::test_stage_12_training_modules_export_only_code_backed_names tests/package/test_import_boundaries.py::test_stage_12_training_imports_do_not_load_frameworks_or_datasources` - 15 passed.
- Optional installed-Lightning preflight:
  `uv run python -c 'from rphys.training.lightning import preflight_lightning_dependency; p=preflight_lightning_dependency(); print(p.status.value, p.package_name, p.version, p.reason)'` -
  reported `absent`, so real installed-Lightning acceptance was skipped
  without importing Lightning.
- `make test-package` - 72 passed.
- `make test-unit` - 804 passed.
- `make test-contract` - 192 passed.
- `make test-integration` - 32 passed.
- `make test-summary` - package 72, unit 804, contract 192, integration 32;
  e2e and acceptance suites not present.
- `make validate-pr` - passed.
- `uv lock --check` - passed.
- `git diff --check` - passed.

## Implementation Notes

- `LightningTrainingEngine` builds `LightningBridgeConfig.from_plan(plan)` by
  default, so rphys-native plans can reuse the same resource monitor, writer,
  probe, checkpoint, restart, and attribution contracts under Lightning.
- Direct LightningModule/DataModule entrypoints accept an explicit
  `bridge_config` for users who need the same normalized evidence outside the
  shared `Trainer(engine=...)` path.
- Checkpoint save cadence maps to public `ModelCheckpoint` settings for step,
  epoch, elapsed-time, monitored metric, failure, and final checkpoints.
  Best-k retention maps to `save_top_k`, `monitor`, and `mode`.
- Keep-recent retention records `CheckpointPruneResult` evidence because
  Lightning's built-in checkpoint callback is metric-oriented and only provides
  deterministic latest access via `save_last`.
- Resource monitors are started during callback setup, sampled at batch
  boundaries, flushed/stopped during teardown/finalization, and recorded with
  lifecycle evidence. Profile writers receive append evidence and explicit
  step/run flush results.
- Probe failures are converted to `UnavailableProbeEvidence` with
  `RECORD_AND_CONTINUE` semantics so diagnostic failures do not hide the
  underlying Lightning loop result.
