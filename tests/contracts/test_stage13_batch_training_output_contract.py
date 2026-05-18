from __future__ import annotations

import pytest

from rphys.data import Batch, BatchOutputFieldSpec, BatchOutputSpec, FieldValue
from rphys.errors import RemotePhysDataError, RemotePhysTrainingError
from rphys.learning import LoopContext, LoopMode, require_backwardable_scalar
from rphys.training import TrainingOutputSpec


class FakeScalar:
    def backward(self) -> None:
        return None


def test_batch_output_spec_replaces_method_output_patch_contract() -> None:
    spec = BatchOutputSpec(
        [BatchOutputFieldSpec("bvp", "predictions/signal.bvp", expected_type=list)]
    )

    output = spec.build([0.1, 0.2])

    assert isinstance(output, Batch)
    assert output.require("predictions/signal.bvp") == [0.1, 0.2]
    assert not hasattr(output, "materialized_predictions")
    assert not hasattr(output, "export_path")


def test_train_step_objective_is_declared_by_training_output_spec() -> None:
    spec = TrainingOutputSpec(objective="objectives/custom.training.total")
    output = Batch({"objectives/custom.training.total": FieldValue(FakeScalar())})

    spec.validate_batch(output, "train")
    require_backwardable_scalar(spec.objective_value(output, "train"))

    with pytest.raises(RemotePhysTrainingError):
        spec.validate_batch(Batch(), "train")
    with pytest.raises(RemotePhysTrainingError):
        spec.validate_batch(Batch({"objectives/custom.training.total": FieldValue(1.0)}), "train")


def test_plain_batch_output_spec_rejects_target_role_as_output_by_default() -> None:
    with pytest.raises(RemotePhysDataError):
        BatchOutputFieldSpec("target", "targets/signal.bvp")


def test_loop_context_records_split_without_conflating_it_with_mode() -> None:
    context = LoopContext(LoopMode.PREDICT, split="train")

    assert context.mode is LoopMode.PREDICT
    assert context.split == "train"
