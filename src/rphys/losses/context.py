"""Loss execution context records."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from rphys.data import FieldContainer
from rphys.errors import InvalidLossContextError

from ._validation import coerce_string_mapping
from .specs import LossContract

__all__ = ["LossContext"]


@dataclass(frozen=True, init=False, slots=True)
class LossContext:
    """Runtime field container plus metadata consumed by a loss call."""

    contract: LossContract
    fields: FieldContainer
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        contract: LossContract,
        fields: FieldContainer,
        *,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        if not isinstance(contract, LossContract):
            raise InvalidLossContextError(
                "LossContext contract must be a LossContract.",
                owner="LossContext",
                field="contract",
                expected="LossContract",
                actual=type(contract).__name__,
            )
        _validate_field_container(fields)
        contract.validate(fields)
        object.__setattr__(self, "contract", contract)
        object.__setattr__(self, "fields", fields)
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                metadata,
                owner="LossContext",
                field="metadata",
                error_type=InvalidLossContextError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(
                provenance,
                owner="LossContext",
                field="provenance",
                error_type=InvalidLossContextError,
            ),
        )


def _validate_field_container(fields: object) -> None:
    for method_name in ("has", "field", "get", "require", "role", "field_items"):
        method = getattr(fields, method_name, None)
        if method is None or not callable(method):
            raise InvalidLossContextError(
                "LossContext fields must satisfy the FieldContainer protocol.",
                owner="LossContext",
                field="fields",
                method=method_name,
                actual=type(fields).__name__,
            )


LossContext.__hash__ = None  # type: ignore[assignment]
