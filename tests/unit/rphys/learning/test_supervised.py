from __future__ import annotations

import pytest

from rphys.data import Batch, FieldValue
from rphys.errors import RemotePhysLearningError
from rphys.learning import LoopContext, LoopMode, SupervisedLearner
from rphys.losses import LossContext, LossContract, LossInputSpec, LossResult, LossTerm
from rphys.metrics import MetricContext, MetricContract, MetricValue
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

    def predict(self, batch: Batch, *, context: object | None = None) -> Batch:
        self.calls.append((batch, context))
        source = batch.require("inputs/signal.pulse")[0]
        output = batch.shallow_copy()
        output.set_field("predictions/signal.pulse", FieldValue([source + 0.5]))
        return output


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
    contract = MetricContract(
        "stage12-metric",
        level="batch",
        writes=("metrics/custom.training.pulse.mae",),
    )

    def __call__(self, context: MetricContext) -> MetricValue:
        prediction = context.fields.require("predictions/signal.pulse")[0]
        target = context.fields.require("targets/signal.pulse")[0]
        return MetricValue(
            FakeScalar(abs(prediction - target)),
            backend="fake",
            unit="bpm",
            metadata={"split": context.metadata["split"]},
        )


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

    assert isinstance(output, Batch)
    assert not batch.has("predictions/signal.pulse")
    assert output.require("predictions/signal.pulse") == [1.5]
    assert output.require("losses/custom.training.l1") == FakeScalar(0.5)
    assert output.require("objectives/custom.training.total") == FakeScalar(0.5)
    assert output.require("objectives/custom.training.l1") == FakeScalar(0.5)
    assert output.require("metrics/custom.training.pulse.mae").value == FakeScalar(0.5)
    assert len(method.calls) == 1


def test_predict_mode_preserves_method_output_without_objective_or_targets() -> None:
    method = SyntheticMethod()
    learner = SupervisedLearner(method)
    batch = Batch({"inputs/signal.pulse": FieldValue([1.0])})

    output = learner.step(batch, LoopContext("predict", split="inference"))

    assert isinstance(output, Batch)
    assert output.require("predictions/signal.pulse") == [1.5]
    assert not output.has("objectives/custom.training.total")
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

    assert isinstance(output, Batch)
    assert output.require("predictions/signal.pulse") == [1.5]
    assert not output.has("objectives/custom.training.total")
    assert not output.has("metrics/custom.training.pulse.mae")


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
