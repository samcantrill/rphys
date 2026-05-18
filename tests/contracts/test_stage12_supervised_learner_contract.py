from __future__ import annotations

from rphys.data import Batch, FieldValue
from rphys.learning import Learner, LoopContext, SupervisedLearner


class PredictOnlyMethod:
    def predict(self, batch: Batch, *, context: object | None = None) -> Batch:
        output = batch.shallow_copy()
        output.set_field("predictions/signal.bvp", FieldValue(batch.require("inputs/signal.bvp")))
        return output


def test_supervised_learner_is_a_structural_learner_with_prediction_pass_through() -> None:
    learner = SupervisedLearner(PredictOnlyMethod())
    batch = Batch({"inputs/signal.bvp": FieldValue([0.1, 0.2])})

    output = learner.step(batch, LoopContext("predict", split="heldout"))

    assert isinstance(learner, Learner)
    assert isinstance(output, Batch)
    assert output.require("predictions/signal.bvp") == [0.1, 0.2]
    assert not batch.has("predictions/signal.bvp")


def test_supervised_learner_does_not_expose_training_loop_or_export_lifecycle() -> None:
    learner = SupervisedLearner(PredictOnlyMethod())

    for forbidden in [
        "fit",
        "validate",
        "test",
        "predict",
        "backward",
        "optimizer_step",
        "scheduler_step",
        "zero_grad",
        "save_checkpoint",
        "export_predictions",
        "train_pipeline",
        "eval_pipeline",
        "inference_pipeline",
    ]:
        assert not hasattr(learner, forbidden)
