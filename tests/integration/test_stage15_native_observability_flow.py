from __future__ import annotations

from rphys.data import Batch, FieldValue
from rphys.learning import LoopContext
from rphys.metrics import MetricValue
from rphys.training import (
    AsyncTrainingProfileWriter,
    CheckpointCatalog,
    CheckpointPrunePolicy,
    CheckpointPruneResult,
    CheckpointRef,
    CheckpointRefStatus,
    CheckpointResultStatus,
    CheckpointSavePolicy,
    CheckpointSelection,
    CheckpointSelectionMode,
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
    TrainingOutputSpec,
    TrainingPlan,
    TrainingStatus,
)


class FakeScalar:
    def __init__(self, value: float = 0.5) -> None:
        self.value = value
        self.backward_calls = 0

    def backward(self) -> None:
        self.backward_calls += 1


class SyntheticLearner:
    def step(self, batch: Batch, context: LoopContext) -> Batch:
        output = batch.shallow_copy()
        if context.mode.value == "train":
            output.set_field("objectives/custom.training.total", FieldValue(FakeScalar()))
        output.set_field("metrics/custom.training.mae", FieldValue(MetricValue(0.5, unit="bpm")))
        return output


class StepCompletedProbe:
    def collect(self, context: dict[object, object]) -> tuple[ModelProbeSummary, ...]:
        if context["hook_point"] != "step_completed":
            return ()
        return (
            ModelProbeSummary(
                "native-model-probe",
                "gradient_norm",
                hook_point=ProbeHookPoint.STEP_COMPLETED,
                selector=ProbeSelector(ProbeSelectorMode.ALL),
                cadence=ProbeCadence(),
                value=0.25,
                run_id=str(context["run_id"]),
                timeline_id=str(context["timeline_id"]),
                split=str(context["split"]),
                step_index=int(context["step_index"]),
            ),
        )


def test_stage15_native_fit_records_profile_resource_probe_writer_and_checkpoint_evidence() -> None:
    clock_values = [1.0 + index * 0.1 for index in range(80)]

    def clock() -> float:
        return clock_values.pop(0)

    backend = InMemoryProfileWriterBackend()
    writer = AsyncTrainingProfileWriter(backend, queue_capacity=128, clock=clock)
    monitor = ResourceMonitor(
        FakeCPUResourceProbe(values=(12.0, 18.0), probe_id="fake-cpu"),
        execution_mode=ResourceMonitorExecutionMode.INLINE,
        clock=clock,
        run_id="run-stage15",
        timeline_id="timeline-stage15",
    )
    saved: list[CheckpointRef] = []

    def save_hook(context: dict[str, object]) -> CheckpointRef:
        ref = CheckpointRef(
            f"ckpt-{len(saved)}",
            run_id=str(context["run_id"]),
            timeline_id=str(context["timeline_id"]),
            step=int(context["step_index"] or 0),
            timestamp=5.0 + len(saved),
            sequence_id=len(saved),
            status=CheckpointRefStatus.COMPLETED,
            metric_name="metrics/custom.training.mae",
            metric_direction="min",
            metric_value=0.5,
            metadata={"reason": str(context["reason"])},
        )
        saved.append(ref)
        return ref

    def prune_hook(catalog: CheckpointCatalog) -> CheckpointPruneResult:
        return CheckpointPruneResult(
            status=CheckpointResultStatus.COMPLETED,
            kept=catalog.refs[-1:],
            keep_count=1,
            run_id="run-stage15",
            timeline_id="timeline-stage15",
        )

    previous = CheckpointRef(
        "ckpt-previous",
        run_id="run-stage15",
        timeline_id="timeline-stage15",
        step=0,
        timestamp=1.0,
        sequence_id=0,
        status=CheckpointRefStatus.COMPLETED,
    )
    plan = TrainingPlan(
        train_batches=(Batch(),),
        validation_batches=(Batch(),),
        output_spec=TrainingOutputSpec(
            objective="objectives/custom.training.total",
            metrics=("metrics/custom.training.mae",),
        ),
        resource_monitors=(monitor,),
        profile_writers=(writer,),
        training_probes=(StepCompletedProbe(),),
        checkpoint_catalog=CheckpointCatalog((previous,)),
        checkpoint_restore_selection=CheckpointSelection(CheckpointSelectionMode.LATEST_COMPLETED),
        checkpoint_save_policy=CheckpointSavePolicy(by_step=1, on_final=True),
        checkpoint_save_hook=save_hook,
        checkpoint_prune_policy=CheckpointPrunePolicy(keep_recent=1),
        checkpoint_prune_hook=prune_hook,
        run_id="run-stage15",
        timeline_id="timeline-stage15",
    )

    result = NativeTrainingEngine().fit(plan, SyntheticLearner())

    assert result.status is TrainingStatus.COMPLETED
    assert result.training_profile is not None
    profile = result.training_profile
    assert profile.events(timeline_id="timeline-stage15")
    assert profile.resource_samples(metric_kind=ResourceMetricKind.CPU_UTILIZATION)
    assert profile.monitor_lifecycle_records
    assert profile.writer_results
    assert backend.written_records
    assert profile.probe_results_for(probe_id="native-model-probe")
    assert any(getattr(item, "selection", None) is not None for item in profile.checkpoint_results)
    assert any(getattr(item, "ref_id", None) == result.checkpoint_id for item in profile.checkpoint_results)
    assert result.checkpoint_id in {ref.ref_id for ref in saved}
    assert result.metadata["validation_step_count"] == 1
