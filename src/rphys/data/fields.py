"""Field declarations and loaded runtime field values."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, field
import re
from typing import Any

from rphys.data.collation import CollatePolicy
from rphys.data.keys import DataKey
from rphys.errors import RemotePhysDataError

__all__ = ["FieldSpec", "FieldValue"]

_DATA_TYPE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$")


@dataclass(slots=True)
class FieldSpec:
    """Minimal declaration for a logical runtime field.

    API stability: Stable.

    Parameters:
        key:
            Validated logical field key. String inputs are normalized to
            ``DataKey``.
        data_type:
            Lowercase ASCII dot-separated data category, such as ``video`` or
            ``signal``. This is broad runtime identity, not a concrete Python
            type or backend class.
        schema:
            Optional schema identifier. The base contract stores this token and
            lets later specialized specs, data objects, or contracts interpret
            it.

    Scientific contract:
        The base spec deliberately excludes coordinate frames, temporal axes,
        units, layouts, shapes, sample rates, descriptions, and runtime class
        hints. Not every field needs those concepts, and freezing them here
        would create unused or misleading contracts. Concrete packages should
        add specialized specs or data-object contracts when those details become
        scientifically required.

    Equality, hashing, copying, and serialization:
        Value equality covers ``key``, ``data_type``, and ``schema``. Instances
        are not hashable by public contract. Copying and deep copying are
        value-preserving over these primitive fields; callers should rely on
        equality rather than object identity. No public dict or JSON round trip
        is introduced in this phase.

    Failure behavior:
        Invalid keys, invalid data-type tokens, and blank/non-string schema
        values raise ``RemotePhysDataError``.
    """

    key: DataKey | str
    data_type: str
    schema: str | None = None

    def __post_init__(self) -> None:
        self.key = DataKey(self.key)
        self.data_type = _validate_data_type(self.data_type)
        self.schema = _validate_optional_schema(self.schema)


@dataclass(eq=False, slots=True)
class FieldValue:
    """Loaded runtime payload plus narrow field-level metadata.

    API stability: Stable.

    Parameters:
        value:
            Loaded runtime payload. The base package accepts arbitrary payloads
            and does not import backend libraries.
        schema:
            Optional schema identifier carried with this loaded value.
        metadata:
            Field-level metadata mapping. Keys must be strings. Construction
            shallow-copies the mapping so later caller mutations of the input
            mapping do not alter the wrapper.
        collate_policy:
            Optional explicit field-level collation policy. Phase 1 supports
            only ``CollatePolicy.LIST``.

    Scientific contract:
        ``metadata`` describes this field value, not the whole sample. Shape,
        dtype, units, coordinate-frame, temporal-axis, and sample-rate
        validation are intentionally deferred to specialized data objects,
        specialized specs, sample contracts, or downstream scientific docs.

    Equality, hashing, copying, and serialization:
        Equality is object identity so tensor-like payload equality is never
        invoked accidentally. Instances are not hashable. Shallow copying shares
        the payload and nested metadata values while copying the metadata
        mapping. Deep copying delegates to normal Python deep-copy behavior and
        may fail with the payload's underlying error. No public serialization
        contract exists for arbitrary payloads.

    Failure behavior:
        Invalid schema values, non-mapping metadata, non-string metadata keys,
        or unsupported collation policies raise ``RemotePhysDataError``.
    """

    value: Any
    schema: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    collate_policy: CollatePolicy | None = None

    __hash__ = None

    def __post_init__(self) -> None:
        self.schema = _validate_optional_schema(self.schema)
        self.metadata = _copy_metadata(self.metadata)
        self.collate_policy = _validate_collate_policy(self.collate_policy)

    def __copy__(self) -> "FieldValue":
        return type(self)(
            value=self.value,
            schema=self.schema,
            metadata=self.metadata,
            collate_policy=self.collate_policy,
        )

    def __deepcopy__(self, memo: dict[int, Any]) -> "FieldValue":
        return type(self)(
            value=deepcopy(self.value, memo),
            schema=deepcopy(self.schema, memo),
            metadata=deepcopy(self.metadata, memo),
            collate_policy=self.collate_policy,
        )


def _validate_data_type(value: str) -> str:
    if not isinstance(value, str):
        raise RemotePhysDataError("FieldSpec data_type must be a string.")

    if _DATA_TYPE_PATTERN.fullmatch(value) is None:
        raise RemotePhysDataError(
            "FieldSpec data_type must be lowercase ASCII dot-separated tokens."
        )

    return value


def _validate_optional_schema(value: str | None) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise RemotePhysDataError("Field schema must be a string or None.")

    if value == "" or value.strip() != value:
        raise RemotePhysDataError("Field schema must be a non-empty unpadded string.")

    return value


def _copy_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(metadata, Mapping):
        raise RemotePhysDataError("FieldValue metadata must be a mapping.")

    copied = dict(metadata)
    invalid_keys = [key for key in copied if not isinstance(key, str)]
    if invalid_keys:
        raise RemotePhysDataError("FieldValue metadata keys must be strings.")

    return copied


def _validate_collate_policy(policy: CollatePolicy | None) -> CollatePolicy | None:
    if policy is None:
        return None

    if not isinstance(policy, CollatePolicy):
        raise RemotePhysDataError(
            "FieldValue collate_policy must be a CollatePolicy member or None."
        )

    if policy is not CollatePolicy.LIST:
        raise RemotePhysDataError("Only CollatePolicy.LIST is supported in this phase.")

    return policy
