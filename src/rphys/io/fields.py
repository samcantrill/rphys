"""Lazy logical field descriptors and field-native views.

``FieldRef`` names a logical field by intrinsic ``DataKey`` and ordered
``ResourceRef`` descriptors. ``FieldView`` optionally adds a field-native
``FieldIndex`` request. Neither object carries runtime roles, payloads, open
handles, codec dispatch, loading behavior, or cross-field alignment policy.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Self

from rphys.data.keys import DataKey
from rphys.data.metadata import MetadataKey
from rphys.data.schemas import SchemaName
from rphys.errors import InvalidFieldRefError, InvalidFieldViewError

from ._primitives import (
    FrozenPrimitive,
    freeze_primitive,
    require_exact_keys,
    require_mapping,
    thaw_primitive,
)
from .indexes import FieldIndex, _field_index_from_dict
from .resources import ResourceRef

__all__ = ["FieldRef", "FieldView"]


@dataclass(frozen=True, init=False, slots=True)
class FieldRef:
    """Serializable descriptor for a complete logical field.

    ``resources`` preserves caller-provided order as descriptor data only. It
    does not imply selector, priority, canonical resource identity, compound
    member semantics, or codec binding policy.
    """

    key: DataKey
    resources: tuple[ResourceRef, ...]
    schema: SchemaName | None
    metadata: Mapping[MetadataKey, FrozenPrimitive]

    def __init__(
        self,
        key: DataKey | str,
        resources: Sequence[ResourceRef],
        schema: SchemaName | str | None = None,
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        object.__setattr__(self, "key", DataKey(key))
        object.__setattr__(self, "resources", _coerce_resources(resources))
        object.__setattr__(
            self,
            "schema",
            SchemaName(schema) if schema is not None else None,
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata)),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize to primitive values without payloads or manifest fields."""

        return {
            "key": str(self.key),
            "resources": [resource.to_dict() for resource in self.resources],
            "schema": str(self.schema) if self.schema is not None else None,
            "metadata": {
                str(key): thaw_primitive(value)
                for key, value in self.metadata.items()
            },
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct a field descriptor from ``to_dict`` output."""

        data = require_mapping(
            value,
            error_type=InvalidFieldRefError,
            field="field_ref",
        )
        require_exact_keys(
            data,
            {"key", "resources", "schema", "metadata"},
            error_type=InvalidFieldRefError,
            descriptor="FieldRef",
        )
        resources = _resources_from_dicts(data["resources"])
        return cls(
            data["key"],  # type: ignore[arg-type]
            resources,
            schema=data["schema"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
        )


FieldRef.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class FieldView:
    """Lazy view of a field with an optional field-native index.

    Numeric index values are local to ``field_ref``. Stage 3 does not infer
    temporal alignment, resampling, padding, or seconds conversion between two
    ``FieldView`` instances, even when their numeric slices match.
    """

    field_ref: FieldRef
    field_index: FieldIndex | None

    def __init__(
        self,
        field_ref: FieldRef,
        field_index: FieldIndex | None = None,
    ) -> None:
        if not isinstance(field_ref, FieldRef):
            raise InvalidFieldViewError(
                "FieldView field_ref must be a FieldRef.",
                field="field_ref",
                actual=type(field_ref).__name__,
            )
        if field_index is not None and not isinstance(field_index, FieldIndex):
            raise InvalidFieldViewError(
                "FieldView field_index must be a FieldIndex or None.",
                field="field_index",
                actual=type(field_index).__name__,
            )

        object.__setattr__(self, "field_ref", field_ref)
        object.__setattr__(self, "field_index", field_index)

    def to_dict(self) -> dict[str, object]:
        """Serialize the field view with no payload or alignment metadata."""

        return {
            "field_ref": self.field_ref.to_dict(),
            "field_index": (
                self.field_index.to_dict() if self.field_index is not None else None
            ),
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct a field view from ``to_dict`` output."""

        data = require_mapping(
            value,
            error_type=InvalidFieldViewError,
            field="field_view",
        )
        require_exact_keys(
            data,
            {"field_ref", "field_index"},
            error_type=InvalidFieldViewError,
            descriptor="FieldView",
        )
        field_index = (
            _field_index_from_dict(data["field_index"])
            if data["field_index"] is not None
            else None
        )
        return cls(FieldRef.from_dict(data["field_ref"]), field_index)


FieldView.__hash__ = None  # type: ignore[assignment]


def _coerce_resources(resources: Sequence[ResourceRef]) -> tuple[ResourceRef, ...]:
    if (
        isinstance(resources, (str, bytes))
        or not isinstance(resources, Sequence)
        or len(resources) == 0
    ):
        raise InvalidFieldRefError(
            "FieldRef resources must be a non-empty sequence.",
            field="resources",
            actual=type(resources).__name__,
        )

    coerced = tuple(resources)
    for resource in coerced:
        if not isinstance(resource, ResourceRef):
            raise InvalidFieldRefError(
                "FieldRef resources must contain ResourceRef instances.",
                field="resources",
                actual=type(resource).__name__,
            )
    return coerced


def _coerce_metadata(
    metadata: Mapping[MetadataKey | str, object] | None,
) -> dict[MetadataKey, FrozenPrimitive]:
    if metadata is None:
        return {}
    if not isinstance(metadata, Mapping):
        raise InvalidFieldRefError(
            "FieldRef metadata must be a mapping.",
            field="metadata",
            actual=type(metadata).__name__,
        )

    return {
        MetadataKey(key): freeze_primitive(
            value,
            error_type=InvalidFieldRefError,
            field="metadata",
        )
        for key, value in metadata.items()
    }


def _resources_from_dicts(value: object) -> tuple[ResourceRef, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise InvalidFieldRefError(
            "Serialized FieldRef resources must be a sequence.",
            field="resources",
            actual=type(value).__name__,
        )
    return tuple(ResourceRef.from_dict(resource) for resource in value)
