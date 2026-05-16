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
