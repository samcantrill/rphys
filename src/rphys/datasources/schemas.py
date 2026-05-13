"""Declaration-only datasource schema descriptors.

``DataSourceSchema`` declares which logical fields a datasource or datasource
view is expected to expose. It reuses ``FieldSpec`` vocabulary but does not
load payloads, scan records, validate observed data, distinguish expected from
observed fields, or carry validation evidence, schema versions, manifests, or
fingerprints.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Self

from rphys.data.fields import FieldSpec
from rphys.data.keys import DataKey
from rphys.data.metadata import MetadataKey
from rphys.data.types import DataType
from rphys.errors import InvalidDataSourceSchemaError
from rphys.io._primitives import (
    FrozenPrimitive,
    freeze_primitive,
    require_exact_keys,
    require_mapping,
    thaw_primitive,
)

__all__ = ["DataSourceSchema"]


@dataclass(frozen=True, init=False, slots=True)
class DataSourceSchema:
    """Minimal structural declaration for datasource fields.

    ``fields`` is a non-empty intrinsic ``DataKey -> FieldSpec`` mapping. The
    mapping key must match ``FieldSpec.key`` so schema declarations cannot
    silently drift from the field identity used by records and views.
    """

    fields: Mapping[DataKey, FieldSpec]
    metadata: Mapping[MetadataKey, FrozenPrimitive]

    def __init__(
        self,
        fields: Mapping[DataKey | str, FieldSpec],
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        object.__setattr__(self, "fields", MappingProxyType(_coerce_fields(fields)))
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata)),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize declarations without validation evidence or version fields."""

        return {
            "fields": {
                str(key): _field_spec_to_dict(spec)
                for key, spec in self.fields.items()
            },
            "metadata": {
                str(key): thaw_primitive(value)
                for key, value in self.metadata.items()
            },
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct a declaration-only schema from ``to_dict`` output."""

        data = require_mapping(
            value,
            error_type=InvalidDataSourceSchemaError,
            field="datasource_schema",
        )
        require_exact_keys(
            data,
            {"fields", "metadata"},
            error_type=InvalidDataSourceSchemaError,
            descriptor="DataSourceSchema",
        )
        raw_fields = require_mapping(
            data["fields"],
            error_type=InvalidDataSourceSchemaError,
            field="fields",
        )
        fields = {
            key: _field_spec_from_dict(spec)
            for key, spec in raw_fields.items()
        }
        return cls(fields, metadata=data["metadata"])  # type: ignore[arg-type]


DataSourceSchema.__hash__ = None  # type: ignore[assignment]


def _coerce_fields(fields: Mapping[DataKey | str, FieldSpec]) -> dict[DataKey, FieldSpec]:
    if not isinstance(fields, Mapping) or not fields:
        raise InvalidDataSourceSchemaError(
            "DataSourceSchema fields must be a non-empty mapping.",
            field="fields",
            actual=type(fields).__name__,
        )

    coerced: dict[DataKey, FieldSpec] = {}
    for key, spec in fields.items():
        data_key = DataKey(key)
        if not isinstance(spec, FieldSpec):
            raise InvalidDataSourceSchemaError(
                "DataSourceSchema fields must contain FieldSpec values.",
                field="fields",
                key=str(data_key),
                actual=type(spec).__name__,
            )
        if spec.key != data_key:
            raise InvalidDataSourceSchemaError(
                "DataSourceSchema mapping key must match FieldSpec.key.",
                field="fields",
                key=str(data_key),
                spec_key=str(spec.key),
            )
        coerced[data_key] = spec
    return coerced


def _coerce_metadata(
    metadata: Mapping[MetadataKey | str, object] | None,
) -> dict[MetadataKey, FrozenPrimitive]:
    if metadata is None:
        return {}
    if not isinstance(metadata, Mapping):
        raise InvalidDataSourceSchemaError(
            "DataSourceSchema metadata must be a mapping.",
            field="metadata",
            actual=type(metadata).__name__,
        )
    return {
        MetadataKey(key): freeze_primitive(
            value,
            error_type=InvalidDataSourceSchemaError,
            field="metadata",
        )
        for key, value in metadata.items()
    }


def _field_spec_to_dict(spec: FieldSpec) -> dict[str, object]:
    return {
        "key": str(spec.key),
        "data_type": str(spec.data_type),
        "schema": str(spec.schema) if spec.schema is not None else None,
    }


def _field_spec_from_dict(value: object) -> FieldSpec:
    data = require_mapping(
        value,
        error_type=InvalidDataSourceSchemaError,
        field="field_spec",
    )
    require_exact_keys(
        data,
        {"key", "data_type", "schema"},
        error_type=InvalidDataSourceSchemaError,
        descriptor="FieldSpec",
    )
    return FieldSpec(
        data["key"],  # type: ignore[arg-type]
        DataType(data["data_type"]),  # type: ignore[arg-type]
        data["schema"],  # type: ignore[arg-type]
    )
