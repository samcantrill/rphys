from __future__ import annotations

from dataclasses import dataclass

from rphys.data import Batch, FieldValue
from rphys.data.locators import FieldLocator
from rphys.methods import (
    BatchOutputFieldSpec,
    BatchOutputSpec,
    Method,
    MethodInputAdapter,
    MethodInputSpec,
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
    ) -> Batch:
        values = batch.require(INPUT, expected_type=list)
        metadata = {"source": context.metadata["source"]} if context is not None else {}
        output = Batch(
            {
                PREDICTION: FieldValue(
                    [value * self.scale for value in values],
                    schema=batch.field(INPUT).schema,
                    metadata=metadata,
                )
            }
        )
        return output


@dataclass
class AdapterBackedEchoMethod:
    input_adapter: MethodInputAdapter
    output_spec: BatchOutputSpec

    def predict(
        self,
        batch: Batch,
        *,
        context: PredictionContext | None = None,
    ) -> Batch:
        inputs = self.input_adapter.extract(batch)
        scaled = [value * 2.0 for value in inputs["signal"]]
        return self.output_spec.build(
            {"prediction": scaled},
        )


def test_method_contract_is_structural_and_returns_batch_output() -> None:
    method = EchoMethod(scale=2.0)
    batch = Batch({INPUT: FieldValue([0.1, 0.2], schema="signal.bvp.v1")})
    before_items = batch.field_items()

    output = method.predict(
        batch,
        context=PredictionContext(metadata={"source": "contract"}),
    )

    assert isinstance(method, Method)
    assert isinstance(output, Batch)
    assert output.field(PREDICTION).payload == [0.2, 0.4]
    assert output.field(PREDICTION).schema == "signal.bvp.v1"
    assert output.field(PREDICTION).metadata["source"] == "contract"
    assert batch.field_items() == before_items


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
        output_spec=BatchOutputSpec(
            [
                BatchOutputFieldSpec(
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
    assert output.field(PREDICTION).payload == [0.2, 0.4]
    assert output.field(PREDICTION).schema == "signal.bvp.v1"
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
