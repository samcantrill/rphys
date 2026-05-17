from __future__ import annotations

import pytest

from rphys.data import Batch, FieldValue
from rphys.learning import Learner, LoopContext, LoopMode


class FakeLearner:
    def __init__(self) -> None:
        self.contexts: list[LoopContext] = []

    def step(self, batch: Batch, context: LoopContext) -> Batch:
        self.contexts.append(context)
        output = batch.shallow_copy()
        output.set_field("predictions/signal.bvp", FieldValue(batch.require("inputs/signal.bvp")))
        return output


def test_learner_is_structural_and_returns_step_output() -> None:
    learner = FakeLearner()
    batch = Batch({"inputs/signal.bvp": FieldValue([0.1, 0.2])})
    context = LoopContext(LoopMode.PREDICT, split="heldout", batch_index=0)

    output = learner.step(batch, context)

    assert isinstance(learner, Learner)
    assert isinstance(output, Batch)
    assert output.require("predictions/signal.bvp") == [0.1, 0.2]
    assert learner.contexts == [context]


def test_learner_contract_has_no_loop_or_training_lifecycle_methods() -> None:
    learner = FakeLearner()

    for forbidden in [
        "fit",
        "validate",
        "test",
        "predict",
        "backward",
        "optimizer_step",
        "scheduler_step",
        "save_checkpoint",
        "export_predictions",
    ]:
        assert not hasattr(learner, forbidden)


def test_learner_protocol_rejects_objects_without_step() -> None:
    assert not isinstance(object(), Learner)
