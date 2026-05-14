"""Mutable runtime field containers for loaded samples and batches.

``Sample`` and ``Batch`` expose the same Stage 2 access and mutation API while
remaining distinct public classes. They store loaded ``FieldValue`` objects
behind private entries keyed by ``FieldLocator`` and do not perform IO, lazy
loading, serialization, padding, stacking, or scientific schema validation.
"""

from __future__ import annotations

import copy
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from typing import Any, Protocol, TypeAlias, runtime_checkable

from rphys.errors import FieldSchemaError, FieldTypeError, MissingFieldError

from .fields import FieldValue
from .locators import FieldLocator, FieldRole
from .metadata import MetadataKey
from .schemas import SchemaName

__all__ = ["Batch", "FieldContainer", "Sample"]

FieldValueInput: TypeAlias = FieldValue | object
PayloadType: TypeAlias = type | tuple[type, ...]
_MISSING = object()


@runtime_checkable
class FieldContainer(Protocol):
    """Protocol for field containers used by loaded runtime sample-like objects."""

    def has(self, locator: FieldLocator | str) -> bool:
        ...

    def field(
        self,
        locator: FieldLocator | str,
        *,
        expected_type: PayloadType | None = None,
        schema: SchemaName | str | None = None,
    ) -> FieldValue:
        ...

    def get(
        self,
        locator: FieldLocator | str,
        default: object = None,
        *,
        expected_type: PayloadType | None = None,
        schema: SchemaName | str | None = None,
    ) -> object:
        ...

    def require(
        self,
        locator: FieldLocator | str,
        *,
        expected_type: PayloadType | None = None,
        schema: SchemaName | str | None = None,
    ) -> object:
        ...

    def role(self, role: FieldRole | str) -> Mapping[FieldLocator, FieldValue]:
        ...

    def field_items(self) -> tuple[tuple[FieldLocator, FieldValue], ...]:
        ...


@dataclass(slots=True)
class _FieldEntry:
    value: FieldValue


class _RoleView(Mapping[FieldLocator, FieldValue]):
    def __init__(self, entries: Mapping[FieldLocator, _FieldEntry]) -> None:
        self._values = {locator: entry.value for locator, entry in entries.items()}

    def __getitem__(self, locator: FieldLocator) -> FieldValue:
        return self._values[locator]

    def __iter__(self) -> Iterator[FieldLocator]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)


class _FieldContainerBase:
    """Private shared implementation for ``Sample`` and ``Batch``."""

    __slots__ = ("_fields",)

    _fields: dict[FieldLocator, _FieldEntry]

    def __init__(
        self,
        fields: Mapping[FieldLocator | str, FieldValueInput] | None = None,
    ) -> None:
        self._fields = {}
        if fields is not None:
            for locator, value in fields.items():
                self.set_field(locator, value)

    def has(self, locator: FieldLocator | str) -> bool:
        """Return whether ``locator`` is present."""

        return _coerce_locator(locator) in self._fields

    def field(
        self,
        locator: FieldLocator | str,
        *,
        expected_type: PayloadType | None = None,
        schema: SchemaName | str | None = None,
    ) -> FieldValue:
        """Return the stored ``FieldValue`` for ``locator`` or fail loudly."""

        resolved = _coerce_locator(locator)
        value = self._require_entry(resolved).value
        _validate_field_value(
            resolved,
            value,
            expected_type=expected_type,
            schema=schema,
        )
        return value

    def get(
        self,
        locator: FieldLocator | str,
        default: object = None,
        *,
        expected_type: PayloadType | None = None,
        schema: SchemaName | str | None = None,
    ) -> object:
        """Return the payload for ``locator`` or ``default`` when absent."""

        resolved = _coerce_locator(locator)
        entry = self._fields.get(resolved)
        if entry is None:
            return default
        _validate_field_value(
            resolved,
            entry.value,
            expected_type=expected_type,
            schema=schema,
        )
        return entry.value.payload

    def require(
        self,
        locator: FieldLocator | str,
        *,
        expected_type: PayloadType | None = None,
        schema: SchemaName | str | None = None,
    ) -> object:
        """Return the payload for ``locator`` and raise if missing or invalid."""

        return self.field(
            locator,
            expected_type=expected_type,
            schema=schema,
        ).payload

    def set_field(
        self,
        locator: FieldLocator | str,
        value: FieldValueInput,
        *,
        schema: SchemaName | str | None = None,
        metadata: Mapping[MetadataKey | str, object] | None = None,
        collate_policy: object | None = None,
    ) -> "_FieldContainerBase":
        """Set ``locator`` to a ``FieldValue`` or wrap a raw payload."""

        resolved = _coerce_locator(locator)
        if isinstance(value, FieldValue):
            if schema is not None or metadata is not None or collate_policy is not None:
                raise FieldTypeError(
                    "FieldValue inputs cannot be combined with wrapper metadata.",
                    locator=str(resolved),
                )
            field_value = value
        else:
            field_value = FieldValue(
                value,
                schema=schema,
                metadata=metadata,
                collate_policy=collate_policy,
            )
        self._fields[resolved] = _FieldEntry(field_value)
        return self

    def delete_field(self, locator: FieldLocator | str) -> FieldValue:
        """Remove ``locator`` and return the removed ``FieldValue``."""

        resolved = _coerce_locator(locator)
        try:
            return self._fields.pop(resolved).value
        except KeyError as exc:
            raise MissingFieldError(
                "Required field is missing.",
                locator=str(resolved),
            ) from exc

    def rename_field(
        self,
        source: FieldLocator | str,
        target: FieldLocator | str,
    ) -> "_FieldContainerBase":
        """Move a stored ``FieldValue`` from ``source`` to ``target``."""

        source_locator = _coerce_locator(source)
        target_locator = _coerce_locator(target)
        if target_locator in self._fields:
            raise FieldTypeError(
                "Target field already exists.",
                source=str(source_locator),
                target=str(target_locator),
            )
        try:
            self._fields[target_locator] = self._fields.pop(source_locator)
        except KeyError as exc:
            raise MissingFieldError(
                "Required field is missing.",
                locator=str(source_locator),
            ) from exc
        return self

    def role(self, role: FieldRole | str) -> Mapping[FieldLocator, FieldValue]:
        """Return a read-only shallow mapping of fields with ``role``."""

        resolved_role = _coerce_role(role)
        return _RoleView(
            {
                locator: entry
                for locator, entry in self._fields.items()
                if locator.role is resolved_role
            }
        )

    def shallow_copy(self) -> "_FieldContainerBase":
        """Return a new container with the same ``FieldValue`` objects."""

        copied = type(self)()
        copied._fields = {
            locator: _FieldEntry(entry.value)
            for locator, entry in self._fields.items()
        }
        return copied

    def deep_copy(self) -> "_FieldContainerBase":
        """Return a new container with deep-copied field values."""

        copied = type(self)()
        copied._fields = {
            locator: _FieldEntry(copy.deepcopy(entry.value))
            for locator, entry in self._fields.items()
        }
        return copied

    def map_tensors_(self, mapper: Callable[[object], object]) -> "_FieldContainerBase":
        """Map tensor leaves inside payloads that expose ``map_tensors``."""

        for locator, entry in tuple(self._fields.items()):
            payload = entry.value.payload
            map_tensors = getattr(payload, "map_tensors", None)
            if map_tensors is None or not callable(map_tensors):
                continue
            mapped_payload = map_tensors(mapper)
            if mapped_payload is not payload:
                self._fields[locator] = _FieldEntry(
                    FieldValue(
                        mapped_payload,
                        schema=entry.value.schema,
                        metadata=entry.value.metadata,
                        collate_policy=entry.value.collate_policy,
                    )
                )
        return self

    def _require_entry(self, locator: FieldLocator) -> _FieldEntry:
        try:
            return self._fields[locator]
        except KeyError as exc:
            raise MissingFieldError(
                "Required field is missing.",
                locator=str(locator),
            ) from exc

    def field_items(self) -> tuple[tuple[FieldLocator, FieldValue], ...]:
        return tuple((locator, entry.value) for locator, entry in self._fields.items())

    def _field_items(self) -> tuple[tuple[FieldLocator, FieldValue], ...]:
        # Compatibility shim for internal callers that may still rely on the
        # legacy private method name.
        return self.field_items()


class Sample(_FieldContainerBase):
    """Mutable collection of loaded fields for one runtime sample."""


class Batch(_FieldContainerBase):
    """Mutable collection of loaded fields after explicit batch construction."""


def _coerce_locator(locator: FieldLocator | str) -> FieldLocator:
    if isinstance(locator, FieldLocator):
        return locator
    return FieldLocator.parse(locator)


def _coerce_role(role: FieldRole | str) -> FieldRole:
    if isinstance(role, FieldRole):
        return role
    try:
        return FieldRole(role)
    except ValueError as exc:
        raise FieldTypeError(
            "Invalid field role.",
            role=role,
            expected=sorted(field_role.value for field_role in FieldRole),
            actual=role,
        ) from exc


def _validate_field_value(
    locator: FieldLocator,
    value: FieldValue,
    *,
    expected_type: PayloadType | None,
    schema: SchemaName | str | None,
) -> None:
    if expected_type is not None and not isinstance(value.payload, expected_type):
        raise FieldTypeError(
            "Field payload has the wrong type.",
            locator=str(locator),
            expected=_expected_type_name(expected_type),
            actual=type(value.payload).__name__,
        )

    if schema is not None:
        expected_schema = SchemaName(schema)
        if value.schema != expected_schema:
            raise FieldSchemaError(
                "Field schema does not match the required schema.",
                locator=str(locator),
                expected=str(expected_schema),
                actual=str(value.schema) if value.schema is not None else None,
            )


def _expected_type_name(expected_type: PayloadType) -> str:
    if isinstance(expected_type, tuple):
        return " | ".join(item.__name__ for item in expected_type)
    return expected_type.__name__
