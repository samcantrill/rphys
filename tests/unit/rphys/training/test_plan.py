from __future__ import annotations

import pytest

from rphys.data import Batch, FieldValue
from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopMode
from rphys.training import (
    AsyncTrainingProfileWriter,
    CheckpointCatalog,
    CheckpointPrunePolicy,
    CheckpointRestorePolicy,
    CheckpointSavePolicy,
    FakeCPUResourceProbe,
    InMemoryProfileWriterBackend,
    ResourceMonitor,
    ResourceMonitorExecutionMode,
    TrainingOutputSpec,
    TrainingPlan,
)


class FakeScalar:
    def backward(self) -> None:
        return None


def test_training_plan_stores_caller_built_batches_and_loop_limits() -> None:
    train_batches = (Batch(), Batch())
    valid_batches = (Batch(),)
    plan = TrainingPlan(
        train_batches=train_batches,
        validation_batches=valid_batches,
        max_epochs=3,
        max_train_steps=5,
        output_spec=TrainingOutputSpec(objective="objectives/custom.training.total"),
        metadata={"study": "synthetic"},
        provenance={"stage": "unit"},
    )

    assert plan.train_batches == train_batches
    assert plan.batches_for(LoopMode.TRAIN) == train_batches
    assert plan.batches_for("validate") == valid_batches
    assert plan.max_epochs == 3
    assert plan.max_steps_for("train") == 5
    assert plan.max_steps_for("predict") is None
    assert plan.output_spec.objective is not None
    assert plan.metadata == {"study": "synthetic"}
    assert plan.provenance == {"stage": "unit"}

    with pytest.raises(TypeError):
        plan.metadata["study"] = "mutated"  # type: ignore[index]


def test_training_plan_rejects_invalid_limits_batches_and_hooks() -> None:
    with pytest.raises(RemotePhysTrainingError) as epoch_error:
        TrainingPlan(max_epochs=0)
    assert epoch_error.value.context["field"] == "max_epochs"

    with pytest.raises(RemotePhysTrainingError) as batch_error:
        TrainingPlan(train_batches=(object(),))  # type: ignore[arg-type]
    assert batch_error.value.context["field"] == "train_batches"

    with pytest.raises(RemotePhysTrainingError) as output_error:
        TrainingPlan(train_batches=(Batch(),))
    assert output_error.value.context["field"] == "output_spec"

    with pytest.raises(RemotePhysTrainingError) as hook_error:
        TrainingPlan(device_mover=object())  # type: ignore[arg-type]
    assert hook_error.value.context["field"] == "device_mover"

    with pytest.raises(RemotePhysTrainingError) as metadata_error:
        TrainingPlan(metadata={"history": []})
    assert metadata_error.value.context["key"] == "history"


def test_training_plan_has_no_learner_engine_config_or_workflow_ownership() -> None:
    plan = TrainingPlan(
        train_batches=(Batch(),),
        output_spec=TrainingOutputSpec(objective="objectives/custom.training.total"),
    )

    for forbidden in [
        "learner",
        "engine_config",
        "dataset_path",
        "artifact_dir",
        "logger",
        "workflow",
    ]:
        assert not hasattr(plan, forbidden)


def test_training_plan_accepts_observe_only_event_and_profiler_hooks() -> None:
    class Sink:
        def record(self, event: object) -> None:
            return None

    class Callback:
        def on_event(self, event: object) -> None:
            return None

    class Profiler:
        def span(self, name: str, **kwargs: object) -> object:
            return object()

    plan = TrainingPlan(event_sinks=(Sink(),), callbacks=(Callback(),), profilers=(Profiler(),))

    assert len(plan.event_sinks) == 1
    assert len(plan.callbacks) == 1
    assert len(plan.profilers) == 1

    with pytest.raises(RemotePhysTrainingError) as observer_error:
        TrainingPlan(event_sinks=(object(),))
    assert observer_error.value.context["field"] == "event_sinks"


def test_training_plan_accepts_typed_native_observability_and_checkpoint_inputs() -> None:
    class Probe:
        def collect(self, context: object) -> tuple[object, ...]:
            del context
            return ()

    def restore_hook(result: object) -> object:
        return result

    def save_hook(context: object) -> object:
        return context

    def prune_hook(catalog: object) -> object:
        return catalog

    monitor = ResourceMonitor(
        FakeCPUResourceProbe(),
        execution_mode=ResourceMonitorExecutionMode.INLINE,
    )
    writer = AsyncTrainingProfileWriter(InMemoryProfileWriterBackend())
    plan = TrainingPlan(
        resource_monitors=(monitor,),
        profile_writers=(writer,),
        training_probes=(Probe(),),
        checkpoint_catalog=CheckpointCatalog(),
        checkpoint_restore_policy=CheckpointRestorePolicy(),
        checkpoint_save_policy=CheckpointSavePolicy(by_step=1),
        checkpoint_prune_policy=CheckpointPrunePolicy(keep_recent=1),
        checkpoint_restore_hook=restore_hook,
        checkpoint_save_hook=save_hook,
        checkpoint_prune_hook=prune_hook,
        run_id="run-1",
        timeline_id="timeline-1",
        process_id=1,
        node_id="node-a",
        local_rank=0,
        global_rank=2,
        device_id="cpu",
    )

    assert plan.resource_monitors == (monitor,)
    assert plan.profile_writers == (writer,)
    assert len(plan.training_probes) == 1
    assert isinstance(plan.checkpoint_catalog, CheckpointCatalog)
    assert plan.checkpoint_restore_policy is not None
    assert plan.checkpoint_save_policy is not None
    assert plan.checkpoint_prune_policy is not None
    assert plan.run_id == "run-1"
    assert plan.timeline_id == "timeline-1"
    assert plan.process_id == 1
    assert plan.node_id == "node-a"
    assert plan.local_rank == 0
    assert plan.global_rank == 2
    assert plan.device_id == "cpu"

    with pytest.raises(RemotePhysTrainingError) as monitor_error:
        TrainingPlan(resource_monitors=(object(),))  # type: ignore[arg-type]
    assert monitor_error.value.context["field"] == "resource_monitors"

    with pytest.raises(RemotePhysTrainingError) as writer_error:
        TrainingPlan(profile_writers=(object(),))  # type: ignore[arg-type]
    assert writer_error.value.context["field"] == "profile_writers"

    with pytest.raises(RemotePhysTrainingError) as probe_error:
        TrainingPlan(training_probes=(object(),))
    assert probe_error.value.context["field"] == "training_probes"

    with pytest.raises(RemotePhysTrainingError) as hook_error:
        TrainingPlan(checkpoint_save_hook=object())  # type: ignore[arg-type]
    assert hook_error.value.context["field"] == "checkpoint_save_hook"

    with pytest.raises(RemotePhysTrainingError) as run_id_error:
        TrainingPlan(run_id="")
    assert run_id_error.value.context["field"] == "run_id"


def test_training_output_spec_validates_mode_required_fields_and_objective() -> None:
    spec = TrainingOutputSpec(
        objective="objectives/custom.training.total",
        metrics=("metrics/custom.training.mae",),
        required_by_mode={"validate": ("metrics/custom.training.mae",)},
    )
    train_batch = Batch(
        {
            "objectives/custom.training.total": FieldValue(FakeScalar()),
            "metrics/custom.training.mae": FieldValue(0.5),
        }
    )

    assert spec.validate_batch(train_batch, "train") is train_batch
    assert spec.objective_value(train_batch, "train") is train_batch.require("objectives/custom.training.total")
    assert spec.metric_values(train_batch) == {"metrics/custom.training.mae": 0.5}

    with pytest.raises(RemotePhysTrainingError) as missing_mode_required:
        spec.validate_batch(Batch(), "validate")
    assert missing_mode_required.value.context["locator"] == "metrics/custom.training.mae"

    with pytest.raises(RemotePhysTrainingError) as invalid_objective:
        spec.validate_batch(Batch({"objectives/custom.training.total": FieldValue(1.0)}), "train")
    assert invalid_objective.value.context["field"] == "objective"
