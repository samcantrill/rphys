from __future__ import annotations

import pytest

from rphys.errors import RemotePhysTrainingError
from rphys.training import (
    TrainingCallback,
    TrainingEvent,
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


def test_training_event_preserves_primitive_loop_evidence() -> None:
    event = TrainingEvent(
        "step_completed",
        "train",
        status="completed",
        epoch_index=1,
        step_index=4,
        batch_index=2,
        split="train",
        metadata={"loss": 0.2},
        provenance={"engine": "native"},
    )

    assert event.phase is TrainingEventPhase.STEP_COMPLETED
    assert event.mode.value == "train"
    assert event.step_index == 4
    assert event.metadata == {"loss": 0.2}
    assert event.provenance == {"engine": "native"}


def test_emit_training_event_is_observe_only_for_sinks_and_callbacks() -> None:
    sink = RecordingSink()
    callback = RecordingCallback()
    event = TrainingEvent(TrainingEventPhase.LOOP_STARTED, "validate")

    emit_training_event(event, sinks=(sink,), callbacks=(callback,))

    assert isinstance(sink, TrainingEventSink)
    assert isinstance(callback, TrainingCallback)
    assert sink.events == [event]
    assert callback.events == [event]


def test_training_events_reject_invalid_context_and_observers() -> None:
    with pytest.raises(RemotePhysTrainingError) as phase_error:
        TrainingEvent("done", "train")  # type: ignore[arg-type]
    assert phase_error.value.context["field"] == "phase"

    with pytest.raises(RemotePhysTrainingError) as metadata_error:
        TrainingEvent("step_started", "train", metadata={"raw": object()})
    assert metadata_error.value.context["field"] == "metadata"

    with pytest.raises(RemotePhysTrainingError) as sink_error:
        emit_training_event(TrainingEvent("step_started", "train"), sinks=(object(),))  # type: ignore[arg-type]
    assert sink_error.value.context["owner"] == "TrainingEventSink"
