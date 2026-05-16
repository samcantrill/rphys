from __future__ import annotations

import pytest

from rphys.data import FieldValue
from rphys.errors import RemotePhysLearningError
from rphys.learning import LoopContext, LoopMode, StepOutput
from rphys.methods import MethodOutput


class FakeScalar:
    def backward(self) -> None:
        return None


def test_step_output_preserves_method_output_predictions_as_opaque_patch() -> None:
    method_output = MethodOutput(fields={"predictions/signal.bvp": FieldValue([0.1])})
    output = StepOutput(
        predictions=method_output,
        objective=None,
        metadata={"prediction_contract": "opaque"},
        provenance={"revisit": "stage-13"},
    )

    assert output.predictions is method_output
    assert not hasattr(output, "materialized_predictions")
    assert not hasattr(output, "export_path")
    assert output.provenance == {"revisit": "stage-13"}


def test_train_step_can_carry_backwardable_objective_without_backend_import() -> None:
    output = StepOutput(objective=FakeScalar())

    assert output.objective is not None
    output.objective.backward()


def test_plain_numeric_objective_fails_loudly_for_native_backward_boundary() -> None:
    with pytest.raises(RemotePhysLearningError) as exc_info:
        StepOutput(objective=1.0)

    assert exc_info.value.context["owner"] == "BackwardableScalar"


def test_loop_context_records_split_without_conflating_it_with_mode() -> None:
    context = LoopContext(LoopMode.PREDICT, split="train")

    assert context.mode is LoopMode.PREDICT
    assert context.split == "train"
