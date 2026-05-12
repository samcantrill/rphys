"""Role-qualified field locators.

``FieldLocator`` addresses a field as ``<role>/<data-key>[#<metadata-key>]``
while preserving the runtime role, intrinsic ``DataKey``, and optional
``MetadataKey`` as separate components. Locators do not perform sample lookup,
mutation, routing, collation, datasource indexing, operation wiring, metadata
loading, normalization, or registry resolution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Self

from rphys.errors import (
    InvalidDataKeyError,
    InvalidFieldLocatorError,
    InvalidMetadataKeyError,
)

from .keys import DataKey
from .metadata import MetadataKey

__all__ = ["FieldLocator", "FieldRole"]

_LOCATOR_EXPECTED = "<role>/<data-key>[#<metadata-key>]"


class FieldRole(StrEnum):
    """Closed runtime role vocabulary for role-qualified field addresses."""

    INPUTS = "inputs"
    TARGETS = "targets"
    SOURCE = "source"
    PREDICTIONS = "predictions"
    OUTPUTS = "outputs"
    LOSSES = "losses"
    OBJECTIVES = "objectives"
    METRICS = "metrics"
    METADATA = "metadata"
    DIAGNOSTICS = "diagnostics"


@dataclass(frozen=True, slots=True)
class FieldLocator:
    """Component-preserving field address.

    Direct construction coerces ``role`` to ``FieldRole``, ``key`` to
    ``DataKey``, and ``metadata_key`` to ``MetadataKey`` when provided. Direct
    component constructors keep their own typed errors; ``parse()`` wraps any
    whole-locator or component failure as ``InvalidFieldLocatorError`` with
    component context.
    """

    role: FieldRole
    key: DataKey
    metadata_key: MetadataKey | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "role", _coerce_role(self.role))
        object.__setattr__(self, "key", DataKey(self.key))
        if self.metadata_key is not None:
            object.__setattr__(self, "metadata_key", MetadataKey(self.metadata_key))

    def __str__(self) -> str:
        locator = f"{self.role.value}/{self.key}"
        if self.metadata_key is not None:
            locator = f"{locator}#{self.metadata_key}"
        return locator

    @classmethod
    def parse(cls, value: str) -> Self:
        """Parse ``<role>/<data-key>[#<metadata-key>]`` without normalization."""

        if not isinstance(value, str):
            raise InvalidFieldLocatorError(
                "Field locators must be strings.",
                locator=value,
                expected=_LOCATOR_EXPECTED,
                actual=type(value).__name__,
            )

        if value.count("/") != 1:
            raise InvalidFieldLocatorError(
                "Field locators require exactly one role separator.",
                locator=value,
                expected=_LOCATOR_EXPECTED,
                actual=value,
            )

        role_value, remainder = value.split("/", 1)
        if not role_value or not remainder:
            raise InvalidFieldLocatorError(
                "Field locator role and key must both be present.",
                locator=value,
                expected=_LOCATOR_EXPECTED,
                actual=value,
            )

        if remainder.count("#") > 1:
            raise InvalidFieldLocatorError(
                "Field locators allow at most one metadata selector.",
                locator=value,
                expected=_LOCATOR_EXPECTED,
                actual=value,
            )

        key_value, metadata_value = _split_metadata_selector(remainder)
        if not key_value:
            raise InvalidFieldLocatorError(
                "Field locator data key must be present.",
                locator=value,
                component="key",
                expected=_LOCATOR_EXPECTED,
                actual=value,
            )
        if metadata_value == "":
            raise InvalidFieldLocatorError(
                "Field locator metadata selector must not be empty.",
                locator=value,
                component="metadata_key",
                expected=_LOCATOR_EXPECTED,
                actual=value,
            )

        try:
            role = _coerce_role(role_value)
        except InvalidFieldLocatorError as exc:
            raise InvalidFieldLocatorError(
                "Invalid field locator role.",
                locator=value,
                component="role",
                role=role_value,
                expected=exc.context.get("expected", _LOCATOR_EXPECTED),
                actual=role_value,
            ) from exc

        try:
            key = DataKey(key_value)
        except InvalidDataKeyError as exc:
            raise InvalidFieldLocatorError(
                "Invalid field locator data key.",
                locator=value,
                component="key",
                key=key_value,
                expected=exc.context.get("expected", _LOCATOR_EXPECTED),
                actual=key_value,
            ) from exc

        metadata_key = None
        if metadata_value is not None:
            try:
                metadata_key = MetadataKey(metadata_value)
            except InvalidMetadataKeyError as exc:
                raise InvalidFieldLocatorError(
                    "Invalid field locator metadata selector.",
                    locator=value,
                    component="metadata_key",
                    metadata_key=metadata_value,
                    expected=exc.context.get("expected", _LOCATOR_EXPECTED),
                    actual=metadata_value,
                ) from exc

        return cls(role=role, key=key, metadata_key=metadata_key)


def _coerce_role(value: FieldRole | str) -> FieldRole:
    if isinstance(value, FieldRole):
        return value
    if not isinstance(value, str):
        raise InvalidFieldLocatorError(
            "Field roles must be strings or FieldRole values.",
            role=value,
            expected=sorted(role.value for role in FieldRole),
            actual=type(value).__name__,
        )
    try:
        return FieldRole(value)
    except ValueError as exc:
        raise InvalidFieldLocatorError(
            "Invalid field role.",
            role=value,
            expected=sorted(role.value for role in FieldRole),
            actual=value,
        ) from exc


def _split_metadata_selector(value: str) -> tuple[str, str | None]:
    if "#" not in value:
        return value, None
    key_value, metadata_value = value.split("#", 1)
    return key_value, metadata_value
