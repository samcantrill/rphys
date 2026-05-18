"""Descriptive experiment tier and restart evidence records."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum

from rphys.errors import RemotePhysTrainingError

from ._validation import (
    PrimitiveMapping,
    coerce_non_negative_int,
    coerce_optional_non_empty_string,
    coerce_optional_positive_int,
    freeze_primitive_mapping,
)
from .checkpoint import CheckpointRef

__all__ = [
    "ExperimentTierName",
    "ExperimentTierSpec",
    "RestartCompatibilityStatus",
    "RestartState",
    "default_experiment_tiers",
]


class ExperimentTierName(StrEnum):
    """Descriptive validation tiers that scale the same execution path."""

    DEBUG = "debug"
    SMOKE = "smoke"
    SIGNAL = "signal"
    COMPARISON = "comparison"
    FULL = "full"

    @classmethod
    def coerce(cls, value: "ExperimentTierName | str") -> "ExperimentTierName":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported experiment tier.",
                    owner="ExperimentTierName",
                    field="tier",
                    expected=tuple(tier.value for tier in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ExperimentTierName must be an ExperimentTierName or string.",
            owner="ExperimentTierName",
            field="tier",
            expected="ExperimentTierName | str",
            actual=type(value).__name__,
        )


class RestartCompatibilityStatus(StrEnum):
    """Restart compatibility status for a checkpoint-linked snapshot."""

    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    AMBIGUOUS = "ambiguous"
    UNAVAILABLE = "unavailable"

    @classmethod
    def coerce(
        cls,
        value: "RestartCompatibilityStatus | str",
    ) -> "RestartCompatibilityStatus":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported restart compatibility status.",
                    owner="RestartCompatibilityStatus",
                    field="compatibility_status",
                    expected=tuple(status.value for status in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "RestartCompatibilityStatus must be a RestartCompatibilityStatus or string.",
            owner="RestartCompatibilityStatus",
            field="compatibility_status",
            expected="RestartCompatibilityStatus | str",
            actual=type(value).__name__,
        )


@dataclass(frozen=True, init=False, slots=True)
class ExperimentTierSpec:
    """Scale descriptor for validation runs, not a scheduler or runtime policy.

    Limits are optional positive integers describing the same code, loader,
    checkpoint, and profiling path at different breadth. Fingerprints and
    expected evidence names let downstream systems reason about coverage
    without `rphys` owning orchestration, cost dashboards, or artifact
    lifecycle.
    """

    tier: ExperimentTierName
    description: str | None
    subject_limit: int | None
    record_limit: int | None
    sample_limit: int | None
    epoch_limit: int | None
    step_limit: int | None
    batch_limit: int | None
    worker_limit: int | None
    same_execution_path: bool
    expected_evidence: tuple[str, ...]
    loader_fingerprint: str | None
    materialization_fingerprint: str | None
    data_path_fingerprint: str | None
    profile_fingerprint: str | None
    checkpoint_fingerprint: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        tier: ExperimentTierName | str,
        *,
        description: str | None = None,
        subject_limit: int | None = None,
        record_limit: int | None = None,
        sample_limit: int | None = None,
        epoch_limit: int | None = None,
        step_limit: int | None = None,
        batch_limit: int | None = None,
        worker_limit: int | None = None,
        same_execution_path: bool = True,
        expected_evidence: Iterable[str] = (),
        loader_fingerprint: str | None = None,
        materialization_fingerprint: str | None = None,
        data_path_fingerprint: str | None = None,
        profile_fingerprint: str | None = None,
        checkpoint_fingerprint: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        same_execution_path = _coerce_bool(
            same_execution_path,
            owner="ExperimentTierSpec",
            field="same_execution_path",
        )
        if not same_execution_path:
            raise RemotePhysTrainingError(
                "ExperimentTierSpec must describe the same execution path at a smaller or larger scale.",
                owner="ExperimentTierSpec",
                field="same_execution_path",
                value=same_execution_path,
            )

        object.__setattr__(self, "tier", ExperimentTierName.coerce(tier))
        object.__setattr__(
            self,
            "description",
            coerce_optional_non_empty_string(description, owner="ExperimentTierSpec", field="description"),
        )
        for field, value in (
            ("subject_limit", subject_limit),
            ("record_limit", record_limit),
            ("sample_limit", sample_limit),
            ("epoch_limit", epoch_limit),
            ("step_limit", step_limit),
            ("batch_limit", batch_limit),
            ("worker_limit", worker_limit),
        ):
            object.__setattr__(
                self,
                field,
                coerce_optional_positive_int(value, owner="ExperimentTierSpec", field=field),
            )
        object.__setattr__(self, "same_execution_path", same_execution_path)
        object.__setattr__(
            self,
            "expected_evidence",
            _coerce_names(expected_evidence, owner="ExperimentTierSpec", field="expected_evidence"),
        )
        for field, value in (
            ("loader_fingerprint", loader_fingerprint),
            ("materialization_fingerprint", materialization_fingerprint),
            ("data_path_fingerprint", data_path_fingerprint),
            ("profile_fingerprint", profile_fingerprint),
            ("checkpoint_fingerprint", checkpoint_fingerprint),
        ):
            object.__setattr__(
                self,
                field,
                coerce_optional_non_empty_string(value, owner="ExperimentTierSpec", field=field),
            )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(metadata, owner="ExperimentTierSpec", field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(provenance, owner="ExperimentTierSpec", field="provenance"),
        )


@dataclass(frozen=True, init=False, slots=True)
class RestartState:
    """Checkpoint-linked restart snapshot with profile and data-path evidence.

    This record states where a run can resume and why that resume is or is not
    compatible with the measured data path. It never owns checkpoint payloads,
    filesystem lifecycle, job scheduling, or retry policy.
    """

    checkpoint_ref: CheckpointRef | None
    checkpoint_ref_id: str
    tier: ExperimentTierName | None
    run_id: str | None
    timeline_id: str | None
    epoch: int | None
    step: int | None
    batch_index: int | None
    loader_fingerprint: str | None
    materialization_fingerprint: str | None
    data_path_fingerprint: str | None
    profile_fingerprint: str | None
    profile_summary_id: str | None
    checkpoint_fingerprint: str | None
    completion_markers: tuple[str, ...]
    compatibility_status: RestartCompatibilityStatus
    compatibility_note: str
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        *,
        checkpoint_ref: CheckpointRef | None = None,
        checkpoint_ref_id: str | None = None,
        tier: ExperimentTierName | str | None = None,
        run_id: str | None = None,
        timeline_id: str | None = None,
        epoch: int | None = None,
        step: int | None = None,
        batch_index: int | None = None,
        loader_fingerprint: str | None = None,
        materialization_fingerprint: str | None = None,
        data_path_fingerprint: str | None = None,
        profile_fingerprint: str | None = None,
        profile_summary_id: str | None = None,
        checkpoint_fingerprint: str | None = None,
        completion_markers: Iterable[str] = (),
        compatibility_status: RestartCompatibilityStatus | str = RestartCompatibilityStatus.AMBIGUOUS,
        compatibility_note: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        if checkpoint_ref is not None and not isinstance(checkpoint_ref, CheckpointRef):
            raise RemotePhysTrainingError(
                "RestartState checkpoint_ref must be a CheckpointRef when provided.",
                owner="RestartState",
                field="checkpoint_ref",
                expected="CheckpointRef | None",
                actual=type(checkpoint_ref).__name__,
            )
        resolved_ref_id = checkpoint_ref.ref_id if checkpoint_ref is not None else checkpoint_ref_id
        resolved_ref_id = _coerce_name(resolved_ref_id, owner="RestartState", field="checkpoint_ref_id")
        if checkpoint_ref_id is not None and checkpoint_ref is not None and checkpoint_ref_id != checkpoint_ref.ref_id:
            raise RemotePhysTrainingError(
                "RestartState checkpoint_ref_id must match checkpoint_ref.ref_id.",
                owner="RestartState",
                field="checkpoint_ref_id",
                checkpoint_ref_id=checkpoint_ref_id,
                checkpoint_ref_ref_id=checkpoint_ref.ref_id,
            )

        object.__setattr__(self, "checkpoint_ref", checkpoint_ref)
        object.__setattr__(self, "checkpoint_ref_id", resolved_ref_id)
        object.__setattr__(self, "tier", ExperimentTierName.coerce(tier) if tier is not None else None)
        object.__setattr__(
            self,
            "run_id",
            coerce_optional_non_empty_string(run_id, owner="RestartState", field="run_id"),
        )
        object.__setattr__(
            self,
            "timeline_id",
            coerce_optional_non_empty_string(timeline_id, owner="RestartState", field="timeline_id"),
        )
        for field, value in (("epoch", epoch), ("step", step), ("batch_index", batch_index)):
            object.__setattr__(
                self,
                field,
                coerce_non_negative_int(value, owner="RestartState", field=field) if value is not None else None,
            )
        for field, value in (
            ("loader_fingerprint", loader_fingerprint),
            ("materialization_fingerprint", materialization_fingerprint),
            ("data_path_fingerprint", data_path_fingerprint),
            ("profile_fingerprint", profile_fingerprint),
            ("profile_summary_id", profile_summary_id),
            ("checkpoint_fingerprint", checkpoint_fingerprint),
        ):
            object.__setattr__(
                self,
                field,
                coerce_optional_non_empty_string(value, owner="RestartState", field=field),
            )
        object.__setattr__(
            self,
            "completion_markers",
            _coerce_names(
                completion_markers,
                owner="RestartState",
                field="completion_markers",
                allow_empty=False,
            ),
        )
        object.__setattr__(
            self,
            "compatibility_status",
            RestartCompatibilityStatus.coerce(compatibility_status),
        )
        object.__setattr__(
            self,
            "compatibility_note",
            _coerce_name(compatibility_note, owner="RestartState", field="compatibility_note"),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(metadata, owner="RestartState", field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(provenance, owner="RestartState", field="provenance"),
        )


def default_experiment_tiers() -> tuple[ExperimentTierSpec, ...]:
    """Return threshold-free descriptors for the standard validation breadths."""

    return (
        ExperimentTierSpec(
            ExperimentTierName.DEBUG,
            description="single-pass structural check of the real execution path",
            sample_limit=1,
            epoch_limit=1,
            step_limit=1,
            batch_limit=1,
            worker_limit=1,
            expected_evidence=("training_events", "profile_spans", "unavailable_probes"),
        ),
        ExperimentTierSpec(
            ExperimentTierName.SMOKE,
            description="small deterministic run through training, data-path, and checkpoint evidence",
            sample_limit=8,
            epoch_limit=1,
            step_limit=5,
            batch_limit=5,
            worker_limit=1,
            expected_evidence=("training_events", "profile_spans", "checkpoint_refs", "data_path_fingerprints"),
        ),
        ExperimentTierSpec(
            ExperimentTierName.SIGNAL,
            description="broader synthetic run with resource and probe evidence",
            subject_limit=2,
            record_limit=2,
            sample_limit=32,
            epoch_limit=2,
            step_limit=20,
            expected_evidence=("resource_traces", "model_probes", "data_probes", "checkpoint_refs"),
        ),
        ExperimentTierSpec(
            ExperimentTierName.COMPARISON,
            description="repeatable run breadth for comparing engines or policy choices",
            subject_limit=3,
            record_limit=3,
            sample_limit=96,
            epoch_limit=3,
            step_limit=60,
            expected_evidence=("profile_fingerprint", "data_path_fingerprint", "restart_state"),
        ),
        ExperimentTierSpec(
            ExperimentTierName.FULL,
            description="configured complete run using the same validated path",
            expected_evidence=(
                "training_events",
                "profile_summary",
                "checkpoint_catalog",
                "restart_state",
                "data_path_profile",
            ),
        ),
    )


def _coerce_bool(value: object, *, owner: str, field: str) -> bool:
    if not isinstance(value, bool):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a boolean.",
            owner=owner,
            field=field,
            expected="bool",
            actual=type(value).__name__,
        )
    return value


def _coerce_name(value: str | None, *, owner: str, field: str) -> str:
    coerced = coerce_optional_non_empty_string(value, owner=owner, field=field)
    if coerced is None:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a non-empty string.",
            owner=owner,
            field=field,
            expected="non-empty string",
            actual=type(value).__name__,
        )
    return coerced


def _coerce_names(
    values: Iterable[str],
    *,
    owner: str,
    field: str,
    allow_empty: bool = True,
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be an iterable of non-empty strings.",
            owner=owner,
            field=field,
            expected="iterable[str]",
            actual=type(values).__name__,
        )
    try:
        names = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be iterable.",
            owner=owner,
            field=field,
            expected="iterable[str]",
            actual=type(values).__name__,
        ) from exc
    if not allow_empty and not names:
        raise RemotePhysTrainingError(
            f"{owner} {field} must contain at least one marker.",
            owner=owner,
            field=field,
            expected="non-empty iterable[str]",
        )
    for index, name in enumerate(names):
        if not isinstance(name, str) or not name:
            raise RemotePhysTrainingError(
                f"{owner} {field} values must be non-empty strings.",
                owner=owner,
                field=field,
                index=index,
                actual=type(name).__name__,
            )
    return names


ExperimentTierSpec.__hash__ = None  # type: ignore[assignment]
RestartState.__hash__ = None  # type: ignore[assignment]
