"""Adapters between runtime ``Batch`` fields and method/model values."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TypeAlias

from rphys.data import Batch
from rphys.data.locators import FieldLocator, FieldRole
from rphys.data.schemas import SchemaName
from rphys.errors import RemotePhysMethodError

__all__ = [
    "MethodInputAdapter",
    "MethodInputSpec",
]

ExpectedType: TypeAlias = type | tuple[type, ...]
_INPUT_ROLES = (FieldRole.INPUTS, FieldRole.SOURCE, FieldRole.METADATA)


@dataclass(frozen=True, slots=True)
class MethodInputSpec:
    """Declared input field consumed by a method/model adapter.

    ``locator`` is parsed at construction so hot-loop extraction does not
    perform selector parsing. Optional ``expected_type`` and ``schema`` checks
    are runtime container checks, not a tensor schema language.
    """

    name: str
    locator: FieldLocator | str
    expected_type: ExpectedType | None = None
    schema: SchemaName | str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _validate_name(self.name, field="name"))
        locator = _coerce_locator(self.locator)
        if locator.role not in _INPUT_ROLES:
            raise RemotePhysMethodError(
                "Method input locators must not consume targets, predictions, outputs, or score fields.",
                name=self.name,
                locator=str(locator),
                role=locator.role.value,
                expected=[role.value for role in _INPUT_ROLES],
            )
        object.__setattr__(self, "locator", locator)
        object.__setattr__(
            self,
            "expected_type",
            _validate_expected_type(self.expected_type, field=self.name),
        )
        if self.schema is not None:
            object.__setattr__(self, "schema", SchemaName(self.schema))

@dataclass(frozen=True, slots=True)
class MethodInputAdapter:
    """Extract named payloads from a ``Batch`` using declared input specs."""

    specs: Sequence[MethodInputSpec]

    def __post_init__(self) -> None:
        specs = _coerce_specs(self.specs, expected_type=MethodInputSpec, field="specs")
        _validate_unique_specs(specs)
        object.__setattr__(self, "specs", specs)

    def extract(self, batch: Batch) -> dict[str, object]:
        if not isinstance(batch, Batch):
            raise RemotePhysMethodError(
                "MethodInputAdapter.extract requires a Batch.",
                actual=type(batch).__name__,
            )
        return {
            spec.name: batch.require(
                spec.locator,
                expected_type=spec.expected_type,
                schema=spec.schema,
            )
            for spec in self.specs
        }


def _coerce_specs(
    specs: Sequence[object],
    *,
    expected_type: type,
    field: str,
) -> tuple[object, ...]:
    if isinstance(specs, (str, bytes)) or not isinstance(specs, Sequence):
        raise RemotePhysMethodError(
            "Adapter specs must be a sequence.",
            field=field,
            actual=type(specs).__name__,
        )
    coerced = tuple(specs)
    for spec in coerced:
        if not isinstance(spec, expected_type):
            raise RemotePhysMethodError(
                "Adapter specs contain an invalid item.",
                field=field,
                expected=expected_type.__name__,
                actual=type(spec).__name__,
            )
    return coerced


def _validate_unique_specs(specs: tuple[object, ...]) -> None:
    names: set[str] = set()
    locators: set[FieldLocator] = set()
    for spec in specs:
        name = getattr(spec, "name")
        locator = getattr(spec, "locator")
        if name in names:
            raise RemotePhysMethodError(
                "Adapter specs must not contain duplicate names.",
                name=name,
            )
        if locator in locators:
            raise RemotePhysMethodError(
                "Adapter specs must not contain duplicate locators.",
                locator=str(locator),
            )
        names.add(name)
        locators.add(locator)


def _validate_name(value: str, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise RemotePhysMethodError(
            "Adapter names must be non-empty strings.",
            field=field,
            actual=type(value).__name__,
        )
    return value


def _coerce_locator(value: FieldLocator | str) -> FieldLocator:
    if isinstance(value, FieldLocator):
        return value
    if isinstance(value, str):
        return FieldLocator.parse(value)
    raise RemotePhysMethodError(
        "Adapter locators must be FieldLocator objects or strings.",
        actual=type(value).__name__,
    )


def _validate_expected_type(
    value: ExpectedType | None,
    *,
    field: str,
) -> ExpectedType | None:
    if value is None:
        return None
    if isinstance(value, type):
        return value
    if isinstance(value, tuple) and value and all(isinstance(item, type) for item in value):
        return value
    raise RemotePhysMethodError(
        "Adapter expected_type must be a type or non-empty tuple of types.",
        field=field,
        actual=type(value).__name__,
    )


def _expected_type_name(expected_type: ExpectedType) -> str:
    if isinstance(expected_type, tuple):
        return " | ".join(item.__name__ for item in expected_type)
    return expected_type.__name__
