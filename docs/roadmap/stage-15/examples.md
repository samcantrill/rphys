# Stage 15 Training Profiling And Restart Examples

Stage 15 makes training execution diagnosable through shared primitive records:
`TrainingEventLog`, `TrainingProfile`, resource traces, probe summaries,
checkpoint records, policy records, data-path fingerprints, and descriptive
tier/restart evidence. Native, Lightning, and future engines should normalize
into the same rphys records rather than exposing raw framework timelines,
checkpoint payloads, tensors, profiler objects, or scheduler state.

## Native Profile, Checkpoint, And Restart Evidence

The native engine owns the reference Python loop. It records setup, data wait,
device transfer, learner step, objective, backward, optimizer, validation,
checkpoint, callback, profile summary, teardown, and failure evidence when the
corresponding plan components are supplied.

```python
from rphys.training import (
    CheckpointCatalog,
    CheckpointRef,
    CheckpointRestorePolicy,
    CheckpointSavePolicy,
    CheckpointSelection,
    CheckpointSelectionMode,
    RestartState,
    Trainer,
    TrainingPlan,
    TrainingOutputSpec,
)

catalog = CheckpointCatalog(
    (
        CheckpointRef(
            "run-a-step-20",
            run_id="run-a",
            timeline_id="timeline-a",
            status="completed",
            epoch=2,
            step=20,
            path="/checkpoints/run-a-step-20.ckpt",
        ),
    ),
)

plan = TrainingPlan(
    train_batches=train_batches,
    validation_batches=validation_batches,
    max_epochs=2,
    max_train_steps=20,
    output_spec=TrainingOutputSpec(objective="objectives/loss", metrics=("metrics/mae",)),
    checkpoint_catalog=catalog,
    checkpoint_restore_policy=CheckpointRestorePolicy(),
    checkpoint_save_policy=CheckpointSavePolicy(by_step=10, on_final=True),
    checkpoint_save_hook=save_checkpoint,
    checkpoint_restore_hook=restore_checkpoint,
    run_id="run-a",
    timeline_id="timeline-a",
)

result = Trainer().fit(plan, learner)
profile = result.training_profile
selected = catalog.select(CheckpointSelection(CheckpointSelectionMode.LATEST_COMPLETED))
assert selected.ref is not None

restart = RestartState(
    checkpoint_ref=selected.ref,
    tier="smoke",
    run_id="run-a",
    timeline_id="timeline-a",
    step=20,
    loader_fingerprint="loader:synthetic:v1",
    materialization_fingerprint="materialized:none",
    data_path_fingerprint="data-path:stage9:v1",
    profile_fingerprint="profile:run-a:v1",
    profile_summary_id="summary:run-a",
    checkpoint_fingerprint="checkpoint:run-a-step-20",
    completion_markers=("epoch:2", "step:20", "checkpoint:completed"),
    compatibility_status="compatible",
    compatibility_note="loader, data-path, profile, and checkpoint evidence describe the same path",
)
```

`RestartState` is evidence only. It links checkpoint identity, loader and
materialization fingerprints, profile summaries, completion markers, and a
compatibility note. It does not restore payloads, create files, schedule retry
jobs, or manage artifact retention.

## Lightning Bridge With Shared Output Records

Lightning support is optional and import-gated under `rphys.training.lightning`.
The bridge maps public Lightning callbacks, profiler actions, checkpoint
callbacks, `ckpt_path`, ranks, resource monitors, profile writers, and probes
into shared rphys records.

```python
from rphys.training import CheckpointPrunePolicy, CheckpointSavePolicy
from rphys.training.lightning import (
    LightningBridgeConfig,
    LightningTrainingEngine,
    fit_lightning_module,
    preflight_lightning_dependency,
)

preflight = preflight_lightning_dependency()
if preflight.status.value == "available":
    bridge = LightningBridgeConfig(
        checkpoint_save_policy=CheckpointSavePolicy(
            by_step=100,
            on_metric=True,
            metric_name="val_loss",
            metric_direction="min",
            on_final=True,
        ),
        checkpoint_prune_policy=CheckpointPrunePolicy(
            keep_recent=3,
            keep_best=1,
            best_metric_name="val_loss",
            best_metric_direction="min",
        ),
        run_id="lightning-run-a",
        timeline_id="lightning-timeline-a",
        global_rank=0,
        local_rank=0,
        device_id="cuda:0",
    )

    result = fit_lightning_module(
        module=lightning_module,
        train_dataloaders=train_loader,
        val_dataloaders=valid_loader,
        trainer_config={"max_epochs": 2},
        bridge_config=bridge,
    )

    engine = LightningTrainingEngine(bridge_config=bridge)
```

If Lightning is absent or unsafe, the preflight returns explicit unavailable or
blocked evidence without importing Lightning or torch through base
`rphys.training`. The adapter does not expose raw Lightning trainer state,
private callback internals, profiler timeline objects, tensors, batches, or
checkpoint payloads as public rphys data.

## Data-Path And Probe Evidence

Data-path profiling stays anchored to Stage 9 datasource records. Pipeline
stage names such as `indexed`, `cache_lookup`, `prepared_read`,
`pre_augmentation`, `collate`, `pre_device_transfer`, and
`post_device_transfer` describe where evidence was collected. Probe summaries
can report data quality, model health, unavailable hardware checks, and
resource blind spots without changing learner semantics.

```python
from rphys.datasources import DataPathProfile
from rphys.training import (
    DataFieldProbeSummary,
    DataProbeSummary,
    ProbeCadence,
    ProbeSelector,
    TrainingPipelineStage,
)

profile = DataPathProfile(
    "stage9-loader-profile",
    loader_state_fingerprint="loader:stage9:v1",
    summaries={
        "decode.duration.ms": 12.5,
        "collate.duration.ms": 3.1,
        "queue.wait.ms": 7.4,
        "device_transfer.bytes": 1048576,
    },
)

batch_probe = DataFieldProbeSummary(
    DataProbeSummary(
        "batch-quality",
        "batch",
        hook_point="batch_fetch",
        selector=ProbeSelector("all"),
        cadence=ProbeCadence("every_n_steps", interval=1),
        pipeline_stage=TrainingPipelineStage.COLLATE,
        split="train",
    ),
    field="video.rgb",
    locator="inputs/video.rgb",
    shape=(8, "frames", "height", "width", 3),
    dtype="float32",
    present_ratio=1.0,
    nan_fraction=0.0,
    inf_fraction=0.0,
)
```

Timing and throughput summaries remain threshold-free and attribution-aware.
They should state unavailable probes, ambiguous system-wide measurements, rank
or device labels, units, sample cadence, and synchronization caveats when those
details affect interpretation.

## Descriptive Validation Tiers

`ExperimentTierSpec` names the breadth of a run and the evidence expected from
that breadth. Tiers are descriptive records, not a scheduler, cost policy,
storage backend, or alternate fake execution path.

```python
from rphys.training import ExperimentTierSpec, default_experiment_tiers

debug, smoke, signal, comparison, full = default_experiment_tiers()

custom_signal = ExperimentTierSpec(
    "signal",
    subject_limit=2,
    record_limit=2,
    sample_limit=32,
    epoch_limit=2,
    step_limit=20,
    expected_evidence=(
        "training_events",
        "profile_spans",
        "resource_traces",
        "checkpoint_refs",
        "data_path_fingerprint",
    ),
    loader_fingerprint="loader:signal:v1",
    data_path_fingerprint="data-path:signal:v1",
    profile_fingerprint="profile:signal:v1",
)
```

Debug, smoke, signal, comparison, and full tiers should differ by scale and
coverage expectations while using the same data-path, training, profiling,
checkpoint, and restart contracts. Default tests stay CPU-only, synthetic,
deterministic, and free of machine-speed thresholds. Optional hardware,
system-probe, and installed-Lightning acceptance should record unavailable
evidence when the environment cannot support them.
