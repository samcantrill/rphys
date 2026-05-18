"""Dependency-light optimization policy descriptors for training runtime configuration."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum

from rphys.errors import RemotePhysTrainingError

from ._validation import (
    PrimitiveMapping,
    coerce_optional_non_empty_string,
    freeze_primitive_mapping,
)

__all__ = [
    "CompilePolicy",
    "KernelPolicy",
    "PrecisionPolicy",
    "PolicyStatus",
]


class PolicyStatus(StrEnum):
    """Common optimization-policy state for checkpoint-light execution."""

    REQUESTED = "requested"
    APPLIED = "applied"
    FALLBACK = "fallback"
    DISABLED = "disabled"
    UNSUPPORTED = "unsupported"
    UNAVAILABLE = "unavailable"

    @classmethod
    def coerce(cls, value: "PolicyStatus | str") -> "PolicyStatus":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported policy status.",
                    owner="PolicyStatus",
                    field="status",
                    expected=tuple(status.value for status in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "PolicyStatus must be a PolicyStatus or string.",
            owner="PolicyStatus",
            field="status",
            expected="PolicyStatus | str",
            actual=type(value).__name__,
        )


@dataclass(frozen=True, init=False, slots=True)
class PrecisionPolicy:
    """Precision policy evidence with fallback and backend applicability."""

    requested_precision: str | None
    applied_precision: str | None
    fallback_precision: str | None
    status: PolicyStatus
    backend: str | None
    supported_backends: tuple[str, ...]
    numerical_equivalence: str | None
    unsupported_reason: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        requested_precision: str | None = None,
        *,
        applied_precision: str | None = None,
        fallback_precision: str | None = None,
        status: PolicyStatus | str = PolicyStatus.REQUESTED,
        backend: str | None = None,
        supported_backends: Iterable[str] | None = None,
        numerical_equivalence: str | None = None,
        unsupported_reason: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        status = PolicyStatus.coerce(status)
        object.__setattr__(
            self,
            "requested_precision",
            coerce_optional_non_empty_string(
                requested_precision,
                owner="PrecisionPolicy",
                field="requested_precision",
            ),
        )
        object.__setattr__(
            self,
            "applied_precision",
            coerce_optional_non_empty_string(
                applied_precision,
                owner="PrecisionPolicy",
                field="applied_precision",
            ),
        )
        object.__setattr__(
            self,
            "fallback_precision",
            coerce_optional_non_empty_string(
                fallback_precision,
                owner="PrecisionPolicy",
                field="fallback_precision",
            ),
        )
        object.__setattr__(self, "status", status)
        object.__setattr__(
            self,
            "backend",
            coerce_optional_non_empty_string(backend, owner="PrecisionPolicy", field="backend"),
        )
        object.__setattr__(
            self,
            "numerical_equivalence",
            coerce_optional_non_empty_string(
                numerical_equivalence,
                owner="PrecisionPolicy",
                field="numerical_equivalence",
            ),
        )
        object.__setattr__(
            self,
            "unsupported_reason",
            coerce_optional_non_empty_string(
                unsupported_reason,
                owner="PrecisionPolicy",
                field="unsupported_reason",
            ),
        )
        object.__setattr__(
            self,
            "supported_backends",
            tuple(_coerce_backend_list(supported_backends, owner="PrecisionPolicy")),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(metadata, owner="PrecisionPolicy", field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(provenance, owner="PrecisionPolicy", field="provenance"),
        )

        if status is PolicyStatus.DISABLED:
            if requested_precision is not None or applied_precision is not None or fallback_precision is not None:
                raise RemotePhysTrainingError(
                    "PrecisionPolicy disabled should not report precision states.",
                    owner="PrecisionPolicy",
                    field="status",
                    value=status.value,
                )
            if unsupported_reason is not None:
                raise RemotePhysTrainingError(
                    "Disabled PrecisionPolicy cannot be unsupported.",
                    owner="PrecisionPolicy",
                    field="unsupported_reason",
                    value=unsupported_reason,
                )
        if status in {PolicyStatus.UNSUPPORTED, PolicyStatus.UNAVAILABLE} and unsupported_reason is None:
            raise RemotePhysTrainingError(
                "PrecisionPolicy requires unsupported_reason when unsupported or unavailable.",
                owner="PrecisionPolicy",
                field="unsupported_reason",
            )
        if status is PolicyStatus.FALLBACK and fallback_precision is None:
            raise RemotePhysTrainingError(
                "PrecisionPolicy fallback requires fallback_precision.",
                owner="PrecisionPolicy",
                field="fallback_precision",
            )
        if status in {PolicyStatus.APPLIED, PolicyStatus.FALLBACK} and applied_precision is None:
            raise RemotePhysTrainingError(
                "PrecisionPolicy requires applied_precision when status is applied or fallback.",
                owner="PrecisionPolicy",
                field="applied_precision",
            )
        if status in {PolicyStatus.REQUESTED, PolicyStatus.APPLIED, PolicyStatus.FALLBACK} and requested_precision is None:
            raise RemotePhysTrainingError(
                "PrecisionPolicy requires requested_precision for active status.",
                owner="PrecisionPolicy",
                field="requested_precision",
            )


@dataclass(frozen=True, init=False, slots=True)
class CompilePolicy:
    """Compile policy evidence with backend mapping and fallback reason."""

    requested_mode: str | None
    applied_mode: str | None
    fallback_mode: str | None
    status: PolicyStatus
    backend: str | None
    supported_backends: tuple[str, ...]
    backend_equivalence_note: str | None
    unsupported_reason: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        requested_mode: str | None = None,
        *,
        applied_mode: str | None = None,
        fallback_mode: str | None = None,
        status: PolicyStatus | str = PolicyStatus.REQUESTED,
        backend: str | None = None,
        supported_backends: Iterable[str] | None = None,
        backend_equivalence_note: str | None = None,
        unsupported_reason: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        status = PolicyStatus.coerce(status)
        object.__setattr__(
            self,
            "requested_mode",
            coerce_optional_non_empty_string(requested_mode, owner="CompilePolicy", field="requested_mode"),
        )
        object.__setattr__(
            self,
            "applied_mode",
            coerce_optional_non_empty_string(applied_mode, owner="CompilePolicy", field="applied_mode"),
        )
        object.__setattr__(
            self,
            "fallback_mode",
            coerce_optional_non_empty_string(fallback_mode, owner="CompilePolicy", field="fallback_mode"),
        )
        object.__setattr__(self, "status", status)
        object.__setattr__(
            self,
            "backend",
            coerce_optional_non_empty_string(backend, owner="CompilePolicy", field="backend"),
        )
        object.__setattr__(
            self,
            "unsupported_reason",
            coerce_optional_non_empty_string(
                unsupported_reason,
                owner="CompilePolicy",
                field="unsupported_reason",
            ),
        )
        object.__setattr__(
            self,
            "backend_equivalence_note",
            coerce_optional_non_empty_string(
                backend_equivalence_note,
                owner="CompilePolicy",
                field="backend_equivalence_note",
            ),
        )
        object.__setattr__(
            self,
            "supported_backends",
            tuple(_coerce_backend_list(supported_backends, owner="CompilePolicy")),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(metadata, owner="CompilePolicy", field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(provenance, owner="CompilePolicy", field="provenance"),
        )

        if status is PolicyStatus.DISABLED:
            if requested_mode is not None or applied_mode is not None or fallback_mode is not None:
                raise RemotePhysTrainingError(
                    "CompilePolicy disabled should not report mode states.",
                    owner="CompilePolicy",
                    field="status",
                    value=status.value,
                )
            if unsupported_reason is not None:
                raise RemotePhysTrainingError(
                    "Disabled CompilePolicy cannot be unsupported.",
                    owner="CompilePolicy",
                    field="unsupported_reason",
                    value=unsupported_reason,
                )
        if status in {PolicyStatus.UNSUPPORTED, PolicyStatus.UNAVAILABLE} and unsupported_reason is None:
            raise RemotePhysTrainingError(
                "CompilePolicy requires unsupported_reason when unsupported or unavailable.",
                owner="CompilePolicy",
                field="unsupported_reason",
            )
        if status is PolicyStatus.FALLBACK and fallback_mode is None:
            raise RemotePhysTrainingError(
                "CompilePolicy fallback requires fallback_mode.",
                owner="CompilePolicy",
                field="fallback_mode",
            )
        if status in {PolicyStatus.APPLIED, PolicyStatus.FALLBACK} and applied_mode is None:
            raise RemotePhysTrainingError(
                "CompilePolicy requires applied_mode when status is applied or fallback.",
                owner="CompilePolicy",
                field="applied_mode",
            )
        if status in {PolicyStatus.REQUESTED, PolicyStatus.APPLIED, PolicyStatus.FALLBACK} and requested_mode is None:
            raise RemotePhysTrainingError(
                "CompilePolicy requires requested_mode for active status.",
                owner="CompilePolicy",
                field="requested_mode",
            )


@dataclass(frozen=True, init=False, slots=True)
class KernelPolicy:
    """Kernel dispatch policy evidence with requested and applied fallback states."""

    requested_kernel: str | None
    applied_kernel: str | None
    fallback_kernel: str | None
    status: PolicyStatus
    backend: str | None
    supported_backends: tuple[str, ...]
    backend_scope: str | None
    unsupported_reason: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        requested_kernel: str | None = None,
        *,
        applied_kernel: str | None = None,
        fallback_kernel: str | None = None,
        status: PolicyStatus | str = PolicyStatus.REQUESTED,
        backend: str | None = None,
        supported_backends: Iterable[str] | None = None,
        backend_scope: str | None = None,
        unsupported_reason: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        status = PolicyStatus.coerce(status)
        object.__setattr__(
            self,
            "requested_kernel",
            coerce_optional_non_empty_string(requested_kernel, owner="KernelPolicy", field="requested_kernel"),
        )
        object.__setattr__(
            self,
            "applied_kernel",
            coerce_optional_non_empty_string(applied_kernel, owner="KernelPolicy", field="applied_kernel"),
        )
        object.__setattr__(
            self,
            "fallback_kernel",
            coerce_optional_non_empty_string(fallback_kernel, owner="KernelPolicy", field="fallback_kernel"),
        )
        object.__setattr__(self, "status", status)
        object.__setattr__(
            self,
            "backend",
            coerce_optional_non_empty_string(backend, owner="KernelPolicy", field="backend"),
        )
        object.__setattr__(
            self,
            "unsupported_reason",
            coerce_optional_non_empty_string(
                unsupported_reason,
                owner="KernelPolicy",
                field="unsupported_reason",
            ),
        )
        object.__setattr__(
            self,
            "backend_scope",
            coerce_optional_non_empty_string(backend_scope, owner="KernelPolicy", field="backend_scope"),
        )
        object.__setattr__(
            self,
            "supported_backends",
            tuple(_coerce_backend_list(supported_backends, owner="KernelPolicy")),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(metadata, owner="KernelPolicy", field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(provenance, owner="KernelPolicy", field="provenance"),
        )

        if status is PolicyStatus.DISABLED:
            if requested_kernel is not None or applied_kernel is not None or fallback_kernel is not None:
                raise RemotePhysTrainingError(
                    "KernelPolicy disabled should not report kernel states.",
                    owner="KernelPolicy",
                    field="status",
                    value=status.value,
                )
            if unsupported_reason is not None:
                raise RemotePhysTrainingError(
                    "Disabled KernelPolicy cannot be unsupported.",
                    owner="KernelPolicy",
                    field="unsupported_reason",
                    value=unsupported_reason,
                )
        if status in {PolicyStatus.UNSUPPORTED, PolicyStatus.UNAVAILABLE} and unsupported_reason is None:
            raise RemotePhysTrainingError(
                "KernelPolicy requires unsupported_reason when unsupported or unavailable.",
                owner="KernelPolicy",
                field="unsupported_reason",
            )
        if status is PolicyStatus.FALLBACK and fallback_kernel is None:
            raise RemotePhysTrainingError(
                "KernelPolicy fallback requires fallback_kernel.",
                owner="KernelPolicy",
                field="fallback_kernel",
            )
        if status in {PolicyStatus.APPLIED, PolicyStatus.FALLBACK} and applied_kernel is None:
            raise RemotePhysTrainingError(
                "KernelPolicy requires applied_kernel when status is applied or fallback.",
                owner="KernelPolicy",
                field="applied_kernel",
            )
        if status in {PolicyStatus.REQUESTED, PolicyStatus.APPLIED, PolicyStatus.FALLBACK} and requested_kernel is None:
            raise RemotePhysTrainingError(
                "KernelPolicy requires requested_kernel for active status.",
                owner="KernelPolicy",
                field="requested_kernel",
            )


def _coerce_backend_list(values: Iterable[str] | None, *, owner: str) -> tuple[str, ...]:
    if values is None:
        return ()
    try:
        coerced = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            f"{owner} supported_backends must be iterable.",
            owner=owner,
            field="supported_backends",
            expected="iterable[str] | None",
            actual=type(values).__name__,
        ) from exc
    for index, value in enumerate(coerced):
        if not isinstance(value, str) or not value:
            raise RemotePhysTrainingError(
                f"{owner} supported_backends values must be non-empty strings.",
                owner=owner,
                field="supported_backends",
                index=index,
                actual=type(value).__name__,
            )
    return coerced


PrecisionPolicy.__hash__ = None  # type: ignore[assignment]
CompilePolicy.__hash__ = None  # type: ignore[assignment]
KernelPolicy.__hash__ = None  # type: ignore[assignment]
