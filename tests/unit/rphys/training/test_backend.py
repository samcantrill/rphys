from __future__ import annotations

from rphys.data import Batch, FieldValue
from rphys.learning import LoopContext, LoopMode
from rphys.metrics import MetricValue
from rphys.training import (
    AsyncTrainingProfileWriter,
    CheckpointPrunePolicy,
    CheckpointPruneResult,
    CheckpointRef,
    CheckpointRefStatus,
    CheckpointResultStatus,
    CheckpointSavePolicy,
    FakeCPUResourceProbe,
    InMemoryProfileWriterBackend,
    ModelProbeSummary,
    NativeTrainingEngine,
    ProbeCadence,
    ProbeHookPoint,
    ProbeSelector,
    ProbeSelectorMode,
    ResourceMetricKind,
    ResourceMonitor,
    ResourceMonitorExecutionMode,
    TrainingEventPhase,
    TrainingOutputSpec,
    TrainingPlan,
    TrainingStatus,
)
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

    def step(self, batch: Batch, context: LoopContext) -> Batch:
        self.contexts.append(context)
        self.calls.append(f"step:{context.mode.value}:{context.step_index}")
        output = batch.shallow_copy()
        if context.mode is LoopMode.TRAIN:
            output.set_field("objectives/custom.training.total", FieldValue(FakeScalar(self.calls, value=0.5)))
        output.set_field("metrics/custom.training.mae", FieldValue(MetricValue(0.5, unit="bpm")))
        return output


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
        output_spec=TrainingOutputSpec(
            objective="objectives/custom.training.total",
            metrics=("metrics/custom.training.mae",),
        ),
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
    assert result.metrics["metrics/custom.training.mae"].value == 0.5
    assert calls == [
        "device_mover",
        "step:train:0",
        "zero_grad",
        "backward",
        "optimizer_step",
        "scheduler_step",
        "device_mover",
        "step:train:1",
        "zero_grad",
        "backward",
        "optimizer_step",
        "scheduler_step",
    ]


def test_native_engine_emits_observer_events_and_unavailable_profiles() -> None:
    sink = RecordingSink()
    plan = TrainingPlan(
        train_batches=(Batch(),),
        event_sinks=(sink,),
        output_spec=TrainingOutputSpec(objective="objectives/custom.training.total"),
    )
    learner = RecordingLearner([])

    result = NativeTrainingEngine().fit(plan, learner)

    assert [event.phase.value for event in sink.events] == [
        "setup",
        "setup",
        "loop_started",
        "data_wait",
        "device_transfer",
        "step_started",
        "step_completed",
        "loop_completed",
        "teardown",
        "profiling_summary",
        "teardown",
    ]
    assert result.training_profile is not None
    assert result.profiles[0].name == "native.setup"
    assert result.profiles[0].status == "available"


def test_native_engine_attaches_stage15_profile_monitors_writers_probes_and_checkpoints() -> None:
    clock_values = [1.0 + index * 0.1 for index in range(40)]

    def clock() -> float:
        return clock_values.pop(0)

    monitor = ResourceMonitor(
        FakeCPUResourceProbe(values=(10.0, 20.0), probe_id="fake-cpu"),
        execution_mode=ResourceMonitorExecutionMode.INLINE,
        clock=clock,
        run_id="run-1",
        timeline_id="timeline-1",
    )
    writer_backend = InMemoryProfileWriterBackend()
    writer = AsyncTrainingProfileWriter(writer_backend, queue_capacity=64, clock=clock)

    class RecordingProbe:
        def __init__(self) -> None:
            self.hook_points: list[str] = []

        def collect(self, context: dict[object, object]) -> tuple[ModelProbeSummary, ...]:
            hook_point = str(context["hook_point"])
            self.hook_points.append(hook_point)
            if hook_point != "step_completed":
                return ()
            return (
                ModelProbeSummary(
                    "fake-model",
                    "parameter_norm",
                    hook_point=ProbeHookPoint.STEP_COMPLETED,
                    selector=ProbeSelector(ProbeSelectorMode.ALL),
                    cadence=ProbeCadence(),
                    value=1.5,
                    run_id=str(context["run_id"]),
                    timeline_id=str(context["timeline_id"]),
                    split=str(context["split"]),
                    step_index=int(context["step_index"]),
                ),
            )

    probe = RecordingProbe()
    saved_refs: list[CheckpointRef] = []

    def save_hook(context: dict[str, object]) -> CheckpointRef:
        ref = CheckpointRef(
            f"ckpt-{len(saved_refs)}",
            run_id=str(context["run_id"]),
            timeline_id=str(context["timeline_id"]),
            step=int(context["step_index"] or 0),
            timestamp=10.0 + len(saved_refs),
            sequence_id=len(saved_refs),
            status=CheckpointRefStatus.COMPLETED,
            metadata={"reason": str(context["reason"])},
        )
        saved_refs.append(ref)
        return ref

    def prune_hook(catalog: object) -> CheckpointPruneResult:
        refs = getattr(catalog, "refs")
        return CheckpointPruneResult(
            status=CheckpointResultStatus.COMPLETED,
            kept=refs[-1:],
            keep_count=1,
            run_id="run-1",
            timeline_id="timeline-1",
        )

    plan = TrainingPlan(
        train_batches=(Batch(),),
        max_epochs=1,
        output_spec=TrainingOutputSpec(
            objective="objectives/custom.training.total",
            metrics=("metrics/custom.training.mae",),
        ),
        resource_monitors=(monitor,),
        profile_writers=(writer,),
        training_probes=(probe,),
        checkpoint_save_policy=CheckpointSavePolicy(by_step=1, on_final=True),
        checkpoint_save_hook=save_hook,
        checkpoint_prune_policy=CheckpointPrunePolicy(keep_recent=1),
        checkpoint_prune_hook=prune_hook,
        run_id="run-1",
        timeline_id="timeline-1",
    )

    result = NativeTrainingEngine().fit(plan, RecordingLearner([]))

    assert result.status is TrainingStatus.COMPLETED
    assert result.training_profile is not None
    profile = result.training_profile
    assert {event.phase.value for event in profile.events()} >= {
        "setup",
        "data_wait",
        "device_transfer",
        "checkpoint",
        "teardown",
    }
    assert {span.stage_name for span in profile.scalar_spans} >= {
        "setup",
        "data_wait",
        "device_transfer",
        "forward",
        "backward",
        "optimizer_step",
        "checkpoint",
        "teardown",
    }
    assert profile.resource_samples(metric_kind=ResourceMetricKind.CPU_UTILIZATION)
    assert profile.monitor_lifecycle_records
    assert profile.writer_results
    assert writer_backend.written_records
    assert profile.probe_results_for(probe_id="fake-model")
    assert any(getattr(item, "ref_id", None) == result.checkpoint_id for item in profile.checkpoint_results)
    assert result.checkpoint_id in {ref.ref_id for ref in saved_refs}
    assert probe.hook_points


def test_native_engine_records_failure_profile_and_teardown_after_observer_failure() -> None:
    class FailingSink:
        def __init__(self) -> None:
            self.calls = 0

        def record(self, event: TrainingEvent) -> None:
            self.calls += 1
            if event.phase is TrainingEventPhase.STEP_STARTED:
                raise RuntimeError("sink failed")

    sink = FailingSink()
    plan = TrainingPlan(
        train_batches=(Batch(),),
        event_sinks=(sink,),
        output_spec=TrainingOutputSpec(objective="objectives/custom.training.total"),
    )

    result = NativeTrainingEngine().fit(plan, RecordingLearner([]))

    assert result.status is TrainingStatus.FAILED
    assert result.training_profile is not None
    phases = [event.phase.value for event in result.training_profile.events()]
    assert "loop_failed" in phases
    assert "teardown" in phases
    assert "RuntimeError" in (result.failure or "")


def test_native_engine_respects_step_limits_and_builds_contexts() -> None:
    calls: list[str] = []
    learner = RecordingLearner(calls)
    plan = TrainingPlan(
        train_batches=(Batch(), Batch()),
        max_epochs=3,
        max_train_steps=3,
        output_spec=TrainingOutputSpec(objective="objectives/custom.training.total"),
    )

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
        output_spec=TrainingOutputSpec(objective="objectives/custom.training.total"),
    )
    learner = RecordingLearner(calls)

    result = NativeTrainingEngine().fit(plan, learner)

    assert result.status is TrainingStatus.COMPLETED
    assert result.step_count == 1
    assert result.metadata["validation_step_count"] == 1
    assert calls == [
        "step:train:0",
        "zero_grad",
        "backward",
        "optimizer_step",
        "step:validate:0",
    ]


def test_native_engine_normalizes_missing_batches_and_step_failures() -> None:
    stopped = NativeTrainingEngine().validate(TrainingPlan(), RecordingLearner([]))
    assert stopped.status is TrainingStatus.STOPPED
    assert stopped.failure == "No validate_batches configured."

    class MissingObjectiveLearner:
        def step(self, batch: Batch, context: LoopContext) -> Batch:
            return Batch()

    failed = NativeTrainingEngine().fit(
        TrainingPlan(
            train_batches=(Batch(),),
            output_spec=TrainingOutputSpec(objective="objectives/custom.training.total"),
        ),
        MissingObjectiveLearner(),
    )
    assert failed.status is TrainingStatus.FAILED
    assert failed.step_count == 0
    assert "objective" in (failed.failure or "")
