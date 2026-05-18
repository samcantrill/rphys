from __future__ import annotations

import pytest

from rphys.errors import RemotePhysTrainingError
from rphys.training import (
    ProfileSpanSummary,
    TrainingEvent,
    TrainingEventLog,
    TrainingProfile,
    TrainingProfileRecorder,
    TrainingProfiler,
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
