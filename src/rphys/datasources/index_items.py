"""Role-qualified lazy index item descriptors.

``IndexItem`` is the Stage 3 unit that later sample builders can consume. It
maps runtime ``FieldLocator`` roles to lazy ``FieldView`` descriptors while
preserving mandatory ``RecordRef`` provenance. It does not construct runtime
samples, load payloads, align fields, apply transforms, define item identity, or
own datasource-index manifests.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Self

from rphys.data.locators import FieldLocator
from rphys.data.metadata import MetadataKey
from rphys.errors import InvalidIndexItemError
from rphys.io._primitives import (
    FrozenPrimitive,
    freeze_primitive,
    require_exact_keys,
    require_mapping,
    thaw_primitive,
)
from rphys.io.fields import FieldView

from .refs import RecordRef

__all__ = ["IndexItem"]


@dataclass(frozen=True, init=False, slots=True)
class IndexItem:
    """Pure lazy IO item with role-qualified field views.

    ``fields`` is a non-empty ``FieldLocator -> FieldView`` mapping. The
    locator's intrinsic ``DataKey`` must match the view's ``FieldRef.key``, and
    every view field key must be present in ``record.fields``. Matching numeric
    indexes across views do not imply alignment.
    """

    fields: Mapping[FieldLocator, FieldView]
    record: RecordRef
    metadata: Mapping[MetadataKey, FrozenPrimitive]

    def __init__(
        self,
        fields: Mapping[FieldLocator | str, FieldView],
        record: RecordRef,
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        if not isinstance(record, RecordRef):
            raise InvalidIndexItemError(
                "IndexItem record must be a RecordRef.",
                field="record",
                actual=type(record).__name__,
            )
        object.__setattr__(self, "record", record)
        object.__setattr__(
            self,
            "fields",
            MappingProxyType(_coerce_fields(fields, record=record)),
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata)),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize without payloads, item IDs, fingerprints, or manifests."""

        return {
            "fields": {
                str(locator): view.to_dict()
                for locator, view in self.fields.items()
            },
            "record": self.record.to_dict(),
            "metadata": {
                str(key): thaw_primitive(value)
                for key, value in self.metadata.items()
            },
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct an index item from ``to_dict`` output."""

        data = require_mapping(
            value,
            error_type=InvalidIndexItemError,
            field="index_item",
        )
        require_exact_keys(
            data,
            {"fields", "record", "metadata"},
            error_type=InvalidIndexItemError,
            descriptor="IndexItem",
        )
        raw_fields = require_mapping(
            data["fields"],
            error_type=InvalidIndexItemError,
            field="fields",
        )
        fields = {
            locator: FieldView.from_dict(view)
            for locator, view in raw_fields.items()
        }
        return cls(
            fields,
            RecordRef.from_dict(data["record"]),
            metadata=data["metadata"],  # type: ignore[arg-type]
        )


IndexItem.__hash__ = None  # type: ignore[assignment]


def _coerce_fields(
    fields: Mapping[FieldLocator | str, FieldView],
    *,
    record: RecordRef,
) -> dict[FieldLocator, FieldView]:
    if not isinstance(fields, Mapping) or not fields:
        raise InvalidIndexItemError(
            "IndexItem fields must be a non-empty mapping.",
            field="fields",
            actual=type(fields).__name__,
        )

    coerced: dict[FieldLocator, FieldView] = {}
    for locator, view in fields.items():
        field_locator = _coerce_locator(locator)
        if not isinstance(view, FieldView):
            raise InvalidIndexItemError(
                "IndexItem fields must contain FieldView values.",
                field="fields",
                locator=str(field_locator),
                actual=type(view).__name__,
            )
        if field_locator.key != view.field_ref.key:
            raise InvalidIndexItemError(
                "IndexItem locator key must match FieldView.field_ref.key.",
                field="fields",
                locator=str(field_locator),
                locator_key=str(field_locator.key),
                field_ref_key=str(view.field_ref.key),
            )
        if view.field_ref.key not in record.fields:
            raise InvalidIndexItemError(
                "IndexItem view field key must be present in RecordRef.fields.",
                field="fields",
                locator=str(field_locator),
                field_ref_key=str(view.field_ref.key),
                record_fields=[str(key) for key in record.fields],
            )
        coerced[field_locator] = view
    return coerced


def _coerce_locator(value: FieldLocator | str) -> FieldLocator:
    if isinstance(value, FieldLocator):
        return value
    return FieldLocator.parse(value)


def _coerce_metadata(
    metadata: Mapping[MetadataKey | str, object] | None,
) -> dict[MetadataKey, FrozenPrimitive]:
    if metadata is None:
        return {}
    if not isinstance(metadata, Mapping):
        raise InvalidIndexItemError(
            "IndexItem metadata must be a mapping.",
            field="metadata",
            actual=type(metadata).__name__,
        )
    return {
        MetadataKey(key): freeze_primitive(
            value,
            error_type=InvalidIndexItemError,
            field="metadata",
        )
        for key, value in metadata.items()
    }
