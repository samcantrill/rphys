"""Descriptor-only derived datasource assembly from export evidence.

Stage 8 derived assembly converts in-memory field export results into ordinary
``DataSourceRef`` and ``RecordRef`` descriptors. It does not save fields, scan
output directories, write manifests, reuse datasource-index manifests, cache
payloads, or define prediction/evaluation behavior.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

from rphys.data.keys import DataKey
from rphys.data.metadata import MetadataKey
from rphys.errors import RemotePhysDataSourceError
from rphys.io._primitives import FrozenPrimitive, freeze_primitive
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef

from .refs import DataSourceRef, RecordRef

if TYPE_CHECKING:
    from rphys.ops.export import (
        ExportResult,
        FieldExportResult,
        RecordExportResult,
    )

__all__ = ["DerivedDataSourceAssembly", "DerivedDataSourceBuilder"]


@dataclass(frozen=True, init=False, slots=True)
class DerivedDataSourceAssembly:
    """In-memory descriptor assembly for a derived datasource.

    ``datasource`` is the new derived descriptor, ``records`` are ordered
    derived records using exported target fields, and ``field_results`` retains
    the successful export evidence used to create those records. Source
    descriptors are retained as immutable provenance only.
    """

    datasource: DataSourceRef
    records: tuple[RecordRef, ...]
    field_results: tuple["FieldExportResult", ...]
    source_records: tuple[RecordRef, ...]
    source_datasources: tuple[DataSourceRef, ...]
    metadata: Mapping[MetadataKey, FrozenPrimitive]

    def __init__(
        self,
        *,
        datasource: DataSourceRef,
        records: Sequence[RecordRef],
        field_results: Sequence["FieldExportResult"],
        source_records: Sequence[RecordRef],
        source_datasources: Sequence[DataSourceRef],
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        if not isinstance(datasource, DataSourceRef):
            raise RemotePhysDataSourceError(
                "DerivedDataSourceAssembly datasource must be a DataSourceRef.",
                field="datasource",
                actual=type(datasource).__name__,
            )
        record_tuple = _coerce_derived_records(records, datasource)
        result_tuple = _coerce_successful_field_results(field_results)
        source_record_tuple = _coerce_source_records(source_records)
        source_datasource_tuple = _coerce_source_datasources(source_datasources)
        object.__setattr__(self, "datasource", datasource)
        object.__setattr__(self, "records", record_tuple)
        object.__setattr__(self, "field_results", result_tuple)
        object.__setattr__(self, "source_records", source_record_tuple)
        object.__setattr__(self, "source_datasources", source_datasource_tuple)
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata)),
        )

    @property
    def record_count(self) -> int:
        """Number of derived records assembled."""

        return len(self.records)

    @property
    def field_count(self) -> int:
        """Number of successful exported fields represented."""

        return len(self.field_results)


DerivedDataSourceAssembly.__hash__ = None  # type: ignore[assignment]


class DerivedDataSourceBuilder:
    """Build descriptor-only derived datasource assemblies from export results."""

    __slots__ = ("datasource",)

    def __init__(
        self,
        datasource_id: str,
        *,
        source: ResourceRef | None = None,
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        self.datasource = DataSourceRef(
            datasource_id,
            source=source,
            metadata=metadata,
        )

    def from_export_result(self, export_result: "ExportResult") -> DerivedDataSourceAssembly:
        """Assemble from one in-memory export result without reading outputs."""

        export_result_type, _, _ = _export_result_types()
        if not isinstance(export_result, export_result_type):
            raise RemotePhysDataSourceError(
                "DerivedDataSourceBuilder requires an ExportResult.",
                field="export_result",
                actual=type(export_result).__name__,
            )
        return self.from_record_results(export_result.record_results)

    def from_record_results(
        self,
        record_results: Sequence["RecordExportResult"],
    ) -> DerivedDataSourceAssembly:
        """Assemble from ordered per-record export evidence."""

        _, record_result_type, _ = _export_result_types()
        if (
            isinstance(record_results, (str, bytes))
            or not isinstance(record_results, Sequence)
            or not record_results
        ):
            raise RemotePhysDataSourceError(
                "DerivedDataSourceBuilder record_results must be a non-empty sequence.",
                field="record_results",
                actual=type(record_results).__name__,
            )
        flattened = []
        for record_result in record_results:
            if not isinstance(record_result, record_result_type):
                raise RemotePhysDataSourceError(
                    "DerivedDataSourceBuilder record_results must contain RecordExportResult values.",
                    field="record_results",
                    actual=type(record_result).__name__,
                )
            flattened.extend(record_result.field_results)
        return self.from_field_results(flattened)

    def from_field_results(
        self,
        field_results: Sequence["FieldExportResult"],
    ) -> DerivedDataSourceAssembly:
        """Assemble derived records from successful field export evidence."""

        usable_results = _usable_field_results(field_results)
        grouped = _group_results_by_source_record(usable_results)
        records = []
        source_records = []
        for source_record, results in grouped:
            source_records.append(source_record)
            records.append(_derive_record(self.datasource, source_record, results))
        return DerivedDataSourceAssembly(
            datasource=self.datasource,
            records=records,
            field_results=usable_results,
            source_records=source_records,
            source_datasources=_source_datasources(source_records),
            metadata={
                "derived.record_count": len(records),
                "derived.field_count": len(usable_results),
            },
        )


def _export_result_types() -> tuple[type[object], type[object], type[object]]:
    from rphys.ops.export import ExportResult, FieldExportResult, RecordExportResult

    return ExportResult, RecordExportResult, FieldExportResult


def _failed_outcome() -> object:
    from rphys.ops.export import FieldExportOutcome

    return FieldExportOutcome.FAILED


def _usable_field_results(
    field_results: Sequence["FieldExportResult"],
) -> tuple["FieldExportResult", ...]:
    _, _, field_result_type = _export_result_types()
    failed_outcome = _failed_outcome()
    if (
        isinstance(field_results, (str, bytes))
        or not isinstance(field_results, Sequence)
        or not field_results
    ):
        raise RemotePhysDataSourceError(
            "DerivedDataSourceBuilder field_results must be a non-empty sequence.",
            field="field_results",
            actual=type(field_results).__name__,
        )
    usable = []
    for result in field_results:
        if not isinstance(result, field_result_type):
            raise RemotePhysDataSourceError(
                "DerivedDataSourceBuilder field_results must contain FieldExportResult values.",
                field="field_results",
                actual=type(result).__name__,
            )
        if result.outcome == failed_outcome:
            continue
        usable.append(result)
    if not usable:
        raise RemotePhysDataSourceError(
            "Derived datasource assembly requires at least one successful field export result.",
            field="field_results",
        )
    return tuple(usable)


def _group_results_by_source_record(
    field_results: tuple["FieldExportResult", ...],
) -> tuple[tuple[RecordRef, tuple["FieldExportResult", ...]], ...]:
    records: dict[tuple[str, str], RecordRef] = {}
    grouped: dict[tuple[str, str], list["FieldExportResult"]] = {}
    order: list[tuple[str, str]] = []
    for result in field_results:
        key = (
            result.source_record.datasource.datasource_id,
            result.source_record.record_id,
        )
        existing = records.get(key)
        if existing is None:
            records[key] = result.source_record
            grouped[key] = []
            order.append(key)
        elif existing != result.source_record:
            raise RemotePhysDataSourceError(
                "Derived datasource assembly cannot merge different source descriptors with one identity.",
                field="source_record",
                datasource_id=key[0],
                record_id=key[1],
            )
        grouped[key].append(result)
    return tuple((records[key], tuple(grouped[key])) for key in order)


def _derive_record(
    datasource: DataSourceRef,
    source_record: RecordRef,
    field_results: tuple["FieldExportResult", ...],
) -> RecordRef:
    fields: dict[DataKey, FieldRef] = {}
    for result in field_results:
        field = _target_field(result)
        if field.key in fields:
            raise RemotePhysDataSourceError(
                "Derived datasource assembly found duplicate target fields for one record.",
                field="field_results",
                record_id=source_record.record_id,
                field_key=str(field.key),
            )
        fields[field.key] = field
    return RecordRef(
        datasource,
        source_record.record_id,
        fields,
        metadata={
            **dict(source_record.metadata),
            "derived.source_datasource_id": source_record.datasource.datasource_id,
            "derived.source_record_id": source_record.record_id,
            "derived.field_count": len(fields),
        },
    )


def _target_field(result: "FieldExportResult") -> FieldRef:
    if result.target.resources == result.target_resources:
        return result.target
    return FieldRef(
        result.target.key,
        result.target_resources,
        schema=result.target.schema,
        metadata=result.target.metadata,
    )


def _source_datasources(source_records: Sequence[RecordRef]) -> tuple[DataSourceRef, ...]:
    by_id: dict[str, DataSourceRef] = {}
    ordered: list[DataSourceRef] = []
    for record in source_records:
        datasource = record.datasource
        existing = by_id.get(datasource.datasource_id)
        if existing is None:
            by_id[datasource.datasource_id] = datasource
            ordered.append(datasource)
        elif existing != datasource:
            raise RemotePhysDataSourceError(
                "Derived datasource assembly cannot merge different datasource descriptors with one identity.",
                field="source_datasources",
                datasource_id=datasource.datasource_id,
            )
    return tuple(ordered)


def _coerce_derived_records(
    records: Sequence[RecordRef],
    datasource: DataSourceRef,
) -> tuple[RecordRef, ...]:
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence) or not records:
        raise RemotePhysDataSourceError(
            "DerivedDataSourceAssembly records must be a non-empty sequence.",
            field="records",
            actual=type(records).__name__,
        )
    coerced = tuple(records)
    seen: set[str] = set()
    for record in coerced:
        if not isinstance(record, RecordRef):
            raise RemotePhysDataSourceError(
                "DerivedDataSourceAssembly records must contain RecordRef values.",
                field="records",
                actual=type(record).__name__,
            )
        if record.datasource != datasource:
            raise RemotePhysDataSourceError(
                "Derived records must reference the assembly datasource.",
                field="records",
                record_id=record.record_id,
            )
        if record.record_id in seen:
            raise RemotePhysDataSourceError(
                "Derived records must have unique record_id values.",
                field="records",
                record_id=record.record_id,
            )
        seen.add(record.record_id)
    return coerced


def _coerce_successful_field_results(
    field_results: Sequence["FieldExportResult"],
) -> tuple["FieldExportResult", ...]:
    coerced = _usable_field_results(field_results)
    return coerced


def _coerce_source_records(records: Sequence[RecordRef]) -> tuple[RecordRef, ...]:
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence) or not records:
        raise RemotePhysDataSourceError(
            "DerivedDataSourceAssembly source_records must be a non-empty sequence.",
            field="source_records",
            actual=type(records).__name__,
        )
    coerced = tuple(records)
    for record in coerced:
        if not isinstance(record, RecordRef):
            raise RemotePhysDataSourceError(
                "DerivedDataSourceAssembly source_records must contain RecordRef values.",
                field="source_records",
                actual=type(record).__name__,
            )
    return coerced


def _coerce_source_datasources(
    datasources: Sequence[DataSourceRef],
) -> tuple[DataSourceRef, ...]:
    if (
        isinstance(datasources, (str, bytes))
        or not isinstance(datasources, Sequence)
        or not datasources
    ):
        raise RemotePhysDataSourceError(
            "DerivedDataSourceAssembly source_datasources must be a non-empty sequence.",
            field="source_datasources",
            actual=type(datasources).__name__,
        )
    coerced = tuple(datasources)
    for datasource in coerced:
        if not isinstance(datasource, DataSourceRef):
            raise RemotePhysDataSourceError(
                "DerivedDataSourceAssembly source_datasources must contain DataSourceRef values.",
                field="source_datasources",
                actual=type(datasource).__name__,
            )
    return coerced


def _coerce_metadata(
    metadata: Mapping[MetadataKey | str, object] | None,
) -> dict[MetadataKey, FrozenPrimitive]:
    if metadata is None:
        return {}
    if not isinstance(metadata, Mapping):
        raise RemotePhysDataSourceError(
            "Derived datasource metadata must be a mapping.",
            field="metadata",
            actual=type(metadata).__name__,
        )
    return {
        MetadataKey(key): freeze_primitive(
            value,
            error_type=RemotePhysDataSourceError,
            field="metadata",
        )
        for key, value in metadata.items()
    }
