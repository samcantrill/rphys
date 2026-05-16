"""Adapters between runtime ``Batch`` fields and method/model values."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TypeAlias

from rphys.data import Batch
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator, FieldRole
from rphys.data.schemas import SchemaName
from rphys.errors import FieldSchemaError, FieldTypeError, RemotePhysMethodError

from .output import MethodOutput

__all__ = [
    "MethodInputAdapter",
    "MethodInputSpec",
    "MethodOutputAdapter",
    "MethodOutputSpec",
]

ExpectedType: TypeAlias = type | tuple[type, ...]
_OUTPUT_ROLES = (FieldRole.PREDICTIONS, FieldRole.OUTPUTS)


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
        object.__setattr__(self, "locator", _coerce_locator(self.locator))
        object.__setattr__(
            self,
            "expected_type",
            _validate_expected_type(self.expected_type, field=self.name),
        )
        if self.schema is not None:
            object.__setattr__(self, "schema", SchemaName(self.schema))


@dataclass(frozen=True, slots=True)
class MethodOutputSpec:
    """Declared output field produced by a method/model adapter."""

    name: str
    locator: FieldLocator | str
    expected_type: ExpectedType | None = None
    schema: SchemaName | str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _validate_name(self.name, field="name"))
        locator = _coerce_locator(self.locator)
        if locator.role not in _OUTPUT_ROLES:
            raise RemotePhysMethodError(
                "Method output locators must use prediction or output roles.",
                name=self.name,
                locator=str(locator),
                role=locator.role.value,
                expected=[role.value for role in _OUTPUT_ROLES],
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


@dataclass(frozen=True, slots=True)
class MethodOutputAdapter:
    """Map named model/method result values into a ``MethodOutput`` patch."""

    specs: Sequence[MethodOutputSpec]

    def __post_init__(self) -> None:
        specs = _coerce_specs(self.specs, expected_type=MethodOutputSpec, field="specs")
        _validate_unique_specs(specs)
        object.__setattr__(self, "specs", specs)

    def adapt(
        self,
        result: Mapping[str, object] | Sequence[object] | object,
        *,
        diagnostics: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        provenance: Mapping[str, object] | None = None,
    ) -> MethodOutput:
        values = self._result_mapping(result)
        fields = {
            spec.locator: _coerce_output_field_value(spec, values[spec.name])
            for spec in self.specs
        }
        return MethodOutput(
            fields=fields,
            diagnostics=diagnostics,
            metadata=metadata,
            provenance=provenance,
        )

    def _result_mapping(
        self,
        result: Mapping[str, object] | Sequence[object] | object,
    ) -> dict[str, object]:
        names = tuple(spec.name for spec in self.specs)
        if isinstance(result, Mapping):
            keys = tuple(result)
            invalid_keys = [key for key in keys if not isinstance(key, str)]
            if invalid_keys:
                raise RemotePhysMethodError(
                    "Model result mapping keys must be strings.",
                    actual=type(invalid_keys[0]).__name__,
                )
            missing = sorted(set(names) - set(keys))
            extra = sorted(set(keys) - set(names))
            if missing or extra:
                raise RemotePhysMethodError(
                    "Model result mapping does not match declared outputs.",
                    missing=missing,
                    extra=extra,
                )
            return {name: result[name] for name in names}

        if len(self.specs) == 1:
            return {names[0]: result}

        if isinstance(result, Sequence) and not isinstance(result, (str, bytes)):
            if len(result) != len(self.specs):
                raise RemotePhysMethodError(
                    "Model result sequence length does not match declared outputs.",
                    expected=len(self.specs),
                    actual=len(result),
                )
            return {name: value for name, value in zip(names, result)}

        raise RemotePhysMethodError(
            "Model result shape is incompatible with declared outputs.",
            expected="mapping or sequence",
            actual=type(result).__name__,
        )


def _coerce_output_field_value(
    spec: MethodOutputSpec,
    value: object,
) -> FieldValue:
    if isinstance(value, FieldValue):
        _validate_output_payload(spec, value.payload)
        if spec.schema is not None and value.schema != spec.schema:
            raise FieldSchemaError(
                "Output field schema does not match the declared schema.",
                locator=str(spec.locator),
                name=spec.name,
                expected=str(spec.schema),
                actual=str(value.schema) if value.schema is not None else None,
            )
        return value

    _validate_output_payload(spec, value)
    return FieldValue(value, schema=spec.schema)


def _validate_output_payload(spec: MethodOutputSpec, value: object) -> None:
    if spec.expected_type is not None and not isinstance(value, spec.expected_type):
        raise FieldTypeError(
            "Output payload has the wrong type.",
            locator=str(spec.locator),
            name=spec.name,
            expected=_expected_type_name(spec.expected_type),
            actual=type(value).__name__,
        )


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
