from __future__ import annotations

import pytest

from rphys.data import Batch
from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopMode
from rphys.training import TrainingPlan


def test_training_plan_stores_caller_built_batches_and_loop_limits() -> None:
    train_batches = (Batch(), Batch())
    valid_batches = (Batch(),)
    plan = TrainingPlan(
        train_batches=train_batches,
        validation_batches=valid_batches,
        max_epochs=3,
        max_train_steps=5,
        metadata={"study": "synthetic"},
        provenance={"stage": "unit"},
    )

    assert plan.train_batches == train_batches
    assert plan.batches_for(LoopMode.TRAIN) == train_batches
    assert plan.batches_for("validate") == valid_batches
    assert plan.max_epochs == 3
    assert plan.max_steps_for("train") == 5
    assert plan.max_steps_for("predict") is None
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

    with pytest.raises(RemotePhysTrainingError) as hook_error:
        TrainingPlan(device_mover=object())  # type: ignore[arg-type]
    assert hook_error.value.context["field"] == "device_mover"

    with pytest.raises(RemotePhysTrainingError) as metadata_error:
        TrainingPlan(metadata={"history": []})
    assert metadata_error.value.context["key"] == "history"


def test_training_plan_has_no_learner_engine_config_or_workflow_ownership() -> None:
    plan = TrainingPlan(train_batches=(Batch(),))

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
