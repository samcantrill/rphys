from __future__ import annotations

import pytest

from rphys.errors import RemotePhysTrainingError
from rphys.training import (
    TrainingCallback,
    TrainingEvent,
    TrainingEventLog,
    TrainingEventPhase,
    TrainingEventSink,
    emit_training_event,
)


class RecordingSink:
    def __init__(self) -> None:
        self.events: list[TrainingEvent] = []

    def record(self, event: TrainingEvent) -> None:
        self.events.append(event)


class RecordingCallback:
    def __init__(self) -> None:
        self.events: list[TrainingEvent] = []

    def on_event(self, event: TrainingEvent) -> str:
        self.events.append(event)
        return "ignored"


def test_training_event_phase_coerces_stage12_and_stage15_values() -> None:
    stage12_values = {
        "loop_started": TrainingEventPhase.LOOP_STARTED,
        "step_started": TrainingEventPhase.STEP_STARTED,
        "step_completed": TrainingEventPhase.STEP_COMPLETED,
        "loop_completed": TrainingEventPhase.LOOP_COMPLETED,
        "loop_failed": TrainingEventPhase.LOOP_FAILED,
        "external_summary": TrainingEventPhase.EXTERNAL_SUMMARY,
    }
    stage15_values = {
        "setup": TrainingEventPhase.SETUP,
        "teardown": TrainingEventPhase.TEARDOWN,
        "data_wait": TrainingEventPhase.DATA_WAIT,
        "device_transfer": TrainingEventPhase.DEVICE_TRANSFER,
        "validation": TrainingEventPhase.VALIDATION,
        "checkpoint": TrainingEventPhase.CHECKPOINT,
        "profiling_summary": TrainingEventPhase.PROFILING_SUMMARY,
        "stage": TrainingEventPhase.STAGE,
    }

    for value, expected in stage12_values.items():
        assert TrainingEventPhase.coerce(value) is expected

    for value, expected in stage15_values.items():
        assert TrainingEventPhase.coerce(value) is expected
        assert TrainingEvent(value, "train").phase is expected


def test_training_event_preserves_extended_timeline_and_timestamps() -> None:
    event = TrainingEvent(
        "step_completed",
        "train",
        status="completed",
        epoch_index=1,
        step_index=4,
        batch_index=2,
        split="train",
        run_id="run-1",
        timeline_id="timeline-1",
        sequence_id=2,
        timestamp=12.5,
        clock_name="monotonic",
        process_id=0,
        local_rank=1,
        global_rank=0,
        node_id="node-a",
        device_id="cuda:0",
        metadata={"loss": 0.2},
        provenance={"engine": "native"},
    )

    assert event.phase is TrainingEventPhase.STEP_COMPLETED
    assert event.mode.value == "train"
    assert event.step_index == 4
    assert event.metadata == {"loss": 0.2}
    assert event.provenance == {"engine": "native"}
    assert event.run_id == "run-1"
    assert event.timeline_id == "timeline-1"
    assert event.sequence_id == 2
    assert event.timestamp == 12.5
    assert event.clock_name == "monotonic"
    assert event.process_id == 0
    assert event.local_rank == 1


def test_emit_training_event_is_observe_only_for_sinks_and_callbacks() -> None:
    sink = RecordingSink()
    callback = RecordingCallback()
    event = TrainingEvent(TrainingEventPhase.LOOP_STARTED, "validate")

    emit_training_event(event, sinks=(sink,), callbacks=(callback,))

    assert isinstance(sink, TrainingEventSink)
    assert isinstance(callback, TrainingCallback)
    assert sink.events == [event]
    assert callback.events == [event]


def test_training_event_log_is_append_only_and_validates_sequence_ids() -> None:
    baseline = TrainingEventLog(
        "timeline-1",
        run_id="run-1",
        events=(TrainingEvent("loop_started", "train", sequence_id=0, timeline_id="timeline-1", run_id="run-1"),),
    )
    updated = baseline.append(
        TrainingEvent("step_started", "train", sequence_id=1, timeline_id="timeline-1", run_id="run-1"),
    )

    assert baseline.events[0].sequence_id == 0
    assert updated.events[0].sequence_id == 0
    assert updated.events[1].sequence_id == 1

    with pytest.raises(RemotePhysTrainingError) as duplicate_error:
        updated.append(TrainingEvent("step_completed", "train", sequence_id=1, timeline_id="timeline-1", run_id="run-1"))
    assert duplicate_error.value.context["field"] == "sequence_id"

    with pytest.raises(RemotePhysTrainingError) as out_of_order_error:
        updated.append(TrainingEvent("step_completed", "train", sequence_id=0, timeline_id="timeline-1", run_id="run-1"))
    assert out_of_order_error.value.context["field"] == "sequence_id"

    with pytest.raises(RemotePhysTrainingError) as timeline_error:
        updated.append(
            TrainingEvent("step_completed", "train", sequence_id=2, timeline_id="timeline-2", run_id="run-1"),
        )
    assert timeline_error.value.context["field"] == "event"


def test_training_events_reject_invalid_context_and_observers() -> None:
    with pytest.raises(RemotePhysTrainingError) as phase_error:
        TrainingEvent("done", "train")  # type: ignore[arg-type]
    assert phase_error.value.context["field"] == "phase"
    assert "setup" in phase_error.value.context["expected"]
    assert "loop_started" in phase_error.value.context["expected"]

    with pytest.raises(RemotePhysTrainingError) as metadata_error:
        TrainingEvent("step_started", "train", metadata={"raw": object()})
    assert metadata_error.value.context["field"] == "metadata"

    with pytest.raises(RemotePhysTrainingError) as sink_error:
        emit_training_event(TrainingEvent("step_started", "train"), sinks=(object(),))  # type: ignore[arg-type]
    assert sink_error.value.context["owner"] == "TrainingEventSink"
