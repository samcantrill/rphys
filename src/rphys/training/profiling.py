"""Dependency-light training profile records."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from time import monotonic
from typing import Protocol, runtime_checkable

from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopMode

from ._validation import (
    PrimitiveMapping,
    coerce_non_negative_int,
    coerce_optional_non_empty_string,
    freeze_primitive_mapping,
)
from .events import TrainingEvent, TrainingEventLog

__all__ = [
    "ProfileSpanSummary",
    "TrainingProfile",
    "TrainingProfileRecorder",
    "TrainingProfiler",
    "UnavailableProfileProbe",
]


@dataclass(frozen=True, init=False, slots=True)
class ProfileSpanSummary:
    """Primitive span summary with explicit timing availability."""

    name: str
    mode: LoopMode | None
    status: str
    stage_name: str | None
    duration_seconds: float | None
    start_timestamp: float | None
    end_timestamp: float | None
    overhead_seconds: float | None
    synchronization: str | None
    run_id: str | None
    timeline_id: str | None
    clock_name: str | None
    clock_origin: str | None
    process_id: int | None
    node_id: str | None
    local_rank: int | None
    global_rank: int | None
    device_id: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        name: str,
        *,
        mode: LoopMode | str | None = None,
        status: str = "available",
        stage_name: str | None = None,
        duration_seconds: float | None = None,
        start_timestamp: float | int | None = None,
        end_timestamp: float | int | None = None,
        overhead_seconds: float | None = None,
        synchronization: str | None = None,
        run_id: str | None = None,
        timeline_id: str | None = None,
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
        object.__setattr__(self, "name", _coerce_name(name, owner="ProfileSpanSummary", field="name"))
        object.__setattr__(self, "mode", None if mode is None else LoopMode.coerce(mode))
        object.__setattr__(self, "status", _coerce_name(status, owner="ProfileSpanSummary", field="status"))
        object.__setattr__(
            self,
            "stage_name",
            coerce_optional_non_empty_string(
                stage_name,
                owner="ProfileSpanSummary",
                field="stage_name",
            ),
        )
        object.__setattr__(
            self,
            "duration_seconds",
            _coerce_optional_duration(
                duration_seconds,
                owner="ProfileSpanSummary",
                field="duration_seconds",
            ),
        )
        object.__setattr__(
            self,
            "start_timestamp",
            _coerce_optional_timestamp(
                start_timestamp,
                owner="ProfileSpanSummary",
                field="start_timestamp",
            ),
        )
        object.__setattr__(
            self,
            "end_timestamp",
            _coerce_optional_timestamp(
                end_timestamp,
                owner="ProfileSpanSummary",
                field="end_timestamp",
            ),
        )
        if (
            start_timestamp is not None
            and end_timestamp is not None
            and float(end_timestamp) < float(start_timestamp)
        ):
            raise RemotePhysTrainingError(
                "ProfileSpanSummary end_timestamp must be >= start_timestamp.",
                owner="ProfileSpanSummary",
                field="end_timestamp",
                expected="non-decreasing timestamp range",
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
            )
        object.__setattr__(
            self,
            "overhead_seconds",
            _coerce_optional_duration(
                overhead_seconds,
                owner="ProfileSpanSummary",
                field="overhead_seconds",
            ),
        )
        object.__setattr__(
            self,
            "synchronization",
            coerce_optional_non_empty_string(
                synchronization,
                owner="ProfileSpanSummary",
                field="synchronization",
            ),
        )
        object.__setattr__(
            self,
            "run_id",
            coerce_optional_non_empty_string(
                run_id,
                owner="ProfileSpanSummary",
                field="run_id",
            ),
        )
        object.__setattr__(
            self,
            "timeline_id",
            coerce_optional_non_empty_string(
                timeline_id,
                owner="ProfileSpanSummary",
                field="timeline_id",
            ),
        )
        object.__setattr__(
            self,
            "clock_name",
            coerce_optional_non_empty_string(
                clock_name,
                owner="ProfileSpanSummary",
                field="clock_name",
            ),
        )
        object.__setattr__(
            self,
            "clock_origin",
            coerce_optional_non_empty_string(
                clock_origin,
                owner="ProfileSpanSummary",
                field="clock_origin",
            ),
        )
        object.__setattr__(
            self,
            "process_id",
            _coerce_optional_non_negative_int(
                process_id,
                owner="ProfileSpanSummary",
                field="process_id",
            ),
        )
        object.__setattr__(
            self,
            "node_id",
            coerce_optional_non_empty_string(
                node_id,
                owner="ProfileSpanSummary",
                field="node_id",
            ),
        )
        object.__setattr__(
            self,
            "local_rank",
            _coerce_optional_non_negative_int(
                local_rank,
                owner="ProfileSpanSummary",
                field="local_rank",
            ),
        )
        object.__setattr__(
            self,
            "global_rank",
            _coerce_optional_non_negative_int(
                global_rank,
                owner="ProfileSpanSummary",
                field="global_rank",
            ),
        )
        object.__setattr__(
            self,
            "device_id",
            coerce_optional_non_empty_string(
                device_id,
                owner="ProfileSpanSummary",
                field="device_id",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(
                metadata,
                owner="ProfileSpanSummary",
                field="metadata",
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(
                provenance,
                owner="ProfileSpanSummary",
                field="provenance",
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class UnavailableProfileProbe:
    """Record that a profiler probe was intentionally unavailable."""

    name: str
    reason: str
    stage_name: str | None
    duration_seconds: float | None
    start_timestamp: float | None
    end_timestamp: float | None
    overhead_seconds: float | None
    synchronization: str | None
    run_id: str | None
    timeline_id: str | None
    clock_name: str | None
    clock_origin: str | None
    process_id: int | None
    node_id: str | None
    local_rank: int | None
    global_rank: int | None
    device_id: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        name: str,
        *,
        reason: str,
        stage_name: str | None = None,
        duration_seconds: float | None = None,
        start_timestamp: float | int | None = None,
        end_timestamp: float | int | None = None,
        overhead_seconds: float | None = None,
        synchronization: str | None = None,
        run_id: str | None = None,
        timeline_id: str | None = None,
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
        object.__setattr__(self, "name", _coerce_name(name, owner="UnavailableProfileProbe", field="name"))
        object.__setattr__(self, "reason", _coerce_name(reason, owner="UnavailableProfileProbe", field="reason"))
        object.__setattr__(
            self,
            "stage_name",
            coerce_optional_non_empty_string(
                stage_name,
                owner="UnavailableProfileProbe",
                field="stage_name",
            ),
        )
        object.__setattr__(
            self,
            "duration_seconds",
            _coerce_optional_duration(
                duration_seconds,
                owner="UnavailableProfileProbe",
                field="duration_seconds",
            ),
        )
        object.__setattr__(
            self,
            "start_timestamp",
            _coerce_optional_timestamp(
                start_timestamp,
                owner="UnavailableProfileProbe",
                field="start_timestamp",
            ),
        )
        object.__setattr__(
            self,
            "end_timestamp",
            _coerce_optional_timestamp(
                end_timestamp,
                owner="UnavailableProfileProbe",
                field="end_timestamp",
            ),
        )
        if (
            start_timestamp is not None
            and end_timestamp is not None
            and float(end_timestamp) < float(start_timestamp)
        ):
            raise RemotePhysTrainingError(
                "UnavailableProfileProbe end_timestamp must be >= start_timestamp.",
                owner="UnavailableProfileProbe",
                field="end_timestamp",
                expected="non-decreasing timestamp range",
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
            )
        object.__setattr__(
            self,
            "overhead_seconds",
            _coerce_optional_duration(
                overhead_seconds,
                owner="UnavailableProfileProbe",
                field="overhead_seconds",
            ),
        )
        object.__setattr__(
            self,
            "synchronization",
            coerce_optional_non_empty_string(
                synchronization,
                owner="UnavailableProfileProbe",
                field="synchronization",
            ),
        )
        object.__setattr__(
            self,
            "run_id",
            coerce_optional_non_empty_string(
                run_id,
                owner="UnavailableProfileProbe",
                field="run_id",
            ),
        )
        object.__setattr__(
            self,
            "timeline_id",
            coerce_optional_non_empty_string(
                timeline_id,
                owner="UnavailableProfileProbe",
                field="timeline_id",
            ),
        )
        object.__setattr__(
            self,
            "clock_name",
            coerce_optional_non_empty_string(
                clock_name,
                owner="UnavailableProfileProbe",
                field="clock_name",
            ),
        )
        object.__setattr__(
            self,
            "clock_origin",
            coerce_optional_non_empty_string(
                clock_origin,
                owner="UnavailableProfileProbe",
                field="clock_origin",
            ),
        )
        object.__setattr__(
            self,
            "process_id",
            _coerce_optional_non_negative_int(
                process_id,
                owner="UnavailableProfileProbe",
                field="process_id",
            ),
        )
        object.__setattr__(
            self,
            "node_id",
            coerce_optional_non_empty_string(
                node_id,
                owner="UnavailableProfileProbe",
                field="node_id",
            ),
        )
        object.__setattr__(
            self,
            "local_rank",
            _coerce_optional_non_negative_int(
                local_rank,
                owner="UnavailableProfileProbe",
                field="local_rank",
            ),
        )
        object.__setattr__(
            self,
            "global_rank",
            _coerce_optional_non_negative_int(
                global_rank,
                owner="UnavailableProfileProbe",
                field="global_rank",
            ),
        )
        object.__setattr__(
            self,
            "device_id",
            coerce_optional_non_empty_string(
                device_id,
                owner="UnavailableProfileProbe",
                field="device_id",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(
                metadata,
                owner="UnavailableProfileProbe",
                field="metadata",
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(
                provenance,
                owner="UnavailableProfileProbe",
                field="provenance",
            ),
        )

    def as_span(self) -> ProfileSpanSummary:
        """Return an unavailable span summary for result normalization."""

        return ProfileSpanSummary(
            self.name,
            stage_name=self.stage_name,
            status="unavailable",
            duration_seconds=self.duration_seconds,
            start_timestamp=self.start_timestamp,
            end_timestamp=self.end_timestamp,
            overhead_seconds=self.overhead_seconds,
            synchronization=self.synchronization,
            run_id=self.run_id,
            timeline_id=self.timeline_id,
            clock_name=self.clock_name,
            clock_origin=self.clock_origin,
            process_id=self.process_id,
            node_id=self.node_id,
            local_rank=self.local_rank,
            global_rank=self.global_rank,
            device_id=self.device_id,
            metadata={"reason": self.reason, **self.metadata},
            provenance=self.provenance,
        )


@dataclass(frozen=True, init=False, slots=True)
class TrainingProfile:
    """Minimal profile aggregate with primitive trace evidence.

    The aggregate is intentionally provisional and does not define resource-trace
    record families in this phase.
    """

    event_logs: tuple[TrainingEventLog, ...]
    scalar_spans: tuple[ProfileSpanSummary, ...]
    unavailable_spans: tuple[UnavailableProfileProbe, ...]
    decisions: tuple[str, ...]

    def __init__(
        self,
        *,
        event_logs: Iterable[TrainingEventLog] = (),
        scalar_spans: Iterable[ProfileSpanSummary] = (),
        unavailable_spans: Iterable[UnavailableProfileProbe] = (),
        decisions: Iterable[str] = (),
    ) -> None:
        object.__setattr__(
            self,
            "event_logs",
            _coerce_records(event_logs, TrainingEventLog, owner="TrainingProfile", field="event_logs"),
        )
        object.__setattr__(
            self,
            "scalar_spans",
            _coerce_records(scalar_spans, ProfileSpanSummary, owner="TrainingProfile", field="scalar_spans"),
        )
        object.__setattr__(
            self,
            "unavailable_spans",
            _coerce_records(
                unavailable_spans,
                UnavailableProfileProbe,
                owner="TrainingProfile",
                field="unavailable_spans",
            ),
        )
        object.__setattr__(
            self,
            "decisions",
            _coerce_decisions(decisions, owner="TrainingProfile", field="decisions"),
        )

    def events(self, *, timeline_id: str | None = None) -> tuple[TrainingEvent, ...]:
        events: list[TrainingEvent] = []
        for event_log in self.event_logs:
            if timeline_id is None or event_log.timeline_id == timeline_id:
                events.extend(event_log.events)
        return tuple(events)

    def spans(self, *, stage_name: str | None = None) -> tuple[ProfileSpanSummary, ...]:
        if stage_name is None:
            return self.scalar_spans
        return tuple(span for span in self.scalar_spans if span.stage_name == stage_name)

    def unavailable_probes(self, *, stage_name: str | None = None) -> tuple[UnavailableProfileProbe, ...]:
        if stage_name is None:
            return self.unavailable_spans
        return tuple(
            probe
            for probe in self.unavailable_spans
            if probe.stage_name == stage_name
        )

    def as_profile_summaries(self) -> tuple[ProfileSpanSummary, ...]:
        return self.scalar_spans + tuple(probe.as_span() for probe in self.unavailable_spans)


class TrainingProfileRecorder:
    """Append-only, immutable-profile recorder with deterministic timestamping."""

    def __init__(
        self,
        *,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._clock = monotonic if clock is None else clock
        self._event_logs: tuple[TrainingEventLog, ...] = ()
        self._scalar_spans: tuple[ProfileSpanSummary, ...] = ()
        self._unavailable_spans: tuple[UnavailableProfileProbe, ...] = ()
        self._decisions: tuple[str, ...] = ()

    def record_event(self, event: TrainingEvent) -> None:
        """Record a timestamped event and return nothing."""

        if not isinstance(event, TrainingEvent):
            raise RemotePhysTrainingError(
                "TrainingProfileRecorder.record_event expects a TrainingEvent.",
                owner="TrainingProfileRecorder",
                field="event",
                expected="TrainingEvent",
                actual=type(event).__name__,
            )
        event = self._with_timestamp(event)
        timeline_id = event.timeline_id or "default"
        event_logs = list(self._event_logs)
        for index, event_log in enumerate(event_logs):
            if event_log.timeline_id == timeline_id:
                event_logs[index] = event_log.append(event)
                break
        else:
            event_logs.append(TrainingEventLog(timeline_id, run_id=event.run_id, events=(event,)))
        self._event_logs = tuple(event_logs)

    def record_scalar_span(self, span: ProfileSpanSummary) -> None:
        """Record a scalar span summary."""

        if not isinstance(span, ProfileSpanSummary):
            raise RemotePhysTrainingError(
                "TrainingProfileRecorder.record_scalar_span expects a ProfileSpanSummary.",
                owner="TrainingProfileRecorder",
                field="span",
                expected="ProfileSpanSummary",
                actual=type(span).__name__,
            )
        self._scalar_spans += (self._with_timing(span),)

    def record_unavailable_probe(self, probe: UnavailableProfileProbe) -> None:
        """Record unavailable profiling evidence."""

        if not isinstance(probe, UnavailableProfileProbe):
            raise RemotePhysTrainingError(
                "TrainingProfileRecorder.record_unavailable_probe expects an UnavailableProfileProbe.",
                owner="TrainingProfileRecorder",
                field="probe",
                expected="UnavailableProfileProbe",
                actual=type(probe).__name__,
            )
        self._unavailable_spans += (probe,)

    def record_decision(self, decision: str) -> None:
        """Record a primitive decision string."""

        self._decisions += (_coerce_name(decision, owner="TrainingProfileRecorder", field="decision"),)

    @property
    def profile(self) -> TrainingProfile:
        """Return a frozen snapshot."""

        return self.snapshot()

    def snapshot(self) -> TrainingProfile:
        """Return a frozen snapshot."""

        return TrainingProfile(
            event_logs=self._event_logs,
            scalar_spans=self._scalar_spans,
            unavailable_spans=self._unavailable_spans,
            decisions=self._decisions,
        )

    def _with_timestamp(self, event: TrainingEvent) -> TrainingEvent:
        if event.timestamp is not None:
            return event
        timestamp = self._clock()
        return TrainingEvent(
            event.phase,
            event.mode,
            status=event.status,
            epoch_index=event.epoch_index,
            step_index=event.step_index,
            batch_index=event.batch_index,
            split=event.split,
            run_id=event.run_id,
            timeline_id=event.timeline_id,
            sequence_id=event.sequence_id,
            timestamp=timestamp,
            clock_name=event.clock_name,
            clock_origin=event.clock_origin,
            process_id=event.process_id,
            node_id=event.node_id,
            local_rank=event.local_rank,
            global_rank=event.global_rank,
            device_id=event.device_id,
            metadata=event.metadata,
            provenance=event.provenance,
        )

    def _with_timing(self, span: ProfileSpanSummary) -> ProfileSpanSummary:
        if span.start_timestamp is not None and span.end_timestamp is not None:
            return span
        now = self._clock()
        if span.start_timestamp is None and span.end_timestamp is None:
            start_timestamp = now
            if span.duration_seconds is None:
                end_timestamp = now
            else:
                end_timestamp = now + span.duration_seconds
        elif span.start_timestamp is None:
            end_timestamp = span.end_timestamp
            if span.duration_seconds is None:
                start_timestamp = end_timestamp
            else:
                start_timestamp = max(0.0, end_timestamp - span.duration_seconds)
        else:
            start_timestamp = span.start_timestamp
            if span.duration_seconds is None:
                end_timestamp = start_timestamp
            else:
                end_timestamp = start_timestamp + span.duration_seconds
        return ProfileSpanSummary(
            span.name,
            mode=span.mode,
            status=span.status,
            stage_name=span.stage_name,
            duration_seconds=span.duration_seconds,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            overhead_seconds=span.overhead_seconds,
            synchronization=span.synchronization,
            run_id=span.run_id,
            timeline_id=span.timeline_id,
            clock_name=span.clock_name,
            clock_origin=span.clock_origin,
            process_id=span.process_id,
            node_id=span.node_id,
            local_rank=span.local_rank,
            global_rank=span.global_rank,
            device_id=span.device_id,
            metadata=span.metadata,
            provenance=span.provenance,
        )


@runtime_checkable
class TrainingProfiler(Protocol):
    """Observer-only profiler capability for future native or adapter timing."""

    def span(
        self,
        name: str,
        *,
        mode: LoopMode | str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> ProfileSpanSummary:
        ...


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


def _coerce_optional_duration(
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


def _coerce_optional_non_negative_int(
    value: int | None,
    *,
    owner: str,
    field: str,
) -> int | None:
    if value is None:
        return None
    return coerce_non_negative_int(value, owner=owner, field=field)


def _coerce_records(
    values: Iterable[object],
    expected_type: type,
    *,
    owner: str,
    field: str,
) -> tuple[object, ...]:
    try:
        records = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be iterable.",
            owner=owner,
            field=field,
            expected=f"iterable of {expected_type.__name__}",
            actual=type(values).__name__,
        ) from exc

    for index, record in enumerate(records):
        if not isinstance(record, expected_type):
            raise RemotePhysTrainingError(
                f"{owner} {field} contains an invalid record.",
                owner=owner,
                field=field,
                expected=expected_type.__name__,
                index=index,
                actual=type(record).__name__,
            )
    return records


def _coerce_decisions(
    values: Iterable[object],
    *,
    owner: str,
    field: str,
) -> tuple[str, ...]:
    try:
        items = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be iterable.",
            owner=owner,
            field=field,
            expected="iterable of non-empty string",
            actual=type(values).__name__,
        ) from exc
    for index, item in enumerate(items):
        if not isinstance(item, str) or not item:
            raise RemotePhysTrainingError(
                f"{owner} {field} must be non-empty strings.",
                owner=owner,
                field=field,
                expected="iterable of non-empty string",
                index=index,
                actual=type(item).__name__,
            )
    return items


ProfileSpanSummary.__hash__ = None  # type: ignore[assignment]
UnavailableProfileProbe.__hash__ = None  # type: ignore[assignment]
TrainingProfile.__hash__ = None  # type: ignore[assignment]
