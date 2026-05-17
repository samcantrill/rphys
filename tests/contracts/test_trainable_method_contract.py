from __future__ import annotations

from dataclasses import dataclass

from rphys.data import Batch, FieldValue
from rphys.data.locators import FieldLocator
from rphys.methods import (
    ParameterView,
    PredictionContext,
    StateEntry,
    StateLoadResult,
    StateView,
    StatefulMethod,
    TrainableMethod,
)


INPUT = FieldLocator.parse("inputs/signal.bvp.source")
PREDICTION = FieldLocator.parse("predictions/signal.bvp.estimated")


@dataclass
class SyntheticBackendParameter:
    value: float


class SyntheticBackendMethod:
    def __init__(self) -> None:
        self.offset = 0.5
        self.scale = SyntheticBackendParameter(2.0)

    def predict(
        self,
        batch: Batch,
        *,
        context: PredictionContext | None = None,
    ) -> Batch:
        values = batch.require(INPUT, expected_type=list)
        return Batch(
            {
                PREDICTION: FieldValue(
                    [self.scale.value * value + self.offset for value in values],
                    schema=batch.field(INPUT).schema,
                )
            }
        )

    def state(self) -> StateView:
        return StateView(
            [
                StateEntry("offset", self.offset, metadata={"kind": "scalar"}),
                StateEntry("scale", self.scale, metadata={"kind": "backend-parameter"}),
            ],
            provenance={"backend": "synthetic-array-runtime"},
        )

    def load_state(
        self,
        state: StateView,
        *,
        strict: bool = True,
    ) -> StateLoadResult:
        current = {"offset", "scale"}
        incoming = {entry.name for entry in state.entries}
        missing = sorted(current - incoming)
        unexpected = sorted(incoming - current)
        if strict and (missing or unexpected):
            return StateLoadResult(
                loaded=sorted(current & incoming),
                missing=missing,
                unexpected=unexpected,
                diagnostics={"strict": strict},
            )
        if "offset" in incoming:
            self.offset = float(state.entry("offset").value)
        if "scale" in incoming:
            value = state.entry("scale").value
            self.scale = (
                value
                if isinstance(value, SyntheticBackendParameter)
                else SyntheticBackendParameter(float(value))
            )
        return StateLoadResult(
            loaded=sorted(current & incoming),
            missing=missing,
            unexpected=unexpected,
            diagnostics={"strict": strict},
        )

    def parameters(self) -> tuple[ParameterView, ...]:
        return (
            ParameterView(
                "scale",
                self.scale,
                trainable=True,
                requires_update=True,
                metadata={"kind": "backend-native"},
                provenance={"backend": "synthetic-array-runtime"},
            ),
        )


def test_trainable_method_contract_uses_backend_neutral_records() -> None:
    method = SyntheticBackendMethod()
    batch = Batch({INPUT: FieldValue([0.1, 0.2], schema="signal.bvp.v1")})

    output = method.predict(batch)
    state = method.state()
    parameters = method.parameters()

    assert isinstance(method, StatefulMethod)
    assert isinstance(method, TrainableMethod)
    assert output.require(PREDICTION) == [0.7, 0.9]
    assert state.entry("offset").value == 0.5
    assert state.entry("scale").value is method.scale
    assert state.provenance == {"backend": "synthetic-array-runtime"}
    assert parameters[0].name == "scale"
    assert isinstance(parameters[0].handle, SyntheticBackendParameter)
    assert parameters[0].trainable is True
    assert parameters[0].requires_update is True


def test_strict_load_reports_missing_and_unexpected_state_without_checkpoint_policy() -> None:
    method = SyntheticBackendMethod()
    result = method.load_state(
        StateView(
            [
                StateEntry("offset", 1.0),
                StateEntry("extra", 3.0),
            ]
        ),
        strict=True,
    )

    assert result.success is False
    assert result.loaded == ("offset",)
    assert result.missing == ("scale",)
    assert result.unexpected == ("extra",)
    assert result.diagnostics == {"strict": True}
    assert method.offset == 0.5


def test_permissive_load_updates_known_state_and_ignores_unexpected_names() -> None:
    method = SyntheticBackendMethod()
    result = method.load_state(
        StateView(
            [
                StateEntry("offset", 1.0),
                StateEntry("extra", 3.0),
            ]
        ),
        strict=False,
    )

    assert result.success is False
    assert result.missing == ("scale",)
    assert result.unexpected == ("extra",)
    assert method.offset == 1.0


def test_trainable_method_contract_has_no_framework_lifecycle_or_device_hooks() -> None:
    method = SyntheticBackendMethod()

    for forbidden in [
        "state_dict",
        "load_state_dict",
        "training_step",
        "validation_step",
        "configure_optimizers",
        "to",
        "compile",
        "save_checkpoint",
        "optimizer",
        "device",
    ]:
        assert not hasattr(method, forbidden)
