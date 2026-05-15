"""Prepared-data manifests and provisional reader boundary for sample sources.

Stage 9 prepared data is an immutable equivalence contract, not a storage
backend. This module records primitive manifest evidence and defines a public
provisional ``PreparedSampleReader`` protocol that backend-specific readers can
implement without making backend details part of rphys domain semantics.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Protocol, runtime_checkable

from rphys.data.containers import Sample
from rphys.data.locators import FieldLocator
from rphys.datasources.sources import (
    SampleRequest,
    SampleRequestLike,
    SampleRuntimeContext,
    SampleSource,
)
from rphys.errors import FieldTypeError, RemotePhysDataSourceError
from rphys.io._primitives import FrozenPrimitive, freeze_primitive

__all__ = [
    "PreparedField",
    "PreparedDataManifest",
    "PreparedReadRequest",
    "PreparedReadResult",
    "PreparedSampleReader",
    "PreparedSampleSource",
    "OptimizedStorageFormat",
    "OptimizedDataPlan",
    "MaterializationPlan",
    "MaterializationManifest",
    "ShardManifest",
    "ChunkMetadata",
    "AccessPatternPlan",
    "RecordLayoutMetadata",
    "BatchCostMetadata",
    "BatchSamplerPlan",
    "BatchShapePolicy",
]

_PREPARED_MANIFEST_SCHEMA_VERSION = 1


@dataclass(frozen=True, init=False, slots=True)
class PreparedField:
    """Primitive descriptor for one field in a prepared product."""

    locator: FieldLocator
    schema: str | None
    dtype: str | None
    shape: tuple[int | None, ...] | None
    unit: str | None
    checksum: str | None
    layout: Mapping[str, FrozenPrimitive]
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        locator: FieldLocator | str,
        *,
        schema: str | None = None,
        dtype: str | None = None,
        shape: Sequence[int | None] | None = None,
        unit: str | None = None,
        checksum: str | None = None,
        layout: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        object.__setattr__(self, "locator", _coerce_locator(locator))
        object.__setattr__(
            self,
            "schema",
            _coerce_optional_non_empty_string(
                schema,
                owner="PreparedField",
                field="schema",
            ),
        )
        object.__setattr__(
            self,
            "dtype",
            _coerce_optional_non_empty_string(
                dtype,
                owner="PreparedField",
                field="dtype",
            ),
        )
        object.__setattr__(
            self,
            "shape",
            _coerce_optional_shape(shape),
        )
        object.__setattr__(
            self,
            "unit",
            _coerce_optional_non_empty_string(
                unit,
                owner="PreparedField",
                field="unit",
            ),
        )
        object.__setattr__(
            self,
            "checksum",
            _coerce_optional_non_empty_string(
                checksum,
                owner="PreparedField",
                field="checksum",
            ),
        )
        object.__setattr__(
            self,
            "layout",
            MappingProxyType(
                _coerce_primitive_mapping(
                    layout,
                    owner="PreparedField",
                    field="layout",
                )
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                _coerce_primitive_mapping(
                    metadata,
                    owner="PreparedField",
                    field="metadata",
                )
            ),
        )
        object.__setattr__(
            self,
            "fingerprint",
            _sha256(self.to_dict(include_fingerprint=False)),
        )

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        payload: dict[str, object] = {
            "locator": str(self.locator),
            "schema": self.schema,
            "dtype": self.dtype,
            "shape": None if self.shape is None else list(self.shape),
            "unit": self.unit,
            "checksum": self.checksum,
            "layout": dict(self.layout),
            "metadata": dict(self.metadata),
        }
        if include_fingerprint:
            payload["fingerprint"] = self.fingerprint
        return payload

    @classmethod
    def from_dict(cls, value: object) -> "PreparedField":
        data = _require_mapping(value, field="field")
        _require_keys(
            data,
            {
                "locator",
                "schema",
                "dtype",
                "shape",
                "unit",
                "checksum",
                "layout",
                "metadata",
                "fingerprint",
            },
            descriptor="PreparedField",
        )
        field = cls(
            data["locator"],  # type: ignore[arg-type]
            schema=data["schema"],  # type: ignore[arg-type]
            dtype=data["dtype"],  # type: ignore[arg-type]
            shape=data["shape"],  # type: ignore[arg-type]
            unit=data["unit"],  # type: ignore[arg-type]
            checksum=data["checksum"],  # type: ignore[arg-type]
            layout=data["layout"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
        )
        _validate_fingerprint(
            data["fingerprint"],
            expected=field.fingerprint,
            descriptor="PreparedField",
        )
        return field


PreparedField.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class PreparedDataManifest:
    """Versioned primitive equivalence record for an immutable prepared product."""

    schema_version: int
    manifest_id: str
    backend_id: str
    index_id: str
    datasource_id: str
    source_id: str | None
    sample_count: int
    request_fingerprint: str
    operation_fingerprint: FrozenPrimitive | None
    materialization_fingerprint: FrozenPrimitive | None
    fields: tuple[PreparedField, ...]
    split_counts: Mapping[str, int]
    group_counts: Mapping[str, int]
    checksums: Mapping[str, FrozenPrimitive]
    layout: Mapping[str, FrozenPrimitive]
    cost: Mapping[str, FrozenPrimitive]
    runtime: Mapping[str, FrozenPrimitive]
    invalidation: Mapping[str, FrozenPrimitive]
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        *,
        manifest_id: str,
        backend_id: str,
        index_id: str,
        datasource_id: str,
        sample_count: int,
        request_fingerprint: str,
        fields: Sequence[PreparedField],
        source_id: str | None = None,
        operation_fingerprint: object | None = None,
        materialization_fingerprint: object | None = None,
        split_counts: Mapping[str, int] | None = None,
        group_counts: Mapping[str, int] | None = None,
        checksums: Mapping[str, object] | None = None,
        layout: Mapping[str, object] | None = None,
        cost: Mapping[str, object] | None = None,
        runtime: Mapping[str, object] | None = None,
        invalidation: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        schema_version: int = _PREPARED_MANIFEST_SCHEMA_VERSION,
        fingerprint: str | None = None,
    ) -> None:
        object.__setattr__(self, "schema_version", _coerce_schema_version(schema_version))
        object.__setattr__(
            self,
            "manifest_id",
            _coerce_non_empty_string(
                manifest_id,
                owner="PreparedDataManifest",
                field="manifest_id",
            ),
        )
        object.__setattr__(
            self,
            "backend_id",
            _coerce_non_empty_string(
                backend_id,
                owner="PreparedDataManifest",
                field="backend_id",
            ),
        )
        object.__setattr__(
            self,
            "index_id",
            _coerce_non_empty_string(
                index_id,
                owner="PreparedDataManifest",
                field="index_id",
            ),
        )
        object.__setattr__(
            self,
            "datasource_id",
            _coerce_non_empty_string(
                datasource_id,
                owner="PreparedDataManifest",
                field="datasource_id",
            ),
        )
        object.__setattr__(
            self,
            "source_id",
            _coerce_optional_non_empty_string(
                source_id,
                owner="PreparedDataManifest",
                field="source_id",
            ),
        )
        object.__setattr__(
            self,
            "sample_count",
            _coerce_non_negative_int(
                sample_count,
                owner="PreparedDataManifest",
                field="sample_count",
            ),
        )
        object.__setattr__(
            self,
            "request_fingerprint",
            _coerce_fingerprint(
                request_fingerprint,
                owner="PreparedDataManifest",
                field="request_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "operation_fingerprint",
            _coerce_optional_primitive(
                operation_fingerprint,
                owner="PreparedDataManifest",
                field="operation_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "materialization_fingerprint",
            _coerce_optional_primitive(
                materialization_fingerprint,
                owner="PreparedDataManifest",
                field="materialization_fingerprint",
            ),
        )
        object.__setattr__(self, "fields", _coerce_prepared_fields(fields))
        object.__setattr__(
            self,
            "split_counts",
            MappingProxyType(
                _coerce_count_mapping(
                    split_counts,
                    owner="PreparedDataManifest",
                    field="split_counts",
                )
            ),
        )
        object.__setattr__(
            self,
            "group_counts",
            MappingProxyType(
                _coerce_count_mapping(
                    group_counts,
                    owner="PreparedDataManifest",
                    field="group_counts",
                )
            ),
        )
        for field_name, value in {
            "checksums": checksums,
            "layout": layout,
            "cost": cost,
            "runtime": runtime,
            "invalidation": invalidation,
            "metadata": metadata,
        }.items():
            object.__setattr__(
                self,
                field_name,
                MappingProxyType(
                    _coerce_primitive_mapping(
                        value,
                        owner="PreparedDataManifest",
                        field=field_name,
                    )
                ),
            )
        resolved_fingerprint = fingerprint or _sha256(self.to_dict(include_fingerprint=False))
        _validate_fingerprint(
            resolved_fingerprint,
            expected=_sha256(self.to_dict(include_fingerprint=False)),
            descriptor="PreparedDataManifest",
        )
        object.__setattr__(self, "fingerprint", resolved_fingerprint)

    @property
    def field_locators(self) -> tuple[FieldLocator, ...]:
        """Prepared field locators in manifest order."""

        return tuple(field.locator for field in self.fields)

    def validate_request_context(
        self,
        request: SampleRequest,
        context: SampleRuntimeContext,
        *,
        position: int | None = None,
    ) -> None:
        """Raise when request/context evidence does not match this manifest."""

        if not isinstance(request, SampleRequest):
            raise FieldTypeError(
                "PreparedDataManifest request must be a SampleRequest.",
                field="request",
                actual=type(request).__name__,
            )
        if not isinstance(context, SampleRuntimeContext):
            raise FieldTypeError(
                "PreparedDataManifest context must be a SampleRuntimeContext.",
                field="context",
                actual=type(context).__name__,
            )
        mismatches: dict[str, object] = {}
        expected_position = context.position if position is None else position
        expected: dict[str, object] = {
            "context_request_fingerprint": request.fingerprint,
            "index_id": self.index_id,
            "datasource_id": self.datasource_id,
            "position": expected_position,
        }
        actual: dict[str, object] = {
            "context_request_fingerprint": context.request_fingerprint,
            "index_id": context.index_id,
            "datasource_id": context.datasource_id,
            "position": context.position,
        }
        if not self._request_compatible(request):
            mismatches["request_fingerprint"] = {
                "expected": self.request_fingerprint,
                "actual": request.fingerprint,
            }
        if self.source_id is not None:
            expected["source_id"] = self.source_id
            actual["source_id"] = context.source_id
        for field, expected_value in expected.items():
            if actual[field] != expected_value:
                mismatches[field] = {
                    "expected": _to_jsonable(expected_value),
                    "actual": _to_jsonable(actual[field]),
                }
        if mismatches:
            raise RemotePhysDataSourceError(
                "Prepared manifest evidence does not match the requested sample.",
                field="manifest",
                mismatches=mismatches,
            )

    def expected_locators(self, request: SampleRequest) -> tuple[FieldLocator, ...]:
        if request.requested is None:
            return self.field_locators
        missing = [
            str(locator)
            for locator in request.requested
            if locator not in self.field_locators
        ]
        if missing:
            raise RemotePhysDataSourceError(
                "Prepared manifest does not contain requested fields.",
                field="request",
                missing=missing,
            )
        return request.requested

    def _request_compatible(self, request: SampleRequest) -> bool:
        if self.request_fingerprint == request.fingerprint:
            return True
        if self.request_fingerprint != SampleRequest().fingerprint:
            return False
        if request.requested is None:
            return True
        return all(locator in self.field_locators for locator in request.requested)

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema_version": self.schema_version,
            "manifest_id": self.manifest_id,
            "backend_id": self.backend_id,
            "index_id": self.index_id,
            "datasource_id": self.datasource_id,
            "source_id": self.source_id,
            "sample_count": self.sample_count,
            "request_fingerprint": self.request_fingerprint,
            "operation_fingerprint": self.operation_fingerprint,
            "materialization_fingerprint": self.materialization_fingerprint,
            "fields": [field.to_dict() for field in self.fields],
            "split_counts": dict(self.split_counts),
            "group_counts": dict(self.group_counts),
            "checksums": dict(self.checksums),
            "layout": dict(self.layout),
            "cost": dict(self.cost),
            "runtime": dict(self.runtime),
            "invalidation": dict(self.invalidation),
            "metadata": dict(self.metadata),
        }
        if include_fingerprint:
            payload["fingerprint"] = self.fingerprint
        return payload

    @classmethod
    def from_dict(cls, value: object) -> "PreparedDataManifest":
        data = _require_mapping(value, field="manifest")
        _require_keys(
            data,
            {
                "schema_version",
                "manifest_id",
                "backend_id",
                "index_id",
                "datasource_id",
                "source_id",
                "sample_count",
                "request_fingerprint",
                "operation_fingerprint",
                "materialization_fingerprint",
                "fields",
                "split_counts",
                "group_counts",
                "checksums",
                "layout",
                "cost",
                "runtime",
                "invalidation",
                "metadata",
                "fingerprint",
            },
            descriptor="PreparedDataManifest",
        )
        return cls(
            manifest_id=data["manifest_id"],  # type: ignore[arg-type]
            backend_id=data["backend_id"],  # type: ignore[arg-type]
            index_id=data["index_id"],  # type: ignore[arg-type]
            datasource_id=data["datasource_id"],  # type: ignore[arg-type]
            source_id=data["source_id"],  # type: ignore[arg-type]
            sample_count=data["sample_count"],  # type: ignore[arg-type]
            request_fingerprint=data["request_fingerprint"],  # type: ignore[arg-type]
            operation_fingerprint=data["operation_fingerprint"],
            materialization_fingerprint=data["materialization_fingerprint"],
            fields=[
                PreparedField.from_dict(item)
                for item in _require_sequence(data["fields"], field="fields")
            ],
            split_counts=data["split_counts"],  # type: ignore[arg-type]
            group_counts=data["group_counts"],  # type: ignore[arg-type]
            checksums=data["checksums"],  # type: ignore[arg-type]
            layout=data["layout"],  # type: ignore[arg-type]
            cost=data["cost"],  # type: ignore[arg-type]
            runtime=data["runtime"],  # type: ignore[arg-type]
            invalidation=data["invalidation"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            schema_version=data["schema_version"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


PreparedDataManifest.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class PreparedReadRequest:
    """One-position read request handed to a prepared backend reader."""

    position: int
    request: SampleRequest
    context: SampleRuntimeContext
    manifest_fingerprint: str
    metadata: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        *,
        position: int,
        request: SampleRequest,
        context: SampleRuntimeContext,
        manifest_fingerprint: str,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        source_position = _coerce_non_negative_int(
            position,
            owner="PreparedReadRequest",
            field="position",
        )
        if not isinstance(request, SampleRequest):
            raise FieldTypeError(
                "PreparedReadRequest request must be a SampleRequest.",
                field="request",
                actual=type(request).__name__,
            )
        if not isinstance(context, SampleRuntimeContext):
            raise FieldTypeError(
                "PreparedReadRequest context must be a SampleRuntimeContext.",
                field="context",
                actual=type(context).__name__,
            )
        if context.position != source_position:
            raise RemotePhysDataSourceError(
                "PreparedReadRequest context position does not match the read position.",
                field="context",
                expected=source_position,
                actual=context.position,
            )
        if context.request_fingerprint != request.fingerprint:
            raise RemotePhysDataSourceError(
                "PreparedReadRequest context request fingerprint does not match the sample request.",
                field="context",
                expected=request.fingerprint,
                actual=context.request_fingerprint,
            )
        object.__setattr__(self, "position", source_position)
        object.__setattr__(self, "request", request)
        object.__setattr__(self, "context", context)
        object.__setattr__(
            self,
            "manifest_fingerprint",
            _coerce_fingerprint(
                manifest_fingerprint,
                owner="PreparedReadRequest",
                field="manifest_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                _coerce_primitive_mapping(
                    metadata,
                    owner="PreparedReadRequest",
                    field="metadata",
                )
            ),
        )


PreparedReadRequest.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class PreparedReadResult:
    """Validated result returned by a ``PreparedSampleReader``."""

    sample: Sample
    manifest_fingerprint: str
    backend_id: str
    field_locators: tuple[FieldLocator, ...]
    metadata: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        *,
        sample: Sample,
        manifest_fingerprint: str,
        backend_id: str,
        field_locators: Sequence[FieldLocator | str] | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        if not isinstance(sample, Sample):
            raise FieldTypeError(
                "PreparedReadResult sample must be a Sample.",
                field="sample",
                actual=type(sample).__name__,
            )
        object.__setattr__(self, "sample", sample)
        object.__setattr__(
            self,
            "manifest_fingerprint",
            _coerce_fingerprint(
                manifest_fingerprint,
                owner="PreparedReadResult",
                field="manifest_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "backend_id",
            _coerce_non_empty_string(
                backend_id,
                owner="PreparedReadResult",
                field="backend_id",
            ),
        )
        locators = (
            tuple(locator for locator, _ in sample.field_items())
            if field_locators is None
            else _coerce_locators(field_locators)
        )
        object.__setattr__(self, "field_locators", locators)
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                _coerce_primitive_mapping(
                    metadata,
                    owner="PreparedReadResult",
                    field="metadata",
                )
            ),
        )


PreparedReadResult.__hash__ = None  # type: ignore[assignment]


@runtime_checkable
class PreparedSampleReader(Protocol):
    """Public provisional protocol for backend-specific prepared readers."""

    @property
    def manifest(self) -> PreparedDataManifest:
        ...

    def read(self, request: PreparedReadRequest) -> PreparedReadResult:
        ...


class PreparedSampleSource(SampleSource):
    """Sample source that reads an immutable prepared product through a reader."""

    __slots__ = ("_manifest", "_reader", "_context_factory")

    def __init__(
        self,
        manifest: PreparedDataManifest,
        reader: PreparedSampleReader,
        *,
        context_factory: Callable[[int, SampleRequest], SampleRuntimeContext] | None = None,
    ) -> None:
        if not isinstance(manifest, PreparedDataManifest):
            raise RemotePhysDataSourceError(
                "PreparedSampleSource manifest must be a PreparedDataManifest.",
                field="manifest",
                actual=type(manifest).__name__,
            )
        _validate_reader(reader)
        reader_manifest = reader.manifest
        if reader_manifest.fingerprint != manifest.fingerprint:
            raise RemotePhysDataSourceError(
                "PreparedSampleSource reader manifest does not match the source manifest.",
                field="reader",
                expected=manifest.fingerprint,
                actual=reader_manifest.fingerprint,
            )
        if context_factory is not None and not callable(context_factory):
            raise FieldTypeError(
                "PreparedSampleSource context_factory must be callable.",
                field="context_factory",
                actual=type(context_factory).__name__,
            )
        self._manifest = manifest
        self._reader = reader
        self._context_factory = context_factory

    @property
    def manifest(self) -> PreparedDataManifest:
        """Prepared manifest used for equivalence validation."""

        return self._manifest

    @property
    def reader(self) -> PreparedSampleReader:
        """Backend reader, exposed for inspection without mutation."""

        return self._reader

    def __len__(self) -> int:
        return self._manifest.sample_count

    def sample_at(
        self,
        position: int,
        request: SampleRequestLike = None,
        context: SampleRuntimeContext | None = None,
    ) -> Sample:
        source_position = _coerce_non_negative_int(
            position,
            owner="PreparedSampleSource",
            field="position",
        )
        if source_position >= self._manifest.sample_count:
            raise RemotePhysDataSourceError(
                "Prepared sample position is out of range.",
                field="position",
                expected=f"0 <= position < {self._manifest.sample_count}",
                actual=source_position,
            )
        request_object = SampleRequest.coerce(request)
        if context is None:
            context = self._make_context(source_position, request_object)
        expected_locators = self._manifest.expected_locators(request_object)
        self._manifest.validate_request_context(
            request_object,
            context,
            position=source_position,
        )
        read_request = PreparedReadRequest(
            position=source_position,
            request=request_object,
            context=context,
            manifest_fingerprint=self._manifest.fingerprint,
        )
        result = self._reader.read(read_request)
        self._validate_result(result, expected_locators)
        return result.sample

    def _make_context(
        self,
        position: int,
        request: SampleRequest,
    ) -> SampleRuntimeContext:
        if self._context_factory is not None:
            context = self._context_factory(position, request)
            if not isinstance(context, SampleRuntimeContext):
                raise FieldTypeError(
                    "PreparedSampleSource context_factory must return a SampleRuntimeContext.",
                    field="context_factory",
                    actual=type(context).__name__,
                )
            return context
        return SampleRuntimeContext(
            index_id=self._manifest.index_id,
            entry_id=f"{self._manifest.manifest_id}:{position}",
            position=position,
            candidate_id=f"{self._manifest.manifest_id}:{position}",
            record_id=f"{self._manifest.manifest_id}:{position}",
            datasource_id=self._manifest.datasource_id,
            source_id=self._manifest.source_id,
            request_fingerprint=request.fingerprint,
            metadata={
                "prepared_manifest_fingerprint": self._manifest.fingerprint,
                "prepared_manifest_id": self._manifest.manifest_id,
            },
        )

    def _validate_result(
        self,
        result: object,
        expected_locators: tuple[FieldLocator, ...],
    ) -> None:
        if not isinstance(result, PreparedReadResult):
            raise FieldTypeError(
                "PreparedSampleReader read must return a PreparedReadResult.",
                field="reader",
                actual=type(result).__name__,
            )
        mismatches: dict[str, object] = {}
        if result.manifest_fingerprint != self._manifest.fingerprint:
            mismatches["manifest_fingerprint"] = {
                "expected": self._manifest.fingerprint,
                "actual": result.manifest_fingerprint,
            }
        if result.backend_id != self._manifest.backend_id:
            mismatches["backend_id"] = {
                "expected": self._manifest.backend_id,
                "actual": result.backend_id,
            }
        if result.field_locators != expected_locators:
            mismatches["field_locators"] = {
                "expected": [str(locator) for locator in expected_locators],
                "actual": [str(locator) for locator in result.field_locators],
            }
        missing = [str(locator) for locator in expected_locators if not result.sample.has(locator)]
        if missing:
            mismatches["sample_fields"] = {"missing": missing}
        if mismatches:
            raise RemotePhysDataSourceError(
                "PreparedSampleReader result does not match the prepared request.",
                field="reader",
                mismatches=mismatches,
            )


@dataclass(frozen=True, init=False, slots=True)
class OptimizedStorageFormat:
    """Backend-neutral description of a prepared storage format."""

    name: str
    version: str | None
    media_type: str | None
    capabilities: Mapping[str, FrozenPrimitive]
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        name: str,
        *,
        version: str | None = None,
        media_type: str | None = None,
        capabilities: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "name", name, owner="OptimizedStorageFormat")
        _set_optional_string(self, "version", version, owner="OptimizedStorageFormat")
        _set_optional_string(self, "media_type", media_type, owner="OptimizedStorageFormat")
        _set_primitive_mapping(self, "capabilities", capabilities, owner="OptimizedStorageFormat")
        _set_primitive_mapping(self, "metadata", metadata, owner="OptimizedStorageFormat")
        _set_fingerprint(self, fingerprint, owner="OptimizedStorageFormat")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "name": self.name,
                "version": self.version,
                "media_type": self.media_type,
                "capabilities": dict(self.capabilities),
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "OptimizedStorageFormat":
        data = _require_record(
            value,
            {
                "name",
                "version",
                "media_type",
                "capabilities",
                "metadata",
                "fingerprint",
            },
            descriptor="OptimizedStorageFormat",
        )
        return cls(
            data["name"],  # type: ignore[arg-type]
            version=data["version"],  # type: ignore[arg-type]
            media_type=data["media_type"],  # type: ignore[arg-type]
            capabilities=data["capabilities"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


OptimizedStorageFormat.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class ChunkMetadata:
    """Descriptive metadata for one contiguous prepared chunk."""

    chunk_id: str
    field_locators: tuple[FieldLocator, ...]
    sample_start: int
    sample_count: int
    byte_offset: int | None
    byte_length: int | None
    checksum: str | None
    compression: Mapping[str, FrozenPrimitive]
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        chunk_id: str,
        *,
        field_locators: Sequence[FieldLocator | str],
        sample_start: int,
        sample_count: int,
        byte_offset: int | None = None,
        byte_length: int | None = None,
        checksum: str | None = None,
        compression: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "chunk_id", chunk_id, owner="ChunkMetadata")
        object.__setattr__(
            self,
            "field_locators",
            _coerce_required_locators(field_locators, owner="ChunkMetadata"),
        )
        _set_non_negative_int(self, "sample_start", sample_start, owner="ChunkMetadata")
        _set_non_negative_int(self, "sample_count", sample_count, owner="ChunkMetadata")
        _set_optional_non_negative_int(self, "byte_offset", byte_offset, owner="ChunkMetadata")
        _set_optional_non_negative_int(self, "byte_length", byte_length, owner="ChunkMetadata")
        _set_optional_string(self, "checksum", checksum, owner="ChunkMetadata")
        _set_primitive_mapping(self, "compression", compression, owner="ChunkMetadata")
        _set_primitive_mapping(self, "metadata", metadata, owner="ChunkMetadata")
        _set_fingerprint(self, fingerprint, owner="ChunkMetadata")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "chunk_id": self.chunk_id,
                "field_locators": [str(locator) for locator in self.field_locators],
                "sample_start": self.sample_start,
                "sample_count": self.sample_count,
                "byte_offset": self.byte_offset,
                "byte_length": self.byte_length,
                "checksum": self.checksum,
                "compression": dict(self.compression),
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "ChunkMetadata":
        data = _require_record(
            value,
            {
                "chunk_id",
                "field_locators",
                "sample_start",
                "sample_count",
                "byte_offset",
                "byte_length",
                "checksum",
                "compression",
                "metadata",
                "fingerprint",
            },
            descriptor="ChunkMetadata",
        )
        return cls(
            data["chunk_id"],  # type: ignore[arg-type]
            field_locators=data["field_locators"],  # type: ignore[arg-type]
            sample_start=data["sample_start"],  # type: ignore[arg-type]
            sample_count=data["sample_count"],  # type: ignore[arg-type]
            byte_offset=data["byte_offset"],  # type: ignore[arg-type]
            byte_length=data["byte_length"],  # type: ignore[arg-type]
            checksum=data["checksum"],  # type: ignore[arg-type]
            compression=data["compression"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


ChunkMetadata.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class ShardManifest:
    """Descriptor for one shard in a materialized prepared product."""

    shard_id: str
    storage_format: OptimizedStorageFormat
    uri: str
    sample_count: int
    chunks: tuple[ChunkMetadata, ...]
    checksums: Mapping[str, FrozenPrimitive]
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        shard_id: str,
        *,
        storage_format: OptimizedStorageFormat,
        uri: str,
        sample_count: int,
        chunks: Sequence[ChunkMetadata],
        checksums: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "shard_id", shard_id, owner="ShardManifest")
        object.__setattr__(self, "storage_format", _coerce_storage_format(storage_format))
        _set_string(self, "uri", uri, owner="ShardManifest")
        _set_non_negative_int(self, "sample_count", sample_count, owner="ShardManifest")
        object.__setattr__(self, "chunks", _coerce_chunks(chunks))
        _set_primitive_mapping(self, "checksums", checksums, owner="ShardManifest")
        _set_primitive_mapping(self, "metadata", metadata, owner="ShardManifest")
        _validate_shard_chunks(self)
        _set_fingerprint(self, fingerprint, owner="ShardManifest")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "shard_id": self.shard_id,
                "storage_format": self.storage_format.to_dict(),
                "uri": self.uri,
                "sample_count": self.sample_count,
                "chunks": [chunk.to_dict() for chunk in self.chunks],
                "checksums": dict(self.checksums),
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "ShardManifest":
        data = _require_record(
            value,
            {
                "shard_id",
                "storage_format",
                "uri",
                "sample_count",
                "chunks",
                "checksums",
                "metadata",
                "fingerprint",
            },
            descriptor="ShardManifest",
        )
        return cls(
            data["shard_id"],  # type: ignore[arg-type]
            storage_format=OptimizedStorageFormat.from_dict(data["storage_format"]),
            uri=data["uri"],  # type: ignore[arg-type]
            sample_count=data["sample_count"],  # type: ignore[arg-type]
            chunks=[
                ChunkMetadata.from_dict(item)
                for item in _require_sequence(data["chunks"], field="chunks")
            ],
            checksums=data["checksums"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


ShardManifest.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class AccessPatternPlan:
    """Descriptive access pattern evidence, not an execution plan."""

    pattern_id: str
    mode: str
    prefetch: int | None
    ordering: str | None
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        pattern_id: str,
        *,
        mode: str,
        prefetch: int | None = None,
        ordering: str | None = None,
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "pattern_id", pattern_id, owner="AccessPatternPlan")
        object.__setattr__(
            self,
            "mode",
            _coerce_choice(
                mode,
                owner="AccessPatternPlan",
                field="mode",
                choices={"sequential", "random", "sharded", "batched"},
            ),
        )
        _set_optional_non_negative_int(self, "prefetch", prefetch, owner="AccessPatternPlan")
        _set_optional_string(self, "ordering", ordering, owner="AccessPatternPlan")
        _set_primitive_mapping(self, "metadata", metadata, owner="AccessPatternPlan")
        _set_fingerprint(self, fingerprint, owner="AccessPatternPlan")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "pattern_id": self.pattern_id,
                "mode": self.mode,
                "prefetch": self.prefetch,
                "ordering": self.ordering,
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "AccessPatternPlan":
        data = _require_record(
            value,
            {"pattern_id", "mode", "prefetch", "ordering", "metadata", "fingerprint"},
            descriptor="AccessPatternPlan",
        )
        return cls(
            data["pattern_id"],  # type: ignore[arg-type]
            mode=data["mode"],  # type: ignore[arg-type]
            prefetch=data["prefetch"],  # type: ignore[arg-type]
            ordering=data["ordering"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


AccessPatternPlan.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class RecordLayoutMetadata:
    """Location evidence for one record or sample inside a shard."""

    record_id: str
    shard_id: str
    position: int
    field_locators: tuple[FieldLocator, ...]
    byte_offset: int | None
    byte_length: int | None
    checksum: str | None
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        record_id: str,
        *,
        shard_id: str,
        position: int,
        field_locators: Sequence[FieldLocator | str],
        byte_offset: int | None = None,
        byte_length: int | None = None,
        checksum: str | None = None,
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "record_id", record_id, owner="RecordLayoutMetadata")
        _set_string(self, "shard_id", shard_id, owner="RecordLayoutMetadata")
        _set_non_negative_int(self, "position", position, owner="RecordLayoutMetadata")
        object.__setattr__(
            self,
            "field_locators",
            _coerce_required_locators(field_locators, owner="RecordLayoutMetadata"),
        )
        _set_optional_non_negative_int(
            self,
            "byte_offset",
            byte_offset,
            owner="RecordLayoutMetadata",
        )
        _set_optional_non_negative_int(
            self,
            "byte_length",
            byte_length,
            owner="RecordLayoutMetadata",
        )
        _set_optional_string(self, "checksum", checksum, owner="RecordLayoutMetadata")
        _set_primitive_mapping(self, "metadata", metadata, owner="RecordLayoutMetadata")
        _set_fingerprint(self, fingerprint, owner="RecordLayoutMetadata")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "record_id": self.record_id,
                "shard_id": self.shard_id,
                "position": self.position,
                "field_locators": [str(locator) for locator in self.field_locators],
                "byte_offset": self.byte_offset,
                "byte_length": self.byte_length,
                "checksum": self.checksum,
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "RecordLayoutMetadata":
        data = _require_record(
            value,
            {
                "record_id",
                "shard_id",
                "position",
                "field_locators",
                "byte_offset",
                "byte_length",
                "checksum",
                "metadata",
                "fingerprint",
            },
            descriptor="RecordLayoutMetadata",
        )
        return cls(
            data["record_id"],  # type: ignore[arg-type]
            shard_id=data["shard_id"],  # type: ignore[arg-type]
            position=data["position"],  # type: ignore[arg-type]
            field_locators=data["field_locators"],  # type: ignore[arg-type]
            byte_offset=data["byte_offset"],  # type: ignore[arg-type]
            byte_length=data["byte_length"],  # type: ignore[arg-type]
            checksum=data["checksum"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


RecordLayoutMetadata.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class OptimizedDataPlan:
    """Storage-neutral plan for prepared data layout."""

    plan_id: str
    storage_format: OptimizedStorageFormat
    prepared_manifest_fingerprint: str
    field_locators: tuple[FieldLocator, ...]
    sample_count: int
    access_pattern: AccessPatternPlan | None
    layout: Mapping[str, FrozenPrimitive]
    runtime: Mapping[str, FrozenPrimitive]
    invalidation: Mapping[str, FrozenPrimitive]
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        plan_id: str,
        *,
        storage_format: OptimizedStorageFormat,
        prepared_manifest_fingerprint: str,
        field_locators: Sequence[FieldLocator | str],
        sample_count: int,
        access_pattern: AccessPatternPlan | None = None,
        layout: Mapping[str, object] | None = None,
        runtime: Mapping[str, object] | None = None,
        invalidation: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "plan_id", plan_id, owner="OptimizedDataPlan")
        object.__setattr__(self, "storage_format", _coerce_storage_format(storage_format))
        object.__setattr__(
            self,
            "prepared_manifest_fingerprint",
            _coerce_fingerprint(
                prepared_manifest_fingerprint,
                owner="OptimizedDataPlan",
                field="prepared_manifest_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "field_locators",
            _coerce_required_locators(field_locators, owner="OptimizedDataPlan"),
        )
        _set_non_negative_int(self, "sample_count", sample_count, owner="OptimizedDataPlan")
        if access_pattern is not None and not isinstance(access_pattern, AccessPatternPlan):
            raise FieldTypeError(
                "OptimizedDataPlan access_pattern must be an AccessPatternPlan.",
                field="access_pattern",
                actual=type(access_pattern).__name__,
            )
        object.__setattr__(self, "access_pattern", access_pattern)
        _set_primitive_mapping(self, "layout", layout, owner="OptimizedDataPlan")
        _set_primitive_mapping(self, "runtime", runtime, owner="OptimizedDataPlan")
        _set_primitive_mapping(self, "invalidation", invalidation, owner="OptimizedDataPlan")
        _set_primitive_mapping(self, "metadata", metadata, owner="OptimizedDataPlan")
        _set_fingerprint(self, fingerprint, owner="OptimizedDataPlan")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "plan_id": self.plan_id,
                "storage_format": self.storage_format.to_dict(),
                "prepared_manifest_fingerprint": self.prepared_manifest_fingerprint,
                "field_locators": [str(locator) for locator in self.field_locators],
                "sample_count": self.sample_count,
                "access_pattern": (
                    None if self.access_pattern is None else self.access_pattern.to_dict()
                ),
                "layout": dict(self.layout),
                "runtime": dict(self.runtime),
                "invalidation": dict(self.invalidation),
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "OptimizedDataPlan":
        data = _require_record(
            value,
            {
                "plan_id",
                "storage_format",
                "prepared_manifest_fingerprint",
                "field_locators",
                "sample_count",
                "access_pattern",
                "layout",
                "runtime",
                "invalidation",
                "metadata",
                "fingerprint",
            },
            descriptor="OptimizedDataPlan",
        )
        access_pattern = (
            None
            if data["access_pattern"] is None
            else AccessPatternPlan.from_dict(data["access_pattern"])
        )
        return cls(
            data["plan_id"],  # type: ignore[arg-type]
            storage_format=OptimizedStorageFormat.from_dict(data["storage_format"]),
            prepared_manifest_fingerprint=data["prepared_manifest_fingerprint"],  # type: ignore[arg-type]
            field_locators=data["field_locators"],  # type: ignore[arg-type]
            sample_count=data["sample_count"],  # type: ignore[arg-type]
            access_pattern=access_pattern,
            layout=data["layout"],  # type: ignore[arg-type]
            runtime=data["runtime"],  # type: ignore[arg-type]
            invalidation=data["invalidation"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


OptimizedDataPlan.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class MaterializationPlan:
    """Descriptive plan for creating an immutable materialized product."""

    plan_id: str
    optimized_plan: OptimizedDataPlan
    prepared_manifest_fingerprint: str
    request_fingerprint: str
    field_locators: tuple[FieldLocator, ...]
    sample_count: int
    split_counts: Mapping[str, int]
    group_counts: Mapping[str, int]
    invalidation: Mapping[str, FrozenPrimitive]
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        plan_id: str,
        *,
        optimized_plan: OptimizedDataPlan,
        prepared_manifest_fingerprint: str,
        request_fingerprint: str,
        field_locators: Sequence[FieldLocator | str],
        sample_count: int,
        split_counts: Mapping[str, int] | None = None,
        group_counts: Mapping[str, int] | None = None,
        invalidation: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "plan_id", plan_id, owner="MaterializationPlan")
        if not isinstance(optimized_plan, OptimizedDataPlan):
            raise FieldTypeError(
                "MaterializationPlan optimized_plan must be an OptimizedDataPlan.",
                field="optimized_plan",
                actual=type(optimized_plan).__name__,
            )
        object.__setattr__(self, "optimized_plan", optimized_plan)
        object.__setattr__(
            self,
            "prepared_manifest_fingerprint",
            _coerce_fingerprint(
                prepared_manifest_fingerprint,
                owner="MaterializationPlan",
                field="prepared_manifest_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "request_fingerprint",
            _coerce_fingerprint(
                request_fingerprint,
                owner="MaterializationPlan",
                field="request_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "field_locators",
            _coerce_required_locators(field_locators, owner="MaterializationPlan"),
        )
        _set_non_negative_int(self, "sample_count", sample_count, owner="MaterializationPlan")
        object.__setattr__(
            self,
            "split_counts",
            MappingProxyType(
                _coerce_count_mapping(
                    split_counts,
                    owner="MaterializationPlan",
                    field="split_counts",
                )
            ),
        )
        object.__setattr__(
            self,
            "group_counts",
            MappingProxyType(
                _coerce_count_mapping(
                    group_counts,
                    owner="MaterializationPlan",
                    field="group_counts",
                )
            ),
        )
        _set_primitive_mapping(self, "invalidation", invalidation, owner="MaterializationPlan")
        _set_primitive_mapping(self, "metadata", metadata, owner="MaterializationPlan")
        _validate_materialization_plan(self)
        _set_fingerprint(self, fingerprint, owner="MaterializationPlan")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "plan_id": self.plan_id,
                "optimized_plan": self.optimized_plan.to_dict(),
                "prepared_manifest_fingerprint": self.prepared_manifest_fingerprint,
                "request_fingerprint": self.request_fingerprint,
                "field_locators": [str(locator) for locator in self.field_locators],
                "sample_count": self.sample_count,
                "split_counts": dict(self.split_counts),
                "group_counts": dict(self.group_counts),
                "invalidation": dict(self.invalidation),
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "MaterializationPlan":
        data = _require_record(
            value,
            {
                "plan_id",
                "optimized_plan",
                "prepared_manifest_fingerprint",
                "request_fingerprint",
                "field_locators",
                "sample_count",
                "split_counts",
                "group_counts",
                "invalidation",
                "metadata",
                "fingerprint",
            },
            descriptor="MaterializationPlan",
        )
        return cls(
            data["plan_id"],  # type: ignore[arg-type]
            optimized_plan=OptimizedDataPlan.from_dict(data["optimized_plan"]),
            prepared_manifest_fingerprint=data["prepared_manifest_fingerprint"],  # type: ignore[arg-type]
            request_fingerprint=data["request_fingerprint"],  # type: ignore[arg-type]
            field_locators=data["field_locators"],  # type: ignore[arg-type]
            sample_count=data["sample_count"],  # type: ignore[arg-type]
            split_counts=data["split_counts"],  # type: ignore[arg-type]
            group_counts=data["group_counts"],  # type: ignore[arg-type]
            invalidation=data["invalidation"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


MaterializationPlan.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class MaterializationManifest:
    """Manifest for a materialized prepared product, without writer behavior."""

    materialization_id: str
    plan_fingerprint: str
    storage_format: OptimizedStorageFormat
    prepared_manifest_fingerprint: str
    shards: tuple[ShardManifest, ...]
    records: tuple[RecordLayoutMetadata, ...]
    sample_count: int
    field_locators: tuple[FieldLocator, ...]
    checksums: Mapping[str, FrozenPrimitive]
    invalidation: Mapping[str, FrozenPrimitive]
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        materialization_id: str,
        *,
        plan_fingerprint: str,
        storage_format: OptimizedStorageFormat,
        prepared_manifest_fingerprint: str,
        shards: Sequence[ShardManifest],
        records: Sequence[RecordLayoutMetadata] | None = None,
        sample_count: int,
        field_locators: Sequence[FieldLocator | str],
        checksums: Mapping[str, object] | None = None,
        invalidation: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "materialization_id", materialization_id, owner="MaterializationManifest")
        object.__setattr__(
            self,
            "plan_fingerprint",
            _coerce_fingerprint(
                plan_fingerprint,
                owner="MaterializationManifest",
                field="plan_fingerprint",
            ),
        )
        object.__setattr__(self, "storage_format", _coerce_storage_format(storage_format))
        object.__setattr__(
            self,
            "prepared_manifest_fingerprint",
            _coerce_fingerprint(
                prepared_manifest_fingerprint,
                owner="MaterializationManifest",
                field="prepared_manifest_fingerprint",
            ),
        )
        object.__setattr__(self, "shards", _coerce_shards(shards))
        object.__setattr__(self, "records", _coerce_records(records or ()))
        _set_non_negative_int(self, "sample_count", sample_count, owner="MaterializationManifest")
        object.__setattr__(
            self,
            "field_locators",
            _coerce_required_locators(field_locators, owner="MaterializationManifest"),
        )
        _set_primitive_mapping(self, "checksums", checksums, owner="MaterializationManifest")
        _set_primitive_mapping(self, "invalidation", invalidation, owner="MaterializationManifest")
        _set_primitive_mapping(self, "metadata", metadata, owner="MaterializationManifest")
        _validate_materialization_manifest(self)
        _set_fingerprint(self, fingerprint, owner="MaterializationManifest")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "materialization_id": self.materialization_id,
                "plan_fingerprint": self.plan_fingerprint,
                "storage_format": self.storage_format.to_dict(),
                "prepared_manifest_fingerprint": self.prepared_manifest_fingerprint,
                "shards": [shard.to_dict() for shard in self.shards],
                "records": [record.to_dict() for record in self.records],
                "sample_count": self.sample_count,
                "field_locators": [str(locator) for locator in self.field_locators],
                "checksums": dict(self.checksums),
                "invalidation": dict(self.invalidation),
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "MaterializationManifest":
        data = _require_record(
            value,
            {
                "materialization_id",
                "plan_fingerprint",
                "storage_format",
                "prepared_manifest_fingerprint",
                "shards",
                "records",
                "sample_count",
                "field_locators",
                "checksums",
                "invalidation",
                "metadata",
                "fingerprint",
            },
            descriptor="MaterializationManifest",
        )
        return cls(
            data["materialization_id"],  # type: ignore[arg-type]
            plan_fingerprint=data["plan_fingerprint"],  # type: ignore[arg-type]
            storage_format=OptimizedStorageFormat.from_dict(data["storage_format"]),
            prepared_manifest_fingerprint=data["prepared_manifest_fingerprint"],  # type: ignore[arg-type]
            shards=[
                ShardManifest.from_dict(item)
                for item in _require_sequence(data["shards"], field="shards")
            ],
            records=[
                RecordLayoutMetadata.from_dict(item)
                for item in _require_sequence(data["records"], field="records")
            ],
            sample_count=data["sample_count"],  # type: ignore[arg-type]
            field_locators=data["field_locators"],  # type: ignore[arg-type]
            checksums=data["checksums"],  # type: ignore[arg-type]
            invalidation=data["invalidation"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


MaterializationManifest.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class BatchCostMetadata:
    """Descriptive per-sample cost evidence for later batching policy."""

    position: int
    cost: float
    weight: float
    length: int | None
    group: str | None
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        *,
        position: int,
        cost: float | int,
        weight: float | int = 1.0,
        length: int | None = None,
        group: str | None = None,
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_non_negative_int(self, "position", position, owner="BatchCostMetadata")
        object.__setattr__(self, "cost", _coerce_non_negative_float(cost, owner="BatchCostMetadata", field="cost"))
        object.__setattr__(
            self,
            "weight",
            _coerce_non_negative_float(weight, owner="BatchCostMetadata", field="weight"),
        )
        _set_optional_non_negative_int(self, "length", length, owner="BatchCostMetadata")
        _set_optional_string(self, "group", group, owner="BatchCostMetadata")
        _set_primitive_mapping(self, "metadata", metadata, owner="BatchCostMetadata")
        _set_fingerprint(self, fingerprint, owner="BatchCostMetadata")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "position": self.position,
                "cost": self.cost,
                "weight": self.weight,
                "length": self.length,
                "group": self.group,
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "BatchCostMetadata":
        data = _require_record(
            value,
            {"position", "cost", "weight", "length", "group", "metadata", "fingerprint"},
            descriptor="BatchCostMetadata",
        )
        return cls(
            position=data["position"],  # type: ignore[arg-type]
            cost=data["cost"],  # type: ignore[arg-type]
            weight=data["weight"],  # type: ignore[arg-type]
            length=data["length"],  # type: ignore[arg-type]
            group=data["group"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


BatchCostMetadata.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class BatchShapePolicy:
    """Data-only batch shape policy record."""

    policy_id: str
    mode: str
    batch_size: int
    drop_last: bool
    pad: bool
    max_tokens: int | None
    field_locators: tuple[FieldLocator, ...] | None
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        policy_id: str,
        *,
        mode: str = "fixed",
        batch_size: int,
        drop_last: bool = False,
        pad: bool = False,
        max_tokens: int | None = None,
        field_locators: Sequence[FieldLocator | str] | None = None,
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "policy_id", policy_id, owner="BatchShapePolicy")
        object.__setattr__(
            self,
            "mode",
            _coerce_choice(
                mode,
                owner="BatchShapePolicy",
                field="mode",
                choices={"fixed", "dynamic", "packing"},
            ),
        )
        _set_positive_int(self, "batch_size", batch_size, owner="BatchShapePolicy")
        object.__setattr__(self, "drop_last", _coerce_bool(drop_last, owner="BatchShapePolicy", field="drop_last"))
        object.__setattr__(self, "pad", _coerce_bool(pad, owner="BatchShapePolicy", field="pad"))
        _set_optional_non_negative_int(self, "max_tokens", max_tokens, owner="BatchShapePolicy")
        object.__setattr__(
            self,
            "field_locators",
            None
            if field_locators is None
            else _coerce_required_locators(field_locators, owner="BatchShapePolicy"),
        )
        _set_primitive_mapping(self, "metadata", metadata, owner="BatchShapePolicy")
        _set_fingerprint(self, fingerprint, owner="BatchShapePolicy")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "policy_id": self.policy_id,
                "mode": self.mode,
                "batch_size": self.batch_size,
                "drop_last": self.drop_last,
                "pad": self.pad,
                "max_tokens": self.max_tokens,
                "field_locators": None
                if self.field_locators is None
                else [str(locator) for locator in self.field_locators],
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "BatchShapePolicy":
        data = _require_record(
            value,
            {
                "policy_id",
                "mode",
                "batch_size",
                "drop_last",
                "pad",
                "max_tokens",
                "field_locators",
                "metadata",
                "fingerprint",
            },
            descriptor="BatchShapePolicy",
        )
        return cls(
            data["policy_id"],  # type: ignore[arg-type]
            mode=data["mode"],  # type: ignore[arg-type]
            batch_size=data["batch_size"],  # type: ignore[arg-type]
            drop_last=data["drop_last"],  # type: ignore[arg-type]
            pad=data["pad"],  # type: ignore[arg-type]
            max_tokens=data["max_tokens"],  # type: ignore[arg-type]
            field_locators=data["field_locators"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


BatchShapePolicy.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class BatchSamplerPlan:
    """Descriptive sampler plan record; it does not sample batches."""

    plan_id: str
    shape_policy: BatchShapePolicy
    ordering: str
    cost_metadata: tuple[BatchCostMetadata, ...]
    seed: FrozenPrimitive | None
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        plan_id: str,
        *,
        shape_policy: BatchShapePolicy,
        ordering: str = "sequential",
        cost_metadata: Sequence[BatchCostMetadata] = (),
        seed: object | None = None,
        metadata: Mapping[str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        _set_string(self, "plan_id", plan_id, owner="BatchSamplerPlan")
        if not isinstance(shape_policy, BatchShapePolicy):
            raise FieldTypeError(
                "BatchSamplerPlan shape_policy must be a BatchShapePolicy.",
                field="shape_policy",
                actual=type(shape_policy).__name__,
            )
        object.__setattr__(self, "shape_policy", shape_policy)
        object.__setattr__(
            self,
            "ordering",
            _coerce_choice(
                ordering,
                owner="BatchSamplerPlan",
                field="ordering",
                choices={"sequential", "shuffle", "cost_aware", "grouped"},
            ),
        )
        object.__setattr__(self, "cost_metadata", _coerce_cost_metadata(cost_metadata))
        object.__setattr__(
            self,
            "seed",
            _coerce_optional_primitive(seed, owner="BatchSamplerPlan", field="seed"),
        )
        _set_primitive_mapping(self, "metadata", metadata, owner="BatchSamplerPlan")
        _set_fingerprint(self, fingerprint, owner="BatchSamplerPlan")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        return _record_dict(
            {
                "plan_id": self.plan_id,
                "shape_policy": self.shape_policy.to_dict(),
                "ordering": self.ordering,
                "cost_metadata": [cost.to_dict() for cost in self.cost_metadata],
                "seed": self.seed,
                "metadata": dict(self.metadata),
            },
            self,
            include_fingerprint=include_fingerprint,
        )

    @classmethod
    def from_dict(cls, value: object) -> "BatchSamplerPlan":
        data = _require_record(
            value,
            {
                "plan_id",
                "shape_policy",
                "ordering",
                "cost_metadata",
                "seed",
                "metadata",
                "fingerprint",
            },
            descriptor="BatchSamplerPlan",
        )
        return cls(
            data["plan_id"],  # type: ignore[arg-type]
            shape_policy=BatchShapePolicy.from_dict(data["shape_policy"]),
            ordering=data["ordering"],  # type: ignore[arg-type]
            cost_metadata=[
                BatchCostMetadata.from_dict(item)
                for item in _require_sequence(data["cost_metadata"], field="cost_metadata")
            ],
            seed=data["seed"],
            metadata=data["metadata"],  # type: ignore[arg-type]
            fingerprint=data["fingerprint"],  # type: ignore[arg-type]
        )


BatchSamplerPlan.__hash__ = None  # type: ignore[assignment]


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


def _set_optional_string(
    record: object,
    field: str,
    value: object | None,
    *,
    owner: str,
) -> None:
    object.__setattr__(
        record,
        field,
        _coerce_optional_non_empty_string(value, owner=owner, field=field),
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


def _coerce_storage_format(value: object) -> OptimizedStorageFormat:
    if not isinstance(value, OptimizedStorageFormat):
        raise FieldTypeError(
            "Storage format must be an OptimizedStorageFormat.",
            field="storage_format",
            actual=type(value).__name__,
        )
    return value


def _coerce_chunks(values: Sequence[ChunkMetadata]) -> tuple[ChunkMetadata, ...]:
    chunks = _coerce_record_sequence(values, ChunkMetadata, field="chunks")
    if not chunks:
        raise FieldTypeError("ShardManifest chunks must not be empty.", field="chunks")
    _require_unique_ids((chunk.chunk_id for chunk in chunks), field="chunks")
    return chunks


def _coerce_shards(values: Sequence[ShardManifest]) -> tuple[ShardManifest, ...]:
    shards = _coerce_record_sequence(values, ShardManifest, field="shards")
    if not shards:
        raise FieldTypeError("MaterializationManifest shards must not be empty.", field="shards")
    _require_unique_ids((shard.shard_id for shard in shards), field="shards")
    return shards


def _coerce_records(values: Sequence[RecordLayoutMetadata]) -> tuple[RecordLayoutMetadata, ...]:
    records = _coerce_record_sequence(values, RecordLayoutMetadata, field="records")
    _require_unique_ids((record.record_id for record in records), field="records")
    return records


def _coerce_cost_metadata(values: Sequence[BatchCostMetadata]) -> tuple[BatchCostMetadata, ...]:
    costs = _coerce_record_sequence(values, BatchCostMetadata, field="cost_metadata")
    positions = [str(cost.position) for cost in costs]
    _require_unique_ids(positions, field="cost_metadata")
    return costs


def _coerce_record_sequence(
    values: Sequence[object],
    expected_type: type,
    *,
    field: str,
) -> tuple:
    if isinstance(values, (str, bytes)):
        raise FieldTypeError(
            f"{field} must be a sequence.",
            field=field,
            actual=type(values).__name__,
        )
    try:
        records = tuple(values)
    except TypeError as exc:
        raise FieldTypeError(
            f"{field} must be a sequence.",
            field=field,
            actual=type(values).__name__,
        ) from exc
    for record in records:
        if not isinstance(record, expected_type):
            raise FieldTypeError(
                f"{field} entries must be {expected_type.__name__} records.",
                field=field,
                actual=type(record).__name__,
            )
    return records


def _require_unique_ids(values: Iterable[str], *, field: str) -> None:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen:
            duplicates.append(value)
        seen.add(value)
    if duplicates:
        raise FieldTypeError(
            "Descriptor identifiers must be unique.",
            field=field,
            duplicates=sorted(duplicates),
        )


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


def _coerce_bool(value: object, *, owner: str, field: str) -> bool:
    if type(value) is not bool:
        raise FieldTypeError(
            f"{owner} {field} must be a bool.",
            owner=owner,
            field=field,
            expected="bool",
            actual=type(value).__name__,
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


def _validate_shard_chunks(shard: ShardManifest) -> None:
    out_of_range = [
        chunk.chunk_id
        for chunk in shard.chunks
        if chunk.sample_start + chunk.sample_count > shard.sample_count
    ]
    if out_of_range:
        raise RemotePhysDataSourceError(
            "Shard chunk ranges must fit within the shard sample count.",
            field="chunks",
            shard_id=shard.shard_id,
            sample_count=shard.sample_count,
            chunk_ids=out_of_range,
        )


def _validate_materialization_plan(plan: MaterializationPlan) -> None:
    if plan.prepared_manifest_fingerprint != plan.optimized_plan.prepared_manifest_fingerprint:
        raise RemotePhysDataSourceError(
            "MaterializationPlan prepared manifest fingerprint must match its optimized plan.",
            field="prepared_manifest_fingerprint",
            expected=plan.optimized_plan.prepared_manifest_fingerprint,
            actual=plan.prepared_manifest_fingerprint,
        )
    optimized_locators = set(plan.optimized_plan.field_locators)
    missing = [
        str(locator)
        for locator in plan.field_locators
        if locator not in optimized_locators
    ]
    if missing:
        raise RemotePhysDataSourceError(
            "MaterializationPlan field locators must be present in the optimized plan.",
            field="field_locators",
            missing=missing,
        )


def _validate_materialization_manifest(manifest: MaterializationManifest) -> None:
    mismatched_shards = [
        shard.shard_id
        for shard in manifest.shards
        if shard.storage_format.fingerprint != manifest.storage_format.fingerprint
    ]
    if mismatched_shards:
        raise RemotePhysDataSourceError(
            "MaterializationManifest shard storage formats must match the manifest format.",
            field="shards",
            shard_ids=mismatched_shards,
        )

    manifest_locators = set(manifest.field_locators)
    shard_ids = {shard.shard_id for shard in manifest.shards}
    bad_chunks: dict[str, list[str]] = {}
    for shard in manifest.shards:
        for chunk in shard.chunks:
            missing = [
                str(locator)
                for locator in chunk.field_locators
                if locator not in manifest_locators
            ]
            if missing:
                bad_chunks[f"{shard.shard_id}:{chunk.chunk_id}"] = missing
    if bad_chunks:
        raise RemotePhysDataSourceError(
            "MaterializationManifest chunk locators must be present in the manifest.",
            field="chunks",
            missing=bad_chunks,
        )

    bad_records: dict[str, object] = {}
    for record in manifest.records:
        record_issues: dict[str, object] = {}
        if record.shard_id not in shard_ids:
            record_issues["shard_id"] = record.shard_id
        if record.position >= manifest.sample_count:
            record_issues["position"] = record.position
        missing = [
            str(locator)
            for locator in record.field_locators
            if locator not in manifest_locators
        ]
        if missing:
            record_issues["field_locators"] = missing
        if record_issues:
            bad_records[record.record_id] = record_issues
    if bad_records:
        raise RemotePhysDataSourceError(
            "MaterializationManifest records must reference declared shards, samples, and fields.",
            field="records",
            records=bad_records,
        )


def _validate_reader(reader: object) -> None:
    if not isinstance(reader, PreparedSampleReader):
        raise RemotePhysDataSourceError(
            "PreparedSampleSource reader must implement PreparedSampleReader.",
            field="reader",
            actual=type(reader).__name__,
        )
    if not isinstance(reader.manifest, PreparedDataManifest):
        raise RemotePhysDataSourceError(
            "PreparedSampleReader manifest must be a PreparedDataManifest.",
            field="reader.manifest",
            actual=type(reader.manifest).__name__,
        )


def _coerce_locator(value: FieldLocator | str) -> FieldLocator:
    if isinstance(value, FieldLocator):
        return value
    return FieldLocator.parse(value)


def _coerce_locators(values: Sequence[FieldLocator | str]) -> tuple[FieldLocator, ...]:
    if isinstance(values, (str, bytes)):
        raise FieldTypeError(
            "Prepared field locators must be a sequence of locators.",
            field="field_locators",
            actual=type(values).__name__,
        )
    locators = tuple(_coerce_locator(value) for value in values)
    duplicates = sorted(
        str(locator)
        for index, locator in enumerate(locators)
        if locator in locators[:index]
    )
    if duplicates:
        raise FieldTypeError(
            "Prepared field locators must be unique.",
            field="field_locators",
            duplicates=duplicates,
        )
    return locators


def _coerce_required_locators(
    values: Sequence[FieldLocator | str],
    *,
    owner: str,
) -> tuple[FieldLocator, ...]:
    locators = _coerce_locators(values)
    if not locators:
        raise FieldTypeError(
            f"{owner} field_locators must not be empty.",
            owner=owner,
            field="field_locators",
        )
    return locators


def _coerce_prepared_fields(values: Sequence[PreparedField]) -> tuple[PreparedField, ...]:
    if isinstance(values, (str, bytes)):
        raise FieldTypeError(
            "PreparedDataManifest fields must be a sequence of PreparedField records.",
            field="fields",
            actual=type(values).__name__,
        )
    try:
        fields = tuple(values)
    except TypeError as exc:
        raise FieldTypeError(
            "PreparedDataManifest fields must be a sequence.",
            field="fields",
            actual=type(values).__name__,
        ) from exc
    if not fields:
        raise FieldTypeError("PreparedDataManifest fields must not be empty.", field="fields")
    for field in fields:
        if not isinstance(field, PreparedField):
            raise FieldTypeError(
                "PreparedDataManifest fields must be PreparedField records.",
                field="fields",
                actual=type(field).__name__,
            )
    _coerce_locators([field.locator for field in fields])
    return fields


def _coerce_optional_shape(
    value: Sequence[int | None] | None,
) -> tuple[int | None, ...] | None:
    if value is None:
        return None
    if isinstance(value, (str, bytes)):
        raise FieldTypeError(
            "PreparedField shape must be a sequence of non-negative integers or None values.",
            field="shape",
            actual=type(value).__name__,
        )
    try:
        shape = tuple(value)
    except TypeError as exc:
        raise FieldTypeError(
            "PreparedField shape must be a sequence.",
            field="shape",
            actual=type(value).__name__,
        ) from exc
    for dimension in shape:
        if dimension is None:
            continue
        _coerce_non_negative_int(dimension, owner="PreparedField", field="shape")
    return shape


def _coerce_schema_version(value: object) -> int:
    if type(value) is not int or value != _PREPARED_MANIFEST_SCHEMA_VERSION:
        raise RemotePhysDataSourceError(
            "Unsupported prepared manifest schema version.",
            field="schema_version",
            expected=_PREPARED_MANIFEST_SCHEMA_VERSION,
            actual=value,
        )
    return value


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


def _coerce_non_empty_string(value: object, *, owner: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise FieldTypeError(
            f"{owner} {field} must be a non-empty string.",
            owner=owner,
            field=field,
            actual=type(value).__name__,
        )
    return value


def _coerce_optional_non_empty_string(
    value: object | None,
    *,
    owner: str,
    field: str,
) -> str | None:
    if value is None:
        return None
    return _coerce_non_empty_string(value, owner=owner, field=field)


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


def _coerce_count_mapping(
    value: Mapping[str, int] | None,
    *,
    owner: str,
    field: str,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise FieldTypeError(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            actual=type(value).__name__,
        )
    return {
        _coerce_non_empty_string(key, owner=owner, field=f"{field} key"): (
            _coerce_non_negative_int(item, owner=owner, field=f"{field}[{key}]")
        )
        for key, item in value.items()
    }


def _require_sequence(value: object, *, field: str) -> tuple[object, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
        raise RemotePhysDataSourceError(
            "Serialized prepared descriptor values must be sequences.",
            field=field,
            actual=type(value).__name__,
        )
    return tuple(value)


def _require_mapping(value: object, *, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise RemotePhysDataSourceError(
            "Serialized prepared descriptors must be mappings.",
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
            "Serialized prepared descriptor keys do not match the schema.",
            descriptor=descriptor,
            expected=sorted(keys),
            actual=sorted(actual),
        )


def _canonical_json(value: object) -> str:
    return json.dumps(_to_jsonable(value), sort_keys=True, separators=(",", ":"))


def _to_jsonable(value: object) -> object:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()
