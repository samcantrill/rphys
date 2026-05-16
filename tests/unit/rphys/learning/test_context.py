from __future__ import annotations

import pytest

from rphys.errors import RemotePhysLearningError
from rphys.learning import LoopContext, LoopMode


def test_loop_mode_coerces_supported_values() -> None:
    assert LoopMode.coerce("train") is LoopMode.TRAIN
    assert LoopMode.coerce(LoopMode.PREDICT) is LoopMode.PREDICT
    assert [mode.value for mode in LoopMode] == ["train", "validate", "test", "predict"]


def test_loop_mode_rejects_unsupported_values() -> None:
    with pytest.raises(RemotePhysLearningError) as exc_info:
        LoopMode.coerce("validation")

    assert exc_info.value.context["expected"] == ("train", "validate", "test", "predict")
    assert exc_info.value.context["actual"] == "validation"


def test_loop_context_preserves_mode_split_indexes_and_primitive_context() -> None:
    metadata = {"subject": "s01", "has_label": True}
    context = LoopContext(
        "train",
        split="subject-heldout",
        epoch_index=2,
        step_index=7,
        batch_index=3,
        metadata=metadata,
        provenance={"loader": "synthetic"},
    )
    metadata["subject"] = "s02"

    assert context.mode is LoopMode.TRAIN
    assert context.split == "subject-heldout"
    assert context.epoch_index == 2
    assert context.step_index == 7
    assert context.batch_index == 3
    assert context.metadata == {"subject": "s01", "has_label": True}
    assert context.provenance == {"loader": "synthetic"}

    with pytest.raises(TypeError):
        context.metadata["subject"] = "mutated"  # type: ignore[index]


def test_loop_context_rejects_invalid_indexes_and_context_mappings() -> None:
    with pytest.raises(RemotePhysLearningError) as index_error:
        LoopContext("train", step_index=-1)
    assert index_error.value.context["field"] == "step_index"

    with pytest.raises(RemotePhysLearningError) as bool_error:
        LoopContext("train", batch_index=True)  # type: ignore[arg-type]
    assert bool_error.value.context["field"] == "batch_index"

    with pytest.raises(RemotePhysLearningError) as key_error:
        LoopContext("train", metadata={1: "bad"})
    assert key_error.value.context["field"] == "metadata"

    with pytest.raises(RemotePhysLearningError) as value_error:
        LoopContext("train", provenance={"history": ["not", "primitive"]})
    assert value_error.value.context["key"] == "history"


def test_loop_context_keeps_mode_and_split_distinct() -> None:
    context = LoopContext(LoopMode.VALIDATE, split="train")

    assert context.mode is LoopMode.VALIDATE
    assert context.split == "train"
