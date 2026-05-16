from __future__ import annotations

import pytest

from rphys.data import Batch, FieldValue
from rphys.errors import RemotePhysLearningError
from rphys.learning import LoopContext, LoopMode, SupervisedLearner
from rphys.losses import LossContext, LossContract, LossInputSpec, LossResult, LossTerm
from rphys.methods import MethodOutput
from rphys.metrics import MetricContext, MetricContract, MetricObservation, MetricObservationCollection, MetricResult, MetricValue
from rphys.objectives import ObjectiveContext, ObjectiveContract, ObjectiveResult, ObjectiveTerm, ObjectiveTermSpec


class FakeScalar:
    def __init__(self, value: float) -> None:
        self.value = value
        self.backward_calls = 0

    def backward(self) -> None:
        self.backward_calls += 1

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FakeScalar) and other.value == self.value


class SyntheticMethod:
    def __init__(self) -> None:
        self.calls: list[tuple[Batch, object]] = []

    def predict(self, batch: Batch, *, context: object | None = None) -> MethodOutput:
        self.calls.append((batch, context))
        source = batch.require("inputs/signal.pulse")[0]
        return MethodOutput(
            fields={"predictions/signal.pulse": FieldValue([source + 0.5])},
            diagnostics={"method": "synthetic"},
        )


class SyntheticLoss:
    contract = LossContract(
        "stage12-synthetic-l1",
        (
            LossInputSpec("predictions/signal.pulse", role="prediction"),
            LossInputSpec("targets/signal.pulse", role="target"),
        ),
    )

    def __call__(self, context: LossContext) -> LossResult:
        prediction = context.fields.require("predictions/signal.pulse")[0]
        target = context.fields.require("targets/signal.pulse")[0]
        return LossResult(
            (
                LossTerm(
                    "l1",
                    FakeScalar(abs(prediction - target)),
                    backend="fake",
                    gradient_path="prediction->l1",
                ),
            ),
            provenance={"loss": self.contract.name},
        )


class SyntheticObjective:
    contract = ObjectiveContract(
        "stage12-objective",
        (ObjectiveTermSpec("l1", source="loss:l1"),),
    )

    def __call__(self, context: ObjectiveContext) -> ObjectiveResult:
        component = ObjectiveTerm.from_loss_term(context.loss_results[0].primary, name="l1")
        total = ObjectiveTerm(
            "total",
            component.value,
            backend=component.backend,
            source_terms=(component.name,),
            gradient_path=component.gradient_path,
        )
        return ObjectiveResult(total=total, terms=(component,), provenance={"objective": self.contract.name})


class SyntheticMetric:
    contract = MetricContract("stage12-metric", level="batch")

    def __call__(self, context: MetricContext) -> MetricResult:
        prediction = context.fields.require("predictions/signal.pulse")[0]
        target = context.fields.require("targets/signal.pulse")[0]
        observation = MetricObservation(
            "pulse-mae",
            MetricValue(FakeScalar(abs(prediction - target)), backend="fake", unit="bpm"),
            level=context.contract.level,
            groups={"split": context.metadata["split"]},
        )
        return MetricResult(MetricObservationCollection((observation,)))


def _batch() -> Batch:
    return Batch(
        {
            "inputs/signal.pulse": FieldValue([1.0]),
            "targets/signal.pulse": FieldValue([2.0]),
        }
    )


def test_supervised_learner_composes_method_loss_objective_and_metric_without_mutating_input() -> None:
    method = SyntheticMethod()
    learner = SupervisedLearner(
        method,
        losses=(SyntheticLoss(),),
        objective=SyntheticObjective(),
        metrics=(SyntheticMetric(),),
    )
    batch = _batch()

    output = learner.step(batch, LoopContext(LoopMode.TRAIN, split="train", batch_index=4))

    assert isinstance(output.predictions, MethodOutput)
    assert not batch.has("predictions/signal.pulse")
    assert output.objective == FakeScalar(0.5)
    assert [term.name for term in output.loss_terms] == ["l1"]
    assert [term.name for term in output.objective_terms] == ["total", "l1"]
    assert output.metric_values["pulse-mae"].value == FakeScalar(0.5)
    assert output.diagnostics == {
        "method": "synthetic",
        "loss_result_count": 1,
        "objective_present": True,
        "metric_result_count": 1,
    }
    assert output.metadata == {"mode": "train", "split": "train"}
    assert len(method.calls) == 1


def test_predict_mode_preserves_method_output_without_objective_or_targets() -> None:
    method = SyntheticMethod()
    learner = SupervisedLearner(method)
    batch = Batch({"inputs/signal.pulse": FieldValue([1.0])})

    output = learner.step(batch, LoopContext("predict", split="inference"))

    assert isinstance(output.predictions, MethodOutput)
    assert output.objective is None
    assert output.loss_terms == ()
    assert output.objective_terms == ()
    assert output.metric_values == {}
    assert not batch.has("predictions/signal.pulse")


def test_predict_mode_skips_configured_objective_losses_and_metrics() -> None:
    learner = SupervisedLearner(
        SyntheticMethod(),
        losses=(SyntheticLoss(),),
        objective=SyntheticObjective(),
        metrics=(SyntheticMetric(),),
    )
    batch = Batch({"inputs/signal.pulse": FieldValue([1.0])})

    output = learner.step(batch, LoopContext("predict", split="inference"))

    assert isinstance(output.predictions, MethodOutput)
    assert output.objective is None
    assert output.loss_terms == ()
    assert output.objective_terms == ()
    assert output.metric_values == {}


def test_train_mode_requires_objective() -> None:
    learner = SupervisedLearner(SyntheticMethod())

    with pytest.raises(RemotePhysLearningError) as exc_info:
        learner.step(_batch(), LoopContext("train"))

    assert exc_info.value.context["field"] == "objective"
    assert exc_info.value.context["mode"] == "train"


def test_supervised_learner_rejects_invalid_collaborators_and_step_inputs() -> None:
    with pytest.raises(RemotePhysLearningError):
        SupervisedLearner(object())  # type: ignore[arg-type]
    with pytest.raises(RemotePhysLearningError):
        SupervisedLearner(SyntheticMethod(), metrics=(object(),))  # type: ignore[arg-type]

    learner = SupervisedLearner(SyntheticMethod())
    with pytest.raises(RemotePhysLearningError):
        learner.step(object(), LoopContext("predict"))  # type: ignore[arg-type]
    with pytest.raises(RemotePhysLearningError):
        learner.step(Batch(), object())  # type: ignore[arg-type]
