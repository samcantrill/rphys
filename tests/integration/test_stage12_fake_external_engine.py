from __future__ import annotations

from rphys.data import Batch
from rphys.learning import LoopContext, StepOutput
from rphys.training import Trainer, TrainingPlan, TrainingStatus
from tests.support.stage12_fake_external import FakeExternalEngine, FakeExternalEvidence


class PassiveLearner:
    def step(self, batch: Batch, context: LoopContext) -> StepOutput:
        raise AssertionError("external fake should not call learner.step")


def test_stage12_fake_external_engine_normalizes_result_summaries_without_native_loop() -> None:
    engine = FakeExternalEngine(
        FakeExternalEvidence(
            metrics={"external_loss": 1.0},
            callback_statuses={"callback.progress": "observed"},
            profile_statuses={"external.step": "available"},
        )
    )
    plan = TrainingPlan(train_batches=(Batch(),))
    learner = PassiveLearner()

    result = Trainer(engine=engine).fit(plan, learner)

    assert result.status is TrainingStatus.COMPLETED
    assert result.mode.value == "train"
    assert result.metrics["external_loss"].value == 1.0
    assert result.events[0].status == "observed"
    assert result.profiles[0].status == "available"
    assert engine.calls == [("fit", plan, learner)]
