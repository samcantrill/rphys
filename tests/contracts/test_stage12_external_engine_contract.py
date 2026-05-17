from __future__ import annotations

import pytest

import rphys.training as training
from rphys.data import Batch
from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopContext
from rphys.training import Trainer, TrainingOutputSpec, TrainingPlan
from tests.support.stage12_fake_external import (
    FakeExternalEngine,
    FakeExternalEvidence,
    FakeMethod,
    FakeModule,
    FakeTrainableOwnerRegistry,
)


class LearnerThatMustNotRun:
    def step(self, batch: Batch, context: LoopContext) -> Batch:
        raise AssertionError("fake external engine must own loop control")


def test_fake_external_engine_delegation_maps_only_primitive_evidence() -> None:
    evidence = FakeExternalEvidence(
        metrics={"val_mae": 0.2},
        checkpoint_id="external-ckpt-1",
        callback_statuses={"callback.progress": "observed"},
        profile_statuses={"external.forward": "available"},
        unavailable_probes={"cuda-timing": "not configured"},
        event_counts={"external.step": 3},
    )
    engine = FakeExternalEngine(evidence)
    plan = TrainingPlan(
        train_batches=(Batch(),),
        output_spec=TrainingOutputSpec(objective="objectives/custom.training.total"),
    )
    learner = LearnerThatMustNotRun()

    result = Trainer(engine=engine).fit(plan, learner)

    assert engine.calls == [("fit", plan, learner)]
    assert result.metrics["val_mae"].value == 0.2
    assert result.checkpoint_id == "external-ckpt-1"
    assert result.events[0].name == "callback.progress"
    assert result.profiles[-1].metadata["reason"] == "not configured"


def test_fake_trainable_owner_registry_rejects_duplicates_and_unsupported_python_objects() -> None:
    child = FakeModule("child")
    root = FakeModule("root", children=(child,))
    registry = FakeTrainableOwnerRegistry()

    assert registry.register_method(FakeMethod(root)) is root
    with pytest.raises(RemotePhysTrainingError):
        registry.register_method(FakeMethod(root))
    with pytest.raises(RemotePhysTrainingError):
        registry.register_method(FakeMethod(child))
    with pytest.raises(RemotePhysTrainingError):
        registry.register_method(FakeMethod(None))

    assert not hasattr(training, "TrainableOwnerRegistry")
    assert not hasattr(training, "TrainableModule")
