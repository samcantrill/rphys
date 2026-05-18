"""Primitive-oriented training result summaries."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopMode

from .profiling import TrainingProfile
from ._validation import (
    PrimitiveMapping,
    PrimitiveValue,
    coerce_non_negative_int,
    coerce_optional_non_empty_string,
    freeze_primitive_mapping,
)

__all__ = [
    "ProfileSummary",
    "TrainingEventSummary",
    "TrainingMetricSummary",
    "TrainingResult",
    "TrainingStatus",
    "TrainingStepSummary",
]


class TrainingStatus(StrEnum):
    """Primitive status labels for a training engine result."""

    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"
    PARTIAL = "partial"

    @classmethod
    def coerce(cls, value: "TrainingStatus | str") -> "TrainingStatus":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported training result status.",
                    owner="TrainingStatus",
                    field="status",
                    expected=tuple(status.value for status in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "Training result status must be a TrainingStatus or string.",
            owner="TrainingStatus",
            field="status",
            expected="TrainingStatus | str",
            actual=type(value).__name__,
        )


@dataclass(frozen=True, init=False, slots=True)
class TrainingMetricSummary:
    """Primitive metric summary suitable for persistence and PR evidence."""

    name: str
    value: PrimitiveValue
    unit: str | None
    level: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        name: str,
        value: PrimitiveValue,
        *,
        unit: str | None = None,
        level: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            _coerce_name(name, owner="TrainingMetricSummary", field="name"),
        )
        object.__setattr__(
            self,
            "value",
            _coerce_primitive(value, owner="TrainingMetricSummary", field="value"),
        )
        object.__setattr__(
            self,
            "unit",
            coerce_optional_non_empty_string(
                unit,
                owner="TrainingMetricSummary",
                field="unit",
            ),
        )
        object.__setattr__(
            self,
            "level",
            coerce_optional_non_empty_string(
                level,
                owner="TrainingMetricSummary",
                field="level",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(
                metadata,
                owner="TrainingMetricSummary",
                field="metadata",
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(
                provenance,
                owner="TrainingMetricSummary",
                field="provenance",
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class TrainingStepSummary:
    """Primitive evidence from the last or selected loop step."""

    mode: LoopMode
    epoch_index: int | None
    step_index: int | None
    batch_index: int | None
    split: str | None
    objective: PrimitiveValue
    metrics: PrimitiveMapping
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        mode: LoopMode | str,
        *,
        epoch_index: int | None = None,
        step_index: int | None = None,
        batch_index: int | None = None,
        split: str | None = None,
        objective: PrimitiveValue = None,
        metrics: Mapping[object, object] | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(self, "mode", LoopMode.coerce(mode))
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
                owner="TrainingStepSummary",
                field="split",
            ),
        )
        object.__setattr__(
            self,
            "objective",
            _coerce_primitive(objective, owner="TrainingStepSummary", field="objective"),
        )
        object.__setattr__(
            self,
            "metrics",
            freeze_primitive_mapping(
                metrics,
                owner="TrainingStepSummary",
                field="metrics",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(
                metadata,
                owner="TrainingStepSummary",
                field="metadata",
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(
                provenance,
                owner="TrainingStepSummary",
                field="provenance",
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class TrainingEventSummary:
    """Primitive event count/status summary."""

    name: str
    status: str
    count: int
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        name: str,
        *,
        status: str = "observed",
        count: int = 1,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            _coerce_name(name, owner="TrainingEventSummary", field="name"),
        )
        object.__setattr__(
            self,
            "status",
            _coerce_name(status, owner="TrainingEventSummary", field="status"),
        )
        object.__setattr__(
            self,
            "count",
            coerce_non_negative_int(count, owner="TrainingEventSummary", field="count"),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(
                metadata,
                owner="TrainingEventSummary",
                field="metadata",
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(
                provenance,
                owner="TrainingEventSummary",
                field="provenance",
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class ProfileSummary:
    """Primitive profile/span summary without profiler backend state."""

    name: str
    status: str
    duration_seconds: float | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        name: str,
        *,
        status: str = "available",
        duration_seconds: float | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            _coerce_name(name, owner="ProfileSummary", field="name"),
        )
        object.__setattr__(
            self,
            "status",
            _coerce_name(status, owner="ProfileSummary", field="status"),
        )
        if duration_seconds is not None and (
            isinstance(duration_seconds, bool)
            or not isinstance(duration_seconds, (int, float))
            or duration_seconds < 0
        ):
            raise RemotePhysTrainingError(
                "ProfileSummary duration_seconds must be non-negative when provided.",
                owner="ProfileSummary",
                field="duration_seconds",
                expected="non-negative number | None",
                actual=type(duration_seconds).__name__,
            )
        object.__setattr__(
            self,
            "duration_seconds",
            None if duration_seconds is None else float(duration_seconds),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(
                metadata,
                owner="ProfileSummary",
                field="metadata",
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(
                provenance,
                owner="ProfileSummary",
                field="provenance",
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class TrainingResult:
    """Primitive outcome summary returned by a training engine."""

    status: TrainingStatus
    mode: LoopMode
    epoch_count: int
    step_count: int
    batch_count: int
    failure: str | None
    metrics: Mapping[str, TrainingMetricSummary]
    last_step: TrainingStepSummary | None
    events: tuple[TrainingEventSummary, ...]
    profiles: tuple[ProfileSummary, ...]
    training_profile: TrainingProfile | None
    monitored_metric: str | None
    checkpoint_id: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        *,
        status: TrainingStatus | str,
        mode: LoopMode | str,
        epoch_count: int = 0,
        step_count: int = 0,
        batch_count: int = 0,
        failure: str | None = None,
        metrics: Iterable[TrainingMetricSummary] = (),
        last_step: TrainingStepSummary | None = None,
        events: Iterable[TrainingEventSummary] = (),
        profiles: Iterable[ProfileSummary] | None = None,
        monitored_metric: str | None = None,
        checkpoint_id: str | None = None,
        training_profile: TrainingProfile | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(self, "status", TrainingStatus.coerce(status))
        object.__setattr__(self, "mode", LoopMode.coerce(mode))
        object.__setattr__(
            self,
            "epoch_count",
            coerce_non_negative_int(epoch_count, owner="TrainingResult", field="epoch_count"),
        )
        object.__setattr__(
            self,
            "step_count",
            coerce_non_negative_int(step_count, owner="TrainingResult", field="step_count"),
        )
        object.__setattr__(
            self,
            "batch_count",
            coerce_non_negative_int(batch_count, owner="TrainingResult", field="batch_count"),
        )
        object.__setattr__(
            self,
            "failure",
            coerce_optional_non_empty_string(
                failure,
                owner="TrainingResult",
                field="failure",
            ),
        )
        object.__setattr__(self, "metrics", _coerce_metric_summaries(metrics))
        if last_step is not None and not isinstance(last_step, TrainingStepSummary):
            raise RemotePhysTrainingError(
                "TrainingResult last_step must be a TrainingStepSummary.",
                owner="TrainingResult",
                field="last_step",
                expected="TrainingStepSummary | None",
                actual=type(last_step).__name__,
            )
        object.__setattr__(self, "last_step", last_step)
        object.__setattr__(
            self,
            "events",
            _coerce_records(events, TrainingEventSummary, field="events"),
        )
        if training_profile is not None and not isinstance(training_profile, TrainingProfile):
            raise RemotePhysTrainingError(
                "TrainingResult training_profile must be a TrainingProfile or None.",
                owner="TrainingResult",
                field="training_profile",
                expected="TrainingProfile | None",
                actual=type(training_profile).__name__,
            )
        object.__setattr__(
            self,
            "training_profile",
            training_profile,
        )
        if profiles is None:
            derived_profiles = _coerce_profile_summaries(training_profile) if training_profile is not None else ()
            object.__setattr__(
                self,
                "profiles",
                derived_profiles,
            )
        else:
            object.__setattr__(
                self,
                "profiles",
                _coerce_records(
                    profiles,
                    ProfileSummary,
                    field="profiles",
                ),
            )
        object.__setattr__(
            self,
            "monitored_metric",
            coerce_optional_non_empty_string(
                monitored_metric,
                owner="TrainingResult",
                field="monitored_metric",
            ),
        )
        object.__setattr__(
            self,
            "checkpoint_id",
            coerce_optional_non_empty_string(
                checkpoint_id,
                owner="TrainingResult",
                field="checkpoint_id",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(
                metadata,
                owner="TrainingResult",
                field="metadata",
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(
                provenance,
                owner="TrainingResult",
                field="provenance",
            ),
        )


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


def _coerce_primitive(value: object, *, owner: str, field: str) -> PrimitiveValue:
    if value is not None and not isinstance(value, (str, int, float, bool)):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be primitive.",
            owner=owner,
            field=field,
            expected="str | int | float | bool | None",
            actual=type(value).__name__,
        )
    return value


def _coerce_optional_index(value: int | None, *, field: str) -> int | None:
    if value is None:
        return None
    return coerce_non_negative_int(value, owner="TrainingStepSummary", field=field)


def _coerce_metric_summaries(
    values: Iterable[TrainingMetricSummary],
) -> Mapping[str, TrainingMetricSummary]:
    try:
        summaries = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            "TrainingResult metrics must be iterable.",
            owner="TrainingResult",
            field="metrics",
            expected="iterable of TrainingMetricSummary",
            actual=type(values).__name__,
        ) from exc
    by_name: dict[str, TrainingMetricSummary] = {}
    for index, summary in enumerate(summaries):
        if not isinstance(summary, TrainingMetricSummary):
            raise RemotePhysTrainingError(
                "TrainingResult metrics must contain TrainingMetricSummary records.",
                owner="TrainingResult",
                field="metrics",
                index=index,
                actual=type(summary).__name__,
            )
        if summary.name in by_name:
            raise RemotePhysTrainingError(
                "TrainingResult metric summaries must not repeat names.",
                owner="TrainingResult",
                field="metrics",
                name=summary.name,
            )
        by_name[summary.name] = summary
    return MappingProxyType(by_name)


def _coerce_records(
    values: Iterable[object],
    expected_type: type,
    *,
    field: str,
) -> tuple[object, ...]:
    try:
        records = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            f"TrainingResult {field} must be iterable.",
            owner="TrainingResult",
            field=field,
            expected=f"iterable of {expected_type.__name__}",
            actual=type(values).__name__,
        ) from exc
    for index, record in enumerate(records):
        if not isinstance(record, expected_type):
            raise RemotePhysTrainingError(
                f"TrainingResult {field} contains an invalid record.",
                owner="TrainingResult",
                field=field,
                expected=expected_type.__name__,
                index=index,
                actual=type(record).__name__,
            )
    return records


def _coerce_profile_summaries(training_profile: TrainingProfile) -> tuple[ProfileSummary, ...]:
    summaries: list[ProfileSummary] = []
    for span in training_profile.as_profile_summaries():
        summaries.append(
            ProfileSummary(
                span.name,
                status=span.status,
                duration_seconds=span.duration_seconds,
                metadata=span.metadata,
                provenance=span.provenance,
            )
        )
    return tuple(summaries)


TrainingMetricSummary.__hash__ = None  # type: ignore[assignment]
TrainingStepSummary.__hash__ = None  # type: ignore[assignment]
TrainingEventSummary.__hash__ = None  # type: ignore[assignment]
ProfileSummary.__hash__ = None  # type: ignore[assignment]
TrainingResult.__hash__ = None  # type: ignore[assignment]
