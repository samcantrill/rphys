from __future__ import annotations

from rphys.data import Batch, FieldValue
from rphys.learning import LoopContext, SupervisedLearner
from rphys.losses import LossContext, LossContract, LossInputSpec, LossResult, LossTerm
from rphys.metrics import MetricContext, MetricContract, MetricValue
from rphys.objectives import ObjectiveContext, ObjectiveContract, ObjectiveResult, ObjectiveTerm, ObjectiveTermSpec
from rphys.training import NativeTrainingEngine, Trainer, TrainingOutputSpec, TrainingPlan, TrainingStatus


class FakeScalar:
    def __init__(self, value: float) -> None:
        self.value = value
        self.backward_calls = 0

    def backward(self) -> None:
        self.backward_calls += 1


class PulseMethod:
    def predict(self, batch: Batch, *, context: object | None = None) -> Batch:
        output = batch.shallow_copy()
        output.set_field("predictions/signal.pulse", FieldValue([batch.require("inputs/signal.pulse")[0] * 2.0]))
        return output


class PulseLoss:
    contract = LossContract(
        "pulse-l1",
        (
            LossInputSpec("predictions/signal.pulse", role="prediction"),
            LossInputSpec("targets/signal.pulse", role="target"),
        ),
    )

    def __call__(self, context: LossContext) -> LossResult:
        value = abs(
            context.fields.require("predictions/signal.pulse")[0]
            - context.fields.require("targets/signal.pulse")[0]
        )
        return LossResult((LossTerm("pulse-l1", FakeScalar(value), backend="fake"),))


class PulseObjective:
    contract = ObjectiveContract("pulse-total", (ObjectiveTermSpec("pulse-l1", source="loss:pulse-l1"),))

    def __call__(self, context: ObjectiveContext) -> ObjectiveResult:
        term = ObjectiveTerm.from_loss_term(context.loss_results[0].primary)
        return ObjectiveResult(total=ObjectiveTerm("total", term.value, backend=term.backend), terms=(term,))


class PulseMetric:
    contract = MetricContract(
        "pulse-mae",
        level="batch",
        writes=("metrics/custom.training.pulse.mae",),
    )

    def __call__(self, context: MetricContext) -> MetricValue:
        value = abs(
            context.fields.require("predictions/signal.pulse")[0]
            - context.fields.require("targets/signal.pulse")[0]
        )
        return MetricValue(
            FakeScalar(value),
            backend="fake",
            unit="bpm",
            metadata={"split": context.metadata["split"]},
        )


def test_stage12_supervised_learner_composes_stage10_method_and_stage11_contracts() -> None:
    learner = SupervisedLearner(
        PulseMethod(),
        losses=(PulseLoss(),),
        objective=PulseObjective(),
        metrics=(PulseMetric(),),
    )
    batch = Batch(
        {
            "inputs/signal.pulse": FieldValue([1.0]),
            "targets/signal.pulse": FieldValue([2.5]),
        }
    )

    output = learner.step(batch, LoopContext("train", split="train", step_index=0))

    assert isinstance(output, Batch)
    assert output.require("objectives/custom.training.total").value == 0.5
    assert output.require("metrics/custom.training.pulse.mae").value.value == 0.5
    assert not batch.has("predictions/signal.pulse")


class RecordingOptimizer:
    def __init__(self) -> None:
        self.zero_grad_calls = 0
        self.step_calls = 0

    def zero_grad(self) -> None:
        self.zero_grad_calls += 1

    def step(self) -> None:
        self.step_calls += 1


def test_stage12_native_engine_runs_synthetic_supervised_fit_validate_test_predict() -> None:
    learner = SupervisedLearner(
        PulseMethod(),
        losses=(PulseLoss(),),
        objective=PulseObjective(),
        metrics=(PulseMetric(),),
    )
    optimizer = RecordingOptimizer()
    train_batch = Batch(
        {
            "inputs/signal.pulse": FieldValue([1.0]),
            "targets/signal.pulse": FieldValue([2.5]),
        }
    )
    eval_batch = Batch(
        {
            "inputs/signal.pulse": FieldValue([1.0]),
            "targets/signal.pulse": FieldValue([2.0]),
        }
    )
    predict_batch = Batch({"inputs/signal.pulse": FieldValue([1.0])})
    plan = TrainingPlan(
        train_batches=(train_batch,),
        validation_batches=(eval_batch,),
        test_batches=(eval_batch,),
        predict_batches=(predict_batch,),
        optimizer=optimizer,
        output_spec=TrainingOutputSpec(
            objective="objectives/custom.training.total",
            metrics=("metrics/custom.training.pulse.mae",),
        ),
    )
    trainer = Trainer()

    fit_result = trainer.fit(plan, learner)
    validate_result = NativeTrainingEngine().validate(plan, learner)
    test_result = NativeTrainingEngine().test(plan, learner)
    predict_result = trainer.predict(plan, learner)

    assert fit_result.status is TrainingStatus.COMPLETED
    assert fit_result.step_count == 1
    assert fit_result.metadata["validation_step_count"] == 1
    assert optimizer.zero_grad_calls == 1
    assert optimizer.step_calls == 1
    assert validate_result.mode.value == "validate"
    assert test_result.mode.value == "test"
    assert predict_result.mode.value == "predict"
    assert predict_result.step_count == 1
