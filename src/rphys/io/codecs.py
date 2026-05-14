"""Datasource-neutral codec contracts for lazy field materialization.

The records in this module describe how codecs receive ``FieldView`` and
``FieldRef`` descriptors and return probe/load/save evidence. They do not
discover codecs, scan datasources, load payloads by themselves, define export
layouts, or attach datasource record provenance to IO contexts.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Protocol, runtime_checkable

from rphys.data.fields import FieldSpec, FieldValue
from rphys.errors import (
    CodecDependencyError,
    CodecOperationError,
    CodecResolutionError,
    InvalidCodecError,
    RemotePhysCodecError,
    RemotePhysDependencyError,
    RemotePhysSliceError,
    UnsupportedCodecIndexError,
    UnsupportedCodecOperationError,
)

from ._primitives import FrozenPrimitive, copy_string_mapping
from .fields import FieldRef, FieldView
from .resources import ResourceRef

__all__ = [
    "CodecCapabilities",
    "CodecLoadResult",
    "CodecProbeResult",
    "CodecRegistry",
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


class CodecRegistry:
    """Explicit ordered registry for structural field codecs.

    Registry instances are intentionally local objects. They do not discover
    codecs, consult process-global state, assign symbolic names, or import
    optional dependencies during core import.

    Registered codecs may optionally define ``supports_probe(context)``,
    ``supports_load(context)``, and ``supports_save(value, context)``
    predicates. Predicates must return ``bool`` and are used only to select a
    unique operation-specific codec; unsupported indexed views should fail
    loudly instead of falling back to full-resource loads.
    """

    __slots__ = ("_codecs",)

    def __init__(self, codecs: Sequence[object] | None = None) -> None:
        self._codecs: list[object] = []
        if codecs is not None:
            if isinstance(codecs, (str, bytes)) or not isinstance(codecs, Sequence):
                raise InvalidCodecError(
                    "CodecRegistry codecs must be a sequence of codec objects.",
                    field="codecs",
                    actual=type(codecs).__name__,
                )
            for codec in codecs:
                self.register(codec)

    @property
    def codecs(self) -> tuple[object, ...]:
        """Registered codec objects in deterministic resolution order."""

        return tuple(self._codecs)

    def register(self, codec: object) -> object:
        """Register one structural codec and return it unchanged."""

        _codec_capabilities(codec, operation="register", index=len(self._codecs))
        self._codecs.append(codec)
        return codec

    def resolve_probe(self, context: LoadContext) -> object:
        """Return the unique codec that can probe ``context``."""

        _require_load_context(context, operation="probe")
        return self._resolve("probe", context)

    def resolve_load(self, context: LoadContext) -> object:
        """Return the unique codec that can load ``context``."""

        _require_load_context(context, operation="load")
        return self._resolve("load", context)

    def resolve_save(self, value: FieldValue, context: SaveContext) -> object:
        """Return the unique codec that can save ``value`` to ``context``."""

        _require_field_value(value, operation="save")
        _require_save_context(context, operation="save")
        return self._resolve("save", context, value=value)

    def probe(self, context: LoadContext) -> CodecProbeResult:
        """Probe a field view through the unique matching codec."""

        codec = self.resolve_probe(context)
        result = _invoke_codec(codec, "probe", CodecProbeResult, context)
        return result

    def load(self, context: LoadContext) -> CodecLoadResult:
        """Load a field view through the unique matching codec."""

        codec = self.resolve_load(context)
        result = _invoke_codec(codec, "load", CodecLoadResult, context)
        return result

    def save(self, value: FieldValue, context: SaveContext) -> CodecSaveResult:
        """Save one field value through the unique matching codec."""

        codec = self.resolve_save(value, context)
        result = _invoke_codec(codec, "save", CodecSaveResult, value, context)
        return result

    def _resolve(
        self,
        operation: str,
        context: LoadContext | SaveContext,
        *,
        value: FieldValue | None = None,
    ) -> object:
        if not self._codecs:
            raise CodecResolutionError(
                "No codecs are registered.",
                operation=operation,
            )

        matches: list[tuple[int, object]] = []
        unsupported_operation_count = 0
        unsupported_index_errors: list[UnsupportedCodecIndexError] = []
        for index, codec in enumerate(self._codecs):
            capabilities = _codec_capabilities(codec, operation=operation, index=index)
            if not _operation_enabled(capabilities, operation):
                unsupported_operation_count += 1
                continue
            if (
                operation == "save"
                and isinstance(context, SaveContext)
                and context.metadata_policy not in capabilities.metadata_policies
            ):
                continue
            _codec_operation_method(codec, operation, index=index)
            try:
                supported = _codec_supports(
                    codec,
                    operation,
                    context,
                    value=value,
                    index=index,
                )
            except UnsupportedCodecIndexError as exc:
                unsupported_index_errors.append(exc)
                continue
            if supported:
                matches.append((index, codec))

        if len(matches) == 1:
            return matches[0][1]
        if len(matches) > 1:
            raise CodecResolutionError(
                "Codec resolution is ambiguous.",
                operation=operation,
                field_key=_context_field_key(context),
                matches=[_codec_label(codec, index=index) for index, codec in matches],
            )
        if unsupported_index_errors:
            raise unsupported_index_errors[0]
        if unsupported_operation_count == len(self._codecs):
            raise UnsupportedCodecOperationError(
                "No registered codec declares support for the requested operation.",
                operation=operation,
                registered=len(self._codecs),
            )
        raise CodecResolutionError(
            "No registered codec matched the operation context.",
            operation=operation,
            field_key=_context_field_key(context),
            registered=len(self._codecs),
        )


CodecRegistry.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class IOContext:
    """Operation context metadata shared by load/probe and save contexts."""

    metadata: Mapping[str, FrozenPrimitive]

    def __init__(self, metadata: Mapping[str, object] | None = None) -> None:
        object.__setattr__(self, "metadata", _freeze_metadata(metadata))


IOContext.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class LoadContext(IOContext):
    """Datasource-neutral context for probing or loading one ``FieldView``.

    This context deliberately omits datasource records, index items,
    role-qualified locators, split labels, member/alignment semantics, cache
    keys, and export policy. Builder-side provenance remains outside codec
    dispatch.
    """

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
    """Datasource-neutral context for saving one logical field target.

    ``target`` is the logical ``FieldRef`` being written. Save policy is
    explicit and narrow; load/probe operations do not imply metadata
    persistence or export layout behavior.
    """

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


def _require_load_context(context: object, *, operation: str) -> None:
    if not isinstance(context, LoadContext):
        raise CodecOperationError(
            "Codec operation requires a LoadContext.",
            operation=operation,
            field="context",
            actual=type(context).__name__,
        )


def _require_save_context(context: object, *, operation: str) -> None:
    if not isinstance(context, SaveContext):
        raise CodecOperationError(
            "Codec operation requires a SaveContext.",
            operation=operation,
            field="context",
            actual=type(context).__name__,
        )


def _require_field_value(value: object, *, operation: str) -> None:
    if not isinstance(value, FieldValue):
        raise CodecOperationError(
            "Codec save operation requires a FieldValue.",
            operation=operation,
            field="value",
            actual=type(value).__name__,
        )


def _codec_capabilities(
    codec: object,
    *,
    operation: str,
    index: int,
) -> CodecCapabilities:
    capabilities = getattr(codec, "capabilities", None)
    if not isinstance(capabilities, CodecCapabilities):
        raise InvalidCodecError(
            "Registered codecs must expose CodecCapabilities.",
            operation=operation,
            codec=_codec_label(codec, index=index),
            field="capabilities",
            actual=type(capabilities).__name__,
        )
    return capabilities


def _operation_enabled(capabilities: CodecCapabilities, operation: str) -> bool:
    if operation == "probe":
        return capabilities.can_probe
    if operation == "load":
        return capabilities.can_load
    if operation == "save":
        return capabilities.can_save
    raise CodecOperationError(
        "Unsupported codec registry operation.",
        operation=operation,
    )


def _codec_operation_method(
    codec: object,
    operation: str,
    *,
    index: int,
) -> Callable[..., object]:
    method = getattr(codec, operation, None)
    if not callable(method):
        raise InvalidCodecError(
            "Registered codec operation attribute must be callable.",
            operation=operation,
            codec=_codec_label(codec, index=index),
            field=operation,
            actual=type(method).__name__,
        )
    return method


def _codec_supports(
    codec: object,
    operation: str,
    context: LoadContext | SaveContext,
    *,
    value: FieldValue | None,
    index: int,
) -> bool:
    support_name = f"supports_{operation}"
    support = getattr(codec, support_name, None)
    if support is None:
        return True
    if not callable(support):
        raise InvalidCodecError(
            "Codec support predicate attribute must be callable.",
            operation=operation,
            codec=_codec_label(codec, index=index),
            field=support_name,
            actual=type(support).__name__,
        )

    try:
        if operation == "save":
            supported = support(value, context)
        else:
            supported = support(context)
    except CodecDependencyError:
        raise
    except RemotePhysDependencyError as exc:
        raise CodecDependencyError(
            "Codec support check dependency is unavailable.",
            operation=operation,
            codec=_codec_label(codec, index=index),
            field_key=_context_field_key(context),
            dependency_error=str(exc),
        ) from exc
    except (RemotePhysSliceError, RemotePhysCodecError):
        raise
    except Exception as exc:
        raise CodecOperationError(
            "Codec support check failed.",
            operation=operation,
            codec=_codec_label(codec, index=index),
            field_key=_context_field_key(context),
            error_type=type(exc).__name__,
        ) from exc

    if not isinstance(supported, bool):
        raise InvalidCodecError(
            "Codec support predicate must return bool.",
            operation=operation,
            codec=_codec_label(codec, index=index),
            field=support_name,
            actual=type(supported).__name__,
        )
    return supported


def _invoke_codec(
    codec: object,
    operation: str,
    expected_type: type[CodecProbeResult] | type[CodecLoadResult] | type[CodecSaveResult],
    *args: object,
) -> CodecProbeResult | CodecLoadResult | CodecSaveResult:
    method = _codec_operation_method(codec, operation, index=-1)
    try:
        result = method(*args)
    except CodecDependencyError:
        raise
    except RemotePhysDependencyError as exc:
        raise CodecDependencyError(
            "Codec operation dependency is unavailable.",
            operation=operation,
            codec=_codec_label(codec, index=-1),
            dependency_error=str(exc),
        ) from exc
    except (RemotePhysSliceError, RemotePhysCodecError):
        raise
    except Exception as exc:
        raise CodecOperationError(
            "Codec operation failed.",
            operation=operation,
            codec=_codec_label(codec, index=-1),
            error_type=type(exc).__name__,
        ) from exc

    if not isinstance(result, expected_type):
        raise CodecOperationError(
            "Codec operation returned an invalid result type.",
            operation=operation,
            codec=_codec_label(codec, index=-1),
            expected=expected_type.__name__,
            actual=type(result).__name__,
        )
    return result


def _context_field_key(context: LoadContext | SaveContext) -> str:
    if isinstance(context, LoadContext):
        return str(context.field_view.field_ref.key)
    return str(context.target.key)


def _codec_label(codec: object, *, index: int) -> str:
    name = getattr(codec, "name", None)
    label = name if isinstance(name, str) and name else type(codec).__qualname__
    if index >= 0:
        return f"{index}:{label}"
    return label


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
