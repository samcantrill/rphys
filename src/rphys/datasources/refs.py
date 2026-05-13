"""Lazy datasource and record provenance descriptors.

``DataSourceRef`` and ``RecordRef`` preserve datasource identity, record
identity, declared field presence, and primitive metadata. They do not scan
datasources, filter records, build splits, validate payloads, load resources,
create manifests, or define cache fingerprints.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Self

from rphys.data.keys import DataKey
from rphys.data.metadata import MetadataKey
from rphys.errors import InvalidDataSourceRefError, InvalidRecordRefError
from rphys.io._primitives import (
    FrozenPrimitive,
    freeze_primitive,
    require_exact_keys,
    require_mapping,
    thaw_primitive,
)
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef

from .schemas import DataSourceSchema

__all__ = ["DataSourceRef", "RecordRef"]


@dataclass(frozen=True, init=False, slots=True)
class DataSourceRef:
    """Serializable datasource provenance descriptor.

    ``datasource_id`` is mandatory stable datasource identity for Stage 3.
    ``source`` can point to a top-level resource, and ``schema`` can declare
    expected fields, but both remain descriptor data only. Leakage-sensitive
    values such as source, subject, split, and group IDs stay in metadata.
    """

    datasource_id: str
    source: ResourceRef | None
    schema: DataSourceSchema | None
    metadata: Mapping[MetadataKey, FrozenPrimitive]

    def __init__(
        self,
        datasource_id: str,
        source: ResourceRef | None = None,
        schema: DataSourceSchema | None = None,
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "datasource_id",
            _non_empty_string(
                datasource_id,
                field="datasource_id",
                error_type=InvalidDataSourceRefError,
            ),
        )
        if source is not None and not isinstance(source, ResourceRef):
            raise InvalidDataSourceRefError(
                "DataSourceRef source must be a ResourceRef or None.",
                field="source",
                actual=type(source).__name__,
            )
        if schema is not None and not isinstance(schema, DataSourceSchema):
            raise InvalidDataSourceRefError(
                "DataSourceRef schema must be a DataSourceSchema or None.",
                field="schema",
                actual=type(schema).__name__,
            )
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "schema", schema)
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                _coerce_metadata(
                    metadata,
                    error_type=InvalidDataSourceRefError,
                    owner="DataSourceRef",
                )
            ),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize without manifest, fingerprint, or validation evidence."""

        return {
            "datasource_id": self.datasource_id,
            "source": self.source.to_dict() if self.source is not None else None,
            "schema": self.schema.to_dict() if self.schema is not None else None,
            "metadata": {
                str(key): thaw_primitive(value)
                for key, value in self.metadata.items()
            },
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct a datasource descriptor from ``to_dict`` output."""

        data = require_mapping(
            value,
            error_type=InvalidDataSourceRefError,
            field="datasource_ref",
        )
        require_exact_keys(
            data,
            {"datasource_id", "source", "schema", "metadata"},
            error_type=InvalidDataSourceRefError,
            descriptor="DataSourceRef",
        )
        source = (
            ResourceRef.from_dict(data["source"]) if data["source"] is not None else None
        )
        schema = (
            DataSourceSchema.from_dict(data["schema"])
            if data["schema"] is not None
            else None
        )
        return cls(
            data["datasource_id"],  # type: ignore[arg-type]
            source=source,
            schema=schema,
            metadata=data["metadata"],  # type: ignore[arg-type]
        )


DataSourceRef.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class RecordRef:
    """Serializable descriptor for one datasource record.

    ``fields`` is a non-empty intrinsic ``DataKey -> FieldRef`` mapping. Every
    mapping key must match ``FieldRef.key`` so record membership is explicit
    before later windowing or sample-building stages consume the record.
    """

    datasource: DataSourceRef
    record_id: str
    fields: Mapping[DataKey, FieldRef]
    metadata: Mapping[MetadataKey, FrozenPrimitive]

    def __init__(
        self,
        datasource: DataSourceRef,
        record_id: str,
        fields: Mapping[DataKey | str, FieldRef],
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        if not isinstance(datasource, DataSourceRef):
            raise InvalidRecordRefError(
                "RecordRef datasource must be a DataSourceRef.",
                field="datasource",
                actual=type(datasource).__name__,
            )
        object.__setattr__(self, "datasource", datasource)
        object.__setattr__(
            self,
            "record_id",
            _non_empty_string(
                record_id,
                field="record_id",
                error_type=InvalidRecordRefError,
            ),
        )
        object.__setattr__(self, "fields", MappingProxyType(_coerce_fields(fields)))
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                _coerce_metadata(
                    metadata,
                    error_type=InvalidRecordRefError,
                    owner="RecordRef",
                )
            ),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize record membership without datasource-index identity."""

        return {
            "datasource": self.datasource.to_dict(),
            "record_id": self.record_id,
            "fields": {
                str(key): field_ref.to_dict()
                for key, field_ref in self.fields.items()
            },
            "metadata": {
                str(key): thaw_primitive(value)
                for key, value in self.metadata.items()
            },
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct a record descriptor from ``to_dict`` output."""

        data = require_mapping(
            value,
            error_type=InvalidRecordRefError,
            field="record_ref",
        )
        require_exact_keys(
            data,
            {"datasource", "record_id", "fields", "metadata"},
            error_type=InvalidRecordRefError,
            descriptor="RecordRef",
        )
        raw_fields = require_mapping(
            data["fields"],
            error_type=InvalidRecordRefError,
            field="fields",
        )
        fields = {
            key: FieldRef.from_dict(field_ref)
            for key, field_ref in raw_fields.items()
        }
        return cls(
            DataSourceRef.from_dict(data["datasource"]),
            data["record_id"],  # type: ignore[arg-type]
            fields,
            metadata=data["metadata"],  # type: ignore[arg-type]
        )


RecordRef.__hash__ = None  # type: ignore[assignment]


def _coerce_fields(fields: Mapping[DataKey | str, FieldRef]) -> dict[DataKey, FieldRef]:
    if not isinstance(fields, Mapping) or not fields:
        raise InvalidRecordRefError(
            "RecordRef fields must be a non-empty mapping.",
            field="fields",
            actual=type(fields).__name__,
        )

    coerced: dict[DataKey, FieldRef] = {}
    for key, field_ref in fields.items():
        data_key = DataKey(key)
        if not isinstance(field_ref, FieldRef):
            raise InvalidRecordRefError(
                "RecordRef fields must contain FieldRef values.",
                field="fields",
                key=str(data_key),
                actual=type(field_ref).__name__,
            )
        if field_ref.key != data_key:
            raise InvalidRecordRefError(
                "RecordRef mapping key must match FieldRef.key.",
                field="fields",
                key=str(data_key),
                field_ref_key=str(field_ref.key),
            )
        coerced[data_key] = field_ref
    return coerced


def _coerce_metadata(
    metadata: Mapping[MetadataKey | str, object] | None,
    *,
    error_type: type[InvalidDataSourceRefError] | type[InvalidRecordRefError],
    owner: str,
) -> dict[MetadataKey, FrozenPrimitive]:
    if metadata is None:
        return {}
    if not isinstance(metadata, Mapping):
        raise error_type(
            f"{owner} metadata must be a mapping.",
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


def _non_empty_string(
    value: object,
    *,
    field: str,
    error_type: type[InvalidDataSourceRefError] | type[InvalidRecordRefError],
) -> str:
    if not isinstance(value, str) or not value:
        raise error_type(
            "Datasource descriptor IDs must be non-empty strings.",
            field=field,
            actual=type(value).__name__,
            value=value,
        )
    return value
