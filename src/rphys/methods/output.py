"""Patch-like outputs returned by batch-level methods."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import RemotePhysMethodError

from ._records import freeze_primitive_mapping

__all__ = ["MethodOutput"]


@dataclass(frozen=True, slots=True)
class MethodOutput:
    """Field patch returned by ``Method.predict``.

    ``fields`` maps output ``FieldLocator`` objects to ``FieldValue`` payload
    wrappers. The record is patch-like: it is not a ``Batch`` and does not
    mutate, merge into, export, score, or train against an input batch by
    default. Diagnostics, metadata, and provenance are generic primitive
    mappings copied into read-only containers.
    """

    fields: Mapping[FieldLocator | str, FieldValue] = field(default_factory=dict)
    diagnostics: Mapping[str, object] | None = field(default_factory=dict)
    metadata: Mapping[str, object] | None = field(default_factory=dict)
    provenance: Mapping[str, object] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "fields", _freeze_fields(self.fields))
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


def _freeze_fields(
    value: Mapping[FieldLocator | str, FieldValue],
) -> Mapping[FieldLocator, FieldValue]:
    if not isinstance(value, Mapping):
        raise RemotePhysMethodError(
            "MethodOutput fields must be a mapping.",
            field="fields",
            actual=type(value).__name__,
        )

    fields: dict[FieldLocator, FieldValue] = {}
    for locator, field_value in value.items():
        resolved = _coerce_locator(locator)
        if resolved in fields:
            raise RemotePhysMethodError(
                "MethodOutput fields must not contain duplicate locators.",
                locator=str(resolved),
            )
        if not isinstance(field_value, FieldValue):
            raise RemotePhysMethodError(
                "MethodOutput fields must contain FieldValue objects.",
                locator=str(resolved),
                actual=type(field_value).__name__,
            )
        fields[resolved] = field_value
    return MappingProxyType(fields)


def _coerce_locator(locator: FieldLocator | str) -> FieldLocator:
    if isinstance(locator, FieldLocator):
        return locator
    if isinstance(locator, str):
        return FieldLocator.parse(locator)
    raise RemotePhysMethodError(
        "MethodOutput field locators must be FieldLocator objects or strings.",
        actual=type(locator).__name__,
    )
