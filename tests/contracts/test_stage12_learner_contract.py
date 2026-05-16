from __future__ import annotations

import pytest

from rphys.data import Batch, FieldValue
from rphys.learning import Learner, LoopContext, LoopMode, StepOutput
from rphys.methods import MethodOutput


class FakeLearner:
    def __init__(self) -> None:
        self.contexts: list[LoopContext] = []

    def step(self, batch: Batch, context: LoopContext) -> StepOutput:
        self.contexts.append(context)
        return StepOutput(
            predictions=MethodOutput(
                fields={"predictions/signal.bvp": FieldValue(batch.require("inputs/signal.bvp"))}
            ),
            metadata={"mode": context.mode.value},
            provenance={"source": "contract-fake"},
        )


def test_learner_is_structural_and_returns_step_output() -> None:
    learner = FakeLearner()
    batch = Batch({"inputs/signal.bvp": FieldValue([0.1, 0.2])})
    context = LoopContext(LoopMode.PREDICT, split="heldout", batch_index=0)

    output = learner.step(batch, context)

    assert isinstance(learner, Learner)
    assert output.predictions is not None
    assert output.metadata == {"mode": "predict"}
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
