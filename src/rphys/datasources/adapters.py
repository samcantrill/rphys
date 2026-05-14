"""Datasource adapter specs and descriptor-only scan results.

Adapters are structural importable Python objects with a ``scan(spec)`` method.
Scanning emits datasource and record descriptors, primitive scan metadata,
warnings, rejections, and validation evidence only; it must not construct
views, filter records, load payloads, or register adapter aliases.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol, Self, runtime_checkable

from rphys.data.keys import DataKey
from rphys.data.metadata import MetadataKey
from rphys.errors import (
    InvalidDataSourceScanResultError,
    InvalidDataSourceSpecError,
)
from rphys.io._primitives import (
    FrozenPrimitive,
    copy_string_mapping,
    freeze_primitive,
    thaw_primitive,
)

from .refs import DataSourceRef, RecordRef

__all__ = ["DataSourceAdapter", "DataSourceScanResult", "DataSourceSpec"]


@dataclass(frozen=True, init=False, slots=True)
class DataSourceSpec:
    """Descriptor-only request passed to a datasource adapter scan.

    ``datasource`` carries stable datasource identity, optional source/schema
    descriptors, and provenance metadata. ``required_fields`` are intrinsic
    ``DataKey`` values used by validation; they do not trigger payload loading
    or schema mutation.
    """

    datasource: DataSourceRef
    required_fields: tuple[DataKey, ...]
    metadata: Mapping[MetadataKey, FrozenPrimitive]

    def __init__(
        self,
        datasource: DataSourceRef,
        *,
        required_fields: Sequence[DataKey | str] = (),
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        if not isinstance(datasource, DataSourceRef):
            raise InvalidDataSourceSpecError(
                "DataSourceSpec datasource must be a DataSourceRef.",
                field="datasource",
                actual=type(datasource).__name__,
            )
        object.__setattr__(self, "datasource", datasource)
        object.__setattr__(
            self,
            "required_fields",
            _coerce_required_fields(required_fields),
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata, InvalidDataSourceSpecError)),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize scan inputs without adapter aliases or registry state."""

        return {
            "datasource": self.datasource.to_dict(),
            "required_fields": [str(key) for key in self.required_fields],
            "metadata": {
                str(key): thaw_primitive(value)
                for key, value in self.metadata.items()
            },
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct a scan specification from primitive values."""

        if not isinstance(value, Mapping):
            raise InvalidDataSourceSpecError(
                "Serialized DataSourceSpec must be a mapping.",
                field="datasource_spec",
                actual=type(value).__name__,
            )
        _require_keys(
            value,
            {"datasource", "required_fields", "metadata"},
            error_type=InvalidDataSourceSpecError,
            descriptor="DataSourceSpec",
        )
        return cls(
            DataSourceRef.from_dict(value["datasource"]),
            required_fields=value["required_fields"],  # type: ignore[arg-type]
            metadata=value["metadata"],  # type: ignore[arg-type]
        )


DataSourceSpec.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class DataSourceScanResult:
    """Descriptor-only result from ``DataSourceAdapter.scan``.

    ``records`` preserve adapter-discovered ``RecordRef`` descriptors in order.
    ``warnings`` and ``rejected_record_ids`` are primitive scan diagnostics;
    validation converts them into structured ``ValidationIssue`` records. The
    result intentionally has no dependency on datasource views or filters.
    """

    datasource: DataSourceRef
    records: tuple[RecordRef, ...]
    metadata: Mapping[MetadataKey, FrozenPrimitive]
    validation_evidence: Mapping[str, FrozenPrimitive]
    warnings: tuple[str, ...]
    rejected_record_ids: Mapping[str, str]

    def __init__(
        self,
        datasource: DataSourceRef,
        records: Sequence[RecordRef] = (),
        *,
        metadata: Mapping[MetadataKey | str, object] | None = None,
        validation_evidence: Mapping[str, object] | None = None,
        warnings: Sequence[str] = (),
        rejected_record_ids: Mapping[str, str] | None = None,
    ) -> None:
        if not isinstance(datasource, DataSourceRef):
            raise InvalidDataSourceScanResultError(
                "DataSourceScanResult datasource must be a DataSourceRef.",
                field="datasource",
                actual=type(datasource).__name__,
            )
        object.__setattr__(self, "datasource", datasource)
        object.__setattr__(self, "records", _coerce_records(records, datasource))
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                _coerce_metadata(metadata, InvalidDataSourceScanResultError)
            ),
        )
        object.__setattr__(
            self,
            "validation_evidence",
            MappingProxyType(
                copy_string_mapping(
                    validation_evidence,
                    error_type=InvalidDataSourceScanResultError,
                    field="validation_evidence",
                )
            ),
        )
        object.__setattr__(
            self,
            "warnings",
            _coerce_strings(
                warnings,
                field="warnings",
                error_type=InvalidDataSourceScanResultError,
            ),
        )
        object.__setattr__(
            self,
            "rejected_record_ids",
            MappingProxyType(_coerce_rejections(rejected_record_ids)),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize scan output without view, filter, or manifest fields."""

        return {
            "datasource": self.datasource.to_dict(),
            "records": [record.to_dict() for record in self.records],
            "metadata": {
                str(key): thaw_primitive(value)
                for key, value in self.metadata.items()
            },
            "validation_evidence": {
                key: thaw_primitive(value)
                for key, value in self.validation_evidence.items()
            },
            "warnings": list(self.warnings),
            "rejected_record_ids": dict(self.rejected_record_ids),
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct a scan result from primitive values."""

        if not isinstance(value, Mapping):
            raise InvalidDataSourceScanResultError(
                "Serialized DataSourceScanResult must be a mapping.",
                field="scan_result",
                actual=type(value).__name__,
            )
        _require_keys(
            value,
            {
                "datasource",
                "records",
                "metadata",
                "validation_evidence",
                "warnings",
                "rejected_record_ids",
            },
            error_type=InvalidDataSourceScanResultError,
            descriptor="DataSourceScanResult",
        )
        records = _records_from_dicts(value["records"])
        return cls(
            DataSourceRef.from_dict(value["datasource"]),
            records,
            metadata=value["metadata"],  # type: ignore[arg-type]
            validation_evidence=value["validation_evidence"],  # type: ignore[arg-type]
            warnings=value["warnings"],  # type: ignore[arg-type]
            rejected_record_ids=value["rejected_record_ids"],  # type: ignore[arg-type]
        )


DataSourceScanResult.__hash__ = None  # type: ignore[assignment]


@runtime_checkable
class DataSourceAdapter(Protocol):
    """Structural datasource adapter contract.

    Implementations may be plain objects. The scan method must return
    descriptor-only ``DataSourceScanResult`` values and must not rely on a
    global adapter registry or alias lookup.
    """

    def scan(self, spec: DataSourceSpec) -> DataSourceScanResult:
        """Return descriptor refs and primitive scan evidence for ``spec``."""


def _coerce_required_fields(
    required_fields: Sequence[DataKey | str],
) -> tuple[DataKey, ...]:
    if isinstance(required_fields, (str, bytes)) or not isinstance(
        required_fields,
        Sequence,
    ):
        raise InvalidDataSourceSpecError(
            "DataSourceSpec required_fields must be a sequence.",
            field="required_fields",
            actual=type(required_fields).__name__,
        )
    fields = tuple(DataKey(key) for key in required_fields)
    if len(set(fields)) != len(fields):
        raise InvalidDataSourceSpecError(
            "DataSourceSpec required_fields must not contain duplicates.",
            field="required_fields",
            values=[str(key) for key in fields],
        )
    return fields


def _coerce_records(
    records: Sequence[RecordRef],
    datasource: DataSourceRef,
) -> tuple[RecordRef, ...]:
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise InvalidDataSourceScanResultError(
            "DataSourceScanResult records must be a sequence.",
            field="records",
            actual=type(records).__name__,
        )
    coerced = tuple(records)
    for position, record in enumerate(coerced):
        if not isinstance(record, RecordRef):
            raise InvalidDataSourceScanResultError(
                "DataSourceScanResult records must contain RecordRef values.",
                field="records",
                position=position,
                actual=type(record).__name__,
            )
        if record.datasource.datasource_id != datasource.datasource_id:
            raise InvalidDataSourceScanResultError(
                "RecordRef datasource_id must match scan datasource_id.",
                field="records",
                position=position,
                expected=datasource.datasource_id,
                actual=record.datasource.datasource_id,
            )
    return coerced


def _coerce_metadata(
    metadata: Mapping[MetadataKey | str, object] | None,
    error_type: type[InvalidDataSourceSpecError | InvalidDataSourceScanResultError],
) -> dict[MetadataKey, FrozenPrimitive]:
    if metadata is None:
        return {}
    if not isinstance(metadata, Mapping):
        raise error_type(
            "Datasource metadata must be a mapping.",
            field="metadata",
            actual=type(metadata).__name__,
        )
    return {
        MetadataKey(key): freeze_primitive(
            value,
            error_type=error_type,
            field="metadata",
        )
        for key, value in metadata.items()
    }


def _coerce_strings(
    values: Sequence[str],
    *,
    field: str,
    error_type: type[InvalidDataSourceScanResultError],
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise error_type(
            "Datasource scan diagnostic values must be a sequence.",
            field=field,
            actual=type(values).__name__,
        )
    coerced: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value:
            raise error_type(
                "Datasource scan diagnostic values must be non-empty strings.",
                field=field,
                actual=type(value).__name__,
                value=value,
            )
        coerced.append(value)
    return tuple(coerced)


def _coerce_rejections(value: Mapping[str, str] | None) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise InvalidDataSourceScanResultError(
            "DataSourceScanResult rejected_record_ids must be a mapping.",
            field="rejected_record_ids",
            actual=type(value).__name__,
        )
    rejected: dict[str, str] = {}
    for record_id, reason in value.items():
        if not isinstance(record_id, str) or not record_id:
            raise InvalidDataSourceScanResultError(
                "Rejected record IDs must be non-empty strings.",
                field="rejected_record_ids",
                record_id=record_id,
            )
        if not isinstance(reason, str) or not reason:
            raise InvalidDataSourceScanResultError(
                "Rejected record reasons must be non-empty strings.",
                field="rejected_record_ids",
                record_id=record_id,
                actual=type(reason).__name__,
            )
        rejected[record_id] = reason
    return rejected


def _records_from_dicts(value: object) -> tuple[RecordRef, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise InvalidDataSourceScanResultError(
            "Serialized scan records must be a sequence.",
            field="records",
            actual=type(value).__name__,
        )
    return tuple(RecordRef.from_dict(record) for record in value)


def _require_keys(
    value: Mapping[str, object],
    keys: set[str],
    *,
    error_type: type[InvalidDataSourceSpecError | InvalidDataSourceScanResultError],
    descriptor: str,
) -> None:
    actual = set(value)
    if actual != keys:
        raise error_type(
            "Serialized datasource scan keys do not match the Stage 5 schema.",
            descriptor=descriptor,
            expected=sorted(keys),
            actual=sorted(actual),
        )
