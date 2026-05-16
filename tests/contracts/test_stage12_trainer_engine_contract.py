from __future__ import annotations

from rphys.data import Batch
from rphys.learning import LoopContext, StepOutput
from rphys.training import NativeTrainingEngine, Trainer, TrainingEngine, TrainingPlan, TrainingResult


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


def test_trainer_without_selected_engine_uses_native_default() -> None:
    trainer = Trainer()

    assert isinstance(trainer.engine, NativeTrainingEngine)
    result = trainer.predict(TrainingPlan(predict_batches=(Batch(),)), ContractLearner())
    assert result.mode.value == "predict"
