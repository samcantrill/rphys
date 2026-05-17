"""Returned-Batch field validation and projection helpers.

``BatchOutputSpec`` validates ordinary ``Batch`` values returned by methods,
learners, and batch operations. It records field roles, locators, schemas,
payload types, and pass-through policy without introducing method-specific
patch records.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal, TypeAlias

from rphys.errors import FieldSchemaError, FieldTypeError, MissingFieldError, RemotePhysDataError

from .containers import Batch
from .fields import FieldValue
from .locators import FieldLocator, FieldRole
from .schemas import SchemaName

__all__ = [
    "BatchOutputFieldSpec",
    "BatchOutputSpec",
    "project_batch_fields",
]

ExpectedType: TypeAlias = type | tuple[type, ...]
ConflictPolicy: TypeAlias = Literal["error", "replace"]

_DEFAULT_OUTPUT_ROLES = (
    FieldRole.PREDICTIONS,
    FieldRole.OUTPUTS,
    FieldRole.LOSSES,
    FieldRole.OBJECTIVES,
    FieldRole.METRICS,
    FieldRole.DIAGNOSTICS,
)


@dataclass(frozen=True, slots=True)
class BatchOutputFieldSpec:
    """Declared field on a returned ``Batch``.

    ``locator`` preserves the field role and intrinsic meaning. Optional
    ``expected_type`` and ``schema`` checks validate the stored payload without
    interpreting shape, units, sample rate, alignment, or backend semantics.
    """

    name: str
    locator: FieldLocator | str
    expected_type: ExpectedType | None = None
    schema: SchemaName | str | None = None
    required: bool = True
    allowed_roles: Sequence[FieldRole | str] | None = _DEFAULT_OUTPUT_ROLES

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _validate_name(self.name))
        locator = _coerce_locator(self.locator)
        allowed_roles = _coerce_allowed_roles(self.allowed_roles)
        if allowed_roles is not None and locator.role not in allowed_roles:
            raise RemotePhysDataError(
                "Batch output field locator has an unsupported role.",
                owner="BatchOutputFieldSpec",
                name=self.name,
                locator=str(locator),
                role=locator.role.value,
                expected=[role.value for role in allowed_roles],
            )
        object.__setattr__(self, "locator", locator)
        object.__setattr__(
            self,
            "expected_type",
            _validate_expected_type(self.expected_type, field=self.name),
        )
        if self.schema is not None:
            object.__setattr__(self, "schema", SchemaName(self.schema))
        if not isinstance(self.required, bool):
            raise RemotePhysDataError(
                "Batch output field required flag must be a boolean.",
                owner="BatchOutputFieldSpec",
                name=self.name,
                actual=type(self.required).__name__,
            )
        object.__setattr__(self, "allowed_roles", allowed_roles)

    def validate(self, batch: Batch, *, owner: str = "BatchOutputSpec") -> FieldValue | None:
        """Validate this field on ``batch`` and return it when present."""

        if not batch.has(self.locator):
            if self.required:
                raise MissingFieldError(
                    "Returned batch is missing a required output field.",
                    owner=owner,
                    name=self.name,
                    locator=str(self.locator),
                )
            return None
        return batch.field(
            self.locator,
            expected_type=self.expected_type,
            schema=self.schema,
        )


@dataclass(frozen=True, slots=True)
class BatchOutputSpec:
    """Validation and construction policy for returned ``Batch`` values.

    Declared fields are outputs produced by the operation. ``pass_through``
    locators are fields that may be carried with the returned batch for later
    evaluation or export but are not interpreted as model inputs.
    """

    fields: Sequence[BatchOutputFieldSpec]
    pass_through: Sequence[FieldLocator | str] = ()
    allow_extra_fields: bool = True

    def __post_init__(self) -> None:
        fields = _coerce_field_specs(self.fields)
        _validate_unique_fields(fields)
        pass_through = tuple(_coerce_locator(locator) for locator in self.pass_through)
        overlap = sorted(
            str(locator)
            for locator in pass_through
            if locator in {field.locator for field in fields}
        )
        if overlap:
            raise RemotePhysDataError(
                "Batch output pass-through locators must be distinct from output fields.",
                owner="BatchOutputSpec",
                locators=overlap,
            )
        if not isinstance(self.allow_extra_fields, bool):
            raise RemotePhysDataError(
                "BatchOutputSpec allow_extra_fields must be a boolean.",
                owner="BatchOutputSpec",
                actual=type(self.allow_extra_fields).__name__,
            )
        object.__setattr__(self, "fields", fields)
        object.__setattr__(self, "pass_through", pass_through)

    @property
    def locators(self) -> tuple[FieldLocator, ...]:
        """Return declared output locators in validation order."""

        return tuple(field.locator for field in self.fields)

    def validate(self, batch: Batch, *, owner: str = "BatchOutputSpec") -> Batch:
        """Validate and return an ordinary ``Batch`` output."""

        if not isinstance(batch, Batch):
            raise RemotePhysDataError(
                "BatchOutputSpec.validate requires a Batch.",
                owner=owner,
                expected="Batch",
                actual=type(batch).__name__,
            )
        for field in self.fields:
            field.validate(batch, owner=owner)
        if not self.allow_extra_fields:
            allowed = {*self.locators, *self.pass_through}
            extra = sorted(
                str(locator)
                for locator, _field_value in batch.field_items()
                if locator not in allowed
            )
            if extra:
                raise RemotePhysDataError(
                    "Returned batch contains undeclared fields.",
                    owner=owner,
                    locators=extra,
                )
        return batch

    def build(
        self,
        result: Mapping[str, object] | Sequence[object] | object,
        *,
        base: Batch | None = None,
        copy_base: bool = True,
        on_conflict: ConflictPolicy = "error",
    ) -> Batch:
        """Map raw named values into a returned ``Batch``.

        This is a generic helper for backend adapters that already know the
        output spec. It writes directly to a ``Batch`` and then validates the
        result; it does not create an intermediate patch record.
        """

        if on_conflict not in {"error", "replace"}:
            raise RemotePhysDataError(
                "Unsupported batch output conflict policy.",
                owner="BatchOutputSpec",
                policy=on_conflict,
                expected=["error", "replace"],
            )
        target = Batch() if base is None else base.shallow_copy() if copy_base else base
        values = self._result_mapping(result)
        for field in self.fields:
            field_value = _coerce_output_field_value(field, values[field.name])
            if target.has(field.locator) and on_conflict == "error":
                raise RemotePhysDataError(
                    "Batch output field conflicts with an existing field.",
                    owner="BatchOutputSpec",
                    locator=str(field.locator),
                    policy=on_conflict,
                )
            target.set_field(field.locator, field_value)
        return self.validate(target)

    def _result_mapping(
        self,
        result: Mapping[str, object] | Sequence[object] | object,
    ) -> dict[str, object]:
        names = tuple(field.name for field in self.fields)
        if isinstance(result, Mapping):
            keys = tuple(result)
            invalid_keys = [key for key in keys if not isinstance(key, str)]
            if invalid_keys:
                raise RemotePhysDataError(
                    "Batch output result mapping keys must be strings.",
                    owner="BatchOutputSpec",
                    actual=type(invalid_keys[0]).__name__,
                )
            missing = sorted(set(names) - set(keys))
            extra = sorted(set(keys) - set(names))
            if missing or extra:
                raise RemotePhysDataError(
                    "Batch output result mapping does not match declared fields.",
                    owner="BatchOutputSpec",
                    missing=missing,
                    extra=extra,
                )
            return {name: result[name] for name in names}

        if len(self.fields) == 1:
            return {names[0]: result}

        if isinstance(result, Sequence) and not isinstance(result, (str, bytes)):
            if len(result) != len(self.fields):
                raise RemotePhysDataError(
                    "Batch output result sequence length does not match declared fields.",
                    owner="BatchOutputSpec",
                    expected=len(self.fields),
                    actual=len(result),
                )
            return {name: value for name, value in zip(names, result)}

        raise RemotePhysDataError(
            "Batch output result shape is incompatible with declared fields.",
            owner="BatchOutputSpec",
            expected="mapping or sequence",
            actual=type(result).__name__,
        )


def project_batch_fields(
    batch: Batch,
    *,
    include: Sequence[FieldLocator | str] | None = None,
    exclude_roles: Sequence[FieldRole | str] = (FieldRole.TARGETS,),
) -> Batch:
    """Return a shallow projected ``Batch`` for method or inference inputs.

    By default target fields are excluded so inference projection cannot
    accidentally consume reference labels. When ``include`` is provided, only
    those locators are copied and the same excluded-role check still applies.
    """

    if not isinstance(batch, Batch):
        raise RemotePhysDataError(
            "project_batch_fields requires a Batch.",
            owner="project_batch_fields",
            expected="Batch",
            actual=type(batch).__name__,
        )
    excluded = _coerce_allowed_roles(exclude_roles)
    include_set = None if include is None else frozenset(_coerce_locator(locator) for locator in include)
    projected = Batch()
    for locator, field_value in batch.field_items():
        if include_set is not None and locator not in include_set:
            continue
        if excluded is not None and locator.role in excluded:
            raise RemotePhysDataError(
                "Projected method inputs include an excluded field role.",
                owner="project_batch_fields",
                locator=str(locator),
                role=locator.role.value,
            )
        projected.set_field(locator, field_value)
    return projected


def _coerce_output_field_value(
    spec: BatchOutputFieldSpec,
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


def _validate_output_payload(spec: BatchOutputFieldSpec, value: object) -> None:
    if spec.expected_type is not None and not isinstance(value, spec.expected_type):
        raise FieldTypeError(
            "Output payload has the wrong type.",
            locator=str(spec.locator),
            name=spec.name,
            expected=_expected_type_name(spec.expected_type),
            actual=type(value).__name__,
        )


def _coerce_field_specs(
    values: Sequence[BatchOutputFieldSpec],
) -> tuple[BatchOutputFieldSpec, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise RemotePhysDataError(
            "Batch output fields must be a sequence.",
            owner="BatchOutputSpec",
            actual=type(values).__name__,
        )
    fields = tuple(values)
    for field in fields:
        if not isinstance(field, BatchOutputFieldSpec):
            raise RemotePhysDataError(
                "Batch output fields contain an invalid item.",
                owner="BatchOutputSpec",
                expected="BatchOutputFieldSpec",
                actual=type(field).__name__,
            )
    return fields


def _validate_unique_fields(fields: tuple[BatchOutputFieldSpec, ...]) -> None:
    names: set[str] = set()
    locators: set[FieldLocator] = set()
    for field in fields:
        if field.name in names:
            raise RemotePhysDataError(
                "Batch output fields must not contain duplicate names.",
                owner="BatchOutputSpec",
                name=field.name,
            )
        if field.locator in locators:
            raise RemotePhysDataError(
                "Batch output fields must not contain duplicate locators.",
                owner="BatchOutputSpec",
                locator=str(field.locator),
            )
        names.add(field.name)
        locators.add(field.locator)


def _validate_name(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise RemotePhysDataError(
            "Batch output field names must be non-empty strings.",
            owner="BatchOutputFieldSpec",
            actual=type(value).__name__,
        )
    return value


def _coerce_locator(value: FieldLocator | str) -> FieldLocator:
    if isinstance(value, FieldLocator):
        return value
    if isinstance(value, str):
        return FieldLocator.parse(value)
    raise RemotePhysDataError(
        "Batch output locators must be FieldLocator objects or strings.",
        owner="BatchOutputSpec",
        actual=type(value).__name__,
    )


def _coerce_allowed_roles(
    values: Sequence[FieldRole | str] | None,
) -> tuple[FieldRole, ...] | None:
    if values is None:
        return None
    try:
        roles = tuple(FieldRole(value) for value in values)
    except ValueError as exc:
        raise RemotePhysDataError(
            "Allowed field roles contain an invalid role.",
            owner="BatchOutputFieldSpec",
            actual=str(exc),
        ) from exc
    if not roles:
        raise RemotePhysDataError(
            "Allowed field roles must not be empty.",
            owner="BatchOutputFieldSpec",
        )
    return roles


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
    raise RemotePhysDataError(
        "Batch output expected_type must be a type or non-empty tuple of types.",
        owner="BatchOutputFieldSpec",
        field=field,
        actual=type(value).__name__,
    )


def _expected_type_name(expected_type: ExpectedType) -> str:
    if isinstance(expected_type, tuple):
        return " | ".join(item.__name__ for item in expected_type)
    return expected_type.__name__
