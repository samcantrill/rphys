from __future__ import annotations

from rphys.data import Batch, FieldValue
from rphys.learning import LoopContext, SupervisedLearner
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


class PulseMethod:
    def predict(self, batch: Batch, *, context: object | None = None) -> MethodOutput:
        return MethodOutput(
            fields={"predictions/signal.pulse": FieldValue([batch.require("inputs/signal.pulse")[0] * 2.0])}
        )


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
    contract = MetricContract("pulse-mae", level="batch")

    def __call__(self, context: MetricContext) -> MetricResult:
        value = abs(
            context.fields.require("predictions/signal.pulse")[0]
            - context.fields.require("targets/signal.pulse")[0]
        )
        return MetricResult(
            MetricObservationCollection(
                (
                    MetricObservation(
                        "pulse-mae",
                        MetricValue(FakeScalar(value), backend="fake", unit="bpm"),
                        level="batch",
                        groups={"split": context.metadata["split"]},
                    ),
                )
            )
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

    assert isinstance(output.predictions, MethodOutput)
    assert output.objective is not None
    assert output.objective.value == 0.5
    assert output.metric_values["pulse-mae"].value.value == 0.5
    assert not batch.has("predictions/signal.pulse")
