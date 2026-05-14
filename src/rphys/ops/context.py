"""Operation runtime context and result records for Stage 1 operation schemas."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from rphys.errors import (
    InvalidOperationContextError,
    InvalidOperationResultError,
)

from ._validation import coerce_non_empty_string, coerce_string_mapping
from .contracts import OperationRole

__all__ = ["OperationContext", "OperationResult"]


@dataclass(frozen=True, init=False, slots=True)
class OperationContext:
    """Runtime metadata/provenance bundle consumed by operation execution."""

    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                metadata,
                owner="OperationContext",
                field="metadata",
                error_type=InvalidOperationContextError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(
                provenance,
                owner="OperationContext",
                field="provenance",
                error_type=InvalidOperationContextError,
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class OperationResult:
    """Runtime output record returned by operation invocation."""

    output: object
    operation_name: str
    role: OperationRole
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]
    side_effect_evidence: Mapping[str, object]

    def __init__(
        self,
        output: object,
        operation_name: str,
        role: OperationRole = OperationRole.GENERIC,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
        side_effect_evidence: Mapping[object, object] | None = None,
    ) -> None:
        role_value = _coerce_role(
            role,
            owner="OperationResult",
            field="role",
            error_type=InvalidOperationResultError,
        )

        object.__setattr__(
            self,
            "output",
            output,
        )
        object.__setattr__(
            self,
            "operation_name",
            coerce_non_empty_string(
                operation_name,
                owner="OperationResult",
                field="operation_name",
                expected="non-empty string",
                error_type=InvalidOperationResultError,
            ),
        )
        object.__setattr__(self, "role", role_value)
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                metadata,
                owner="OperationResult",
                field="metadata",
                error_type=InvalidOperationResultError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(
                provenance,
                owner="OperationResult",
                field="provenance",
                error_type=InvalidOperationResultError,
            ),
        )
        object.__setattr__(
            self,
            "side_effect_evidence",
            coerce_string_mapping(
                side_effect_evidence,
                owner="OperationResult",
                field="side_effect_evidence",
                error_type=InvalidOperationResultError,
            ),
        )


def _coerce_role(
    value: object,
    *,
    owner: str,
    field: str,
    error_type: type[InvalidOperationResultError],
) -> OperationRole:
    if isinstance(value, OperationRole):
        return value
    try:
        return OperationRole(value)
    except (TypeError, ValueError):
        raise error_type(
            f"{owner} {field} must be an OperationRole.",
            owner=owner,
            field=field,
            expected=" | ".join(role.value for role in OperationRole),
            actual=repr(value),
        )


OperationContext.__hash__ = None  # type: ignore[assignment]
OperationResult.__hash__ = None  # type: ignore[assignment]
