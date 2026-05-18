"""Dependency-light training event records and observer protocols."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, runtime_checkable

from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopMode

from ._validation import (
    PrimitiveMapping,
    coerce_non_negative_int,
    coerce_optional_non_empty_string,
    freeze_primitive_mapping,
)

__all__ = [
    "TrainingCallback",
    "TrainingEvent",
    "TrainingEventPhase",
    "TrainingEventLog",
    "TrainingEventSink",
    "emit_training_event",
]


class TrainingEventPhase(StrEnum):
    """Small observer vocabulary for native and external loop evidence."""

    LOOP_STARTED = "loop_started"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    LOOP_COMPLETED = "loop_completed"
    LOOP_FAILED = "loop_failed"
    EXTERNAL_SUMMARY = "external_summary"
    SETUP = "setup"
    TEARDOWN = "teardown"
    DATA_WAIT = "data_wait"
    DEVICE_TRANSFER = "device_transfer"
    VALIDATION = "validation"
    CHECKPOINT = "checkpoint"
    PROFILING_SUMMARY = "profiling_summary"
    STAGE = "stage"

    @classmethod
    def coerce(cls, value: "TrainingEventPhase | str") -> "TrainingEventPhase":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported training event phase.",
                    owner="TrainingEventPhase",
                    field="phase",
                    expected=tuple(phase.value for phase in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "Training event phase must be a TrainingEventPhase or string.",
            owner="TrainingEventPhase",
            field="phase",
            expected="TrainingEventPhase | str",
            actual=type(value).__name__,
        )


@dataclass(frozen=True, init=False, slots=True)
class TrainingEvent:
    """Primitive event emitted by native or adapter-owned training loops.

    Events are observe-only evidence. Sinks and callbacks may record or mirror
    them, but they do not control learner semantics, choose splits, step
    optimizers, or manage framework callbacks.
    """

    phase: TrainingEventPhase
    mode: LoopMode
    status: str
    epoch_index: int | None
    step_index: int | None
    batch_index: int | None
    split: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping
    run_id: str | None
    timeline_id: str | None
    sequence_id: int | None
    timestamp: float | None
    clock_name: str | None
    clock_origin: str | None
    process_id: int | None
    node_id: str | None
    local_rank: int | None
    global_rank: int | None
    device_id: str | None

    def __init__(
        self,
        phase: TrainingEventPhase | str,
        mode: LoopMode | str,
        *,
        status: str = "observed",
        epoch_index: int | None = None,
        step_index: int | None = None,
        batch_index: int | None = None,
        split: str | None = None,
        run_id: str | None = None,
        timeline_id: str | None = None,
        sequence_id: int | None = None,
        timestamp: float | int | None = None,
        clock_name: str | None = None,
        clock_origin: str | None = None,
        process_id: int | None = None,
        node_id: str | None = None,
        local_rank: int | None = None,
        global_rank: int | None = None,
        device_id: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(self, "phase", TrainingEventPhase.coerce(phase))
        object.__setattr__(self, "mode", LoopMode.coerce(mode))
        object.__setattr__(
            self,
            "status",
            _coerce_status(status),
        )
        object.__setattr__(
            self,
            "epoch_index",
            _coerce_optional_index(epoch_index, field="epoch_index"),
        )
        object.__setattr__(
            self,
            "step_index",
            _coerce_optional_index(step_index, field="step_index"),
        )
        object.__setattr__(
            self,
            "batch_index",
            _coerce_optional_index(batch_index, field="batch_index"),
        )
        object.__setattr__(
            self,
            "split",
            coerce_optional_non_empty_string(
                split,
                owner="TrainingEvent",
                field="split",
            ),
        )
        object.__setattr__(
            self,
            "run_id",
            coerce_optional_non_empty_string(
                run_id,
                owner="TrainingEvent",
                field="run_id",
            ),
        )
        object.__setattr__(
            self,
            "timeline_id",
            coerce_optional_non_empty_string(
                timeline_id,
                owner="TrainingEvent",
                field="timeline_id",
            ),
        )
        object.__setattr__(
            self,
            "sequence_id",
            _coerce_optional_non_negative_int(
                sequence_id,
                owner="TrainingEvent",
                field="sequence_id",
            ),
        )
        object.__setattr__(
            self,
            "timestamp",
            _coerce_optional_timestamp(
                timestamp,
                owner="TrainingEvent",
                field="timestamp",
            ),
        )
        object.__setattr__(
            self,
            "clock_name",
            coerce_optional_non_empty_string(
                clock_name,
                owner="TrainingEvent",
                field="clock_name",
            ),
        )
        object.__setattr__(
            self,
            "clock_origin",
            coerce_optional_non_empty_string(
                clock_origin,
                owner="TrainingEvent",
                field="clock_origin",
            ),
        )
        object.__setattr__(
            self,
            "process_id",
            _coerce_optional_non_negative_int(
                process_id,
                owner="TrainingEvent",
                field="process_id",
            ),
        )
        object.__setattr__(
            self,
            "node_id",
            coerce_optional_non_empty_string(
                node_id,
                owner="TrainingEvent",
                field="node_id",
            ),
        )
        object.__setattr__(
            self,
            "local_rank",
            _coerce_optional_non_negative_int(
                local_rank,
                owner="TrainingEvent",
                field="local_rank",
            ),
        )
        object.__setattr__(
            self,
            "global_rank",
            _coerce_optional_non_negative_int(
                global_rank,
                owner="TrainingEvent",
                field="global_rank",
            ),
        )
        object.__setattr__(
            self,
            "device_id",
            coerce_optional_non_empty_string(
                device_id,
                owner="TrainingEvent",
                field="device_id",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(
                metadata,
                owner="TrainingEvent",
                field="metadata",
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(
                provenance,
                owner="TrainingEvent",
                field="provenance",
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class TrainingEventLog:
    """Append-only collection of timeline-scoped primitive events."""

    timeline_id: str
    run_id: str | None
    events: tuple[TrainingEvent, ...]

    def __init__(
        self,
        timeline_id: str,
        *,
        run_id: str | None = None,
        events: Iterable[TrainingEvent] = (),
    ) -> None:
        object.__setattr__(
            self,
            "timeline_id",
            _coerce_name(
                timeline_id,
                owner="TrainingEventLog",
                field="timeline_id",
            ),
        )
        object.__setattr__(self, "run_id", coerce_optional_non_empty_string(run_id, owner="TrainingEventLog", field="run_id"))
        event_list = _coerce_event_records(
            events,
            timeline_id=self.timeline_id,
            run_id=self.run_id,
            owner="TrainingEventLog",
            field="events",
        )
        object.__setattr__(self, "events", event_list)
        if self.run_id is None:
            run_ids = {event.run_id for event in event_list if event.run_id is not None}
            if len(run_ids) > 1:
                raise RemotePhysTrainingError(
                    "TrainingEventLog run ids must be consistent.",
                    owner="TrainingEventLog",
                    field="events",
                )
            object.__setattr__(self, "run_id", next(iter(run_ids), None))

    def append(self, event: TrainingEvent) -> "TrainingEventLog":
        if not isinstance(event, TrainingEvent):
            raise RemotePhysTrainingError(
                "TrainingEventLog.append expects a TrainingEvent.",
                owner="TrainingEventLog",
                field="event",
                expected="TrainingEvent",
                actual=type(event).__name__,
            )
        if event.timeline_id is not None and event.timeline_id != self.timeline_id:
            raise RemotePhysTrainingError(
                "TrainingEventLog timeline_id must match appended event timeline_id when provided.",
                owner="TrainingEventLog",
                field="event",
                timeline_id=self.timeline_id,
                event_timeline_id=event.timeline_id,
            )
        if self.run_id is None:
            run_id = event.run_id
        else:
            if event.run_id is not None and event.run_id != self.run_id:
                raise RemotePhysTrainingError(
                    "TrainingEventLog run_id does not match appended event run_id.",
                    owner="TrainingEventLog",
                    field="event",
                    run_id=self.run_id,
                    event_run_id=event.run_id,
                )
            run_id = self.run_id
        return TrainingEventLog(
            self.timeline_id,
            run_id=run_id,
            events=self.events + (event,),
        )

    def events_for_timeline(self) -> tuple[TrainingEvent, ...]:
        return self.events


@runtime_checkable
class TrainingEventSink(Protocol):
    """Observe-only event sink."""

    def record(self, event: TrainingEvent) -> None:
        ...


@runtime_checkable
class TrainingCallback(Protocol):
    """Observe-only callback over training events."""

    def on_event(self, event: TrainingEvent) -> None:
        ...


def emit_training_event(
    event: TrainingEvent,
    *,
    sinks: Iterable[TrainingEventSink] = (),
    callbacks: Iterable[TrainingCallback] = (),
) -> None:
    """Send an event to observer sinks/callbacks without accepting control values."""

    for sink in sinks:
        _require_sink(sink).record(event)
    for callback in callbacks:
        _require_callback(callback).on_event(event)


def _coerce_name(value: object, *, owner: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a non-empty string.",
            owner=owner,
            field=field,
            expected="non-empty string",
            actual=type(value).__name__,
        )
    return value


def _coerce_status(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise RemotePhysTrainingError(
            "TrainingEvent status must be a non-empty string.",
            owner="TrainingEvent",
            field="status",
            expected="non-empty string",
            actual=type(value).__name__,
        )
    return value


def _coerce_optional_index(value: int | None, *, field: str) -> int | None:
    if value is None:
        return None
    return coerce_non_negative_int(value, owner="TrainingEvent", field=field)


def _coerce_optional_non_negative_int(
    value: int | None,
    *,
    owner: str,
    field: str,
) -> int | None:
    if value is None:
        return None
    return coerce_non_negative_int(value, owner=owner, field=field)


def _coerce_optional_timestamp(
    value: float | int | None,
    *,
    owner: str,
    field: str,
) -> float | None:
    if value is None:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or value < 0
    ):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a non-negative number when provided.",
            owner=owner,
            field=field,
            expected="non-negative number | None",
            actual=type(value).__name__,
        )
    return float(value)


def _coerce_event_records(
    values: Iterable[TrainingEvent],
    *,
    timeline_id: str,
    run_id: str | None,
    owner: str,
    field: str,
) -> tuple[TrainingEvent, ...]:
    try:
        events = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be iterable.",
            owner=owner,
            field=field,
            expected="iterable of TrainingEvent",
            actual=type(values).__name__,
        ) from exc

    last_sequence: int | None = None
    for index, event in enumerate(events):
        if not isinstance(event, TrainingEvent):
            raise RemotePhysTrainingError(
                f"{owner} {field} must contain TrainingEvent records.",
                owner=owner,
                field=field,
                expected="TrainingEvent",
                index=index,
                actual=type(event).__name__,
            )
        if event.timeline_id is not None and event.timeline_id != timeline_id:
            raise RemotePhysTrainingError(
                f"{owner} {field} contains mismatched timeline evidence.",
                owner=owner,
                field=field,
                timeline_id=timeline_id,
                event_timeline_id=event.timeline_id,
                index=index,
            )
        if run_id is not None and event.run_id is not None and event.run_id != run_id:
            raise RemotePhysTrainingError(
                f"{owner} {field} contains mismatched run_id.",
                owner=owner,
                field=field,
                run_id=run_id,
                event_run_id=event.run_id,
                index=index,
            )
        if event.sequence_id is not None:
            if last_sequence is not None and event.sequence_id <= last_sequence:
                raise RemotePhysTrainingError(
                    f"{owner} {field} sequence ids must be strictly increasing.",
                    owner=owner,
                    field="sequence_id",
                    expected="strictly increasing non-negative integer",
                    index=index,
                    sequence_id=event.sequence_id,
                    previous_sequence_id=last_sequence,
                )
            last_sequence = event.sequence_id

    return events


def _require_sink(sink: object) -> TrainingEventSink:
    record = getattr(sink, "record", None)
    if not callable(record):
        raise RemotePhysTrainingError(
            "TrainingEventSink entries must expose record(event).",
            owner="TrainingEventSink",
            field="sink",
            expected="record(event)",
            actual=type(sink).__name__,
        )
    return sink


def _require_callback(callback: object) -> TrainingCallback:
    on_event = getattr(callback, "on_event", None)
    if not callable(on_event):
        raise RemotePhysTrainingError(
            "TrainingCallback entries must expose on_event(event).",
            owner="TrainingCallback",
            field="callback",
            expected="on_event(event)",
            actual=type(callback).__name__,
        )
    return callback


TrainingEvent.__hash__ = None  # type: ignore[assignment]
TrainingEventLog.__hash__ = None  # type: ignore[assignment]
