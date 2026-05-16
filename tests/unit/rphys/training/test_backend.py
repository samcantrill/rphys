from __future__ import annotations

from rphys.data import Batch
from rphys.learning import LoopContext, LoopMode, StepOutput
from rphys.metrics import MetricValue
from rphys.training import NativeTrainingEngine, TrainingPlan, TrainingStatus
from rphys.training.events import TrainingEvent


class FakeScalar:
    def __init__(self, calls: list[str], value: float = 1.0) -> None:
        self.calls = calls
        self.value = value

    def backward(self) -> None:
        self.calls.append("backward")


class RecordingOptimizer:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def zero_grad(self) -> None:
        self.calls.append("zero_grad")

    def step(self) -> None:
        self.calls.append("optimizer_step")


class RecordingScheduler:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def step(self) -> None:
        self.calls.append("scheduler_step")


class RecordingLearner:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls
        self.contexts: list[LoopContext] = []

    def step(self, batch: Batch, context: LoopContext) -> StepOutput:
        self.contexts.append(context)
        self.calls.append(f"step:{context.mode.value}:{context.step_index}")
        objective = FakeScalar(self.calls, value=0.5) if context.mode is LoopMode.TRAIN else None
        return StepOutput(
            objective=objective,
            metric_values={"mae": MetricValue(0.5, unit="bpm")},
            metadata={"mode": context.mode.value},
        )


class RecordingSink:
    def __init__(self) -> None:
        self.events: list[TrainingEvent] = []

    def record(self, event: TrainingEvent) -> None:
        self.events.append(event)


def test_native_fit_runs_train_loop_with_device_backward_optimizer_and_scheduler_order() -> None:
    calls: list[str] = []

    def move(batch: Batch) -> Batch:
        calls.append("device_mover")
        return batch

    plan = TrainingPlan(
        train_batches=(Batch(), Batch()),
        max_epochs=1,
        device_mover=move,
        optimizer=RecordingOptimizer(calls),
        scheduler=RecordingScheduler(calls),
    )
    learner = RecordingLearner(calls)

    result = NativeTrainingEngine().fit(plan, learner)

    assert result.status is TrainingStatus.COMPLETED
    assert result.mode is LoopMode.TRAIN
    assert result.step_count == 2
    assert result.batch_count == 2
    assert result.epoch_count == 1
    assert result.last_step is not None
    assert result.last_step.objective == 0.5
    assert result.metrics["mae"].value == 0.5
    assert calls == [
        "device_mover",
        "zero_grad",
        "step:train:0",
        "backward",
        "optimizer_step",
        "scheduler_step",
        "device_mover",
        "zero_grad",
        "step:train:1",
        "backward",
        "optimizer_step",
        "scheduler_step",
    ]


def test_native_engine_emits_observer_events_and_unavailable_profiles() -> None:
    sink = RecordingSink()
    plan = TrainingPlan(train_batches=(Batch(),), event_sinks=(sink,))
    learner = RecordingLearner([])

    result = NativeTrainingEngine().fit(plan, learner)

    assert [event.phase.value for event in sink.events] == [
        "loop_started",
        "step_started",
        "step_completed",
        "loop_completed",
    ]
    assert result.profiles[0].name == "native.step"
    assert result.profiles[0].status == "unavailable"


def test_native_engine_respects_step_limits_and_builds_contexts() -> None:
    calls: list[str] = []
    learner = RecordingLearner(calls)
    plan = TrainingPlan(train_batches=(Batch(), Batch()), max_epochs=3, max_train_steps=3)

    result = NativeTrainingEngine().fit(plan, learner)

    assert result.step_count == 3
    assert [context.step_index for context in learner.contexts] == [0, 1, 2]
    assert [context.batch_index for context in learner.contexts] == [0, 1, 0]
    assert [context.epoch_index for context in learner.contexts] == [0, 0, 1]


def test_native_validate_test_and_predict_do_not_call_backward_or_optimizer() -> None:
    calls: list[str] = []
    plan = TrainingPlan(
        validation_batches=(Batch(),),
        test_batches=(Batch(),),
        predict_batches=(Batch(),),
        optimizer=RecordingOptimizer(calls),
        scheduler=RecordingScheduler(calls),
    )
    learner = RecordingLearner(calls)
    engine = NativeTrainingEngine()

    assert engine.validate(plan, learner).mode is LoopMode.VALIDATE
    assert engine.test(plan, learner).mode is LoopMode.TEST
    assert engine.predict(plan, learner).mode is LoopMode.PREDICT
    assert calls == ["step:validate:0", "step:test:0", "step:predict:0"]


def test_native_fit_runs_optional_validation_without_train_mechanics() -> None:
    calls: list[str] = []
    plan = TrainingPlan(
        train_batches=(Batch(),),
        validation_batches=(Batch(),),
        optimizer=RecordingOptimizer(calls),
    )
    learner = RecordingLearner(calls)

    result = NativeTrainingEngine().fit(plan, learner)

    assert result.status is TrainingStatus.COMPLETED
    assert result.step_count == 1
    assert result.metadata["validation_step_count"] == 1
    assert calls == [
        "zero_grad",
        "step:train:0",
        "backward",
        "optimizer_step",
        "step:validate:0",
    ]


def test_native_engine_normalizes_missing_batches_and_step_failures() -> None:
    stopped = NativeTrainingEngine().validate(TrainingPlan(), RecordingLearner([]))
    assert stopped.status is TrainingStatus.STOPPED
    assert stopped.failure == "No validate_batches configured."

    class MissingObjectiveLearner:
        def step(self, batch: Batch, context: LoopContext) -> StepOutput:
            return StepOutput()

    failed = NativeTrainingEngine().fit(
        TrainingPlan(train_batches=(Batch(),)),
        MissingObjectiveLearner(),
    )
    assert failed.status is TrainingStatus.FAILED
    assert failed.step_count == 0
    assert "objective" in (failed.failure or "")
