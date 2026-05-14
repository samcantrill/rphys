"""Datasource-neutral codec contracts for lazy field materialization.

The records in this module describe how codecs receive ``FieldView`` and
``FieldRef`` descriptors and return probe/load/save evidence. They do not
discover codecs, scan datasources, load payloads by themselves, define export
layouts, or attach datasource record provenance to IO contexts.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Protocol, runtime_checkable

from rphys.data.fields import FieldSpec, FieldValue
from rphys.errors import RemotePhysCodecError

from ._primitives import FrozenPrimitive, copy_string_mapping
from .fields import FieldRef, FieldView
from .resources import ResourceRef

__all__ = [
    "CodecCapabilities",
    "CodecLoadResult",
    "CodecProbeResult",
    "CodecSaveResult",
    "FieldCodec",
    "IOContext",
    "LoadContext",
    "MetadataSavePolicy",
    "SaveContext",
]


class MetadataSavePolicy(StrEnum):
    """Explicit metadata persistence request for single-field codec saves."""

    REFERENCE_ONLY = "reference_only"
    INCLUDE_FIELD_METADATA = "include_field_metadata"


@dataclass(frozen=True, init=False, slots=True)
class CodecCapabilities:
    """Declared operation support for a structural field codec.

    Capabilities are static declaration data. They do not select, rank,
    register, import, probe, load, or save a codec.
    """

    can_probe: bool
    can_load: bool
    can_save: bool
    metadata_policies: tuple[MetadataSavePolicy, ...]

    def __init__(
        self,
        *,
        can_probe: bool = False,
        can_load: bool = False,
        can_save: bool = False,
        metadata_policies: Sequence[MetadataSavePolicy | str] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "can_probe",
            _require_bool(can_probe, field="can_probe"),
        )
        object.__setattr__(self, "can_load", _require_bool(can_load, field="can_load"))
        object.__setattr__(self, "can_save", _require_bool(can_save, field="can_save"))
        object.__setattr__(
            self,
            "metadata_policies",
            _coerce_metadata_policies(metadata_policies),
        )


CodecCapabilities.__hash__ = None  # type: ignore[assignment]


@runtime_checkable
class FieldCodec(Protocol):
    """Structural interface implemented by downstream field codecs."""

    @property
    def capabilities(self) -> CodecCapabilities:
        ...

    def probe(self, context: LoadContext) -> CodecProbeResult:
        ...

    def load(self, context: LoadContext) -> CodecLoadResult:
        ...

    def save(self, value: FieldValue, context: SaveContext) -> CodecSaveResult:
        ...


@dataclass(frozen=True, init=False, slots=True)
class IOContext:
    """Operation context metadata shared by load/probe and save contexts."""

    metadata: Mapping[str, FrozenPrimitive]

    def __init__(self, metadata: Mapping[str, object] | None = None) -> None:
        object.__setattr__(self, "metadata", _freeze_metadata(metadata))


IOContext.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class LoadContext(IOContext):
    """Datasource-neutral context for probing or loading one ``FieldView``."""

    field_view: FieldView

    def __init__(
        self,
        field_view: FieldView,
        *,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        if not isinstance(field_view, FieldView):
            raise RemotePhysCodecError(
                "LoadContext field_view must be a FieldView.",
                field="field_view",
                actual=type(field_view).__name__,
            )
        IOContext.__init__(self, metadata=metadata)
        object.__setattr__(self, "field_view", field_view)


LoadContext.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class SaveContext(IOContext):
    """Datasource-neutral context for saving one logical field target."""

    target: FieldRef
    metadata_policy: MetadataSavePolicy

    def __init__(
        self,
        target: FieldRef,
        *,
        metadata_policy: MetadataSavePolicy | str = MetadataSavePolicy.REFERENCE_ONLY,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        if not isinstance(target, FieldRef):
            raise RemotePhysCodecError(
                "SaveContext target must be a FieldRef.",
                field="target",
                actual=type(target).__name__,
            )
        IOContext.__init__(self, metadata=metadata)
        object.__setattr__(self, "target", target)
        object.__setattr__(
            self,
            "metadata_policy",
            _coerce_metadata_policy(metadata_policy),
        )


SaveContext.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class CodecProbeResult:
    """Lightweight evidence from probing a field without loading payload data."""

    field_spec: FieldSpec | None
    metadata: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        field_spec: FieldSpec | None = None,
        *,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        if field_spec is not None and not isinstance(field_spec, FieldSpec):
            raise RemotePhysCodecError(
                "CodecProbeResult field_spec must be a FieldSpec or None.",
                field="field_spec",
                actual=type(field_spec).__name__,
            )
        object.__setattr__(self, "field_spec", field_spec)
        object.__setattr__(self, "metadata", _freeze_metadata(metadata))


CodecProbeResult.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class CodecLoadResult:
    """Loaded logical field returned by a codec without runtime sample state."""

    field_value: FieldValue
    metadata: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        field_value: FieldValue,
        *,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        if not isinstance(field_value, FieldValue):
            raise RemotePhysCodecError(
                "CodecLoadResult field_value must be a FieldValue.",
                field="field_value",
                actual=type(field_value).__name__,
            )
        object.__setattr__(self, "field_value", field_value)
        object.__setattr__(self, "metadata", _freeze_metadata(metadata))


CodecLoadResult.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class CodecSaveResult:
    """Evidence that one logical field target was saved by a codec."""

    target: FieldRef
    resources: tuple[ResourceRef, ...]
    metadata: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        target: FieldRef,
        *,
        resources: Sequence[ResourceRef] | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        if not isinstance(target, FieldRef):
            raise RemotePhysCodecError(
                "CodecSaveResult target must be a FieldRef.",
                field="target",
                actual=type(target).__name__,
            )
        object.__setattr__(self, "target", target)
        object.__setattr__(
            self,
            "resources",
            _coerce_resources(resources if resources is not None else target.resources),
        )
        object.__setattr__(self, "metadata", _freeze_metadata(metadata))


CodecSaveResult.__hash__ = None  # type: ignore[assignment]


def _require_bool(value: object, *, field: str) -> bool:
    if not isinstance(value, bool):
        raise RemotePhysCodecError(
            "Codec capability flags must be bool values.",
            field=field,
            actual=type(value).__name__,
        )
    return value


def _coerce_metadata_policy(value: MetadataSavePolicy | str) -> MetadataSavePolicy:
    if isinstance(value, MetadataSavePolicy):
        return value
    try:
        return MetadataSavePolicy(value)
    except (TypeError, ValueError) as exc:
        raise RemotePhysCodecError(
            "Unsupported metadata save policy.",
            field="metadata_policy",
            actual=str(value),
            supported=[policy.value for policy in MetadataSavePolicy],
        ) from exc


def _coerce_metadata_policies(
    values: Sequence[MetadataSavePolicy | str] | None,
) -> tuple[MetadataSavePolicy, ...]:
    if values is None:
        return (MetadataSavePolicy.REFERENCE_ONLY,)
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise RemotePhysCodecError(
            "Codec metadata_policies must be a sequence of MetadataSavePolicy values.",
            field="metadata_policies",
            actual=type(values).__name__,
        )
    policies = tuple(_coerce_metadata_policy(value) for value in values)
    if not policies:
        raise RemotePhysCodecError(
            "Codec metadata_policies must not be empty.",
            field="metadata_policies",
        )
    return policies


def _coerce_resources(resources: Sequence[ResourceRef]) -> tuple[ResourceRef, ...]:
    if isinstance(resources, (str, bytes)) or not isinstance(resources, Sequence):
        raise RemotePhysCodecError(
            "CodecSaveResult resources must be a sequence of ResourceRef values.",
            field="resources",
            actual=type(resources).__name__,
        )
    coerced = tuple(resources)
    if not coerced:
        raise RemotePhysCodecError(
            "CodecSaveResult resources must not be empty.",
            field="resources",
        )
    for resource in coerced:
        if not isinstance(resource, ResourceRef):
            raise RemotePhysCodecError(
                "CodecSaveResult resources must contain ResourceRef values.",
                field="resources",
                actual=type(resource).__name__,
            )
    return coerced


def _freeze_metadata(
    metadata: Mapping[str, object] | None,
) -> Mapping[str, FrozenPrimitive]:
    return MappingProxyType(
        copy_string_mapping(
            metadata,
            error_type=RemotePhysCodecError,
            field="metadata",
        )
    )
