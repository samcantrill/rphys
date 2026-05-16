from __future__ import annotations

from dataclasses import dataclass

from rphys.data import Batch, FieldValue, collate_samples, uncollate_batch
from rphys.data.locators import FieldLocator
from rphys.data.containers import Sample
from rphys.methods import (
    Method,
    MethodInputAdapter,
    MethodInputSpec,
    MethodOutput,
    MethodOutputAdapter,
    MethodOutputSpec,
    PredictionContext,
    apply_method_output,
)
from rphys.models import Model


SIGNAL = FieldLocator.parse("inputs/signal.bvp.source")
PREDICTION = FieldLocator.parse("predictions/signal.bvp.estimated")


@dataclass
class ScaleModel:
    factor: float

    def __call__(self, values: list[float]) -> list[float]:
        return [value * self.factor for value in values]


@dataclass
class AdapterMethod:
    model: Model[list[float], list[float]]
    input_adapter: MethodInputAdapter
    output_adapter: MethodOutputAdapter

    def predict(
        self,
        batch: Batch,
        *,
        context: PredictionContext | None = None,
    ) -> MethodOutput:
        inputs = self.input_adapter.extract(batch)
        prediction = self.model(inputs["signal"])
        return self.output_adapter.adapt(
            {"prediction": prediction},
            provenance={"context": context.provenance["run"]} if context is not None else {},
        )


def test_synthetic_method_prediction_flow_uses_explicit_patch_application() -> None:
    samples = (
        Sample({SIGNAL: FieldValue(0.1, schema="signal.bvp.v1", collate_policy="list")}),
        Sample({SIGNAL: FieldValue(0.2, schema="signal.bvp.v1", collate_policy="list")}),
    )
    batch = collate_samples(samples)
    method = AdapterMethod(
        model=ScaleModel(2.0),
        input_adapter=MethodInputAdapter(
            [MethodInputSpec("signal", SIGNAL, expected_type=list, schema="signal.bvp.v1")]
        ),
        output_adapter=MethodOutputAdapter(
            [
                MethodOutputSpec(
                    "prediction",
                    PREDICTION,
                    expected_type=list,
                    schema="signal.bvp.v1",
                )
            ]
        ),
    )

    output = method.predict(batch, context=PredictionContext(provenance={"run": "unit"}))
    applied = apply_method_output(output, batch)
    round_tripped = uncollate_batch(batch)

    assert isinstance(method, Method)
    assert output.fields[PREDICTION].payload == [0.2, 0.4]
    assert output.provenance == {"context": "unit"}
    assert not batch.has(PREDICTION)
    assert applied.require(PREDICTION) == [0.2, 0.4]
    assert round_tripped[0].require(SIGNAL) == 0.1
    assert round_tripped[1].require(SIGNAL) == 0.2
