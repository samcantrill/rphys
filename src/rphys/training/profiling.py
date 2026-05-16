"""Dependency-light training profile records."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopMode

from ._validation import (
    PrimitiveMapping,
    coerce_optional_non_empty_string,
    freeze_primitive_mapping,
)

__all__ = [
    "ProfileSpanSummary",
    "TrainingProfiler",
    "UnavailableProfileProbe",
]


@dataclass(frozen=True, init=False, slots=True)
class ProfileSpanSummary:
    """Primitive span summary with explicit timing availability."""

    name: str
    mode: LoopMode | None
    status: str
    duration_seconds: float | None
    overhead_seconds: float | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        name: str,
        *,
        mode: LoopMode | str | None = None,
        status: str = "available",
        duration_seconds: float | None = None,
        overhead_seconds: float | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(self, "name", _coerce_name(name, owner="ProfileSpanSummary", field="name"))
        object.__setattr__(self, "mode", None if mode is None else LoopMode.coerce(mode))
        object.__setattr__(self, "status", _coerce_name(status, owner="ProfileSpanSummary", field="status"))
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
            "overhead_seconds",
            _coerce_optional_duration(
                overhead_seconds,
                owner="ProfileSpanSummary",
                field="overhead_seconds",
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
    overhead_seconds: float | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        name: str,
        *,
        reason: str,
        overhead_seconds: float | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(self, "name", _coerce_name(name, owner="UnavailableProfileProbe", field="name"))
        object.__setattr__(self, "reason", _coerce_name(reason, owner="UnavailableProfileProbe", field="reason"))
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
            status="unavailable",
            overhead_seconds=self.overhead_seconds,
            metadata={"reason": self.reason, **self.metadata},
            provenance=self.provenance,
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


def _coerce_optional_duration(
    value: float | None,
    *,
    owner: str,
    field: str,
) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be non-negative when provided.",
            owner=owner,
            field=field,
            expected="non-negative number | None",
            actual=type(value).__name__,
        )
    return float(value)


ProfileSpanSummary.__hash__ = None  # type: ignore[assignment]
UnavailableProfileProbe.__hash__ = None  # type: ignore[assignment]
