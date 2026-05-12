"""Loaded runtime field specifications and payload wrappers.

``FieldSpec`` names a loaded field by intrinsic data key, broad data category,
and optional schema identity. It does not define shape, dtype, sample-rate,
coordinate-frame, serialization, or backend-specific payload rules.

``FieldValue`` wraps an already loaded payload with optional schema, metadata,
and collation policy. Payloads are intentionally compared by wrapper identity
only so tensor-like objects are never compared by value accidentally.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Mapping, Self

from rphys.data.keys import DataKey
from rphys.data.metadata import MetadataKey
from rphys.data.schemas import SchemaName
from rphys.data.types import DataType

__all__ = ["FieldSpec", "FieldValue"]


@dataclass(slots=True)
class FieldSpec:
    """Minimal value descriptor for a runtime field.

    Construction coerces Stage 1 vocabulary values and intentionally avoids
    scientific schema details such as shapes, units, axes, sample rates,
    coordinate frames, or runtime payload types. Equality is value-based across
    the three declared fields only.
    """

    key: DataKey
    data_type: DataType
    schema: SchemaName | None = None

    def __post_init__(self) -> None:
        self.key = DataKey(self.key)
        self.data_type = DataType(self.data_type)
        if self.schema is not None:
            self.schema = SchemaName(self.schema)


class FieldValue:
    """Identity-equality wrapper around one loaded payload.

    Metadata is shallow-copied on construction and on ``copy.copy``; nested
    metadata values remain shared by design. ``copy.deepcopy`` delegates to
    Python for payload and metadata copying, so non-copyable payloads fail
    through the underlying payload error rather than a serialization fallback.
    """

    __slots__ = ("payload", "schema", "metadata", "collate_policy")

    payload: Any
    schema: SchemaName | None
    metadata: dict[MetadataKey, object]
    collate_policy: object | None

    def __init__(
        self,
        payload: Any,
        *,
        schema: SchemaName | str | None = None,
        metadata: Mapping[MetadataKey | str, object] | None = None,
        collate_policy: object | None = None,
    ) -> None:
        self.payload = payload
        self.schema = SchemaName(schema) if schema is not None else None
        self.metadata = _coerce_metadata(metadata)
        self.collate_policy = _coerce_collate_policy(collate_policy)

    def __copy__(self) -> Self:
        return type(self)(
            self.payload,
            schema=self.schema,
            metadata=self.metadata,
            collate_policy=self.collate_policy,
        )

    def __deepcopy__(self, memo: dict[int, object]) -> Self:
        return type(self)(
            copy.deepcopy(self.payload, memo),
            schema=copy.deepcopy(self.schema, memo),
            metadata=copy.deepcopy(self.metadata, memo),
            collate_policy=copy.deepcopy(self.collate_policy, memo),
        )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"payload={self.payload!r}, "
            f"schema={self.schema!r}, "
            f"metadata={self.metadata!r}, "
            f"collate_policy={self.collate_policy!r})"
        )


def _coerce_metadata(
    metadata: Mapping[MetadataKey | str, object] | None,
) -> dict[MetadataKey, object]:
    if metadata is None:
        return {}
    return {MetadataKey(key): value for key, value in metadata.items()}


def _coerce_collate_policy(value: object | None) -> object | None:
    if value is None:
        return None

    try:
        from rphys.data.collation import CollatePolicy
    except ImportError:
        return value

    if isinstance(value, CollatePolicy):
        return value
    try:
        return CollatePolicy(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return value
