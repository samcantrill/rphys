"""Backend-neutral state and parameter capability records."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType

from rphys.errors import RemotePhysMethodError

from ._records import freeze_primitive_mapping

__all__ = [
    "ParameterView",
    "StateEntry",
    "StateLoadResult",
    "StateView",
]


@dataclass(frozen=True, slots=True)
class StateEntry:
    """Named backend-neutral state value.

    ``value`` may be any backend-native object. ``rphys`` stores the reference
    for inspection and handoff only; it does not require tensor semantics,
    array semantics, or a framework-specific state API. Metadata and
    provenance are copied into primitive read-only mappings so load
    compatibility and origin evidence stay inspectable without encoding
    checkpoint, device, optimizer, or distributed policy.
    """

    name: str
    value: object
    metadata: Mapping[str, object] | None = field(default_factory=dict)
    provenance: Mapping[str, object] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _validate_name(self.name, field="name"))
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(self.metadata, field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(self.provenance, field="provenance"),
        )


@dataclass(frozen=True, slots=True)
class StateView:
    """Immutable view of named method state entries."""

    entries: Sequence[StateEntry] = ()
    metadata: Mapping[str, object] | None = field(default_factory=dict)
    provenance: Mapping[str, object] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        entries = _coerce_entries(self.entries)
        object.__setattr__(self, "entries", entries)
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(self.metadata, field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(self.provenance, field="provenance"),
        )

    def entry(self, name: str) -> StateEntry:
        """Return the named entry or fail loudly."""

        validated = _validate_name(name, field="name")
        for entry in self.entries:
            if entry.name == validated:
                return entry
        raise RemotePhysMethodError(
            "State entry is missing.",
            name=validated,
        )

    @property
    def by_name(self) -> Mapping[str, StateEntry]:
        """Read-only mapping of entries by name."""

        return MappingProxyType({entry.name: entry for entry in self.entries})


@dataclass(frozen=True, slots=True)
class StateLoadResult:
    """Diagnostics returned by strict or permissive state loading."""

    loaded: Sequence[str] = ()
    missing: Sequence[str] = ()
    unexpected: Sequence[str] = ()
    incompatible: Sequence[str] = ()
    diagnostics: Mapping[str, object] | None = field(default_factory=dict)
    metadata: Mapping[str, object] | None = field(default_factory=dict)
    provenance: Mapping[str, object] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "loaded", _coerce_name_tuple(self.loaded, field="loaded"))
        object.__setattr__(self, "missing", _coerce_name_tuple(self.missing, field="missing"))
        object.__setattr__(
            self,
            "unexpected",
            _coerce_name_tuple(self.unexpected, field="unexpected"),
        )
        object.__setattr__(
            self,
            "incompatible",
            _coerce_name_tuple(self.incompatible, field="incompatible"),
        )
        object.__setattr__(
            self,
            "diagnostics",
            freeze_primitive_mapping(self.diagnostics, field="diagnostics"),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(self.metadata, field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(self.provenance, field="provenance"),
        )

    @property
    def success(self) -> bool:
        """Whether loading completed without missing, unexpected, or incompatible entries."""

        return not (self.missing or self.unexpected or self.incompatible)


@dataclass(frozen=True, slots=True)
class ParameterView:
    """Named backend-neutral parameter handle.

    ``handle`` may be any tensor, array, scalar, object reference, or sentinel
    owned by an arbitrary backend. The flags are descriptive only; optimizer
    grouping, scheduler policy, device movement, checkpoint writing, and
    distributed behavior are intentionally out of scope.
    """

    name: str
    handle: object
    trainable: bool = True
    requires_update: bool = True
    metadata: Mapping[str, object] | None = field(default_factory=dict)
    provenance: Mapping[str, object] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _validate_name(self.name, field="name"))
        if not isinstance(self.trainable, bool):
            raise RemotePhysMethodError(
                "ParameterView trainable flag must be a bool.",
                field="trainable",
                actual=type(self.trainable).__name__,
            )
        if not isinstance(self.requires_update, bool):
            raise RemotePhysMethodError(
                "ParameterView requires_update flag must be a bool.",
                field="requires_update",
                actual=type(self.requires_update).__name__,
            )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(self.metadata, field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(self.provenance, field="provenance"),
        )


def _coerce_entries(entries: Sequence[StateEntry]) -> tuple[StateEntry, ...]:
    if isinstance(entries, (str, bytes)) or not isinstance(entries, Sequence):
        raise RemotePhysMethodError(
            "StateView entries must be a sequence.",
            field="entries",
            actual=type(entries).__name__,
        )
    coerced = tuple(entries)
    names: set[str] = set()
    for entry in coerced:
        if not isinstance(entry, StateEntry):
            raise RemotePhysMethodError(
                "StateView entries must contain StateEntry objects.",
                field="entries",
                actual=type(entry).__name__,
            )
        if entry.name in names:
            raise RemotePhysMethodError(
                "StateView entries must not contain duplicate names.",
                name=entry.name,
            )
        names.add(entry.name)
    return coerced


def _coerce_name_tuple(values: Sequence[str], *, field: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise RemotePhysMethodError(
            "StateLoadResult name fields must be sequences.",
            field=field,
            actual=type(values).__name__,
        )
    return tuple(_validate_name(value, field=field) for value in values)


def _validate_name(value: str, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise RemotePhysMethodError(
            "State and parameter names must be non-empty strings.",
            field=field,
            actual=type(value).__name__,
        )
    return value
