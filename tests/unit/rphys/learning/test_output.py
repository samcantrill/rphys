from __future__ import annotations

import pytest

from rphys.data import Batch, FieldValue, Sample
from rphys.errors import RemotePhysLearningError
from rphys.learning import BackwardableScalar, StepOutput, require_backwardable_scalar
from rphys.methods import MethodOutput
from rphys.metrics import MetricValue


class FakeScalar:
    def __init__(self) -> None:
        self.backward_calls = 0

    def backward(self) -> None:
        self.backward_calls += 1


def test_backwardable_scalar_accepts_minimal_backward_surface() -> None:
    scalar = FakeScalar()

    returned = require_backwardable_scalar(scalar)
    returned.backward()

    assert isinstance(scalar, BackwardableScalar)
    assert scalar.backward_calls == 1


def test_backwardable_scalar_rejects_plain_values() -> None:
    with pytest.raises(RemotePhysLearningError) as exc_info:
        require_backwardable_scalar(1.0)

    assert exc_info.value.context["expected"] == "object with backward()"
    assert exc_info.value.context["actual"] == "float"


@pytest.mark.parametrize(
    "prediction",
    [
        None,
        MethodOutput(fields={"predictions/signal.bvp": FieldValue([0.1])}),
        Sample({"inputs/signal.bvp": FieldValue([0.1])}),
        Batch({"inputs/signal.bvp": FieldValue([[0.1]])}),
    ],
)
def test_step_output_accepts_opaque_prediction_union(prediction: object) -> None:
    output = StepOutput(predictions=prediction)

    assert output.predictions is prediction


def test_step_output_rejects_unsupported_prediction_materialization() -> None:
    with pytest.raises(RemotePhysLearningError) as exc_info:
        StepOutput(predictions={"predictions/signal.bvp": [0.1]})  # type: ignore[arg-type]

    assert exc_info.value.context["field"] == "predictions"
    assert exc_info.value.context["expected"] == "MethodOutput | Sample | Batch | None"


def test_step_output_freezes_primitive_summaries_and_metric_values() -> None:
    metric = MetricValue(0.87, metadata={"scope": "batch"})
    diagnostics = {"flat_signal": False}
    output = StepOutput(
        objective=FakeScalar(),
        metric_values={"mae": metric},
        diagnostics=diagnostics,
        metadata={"mode": "train"},
        provenance={"stage": "unit"},
    )
    diagnostics["flat_signal"] = True

    assert output.objective is not None
    assert output.metric_values == {"mae": metric}
    assert output.diagnostics == {"flat_signal": False}
    assert output.metadata == {"mode": "train"}
    assert output.provenance == {"stage": "unit"}

    with pytest.raises(TypeError):
        output.metric_values["rmse"] = metric  # type: ignore[index]
    with pytest.raises(TypeError):
        output.metadata["mode"] = "predict"  # type: ignore[index]


def test_step_output_rejects_non_primitive_metadata_and_invalid_metrics() -> None:
    with pytest.raises(RemotePhysLearningError) as metadata_error:
        StepOutput(metadata={"history": [1, 2]})
    assert metadata_error.value.context["field"] == "metadata"
    assert metadata_error.value.context["key"] == "history"

    with pytest.raises(RemotePhysLearningError) as metric_error:
        StepOutput(metric_values={"loss": 1.2})  # type: ignore[dict-item]
    assert metric_error.value.context["field"] == "metric_values"
    assert metric_error.value.context["key"] == "loss"
