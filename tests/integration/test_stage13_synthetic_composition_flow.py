from __future__ import annotations

from dataclasses import dataclass

from rphys.data import (
    Batch,
    BatchOutputFieldSpec,
    BatchOutputSpec,
    FieldValue,
    Sample,
    UncollatePlan,
    collate_samples,
    uncollate_batch_fields,
)
from rphys.learning import LoopContext, SupervisedLearner
from rphys.methods import Method, PredictionContext


INPUT = "inputs/signal.bvp"
TARGET = "targets/signal.bvp.reference"
PREDICTION = "predictions/signal.bvp.estimated"


@dataclass(slots=True)
class ScalePulseMethod:
    factor: float
    output_spec: BatchOutputSpec

    def predict(self, batch: Batch, *, context: PredictionContext | None = None) -> Batch:
        values = batch.require(INPUT)
        prediction = [round(value * self.factor, 3) for value in values]
        return self.output_spec.build({"prediction": prediction}, base=batch)


def test_stage13_batch_native_method_and_learner_outputs_feed_explicit_uncollation() -> None:
    samples = (
        Sample(
            {
                INPUT: FieldValue(0.1, schema="signal.bvp.v1", collate_policy="list"),
                TARGET: FieldValue(0.21, schema="signal.bvp.v1", collate_policy="list"),
            }
        ),
        Sample(
            {
                INPUT: FieldValue(0.2, schema="signal.bvp.v1", collate_policy="list"),
                TARGET: FieldValue(0.39, schema="signal.bvp.v1", collate_policy="list"),
            }
        ),
    )
    batch = collate_samples(samples)
    method = ScalePulseMethod(
        factor=2.0,
        output_spec=BatchOutputSpec(
            (
                BatchOutputFieldSpec(
                    "prediction",
                    PREDICTION,
                    expected_type=list,
                    schema="signal.bvp.v1",
                ),
            ),
            pass_through=(TARGET,),
        ),
    )
    learner = SupervisedLearner(method)

    method_output = method.predict(batch, context=PredictionContext(provenance={"run": "stage13-method"}))
    learner_output = learner.step(batch, LoopContext("predict", split="heldout", step_index=0))
    uncollated = uncollate_batch_fields(learner_output, UncollatePlan(2, (INPUT, PREDICTION, TARGET)))

    assert isinstance(method, Method)
    assert isinstance(method_output, Batch)
    assert isinstance(learner_output, Batch)
    assert method_output.require(PREDICTION) == [0.2, 0.4]
    assert learner_output.require(PREDICTION) == [0.2, 0.4]
    assert [sample.require(PREDICTION) for sample in uncollated] == [0.2, 0.4]
    assert [sample.require(TARGET) for sample in uncollated] == [0.21, 0.39]
    assert [sample.require(INPUT) for sample in uncollated] == [0.1, 0.2]
    assert not batch.has(PREDICTION)

    import rphys.learning
    import rphys.methods

    assert not hasattr(rphys.methods, "MethodOutput")
    assert not hasattr(rphys.learning, "StepOutput")
