"""Dependency-light probe contracts for training diagnostics."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Protocol, runtime_checkable

from rphys.errors import RemotePhysTrainingError

from ._validation import (
    PrimitiveMapping,
    PrimitiveValue,
    coerce_non_negative_int,
    coerce_optional_non_empty_string,
    coerce_optional_positive_int,
    freeze_primitive_mapping,
)

__all__ = [
    "DataFieldProbeSummary",
    "DataProbeSummary",
    "DataSampleProbeSummary",
    "ModelActivationProbeSummary",
    "ModelGradientProbeSummary",
    "ModelHealthProbeSummary",
    "ModelParameterProbeSummary",
    "ModelProbeSummary",
    "ModelUpdateProbeSummary",
    "ProbeAggregation",
    "ProbeCadence",
    "ProbeCadenceMode",
    "ProbeFailurePolicy",
    "ProbeHookPoint",
    "ProbeSelector",
    "ProbeSelectorMode",
    "ProbeUnavailable",
    "TrainingPipelineStage",
    "TrainingProbe",
    "UnavailableProbeEvidence",
]


class ProbeHookPoint(StrEnum):
    """Hook points for lifecycle-owned probe attachment."""

    SETUP = "setup"
    TEARDOWN = "teardown"
    FAILURE = "failure"
    EPOCH_STARTED = "epoch_started"
    EPOCH_COMPLETED = "epoch_completed"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    DATA_WAIT = "data_wait"
    BATCH_FETCH = "batch_fetch"
    PRE_DEVICE_TRANSFER = "pre_device_transfer"
    POST_DEVICE_TRANSFER = "post_device_transfer"
    FORWARD = "forward"
    OBJECTIVE = "objective"
    BACKWARD = "backward"
    OPTIMIZER_STEP = "optimizer_step"
    SCHEDULER_STEP = "scheduler_step"
    VALIDATION = "validation"
    CHECKPOINT = "checkpoint"
    CALLBACK = "callback"
    PIPELINE_STAGE = "pipeline_stage"

    @classmethod
    def coerce(cls, value: "ProbeHookPoint | str") -> "ProbeHookPoint":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported training probe hook point.",
                    owner="ProbeHookPoint",
                    field="hook_point",
                    expected=tuple(point.value for point in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ProbeHookPoint must be a ProbeHookPoint or string.",
            owner="ProbeHookPoint",
            field="hook_point",
            expected="ProbeHookPoint | str",
            actual=type(value).__name__,
        )


class TrainingPipelineStage(StrEnum):
    """Stage-9-aligned pipeline stage strings for training data flow."""

    INDEXED = "indexed"
    PRE_CACHE_PROCESSING = "pre_cache_processing"
    CACHE_LOOKUP = "cache_lookup"
    CACHE_HIT_LOAD = "cache_hit_load"
    CACHE_MISS_SOURCE_READ = "cache_miss_source_read"
    CACHE_WRITE = "cache_write"
    PREPARED_READ = "prepared_read"
    PRE_AUGMENTATION = "pre_augmentation"
    POST_AUGMENTATION = "post_augmentation"
    POST_PROCESSING = "post_processing"
    COLLATE = "collate"
    PRE_DEVICE_TRANSFER = "pre_device_transfer"
    POST_DEVICE_TRANSFER = "post_device_transfer"
    LEARNER_OUTPUT_VALIDATION = "learner_output_validation"

    @classmethod
    def coerce(cls, value: "TrainingPipelineStage | str") -> "TrainingPipelineStage":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported training pipeline stage.",
                    owner="TrainingPipelineStage",
                    field="pipeline_stage",
                    expected=tuple(stage.value for stage in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "TrainingPipelineStage must be a TrainingPipelineStage or string.",
            owner="TrainingPipelineStage",
            field="pipeline_stage",
            expected="TrainingPipelineStage | str",
            actual=type(value).__name__,
        )


class ProbeAggregation(StrEnum):
    NONE = "none"
    MEAN = "mean"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    SUM = "sum"
    COUNT = "count"

    @classmethod
    def coerce(cls, value: "ProbeAggregation | str") -> "ProbeAggregation":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported probe aggregation.",
                    owner="ProbeAggregation",
                    field="aggregation",
                    expected=tuple(mode.value for mode in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ProbeAggregation must be a ProbeAggregation or string.",
            owner="ProbeAggregation",
            field="aggregation",
            expected="ProbeAggregation | str",
            actual=type(value).__name__,
        )


class ProbeCadenceMode(StrEnum):
    DISABLED = "disabled"
    MANUAL = "manual"
    EVERY_N_STEPS = "every_n_steps"
    EVERY_N_EPOCHS = "every_n_epochs"
    EVERY_N_SECONDS = "every_n_seconds"
    ON_METRIC = "on_metric"
    ON_FAILURE = "on_failure"

    @classmethod
    def coerce(cls, value: "ProbeCadenceMode | str") -> "ProbeCadenceMode":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported probe cadence mode.",
                    owner="ProbeCadenceMode",
                    field="mode",
                    expected=tuple(mode.value for mode in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ProbeCadenceMode must be a ProbeCadenceMode or string.",
            owner="ProbeCadenceMode",
            field="mode",
            expected="ProbeCadenceMode | str",
            actual=type(value).__name__,
        )


class ProbeSelectorMode(StrEnum):
    ALL = "all"
    BY_HOOK = "by_hook"
    BY_STAGE = "by_stage"
    BY_PROBE = "by_probe"
    BY_SPLIT = "by_split"

    @classmethod
    def coerce(cls, value: "ProbeSelectorMode | str") -> "ProbeSelectorMode":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported probe selector mode.",
                    owner="ProbeSelectorMode",
                    field="mode",
                    expected=tuple(mode.value for mode in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ProbeSelectorMode must be a ProbeSelectorMode or string.",
            owner="ProbeSelectorMode",
            field="mode",
            expected="ProbeSelectorMode | str",
            actual=type(value).__name__,
        )


class ProbeFailurePolicy(StrEnum):
    FAIL = "fail"
    RECORD_AND_CONTINUE = "record_and_continue"
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED = "unsupported"

    @classmethod
    def coerce(cls, value: "ProbeFailurePolicy | str") -> "ProbeFailurePolicy":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported probe failure policy.",
                    owner="ProbeFailurePolicy",
                    field="policy",
                    expected=tuple(policy.value for policy in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ProbeFailurePolicy must be a ProbeFailurePolicy or string.",
            owner="ProbeFailurePolicy",
            field="policy",
            expected="ProbeFailurePolicy | str",
            actual=type(value).__name__,
        )


@dataclass(frozen=True, init=False, slots=True)
class ProbeSelector:
    """Probe target selector used by contracts and replay evidence."""

    mode: ProbeSelectorMode
    values: tuple[str, ...]
    strict: bool

    def __init__(
        self,
        mode: ProbeSelectorMode | str,
        values: Sequence[str] | None = None,
        *,
        strict: bool = True,
    ) -> None:
        mode = ProbeSelectorMode.coerce(mode)
        object.__setattr__(self, "mode", mode)
        object.__setattr__(
            self,
            "values",
            _coerce_mode_values(values, owner="ProbeSelector", field="values", mode=mode),
        )
        object.__setattr__(self, "strict", _coerce_bool(strict, owner="ProbeSelector", field="strict"))


@dataclass(frozen=True, init=False, slots=True)
class ProbeCadence:
    """Cadence with optional cadence metadata and metric trigger support."""

    mode: ProbeCadenceMode
    interval: int | float | None
    metric_name: str | None
    metric_direction: str | None
    metric_threshold: float | None

    def __init__(
        self,
        mode: ProbeCadenceMode | str = ProbeCadenceMode.MANUAL,
        *,
        interval: int | float | None = None,
        metric_name: str | None = None,
        metric_direction: str | None = None,
        metric_threshold: float | None = None,
    ) -> None:
        mode = ProbeCadenceMode.coerce(mode)
        object.__setattr__(self, "mode", mode)
        if mode in {ProbeCadenceMode.EVERY_N_STEPS, ProbeCadenceMode.EVERY_N_EPOCHS}:
            if interval is None:
                raise RemotePhysTrainingError(
                    "ProbeCadence interval must be provided for periodic step/epoch cadence.",
                    owner="ProbeCadence",
                    field="interval",
                    mode=mode.value,
                )
            object.__setattr__(
                self,
                "interval",
                coerce_optional_positive_int(interval, owner="ProbeCadence", field="interval"),
            )
        elif mode is ProbeCadenceMode.EVERY_N_SECONDS:
            if interval is None:
                raise RemotePhysTrainingError(
                    "ProbeCadence interval must be provided for time-based cadence.",
                    owner="ProbeCadence",
                    field="interval",
                    mode=mode.value,
                )
            object.__setattr__(
                self,
                "interval",
                _coerce_positive_float(interval, owner="ProbeCadence", field="interval"),
            )
        else:
            if interval is not None:
                raise RemotePhysTrainingError(
                    "ProbeCadence interval is unsupported for this mode.",
                    owner="ProbeCadence",
                    field="interval",
                    mode=mode.value,
                    actual=interval,
                )
            object.__setattr__(self, "interval", None)

        if mode is ProbeCadenceMode.ON_METRIC:
            metric_name = coerce_optional_non_empty_string(
                metric_name,
                owner="ProbeCadence",
                field="metric_name",
            )
            if metric_name is None:
                raise RemotePhysTrainingError(
                    "ProbeCadence metric_name is required for ON_METRIC cadence.",
                    owner="ProbeCadence",
                    field="metric_name",
                    mode=mode.value,
                )
            metric_direction = _coerce_metric_direction(metric_direction, owner="ProbeCadence", field="metric_direction")
            if metric_direction is None:
                raise RemotePhysTrainingError(
                    "ProbeCadence metric_direction is required for ON_METRIC cadence.",
                    owner="ProbeCadence",
                    field="metric_direction",
                    mode=mode.value,
                )
            if metric_threshold is not None:
                metric_threshold = _coerce_finite_float(
                    metric_threshold,
                    owner="ProbeCadence",
                    field="metric_threshold",
                )
            object.__setattr__(self, "metric_threshold", metric_threshold)
            object.__setattr__(self, "metric_direction", metric_direction)
            object.__setattr__(self, "metric_name", metric_name)
        else:
            if metric_name is not None:
                raise RemotePhysTrainingError(
                    "ProbeCadence metric_name is only supported for ON_METRIC mode.",
                    owner="ProbeCadence",
                    field="metric_name",
                    mode=mode.value,
                    actual=metric_name,
                )
            if metric_direction is not None:
                raise RemotePhysTrainingError(
                    "ProbeCadence metric_direction is only supported for ON_METRIC mode.",
                    owner="ProbeCadence",
                    field="metric_direction",
                    mode=mode.value,
                    actual=metric_direction,
                )
            if metric_threshold is not None:
                raise RemotePhysTrainingError(
                    "ProbeCadence metric_threshold is only supported for ON_METRIC mode.",
                    owner="ProbeCadence",
                    field="metric_threshold",
                    mode=mode.value,
                    actual=metric_threshold,
                )
            object.__setattr__(self, "metric_name", None)
            object.__setattr__(self, "metric_direction", None)
            object.__setattr__(self, "metric_threshold", None)


@dataclass(frozen=True, init=False, slots=True)
class UnavailableProbeEvidence:
    """Record that a probe was unavailable or unsupported."""

    probe_id: str
    reason: str
    hook_point: ProbeHookPoint
    pipeline_stage: TrainingPipelineStage | None
    selector: ProbeSelector
    failure_policy: ProbeFailurePolicy
    run_id: str | None
    timeline_id: str | None
    local_rank: int | None
    global_rank: int | None
    process_id: int | None
    node_id: str | None
    device_id: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        probe_id: str,
        *,
        reason: str,
        hook_point: ProbeHookPoint | str,
        pipeline_stage: TrainingPipelineStage | str | None = None,
        selector: ProbeSelector,
        failure_policy: ProbeFailurePolicy | str = ProbeFailurePolicy.UNAVAILABLE,
        run_id: str | None = None,
        timeline_id: str | None = None,
        local_rank: int | None = None,
        global_rank: int | None = None,
        process_id: int | None = None,
        node_id: str | None = None,
        device_id: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(self, "probe_id", _coerce_probe_id(probe_id, owner="UnavailableProbeEvidence", field="probe_id"))
        object.__setattr__(
            self,
            "reason",
            _coerce_name(reason, owner="UnavailableProbeEvidence", field="reason"),
        )
        object.__setattr__(
            self,
            "hook_point",
            ProbeHookPoint.coerce(hook_point),
        )
        object.__setattr__(
            self,
            "pipeline_stage",
            None if pipeline_stage is None else TrainingPipelineStage.coerce(pipeline_stage),
        )
        object.__setattr__(self, "selector", selector)
        object.__setattr__(
            self,
            "failure_policy",
            ProbeFailurePolicy.coerce(failure_policy),
        )
        _coerce_common_context(
            self,
            owner="UnavailableProbeEvidence",
            run_id=run_id,
            timeline_id=timeline_id,
            local_rank=local_rank,
            global_rank=global_rank,
            process_id=process_id,
            node_id=node_id,
            device_id=device_id,
            metadata=metadata,
            provenance=provenance,
        )


@dataclass(frozen=True, init=False, slots=True)
class ProbeUnavailable:
    """Alias maintained for compatibility with existing probe-facing call sites."""

    name: str
    reason: str
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(self, name: str, *, reason: str, metadata: Mapping[object, object] | None = None, provenance: Mapping[object, object] | None = None) -> None:
        object.__setattr__(self, "name", _coerce_name(name, owner="ProbeUnavailable", field="name"))
        object.__setattr__(self, "reason", _coerce_name(reason, owner="ProbeUnavailable", field="reason"))
        object.__setattr__(self, "metadata", freeze_primitive_mapping(metadata, owner="ProbeUnavailable", field="metadata"))
        object.__setattr__(self, "provenance", freeze_primitive_mapping(provenance, owner="ProbeUnavailable", field="provenance"))


@runtime_checkable
class TrainingProbe(Protocol):
    """Protocol for phase-3-independent probe implementations."""

    def collect(self, context: Mapping[object, object]) -> tuple[ModelProbeSummary | DataProbeSummary | UnavailableProbeEvidence, ...]:
        ...


@dataclass(frozen=True, init=False, slots=True)
class ModelProbeSummary:
    """Generic model-inspection summary from one probe run."""

    probe_id: str
    name: str
    hook_point: ProbeHookPoint
    pipeline_stage: TrainingPipelineStage | None
    selector: ProbeSelector
    cadence: ProbeCadence
    aggregation: ProbeAggregation
    failure_policy: ProbeFailurePolicy
    value: PrimitiveValue
    run_id: str | None
    timeline_id: str | None
    epoch_index: int | None
    step_index: int | None
    batch_index: int | None
    split: str | None
    local_rank: int | None
    global_rank: int | None
    process_id: int | None
    node_id: str | None
    device_id: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        probe_id: str,
        name: str,
        *,
        hook_point: ProbeHookPoint | str,
        selector: ProbeSelector,
        cadence: ProbeCadence,
        aggregation: ProbeAggregation | str = ProbeAggregation.NONE,
        failure_policy: ProbeFailurePolicy | str = ProbeFailurePolicy.RECORD_AND_CONTINUE,
        value: PrimitiveValue = None,
        pipeline_stage: TrainingPipelineStage | str | None = None,
        run_id: str | None = None,
        timeline_id: str | None = None,
        epoch_index: int | None = None,
        step_index: int | None = None,
        batch_index: int | None = None,
        split: str | None = None,
        local_rank: int | None = None,
        global_rank: int | None = None,
        process_id: int | None = None,
        node_id: str | None = None,
        device_id: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(self, "probe_id", _coerce_probe_id(probe_id, owner="ModelProbeSummary", field="probe_id"))
        object.__setattr__(self, "name", _coerce_name(name, owner="ModelProbeSummary", field="name"))
        object.__setattr__(self, "hook_point", ProbeHookPoint.coerce(hook_point))
        object.__setattr__(
            self,
            "pipeline_stage",
            None if pipeline_stage is None else TrainingPipelineStage.coerce(pipeline_stage),
        )
        object.__setattr__(self, "selector", selector)
        object.__setattr__(self, "cadence", cadence)
        object.__setattr__(self, "aggregation", ProbeAggregation.coerce(aggregation))
        object.__setattr__(
            self,
            "failure_policy",
            ProbeFailurePolicy.coerce(failure_policy),
        )
        object.__setattr__(self, "value", _coerce_primitive(value, owner="ModelProbeSummary", field="value"))
        object.__setattr__(self, "run_id", coerce_optional_non_empty_string(run_id, owner="ModelProbeSummary", field="run_id"))
        object.__setattr__(self, "timeline_id", coerce_optional_non_empty_string(timeline_id, owner="ModelProbeSummary", field="timeline_id"))
        object.__setattr__(self, "split", coerce_optional_non_empty_string(split, owner="ModelProbeSummary", field="split"))
        object.__setattr__(self, "epoch_index", coerce_non_negative_int(epoch_index, owner="ModelProbeSummary", field="epoch_index") if epoch_index is not None else None)
        object.__setattr__(self, "step_index", coerce_non_negative_int(step_index, owner="ModelProbeSummary", field="step_index") if step_index is not None else None)
        object.__setattr__(self, "batch_index", coerce_non_negative_int(batch_index, owner="ModelProbeSummary", field="batch_index") if batch_index is not None else None)
        object.__setattr__(self, "local_rank", coerce_non_negative_int(local_rank, owner="ModelProbeSummary", field="local_rank") if local_rank is not None else None)
        object.__setattr__(self, "global_rank", coerce_non_negative_int(global_rank, owner="ModelProbeSummary", field="global_rank") if global_rank is not None else None)
        object.__setattr__(self, "process_id", coerce_non_negative_int(process_id, owner="ModelProbeSummary", field="process_id") if process_id is not None else None)
        object.__setattr__(
            self,
            "node_id",
            coerce_optional_non_empty_string(node_id, owner="ModelProbeSummary", field="node_id"),
        )
        object.__setattr__(
            self,
            "device_id",
            coerce_optional_non_empty_string(device_id, owner="ModelProbeSummary", field="device_id"),
        )
        object.__setattr__(self, "metadata", freeze_primitive_mapping(metadata, owner="ModelProbeSummary", field="metadata"))
        object.__setattr__(self, "provenance", freeze_primitive_mapping(provenance, owner="ModelProbeSummary", field="provenance"))


@dataclass(frozen=True, init=False, slots=True)
class ModelParameterProbeSummary:
    """Parameter-level model-probe evidence summary."""

    summary: ModelProbeSummary
    parameter_count: int
    trainable_parameter_count: int | None
    parameter_norm: float | None
    parameter_zero_fraction: float | None
    nonfinite_count: int | None

    def __init__(
        self,
        summary: ModelProbeSummary,
        *,
        parameter_count: int,
        trainable_parameter_count: int | None = None,
        parameter_norm: float | None = None,
        parameter_zero_fraction: float | None = None,
        nonfinite_count: int | None = None,
    ) -> None:
        if not isinstance(summary, ModelProbeSummary):
            raise RemotePhysTrainingError(
                "ModelParameterProbeSummary summary must be a ModelProbeSummary.",
                owner="ModelParameterProbeSummary",
                field="summary",
                expected="ModelProbeSummary",
                actual=type(summary).__name__,
            )
        object.__setattr__(self, "summary", summary)
        object.__setattr__(self, "parameter_count", coerce_non_negative_int(parameter_count, owner="ModelParameterProbeSummary", field="parameter_count"))
        object.__setattr__(
            self,
            "trainable_parameter_count",
            coerce_non_negative_int(trainable_parameter_count, owner="ModelParameterProbeSummary", field="trainable_parameter_count") if trainable_parameter_count is not None else None,
        )
        if parameter_norm is not None:
            parameter_norm = _coerce_finite_float(parameter_norm, owner="ModelParameterProbeSummary", field="parameter_norm")
        object.__setattr__(self, "parameter_norm", parameter_norm)
        if parameter_zero_fraction is not None:
            parameter_zero_fraction = _coerce_ratio(parameter_zero_fraction, owner="ModelParameterProbeSummary", field="parameter_zero_fraction")
        object.__setattr__(self, "parameter_zero_fraction", parameter_zero_fraction)
        if nonfinite_count is not None:
            nonfinite_count = coerce_non_negative_int(nonfinite_count, owner="ModelParameterProbeSummary", field="nonfinite_count")
        object.__setattr__(self, "nonfinite_count", nonfinite_count)


@dataclass(frozen=True, init=False, slots=True)
class ModelGradientProbeSummary:
    """Gradient-level model-probe evidence summary."""

    summary: ModelProbeSummary
    gradient_norm: float | None
    gradient_zero_fraction: float | None
    nan_fraction: float | None
    inf_fraction: float | None
    clipping_ratio: float | None

    def __init__(
        self,
        summary: ModelProbeSummary,
        *,
        gradient_norm: float | None = None,
        gradient_zero_fraction: float | None = None,
        nan_fraction: float | None = None,
        inf_fraction: float | None = None,
        clipping_ratio: float | None = None,
    ) -> None:
        if not isinstance(summary, ModelProbeSummary):
            raise RemotePhysTrainingError(
                "ModelGradientProbeSummary summary must be a ModelProbeSummary.",
                owner="ModelGradientProbeSummary",
                field="summary",
                expected="ModelProbeSummary",
                actual=type(summary).__name__,
            )
        object.__setattr__(self, "summary", summary)
        if gradient_norm is not None:
            gradient_norm = _coerce_finite_float(gradient_norm, owner="ModelGradientProbeSummary", field="gradient_norm")
        object.__setattr__(self, "gradient_norm", gradient_norm)
        if gradient_zero_fraction is not None:
            gradient_zero_fraction = _coerce_ratio(gradient_zero_fraction, owner="ModelGradientProbeSummary", field="gradient_zero_fraction")
        object.__setattr__(self, "gradient_zero_fraction", gradient_zero_fraction)
        if nan_fraction is not None:
            nan_fraction = _coerce_ratio(nan_fraction, owner="ModelGradientProbeSummary", field="nan_fraction")
        object.__setattr__(self, "nan_fraction", nan_fraction)
        if inf_fraction is not None:
            inf_fraction = _coerce_ratio(inf_fraction, owner="ModelGradientProbeSummary", field="inf_fraction")
        object.__setattr__(self, "inf_fraction", inf_fraction)
        if clipping_ratio is not None:
            clipping_ratio = _coerce_ratio(clipping_ratio, owner="ModelGradientProbeSummary", field="clipping_ratio")
        object.__setattr__(self, "clipping_ratio", clipping_ratio)


@dataclass(frozen=True, init=False, slots=True)
class ModelUpdateProbeSummary:
    """Optimizer-update level evidence summary."""

    summary: ModelProbeSummary
    update_norm: float | None
    update_zero_fraction: float | None
    update_clipping_ratio: float | None

    def __init__(
        self,
        summary: ModelProbeSummary,
        *,
        update_norm: float | None = None,
        update_zero_fraction: float | None = None,
        update_clipping_ratio: float | None = None,
    ) -> None:
        if not isinstance(summary, ModelProbeSummary):
            raise RemotePhysTrainingError(
                "ModelUpdateProbeSummary summary must be a ModelProbeSummary.",
                owner="ModelUpdateProbeSummary",
                field="summary",
                expected="ModelProbeSummary",
                actual=type(summary).__name__,
            )
        object.__setattr__(self, "summary", summary)
        if update_norm is not None:
            update_norm = _coerce_finite_float(update_norm, owner="ModelUpdateProbeSummary", field="update_norm")
        object.__setattr__(self, "update_norm", update_norm)
        if update_zero_fraction is not None:
            update_zero_fraction = _coerce_ratio(update_zero_fraction, owner="ModelUpdateProbeSummary", field="update_zero_fraction")
        object.__setattr__(self, "update_zero_fraction", update_zero_fraction)
        if update_clipping_ratio is not None:
            update_clipping_ratio = _coerce_ratio(update_clipping_ratio, owner="ModelUpdateProbeSummary", field="update_clipping_ratio")
        object.__setattr__(self, "update_clipping_ratio", update_clipping_ratio)


@dataclass(frozen=True, init=False, slots=True)
class ModelActivationProbeSummary:
    """Activation probe summary with shape/dtype fingerprints only."""

    summary: ModelProbeSummary
    shape: tuple[int | str, ...]
    dtype: str | None
    min_value: float | None
    max_value: float | None
    mean_value: float | None
    zero_fraction: float | None

    def __init__(
        self,
        summary: ModelProbeSummary,
        *,
        shape: Iterable[int | str] | tuple[int | str, ...],
        dtype: str,
        min_value: float | None = None,
        max_value: float | None = None,
        mean_value: float | None = None,
        zero_fraction: float | None = None,
    ) -> None:
        if not isinstance(summary, ModelProbeSummary):
            raise RemotePhysTrainingError(
                "ModelActivationProbeSummary summary must be a ModelProbeSummary.",
                owner="ModelActivationProbeSummary",
                field="summary",
                expected="ModelProbeSummary",
                actual=type(summary).__name__,
            )
        object.__setattr__(self, "summary", summary)
        object.__setattr__(
            self,
            "shape",
            _coerce_shape(shape, owner="ModelActivationProbeSummary", field="shape"),
        )
        object.__setattr__(
            self,
            "dtype",
            _coerce_name(dtype, owner="ModelActivationProbeSummary", field="dtype"),
        )
        if min_value is not None:
            min_value = _coerce_finite_float(min_value, owner="ModelActivationProbeSummary", field="min_value")
        if max_value is not None:
            max_value = _coerce_finite_float(max_value, owner="ModelActivationProbeSummary", field="max_value")
        if mean_value is not None:
            mean_value = _coerce_finite_float(mean_value, owner="ModelActivationProbeSummary", field="mean_value")
        if zero_fraction is not None:
            zero_fraction = _coerce_ratio(zero_fraction, owner="ModelActivationProbeSummary", field="zero_fraction")
        object.__setattr__(self, "min_value", min_value)
        object.__setattr__(self, "max_value", max_value)
        object.__setattr__(self, "mean_value", mean_value)
        object.__setattr__(self, "zero_fraction", zero_fraction)


@dataclass(frozen=True, init=False, slots=True)
class ModelHealthProbeSummary:
    """NaN/Inf and saturation/clipping health signal summary for model outputs or parameters."""

    summary: ModelProbeSummary
    nonfinite_count: int | None
    nan_fraction: float | None
    inf_fraction: float | None
    zero_fraction: float | None
    saturation_fraction: float | None
    clipping_fraction: float | None

    def __init__(
        self,
        summary: ModelProbeSummary,
        *,
        nonfinite_count: int | None = None,
        nan_fraction: float | None = None,
        inf_fraction: float | None = None,
        zero_fraction: float | None = None,
        saturation_fraction: float | None = None,
        clipping_fraction: float | None = None,
    ) -> None:
        if not isinstance(summary, ModelProbeSummary):
            raise RemotePhysTrainingError(
                "ModelHealthProbeSummary summary must be a ModelProbeSummary.",
                owner="ModelHealthProbeSummary",
                field="summary",
                expected="ModelProbeSummary",
                actual=type(summary).__name__,
            )
        object.__setattr__(self, "summary", summary)
        if nonfinite_count is not None:
            object.__setattr__(self, "nonfinite_count", coerce_non_negative_int(nonfinite_count, owner="ModelHealthProbeSummary", field="nonfinite_count"))
        else:
            object.__setattr__(self, "nonfinite_count", None)
        if nan_fraction is not None:
            nan_fraction = _coerce_ratio(nan_fraction, owner="ModelHealthProbeSummary", field="nan_fraction")
        if inf_fraction is not None:
            inf_fraction = _coerce_ratio(inf_fraction, owner="ModelHealthProbeSummary", field="inf_fraction")
        if zero_fraction is not None:
            zero_fraction = _coerce_ratio(zero_fraction, owner="ModelHealthProbeSummary", field="zero_fraction")
        if saturation_fraction is not None:
            saturation_fraction = _coerce_ratio(saturation_fraction, owner="ModelHealthProbeSummary", field="saturation_fraction")
        if clipping_fraction is not None:
            clipping_fraction = _coerce_ratio(clipping_fraction, owner="ModelHealthProbeSummary", field="clipping_fraction")
        object.__setattr__(self, "nan_fraction", nan_fraction)
        object.__setattr__(self, "inf_fraction", inf_fraction)
        object.__setattr__(self, "zero_fraction", zero_fraction)
        object.__setattr__(self, "saturation_fraction", saturation_fraction)
        object.__setattr__(self, "clipping_fraction", clipping_fraction)


@dataclass(frozen=True, init=False, slots=True)
class DataProbeSummary:
    """Generic data-surface probe summary."""

    probe_id: str
    name: str
    hook_point: ProbeHookPoint
    pipeline_stage: TrainingPipelineStage | None
    selector: ProbeSelector
    cadence: ProbeCadence
    aggregation: ProbeAggregation
    failure_policy: ProbeFailurePolicy
    run_id: str | None
    timeline_id: str | None
    epoch_index: int | None
    step_index: int | None
    batch_index: int | None
    split: str | None
    local_rank: int | None
    global_rank: int | None
    process_id: int | None
    node_id: str | None
    device_id: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        probe_id: str,
        name: str,
        *,
        hook_point: ProbeHookPoint | str,
        selector: ProbeSelector,
        cadence: ProbeCadence,
        aggregation: ProbeAggregation | str = ProbeAggregation.NONE,
        failure_policy: ProbeFailurePolicy | str = ProbeFailurePolicy.RECORD_AND_CONTINUE,
        pipeline_stage: TrainingPipelineStage | str | None = None,
        run_id: str | None = None,
        timeline_id: str | None = None,
        epoch_index: int | None = None,
        step_index: int | None = None,
        batch_index: int | None = None,
        split: str | None = None,
        local_rank: int | None = None,
        global_rank: int | None = None,
        process_id: int | None = None,
        node_id: str | None = None,
        device_id: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(self, "probe_id", _coerce_probe_id(probe_id, owner="DataProbeSummary", field="probe_id"))
        object.__setattr__(self, "name", _coerce_name(name, owner="DataProbeSummary", field="name"))
        object.__setattr__(self, "hook_point", ProbeHookPoint.coerce(hook_point))
        object.__setattr__(
            self,
            "pipeline_stage",
            None if pipeline_stage is None else TrainingPipelineStage.coerce(pipeline_stage),
        )
        object.__setattr__(self, "selector", selector)
        object.__setattr__(self, "cadence", cadence)
        object.__setattr__(self, "aggregation", ProbeAggregation.coerce(aggregation))
        object.__setattr__(self, "failure_policy", ProbeFailurePolicy.coerce(failure_policy))
        object.__setattr__(self, "run_id", coerce_optional_non_empty_string(run_id, owner="DataProbeSummary", field="run_id"))
        object.__setattr__(self, "timeline_id", coerce_optional_non_empty_string(timeline_id, owner="DataProbeSummary", field="timeline_id"))
        object.__setattr__(self, "split", coerce_optional_non_empty_string(split, owner="DataProbeSummary", field="split"))
        object.__setattr__(self, "epoch_index", coerce_non_negative_int(epoch_index, owner="DataProbeSummary", field="epoch_index") if epoch_index is not None else None)
        object.__setattr__(self, "step_index", coerce_non_negative_int(step_index, owner="DataProbeSummary", field="step_index") if step_index is not None else None)
        object.__setattr__(self, "batch_index", coerce_non_negative_int(batch_index, owner="DataProbeSummary", field="batch_index") if batch_index is not None else None)
        object.__setattr__(self, "local_rank", coerce_non_negative_int(local_rank, owner="DataProbeSummary", field="local_rank") if local_rank is not None else None)
        object.__setattr__(self, "global_rank", coerce_non_negative_int(global_rank, owner="DataProbeSummary", field="global_rank") if global_rank is not None else None)
        object.__setattr__(self, "process_id", coerce_non_negative_int(process_id, owner="DataProbeSummary", field="process_id") if process_id is not None else None)
        object.__setattr__(self, "node_id", coerce_optional_non_empty_string(node_id, owner="DataProbeSummary", field="node_id"))
        object.__setattr__(self, "device_id", coerce_optional_non_empty_string(device_id, owner="DataProbeSummary", field="device_id"))
        object.__setattr__(self, "metadata", freeze_primitive_mapping(metadata, owner="DataProbeSummary", field="metadata"))
        object.__setattr__(self, "provenance", freeze_primitive_mapping(provenance, owner="DataProbeSummary", field="provenance"))


@dataclass(frozen=True, init=False, slots=True)
class DataFieldProbeSummary:
    """Per-field batch evidence with shape and type fingerprints."""

    summary: DataProbeSummary
    field: str
    locator: str | None
    present_ratio: float | None
    nan_fraction: float | None
    inf_fraction: float | None
    shape: tuple[int | str, ...]
    dtype: str

    def __init__(
        self,
        summary: DataProbeSummary,
        *,
        field: str,
        shape: Iterable[int | str] | tuple[int | str, ...],
        dtype: str,
        locator: str | None = None,
        present_ratio: float | None = None,
        nan_fraction: float | None = None,
        inf_fraction: float | None = None,
    ) -> None:
        if not isinstance(summary, DataProbeSummary):
            raise RemotePhysTrainingError(
                "DataFieldProbeSummary summary must be a DataProbeSummary.",
                owner="DataFieldProbeSummary",
                field="summary",
                expected="DataProbeSummary",
                actual=type(summary).__name__,
            )
        object.__setattr__(self, "summary", summary)
        object.__setattr__(self, "field", _coerce_name(field, owner="DataFieldProbeSummary", field="field"))
        object.__setattr__(
            self,
            "locator",
            coerce_optional_non_empty_string(locator, owner="DataFieldProbeSummary", field="locator"),
        )
        if present_ratio is not None:
            present_ratio = _coerce_ratio(present_ratio, owner="DataFieldProbeSummary", field="present_ratio")
        if nan_fraction is not None:
            nan_fraction = _coerce_ratio(nan_fraction, owner="DataFieldProbeSummary", field="nan_fraction")
        if inf_fraction is not None:
            inf_fraction = _coerce_ratio(inf_fraction, owner="DataFieldProbeSummary", field="inf_fraction")
        object.__setattr__(self, "present_ratio", present_ratio)
        object.__setattr__(self, "nan_fraction", nan_fraction)
        object.__setattr__(self, "inf_fraction", inf_fraction)
        object.__setattr__(self, "shape", _coerce_shape(shape, owner="DataFieldProbeSummary", field="shape"))
        object.__setattr__(self, "dtype", _coerce_name(dtype, owner="DataFieldProbeSummary", field="dtype"))


@dataclass(frozen=True, init=False, slots=True)
class DataSampleProbeSummary:
    """Aggregate sample/batch provenance summary with simple distribution signals."""

    summary: DataProbeSummary
    batch_size: int | None
    mask_fraction: float | None
    label_coverage: float | None
    zero_fraction: float | None
    mean_value: float | None
    std_value: float | None

    def __init__(
        self,
        summary: DataProbeSummary,
        *,
        batch_size: int | None = None,
        mask_fraction: float | None = None,
        label_coverage: float | None = None,
        zero_fraction: float | None = None,
        mean_value: float | None = None,
        std_value: float | None = None,
    ) -> None:
        if not isinstance(summary, DataProbeSummary):
            raise RemotePhysTrainingError(
                "DataSampleProbeSummary summary must be a DataProbeSummary.",
                owner="DataSampleProbeSummary",
                field="summary",
                expected="DataProbeSummary",
                actual=type(summary).__name__,
            )
        object.__setattr__(self, "summary", summary)
        if batch_size is not None:
            object.__setattr__(self, "batch_size", coerce_non_negative_int(batch_size, owner="DataSampleProbeSummary", field="batch_size"))
        else:
            object.__setattr__(self, "batch_size", None)
        if mask_fraction is not None:
            object.__setattr__(self, "mask_fraction", _coerce_ratio(mask_fraction, owner="DataSampleProbeSummary", field="mask_fraction"))
        else:
            object.__setattr__(self, "mask_fraction", None)
        if label_coverage is not None:
            object.__setattr__(self, "label_coverage", _coerce_ratio(label_coverage, owner="DataSampleProbeSummary", field="label_coverage"))
        else:
            object.__setattr__(self, "label_coverage", None)
        if zero_fraction is not None:
            object.__setattr__(self, "zero_fraction", _coerce_ratio(zero_fraction, owner="DataSampleProbeSummary", field="zero_fraction"))
        else:
            object.__setattr__(self, "zero_fraction", None)
        if mean_value is not None:
            object.__setattr__(self, "mean_value", _coerce_finite_float(mean_value, owner="DataSampleProbeSummary", field="mean_value"))
        else:
            object.__setattr__(self, "mean_value", None)
        if std_value is not None:
            object.__setattr__(self, "std_value", _coerce_finite_float(std_value, owner="DataSampleProbeSummary", field="std_value"))
        else:
            object.__setattr__(self, "std_value", None)


# ---------------------------------------------------------------------------
# Validation helpers


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


def _coerce_probe_id(value: object, *, owner: str, field: str) -> str:
    return _coerce_name(value, owner=owner, field=field)


def _coerce_mode_values(
    values: Sequence[str] | None,
    *,
    owner: str,
    field: str,
    mode: ProbeSelectorMode,
) -> tuple[str, ...]:
    if mode is ProbeSelectorMode.ALL:
        if values is None:
            return ()
        raise RemotePhysTrainingError(
            "ProbeSelector values are not used when mode is all.",
            owner=owner,
            field=field,
            mode=mode.value,
            actual=tuple(values),
        )
    if values is None:
        raise RemotePhysTrainingError(
            "ProbeSelector values are required for this selector mode.",
            owner=owner,
            field=field,
            mode=mode.value,
        )
    if not isinstance(values, Sequence):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a sequence when mode is restrictive.",
            owner=owner,
            field=field,
            expected="sequence[str, ...]",
            actual=type(values).__name__,
        )
    try:
        values = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be iterable when mode is restrictive.",
            owner=owner,
            field=field,
            expected="sequence[str, ...]",
            actual=type(values).__name__,
        ) from exc
    if not values:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be non-empty when mode is restrictive.",
            owner=owner,
            field=field,
            mode=mode.value,
        )
    for index, item in enumerate(values):
        if not isinstance(item, str) or not item:
            raise RemotePhysTrainingError(
                f"{owner} {field} must be non-empty strings when mode is restrictive.",
                owner=owner,
                field=field,
                index=index,
                actual=type(item).__name__,
            )
    return tuple(values)


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


def _coerce_finite_float(value: object, *, owner: str, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a finite number.",
            owner=owner,
            field=field,
            expected="finite number",
            actual=type(value).__name__,
        )
    return float(value)


def _coerce_positive_float(value: object, *, owner: str, field: str) -> float:
    value = _coerce_finite_float(value, owner=owner, field=field)
    if value <= 0:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be positive.",
            owner=owner,
            field=field,
            expected="positive number",
            actual=value,
        )
    return value


def _coerce_ratio(value: object, *, owner: str, field: str) -> float:
    value = _coerce_finite_float(value, owner=owner, field=field)
    if not 0 <= value <= 1:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be in [0, 1].",
            owner=owner,
            field=field,
            expected="0 <= ratio <= 1",
            actual=value,
        )
    return value


def _coerce_metric_direction(value: str | None, *, owner: str, field: str) -> str | None:
    if value is None:
        return None
    if value not in {"min", "max"}:
        raise RemotePhysTrainingError(
            "Probe metric direction must be min or max when metric cadence is used.",
            owner=owner,
            field=field,
            expected="'min' or 'max'",
            actual=value,
        )
    return value


def _coerce_shape(
    values: Iterable[int | str] | tuple[int | str, ...],
    *,
    owner: str,
    field: str,
) -> tuple[int | str, ...]:
    if values is None:
        return ()
    try:
        shape = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be iterable when provided.",
            owner=owner,
            field=field,
            expected="iterable[int | str] | None",
            actual=type(values).__name__,
        ) from exc
    for index, value in enumerate(shape):
        if isinstance(value, bool) or (not isinstance(value, int) and not isinstance(value, str)):
            raise RemotePhysTrainingError(
                f"{owner} {field} values must be non-negative integers or non-empty strings.",
                owner=owner,
                field=field,
                index=index,
                actual=type(value).__name__,
            )
        if isinstance(value, int) and value < 0:
            raise RemotePhysTrainingError(
                f"{owner} {field} values must be non-negative integers or non-empty strings.",
                owner=owner,
                field=field,
                index=index,
                actual=value,
            )
        if isinstance(value, str) and not value:
            raise RemotePhysTrainingError(
                f"{owner} {field} values must be non-empty strings when symbolic.",
                owner=owner,
                field=field,
                index=index,
            )
    return shape


def _coerce_primitive(value: object, *, owner: str, field: str) -> PrimitiveValue:
    if value is not None and not isinstance(value, (str, int, float, bool)):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be primitive when provided.",
            owner=owner,
            field=field,
            expected="str | int | float | bool | None",
            actual=type(value).__name__,
        )
    if isinstance(value, float) and not isfinite(value):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be finite when provided as a float.",
            owner=owner,
            field=field,
            expected="finite primitive float",
            actual=value,
        )
    return value


def _coerce_common_context(
    instance: object,
    *,
    owner: str,
    run_id: str | None,
    timeline_id: str | None,
    local_rank: int | None,
    global_rank: int | None,
    process_id: int | None,
    node_id: str | None,
    device_id: str | None,
    metadata: Mapping[object, object] | None,
    provenance: Mapping[object, object] | None,
) -> None:
    object.__setattr__(
        instance,
        "run_id",
        coerce_optional_non_empty_string(run_id, owner=owner, field="run_id"),
    )
    object.__setattr__(
        instance,
        "timeline_id",
        coerce_optional_non_empty_string(timeline_id, owner=owner, field="timeline_id"),
    )
    object.__setattr__(
        instance,
        "local_rank",
        coerce_non_negative_int(local_rank, owner=owner, field="local_rank") if local_rank is not None else None,
    )
    object.__setattr__(
        instance,
        "global_rank",
        coerce_non_negative_int(global_rank, owner=owner, field="global_rank") if global_rank is not None else None,
    )
    object.__setattr__(
        instance,
        "process_id",
        coerce_non_negative_int(process_id, owner=owner, field="process_id") if process_id is not None else None,
    )
    object.__setattr__(
        instance,
        "node_id",
        coerce_optional_non_empty_string(node_id, owner=owner, field="node_id"),
    )
    object.__setattr__(
        instance,
        "device_id",
        coerce_optional_non_empty_string(device_id, owner=owner, field="device_id"),
    )
    object.__setattr__(
        instance,
        "metadata",
        freeze_primitive_mapping(metadata, owner=owner, field="metadata"),
    )
    object.__setattr__(
        instance,
        "provenance",
        freeze_primitive_mapping(provenance, owner=owner, field="provenance"),
    )


ModelProbeSummary.__hash__ = None  # type: ignore[assignment]
ModelParameterProbeSummary.__hash__ = None  # type: ignore[assignment]
ModelGradientProbeSummary.__hash__ = None  # type: ignore[assignment]
ModelUpdateProbeSummary.__hash__ = None  # type: ignore[assignment]
ModelActivationProbeSummary.__hash__ = None  # type: ignore[assignment]
ModelHealthProbeSummary.__hash__ = None  # type: ignore[assignment]
DataProbeSummary.__hash__ = None  # type: ignore[assignment]
DataFieldProbeSummary.__hash__ = None  # type: ignore[assignment]
DataSampleProbeSummary.__hash__ = None  # type: ignore[assignment]
ProbeCadence.__hash__ = None  # type: ignore[assignment]
ProbeSelector.__hash__ = None  # type: ignore[assignment]
ProbeUnavailable.__hash__ = None  # type: ignore[assignment]
UnavailableProbeEvidence.__hash__ = None  # type: ignore[assignment]
