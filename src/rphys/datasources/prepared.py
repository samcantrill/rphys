"""Prepared-data manifests and provisional reader boundary for sample sources.

Stage 9 prepared data is an immutable equivalence contract, not a storage
backend. This module records primitive manifest evidence and defines a public
provisional ``PreparedSampleReader`` protocol that backend-specific readers can
implement without making backend details part of rphys domain semantics.
"""

from __future__ import annotations

import hashlib
import json
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
