from __future__ import annotations

from rphys.training import (
    ProfileSpanSummary,
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
        decisions=("decision-a",),
    )

    assert isinstance(profile.event_logs, tuple)
    assert isinstance(profile.scalar_spans, tuple)
    assert isinstance(profile.unavailable_spans, tuple)
    assert profile.decisions == ("decision-a",)
    assert not hasattr(TrainingProfile, "resource_traces")


def test_stage15_training_profile_recorder_uses_clock_for_deterministic_snapshots() -> None:
    values = [1.0, 2.0, 3.0, 4.0, 5.0]

    def clock() -> float:
        return values.pop(0)

    recorder = TrainingProfileRecorder(clock=clock)
    recorder.record_event(TrainingEvent(TrainingEventPhase.STEP_STARTED, "train", timeline_id="timeline-1"))
    recorder.record_scalar_span(ProfileSpanSummary("forward", duration_seconds=0.25))
    recorder.record_scalar_span(ProfileSpanSummary("backward"))
    recorder.record_unavailable_probe(UnavailableProfileProbe("cuda", reason="disabled"))
    recorder.record_decision("a")

    first = recorder.snapshot()
    recorder.record_decision("b")
    second = recorder.profile

    assert first.event_logs[0].events[0].timestamp == 1.0
    assert first.scalar_spans[0].start_timestamp == 2.0
    assert first.scalar_spans[0].end_timestamp == 2.25
    assert first.scalar_spans[1].start_timestamp == 3.0
    assert first.unavailable_spans[0].name == "cuda"
    assert first.decisions == ("a",)
    assert second.decisions == ("a", "b")
