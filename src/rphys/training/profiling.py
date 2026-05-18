"""Dependency-light training profile records."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
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
    "ResourceMetricKind",
    "ResourceMetricUnit",
    "ResourceSample",
    "ResourceSampleStatus",
    "ResourceSampleBuffer",
    "ResourceSampleBufferState",
    "ResourceTrace",
    "ResourceBufferOverflowPolicy",
    "ResourceMonitorExecutionMode",
    "ResourceMonitorLifecycleEvent",
    "ResourceMonitorLifecycleRecord",
    "ResourceProbe",
    "FakeResourceProbe",
    "FakeCPUResourceProbe",
    "FakeGPUResourceProbe",
    "FakeMemoryResourceProbe",
    "FakeDiskResourceProbe",
    "FakeNetworkResourceProbe",
    "FakeUnavailableResourceProbe",
    "FakeAmbiguousResourceProbe",
    "FakeProbeHealthResourceProbe",
    "ResourceMonitor",
    "ProfileWriterBackend",
    "ProfileWriterResultStatus",
    "ProfileWriterFlushScope",
    "ProfileWriterAppendResult",
    "ProfileWriterFlushResult",
    "InMemoryProfileWriterBackend",
    "AsyncTrainingProfileWriter",
    "TrainingProfile",
    "TrainingProfileRecorder",
    "TrainingProfiler",
    "UnavailableProfileProbe",
]


class ResourceMetricKind(StrEnum):
    """Taxonomy for resource probe signal families."""

    CPU_UTILIZATION = "cpu_utilization"
    CPU_MEMORY_BYTES = "cpu_memory_bytes"
    CPU_MEMORY_PERCENT = "cpu_memory_percent"
    HOST_MEMORY_BYTES = "host_memory_bytes"
    HOST_MEMORY_PERCENT = "host_memory_percent"
    GPU_UTILIZATION = "gpu_utilization"
    GPU_MEMORY_BYTES = "gpu_memory_bytes"
    GPU_MEMORY_PERCENT = "gpu_memory_percent"
    DISK_READ_BYTES_PER_SECOND = "disk_read_bytes_per_second"
    DISK_WRITE_BYTES_PER_SECOND = "disk_write_bytes_per_second"
    DISK_QUEUE_DEPTH = "disk_queue_depth"
    NETWORK_RX_BYTES_PER_SECOND = "network_rx_bytes_per_second"
    NETWORK_TX_BYTES_PER_SECOND = "network_tx_bytes_per_second"
    DATA_LOADER_QUEUE_DEPTH = "data_loader_queue_depth"
    CHECKPOINT_PRESSURE = "checkpoint_pressure"
    LOGGING_PRESSURE = "logging_pressure"
    DATA_TRANSFER = "data_transfer"
    FRAMEWORK_SYNCHRONIZATION = "framework_synchronization"
    COMPILER_ACTIVITY = "compiler_activity"
    PROBE_HEALTH = "probe_health"

    @classmethod
    def coerce(cls, value: "ResourceMetricKind | str") -> "ResourceMetricKind":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported resource metric kind.",
                    owner="ResourceMetricKind",
                    field="metric_kind",
                    expected=tuple(kind.value for kind in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ResourceMetricKind must be ResourceMetricKind or string.",
            owner="ResourceMetricKind",
            field="metric_kind",
            expected="ResourceMetricKind | str",
            actual=type(value).__name__,
        )


class ResourceMetricUnit(StrEnum):
    """Units for primitive resource observation values."""

    BYTES = "bytes"
    BYTES_PER_SECOND = "bytes_per_second"
    COUNT = "count"
    COUNT_PER_SECOND = "count_per_second"
    PERCENT = "percent"
    RATIO = "ratio"
    SECONDS = "seconds"
    DIMENSIONLESS = "dimensionless"

    @classmethod
    def coerce(cls, value: "ResourceMetricUnit | str") -> "ResourceMetricUnit":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported resource metric unit.",
                    owner="ResourceMetricUnit",
                    field="unit",
                    expected=tuple(unit.value for unit in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ResourceMetricUnit must be ResourceMetricUnit or string.",
            owner="ResourceMetricUnit",
            field="unit",
            expected="ResourceMetricUnit | str",
            actual=type(value).__name__,
        )


class ResourceSampleStatus(StrEnum):
    """Status for a single resource sample."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    AMBIGUOUS = "ambiguous"
    DROPPED = "dropped"
    DISABLED = "disabled"

    @classmethod
    def coerce(cls, value: "ResourceSampleStatus | str") -> "ResourceSampleStatus":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported resource sample status.",
                    owner="ResourceSampleStatus",
                    field="status",
                    expected=tuple(status.value for status in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ResourceSampleStatus must be ResourceSampleStatus or string.",
            owner="ResourceSampleStatus",
            field="status",
            expected="ResourceSampleStatus | str",
            actual=type(value).__name__,
        )


class ResourceBufferOverflowPolicy(StrEnum):
    """Queue overflow strategies for bounded resource buffers."""

    DROP_OLDEST = "drop_oldest"
    REJECT_NEW = "reject_new"

    @classmethod
    def coerce(cls, value: "ResourceBufferOverflowPolicy | str") -> "ResourceBufferOverflowPolicy":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported resource buffer overflow policy.",
                    owner="ResourceBufferOverflowPolicy",
                    field="policy",
                    expected=tuple(policy.value for policy in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ResourceBufferOverflowPolicy must be ResourceBufferOverflowPolicy or string.",
            owner="ResourceBufferOverflowPolicy",
            field="policy",
            expected="ResourceBufferOverflowPolicy | str",
            actual=type(value).__name__,
        )


class ResourceMonitorExecutionMode(StrEnum):
    """Execution strategy for a monitor sampler."""

    THREAD = "thread"
    PROCESS = "process"
    INLINE = "inline"

    @classmethod
    def coerce(cls, value: "ResourceMonitorExecutionMode | str") -> "ResourceMonitorExecutionMode":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported resource monitor execution mode.",
                    owner="ResourceMonitorExecutionMode",
                    field="execution_mode",
                    expected=tuple(mode.value for mode in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ResourceMonitorExecutionMode must be ResourceMonitorExecutionMode or string.",
            owner="ResourceMonitorExecutionMode",
            field="execution_mode",
            expected="ResourceMonitorExecutionMode | str",
            actual=type(value).__name__,
        )


class ResourceMonitorLifecycleEvent(StrEnum):
    """Lifecycle events for run-scoped resource monitors."""

    CONFIGURED = "configured"
    STARTED = "started"
    SAMPLE_EMITTED = "sample_emitted"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"
    STOPPED = "stopped"
    FLUSH_REQUESTED = "flush_requested"
    FLUSH_COMPLETED = "flush_completed"
    FLUSH_FAILED = "flush_failed"
    ORPHAN_CLEANUP_ATTEMPTED = "orphan_cleanup_attempted"
    ORPHAN_CLEANUP_COMPLETED = "orphan_cleanup_completed"
    ORPHAN_CLEANUP_FAILED = "orphan_cleanup_failed"
    DISABLED = "disabled"

    @classmethod
    def coerce(cls, value: "ResourceMonitorLifecycleEvent | str") -> "ResourceMonitorLifecycleEvent":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported resource monitor lifecycle event.",
                    owner="ResourceMonitorLifecycleEvent",
                    field="event",
                    expected=tuple(event.value for event in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ResourceMonitorLifecycleEvent must be ResourceMonitorLifecycleEvent or string.",
            owner="ResourceMonitorLifecycleEvent",
            field="event",
            expected="ResourceMonitorLifecycleEvent | str",
            actual=type(value).__name__,
        )


class ProfileWriterFlushScope(StrEnum):
    """Writer flush trigger points."""

    PERIODIC = "periodic"
    STEP = "step"
    EPOCH = "epoch"
    RUN = "run"
    MANUAL = "manual"

    @classmethod
    def coerce(cls, value: "ProfileWriterFlushScope | str") -> "ProfileWriterFlushScope":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported profile writer flush scope.",
                    owner="ProfileWriterFlushScope",
                    field="scope",
                    expected=tuple(scope.value for scope in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ProfileWriterFlushScope must be ProfileWriterFlushScope or string.",
            owner="ProfileWriterFlushScope",
            field="scope",
            expected="ProfileWriterFlushScope | str",
            actual=type(value).__name__,
        )


class ProfileWriterResultStatus(StrEnum):
    """Writer contract states for enqueues and flushes."""

    ENQUEUED = "enqueued"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    DISABLED = "disabled"
    RETRYING = "retrying"

    @classmethod
    def coerce(cls, value: "ProfileWriterResultStatus | str") -> "ProfileWriterResultStatus":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported profile writer result status.",
                    owner="ProfileWriterResultStatus",
                    field="status",
                    expected=tuple(status.value for status in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "ProfileWriterResultStatus must be ProfileWriterResultStatus or string.",
            owner="ProfileWriterResultStatus",
            field="status",
            expected="ProfileWriterResultStatus | str",
            actual=type(value).__name__,
        )


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
class ResourceSample:
    """Immutable timestamped primitive resource observations."""

    metric_kind: ResourceMetricKind
    metric_name: str
    series_key: str | None
    unit: ResourceMetricUnit
    status: ResourceSampleStatus
    value: float | None
    timestamp: float
    sequence_id: int
    sample_interval_seconds: float | None
    reason: str | None
    run_id: str | None
    timeline_id: str | None
    clock_name: str | None
    clock_origin: str | None
    clock_alignment: str | None
    process_id: int | None
    node_id: str | None
    local_rank: int | None
    global_rank: int | None
    device_id: str | None
    source_probe_id: str
    resource_id: str | None
    overhead_seconds: float | None
    synchronization: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        metric_kind: ResourceMetricKind | str,
        metric_name: str,
        unit: ResourceMetricUnit | str,
        value: float | None,
        *,
        status: ResourceSampleStatus | str = ResourceSampleStatus.AVAILABLE,
        timestamp: float | int | None = None,
        sequence_id: int = 0,
        sample_interval_seconds: float | int | None = None,
        reason: str | None = None,
        series_key: str | None = None,
        run_id: str | None = None,
        timeline_id: str | None = None,
        clock_name: str | None = None,
        clock_origin: str | None = None,
        clock_alignment: str | None = None,
        process_id: int | None = None,
        node_id: str | None = None,
        local_rank: int | None = None,
        global_rank: int | None = None,
        device_id: str | None = None,
        source_probe_id: str | None = None,
        resource_id: str | None = None,
        overhead_seconds: float | None = None,
        synchronization: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "metric_kind",
            ResourceMetricKind.coerce(metric_kind),
        )
        object.__setattr__(
            self,
            "metric_name",
            _coerce_name(metric_name, owner="ResourceSample", field="metric_name"),
        )
        object.__setattr__(
            self,
            "series_key",
            coerce_optional_non_empty_string(
                series_key,
                owner="ResourceSample",
                field="series_key",
            ),
        )
        object.__setattr__(
            self,
            "unit",
            ResourceMetricUnit.coerce(unit),
        )
        status = ResourceSampleStatus.coerce(status)
        object.__setattr__(self, "status", status)
        object.__setattr__(
            self,
            "value",
            _coerce_resource_sample_value(value, status=status, owner="ResourceSample", field="value"),
        )
        if status is ResourceSampleStatus.AVAILABLE and value is None:
            raise RemotePhysTrainingError(
                "ResourceSample available status requires a finite non-negative value.",
                owner="ResourceSample",
                field="value",
                expected="finite non-negative number",
                actual="None",
            )
        if status is not ResourceSampleStatus.AVAILABLE and value is not None:
            raise RemotePhysTrainingError(
                "ResourceSample unavailable-like statuses must not include a value.",
                owner="ResourceSample",
                field="value",
                expected="None when status is not available",
                actual="number",
            )
        object.__setattr__(
            self,
            "timestamp",
            _coerce_non_negative_timestamp(timestamp, owner="ResourceSample", field="timestamp"),
        )
        object.__setattr__(self, "sequence_id", coerce_non_negative_int(sequence_id, owner="ResourceSample", field="sequence_id"))
        object.__setattr__(
            self,
            "sample_interval_seconds",
            _coerce_optional_positive_or_zero_duration(
                sample_interval_seconds,
                owner="ResourceSample",
                field="sample_interval_seconds",
            ),
        )
        if status is not ResourceSampleStatus.AVAILABLE:
            if reason is None:
                raise RemotePhysTrainingError(
                    "ResourceSample unavailable-like status requires a non-empty reason.",
                    owner="ResourceSample",
                    field="reason",
                    expected="non-empty string",
                    actual="None",
                )
        object.__setattr__(
            self,
            "reason",
            coerce_optional_non_empty_string(reason, owner="ResourceSample", field="reason"),
        )
        object.__setattr__(
            self,
            "run_id",
            coerce_optional_non_empty_string(run_id, owner="ResourceSample", field="run_id"),
        )
        object.__setattr__(
            self,
            "timeline_id",
            coerce_optional_non_empty_string(timeline_id, owner="ResourceSample", field="timeline_id"),
        )
        object.__setattr__(
            self,
            "clock_name",
            coerce_optional_non_empty_string(clock_name, owner="ResourceSample", field="clock_name"),
        )
        object.__setattr__(
            self,
            "clock_origin",
            coerce_optional_non_empty_string(clock_origin, owner="ResourceSample", field="clock_origin"),
        )
        object.__setattr__(
            self,
            "clock_alignment",
            coerce_optional_non_empty_string(
                clock_alignment,
                owner="ResourceSample",
                field="clock_alignment",
            ),
        )
        object.__setattr__(
            self,
            "process_id",
            _coerce_optional_non_negative_int(process_id, owner="ResourceSample", field="process_id"),
        )
        object.__setattr__(
            self,
            "node_id",
            coerce_optional_non_empty_string(node_id, owner="ResourceSample", field="node_id"),
        )
        object.__setattr__(
            self,
            "local_rank",
            _coerce_optional_non_negative_int(local_rank, owner="ResourceSample", field="local_rank"),
        )
        object.__setattr__(
            self,
            "global_rank",
            _coerce_optional_non_negative_int(global_rank, owner="ResourceSample", field="global_rank"),
        )
        object.__setattr__(
            self,
            "device_id",
            coerce_optional_non_empty_string(device_id, owner="ResourceSample", field="device_id"),
        )
        object.__setattr__(
            self,
            "source_probe_id",
            _coerce_name(
                source_probe_id or "",
                owner="ResourceSample",
                field="source_probe_id",
            ),
        )
        object.__setattr__(
            self,
            "resource_id",
            coerce_optional_non_empty_string(resource_id, owner="ResourceSample", field="resource_id"),
        )
        object.__setattr__(
            self,
            "overhead_seconds",
            _coerce_optional_duration(overhead_seconds, owner="ResourceSample", field="overhead_seconds"),
        )
        object.__setattr__(
            self,
            "synchronization",
            coerce_optional_non_empty_string(synchronization, owner="ResourceSample", field="synchronization"),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(metadata, owner="ResourceSample", field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(provenance, owner="ResourceSample", field="provenance"),
        )


@dataclass(frozen=True, init=False, slots=True)
class ResourceTrace:
    """Ordered resource samples for a single logical series."""

    metric_kind: ResourceMetricKind
    metric_name: str
    series_key: str | None
    unit: ResourceMetricUnit
    source_probe_id: str
    samples: tuple[ResourceSample, ...]
    run_id: str | None
    timeline_id: str | None
    clock_name: str | None
    clock_origin: str | None
    process_id: int | None
    node_id: str | None
    local_rank: int | None
    global_rank: int | None
    device_id: str | None
    resource_id: str | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        metric_kind: ResourceMetricKind | str,
        metric_name: str,
        unit: ResourceMetricUnit | str,
        source_probe_id: str,
        samples: Iterable[ResourceSample] = (),
        *,
        series_key: str | None = None,
        run_id: str | None = None,
        timeline_id: str | None = None,
        clock_name: str | None = None,
        clock_origin: str | None = None,
        process_id: int | None = None,
        node_id: str | None = None,
        local_rank: int | None = None,
        global_rank: int | None = None,
        device_id: str | None = None,
        resource_id: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "metric_kind",
            ResourceMetricKind.coerce(metric_kind),
        )
        object.__setattr__(
            self,
            "metric_name",
            _coerce_name(metric_name, owner="ResourceTrace", field="metric_name"),
        )
        object.__setattr__(
            self,
            "series_key",
            coerce_optional_non_empty_string(series_key, owner="ResourceTrace", field="series_key"),
        )
        object.__setattr__(self, "unit", ResourceMetricUnit.coerce(unit))
        object.__setattr__(
            self,
            "source_probe_id",
            _coerce_name(source_probe_id, owner="ResourceTrace", field="source_probe_id"),
        )
        samples_tuple = _coerce_records(samples, ResourceSample, owner="ResourceTrace", field="samples")
        self._validate_samples(samples_tuple)
        object.__setattr__(self, "samples", samples_tuple)
        object.__setattr__(
            self,
            "run_id",
            _coerce_resource_scope_string(run_id, self._coerce_samples_value(samples_tuple, "run_id"), owner="ResourceTrace", field="run_id"),
        )
        object.__setattr__(
            self,
            "timeline_id",
            _coerce_resource_scope_string(timeline_id, self._coerce_samples_value(samples_tuple, "timeline_id"), owner="ResourceTrace", field="timeline_id"),
        )
        object.__setattr__(
            self,
            "clock_name",
            coerce_optional_non_empty_string(clock_name, owner="ResourceTrace", field="clock_name"),
        )
        object.__setattr__(
            self,
            "clock_origin",
            coerce_optional_non_empty_string(clock_origin, owner="ResourceTrace", field="clock_origin"),
        )
        object.__setattr__(
            self,
            "process_id",
            _coerce_optional_non_negative_int(process_id, owner="ResourceTrace", field="process_id"),
        )
        object.__setattr__(
            self,
            "node_id",
            coerce_optional_non_empty_string(node_id, owner="ResourceTrace", field="node_id"),
        )
        object.__setattr__(
            self,
            "local_rank",
            _coerce_optional_non_negative_int(local_rank, owner="ResourceTrace", field="local_rank"),
        )
        object.__setattr__(
            self,
            "global_rank",
            _coerce_optional_non_negative_int(global_rank, owner="ResourceTrace", field="global_rank"),
        )
        object.__setattr__(
            self,
            "device_id",
            coerce_optional_non_empty_string(device_id, owner="ResourceTrace", field="device_id"),
        )
        object.__setattr__(
            self,
            "resource_id",
            coerce_optional_non_empty_string(resource_id, owner="ResourceTrace", field="resource_id"),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(metadata, owner="ResourceTrace", field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(provenance, owner="ResourceTrace", field="provenance"),
        )

    @staticmethod
    def _coerce_samples_value(samples: tuple[ResourceSample, ...], field: str) -> str | None:
        if not samples:
            return None
        values = {getattr(sample, field) for sample in samples}
        if len(values) == 1:
            return next(iter(values))
        if all(value is not None for value in values):
            raise RemotePhysTrainingError(
                "ResourceTrace samples must share one trace-level attribution value.",
                owner="ResourceTrace",
                field=field,
                expected="single value",
            )
        return None

    def _validate_samples(self, samples: tuple[ResourceSample, ...]) -> None:
        previous: ResourceSample | None = None
        for sample in samples:
            if sample.metric_kind is not self.metric_kind:
                raise RemotePhysTrainingError(
                    "ResourceTrace metric_kind must match sample metric kind.",
                    owner="ResourceTrace",
                    field="samples",
                    expected=self.metric_kind.value,
                    actual=sample.metric_kind.value,
                )
            if sample.metric_name != self.metric_name:
                raise RemotePhysTrainingError(
                    "ResourceTrace metric_name must match sample metric name.",
                    owner="ResourceTrace",
                    field="samples",
                    expected=self.metric_name,
                    actual=sample.metric_name,
                )
            if sample.series_key is not None:
                if self.series_key is not None and sample.series_key != self.series_key:
                    raise RemotePhysTrainingError(
                        "ResourceTrace series_key must match sample series_key.",
                        owner="ResourceTrace",
                        field="samples",
                        expected=self.series_key,
                        actual=sample.series_key,
                    )
            if sample.unit != self.unit:
                raise RemotePhysTrainingError(
                    "ResourceTrace unit must match sample unit.",
                    owner="ResourceTrace",
                    field="samples",
                    expected=self.unit.value,
                    actual=sample.unit.value,
                )
            if sample.source_probe_id != self.source_probe_id:
                raise RemotePhysTrainingError(
                    "ResourceTrace source_probe_id must match sample source_probe_id.",
                    owner="ResourceTrace",
                    field="samples",
                    expected=self.source_probe_id,
                    actual=sample.source_probe_id,
                )
            if previous is not None:
                if sample.sequence_id <= previous.sequence_id:
                    raise RemotePhysTrainingError(
                        "ResourceTrace sample sequence_id must be strictly increasing.",
                        owner="ResourceTrace",
                        field="samples",
                        expected="strictly increasing sequence_id",
                        previous=previous.sequence_id,
                        current=sample.sequence_id,
                    )
                if sample.timestamp < previous.timestamp:
                    raise RemotePhysTrainingError(
                        "ResourceTrace sample timestamp must be non-decreasing.",
                        owner="ResourceTrace",
                        field="samples",
                        expected="non-decreasing timestamp",
                        previous=previous.timestamp,
                        current=sample.timestamp,
                    )
            previous = sample

    def append(self, sample: ResourceSample) -> "ResourceTrace":
        """Return a new trace with `sample` appended."""

        if not isinstance(sample, ResourceSample):
            raise RemotePhysTrainingError(
                "ResourceTrace.append expects a ResourceSample.",
                owner="ResourceTrace",
                field="sample",
                expected="ResourceSample",
                actual=type(sample).__name__,
            )
        return ResourceTrace(
            self.metric_kind,
            metric_name=self.metric_name,
            unit=self.unit,
            source_probe_id=self.source_probe_id,
            samples=self.samples + (sample,),
            series_key=self.series_key,
            run_id=self.run_id,
            timeline_id=self.timeline_id,
            clock_name=self.clock_name,
            clock_origin=self.clock_origin,
            process_id=self.process_id,
            node_id=self.node_id,
            local_rank=self.local_rank,
            global_rank=self.global_rank,
            device_id=self.device_id,
            resource_id=self.resource_id,
            metadata=self.metadata,
            provenance=self.provenance,
        )


@dataclass(frozen=True, init=False, slots=True)
class ResourceSampleBufferState:
    """Evidence record for bounded buffer behavior."""

    capacity: int
    overflow_policy: ResourceBufferOverflowPolicy
    queue_depth: int
    accepted_count: int
    dropped_count: int

    def __init__(
        self,
        *,
        capacity: int,
        overflow_policy: ResourceBufferOverflowPolicy | str,
        queue_depth: int,
        accepted_count: int,
        dropped_count: int,
    ) -> None:
        object.__setattr__(
            self,
            "capacity",
            coerce_non_negative_int(capacity, owner="ResourceSampleBufferState", field="capacity"),
        )
        object.__setattr__(
            self,
            "overflow_policy",
            ResourceBufferOverflowPolicy.coerce(overflow_policy),
        )
        object.__setattr__(
            self,
            "queue_depth",
            coerce_non_negative_int(queue_depth, owner="ResourceSampleBufferState", field="queue_depth"),
        )
        object.__setattr__(
            self,
            "accepted_count",
            coerce_non_negative_int(accepted_count, owner="ResourceSampleBufferState", field="accepted_count"),
        )
        object.__setattr__(
            self,
            "dropped_count",
            coerce_non_negative_int(dropped_count, owner="ResourceSampleBufferState", field="dropped_count"),
        )


class ResourceSampleBuffer:
    """Small bounded queue used by monitor and writer contracts."""

    def __init__(
        self,
        *,
        capacity: int = 128,
        overflow_policy: ResourceBufferOverflowPolicy | str = ResourceBufferOverflowPolicy.DROP_OLDEST,
    ) -> None:
        self._capacity = coerce_non_negative_int(capacity, owner="ResourceSampleBuffer", field="capacity")
        if self._capacity <= 0:
            raise RemotePhysTrainingError(
                "ResourceSampleBuffer capacity must be a positive integer.",
                owner="ResourceSampleBuffer",
                field="capacity",
                expected="positive integer",
                actual=capacity,
            )
        self._overflow_policy = ResourceBufferOverflowPolicy.coerce(overflow_policy)
        self._queue: deque[object] = deque()
        self._accepted_count = 0
        self._dropped_count = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def overflow_policy(self) -> ResourceBufferOverflowPolicy:
        return self._overflow_policy

    @property
    def queue_depth(self) -> int:
        return len(self._queue)

    @property
    def accepted_count(self) -> int:
        return self._accepted_count

    @property
    def dropped_count(self) -> int:
        return self._dropped_count

    def push(self, sample: object) -> ResourceSampleBufferState:
        if len(self._queue) >= self._capacity:
            if self._overflow_policy is ResourceBufferOverflowPolicy.DROP_OLDEST:
                self._queue.popleft()
                self._dropped_count += 1
                self._queue.append(sample)
                self._accepted_count += 1
            else:
                self._dropped_count += 1
        else:
            self._queue.append(sample)
            self._accepted_count += 1

        return self.snapshot()

    def clear(self) -> None:
        self._queue.clear()

    def pop(self, count: int | None = None) -> tuple[object, ...]:
        if count is None:
            values = tuple(self._queue)
            self._queue.clear()
            return values

        coerce_non_negative_int(count, owner="ResourceSampleBuffer", field="count")
        values: list[object] = []
        for _ in range(min(count, len(self._queue))):
            values.append(self._queue.popleft())
        return tuple(values)

    def items(self) -> tuple[object, ...]:
        return tuple(self._queue)

    def snapshot(self) -> ResourceSampleBufferState:
        return ResourceSampleBufferState(
            capacity=self._capacity,
            overflow_policy=self._overflow_policy,
            queue_depth=len(self._queue),
            accepted_count=self._accepted_count,
            dropped_count=self._dropped_count,
        )


@dataclass(frozen=True, init=False, slots=True)
class ResourceMonitorLifecycleRecord:
    """Evidence for monitor lifecycle and buffering behavior."""

    event: ResourceMonitorLifecycleEvent
    sequence_id: int
    probe_id: str
    timestamp: float
    reason: str | None
    run_id: str | None
    timeline_id: str | None
    clock_name: str | None
    clock_origin: str | None
    process_id: int | None
    node_id: str | None
    local_rank: int | None
    global_rank: int | None
    device_id: str | None
    resource_id: str | None
    buffer_state: ResourceSampleBufferState | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        event: ResourceMonitorLifecycleEvent | str,
        sequence_id: int,
        *,
        probe_id: str,
        timestamp: float | int,
        reason: str | None = None,
        run_id: str | None = None,
        timeline_id: str | None = None,
        clock_name: str | None = None,
        clock_origin: str | None = None,
        process_id: int | None = None,
        node_id: str | None = None,
        local_rank: int | None = None,
        global_rank: int | None = None,
        device_id: str | None = None,
        resource_id: str | None = None,
        buffer_state: ResourceSampleBufferState | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "event",
            ResourceMonitorLifecycleEvent.coerce(event),
        )
        object.__setattr__(
            self,
            "sequence_id",
            coerce_non_negative_int(sequence_id, owner="ResourceMonitorLifecycleRecord", field="sequence_id"),
        )
        object.__setattr__(
            self,
            "probe_id",
            _coerce_name(probe_id, owner="ResourceMonitorLifecycleRecord", field="probe_id"),
        )
        object.__setattr__(
            self,
            "timestamp",
            _coerce_non_negative_timestamp(timestamp, owner="ResourceMonitorLifecycleRecord", field="timestamp"),
        )
        object.__setattr__(
            self,
            "reason",
            coerce_optional_non_empty_string(reason, owner="ResourceMonitorLifecycleRecord", field="reason"),
        )
        object.__setattr__(
            self,
            "run_id",
            coerce_optional_non_empty_string(run_id, owner="ResourceMonitorLifecycleRecord", field="run_id"),
        )
        object.__setattr__(
            self,
            "timeline_id",
            coerce_optional_non_empty_string(timeline_id, owner="ResourceMonitorLifecycleRecord", field="timeline_id"),
        )
        object.__setattr__(
            self,
            "clock_name",
            coerce_optional_non_empty_string(clock_name, owner="ResourceMonitorLifecycleRecord", field="clock_name"),
        )
        object.__setattr__(
            self,
            "clock_origin",
            coerce_optional_non_empty_string(clock_origin, owner="ResourceMonitorLifecycleRecord", field="clock_origin"),
        )
        object.__setattr__(
            self,
            "process_id",
            _coerce_optional_non_negative_int(process_id, owner="ResourceMonitorLifecycleRecord", field="process_id"),
        )
        object.__setattr__(
            self,
            "node_id",
            coerce_optional_non_empty_string(node_id, owner="ResourceMonitorLifecycleRecord", field="node_id"),
        )
        object.__setattr__(
            self,
            "local_rank",
            _coerce_optional_non_negative_int(local_rank, owner="ResourceMonitorLifecycleRecord", field="local_rank"),
        )
        object.__setattr__(
            self,
            "global_rank",
            _coerce_optional_non_negative_int(global_rank, owner="ResourceMonitorLifecycleRecord", field="global_rank"),
        )
        object.__setattr__(
            self,
            "device_id",
            coerce_optional_non_empty_string(device_id, owner="ResourceMonitorLifecycleRecord", field="device_id"),
        )
        object.__setattr__(
            self,
            "resource_id",
            coerce_optional_non_empty_string(resource_id, owner="ResourceMonitorLifecycleRecord", field="resource_id"),
        )
        object.__setattr__(
            self,
            "buffer_state",
            None if buffer_state is None else buffer_state,
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(metadata, owner="ResourceMonitorLifecycleRecord", field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(provenance, owner="ResourceMonitorLifecycleRecord", field="provenance"),
        )


@runtime_checkable
class ResourceProbe(Protocol):
    """Contract for deterministic resource probes."""

    probe_id: str
    metric_kind: ResourceMetricKind | str
    metric_name: str
    unit: ResourceMetricUnit | str
    series_key: str | None

    def sample(
        self,
        *,
        timestamp: float,
        sequence_id: int,
        run_id: str | None,
        timeline_id: str | None,
        clock_name: str | None = None,
        clock_origin: str | None = None,
        process_id: int | None = None,
        node_id: str | None = None,
        local_rank: int | None = None,
        global_rank: int | None = None,
        device_id: str | None = None,
        source_probe_id: str | None = None,
        resource_id: str | None = None,
    ) -> ResourceSample:
        ...


class FakeResourceProbe:
    """Deterministic CPU-only probe helper."""

    def __init__(
        self,
        metric_kind: ResourceMetricKind | str,
        metric_name: str,
        values: Sequence[float | None],
        *,
        unit: ResourceMetricUnit | str,
        statuses: Sequence[ResourceSampleStatus | str] | None = None,
        probe_id: str | None = None,
        source_probe_id: str | None = None,
        series_key: str | None = None,
        reason_by_status: Mapping[ResourceSampleStatus | str, str] | None = None,
        resource_id: str | None = None,
    ) -> None:
        values_tuple = tuple(values)
        if not values_tuple:
            raise RemotePhysTrainingError(
                "FakeResourceProbe values must be non-empty.",
                owner="FakeResourceProbe",
                field="values",
                expected="non-empty sequence",
                actual="empty sequence",
            )
        status_values = tuple(
            status if isinstance(status, ResourceSampleStatus) else ResourceSampleStatus.coerce(status)
            for status in (statuses if statuses is not None else (ResourceSampleStatus.AVAILABLE,) * len(values_tuple))
        )
        if len(status_values) == 0:
            status_values = (ResourceSampleStatus.AVAILABLE,)
        if len(status_values) != len(values_tuple):
            repeat_statuses = len(values_tuple) // len(status_values)
            remainder = len(values_tuple) % len(status_values)
            status_values = status_values * repeat_statuses + status_values[:remainder]
            if len(status_values) != len(values_tuple):
                status_values = tuple(status_values[: len(values_tuple)])

        self.metric_kind = ResourceMetricKind.coerce(metric_kind)
        self.metric_name = _coerce_name(metric_name, owner="FakeResourceProbe", field="metric_name")
        self.unit = ResourceMetricUnit.coerce(unit)
        self.values = values_tuple
        self.statuses = status_values
        self.probe_id = _coerce_name(
            probe_id or f"fake-{self.metric_kind.value}",
            owner="FakeResourceProbe",
            field="probe_id",
        )
        self.source_probe_id = source_probe_id or self.probe_id
        self.series_key = coerce_optional_non_empty_string(series_key, owner="FakeResourceProbe", field="series_key")
        self.resource_id = coerce_optional_non_empty_string(resource_id, owner="FakeResourceProbe", field="resource_id")
        self.reason_by_status = {
            ResourceSampleStatus.coerce(key): value
            for key, value in (reason_by_status or {}).items()
        }
        self._index = 0

    def sample(
        self,
        *,
        timestamp: float,
        sequence_id: int,
        run_id: str | None,
        timeline_id: str | None,
        clock_name: str | None = None,
        clock_origin: str | None = None,
        process_id: int | None = None,
        node_id: str | None = None,
        local_rank: int | None = None,
        global_rank: int | None = None,
        device_id: str | None = None,
        source_probe_id: str | None = None,
        resource_id: str | None = None,
    ) -> ResourceSample:
        values_index = self._index % len(self.values)
        status_index = self._index % len(self.statuses)
        self._index += 1
        status = self.statuses[status_index]
        raw_value = self.values[values_index]
        reason = self.reason_by_status.get(status)
        return ResourceSample(
            self.metric_kind,
            metric_name=self.metric_name,
            unit=self.unit,
            value=None if status is not ResourceSampleStatus.AVAILABLE else raw_value,
            status=status,
            timestamp=timestamp,
            sequence_id=sequence_id,
            reason=reason,
            run_id=run_id,
            timeline_id=timeline_id,
            clock_name=clock_name,
            clock_origin=clock_origin,
            process_id=process_id,
            node_id=node_id,
            local_rank=local_rank,
            global_rank=global_rank,
            device_id=device_id,
            source_probe_id=source_probe_id or self.source_probe_id,
            resource_id=resource_id or self.resource_id,
            series_key=self.series_key,
            metadata={"probe_id": self.probe_id},
            provenance={"probe": self.probe_id},
        )


class FakeCPUResourceProbe(FakeResourceProbe):
    """CPU utilization probe."""

    def __init__(
        self,
        *,
        probe_id: str = "fake-cpu",
        values: Sequence[float] = (12.5, 20.0, 30.0),
        series_key: str = "cpu",
    ) -> None:
        super().__init__(
            ResourceMetricKind.CPU_UTILIZATION,
            metric_name="cpu_utilization",
            values=values,
            unit=ResourceMetricUnit.PERCENT,
            probe_id=probe_id,
            series_key=series_key,
        )


class FakeMemoryResourceProbe(FakeResourceProbe):
    """Host/GPU memory pressure helper with percent values."""

    def __init__(
        self,
        *,
        probe_id: str = "fake-memory",
        values: Sequence[float] = (1.5e8, 1.55e8, 1.6e8),
        metric_kind: ResourceMetricKind = ResourceMetricKind.HOST_MEMORY_BYTES,
        unit: ResourceMetricUnit = ResourceMetricUnit.BYTES,
        series_key: str = "memory",
    ) -> None:
        metric_name = "host_memory_bytes" if metric_kind is ResourceMetricKind.HOST_MEMORY_BYTES else "gpu_memory_bytes"
        super().__init__(
            metric_kind,
            metric_name=metric_name,
            values=values,
            unit=unit,
            probe_id=probe_id,
            series_key=series_key,
        )


class FakeGPUResourceProbe(FakeResourceProbe):
    """GPU utilization probe."""

    def __init__(
        self,
        *,
        probe_id: str = "fake-gpu",
        values: Sequence[float] = (15.0, 25.0, 35.0),
        series_key: str = "gpu",
    ) -> None:
        super().__init__(
            ResourceMetricKind.GPU_UTILIZATION,
            metric_name="gpu_utilization",
            values=values,
            unit=ResourceMetricUnit.PERCENT,
            probe_id=probe_id,
            series_key=series_key,
        )


class FakeDiskResourceProbe(FakeResourceProbe):
    """Disk I/O throughput probe."""

    def __init__(
        self,
        *,
        probe_id: str = "fake-disk",
        values: Sequence[float] = (1024.0, 2048.0, 4096.0),
        series_key: str = "disk",
    ) -> None:
        super().__init__(
            ResourceMetricKind.DISK_READ_BYTES_PER_SECOND,
            metric_name="disk_read_bytes_per_second",
            values=values,
            unit=ResourceMetricUnit.BYTES_PER_SECOND,
            probe_id=probe_id,
            series_key=series_key,
        )


class FakeNetworkResourceProbe(FakeResourceProbe):
    """Network throughput probe."""

    def __init__(
        self,
        *,
        probe_id: str = "fake-network",
        values: Sequence[float] = (150.0, 250.0, 350.0),
        series_key: str = "network",
    ) -> None:
        super().__init__(
            ResourceMetricKind.NETWORK_RX_BYTES_PER_SECOND,
            metric_name="network_rx_bytes_per_second",
            values=values,
            unit=ResourceMetricUnit.BYTES_PER_SECOND,
            probe_id=probe_id,
            series_key=series_key,
        )


class FakeUnavailableResourceProbe(FakeResourceProbe):
    """Always-UNAVAILABLE deterministic probe."""

    def __init__(
        self,
        *,
        probe_id: str = "fake-unavailable",
        metric_kind: ResourceMetricKind = ResourceMetricKind.GPU_UTILIZATION,
        metric_name: str = "gpu_utilization",
        reason: str = "dependency_missing",
    ) -> None:
        super().__init__(
            metric_kind,
            metric_name=metric_name,
            values=(None,),
            statuses=(ResourceSampleStatus.UNAVAILABLE,),
            unit=ResourceMetricUnit.PERCENT,
            probe_id=probe_id,
            reason_by_status={ResourceSampleStatus.UNAVAILABLE: reason},
        )


class FakeAmbiguousResourceProbe(FakeResourceProbe):
    """Ambiguous attribution deterministic probe."""

    def __init__(
        self,
        *,
        probe_id: str = "fake-ambiguous",
        metric_kind: ResourceMetricKind = ResourceMetricKind.DATA_LOADER_QUEUE_DEPTH,
        metric_name: str = "data_loader_queue_depth",
        reason: str = "multiple_devices",
    ) -> None:
        super().__init__(
            metric_kind,
            metric_name=metric_name,
            values=(None,),
            statuses=(ResourceSampleStatus.AMBIGUOUS,),
            unit=ResourceMetricUnit.COUNT,
            probe_id=probe_id,
            reason_by_status={ResourceSampleStatus.AMBIGUOUS: reason},
        )


class FakeProbeHealthResourceProbe(FakeResourceProbe):
    """Synthetic probe health check sample."""

    def __init__(
        self,
        *,
        probe_id: str = "fake-probe-health",
        values: Sequence[float] = (1.0, 1.0, 0.0),
    ) -> None:
        super().__init__(
            ResourceMetricKind.PROBE_HEALTH,
            metric_name="probe_health",
            values=values,
            unit=ResourceMetricUnit.RATIO,
            probe_id=probe_id,
            series_key="probe-health",
        )


class ResourceMonitor:
    """Dependency-light monitor lifecycle helper."""

    def __init__(
        self,
        probe: ResourceProbe,
        *,
        execution_mode: ResourceMonitorExecutionMode | str = ResourceMonitorExecutionMode.THREAD,
        enabled: bool = True,
        buffer_capacity: int = 64,
        buffer_overflow_policy: ResourceBufferOverflowPolicy | str = ResourceBufferOverflowPolicy.DROP_OLDEST,
        clock: Callable[[], float] | None = None,
        run_id: str | None = None,
        timeline_id: str | None = None,
        process_id: int | None = None,
        node_id: str | None = None,
        local_rank: int | None = None,
        global_rank: int | None = None,
        device_id: str | None = None,
        resource_id: str | None = None,
        clock_name: str | None = None,
        clock_origin: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
        fail_cleanup: bool = False,
    ) -> None:
        self._probe = probe
        self._execution_mode = ResourceMonitorExecutionMode.coerce(execution_mode)
        self._enabled = enabled
        self._clock = monotonic if clock is None else clock
        self._buffer = ResourceSampleBuffer(capacity=buffer_capacity, overflow_policy=buffer_overflow_policy)
        self._configured = False
        self._running = False
        self._lifecycle_sequence = 0
        self._sample_sequence = 0
        self._fail_cleanup = fail_cleanup
        self._run_id = coerce_optional_non_empty_string(run_id, owner="ResourceMonitor", field="run_id")
        self._timeline_id = coerce_optional_non_empty_string(timeline_id, owner="ResourceMonitor", field="timeline_id")
        self._process_id = _coerce_optional_non_negative_int(process_id, owner="ResourceMonitor", field="process_id")
        self._node_id = coerce_optional_non_empty_string(node_id, owner="ResourceMonitor", field="node_id")
        self._local_rank = _coerce_optional_non_negative_int(local_rank, owner="ResourceMonitor", field="local_rank")
        self._global_rank = _coerce_optional_non_negative_int(global_rank, owner="ResourceMonitor", field="global_rank")
        self._device_id = coerce_optional_non_empty_string(device_id, owner="ResourceMonitor", field="device_id")
        self._resource_id = coerce_optional_non_empty_string(resource_id, owner="ResourceMonitor", field="resource_id")
        self._clock_name = coerce_optional_non_empty_string(clock_name, owner="ResourceMonitor", field="clock_name")
        self._clock_origin = coerce_optional_non_empty_string(clock_origin, owner="ResourceMonitor", field="clock_origin")
        self._metadata = freeze_primitive_mapping(metadata, owner="ResourceMonitor", field="metadata")
        self._provenance = freeze_primitive_mapping(provenance, owner="ResourceMonitor", field="provenance")
        self._lifecycle_events: tuple[ResourceMonitorLifecycleRecord, ...] = ()

    @property
    def lifecycle_events(self) -> tuple[ResourceMonitorLifecycleRecord, ...]:
        return self._lifecycle_events

    @property
    def execution_mode(self) -> ResourceMonitorExecutionMode:
        return self._execution_mode

    @property
    def buffer(self) -> ResourceSampleBuffer:
        return self._buffer

    @property
    def probe(self) -> ResourceProbe:
        return self._probe

    def configure(self) -> None:
        if not self._enabled:
            self._record_lifecycle(ResourceMonitorLifecycleEvent.DISABLED, reason="disabled")
            return
        if self._configured:
            return
        self._configured = True
        self._record_lifecycle(ResourceMonitorLifecycleEvent.CONFIGURED)

    def start(self) -> None:
        if not self._enabled:
            self._record_lifecycle(ResourceMonitorLifecycleEvent.DISABLED, reason="disabled")
            return
        if not self._configured:
            self.configure()
        self._running = True
        self._record_lifecycle(ResourceMonitorLifecycleEvent.STARTED)

    def collect_sample(self) -> ResourceSample | None:
        if not self._enabled:
            self._record_lifecycle(ResourceMonitorLifecycleEvent.DISABLED, reason="disabled")
            return None
        if not self._running:
            self._record_lifecycle(
                ResourceMonitorLifecycleEvent.FAILED,
                reason="monitor_not_running",
            )
            return None

        sample_timestamp = self._next_timestamp()
        try:
            sample = self._probe.sample(
                timestamp=sample_timestamp,
                sequence_id=self._sample_sequence,
                run_id=self._run_id,
                timeline_id=self._timeline_id,
                clock_name=self._clock_name,
                clock_origin=self._clock_origin,
                process_id=self._process_id,
                node_id=self._node_id,
                local_rank=self._local_rank,
                global_rank=self._global_rank,
                device_id=self._device_id,
                source_probe_id=self._probe.probe_id,
                resource_id=self._resource_id,
            )
        except Exception as exc:
            self._record_lifecycle(
                ResourceMonitorLifecycleEvent.FAILED,
                reason=_exception_reason(exc),
            )
            return None
        self._sample_sequence += 1
        buffer_state = self._buffer.push(sample)
        self._record_lifecycle(
            ResourceMonitorLifecycleEvent.SAMPLE_EMITTED,
            reason=sample.reason,
            buffer_state=buffer_state,
            metadata={"sequence_id": sample.sequence_id, "status": sample.status.value},
        )
        if sample.status is not ResourceSampleStatus.AVAILABLE:
            self._record_lifecycle(
                ResourceMonitorLifecycleEvent.UNAVAILABLE,
                reason=sample.reason,
                buffer_state=buffer_state,
            )
        return sample

    def request_flush(self) -> ResourceSampleBufferState:
        if not self._enabled:
            self._record_lifecycle(ResourceMonitorLifecycleEvent.DISABLED, reason="disabled")
            return self._buffer.snapshot()
        if not self._running:
            self._record_lifecycle(ResourceMonitorLifecycleEvent.FAILED, reason="monitor_not_running")
            return self._buffer.snapshot()
        self._record_lifecycle(ResourceMonitorLifecycleEvent.FLUSH_REQUESTED, reason="flush_requested")
        state = self._buffer.snapshot()
        self._record_lifecycle(ResourceMonitorLifecycleEvent.FLUSH_COMPLETED, reason="flush_completed", buffer_state=state)
        self._buffer.clear()
        return state

    def stop(self) -> None:
        if not self._enabled:
            self._record_lifecycle(ResourceMonitorLifecycleEvent.DISABLED, reason="disabled")
            return
        self._running = False
        self._record_lifecycle(ResourceMonitorLifecycleEvent.STOPPED)

    def cleanup_orphan(self) -> None:
        self._record_lifecycle(ResourceMonitorLifecycleEvent.ORPHAN_CLEANUP_ATTEMPTED, reason="cleanup_attempt")
        if self._fail_cleanup:
            self._record_lifecycle(
                ResourceMonitorLifecycleEvent.ORPHAN_CLEANUP_FAILED,
                reason="forced_fail",
            )
            return
        self._record_lifecycle(ResourceMonitorLifecycleEvent.ORPHAN_CLEANUP_COMPLETED, reason="cleanup_ok")

    def _record_lifecycle(
        self,
        event: ResourceMonitorLifecycleEvent,
        *,
        reason: str | None = None,
        buffer_state: ResourceSampleBufferState | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        record = ResourceMonitorLifecycleRecord(
            event,
            self._lifecycle_sequence,
            probe_id=self._probe.probe_id,
            timestamp=self._next_timestamp(),
            reason=reason,
            run_id=self._run_id,
            timeline_id=self._timeline_id,
            clock_name=self._clock_name,
            clock_origin=self._clock_origin,
            process_id=self._process_id,
            node_id=self._node_id,
            local_rank=self._local_rank,
            global_rank=self._global_rank,
            device_id=self._device_id,
            resource_id=self._resource_id,
            buffer_state=buffer_state,
            metadata=metadata,
            provenance=provenance,
        )
        self._lifecycle_sequence += 1
        self._lifecycle_events += (record,)

    def _next_timestamp(self) -> float:
        try:
            timestamp = self._clock()
        except Exception as exc:
            raise RemotePhysTrainingError(
                "ResourceMonitor clock failed to produce a timestamp.",
                owner="ResourceMonitor",
                field="clock",
                expected="callable returning a finite non-negative timestamp",
                actual=type(exc).__name__,
            ) from exc
        return _coerce_non_negative_timestamp(timestamp, owner="ResourceMonitor", field="clock")


@dataclass(frozen=True, init=False, slots=True)
class ProfileWriterAppendResult:
    """Evidence for enqueue attempts into profile writer queue."""

    status: ProfileWriterResultStatus
    sequence_id: int
    timestamp: float
    queue_depth: int
    queue_capacity: int
    accepted_count: int
    dropped_count: int
    failure_reason: str | None

    def __init__(
        self,
        status: ProfileWriterResultStatus | str,
        *,
        sequence_id: int,
        timestamp: float | int,
        queue_depth: int,
        queue_capacity: int,
        accepted_count: int,
        dropped_count: int,
        failure_reason: str | None = None,
    ) -> None:
        object.__setattr__(self, "status", ProfileWriterResultStatus.coerce(status))
        object.__setattr__(self, "sequence_id", coerce_non_negative_int(sequence_id, owner="ProfileWriterAppendResult", field="sequence_id"))
        object.__setattr__(self, "timestamp", _coerce_non_negative_timestamp(timestamp, owner="ProfileWriterAppendResult", field="timestamp"))
        object.__setattr__(self, "queue_depth", coerce_non_negative_int(queue_depth, owner="ProfileWriterAppendResult", field="queue_depth"))
        object.__setattr__(self, "queue_capacity", coerce_non_negative_int(queue_capacity, owner="ProfileWriterAppendResult", field="queue_capacity"))
        object.__setattr__(self, "accepted_count", coerce_non_negative_int(accepted_count, owner="ProfileWriterAppendResult", field="accepted_count"))
        object.__setattr__(self, "dropped_count", coerce_non_negative_int(dropped_count, owner="ProfileWriterAppendResult", field="dropped_count"))
        object.__setattr__(
            self,
            "failure_reason",
            coerce_optional_non_empty_string(failure_reason, owner="ProfileWriterAppendResult", field="failure_reason"),
        )


@dataclass(frozen=True, init=False, slots=True)
class ProfileWriterFlushResult:
    """Evidence for async flush and write outcomes."""

    scope: ProfileWriterFlushScope
    status: ProfileWriterResultStatus
    sequence_id: int
    timestamp: float
    requested_count: int
    written_count: int
    dropped_count: int
    remaining_count: int
    failure_reason: str | None
    retry_requested: bool

    def __init__(
        self,
        scope: ProfileWriterFlushScope | str,
        status: ProfileWriterResultStatus | str,
        *,
        sequence_id: int,
        timestamp: float | int,
        requested_count: int,
        written_count: int,
        dropped_count: int,
        remaining_count: int,
        failure_reason: str | None = None,
        retry_requested: bool = False,
    ) -> None:
        object.__setattr__(self, "scope", ProfileWriterFlushScope.coerce(scope))
        object.__setattr__(self, "status", ProfileWriterResultStatus.coerce(status))
        object.__setattr__(self, "sequence_id", coerce_non_negative_int(sequence_id, owner="ProfileWriterFlushResult", field="sequence_id"))
        object.__setattr__(
            self,
            "timestamp",
            _coerce_non_negative_timestamp(timestamp, owner="ProfileWriterFlushResult", field="timestamp"),
        )
        object.__setattr__(self, "requested_count", coerce_non_negative_int(requested_count, owner="ProfileWriterFlushResult", field="requested_count"))
        object.__setattr__(self, "written_count", coerce_non_negative_int(written_count, owner="ProfileWriterFlushResult", field="written_count"))
        object.__setattr__(self, "dropped_count", coerce_non_negative_int(dropped_count, owner="ProfileWriterFlushResult", field="dropped_count"))
        object.__setattr__(self, "remaining_count", coerce_non_negative_int(remaining_count, owner="ProfileWriterFlushResult", field="remaining_count"))
        object.__setattr__(
            self,
            "failure_reason",
            coerce_optional_non_empty_string(failure_reason, owner="ProfileWriterFlushResult", field="failure_reason"),
        )
        object.__setattr__(
            self,
            "retry_requested",
            bool(retry_requested),
        )


@runtime_checkable
class ProfileWriterBackend(Protocol):
    """Minimal contract for profile persistence sinks."""

    def write(
        self,
        records: tuple[object, ...],
        *,
        scope: ProfileWriterFlushScope,
        sequence_id: int,
    ) -> int:
        ...


class InMemoryProfileWriterBackend:
    """Dependency-free test backend with deterministic failure policy."""

    def __init__(self, *, fail_on_calls: Sequence[int] = ()) -> None:
        self.fail_on_calls = tuple(fail_on_calls)
        self.write_calls = 0
        self.written_records: tuple[object, ...] = ()

    def write(self, records: tuple[object, ...], *, scope: ProfileWriterFlushScope, sequence_id: int) -> int:
        del scope, sequence_id
        self.write_calls += 1
        if self.write_calls in self.fail_on_calls:
            raise RuntimeError("in-memory profile writer backend forced failure")
        self.written_records += records
        return len(records)


class AsyncTrainingProfileWriter:
    """Bounded async-ish profile writer contract with flush scopes."""

    def __init__(
        self,
        backend: ProfileWriterBackend | None,
        *,
        enabled: bool = True,
        queue_capacity: int = 256,
        overflow_policy: ResourceBufferOverflowPolicy | str = ResourceBufferOverflowPolicy.DROP_OLDEST,
        flush_cadence_seconds: float | int | None = None,
        enable_retry: bool = False,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._backend = backend
        self._enabled = enabled
        self._enable_retry = enable_retry
        self._clock = monotonic if clock is None else clock
        self._buffer = ResourceSampleBuffer(
            capacity=queue_capacity,
            overflow_policy=overflow_policy,
        )
        self._sequence_id = 0
        self._flush_sequence_id = 0
        self._flush_results: tuple[ProfileWriterFlushResult, ...] = ()
        self._append_results: tuple[ProfileWriterAppendResult, ...] = ()
        if flush_cadence_seconds is not None:
            self._flush_cadence_seconds = _coerce_optional_positive_or_zero_float(
                flush_cadence_seconds,
                owner="AsyncTrainingProfileWriter",
                field="flush_cadence_seconds",
            )
            self._last_periodic_check = self._next_timestamp()
        else:
            self._flush_cadence_seconds = None
            self._last_periodic_check = None

    @property
    def queue_state(self) -> ResourceSampleBufferState:
        return self._buffer.snapshot()

    @property
    def lifecycle(self) -> tuple[ProfileWriterAppendResult, ...]:
        return self._append_results

    @property
    def flush_results(self) -> tuple[ProfileWriterFlushResult, ...]:
        return self._flush_results

    def append(self, record: object) -> ProfileWriterAppendResult:
        if not self._enabled or self._backend is None:
            append_result = ProfileWriterAppendResult(
                ProfileWriterResultStatus.DISABLED,
                sequence_id=self._sequence_id,
                timestamp=self._next_timestamp(),
                queue_depth=self._buffer.queue_depth,
                queue_capacity=self._buffer.capacity,
                accepted_count=self._buffer.accepted_count,
                dropped_count=self._buffer.dropped_count,
            )
            self._sequence_id += 1
            self._append_results += (append_result,)
            return append_result

        before = self._buffer.snapshot()
        self._buffer.push(record)
        after = self._buffer.snapshot()
        status = ProfileWriterResultStatus.ENQUEUED
        failure_reason = None
        if after.dropped_count > before.dropped_count and after.queue_depth == before.queue_depth:
            status = ProfileWriterResultStatus.REJECTED if self._buffer.overflow_policy is ResourceBufferOverflowPolicy.REJECT_NEW else ProfileWriterResultStatus.ENQUEUED
            failure_reason = "buffer_full"
        append_result = ProfileWriterAppendResult(
            status,
            sequence_id=self._sequence_id,
            timestamp=self._next_timestamp(),
            queue_depth=after.queue_depth,
            queue_capacity=after.capacity,
            accepted_count=after.accepted_count,
            dropped_count=after.dropped_count,
            failure_reason=failure_reason,
        )
        self._sequence_id += 1
        self._append_results += (append_result,)

        if self._flush_cadence_seconds is not None and self._last_periodic_check is not None:
            now = self._next_timestamp()
            elapsed = now - self._last_periodic_check
            if elapsed >= self._flush_cadence_seconds:
                self.flush(ProfileWriterFlushScope.PERIODIC)
                self._last_periodic_check = now
        return append_result

    def flush(self, scope: ProfileWriterFlushScope | str = ProfileWriterFlushScope.MANUAL) -> ProfileWriterFlushResult:
        scope = ProfileWriterFlushScope.coerce(scope)
        result = self._flush_records(scope)
        self._flush_results += (result,)
        return result

    def flush_step(self) -> ProfileWriterFlushResult:
        return self.flush(ProfileWriterFlushScope.STEP)

    def flush_epoch(self) -> ProfileWriterFlushResult:
        return self.flush(ProfileWriterFlushScope.EPOCH)

    def flush_run(self) -> ProfileWriterFlushResult:
        return self.flush(ProfileWriterFlushScope.RUN)

    def snapshot(self) -> tuple[ProfileWriterFlushResult, ...]:
        return self._flush_results

    def _flush_records(self, scope: ProfileWriterFlushScope) -> ProfileWriterFlushResult:
        sequence_id = self._flush_sequence_id
        self._flush_sequence_id += 1
        timestamp = self._next_timestamp()
        if not self._enabled or self._backend is None:
            return ProfileWriterFlushResult(
                scope,
                ProfileWriterResultStatus.DISABLED,
                sequence_id=sequence_id,
                timestamp=timestamp,
                requested_count=0,
                written_count=0,
                dropped_count=0,
                remaining_count=self._buffer.queue_depth,
                failure_reason="writer_disabled",
            )

        requested = self._buffer.queue_depth
        if requested == 0:
            result = ProfileWriterFlushResult(
                scope,
                ProfileWriterResultStatus.SKIPPED,
                sequence_id=sequence_id,
                timestamp=timestamp,
                requested_count=0,
                written_count=0,
                dropped_count=0,
                remaining_count=0,
            )
            return result

        pending = self._buffer.items()
        try:
            written = self._backend.write(pending, scope=scope, sequence_id=sequence_id)
        except Exception as exc:
            return ProfileWriterFlushResult(
                scope,
                ProfileWriterResultStatus.FAILED,
                sequence_id=sequence_id,
                timestamp=timestamp,
                requested_count=requested,
                written_count=0,
                dropped_count=0,
                remaining_count=requested,
                failure_reason=_exception_reason(exc),
                retry_requested=self._enable_retry,
            )

        if isinstance(written, bool) or not isinstance(written, int) or written < 0:
            return ProfileWriterFlushResult(
                scope,
                ProfileWriterResultStatus.FAILED,
                sequence_id=sequence_id,
                timestamp=timestamp,
                requested_count=requested,
                written_count=0,
                dropped_count=0,
                remaining_count=requested,
                failure_reason="invalid_write_count",
            )

        if written != requested:
            return ProfileWriterFlushResult(
                scope,
                ProfileWriterResultStatus.FAILED,
                sequence_id=sequence_id,
                timestamp=timestamp,
                requested_count=requested,
                written_count=written,
                dropped_count=0,
                remaining_count=requested,
                failure_reason="partial_or_non_monotonic_write_count",
            )

        self._buffer.clear()
        return ProfileWriterFlushResult(
            scope,
            ProfileWriterResultStatus.COMPLETED,
            sequence_id=sequence_id,
            timestamp=timestamp,
            requested_count=requested,
            written_count=written,
            dropped_count=0,
            remaining_count=0,
        )

    def _next_timestamp(self) -> float:
        try:
            timestamp = self._clock()
        except Exception as exc:
            raise RemotePhysTrainingError(
                "AsyncTrainingProfileWriter clock failed to produce a timestamp.",
                owner="AsyncTrainingProfileWriter",
                field="clock",
                expected="callable returning a finite non-negative timestamp",
                actual=type(exc).__name__,
            ) from exc
        return _coerce_non_negative_timestamp(timestamp, owner="AsyncTrainingProfileWriter", field="clock")


@dataclass(frozen=True, init=False, slots=True)
class TrainingProfile:
    """Minimal profile aggregate with primitive trace evidence."""

    event_logs: tuple[TrainingEventLog, ...]
    scalar_spans: tuple[ProfileSpanSummary, ...]
    unavailable_spans: tuple[UnavailableProfileProbe, ...]
    resource_traces: tuple[ResourceTrace, ...]
    monitor_lifecycle_records: tuple[ResourceMonitorLifecycleRecord, ...]
    writer_results: tuple[ProfileWriterFlushResult, ...]
    decisions: tuple[str, ...]

    def __init__(
        self,
        *,
        event_logs: Iterable[TrainingEventLog] = (),
        scalar_spans: Iterable[ProfileSpanSummary] = (),
        unavailable_spans: Iterable[UnavailableProfileProbe] = (),
        resource_traces: Iterable[ResourceTrace] = (),
        monitor_lifecycle_records: Iterable[ResourceMonitorLifecycleRecord] = (),
        writer_results: Iterable[ProfileWriterFlushResult] = (),
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
            _coerce_records(
                scalar_spans,
                ProfileSpanSummary,
                owner="TrainingProfile",
                field="scalar_spans",
            ),
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
            "resource_traces",
            _coerce_records(
                resource_traces,
                ResourceTrace,
                owner="TrainingProfile",
                field="resource_traces",
            ),
        )
        object.__setattr__(
            self,
            "monitor_lifecycle_records",
            _coerce_records(
                monitor_lifecycle_records,
                ResourceMonitorLifecycleRecord,
                owner="TrainingProfile",
                field="monitor_lifecycle_records",
            ),
        )
        object.__setattr__(
            self,
            "writer_results",
            _coerce_records(
                writer_results,
                ProfileWriterFlushResult,
                owner="TrainingProfile",
                field="writer_results",
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

    def resource_traces_for(
        self,
        *,
        metric_kind: ResourceMetricKind | str | None = None,
        source_probe_id: str | None = None,
        timeline_id: str | None = None,
        series_key: str | None = None,
    ) -> tuple[ResourceTrace, ...]:
        metric = ResourceMetricKind.coerce(metric_kind) if metric_kind is not None else None
        return tuple(
            trace
            for trace in self.resource_traces
            if (metric is None or trace.metric_kind == metric)
            and (source_probe_id is None or trace.source_probe_id == source_probe_id)
            and (timeline_id is None or trace.timeline_id == timeline_id)
            and (series_key is None or trace.series_key == series_key)
        )

    def resource_samples(self, *, metric_kind: ResourceMetricKind | str | None = None) -> tuple[ResourceSample, ...]:
        if metric_kind is None:
            traces = self.resource_traces
        else:
            traces = self.resource_traces_for(metric_kind=metric_kind)
        values: list[ResourceSample] = []
        for trace in traces:
            values.extend(trace.samples)
        return tuple(values)

    def monitor_lifecycle_events(
        self,
        *,
        event: ResourceMonitorLifecycleEvent | str | None = None,
        probe_id: str | None = None,
    ) -> tuple[ResourceMonitorLifecycleRecord, ...]:
        event_value = ResourceMonitorLifecycleEvent.coerce(event) if event is not None else None
        return tuple(
            record
            for record in self.monitor_lifecycle_records
            if (event_value is None or record.event == event_value)
            and (probe_id is None or record.probe_id == probe_id)
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
        self._resource_traces: tuple[ResourceTrace, ...] = ()
        self._monitor_lifecycle_records: tuple[ResourceMonitorLifecycleRecord, ...] = ()
        self._writer_results: tuple[ProfileWriterFlushResult, ...] = ()
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
        timeline_id = event.timeline_id or "default"
        event_logs = list(self._event_logs)
        for index, event_log in enumerate(event_logs):
            if event_log.timeline_id == timeline_id:
                event = self._with_event_log_evidence(event, event_log=event_log)
                event_logs[index] = event_log.append(event)
                break
        else:
            event = self._with_event_log_evidence(event, timeline_id=timeline_id)
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

    def record_resource_sample(self, sample: ResourceSample) -> None:
        """Record a resource sample and bucket it into a stable trace."""

        if not isinstance(sample, ResourceSample):
            raise RemotePhysTrainingError(
                "TrainingProfileRecorder.record_resource_sample expects a ResourceSample.",
                owner="TrainingProfileRecorder",
                field="sample",
                expected="ResourceSample",
                actual=type(sample).__name__,
            )

        key = self._resource_trace_key(sample)
        resource_traces = list(self._resource_traces)
        for index, trace in enumerate(resource_traces):
            if self._resource_trace_key(trace) == key:
                resource_traces[index] = trace.append(sample)
                break
        else:
            resource_traces.append(
                ResourceTrace(
                    metric_kind=sample.metric_kind,
                    metric_name=sample.metric_name,
                    unit=sample.unit,
                    source_probe_id=sample.source_probe_id,
                    samples=(sample,),
                    series_key=sample.series_key,
                    run_id=sample.run_id,
                    timeline_id=sample.timeline_id,
                    clock_name=sample.clock_name,
                    clock_origin=sample.clock_origin,
                    process_id=sample.process_id,
                    node_id=sample.node_id,
                    local_rank=sample.local_rank,
                    global_rank=sample.global_rank,
                    device_id=sample.device_id,
                    resource_id=sample.resource_id,
                    metadata={"metric_kind": sample.metric_kind.value},
                    provenance={"source_probe_id": sample.source_probe_id},
                ),
            )
        self._resource_traces = tuple(resource_traces)

    def record_resource_trace(self, trace: ResourceTrace) -> None:
        if not isinstance(trace, ResourceTrace):
            raise RemotePhysTrainingError(
                "TrainingProfileRecorder.record_resource_trace expects a ResourceTrace.",
                owner="TrainingProfileRecorder",
                field="trace",
                expected="ResourceTrace",
                actual=type(trace).__name__,
            )
        self._resource_traces += (trace,)

    def record_monitor_lifecycle_record(self, record: ResourceMonitorLifecycleRecord) -> None:
        if not isinstance(record, ResourceMonitorLifecycleRecord):
            raise RemotePhysTrainingError(
                "TrainingProfileRecorder.record_monitor_lifecycle_record expects a ResourceMonitorLifecycleRecord.",
                owner="TrainingProfileRecorder",
                field="record",
                expected="ResourceMonitorLifecycleRecord",
                actual=type(record).__name__,
            )
        self._monitor_lifecycle_records += (record,)

    def record_writer_result(self, result: ProfileWriterFlushResult) -> None:
        if not isinstance(result, ProfileWriterFlushResult):
            raise RemotePhysTrainingError(
                "TrainingProfileRecorder.record_writer_result expects a ProfileWriterFlushResult.",
                owner="TrainingProfileRecorder",
                field="result",
                expected="ProfileWriterFlushResult",
                actual=type(result).__name__,
            )
        self._writer_results += (result,)

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
            resource_traces=self._resource_traces,
            monitor_lifecycle_records=self._monitor_lifecycle_records,
            writer_results=self._writer_results,
            decisions=self._decisions,
        )

    def _resource_trace_key(self, sample_or_trace: ResourceSample | ResourceTrace) -> tuple[object, ...]:
        if isinstance(sample_or_trace, ResourceTrace):
            return (
                sample_or_trace.metric_kind,
                sample_or_trace.source_probe_id,
                sample_or_trace.series_key,
                sample_or_trace.run_id,
                sample_or_trace.timeline_id,
            )
        return (
            sample_or_trace.metric_kind,
            sample_or_trace.source_probe_id,
            sample_or_trace.series_key,
            sample_or_trace.run_id,
            sample_or_trace.timeline_id,
        )

    def _with_event_log_evidence(
        self,
        event: TrainingEvent,
        *,
        timeline_id: str | None = None,
        event_log: TrainingEventLog | None = None,
    ) -> TrainingEvent:
        if event_log is not None:
            timeline_id = event_log.timeline_id
            previous_sequences = [
                logged_event.sequence_id
                for logged_event in event_log.events
                if logged_event.sequence_id is not None
            ]
        else:
            previous_sequences = []
        sequence_id = event.sequence_id
        if sequence_id is None:
            sequence_id = max(previous_sequences, default=-1) + 1
        return TrainingEvent(
            event.phase,
            event.mode,
            status=event.status,
            epoch_index=event.epoch_index,
            step_index=event.step_index,
            batch_index=event.batch_index,
            split=event.split,
            run_id=event.run_id,
            timeline_id=event.timeline_id or timeline_id,
            sequence_id=sequence_id,
            timestamp=event.timestamp if event.timestamp is not None else self._clock(),
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


def _exception_reason(exc: Exception) -> str:
    return str(exc) or type(exc).__name__


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


def _coerce_non_negative_timestamp(
    value: float | int | None,
    *,
    owner: str,
    field: str,
) -> float:
    if value is None:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be provided.",
            owner=owner,
            field=field,
            expected="non-negative number",
            actual="None",
        )
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or value < 0
        or not isfinite(value)
    ):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a non-negative number.",
            owner=owner,
            field=field,
            expected="non-negative number",
            actual=type(value).__name__,
        )
    return float(value)


def _coerce_optional_positive_or_zero_float(
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
        or not isfinite(value)
    ):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be non-negative when provided.",
            owner=owner,
            field=field,
            expected="non-negative number | None",
            actual=type(value).__name__,
        )
    return float(value)


def _coerce_optional_timestamp(
    value: float | int | None,
    *,
    owner: str,
    field: str,
) -> float | None:
    return _coerce_optional_positive_or_zero_float(value, owner=owner, field=field)


def _coerce_optional_positive_or_zero_duration(
    value: float | int | None,
    *,
    owner: str,
    field: str,
) -> float | None:
    return _coerce_optional_positive_or_zero_float(value, owner=owner, field=field)


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
        or not isfinite(value)
    ):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a non-negative number when provided.",
            owner=owner,
            field=field,
            expected="non-negative number | None",
            actual=type(value).__name__,
        )
    return float(value)


def _coerce_resource_sample_value(
    value: float | int | None,
    *,
    owner: str,
    field: str,
    status: ResourceSampleStatus,
) -> float | None:
    if status is not ResourceSampleStatus.AVAILABLE:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or value < 0
        or not isfinite(value)
    ):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a non-negative finite number when provided.",
            owner=owner,
            field=field,
            expected="non-negative number",
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


def _coerce_resource_scope_string(
    explicit: str | None,
    inferred: str | None,
    *,
    owner: str,
    field: str,
) -> str | None:
    if explicit is not None:
        return _coerce_name(explicit, owner=owner, field=field)
    return inferred


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
ResourceSample.__hash__ = None  # type: ignore[assignment]
ResourceTrace.__hash__ = None  # type: ignore[assignment]
ResourceSampleBufferState.__hash__ = None  # type: ignore[assignment]
ResourceSampleBuffer.__hash__ = None  # type: ignore[assignment]
ResourceMonitorLifecycleRecord.__hash__ = None  # type: ignore[assignment]
ProfileWriterAppendResult.__hash__ = None  # type: ignore[assignment]
ProfileWriterFlushResult.__hash__ = None  # type: ignore[assignment]
