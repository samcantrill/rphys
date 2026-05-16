from __future__ import annotations

import pytest

from rphys.data import Batch
from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopContext, StepOutput
from rphys.training import Trainer, TrainingPlan, TrainingResult


class FakeLearner:
    def step(self, batch: Batch, context: LoopContext) -> StepOutput:
        return StepOutput(metadata={"mode": context.mode.value})


class FakeEngine:
    def __init__(self) -> None:
        self.calls: list[tuple[str, TrainingPlan, FakeLearner]] = []

    def fit(self, plan: TrainingPlan, learner: FakeLearner) -> TrainingResult:
        self.calls.append(("fit", plan, learner))
        return TrainingResult(status="completed", mode="train", step_count=1)

    def validate(self, plan: TrainingPlan, learner: FakeLearner) -> TrainingResult:
        self.calls.append(("validate", plan, learner))
        return TrainingResult(status="completed", mode="validate", step_count=1)

    def test(self, plan: TrainingPlan, learner: FakeLearner) -> TrainingResult:
        self.calls.append(("test", plan, learner))
        return TrainingResult(status="completed", mode="test", step_count=1)

    def predict(self, plan: TrainingPlan, learner: FakeLearner) -> TrainingResult:
        self.calls.append(("predict", plan, learner))
        return TrainingResult(status="completed", mode="predict", step_count=1)


def test_trainer_delegates_each_mode_to_explicit_engine() -> None:
    engine = FakeEngine()
    trainer = Trainer(engine=engine)
    plan = TrainingPlan(train_batches=(Batch(),))
    learner = FakeLearner()

    assert trainer.fit(plan, learner).mode.value == "train"
    assert trainer.validate(plan, learner).mode.value == "validate"
    assert trainer.test(plan, learner).mode.value == "test"
    assert trainer.predict(plan, learner).mode.value == "predict"
    assert [call[0] for call in engine.calls] == ["fit", "validate", "test", "predict"]
    assert all(call[1] is plan for call in engine.calls)
    assert all(call[2] is learner for call in engine.calls)


def test_trainer_has_no_placeholder_default_engine_in_phase_3() -> None:
    trainer = Trainer()

    with pytest.raises(RemotePhysTrainingError) as exc_info:
        trainer.fit(TrainingPlan(), FakeLearner())

    assert exc_info.value.context["field"] == "engine"
    assert exc_info.value.context["actual"] == "None"


def test_trainer_rejects_invalid_engine_and_plan() -> None:
    with pytest.raises(RemotePhysTrainingError) as engine_error:
        Trainer(engine=object())  # type: ignore[arg-type]
    assert engine_error.value.context["field"] == "engine"

    trainer = Trainer(engine=FakeEngine())
    with pytest.raises(RemotePhysTrainingError) as plan_error:
        trainer.fit(object(), FakeLearner())  # type: ignore[arg-type]
    assert plan_error.value.context["field"] == "plan"
