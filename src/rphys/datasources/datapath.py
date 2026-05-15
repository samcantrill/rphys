"""Descriptor-only data-path evidence records for Stage 9.

These public provisional records make loader/cache/prepared/materialization
evidence inspectable without implementing streaming, profiling, benchmarking,
trainer, device, model-formatting, or distributed runtime behavior.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from rphys.errors import FieldTypeError, RemotePhysDataSourceError
from rphys.io._primitives import FrozenPrimitive, freeze_primitive

__all__ = [
    "StreamingReadPlan",
    "DataLoaderState",
    "DataPathProfile",
    "DataPathBenchmark",
]


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
