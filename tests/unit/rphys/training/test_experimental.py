from __future__ import annotations

import pytest

from rphys.data import Batch
from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopContext
from rphys.training import Trainer, TrainingOutputSpec, TrainingPlan, TrainingResult, run_train


class FakeLearner:
    def step(self, batch: Batch, context: LoopContext) -> Batch:
        return batch


class FakeEngine:
    def __init__(self) -> None:
        self.calls: list[tuple[TrainingPlan, FakeLearner]] = []

    def fit(self, plan: TrainingPlan, learner: FakeLearner) -> TrainingResult:
        self.calls.append((plan, learner))
        return TrainingResult(status="completed", mode="train", step_count=1)

    def validate(self, plan: TrainingPlan, learner: FakeLearner) -> TrainingResult:
        return TrainingResult(status="completed", mode="validate")

    def test(self, plan: TrainingPlan, learner: FakeLearner) -> TrainingResult:
        return TrainingResult(status="completed", mode="test")

    def predict(self, plan: TrainingPlan, learner: FakeLearner) -> TrainingResult:
        return TrainingResult(status="completed", mode="predict")


def test_run_train_delegates_to_trainer_fit_without_workflow_ownership() -> None:
    engine = FakeEngine()
    plan = TrainingPlan(
        train_batches=(Batch(),),
        output_spec=TrainingOutputSpec(objective="objectives/custom.training.total"),
    )
    learner = FakeLearner()

    result = run_train(plan, learner, engine=engine)

    assert result.status.value == "completed"
    assert engine.calls == [(plan, learner)]


def test_run_train_accepts_explicit_trainer_and_rejects_ambiguous_selection() -> None:
    trainer = Trainer(engine=FakeEngine())
    result = run_train(
        TrainingPlan(
            train_batches=(Batch(),),
            output_spec=TrainingOutputSpec(objective="objectives/custom.training.total"),
        ),
        FakeLearner(),
        trainer=trainer,
    )

    assert result.mode.value == "train"
    with pytest.raises(RemotePhysTrainingError):
        run_train(
            TrainingPlan(
                train_batches=(Batch(),),
                output_spec=TrainingOutputSpec(objective="objectives/custom.training.total"),
            ),
            FakeLearner(),
            trainer=trainer,
            engine=FakeEngine(),
        )
