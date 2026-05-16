from __future__ import annotations

from dataclasses import dataclass

from rphys.data import Batch, FieldValue
from rphys.data.locators import FieldLocator
from rphys.methods import (
    Method,
    MethodInputAdapter,
    MethodInputSpec,
    MethodOutput,
    MethodOutputAdapter,
    MethodOutputSpec,
    PredictionContext,
)


INPUT = FieldLocator.parse("inputs/signal.bvp.source")
PREDICTION = FieldLocator.parse("predictions/signal.bvp.estimated")


@dataclass
class EchoMethod:
    scale: float = 1.0

    def predict(
        self,
        batch: Batch,
        *,
        context: PredictionContext | None = None,
    ) -> MethodOutput:
        values = batch.require(INPUT, expected_type=list)
        metadata = {"source": context.metadata["source"]} if context is not None else {}
        return MethodOutput(
            fields={
                PREDICTION: FieldValue(
                    [value * self.scale for value in values],
                    schema=batch.field(INPUT).schema,
                )
            },
            metadata=metadata,
            provenance={"method": "echo"},
        )


@dataclass
class AdapterBackedEchoMethod:
    input_adapter: MethodInputAdapter
    output_adapter: MethodOutputAdapter

    def predict(
        self,
        batch: Batch,
        *,
        context: PredictionContext | None = None,
    ) -> MethodOutput:
        inputs = self.input_adapter.extract(batch)
        scaled = [value * 2.0 for value in inputs["signal"]]
        return self.output_adapter.adapt(
            {"prediction": scaled},
            metadata={"source": context.metadata["source"]} if context is not None else {},
        )


def test_method_contract_is_structural_and_returns_method_output_patch() -> None:
    method = EchoMethod(scale=2.0)
    batch = Batch({INPUT: FieldValue([0.1, 0.2], schema="signal.bvp.v1")})
    before_items = batch.field_items()

    output = method.predict(
        batch,
        context=PredictionContext(metadata={"source": "contract"}),
    )

    assert isinstance(method, Method)
    assert isinstance(output, MethodOutput)
    assert output.fields[PREDICTION].payload == [0.2, 0.4]
    assert output.fields[PREDICTION].schema == "signal.bvp.v1"
    assert output.metadata == {"source": "contract"}
    assert output.provenance == {"method": "echo"}
    assert batch.field_items() == before_items
    assert not isinstance(output, Batch)


def test_adapter_backed_method_contract_keeps_prediction_patch_only() -> None:
    method = AdapterBackedEchoMethod(
        input_adapter=MethodInputAdapter(
            [
                MethodInputSpec(
                    "signal",
                    INPUT,
                    expected_type=list,
                    schema="signal.bvp.v1",
                )
            ]
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
    batch = Batch({INPUT: FieldValue([0.1, 0.2], schema="signal.bvp.v1")})

    output = method.predict(
        batch,
        context=PredictionContext(metadata={"source": "adapter-contract"}),
    )

    assert isinstance(method, Method)
    assert output.fields[PREDICTION].payload == [0.2, 0.4]
    assert output.fields[PREDICTION].schema == "signal.bvp.v1"
    assert output.metadata == {"source": "adapter-contract"}
    assert not batch.has(PREDICTION)


def test_method_contract_does_not_define_training_export_or_metric_behavior() -> None:
    method = EchoMethod()

    for forbidden in [
        "fit",
        "train",
        "training_step",
        "validation_step",
        "loss",
        "metric",
        "export",
        "save",
        "configure_optimizers",
    ]:
        assert not hasattr(method, forbidden)
