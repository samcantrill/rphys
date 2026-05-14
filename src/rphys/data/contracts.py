"""Explicit runtime validation contracts for loaded field containers.

``SampleContract`` checks only Stage 2 runtime preconditions: field presence,
payload type, and schema identity. It does not validate shapes, axes, units,
coordinate frames, sample rates, subject leakage, or scientific schema catalogs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from rphys.errors import FieldTypeError

from .containers import FieldContainer
from .locators import FieldLocator
from .schemas import SchemaName

__all__ = ["FieldRequirement", "SampleContract"]

PayloadType: TypeAlias = type | tuple[type, ...]


@dataclass(frozen=True, slots=True)
class FieldRequirement:
    """Public declaration for one runtime field requirement."""

    locator: FieldLocator
    expected_type: PayloadType | None = None
    schema: SchemaName | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "locator", _coerce_locator(self.locator))
        if self.expected_type is not None:
            _validate_expected_type(self.expected_type)
        if self.schema is not None:
            object.__setattr__(self, "schema", SchemaName(self.schema))


@dataclass(frozen=True, slots=True)
class SampleContract:
    """Explicit runtime validator for ``Sample`` or ``Batch`` containers."""

    required: tuple[FieldRequirement, ...] = ()
    optional: tuple[FieldRequirement, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "required",
            _coerce_requirements(self.required),
        )
        object.__setattr__(
            self,
            "optional",
            _coerce_requirements(self.optional),
        )

    def validate(self, container: object) -> object:
        """Validate ``container`` and return it when all checks pass."""

        _validate_container_shape(container)
        for step in _compile_validator_steps(self):
            step.validate(container)
        return container


@dataclass(frozen=True, slots=True)
class _ValidatorStep:
    requirement: FieldRequirement
    required: bool

    def validate(self, container: object) -> None:
        if self.required:
            container.require(  # type: ignore[attr-defined]
                self.requirement.locator,
                expected_type=self.requirement.expected_type,
                schema=self.requirement.schema,
            )
            return

        if container.has(self.requirement.locator):  # type: ignore[attr-defined]
            container.require(  # type: ignore[attr-defined]
                self.requirement.locator,
                expected_type=self.requirement.expected_type,
                schema=self.requirement.schema,
            )


def _coerce_locator(locator: FieldLocator | str) -> FieldLocator:
    if isinstance(locator, FieldLocator):
        return locator
    return FieldLocator.parse(locator)


def _coerce_requirements(
    requirements: tuple[FieldRequirement | FieldLocator | str, ...],
) -> tuple[FieldRequirement, ...]:
    if isinstance(requirements, (FieldRequirement, FieldLocator, str)):
        requirements = (requirements,)
    return tuple(_coerce_requirement(requirement) for requirement in requirements)


def _coerce_requirement(
    requirement: FieldRequirement | FieldLocator | str,
) -> FieldRequirement:
    if isinstance(requirement, FieldRequirement):
        return requirement
    return FieldRequirement(requirement)


def _validate_expected_type(expected_type: PayloadType) -> None:
    if isinstance(expected_type, tuple):
        valid = bool(expected_type) and all(isinstance(item, type) for item in expected_type)
    else:
        valid = isinstance(expected_type, type)
    if not valid:
        raise FieldTypeError(
            "Field requirement expected_type must be a type or tuple of types.",
            expected="type | tuple[type, ...]",
            actual=type(expected_type).__name__,
        )


def _validate_container_shape(container: object) -> None:
    for method_name in ("has", "field", "get", "require", "role", "field_items"):
        method = getattr(container, method_name, None)
        if method is None or not callable(method):
            raise FieldTypeError(
                "SampleContract requires a Sample-like or Batch-like container.",
                method=method_name,
                actual=type(container).__name__,
            )


def _compile_validator_steps(contract: SampleContract) -> tuple[_ValidatorStep, ...]:
    return tuple(
        [
            *(_ValidatorStep(requirement, True) for requirement in contract.required),
            *(_ValidatorStep(requirement, False) for requirement in contract.optional),
        ]
    )
