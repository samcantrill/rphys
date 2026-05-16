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
    ParameterView,
    PredictionContext,
    StateEntry,
    StateLoadResult,
    StateView,
    TrainableMethod,
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
    model: ScaleModel
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

    def state(self) -> StateView:
        return StateView(
            [StateEntry("factor", self.model.factor, metadata={"kind": "scale"})],
            provenance={"method": "synthetic-adapter"},
        )

    def load_state(
        self,
        state: StateView,
        *,
        strict: bool = True,
    ) -> StateLoadResult:
        incoming = {entry.name for entry in state.entries}
        missing = [] if "factor" in incoming else ["factor"]
        unexpected = sorted(incoming - {"factor"})
        if strict and (missing or unexpected):
            return StateLoadResult(
                loaded=sorted(incoming & {"factor"}),
                missing=missing,
                unexpected=unexpected,
                diagnostics={"strict": strict},
            )
        if "factor" in incoming:
            self.model.factor = float(state.entry("factor").value)
        return StateLoadResult(
            loaded=sorted(incoming & {"factor"}),
            missing=missing,
            unexpected=unexpected,
            diagnostics={"strict": strict},
        )

    def parameters(self) -> tuple[ParameterView, ...]:
        return (
            ParameterView(
                "factor",
                self.model,
                trainable=True,
                requires_update=True,
                metadata={"kind": "backend-native-callable"},
                provenance={"backend": "synthetic-runtime"},
            ),
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


def test_synthetic_trainable_method_state_records_compose_with_prediction_flow() -> None:
    batch = collate_samples(
        (
            Sample({SIGNAL: FieldValue(0.1, schema="signal.bvp.v1", collate_policy="list")}),
            Sample({SIGNAL: FieldValue(0.2, schema="signal.bvp.v1", collate_policy="list")}),
        )
    )
    method = AdapterMethod(
        model=ScaleModel(2.0),
        input_adapter=MethodInputAdapter(
            [MethodInputSpec("signal", SIGNAL, expected_type=list, schema="signal.bvp.v1")]
        ),
        output_adapter=MethodOutputAdapter(
            [MethodOutputSpec("prediction", PREDICTION, expected_type=list)]
        ),
    )

    state = method.state()
    parameters = method.parameters()
    load_result = method.load_state(StateView([StateEntry("factor", 4.0)]), strict=True)
    output = method.predict(batch, context=PredictionContext(provenance={"run": "state"}))
    applied = apply_method_output(output, batch)

    assert isinstance(method, Method)
    assert isinstance(method, TrainableMethod)
    assert isinstance(method.model, Model)
    assert state.entry("factor").value == 2.0
    assert state.provenance == {"method": "synthetic-adapter"}
    assert parameters[0].handle is method.model
    assert parameters[0].trainable is True
    assert load_result.success is True
    assert method.model.factor == 4.0
    assert output.fields[PREDICTION].payload == [0.4, 0.8]
    assert applied.require(PREDICTION) == [0.4, 0.8]
    assert not batch.has(PREDICTION)
