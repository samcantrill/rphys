from __future__ import annotations

from dataclasses import asdict

from rphys.training import (
    CheckpointResultStatus,
    CheckpointSaveResult,
    ModelProbeSummary,
    ProbeCadence,
    ProbeHookPoint,
    ProbeSelector,
    ProbeSelectorMode,
    ProfileSpanSummary,
    ProfileWriterAppendResult,
    ProfileWriterFlushResult,
    ProfileWriterFlushScope,
    ProfileWriterResultStatus,
    ResourceMonitorLifecycleEvent,
    ResourceMonitorLifecycleRecord,
    ResourceMetricKind,
    ResourceSample,
    ResourceSampleStatus,
    ResourceTrace,
    TrainingEvent,
    TrainingEventLog,
    TrainingEventPhase,
    TrainingProfile,
    TrainingProfileRecorder,
    UnavailableProfileProbe,
)


def test_stage15_lifecycle_event_phases_are_observe_only_primitive_evidence() -> None:
    lifecycle_values = (
        "setup",
        "teardown",
        "data_wait",
        "device_transfer",
        "validation",
        "checkpoint",
        "profiling_summary",
        "stage",
    )

    for sequence_id, value in enumerate(lifecycle_values):
        event = TrainingEvent(
            value,
            "train",
            sequence_id=sequence_id,
            timeline_id="timeline-1",
            run_id="run-1",
            metadata={"stage": value},
        )

        assert event.phase is TrainingEventPhase.coerce(value)
        assert event.metadata == {"stage": value}
        for forbidden in (
            "stop",
            "skip_batch",
            "checkpoint",
            "probe",
            "resource_trace",
        ):
            assert not callable(getattr(event, forbidden, None))


def test_stage15_training_profile_records_are_immutable_and_tuple_backed() -> None:
    profile = TrainingProfile(
        event_logs=(
            TrainingEventLog(
                "timeline-1",
                run_id="run-1",
                events=(
                    TrainingEvent(
                        TrainingEventPhase.LOOP_STARTED,
                        "train",
                        sequence_id=0,
                        timeline_id="timeline-1",
                        run_id="run-1",
                    ),
                ),
            ),
        ),
        scalar_spans=(ProfileSpanSummary("forward", status="available"),),
        unavailable_spans=(UnavailableProfileProbe("cuda", reason="missing"),),
        resource_traces=(
            ResourceTrace(
                ResourceMetricKind.CPU_UTILIZATION,
                metric_name="cpu_utilization",
                unit="percent",
                source_probe_id="fake-cpu",
                samples=(
                    ResourceSample(
                        ResourceMetricKind.CPU_UTILIZATION,
                        metric_name="cpu_utilization",
                        unit="percent",
                        value=10.0,
                        status=ResourceSampleStatus.AVAILABLE,
                        timestamp=1.0,
                        sequence_id=0,
                        source_probe_id="fake-cpu",
                    ),
                ),
            ),
        ),
        monitor_lifecycle_records=(
            ResourceMonitorLifecycleRecord(
                ResourceMonitorLifecycleEvent.CONFIGURED,
                0,
                probe_id="fake-cpu",
                timestamp=1.0,
            ),
        ),
        writer_results=(
            ProfileWriterAppendResult(
                ProfileWriterResultStatus.REJECTED,
                sequence_id=0,
                timestamp=0.9,
                queue_depth=1,
                queue_capacity=1,
                accepted_count=1,
                dropped_count=1,
                failure_reason="buffer_full",
            ),
            ProfileWriterFlushResult(
                ProfileWriterFlushScope.MANUAL,
                ProfileWriterResultStatus.COMPLETED,
                sequence_id=1,
                timestamp=1.0,
                requested_count=1,
                written_count=1,
                dropped_count=1,
                remaining_count=0,
            ),
        ),
        probe_results=(
            ModelProbeSummary(
                "model-probe",
                "parameter_norm",
                hook_point=ProbeHookPoint.STEP_COMPLETED,
                selector=ProbeSelector(ProbeSelectorMode.ALL),
                cadence=ProbeCadence(),
                value=1.0,
                run_id="run-1",
                timeline_id="timeline-1",
            ),
        ),
        checkpoint_results=(
            CheckpointSaveResult(
                status=CheckpointResultStatus.COMPLETED,
                ref_id="ckpt-1",
                run_id="run-1",
                timeline_id="timeline-1",
            ),
        ),
        decisions=("decision-a",),
    )

    assert isinstance(profile.event_logs, tuple)
    assert isinstance(profile.scalar_spans, tuple)
    assert isinstance(profile.unavailable_spans, tuple)
    assert isinstance(profile.resource_traces, tuple)
    assert isinstance(profile.monitor_lifecycle_records, tuple)
    assert isinstance(profile.writer_results, tuple)
    assert isinstance(profile.probe_results, tuple)
    assert isinstance(profile.checkpoint_results, tuple)
    assert profile.writer_results[0].dropped_count == 1
    assert profile.writer_results[1].dropped_count == 1
    assert profile.probe_results_for(probe_id="model-probe")[0].name == "parameter_norm"
    assert profile.checkpoint_results[0].ref_id == "ckpt-1"
    assert profile.decisions == ("decision-a",)

    inspected = asdict(profile)
    assert inspected["event_logs"][0]["events"][0]["metadata"] == {}
    assert inspected["scalar_spans"][0]["metadata"] == {}
    assert inspected["unavailable_spans"][0]["metadata"] == {}
    assert inspected["resource_traces"][0]["metric_kind"] == ResourceMetricKind.CPU_UTILIZATION.value
    assert inspected["probe_results"][0]["probe_id"] == "model-probe"
    assert inspected["checkpoint_results"][0]["ref_id"] == "ckpt-1"


def test_stage15_training_profile_recorder_uses_clock_for_deterministic_snapshots() -> None:
    values = [1.0, 2.0, 3.0, 4.0, 5.0]

    def clock() -> float:
        return values.pop(0)

    recorder = TrainingProfileRecorder(clock=clock)
    recorder.record_event(TrainingEvent(TrainingEventPhase.STEP_STARTED, "train", timeline_id="timeline-1"))
    recorder.record_scalar_span(ProfileSpanSummary("forward", duration_seconds=0.25))
    recorder.record_scalar_span(ProfileSpanSummary("backward"))
    recorder.record_unavailable_probe(UnavailableProfileProbe("cuda", reason="disabled"))
    recorder.record_resource_sample(
        ResourceSample(
            ResourceMetricKind.CPU_UTILIZATION,
            metric_name="cpu_utilization",
            unit="percent",
            value=0.1,
            status=ResourceSampleStatus.AVAILABLE,
            timestamp=1.0,
            sequence_id=0,
            source_probe_id="fake-cpu",
        ),
    )
    recorder.record_decision("a")

    first = recorder.snapshot()
    recorder.record_decision("b")
    second = recorder.profile

    assert first.event_logs[0].events[0].timestamp == 1.0
    assert first.event_logs[0].events[0].sequence_id == 0
    assert first.scalar_spans[0].start_timestamp == 2.0
    assert first.scalar_spans[0].end_timestamp == 2.25
    assert first.scalar_spans[1].start_timestamp == 3.0
    assert first.unavailable_spans[0].name == "cuda"
    assert first.resource_traces_for(metric_kind=ResourceMetricKind.CPU_UTILIZATION)[0].samples[0].value == 0.1
    assert first.decisions == ("a",)
    assert second.decisions == ("a", "b")
