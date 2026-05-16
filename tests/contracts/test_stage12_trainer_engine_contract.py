from __future__ import annotations

import pytest

from rphys.data import Batch
from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopContext, StepOutput
from rphys.training import Trainer, TrainingEngine, TrainingPlan, TrainingResult


class ContractLearner:
    def step(self, batch: Batch, context: LoopContext) -> StepOutput:
        return StepOutput(metadata={"mode": context.mode.value})


class RecordingEngine:
    def __init__(self) -> None:
        self.fit_calls: list[tuple[TrainingPlan, ContractLearner]] = []

    def fit(self, plan: TrainingPlan, learner: ContractLearner) -> TrainingResult:
        self.fit_calls.append((plan, learner))
        return TrainingResult(status="completed", mode="train", step_count=1)

    def validate(self, plan: TrainingPlan, learner: ContractLearner) -> TrainingResult:
        return TrainingResult(status="completed", mode="validate")

    def test(self, plan: TrainingPlan, learner: ContractLearner) -> TrainingResult:
        return TrainingResult(status="completed", mode="test")

    def predict(self, plan: TrainingPlan, learner: ContractLearner) -> TrainingResult:
        return TrainingResult(status="completed", mode="predict")


def test_training_engine_is_structural_and_receives_plan_and_learner_separately() -> None:
    engine = RecordingEngine()
    trainer = Trainer(engine=engine)
    plan = TrainingPlan(train_batches=(Batch(),), metadata={"source": "contract"})
    learner = ContractLearner()

    result = trainer.fit(plan, learner)

    assert isinstance(engine, TrainingEngine)
    assert result.status.value == "completed"
    assert engine.fit_calls == [(plan, learner)]
    assert not hasattr(plan, "learner")
    assert not hasattr(plan, "engine_config")


def test_trainer_without_selected_engine_fails_instead_of_running_native_placeholder() -> None:
    with pytest.raises(RemotePhysTrainingError):
        Trainer().fit(TrainingPlan(), ContractLearner())
