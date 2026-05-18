from __future__ import annotations

from dataclasses import asdict

import pytest

from rphys.errors import RemotePhysTrainingError
from rphys.training import (
    ProfileSpanSummary,
    ProfileWriterFlushResult,
    ProfileWriterFlushScope,
    ProfileWriterResultStatus,
    ResourceBufferOverflowPolicy,
    ResourceMetricKind,
    ResourceMetricUnit,
    ResourceMonitor,
    ResourceMonitorExecutionMode,
    ResourceMonitorLifecycleEvent,
    ResourceMonitorLifecycleRecord,
    ResourceSample,
    ResourceSampleBuffer,
    ResourceSampleStatus,
    ResourceTrace,
    FakeCPUResourceProbe,
    FakeUnavailableResourceProbe,
    TrainingEvent,
    TrainingEventLog,
    TrainingProfile,
    TrainingProfileRecorder,
    TrainingProfiler,
    InMemoryProfileWriterBackend,
    AsyncTrainingProfileWriter,
    UnavailableProfileProbe,
)


class FakeProfiler:
    def span(self, name: str, **kwargs: object) -> ProfileSpanSummary:
        return ProfileSpanSummary(name, **kwargs)


def test_profile_span_summary_records_timing_stage_and_timeline_metadata() -> None:
    span = ProfileSpanSummary(
        "forward",
        mode="train",
        stage_name="step",
        duration_seconds=0.01,
        start_timestamp=100.0,
        end_timestamp=100.1,
        synchronization="sync_barrier",
        run_id="run-1",
        timeline_id="timeline-1",
        process_id=1,
        local_rank=0,
        global_rank=0,
        device_id="cuda:0",
        overhead_seconds=0.001,
        metadata={"clock": "cpu"},
    )

    assert span.name == "forward"
    assert span.mode is not None
    assert span.mode.value == "train"
    assert span.stage_name == "step"
    assert span.start_timestamp == 100.0
    assert span.end_timestamp == 100.1
    assert span.synchronization == "sync_barrier"
    assert span.run_id == "run-1"
    assert span.duration_seconds == 0.01
    assert span.overhead_seconds == 0.001
    assert span.metadata == {"clock": "cpu"}
    assert asdict(span)["metadata"] == {"clock": "cpu"}


def test_unavailable_probe_converts_to_unavailable_span() -> None:
    probe = UnavailableProfileProbe(
        "cuda-sync",
        reason="cuda unavailable",
        stage_name="profiling",
        run_id="run-1",
        timeline_id="timeline-1",
        overhead_seconds=0.0,
    )
    span = probe.as_span()

    assert span.name == "cuda-sync"
    assert span.stage_name == "profiling"
    assert span.status == "unavailable"
    assert span.metadata["reason"] == "cuda unavailable"
    assert span.run_id == "run-1"
    assert span.timeline_id == "timeline-1"


def test_training_profile_collects_logs_spans_unavailable_and_decisions() -> None:
    log = TrainingEventLog(
        "timeline-1",
        run_id="run-1",
        events=(TrainingEvent("loop_started", "train", sequence_id=0, timeline_id="timeline-1", run_id="run-1"),),
    )
    span = ProfileSpanSummary("forward", mode="train")
    probe = UnavailableProfileProbe("cuda-sync", reason="disabled")
    profile = TrainingProfile(event_logs=(log,), scalar_spans=(span,), unavailable_spans=(probe,), decisions=("decision-a",))

    assert profile.event_logs[0].events[0].phase.value == "loop_started"
    assert profile.spans()[0] is span
    assert profile.unavailable_probes()[0].name == "cuda-sync"
    assert profile.decisions == ("decision-a",)
    summaries = profile.as_profile_summaries()
    assert summaries[0].status == "available"
    assert summaries[1].status == "unavailable"


def test_training_profiler_protocol_and_validation() -> None:
    profiler = FakeProfiler()

    assert isinstance(profiler, TrainingProfiler)
    assert profiler.span("forward", mode="test").mode.value == "test"

    with pytest.raises(RemotePhysTrainingError) as duration_error:
        ProfileSpanSummary("bad", duration_seconds=-1.0)
    assert duration_error.value.context["field"] == "duration_seconds"

    for value in (float("nan"), float("inf")):
        with pytest.raises(RemotePhysTrainingError) as finite_error:
            ProfileSpanSummary("bad", duration_seconds=value)
        assert finite_error.value.context["field"] == "duration_seconds"

        with pytest.raises(RemotePhysTrainingError) as timestamp_error:
            ProfileSpanSummary("bad", start_timestamp=value)
        assert timestamp_error.value.context["field"] == "start_timestamp"

    with pytest.raises(RemotePhysTrainingError) as reason_error:
        UnavailableProfileProbe("bad", reason="")
    assert reason_error.value.context["field"] == "reason"


def test_training_profile_recorder_snapshots_immutable_state_and_injects_clock() -> None:
    values = [1.0, 2.0, 3.0, 4.0]

    def clock() -> float:
        return values.pop(0)

    recorder = TrainingProfileRecorder(clock=clock)
    recorder.record_event(TrainingEvent("loop_started", "train", timeline_id="timeline-1", run_id="run-1"))
    recorder.record_scalar_span(ProfileSpanSummary("forward", duration_seconds=0.25))
    recorder.record_scalar_span(ProfileSpanSummary("backward"))
    recorder.record_unavailable_probe(UnavailableProfileProbe("cuda-sync", reason="disabled"))
    recorder.record_decision("decision-a")

    first = recorder.snapshot()
    recorder.record_decision("decision-b")
    second = recorder.snapshot()

    assert first is not second
    assert first.event_logs[0].timeline_id == "timeline-1"
    assert first.event_logs[0].events[0].timestamp == 1.0
    assert first.event_logs[0].events[0].sequence_id == 0
    assert first.scalar_spans[0].start_timestamp == 2.0
    assert first.scalar_spans[0].end_timestamp == 2.25
    assert first.scalar_spans[1].start_timestamp == 3.0
    assert first.scalar_spans[1].end_timestamp == 3.0
    assert first.unavailable_spans[0].name == "cuda-sync"
    assert first.decisions == ("decision-a",)
    assert second.decisions == ("decision-a", "decision-b")
    unavailable_summaries = [
        summary for summary in first.as_profile_summaries() if summary.status == "unavailable"
    ]
    assert unavailable_summaries[0].metadata["reason"] == "disabled"


def test_training_profile_recorder_assigns_monotonic_event_sequence_ids() -> None:
    recorder = TrainingProfileRecorder(clock=lambda: 1.0)

    recorder.record_event(TrainingEvent("loop_started", "train", timeline_id="timeline-1"))
    recorder.record_event(TrainingEvent("step_started", "train", timeline_id="timeline-1"))
    recorder.record_event(TrainingEvent("loop_started", "validate", timeline_id="timeline-2", sequence_id=5))

    first_log, second_log = recorder.snapshot().event_logs

    assert [event.sequence_id for event in first_log.events] == [0, 1]
    assert [event.sequence_id for event in second_log.events] == [5]


def test_training_profile_recorder_preserves_duration_with_partial_timestamps() -> None:
    recorder = TrainingProfileRecorder(clock=lambda: 10.0)

    recorder.record_scalar_span(
        ProfileSpanSummary("start-only", start_timestamp=2.0, duration_seconds=0.5),
    )
    recorder.record_scalar_span(
        ProfileSpanSummary("end-only", end_timestamp=5.0, duration_seconds=0.25),
    )

    first, second = recorder.snapshot().scalar_spans

    assert first.start_timestamp == 2.0
    assert first.end_timestamp == 2.5
    assert second.start_timestamp == 4.75
    assert second.end_timestamp == 5.0


def test_resource_sample_and_trace_enforce_contract_and_ordering() -> None:
    first = ResourceSample(
        ResourceMetricKind.CPU_UTILIZATION,
        metric_name="cpu_utilization",
        unit=ResourceMetricUnit.PERCENT,
        value=12.5,
        status=ResourceSampleStatus.AVAILABLE,
        timestamp=1.0,
        sequence_id=0,
        source_probe_id="fake-cpu",
    )
    second = ResourceSample(
        ResourceMetricKind.CPU_UTILIZATION,
        metric_name="cpu_utilization",
        unit=ResourceMetricUnit.PERCENT,
        value=13.1,
        status=ResourceSampleStatus.AVAILABLE,
        timestamp=1.1,
        sequence_id=1,
        source_probe_id="fake-cpu",
    )
    trace = ResourceTrace(
        ResourceMetricKind.CPU_UTILIZATION,
        metric_name="cpu_utilization",
        unit=ResourceMetricUnit.PERCENT,
        source_probe_id="fake-cpu",
        samples=(first, second),
        series_key="cpu",
    )

    assert trace.metric_kind is ResourceMetricKind.CPU_UTILIZATION
    assert trace.samples[0].value == 12.5
    assert trace.append(second).samples == (first, second, second)

    with pytest.raises(RemotePhysTrainingError):
        ResourceSample(
            ResourceMetricKind.CPU_UTILIZATION,
            metric_name="cpu_utilization",
            unit=ResourceMetricUnit.PERCENT,
            value=None,
            status=ResourceSampleStatus.AVAILABLE,
            timestamp=1.0,
            sequence_id=0,
            source_probe_id="fake-cpu",
        )

    with pytest.raises(RemotePhysTrainingError):
        ResourceTrace(
            ResourceMetricKind.GPU_UTILIZATION,
            metric_name="gpu_utilization",
            unit=ResourceMetricUnit.PERCENT,
            source_probe_id="fake-gpu",
            samples=(
                ResourceSample(
                    ResourceMetricKind.CPU_UTILIZATION,
                    metric_name="cpu_utilization",
                    unit=ResourceMetricUnit.PERCENT,
                    value=1.0,
                    timestamp=1.0,
                    sequence_id=0,
                    source_probe_id="fake-cpu",
                ),
            ),
        )


def test_fake_resource_probes_advance_deterministically() -> None:
    probe = FakeCPUResourceProbe(values=(0.5, 0.6), probe_id="fake-cpu", series_key="cpu")
    unavailable = FakeUnavailableResourceProbe(
        probe_id="fake-offline",
        metric_kind=ResourceMetricKind.GPU_UTILIZATION,
        metric_name="gpu_utilization",
        reason="missing_dependency",
    )

    for index, expected in enumerate((0.5, 0.6, 0.5, 0.6)):
        sample = probe.sample(
            timestamp=1.0 + index,
            sequence_id=index,
            run_id="run-1",
            timeline_id="timeline-1",
            source_probe_id="fake-cpu",
        )
        assert sample.value == expected
        assert sample.status is ResourceSampleStatus.AVAILABLE

    sample = unavailable.sample(
        timestamp=4.0,
        sequence_id=0,
        run_id="run-1",
        timeline_id="timeline-1",
        source_probe_id="fake-offline",
    )

    assert sample.status is ResourceSampleStatus.UNAVAILABLE
    assert sample.reason == "missing_dependency"


def test_resource_sample_buffer_records_drop_policy_behavior() -> None:
    drop_oldest = ResourceSampleBuffer(
        capacity=2,
        overflow_policy=ResourceBufferOverflowPolicy.DROP_OLDEST,
    )
    for sample in ("a", "b", "c"):
        state = drop_oldest.push(sample)
    assert drop_oldest.items() == ("b", "c")
    assert state.queue_depth == 2
    assert state.dropped_count == 1
    assert state.overflow_policy is ResourceBufferOverflowPolicy.DROP_OLDEST

    reject_new = ResourceSampleBuffer(
        capacity=2,
        overflow_policy=ResourceBufferOverflowPolicy.REJECT_NEW,
    )
    reject_new.push("a")
    reject_new.push("b")
    state = reject_new.push("c")
    assert reject_new.items() == ("a", "b")
    assert state.queue_depth == 2
    assert state.dropped_count == 1


def test_resource_monitor_records_lifecycle_and_rejected_sample_backpressure() -> None:
    clock_values = [1.0, 1.1, 1.2, 1.3, 1.4]

    def clock() -> float:
        return clock_values.pop(0)

    monitor = ResourceMonitor(
        FakeCPUResourceProbe(values=(10.0, 20.0), probe_id="fake-cpu"),
        execution_mode=ResourceMonitorExecutionMode.INLINE,
        buffer_capacity=2,
        buffer_overflow_policy=ResourceBufferOverflowPolicy.REJECT_NEW,
        clock=clock,
    )

    monitor.start()
    monitor.collect_sample()
    monitor.collect_sample()
    monitor.collect_sample()

    assert monitor.execution_mode is ResourceMonitorExecutionMode.INLINE
    lifecycle_events = monitor.lifecycle_events
    assert lifecycle_events[0].event is ResourceMonitorLifecycleEvent.CONFIGURED
    assert lifecycle_events[1].event is ResourceMonitorLifecycleEvent.STARTED
    assert lifecycle_events[2].event is ResourceMonitorLifecycleEvent.SAMPLE_EMITTED
    assert monitor.buffer.snapshot().dropped_count == 1

    state = monitor.request_flush()
    assert state.queue_depth == 2
    assert ResourceMonitorLifecycleEvent.FLUSH_COMPLETED in {
        event.event for event in monitor.lifecycle_events
    }
    monitor.stop()
    monitor.cleanup_orphan()
    assert ResourceMonitorLifecycleEvent.STOPPED in {event.event for event in monitor.lifecycle_events}


def test_async_training_profile_writer_tracks_append_and_flush_contract() -> None:
    backend = InMemoryProfileWriterBackend()
    writer = AsyncTrainingProfileWriter(
        backend=backend,
        queue_capacity=2,
        overflow_policy=ResourceBufferOverflowPolicy.DROP_OLDEST,
        flush_cadence_seconds=None,
    )

    first = writer.append("a")
    second = writer.append("b")
    third = writer.append("c")

    assert first.status is ProfileWriterResultStatus.ENQUEUED
    assert second.status is ProfileWriterResultStatus.ENQUEUED
    assert third.status is ProfileWriterResultStatus.ENQUEUED
    assert writer.queue_state.queue_depth == 2
    assert writer.queue_state.dropped_count == 1

    flush = writer.flush(ProfileWriterFlushScope.STEP)
    assert flush.status is ProfileWriterResultStatus.COMPLETED
    assert flush.requested_count == 2
    assert flush.written_count == 2
    assert backend.written_records == ("b", "c")
    assert writer.queue_state.queue_depth == 0

    reject = AsyncTrainingProfileWriter(
        backend=backend,
        queue_capacity=1,
        overflow_policy=ResourceBufferOverflowPolicy.REJECT_NEW,
    )
    one = reject.append("a")
    two = reject.append("b")
    assert one.status is ProfileWriterResultStatus.ENQUEUED
    assert two.status is ProfileWriterResultStatus.REJECTED
    assert two.failure_reason == "buffer_full"


def test_async_training_profile_writer_failure_records_retry_intent() -> None:
    backend = InMemoryProfileWriterBackend(fail_on_calls=(1,))
    writer = AsyncTrainingProfileWriter(backend=backend, enable_retry=True)

    writer.append("a")
    first = writer.flush()
    assert first.status is ProfileWriterResultStatus.FAILED
    assert first.retry_requested is True
    assert first.failure_reason is not None
    assert writer.queue_state.queue_depth == 1

    second = writer.flush()
    assert second.status is ProfileWriterResultStatus.COMPLETED
    assert writer.queue_state.queue_depth == 0


def test_profile_recorder_collects_resource_traces_and_writer_lifecycle_records() -> None:
    cpu_sample = ResourceSample(
        metric_kind=ResourceMetricKind.CPU_UTILIZATION,
        metric_name="cpu_utilization",
        unit=ResourceMetricUnit.PERCENT,
        value=15.0,
        status=ResourceSampleStatus.AVAILABLE,
        timestamp=1.0,
        sequence_id=0,
        source_probe_id="fake-cpu",
    )
    cpu_sample_2 = ResourceSample(
        metric_kind=ResourceMetricKind.CPU_UTILIZATION,
        metric_name="cpu_utilization",
        unit=ResourceMetricUnit.PERCENT,
        value=16.0,
        status=ResourceSampleStatus.AVAILABLE,
        timestamp=1.1,
        sequence_id=1,
        source_probe_id="fake-cpu",
    )
    mem_sample = ResourceSample(
        metric_kind=ResourceMetricKind.HOST_MEMORY_BYTES,
        metric_name="host_memory_bytes",
        unit=ResourceMetricUnit.BYTES,
        value=128_000_000.0,
        status=ResourceSampleStatus.AVAILABLE,
        timestamp=1.0,
        sequence_id=0,
        source_probe_id="fake-memory",
    )

    writer_result = ProfileWriterFlushResult(
        ProfileWriterFlushScope.MANUAL,
        ProfileWriterResultStatus.SKIPPED,
        sequence_id=0,
        timestamp=1.0,
        requested_count=0,
        written_count=0,
        dropped_count=0,
        remaining_count=0,
    )
    monitor_record = ResourceMonitorLifecycleRecord(
        ResourceMonitorLifecycleEvent.CONFIGURED,
        sequence_id=0,
        probe_id="fake-cpu",
        timestamp=0.0,
    )

    recorder = TrainingProfileRecorder()
    recorder.record_resource_sample(cpu_sample)
    recorder.record_resource_sample(cpu_sample_2)
    recorder.record_resource_sample(mem_sample)
    recorder.record_writer_result(writer_result)
    recorder.record_monitor_lifecycle_record(monitor_record)

    snapshot = recorder.snapshot()
    cpu_traces = snapshot.resource_traces_for(metric_kind=ResourceMetricKind.CPU_UTILIZATION)

    assert len(snapshot.resource_traces) == 2
    assert len(cpu_traces) == 1
    assert len(cpu_traces[0].samples) == 2
    assert snapshot.monitor_lifecycle_records[0] is monitor_record
    assert snapshot.writer_results[0] is writer_result
