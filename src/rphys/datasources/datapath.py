"""Descriptor-only data-path evidence records for Stage 9 and Stage 15.

These public provisional records make loader/cache/prepared/materialization
evidence inspectable. Stage 15 helpers assemble primitive profile, benchmark,
pipeline-stage, and fake data-quality evidence without implementing streaming,
trainer, device, model-formatting, storage-backend, or distributed runtime
behavior.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from rphys.errors import FieldTypeError, RemotePhysDataSourceError
from rphys.io._primitives import FrozenPrimitive, freeze_primitive

__all__ = [
    "StreamingReadPlan",
    "DataLoaderState",
    "DataPathProfile",
    "DataPathBenchmark",
    "DATA_PATH_MEASUREMENT_UNITS",
    "DataPipelineStage",
    "DataPipelineStageContext",
    "DataQualityIssueKind",
    "DataQualityProbeResult",
    "FakeDataQualityProbe",
    "build_data_path_benchmark",
    "build_data_path_profile",
    "build_data_pipeline_stage_context",
]


DATA_PATH_MEASUREMENT_UNITS = MappingProxyType(
    {
        "duration.decode.ms": "ms",
        "duration.collate.ms": "ms",
        "duration.queue_wait.ms": "ms",
        "duration.worker_wait.ms": "ms",
        "duration.disk_read.ms": "ms",
        "duration.network_read.ms": "ms",
        "duration.device_transfer.ms": "ms",
        "duration.synchronization.ms": "ms",
        "bytes.read": "bytes",
        "bytes.written": "bytes",
        "throughput.samples_per_second": "samples/s",
        "throughput.bytes_per_second": "bytes/s",
        "cache.hit.count": "count",
        "cache.miss.count": "count",
        "prepared.read.count": "count",
        "unavailable.count": "count",
    }
)


class DataPipelineStage(StrEnum):
    """Stage-9-aligned data-path stages for profiling and probe evidence."""

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
    QUEUE_WAIT = "queue_wait"

    @classmethod
    def coerce(cls, value: "DataPipelineStage | str") -> "DataPipelineStage":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise FieldTypeError(
                    "Unsupported data-pipeline stage.",
                    field="stage",
                    expected=tuple(stage.value for stage in cls),
                    actual=value,
                ) from exc
        raise FieldTypeError(
            "DataPipelineStage must be a DataPipelineStage or string.",
            field="stage",
            expected="DataPipelineStage | str",
            actual=type(value).__name__,
        )


@dataclass(frozen=True, init=False, slots=True)
class StreamingReadPlan:
    """Primitive read-window and resume-hint evidence, not a streaming runtime."""

    plan_id: str
    mode: str
    request_fingerprint: str | None
    materialization_fingerprint: str | None
    sample_count: int | None
    start_position: int
    stop_position: int | None
    skip_positions: tuple[int, ...]
    resume_token: FrozenPrimitive | None
    prefetch: int | None
    worker_count: int | None
    distributed_coordination: str
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        plan_id: str,
        *,
        mode: str = "sequential",
        request_fingerprint: str | None = None,
        materialization_fingerprint: str | None = None,
        sample_count: int | None = None,
        start_position: int = 0,
        stop_position: int | None = None,
        skip_positions: Sequence[int] = (),
        resume_token: object | None = None,
        prefetch: int | None = None,
        worker_count: int | None = None,
        distributed_coordination: str = "none",
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "plan_id", plan_id, owner="StreamingReadPlan")
        object.__setattr__(
            self,
            "mode",
            _coerce_choice(
                mode,
                owner="StreamingReadPlan",
                field="mode",
                choices={"sequential", "skip", "resume_hint", "windowed"},
            ),
        )
        _set_optional_fingerprint(
            self,
            "request_fingerprint",
            request_fingerprint,
            owner="StreamingReadPlan",
        )
        _set_optional_fingerprint(
            self,
            "materialization_fingerprint",
            materialization_fingerprint,
            owner="StreamingReadPlan",
        )
        _set_optional_non_negative_int(
            self,
            "sample_count",
            sample_count,
            owner="StreamingReadPlan",
        )
        _set_non_negative_int(self, "start_position", start_position, owner="StreamingReadPlan")
        _set_optional_non_negative_int(
            self,
            "stop_position",
            stop_position,
            owner="StreamingReadPlan",
        )
        object.__setattr__(
            self,
            "skip_positions",
            _coerce_position_sequence(skip_positions, field="skip_positions"),
        )
        object.__setattr__(
            self,
            "resume_token",
            _coerce_optional_primitive(
                resume_token,
                owner="StreamingReadPlan",
                field="resume_token",
            ),
        )
        _set_optional_non_negative_int(self, "prefetch", prefetch, owner="StreamingReadPlan")
        _set_optional_positive_int(self, "worker_count", worker_count, owner="StreamingReadPlan")
        object.__setattr__(
            self,
            "distributed_coordination",
            _coerce_coordination(distributed_coordination, owner="StreamingReadPlan"),
        )
        _set_primitive_mapping(self, "metadata", metadata, owner="StreamingReadPlan")
        _validate_streaming_read_plan(self)
        _set_fingerprint(self, fingerprint, owner="StreamingReadPlan")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "plan_id": self.plan_id,
                "mode": self.mode,
                "request_fingerprint": self.request_fingerprint,
                "materialization_fingerprint": self.materialization_fingerprint,
                "sample_count": self.sample_count,
                "start_position": self.start_position,
                "stop_position": self.stop_position,
                "skip_positions": list(self.skip_positions),
                "resume_token": self.resume_token,
                "prefetch": self.prefetch,
                "worker_count": self.worker_count,
                "distributed_coordination": self.distributed_coordination,
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "StreamingReadPlan":
        data = _require_record(
            value,
            {
                "plan_id",
                "mode",
                "request_fingerprint",
                "materialization_fingerprint",
                "sample_count",
                "start_position",
                "stop_position",
                "skip_positions",
                "resume_token",
                "prefetch",
                "worker_count",
                "distributed_coordination",
                "metadata",
                "fingerprint",
            },
            descriptor="StreamingReadPlan",
        )
        return cls(
            data["plan_id"],  # type: ignore[arg-type]
            mode=data["mode"],  # type: ignore[arg-type]
            request_fingerprint=data["request_fingerprint"],  # type: ignore[arg-type]
            materialization_fingerprint=data["materialization_fingerprint"],  # type: ignore[arg-type]
            sample_count=data["sample_count"],  # type: ignore[arg-type]
            start_position=data["start_position"],  # type: ignore[arg-type]
            stop_position=data["stop_position"],  # type: ignore[arg-type]
            skip_positions=data["skip_positions"],  # type: ignore[arg-type]
            resume_token=data["resume_token"],
            prefetch=data["prefetch"],  # type: ignore[arg-type]
            worker_count=data["worker_count"],  # type: ignore[arg-type]
            distributed_coordination=data["distributed_coordination"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


StreamingReadPlan.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class DataLoaderState:
    """Primitive snapshot of loader progress and cache/prepared outcomes."""

    state_id: str
    status: str
    streaming_plan_fingerprint: str | None
    request_fingerprint: str | None
    positions_seen: int
    positions_skipped: int
    positions_resumed: int
    cache_hits: int
    cache_misses: int
    rereads: int
    prepared_reads: int
    materialized_reads: int
    batch_count: int
    last_position: int | None
    distributed_coordination: str
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        state_id: str,
        *,
        status: str = "completed",
        streaming_plan_fingerprint: str | None = None,
        request_fingerprint: str | None = None,
        positions_seen: int = 0,
        positions_skipped: int = 0,
        positions_resumed: int = 0,
        cache_hits: int = 0,
        cache_misses: int = 0,
        rereads: int = 0,
        prepared_reads: int = 0,
        materialized_reads: int = 0,
        batch_count: int = 0,
        last_position: int | None = None,
        distributed_coordination: str = "none",
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "state_id", state_id, owner="DataLoaderState")
        object.__setattr__(
            self,
            "status",
            _coerce_choice(
                status,
                owner="DataLoaderState",
                field="status",
                choices={"planned", "running_snapshot", "completed", "interrupted"},
            ),
        )
        _set_optional_fingerprint(
            self,
            "streaming_plan_fingerprint",
            streaming_plan_fingerprint,
            owner="DataLoaderState",
        )
        _set_optional_fingerprint(
            self,
            "request_fingerprint",
            request_fingerprint,
            owner="DataLoaderState",
        )
        for field, value in {
            "positions_seen": positions_seen,
            "positions_skipped": positions_skipped,
            "positions_resumed": positions_resumed,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "rereads": rereads,
            "prepared_reads": prepared_reads,
            "materialized_reads": materialized_reads,
            "batch_count": batch_count,
        }.items():
            _set_non_negative_int(self, field, value, owner="DataLoaderState")
        _set_optional_non_negative_int(
            self,
            "last_position",
            last_position,
            owner="DataLoaderState",
        )
        object.__setattr__(
            self,
            "distributed_coordination",
            _coerce_coordination(distributed_coordination, owner="DataLoaderState"),
        )
        _set_primitive_mapping(self, "metadata", metadata, owner="DataLoaderState")
        _set_fingerprint(self, fingerprint, owner="DataLoaderState")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "state_id": self.state_id,
                "status": self.status,
                "streaming_plan_fingerprint": self.streaming_plan_fingerprint,
                "request_fingerprint": self.request_fingerprint,
                "positions_seen": self.positions_seen,
                "positions_skipped": self.positions_skipped,
                "positions_resumed": self.positions_resumed,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "rereads": self.rereads,
                "prepared_reads": self.prepared_reads,
                "materialized_reads": self.materialized_reads,
                "batch_count": self.batch_count,
                "last_position": self.last_position,
                "distributed_coordination": self.distributed_coordination,
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "DataLoaderState":
        data = _require_record(
            value,
            {
                "state_id",
                "status",
                "streaming_plan_fingerprint",
                "request_fingerprint",
                "positions_seen",
                "positions_skipped",
                "positions_resumed",
                "cache_hits",
                "cache_misses",
                "rereads",
                "prepared_reads",
                "materialized_reads",
                "batch_count",
                "last_position",
                "distributed_coordination",
                "metadata",
                "fingerprint",
            },
            descriptor="DataLoaderState",
        )
        return cls(
            data["state_id"],  # type: ignore[arg-type]
            status=data["status"],  # type: ignore[arg-type]
            streaming_plan_fingerprint=data["streaming_plan_fingerprint"],  # type: ignore[arg-type]
            request_fingerprint=data["request_fingerprint"],  # type: ignore[arg-type]
            positions_seen=data["positions_seen"],  # type: ignore[arg-type]
            positions_skipped=data["positions_skipped"],  # type: ignore[arg-type]
            positions_resumed=data["positions_resumed"],  # type: ignore[arg-type]
            cache_hits=data["cache_hits"],  # type: ignore[arg-type]
            cache_misses=data["cache_misses"],  # type: ignore[arg-type]
            rereads=data["rereads"],  # type: ignore[arg-type]
            prepared_reads=data["prepared_reads"],  # type: ignore[arg-type]
            materialized_reads=data["materialized_reads"],  # type: ignore[arg-type]
            batch_count=data["batch_count"],  # type: ignore[arg-type]
            last_position=data["last_position"],  # type: ignore[arg-type]
            distributed_coordination=data["distributed_coordination"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


DataLoaderState.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class DataPathProfile:
    """Primitive performance and outcome evidence for one data path."""

    profile_id: str
    loader_state_fingerprint: str | None
    streaming_plan_fingerprint: str | None
    sample_count: int
    batch_count: int
    cache_hits: int
    cache_misses: int
    rereads: int
    prepared_reads: int
    materialized_reads: int
    total_duration_ms: float | None
    dataloader_wait_ms: float | None
    cache_wait_ms: float | None
    materialization_wait_ms: float | None
    throughput_samples_per_second: float | None
    summaries: Mapping[str, FrozenPrimitive]
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        profile_id: str,
        *,
        loader_state_fingerprint: str | None = None,
        streaming_plan_fingerprint: str | None = None,
        sample_count: int = 0,
        batch_count: int = 0,
        cache_hits: int = 0,
        cache_misses: int = 0,
        rereads: int = 0,
        prepared_reads: int = 0,
        materialized_reads: int = 0,
        total_duration_ms: float | int | None = None,
        dataloader_wait_ms: float | int | None = None,
        cache_wait_ms: float | int | None = None,
        materialization_wait_ms: float | int | None = None,
        throughput_samples_per_second: float | int | None = None,
        summaries: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "profile_id", profile_id, owner="DataPathProfile")
        _set_optional_fingerprint(
            self,
            "loader_state_fingerprint",
            loader_state_fingerprint,
            owner="DataPathProfile",
        )
        _set_optional_fingerprint(
            self,
            "streaming_plan_fingerprint",
            streaming_plan_fingerprint,
            owner="DataPathProfile",
        )
        for field, value in {
            "sample_count": sample_count,
            "batch_count": batch_count,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "rereads": rereads,
            "prepared_reads": prepared_reads,
            "materialized_reads": materialized_reads,
        }.items():
            _set_non_negative_int(self, field, value, owner="DataPathProfile")
        for field, value in {
            "total_duration_ms": total_duration_ms,
            "dataloader_wait_ms": dataloader_wait_ms,
            "cache_wait_ms": cache_wait_ms,
            "materialization_wait_ms": materialization_wait_ms,
            "throughput_samples_per_second": throughput_samples_per_second,
        }.items():
            _set_optional_non_negative_float(self, field, value, owner="DataPathProfile")
        _set_primitive_mapping(self, "summaries", summaries, owner="DataPathProfile")
        _set_primitive_mapping(self, "metadata", metadata, owner="DataPathProfile")
        _set_fingerprint(self, fingerprint, owner="DataPathProfile")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "profile_id": self.profile_id,
                "loader_state_fingerprint": self.loader_state_fingerprint,
                "streaming_plan_fingerprint": self.streaming_plan_fingerprint,
                "sample_count": self.sample_count,
                "batch_count": self.batch_count,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "rereads": self.rereads,
                "prepared_reads": self.prepared_reads,
                "materialized_reads": self.materialized_reads,
                "total_duration_ms": self.total_duration_ms,
                "dataloader_wait_ms": self.dataloader_wait_ms,
                "cache_wait_ms": self.cache_wait_ms,
                "materialization_wait_ms": self.materialization_wait_ms,
                "throughput_samples_per_second": self.throughput_samples_per_second,
                "summaries": dict(self.summaries),
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "DataPathProfile":
        data = _require_record(
            value,
            {
                "profile_id",
                "loader_state_fingerprint",
                "streaming_plan_fingerprint",
                "sample_count",
                "batch_count",
                "cache_hits",
                "cache_misses",
                "rereads",
                "prepared_reads",
                "materialized_reads",
                "total_duration_ms",
                "dataloader_wait_ms",
                "cache_wait_ms",
                "materialization_wait_ms",
                "throughput_samples_per_second",
                "summaries",
                "metadata",
                "fingerprint",
            },
            descriptor="DataPathProfile",
        )
        return cls(
            data["profile_id"],  # type: ignore[arg-type]
            loader_state_fingerprint=data["loader_state_fingerprint"],  # type: ignore[arg-type]
            streaming_plan_fingerprint=data["streaming_plan_fingerprint"],  # type: ignore[arg-type]
            sample_count=data["sample_count"],  # type: ignore[arg-type]
            batch_count=data["batch_count"],  # type: ignore[arg-type]
            cache_hits=data["cache_hits"],  # type: ignore[arg-type]
            cache_misses=data["cache_misses"],  # type: ignore[arg-type]
            rereads=data["rereads"],  # type: ignore[arg-type]
            prepared_reads=data["prepared_reads"],  # type: ignore[arg-type]
            materialized_reads=data["materialized_reads"],  # type: ignore[arg-type]
            total_duration_ms=data["total_duration_ms"],  # type: ignore[arg-type]
            dataloader_wait_ms=data["dataloader_wait_ms"],  # type: ignore[arg-type]
            cache_wait_ms=data["cache_wait_ms"],  # type: ignore[arg-type]
            materialization_wait_ms=data["materialization_wait_ms"],  # type: ignore[arg-type]
            throughput_samples_per_second=data["throughput_samples_per_second"],  # type: ignore[arg-type]
            summaries=data["summaries"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


DataPathProfile.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class DataPathBenchmark:
    """Primitive benchmark evidence without thresholds or profiler integration."""

    benchmark_id: str
    profile_fingerprints: tuple[str, ...]
    metric: str
    value: float
    unit: str
    repetitions: int
    measurements: Mapping[str, FrozenPrimitive]
    environment: Mapping[str, FrozenPrimitive]
    limitations: Mapping[str, FrozenPrimitive]
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        benchmark_id: str,
        *,
        profile_fingerprints: Sequence[str],
        metric: str,
        value: float | int,
        unit: str,
        repetitions: int = 1,
        measurements: Mapping[str, object] | None = None,
        environment: Mapping[str, object] | None = None,
        limitations: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "benchmark_id", benchmark_id, owner="DataPathBenchmark")
        object.__setattr__(
            self,
            "profile_fingerprints",
            _coerce_fingerprint_sequence(profile_fingerprints, field="profile_fingerprints"),
        )
        _set_string(self, "metric", metric, owner="DataPathBenchmark")
        _set_non_negative_float(self, "value", value, owner="DataPathBenchmark")
        _set_string(self, "unit", unit, owner="DataPathBenchmark")
        _set_positive_int(self, "repetitions", repetitions, owner="DataPathBenchmark")
        _set_primitive_mapping(self, "measurements", measurements, owner="DataPathBenchmark")
        _set_primitive_mapping(self, "environment", environment, owner="DataPathBenchmark")
        _set_primitive_mapping(self, "limitations", limitations, owner="DataPathBenchmark")
        _set_primitive_mapping(self, "metadata", metadata, owner="DataPathBenchmark")
        _set_fingerprint(self, fingerprint, owner="DataPathBenchmark")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "benchmark_id": self.benchmark_id,
                "profile_fingerprints": list(self.profile_fingerprints),
                "metric": self.metric,
                "value": self.value,
                "unit": self.unit,
                "repetitions": self.repetitions,
                "measurements": dict(self.measurements),
                "environment": dict(self.environment),
                "limitations": dict(self.limitations),
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "DataPathBenchmark":
        data = _require_record(
            value,
            {
                "benchmark_id",
                "profile_fingerprints",
                "metric",
                "value",
                "unit",
                "repetitions",
                "measurements",
                "environment",
                "limitations",
                "metadata",
                "fingerprint",
            },
            descriptor="DataPathBenchmark",
        )
        return cls(
            data["benchmark_id"],  # type: ignore[arg-type]
            profile_fingerprints=data["profile_fingerprints"],  # type: ignore[arg-type]
            metric=data["metric"],  # type: ignore[arg-type]
            value=data["value"],  # type: ignore[arg-type]
            unit=data["unit"],  # type: ignore[arg-type]
            repetitions=data["repetitions"],  # type: ignore[arg-type]
            measurements=data["measurements"],  # type: ignore[arg-type]
            environment=data["environment"],  # type: ignore[arg-type]
            limitations=data["limitations"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


DataPathBenchmark.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class DataPipelineStageContext:
    """Primitive evidence tying one observation to a Stage 9 data-path stage."""

    stage: DataPipelineStage
    status: str
    source_kind: str
    request_fingerprint: str | None
    runtime_context_fingerprint: str | None
    streaming_plan_fingerprint: str | None
    loader_state_fingerprint: str | None
    cache_key_digest: str | None
    cache_status: str | None
    prepared_manifest_fingerprint: str | None
    materialization_fingerprint: str | None
    operation_fingerprint: FrozenPrimitive | None
    batch_operation_name: str | None
    batch_operation_index: int | None
    sample_position: int | None
    batch_index: int | None
    worker_id: int | None
    rank: int | None
    split: str | None
    measurements: Mapping[str, FrozenPrimitive]
    metadata: Mapping[str, FrozenPrimitive]
    provenance: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        stage: DataPipelineStage | str,
        *,
        status: str = "observed",
        source_kind: str = "unknown",
        request_fingerprint: str | None = None,
        runtime_context_fingerprint: str | None = None,
        streaming_plan_fingerprint: str | None = None,
        loader_state_fingerprint: str | None = None,
        cache_key_digest: str | None = None,
        cache_status: str | None = None,
        prepared_manifest_fingerprint: str | None = None,
        materialization_fingerprint: str | None = None,
        operation_fingerprint: object | None = None,
        batch_operation_name: str | None = None,
        batch_operation_index: int | None = None,
        sample_position: int | None = None,
        batch_index: int | None = None,
        worker_id: int | None = None,
        rank: int | None = None,
        split: str | None = None,
        measurements: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        provenance: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        object.__setattr__(self, "stage", DataPipelineStage.coerce(stage))
        object.__setattr__(
            self,
            "status",
            _coerce_choice(
                status,
                owner="DataPipelineStageContext",
                field="status",
                choices={"observed", "skipped", "unavailable", "unsupported", "failed"},
            ),
        )
        object.__setattr__(
            self,
            "source_kind",
            _coerce_choice(
                source_kind,
                owner="DataPipelineStageContext",
                field="source_kind",
                choices={
                    "source",
                    "cache",
                    "prepared",
                    "materialized",
                    "augmentation",
                    "collate",
                    "device_transfer",
                    "loader",
                    "unknown",
                },
            ),
        )
        for field, value in {
            "request_fingerprint": request_fingerprint,
            "runtime_context_fingerprint": runtime_context_fingerprint,
            "streaming_plan_fingerprint": streaming_plan_fingerprint,
            "loader_state_fingerprint": loader_state_fingerprint,
            "cache_key_digest": cache_key_digest,
            "prepared_manifest_fingerprint": prepared_manifest_fingerprint,
            "materialization_fingerprint": materialization_fingerprint,
        }.items():
            _set_optional_fingerprint(self, field, value, owner="DataPipelineStageContext")
        object.__setattr__(
            self,
            "cache_status",
            _coerce_optional_non_empty_string(
                cache_status,
                owner="DataPipelineStageContext",
                field="cache_status",
            ),
        )
        object.__setattr__(
            self,
            "operation_fingerprint",
            _coerce_optional_primitive(
                operation_fingerprint,
                owner="DataPipelineStageContext",
                field="operation_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "batch_operation_name",
            _coerce_optional_non_empty_string(
                batch_operation_name,
                owner="DataPipelineStageContext",
                field="batch_operation_name",
            ),
        )
        for field, value in {
            "batch_operation_index": batch_operation_index,
            "sample_position": sample_position,
            "batch_index": batch_index,
            "worker_id": worker_id,
            "rank": rank,
        }.items():
            _set_optional_non_negative_int(self, field, value, owner="DataPipelineStageContext")
        object.__setattr__(
            self,
            "split",
            _coerce_optional_non_empty_string(split, owner="DataPipelineStageContext", field="split"),
        )
        _set_primitive_mapping(self, "measurements", measurements, owner="DataPipelineStageContext")
        _validate_measurement_units(self.measurements, owner="DataPipelineStageContext")
        _set_primitive_mapping(self, "metadata", metadata, owner="DataPipelineStageContext")
        _set_primitive_mapping(self, "provenance", provenance, owner="DataPipelineStageContext")
        _set_fingerprint(self, fingerprint, owner="DataPipelineStageContext")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "stage": self.stage.value,
                "status": self.status,
                "source_kind": self.source_kind,
                "request_fingerprint": self.request_fingerprint,
                "runtime_context_fingerprint": self.runtime_context_fingerprint,
                "streaming_plan_fingerprint": self.streaming_plan_fingerprint,
                "loader_state_fingerprint": self.loader_state_fingerprint,
                "cache_key_digest": self.cache_key_digest,
                "cache_status": self.cache_status,
                "prepared_manifest_fingerprint": self.prepared_manifest_fingerprint,
                "materialization_fingerprint": self.materialization_fingerprint,
                "operation_fingerprint": self.operation_fingerprint,
                "batch_operation_name": self.batch_operation_name,
                "batch_operation_index": self.batch_operation_index,
                "sample_position": self.sample_position,
                "batch_index": self.batch_index,
                "worker_id": self.worker_id,
                "rank": self.rank,
                "split": self.split,
                "measurements": dict(self.measurements),
                "metadata": dict(self.metadata),
                "provenance": dict(self.provenance),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "DataPipelineStageContext":
        data = _require_record(
            value,
            {
                "stage",
                "status",
                "source_kind",
                "request_fingerprint",
                "runtime_context_fingerprint",
                "streaming_plan_fingerprint",
                "loader_state_fingerprint",
                "cache_key_digest",
                "cache_status",
                "prepared_manifest_fingerprint",
                "materialization_fingerprint",
                "operation_fingerprint",
                "batch_operation_name",
                "batch_operation_index",
                "sample_position",
                "batch_index",
                "worker_id",
                "rank",
                "split",
                "measurements",
                "metadata",
                "provenance",
                "fingerprint",
            },
            descriptor="DataPipelineStageContext",
        )
        return cls(
            data["stage"],  # type: ignore[arg-type]
            status=data["status"],  # type: ignore[arg-type]
            source_kind=data["source_kind"],  # type: ignore[arg-type]
            request_fingerprint=data["request_fingerprint"],  # type: ignore[arg-type]
            runtime_context_fingerprint=data["runtime_context_fingerprint"],  # type: ignore[arg-type]
            streaming_plan_fingerprint=data["streaming_plan_fingerprint"],  # type: ignore[arg-type]
            loader_state_fingerprint=data["loader_state_fingerprint"],  # type: ignore[arg-type]
            cache_key_digest=data["cache_key_digest"],  # type: ignore[arg-type]
            cache_status=data["cache_status"],  # type: ignore[arg-type]
            prepared_manifest_fingerprint=data["prepared_manifest_fingerprint"],  # type: ignore[arg-type]
            materialization_fingerprint=data["materialization_fingerprint"],  # type: ignore[arg-type]
            operation_fingerprint=data["operation_fingerprint"],
            batch_operation_name=data["batch_operation_name"],  # type: ignore[arg-type]
            batch_operation_index=data["batch_operation_index"],  # type: ignore[arg-type]
            sample_position=data["sample_position"],  # type: ignore[arg-type]
            batch_index=data["batch_index"],  # type: ignore[arg-type]
            worker_id=data["worker_id"],  # type: ignore[arg-type]
            rank=data["rank"],  # type: ignore[arg-type]
            split=data["split"],  # type: ignore[arg-type]
            measurements=data["measurements"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            provenance=data["provenance"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


DataPipelineStageContext.__hash__ = None  # type: ignore[assignment]


class DataQualityIssueKind(StrEnum):
    """Data-quality issue vocabulary emitted by fake data-path probes."""

    NAN = "nan"
    INF = "inf"
    MISSING_FIELD = "missing_field"
    INVALID_MASK = "invalid_mask"
    LABEL_DISTRIBUTION = "label_distribution"
    SHAPE_DRIFT = "shape_drift"
    DTYPE_DRIFT = "dtype_drift"
    DEVICE_DRIFT = "device_drift"
    PROVENANCE_ANOMALY = "provenance_anomaly"

    @classmethod
    def coerce(cls, value: "DataQualityIssueKind | str") -> "DataQualityIssueKind":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise FieldTypeError(
                    "Unsupported data-quality issue kind.",
                    field="issue_kind",
                    expected=tuple(kind.value for kind in cls),
                    actual=value,
                ) from exc
        raise FieldTypeError(
            "DataQualityIssueKind must be a DataQualityIssueKind or string.",
            field="issue_kind",
            actual=type(value).__name__,
        )


@dataclass(frozen=True, init=False, slots=True)
class DataQualityProbeResult:
    """Primitive fake-probe evidence for data-path quality diagnostics."""

    probe_id: str
    issue_kind: DataQualityIssueKind
    status: str
    stage: DataPipelineStage
    field: str | None
    count: int
    sample_count: int | None
    observed: FrozenPrimitive | None
    expected: FrozenPrimitive | None
    metadata: Mapping[str, FrozenPrimitive]
    provenance: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        probe_id: str,
        issue_kind: DataQualityIssueKind | str,
        *,
        status: str = "observed",
        stage: DataPipelineStage | str,
        field: str | None = None,
        count: int = 0,
        sample_count: int | None = None,
        observed: object | None = None,
        expected: object | None = None,
        metadata: Mapping[str, object] | None = None,
        provenance: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "probe_id", probe_id, owner="DataQualityProbeResult")
        object.__setattr__(self, "issue_kind", DataQualityIssueKind.coerce(issue_kind))
        object.__setattr__(
            self,
            "status",
            _coerce_choice(
                status,
                owner="DataQualityProbeResult",
                field="status",
                choices={"observed", "passed", "failed", "unavailable"},
            ),
        )
        object.__setattr__(self, "stage", DataPipelineStage.coerce(stage))
        object.__setattr__(
            self,
            "field",
            _coerce_optional_non_empty_string(field, owner="DataQualityProbeResult", field="field"),
        )
        _set_non_negative_int(self, "count", count, owner="DataQualityProbeResult")
        _set_optional_non_negative_int(self, "sample_count", sample_count, owner="DataQualityProbeResult")
        object.__setattr__(
            self,
            "observed",
            _coerce_optional_primitive(observed, owner="DataQualityProbeResult", field="observed"),
        )
        object.__setattr__(
            self,
            "expected",
            _coerce_optional_primitive(expected, owner="DataQualityProbeResult", field="expected"),
        )
        _set_primitive_mapping(self, "metadata", metadata, owner="DataQualityProbeResult")
        _set_primitive_mapping(self, "provenance", provenance, owner="DataQualityProbeResult")
        _set_fingerprint(self, fingerprint, owner="DataQualityProbeResult")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "probe_id": self.probe_id,
                "issue_kind": self.issue_kind.value,
                "status": self.status,
                "stage": self.stage.value,
                "field": self.field,
                "count": self.count,
                "sample_count": self.sample_count,
                "observed": self.observed,
                "expected": self.expected,
                "metadata": dict(self.metadata),
                "provenance": dict(self.provenance),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "DataQualityProbeResult":
        data = _require_record(
            value,
            {
                "probe_id",
                "issue_kind",
                "status",
                "stage",
                "field",
                "count",
                "sample_count",
                "observed",
                "expected",
                "metadata",
                "provenance",
                "fingerprint",
            },
            descriptor="DataQualityProbeResult",
        )
        return cls(
            data["probe_id"],  # type: ignore[arg-type]
            data["issue_kind"],  # type: ignore[arg-type]
            status=data["status"],  # type: ignore[arg-type]
            stage=data["stage"],  # type: ignore[arg-type]
            field=data["field"],  # type: ignore[arg-type]
            count=data["count"],  # type: ignore[arg-type]
            sample_count=data["sample_count"],  # type: ignore[arg-type]
            observed=data["observed"],
            expected=data["expected"],
            metadata=data["metadata"],  # type: ignore[arg-type]
            provenance=data["provenance"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


DataQualityProbeResult.__hash__ = None  # type: ignore[assignment]


class FakeDataQualityProbe:
    """Deterministic data-quality probe over primitive field mappings.

    This fake probe is intentionally dependency-light. It inspects Python
    scalars/sequences and optional primitive field metadata; it does not import
    array, tensor, dataframe, dataset, or video stacks.
    """

    def __init__(
        self,
        probe_id: str,
        *,
        expected_fields: Sequence[str] = (),
        mask_fields: Sequence[str] = (),
        expected_shapes: Mapping[str, object] | None = None,
        expected_dtypes: Mapping[str, object] | None = None,
        expected_devices: Mapping[str, object] | None = None,
        label_field: str | None = None,
        required_provenance: Sequence[str] = (),
    ) -> None:
        self.probe_id = _coerce_non_empty_string(probe_id, owner="FakeDataQualityProbe", field="probe_id")
        self.expected_fields = _coerce_string_tuple(expected_fields, owner="FakeDataQualityProbe", field="expected_fields")
        self.mask_fields = _coerce_string_tuple(mask_fields, owner="FakeDataQualityProbe", field="mask_fields")
        self.expected_shapes = _coerce_primitive_mapping(expected_shapes, owner="FakeDataQualityProbe", field="expected_shapes")
        self.expected_dtypes = _coerce_primitive_mapping(expected_dtypes, owner="FakeDataQualityProbe", field="expected_dtypes")
        self.expected_devices = _coerce_primitive_mapping(expected_devices, owner="FakeDataQualityProbe", field="expected_devices")
        self.label_field = _coerce_optional_non_empty_string(label_field, owner="FakeDataQualityProbe", field="label_field")
        self.required_provenance = _coerce_string_tuple(required_provenance, owner="FakeDataQualityProbe", field="required_provenance")

    def inspect(
        self,
        fields: Mapping[object, object],
        *,
        stage: DataPipelineStage | str,
        field_metadata: Mapping[str, Mapping[str, object]] | None = None,
        provenance: Mapping[str, object] | None = None,
    ) -> tuple[DataQualityProbeResult, ...]:
        """Return primitive quality evidence for one synthetic data observation."""

        if not isinstance(fields, Mapping):
            raise FieldTypeError(
                "FakeDataQualityProbe fields must be a mapping.",
                field="fields",
                actual=type(fields).__name__,
            )
        stage_value = DataPipelineStage.coerce(stage)
        normalized = {str(key): _unwrap_payload(value) for key, value in fields.items()}
        metadata = _coerce_nested_metadata(field_metadata)
        provenance_mapping = _coerce_primitive_mapping(provenance, owner="FakeDataQualityProbe", field="provenance")
        results: list[DataQualityProbeResult] = []

        for field in self.expected_fields:
            if field not in normalized:
                results.append(
                    self._result(
                        DataQualityIssueKind.MISSING_FIELD,
                        stage=stage_value,
                        field=field,
                        count=1,
                        expected="present",
                        provenance=provenance_mapping,
                    )
                )

        for field, value in normalized.items():
            nan_count, inf_count = _count_nan_inf(value)
            if nan_count:
                results.append(
                    self._result(DataQualityIssueKind.NAN, stage=stage_value, field=field, count=nan_count, provenance=provenance_mapping)
                )
            if inf_count:
                results.append(
                    self._result(DataQualityIssueKind.INF, stage=stage_value, field=field, count=inf_count, provenance=provenance_mapping)
                )

        for field in self.mask_fields:
            value = normalized.get(field)
            if value is None or not _is_valid_mask(value):
                results.append(
                    self._result(
                        DataQualityIssueKind.INVALID_MASK,
                        stage=stage_value,
                        field=field,
                        count=1,
                        observed=value,
                        expected="boolean mask",
                        provenance=provenance_mapping,
                    )
                )

        if self.label_field is not None and self.label_field in normalized:
            distribution = dict(sorted(Counter(_iter_labels(normalized[self.label_field])).items()))
            results.append(
                self._result(
                    DataQualityIssueKind.LABEL_DISTRIBUTION,
                    status="observed",
                    stage=stage_value,
                    field=self.label_field,
                    count=len(distribution),
                    sample_count=sum(distribution.values()),
                    observed=distribution,
                    provenance=provenance_mapping,
                )
            )

        for field, expected in self.expected_shapes.items():
            observed = _field_metadata_value(field, "shape", normalized, metadata)
            if observed != expected:
                results.append(self._result(DataQualityIssueKind.SHAPE_DRIFT, stage=stage_value, field=field, count=1, observed=observed, expected=expected, provenance=provenance_mapping))
        for field, expected in self.expected_dtypes.items():
            observed = _field_metadata_value(field, "dtype", normalized, metadata)
            if observed != expected:
                results.append(self._result(DataQualityIssueKind.DTYPE_DRIFT, stage=stage_value, field=field, count=1, observed=observed, expected=expected, provenance=provenance_mapping))
        for field, expected in self.expected_devices.items():
            observed = _field_metadata_value(field, "device", normalized, metadata)
            if observed != expected:
                results.append(self._result(DataQualityIssueKind.DEVICE_DRIFT, stage=stage_value, field=field, count=1, observed=observed, expected=expected, provenance=provenance_mapping))

        missing_provenance = [key for key in self.required_provenance if key not in provenance_mapping]
        if missing_provenance:
            results.append(
                self._result(
                    DataQualityIssueKind.PROVENANCE_ANOMALY,
                    stage=stage_value,
                    count=len(missing_provenance),
                    observed={"missing": missing_provenance},
                    expected="required provenance keys",
                    provenance=provenance_mapping,
                )
            )

        return tuple(results)

    def _result(
        self,
        issue_kind: DataQualityIssueKind,
        *,
        stage: DataPipelineStage,
        status: str = "failed",
        field: str | None = None,
        count: int = 0,
        sample_count: int | None = None,
        observed: object | None = None,
        expected: object | None = None,
        provenance: Mapping[str, object] | None = None,
    ) -> DataQualityProbeResult:
        return DataQualityProbeResult(
            self.probe_id,
            issue_kind,
            status=status,
            stage=stage,
            field=field,
            count=count,
            sample_count=sample_count,
            observed=_thaw_for_probe_record(observed),
            expected=_thaw_for_probe_record(expected),
            provenance=provenance,
            metadata={"fake_probe": True},
        )


def build_data_pipeline_stage_context(
    stage: DataPipelineStage | str,
    *,
    source_kind: str = "unknown",
    request: object | None = None,
    runtime_context: object | None = None,
    streaming_plan: object | None = None,
    loader_state: object | None = None,
    cache_lookup: object | None = None,
    prepared_manifest: object | None = None,
    materialization: object | None = None,
    measurements: Mapping[str, object] | None = None,
    metadata: Mapping[str, object] | None = None,
    provenance: Mapping[str, object] | None = None,
    **overrides: object,
) -> DataPipelineStageContext:
    """Build a stage context from Stage 9 records without owning their runtime."""

    cache_key = getattr(cache_lookup, "key", None)
    context_kwargs: dict[str, object] = {
        "source_kind": source_kind,
        "request_fingerprint": _fingerprint_attr(request),
        "runtime_context_fingerprint": _fingerprint_attr(runtime_context),
        "streaming_plan_fingerprint": _fingerprint_attr(streaming_plan),
        "loader_state_fingerprint": _fingerprint_attr(loader_state),
        "cache_key_digest": getattr(cache_key, "digest", None),
        "cache_status": getattr(cache_lookup, "status", None),
        "prepared_manifest_fingerprint": _fingerprint_attr(prepared_manifest),
        "materialization_fingerprint": _fingerprint_attr(materialization),
        "sample_position": getattr(runtime_context, "position", None),
        "worker_id": getattr(runtime_context, "worker_id", None),
        "rank": getattr(runtime_context, "rank", None),
        "split": getattr(runtime_context, "split", None),
        "measurements": measurements,
        "metadata": metadata,
        "provenance": provenance,
    }
    context_kwargs.update(overrides)
    return DataPipelineStageContext(stage, **context_kwargs)


def build_data_path_profile(
    profile_id: str,
    *,
    loader_state: DataLoaderState | None = None,
    streaming_plan: StreamingReadPlan | None = None,
    stage_contexts: Sequence[DataPipelineStageContext] = (),
    measurements: Mapping[str, object] | None = None,
    summaries: Mapping[str, object] | None = None,
    metadata: Mapping[str, object] | None = None,
    total_duration_ms: float | int | None = None,
    dataloader_wait_ms: float | int | None = None,
    cache_wait_ms: float | int | None = None,
    materialization_wait_ms: float | int | None = None,
    throughput_samples_per_second: float | int | None = None,
) -> DataPathProfile:
    """Create `DataPathProfile` evidence from Stage 9 state plus stage contexts."""

    contexts = _coerce_stage_contexts(stage_contexts)
    measurement_map = _coerce_primitive_mapping(measurements, owner="build_data_path_profile", field="measurements")
    _validate_measurement_units(measurement_map, owner="build_data_path_profile")
    summary_map: dict[str, object] = {} if summaries is None else dict(summaries)
    if contexts:
        summary_map.setdefault("pipeline_stages", [context.stage.value for context in contexts])
        summary_map.setdefault("stage_context_fingerprints", [context.fingerprint for context in contexts])
        summary_map.setdefault("source_kinds", sorted({context.source_kind for context in contexts}))
    if measurement_map:
        summary_map.setdefault("measurements", dict(measurement_map))
        summary_map.setdefault("measurement_units", dict(DATA_PATH_MEASUREMENT_UNITS))
    metadata_map: dict[str, object] = {} if metadata is None else dict(metadata)
    metadata_map.setdefault("stage15_profile_builder", True)
    return DataPathProfile(
        profile_id,
        loader_state_fingerprint=None if loader_state is None else loader_state.fingerprint,
        streaming_plan_fingerprint=None if streaming_plan is None else streaming_plan.fingerprint,
        sample_count=0 if loader_state is None else loader_state.positions_seen,
        batch_count=0 if loader_state is None else loader_state.batch_count,
        cache_hits=0 if loader_state is None else loader_state.cache_hits,
        cache_misses=0 if loader_state is None else loader_state.cache_misses,
        rereads=0 if loader_state is None else loader_state.rereads,
        prepared_reads=0 if loader_state is None else loader_state.prepared_reads,
        materialized_reads=0 if loader_state is None else loader_state.materialized_reads,
        total_duration_ms=total_duration_ms,
        dataloader_wait_ms=dataloader_wait_ms,
        cache_wait_ms=cache_wait_ms,
        materialization_wait_ms=materialization_wait_ms,
        throughput_samples_per_second=throughput_samples_per_second,
        summaries=summary_map,
        metadata=metadata_map,
    )


def build_data_path_benchmark(
    benchmark_id: str,
    *,
    profiles: Sequence[DataPathProfile],
    metric: str = "throughput.samples_per_second",
    value: float | int | None = None,
    unit: str | None = None,
    repetitions: int = 1,
    measurements: Mapping[str, object] | None = None,
    environment: Mapping[str, object] | None = None,
    limitations: Mapping[str, object] | None = None,
    metadata: Mapping[str, object] | None = None,
) -> DataPathBenchmark:
    """Create threshold-free benchmark evidence over existing profiles."""

    if isinstance(profiles, (str, bytes)) or not profiles:
        raise FieldTypeError(
            "build_data_path_benchmark profiles must be a non-empty sequence.",
            field="profiles",
            actual=type(profiles).__name__,
        )
    for profile in profiles:
        if not isinstance(profile, DataPathProfile):
            raise FieldTypeError(
                "build_data_path_benchmark profiles must contain DataPathProfile records.",
                field="profiles",
                actual=type(profile).__name__,
            )
    measurement_map = _coerce_primitive_mapping(measurements, owner="build_data_path_benchmark", field="measurements")
    _validate_measurement_units(measurement_map, owner="build_data_path_benchmark")
    resolved_value = value
    if resolved_value is None:
        if metric in measurement_map and isinstance(measurement_map[metric], (int, float)):
            resolved_value = measurement_map[metric]
        elif metric == "throughput.samples_per_second" and profiles[0].throughput_samples_per_second is not None:
            resolved_value = profiles[0].throughput_samples_per_second
        else:
            raise FieldTypeError(
                "build_data_path_benchmark value is required when it cannot be derived from measurements or profiles.",
                field="value",
                metric=metric,
            )
    metadata_map: dict[str, object] = {} if metadata is None else dict(metadata)
    metadata_map.setdefault("stage15_benchmark_builder", True)
    limitation_map: dict[str, object] = {"thresholds_claimed": False}
    if limitations is not None:
        limitation_map.update(limitations)
    return DataPathBenchmark(
        benchmark_id,
        profile_fingerprints=[profile.fingerprint for profile in profiles],
        metric=metric,
        value=resolved_value,
        unit=unit or DATA_PATH_MEASUREMENT_UNITS.get(metric, "unknown"),
        repetitions=repetitions,
        measurements=measurement_map,
        environment=environment,
        limitations=limitation_map,
        metadata=metadata_map,
    )


def _validate_measurement_units(measurements: Mapping[str, object], *, owner: str) -> None:
    for key, value in measurements.items():
        if key not in DATA_PATH_MEASUREMENT_UNITS:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise FieldTypeError(
                f"{owner} reserved measurement values must be numeric.",
                owner=owner,
                field=key,
                expected="non-negative finite number",
                actual=type(value).__name__,
            )
        _coerce_non_negative_float(value, owner=owner, field=key)


def _coerce_stage_contexts(values: Sequence[DataPipelineStageContext]) -> tuple[DataPipelineStageContext, ...]:
    if isinstance(values, (str, bytes)):
        raise FieldTypeError(
            "stage_contexts must be a sequence of DataPipelineStageContext records.",
            field="stage_contexts",
            actual=type(values).__name__,
        )
    try:
        contexts = tuple(values)
    except TypeError as exc:
        raise FieldTypeError(
            "stage_contexts must be a sequence of DataPipelineStageContext records.",
            field="stage_contexts",
            actual=type(values).__name__,
        ) from exc
    for context in contexts:
        if not isinstance(context, DataPipelineStageContext):
            raise FieldTypeError(
                "stage_contexts must contain DataPipelineStageContext records.",
                field="stage_contexts",
                actual=type(context).__name__,
            )
    return contexts


def _fingerprint_attr(value: object | None) -> str | None:
    if value is None:
        return None
    fingerprint = getattr(value, "fingerprint", None)
    if fingerprint is None:
        return None
    return _coerce_fingerprint(fingerprint, owner=type(value).__name__, field="fingerprint")


def _coerce_optional_non_empty_string(
    value: object | None,
    *,
    owner: str,
    field: str,
) -> str | None:
    if value is None:
        return None
    return _coerce_non_empty_string(value, owner=owner, field=field)


def _coerce_string_tuple(values: Sequence[str], *, owner: str, field: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise FieldTypeError(
            f"{owner} {field} must be a sequence of strings.",
            owner=owner,
            field=field,
            actual=type(values).__name__,
        )
    try:
        items = tuple(values)
    except TypeError as exc:
        raise FieldTypeError(
            f"{owner} {field} must be a sequence of strings.",
            owner=owner,
            field=field,
            actual=type(values).__name__,
        ) from exc
    return tuple(_coerce_non_empty_string(item, owner=owner, field=field) for item in items)


def _coerce_nested_metadata(
    value: Mapping[str, Mapping[str, object]] | None,
) -> dict[str, dict[str, FrozenPrimitive]]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise FieldTypeError(
            "FakeDataQualityProbe field_metadata must be a mapping.",
            field="field_metadata",
            actual=type(value).__name__,
        )
    output: dict[str, dict[str, FrozenPrimitive]] = {}
    for field, metadata in value.items():
        field_name = _coerce_non_empty_string(field, owner="FakeDataQualityProbe", field="field_metadata key")
        if not isinstance(metadata, Mapping):
            raise FieldTypeError(
                "FakeDataQualityProbe field metadata values must be mappings.",
                field=field_name,
                actual=type(metadata).__name__,
            )
        output[field_name] = _coerce_primitive_mapping(
            metadata,
            owner="FakeDataQualityProbe",
            field=f"field_metadata[{field_name}]",
        )
    return output


def _unwrap_payload(value: object) -> object:
    return getattr(value, "payload", value)


def _count_nan_inf(value: object) -> tuple[int, int]:
    nan_count = 0
    inf_count = 0
    for item in _walk_values(value):
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            continue
        if math.isnan(float(item)):
            nan_count += 1
        elif math.isinf(float(item)):
            inf_count += 1
    return nan_count, inf_count


def _walk_values(value: object) -> Iterable[object]:
    if isinstance(value, Mapping):
        for item in value.values():
            yield from _walk_values(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk_values(item)
        return
    yield value


def _is_valid_mask(value: object) -> bool:
    items = tuple(_walk_values(value))
    return bool(items) and all(type(item) is bool for item in items)


def _iter_labels(value: object) -> Iterable[str]:
    if isinstance(value, (list, tuple)):
        for item in value:
            yield str(item)
        return
    yield str(value)


def _field_metadata_value(
    field: str,
    key: str,
    values: Mapping[str, object],
    metadata: Mapping[str, Mapping[str, object]],
) -> object | None:
    if field in metadata and key in metadata[field]:
        return metadata[field][key]
    value = values.get(field)
    if value is None:
        return None
    if key == "shape":
        shape = getattr(value, "shape", None)
        if shape is not None:
            try:
                return list(shape)
            except TypeError:
                return str(shape)
        if isinstance(value, (list, tuple)):
            return [len(value)]
    attr = getattr(value, key, None)
    if attr is not None:
        return str(attr)
    if key == "dtype":
        return type(value).__name__
    return None


def _thaw_for_probe_record(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _thaw_for_probe_record(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_for_probe_record(item) for item in value]
    if isinstance(value, list):
        return [_thaw_for_probe_record(item) for item in value]
    return value


def _record_dict(
    payload: dict[str, object],
    record: object,
    *,
    include_fingerprint: bool,
) -> dict[str, object]:
    serialized = {key: _to_jsonable(value) for key, value in payload.items()}
    if include_fingerprint:
        return {**serialized, "fingerprint": getattr(record, "fingerprint")}
    return serialized


def _require_record(
    value: object,
    keys: set[str],
    *,
    descriptor: str,
) -> Mapping[str, object]:
    data = _require_mapping(value, field=descriptor)
    _require_keys(data, keys, descriptor=descriptor)
    return data


def _set_string(record: object, field: str, value: object, *, owner: str) -> None:
    object.__setattr__(
        record,
        field,
        _coerce_non_empty_string(value, owner=owner, field=field),
    )


def _set_non_negative_int(record: object, field: str, value: object, *, owner: str) -> None:
    object.__setattr__(
        record,
        field,
        _coerce_non_negative_int(value, owner=owner, field=field),
    )


def _set_positive_int(record: object, field: str, value: object, *, owner: str) -> None:
    resolved = _coerce_non_negative_int(value, owner=owner, field=field)
    if resolved == 0:
        raise FieldTypeError(
            f"{owner} {field} must be positive.",
            owner=owner,
            field=field,
            actual=resolved,
        )
    object.__setattr__(record, field, resolved)


def _set_optional_non_negative_int(
    record: object,
    field: str,
    value: object | None,
    *,
    owner: str,
) -> None:
    if value is None:
        object.__setattr__(record, field, None)
        return
    _set_non_negative_int(record, field, value, owner=owner)


def _set_optional_positive_int(
    record: object,
    field: str,
    value: object | None,
    *,
    owner: str,
) -> None:
    if value is None:
        object.__setattr__(record, field, None)
        return
    _set_positive_int(record, field, value, owner=owner)


def _set_non_negative_float(record: object, field: str, value: object, *, owner: str) -> None:
    object.__setattr__(
        record,
        field,
        _coerce_non_negative_float(value, owner=owner, field=field),
    )


def _set_optional_non_negative_float(
    record: object,
    field: str,
    value: object | None,
    *,
    owner: str,
) -> None:
    if value is None:
        object.__setattr__(record, field, None)
        return
    _set_non_negative_float(record, field, value, owner=owner)


def _set_optional_fingerprint(
    record: object,
    field: str,
    value: object | None,
    *,
    owner: str,
) -> None:
    if value is None:
        object.__setattr__(record, field, None)
        return
    object.__setattr__(record, field, _coerce_fingerprint(value, owner=owner, field=field))


def _set_primitive_mapping(
    record: object,
    field: str,
    value: Mapping[str, object] | None,
    *,
    owner: str,
) -> None:
    object.__setattr__(
        record,
        field,
        MappingProxyType(_coerce_primitive_mapping(value, owner=owner, field=field)),
    )


def _set_fingerprint(record: object, value: str | None, *, owner: str) -> None:
    to_dict = getattr(record, "to_dict")
    expected = _sha256(to_dict(include_fingerprint=False))
    resolved = value or expected
    _validate_fingerprint(resolved, expected=expected, descriptor=owner)
    object.__setattr__(record, "fingerprint", resolved)


def _coerce_choice(
    value: object,
    *,
    owner: str,
    field: str,
    choices: set[str],
) -> str:
    text = _coerce_non_empty_string(value, owner=owner, field=field)
    if text not in choices:
        raise FieldTypeError(
            f"{owner} {field} is unsupported.",
            field=field,
            expected=sorted(choices),
            actual=text,
        )
    return text


def _coerce_coordination(value: object, *, owner: str) -> str:
    return _coerce_choice(
        value,
        owner=owner,
        field="distributed_coordination",
        choices={"none", "unstable"},
    )


def _coerce_position_sequence(values: Sequence[int], *, field: str) -> tuple[int, ...]:
    positions = _coerce_int_sequence(values, field=field)
    _require_unique_values((str(position) for position in positions), field=field)
    return positions


def _coerce_fingerprint_sequence(values: Sequence[str], *, field: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise FieldTypeError(
            f"{field} must be a sequence of fingerprints.",
            field=field,
            actual=type(values).__name__,
        )
    try:
        fingerprints = tuple(values)
    except TypeError as exc:
        raise FieldTypeError(
            f"{field} must be a sequence of fingerprints.",
            field=field,
            actual=type(values).__name__,
        ) from exc
    if not fingerprints:
        raise FieldTypeError(f"{field} must not be empty.", field=field)
    for fingerprint in fingerprints:
        _coerce_fingerprint(fingerprint, owner="DataPathBenchmark", field=field)
    _require_unique_values(fingerprints, field=field)
    return fingerprints


def _coerce_int_sequence(values: Sequence[int], *, field: str) -> tuple[int, ...]:
    if isinstance(values, (str, bytes)):
        raise FieldTypeError(
            f"{field} must be a sequence of non-negative integers.",
            field=field,
            actual=type(values).__name__,
        )
    try:
        items = tuple(values)
    except TypeError as exc:
        raise FieldTypeError(
            f"{field} must be a sequence of non-negative integers.",
            field=field,
            actual=type(values).__name__,
        ) from exc
    return tuple(_coerce_non_negative_int(item, owner=field, field=field) for item in items)


def _require_unique_values(values: Iterable[str], *, field: str) -> None:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen:
            duplicates.append(value)
        seen.add(value)
    if duplicates:
        raise FieldTypeError(
            "Descriptor values must be unique.",
            field=field,
            duplicates=sorted(duplicates),
        )


def _validate_streaming_read_plan(plan: StreamingReadPlan) -> None:
    if plan.stop_position is not None and plan.stop_position <= plan.start_position:
        raise RemotePhysDataSourceError(
            "StreamingReadPlan stop_position must be greater than start_position.",
            field="stop_position",
            start_position=plan.start_position,
            stop_position=plan.stop_position,
        )
    if plan.sample_count is not None:
        if plan.start_position >= plan.sample_count:
            raise RemotePhysDataSourceError(
                "StreamingReadPlan start_position must be inside sample_count.",
                field="start_position",
                sample_count=plan.sample_count,
                start_position=plan.start_position,
            )
        if plan.stop_position is not None and plan.stop_position > plan.sample_count:
            raise RemotePhysDataSourceError(
                "StreamingReadPlan stop_position must not exceed sample_count.",
                field="stop_position",
                sample_count=plan.sample_count,
                stop_position=plan.stop_position,
            )
        out_of_range = [
            position
            for position in plan.skip_positions
            if position >= plan.sample_count
        ]
        if out_of_range:
            raise RemotePhysDataSourceError(
                "StreamingReadPlan skip_positions must be inside sample_count.",
                field="skip_positions",
                sample_count=plan.sample_count,
                positions=out_of_range,
            )
    if plan.stop_position is not None:
        outside_window = [
            position
            for position in plan.skip_positions
            if position < plan.start_position or position >= plan.stop_position
        ]
        if outside_window:
            raise RemotePhysDataSourceError(
                "StreamingReadPlan skip_positions must fit within the requested window.",
                field="skip_positions",
                start_position=plan.start_position,
                stop_position=plan.stop_position,
                positions=outside_window,
            )


def _coerce_non_negative_int(value: object, *, owner: str, field: str) -> int:
    if type(value) is not int:
        raise FieldTypeError(
            f"{owner} {field} must be a non-boolean integer.",
            owner=owner,
            field=field,
            expected="non-negative int",
            actual=type(value).__name__,
        )
    if value < 0:
        raise FieldTypeError(
            f"{owner} {field} must be non-negative.",
            owner=owner,
            field=field,
            actual=value,
        )
    return value


def _coerce_non_negative_float(value: object, *, owner: str, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FieldTypeError(
            f"{owner} {field} must be a non-negative finite number.",
            owner=owner,
            field=field,
            expected="non-negative finite number",
            actual=type(value).__name__,
        )
    resolved = float(value)
    if not math.isfinite(resolved) or resolved < 0:
        raise FieldTypeError(
            f"{owner} {field} must be non-negative and finite.",
            owner=owner,
            field=field,
            actual=value,
        )
    return resolved


def _coerce_non_empty_string(value: object, *, owner: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise FieldTypeError(
            f"{owner} {field} must be a non-empty string.",
            owner=owner,
            field=field,
            actual=type(value).__name__,
        )
    return value


def _coerce_fingerprint(value: object, *, owner: str, field: str) -> str:
    text = _coerce_non_empty_string(value, owner=owner, field=field)
    if len(text) != 64:
        raise FieldTypeError(
            f"{owner} {field} must be a 64-character fingerprint.",
            owner=owner,
            field=field,
            actual=text,
        )
    return text


def _validate_fingerprint(
    value: object,
    *,
    expected: str,
    descriptor: str,
) -> None:
    actual = _coerce_fingerprint(value, owner=descriptor, field="fingerprint")
    if actual != expected:
        raise RemotePhysDataSourceError(
            f"{descriptor} fingerprint mismatch.",
            field="fingerprint",
            expected=expected,
            actual=actual,
        )


def _coerce_optional_primitive(
    value: object | None,
    *,
    owner: str,
    field: str,
) -> FrozenPrimitive | None:
    if value is None:
        return None
    return freeze_primitive(value, error_type=FieldTypeError, field=f"{owner}.{field}")


def _coerce_primitive_mapping(
    value: Mapping[str, object] | None,
    *,
    owner: str,
    field: str,
) -> dict[str, FrozenPrimitive]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise FieldTypeError(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            actual=type(value).__name__,
        )
    output: dict[str, FrozenPrimitive] = {}
    for key, item in value.items():
        output[_coerce_non_empty_string(key, owner=owner, field=f"{field} key")] = (
            freeze_primitive(
                item,
                error_type=FieldTypeError,
                field=f"{owner}.{field}[{key}]",
            )
        )
    return output


def _require_mapping(value: object, *, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise RemotePhysDataSourceError(
            "Serialized data-path descriptors must be mappings.",
            field=field,
            actual=type(value).__name__,
        )
    return value


def _require_keys(
    value: Mapping[str, object],
    keys: set[str],
    *,
    descriptor: str,
) -> None:
    actual = set(value)
    if actual != keys:
        raise RemotePhysDataSourceError(
            "Serialized data-path descriptor keys do not match the schema.",
            descriptor=descriptor,
            expected=sorted(keys),
            actual=sorted(actual),
        )


def _canonical_json(value: object) -> str:
    return json.dumps(_to_jsonable(value), sort_keys=True, separators=(",", ":"))


def _to_jsonable(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()
