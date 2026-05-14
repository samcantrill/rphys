"""Public operation declaration contracts for Stage 6.

The stage keeps contracts dependency-light and payload-agnostic: any runtime
container object can be declared through ``input_type`` and ``output_type`` and
treated as an ordinary payload by :class:`Operation`.

Mutation policy and side-effect declarations are *advisory metadata*. They describe
what an operation may do and what evidence labels it promises to emit, but they do
not impose runtime enforcement in Stage 6.

Planned Stage 7/8/9 fields (for specialized ``Sample``/``Batch`` families, export/save
workflows, and cache/materialization identity) are intentionally deferred.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from rphys.errors import InvalidOperationContractError

from ._validation import coerce_string_sequence, coerce_type_expectation

__all__ = [
    "OperationRole",
    "OperationMutationPolicy",
    "OperationContract",
]


class OperationRole(StrEnum):
    """Operation role vocabulary used by :class:`OperationResult`."""

    GENERIC = "generic"


class OperationMutationPolicy(StrEnum):
    """Declared mutation and side-effect policy for an operation.

    The values are informational declarations and are validated for consistency with
    declared evidence labels. Enforcement of mutation constraints is deferred.
    """

    PURE = "pure"
    MAY_MUTATE = "may_mutate"
    SIDE_EFFECTING = "side_effecting"


@dataclass(frozen=True, init=False, slots=True)
class OperationContract:
    """Immutable declaration of an operation's boundary contract.

    The contract captures:
    - input/output type expectations for boundary checking,
    - required context keys,
    - mutation policy declaration, and
    - declarative side-effect evidence labels.
    """

    role: OperationRole
    input_type: type | tuple[type, ...] | None
    output_type: type | tuple[type, ...] | None
    mutation_policy: OperationMutationPolicy
    side_effects: tuple[str, ...]
    required_context: tuple[str, ...]
    failure_modes: tuple[str, ...]

    def __init__(
        self,
        *,
        role: OperationRole = OperationRole.GENERIC,
        input_type: type | tuple[type, ...] | None = None,
        output_type: type | tuple[type, ...] | None = None,
        mutation_policy: OperationMutationPolicy = OperationMutationPolicy.PURE,
        side_effects: tuple[str, ...] | list[str] | None = None,
        required_context: tuple[str, ...] | list[str] | None = None,
        failure_modes: tuple[str, ...] | list[str] | None = None,
    ) -> None:
        role_value = _coerce_role(
            role,
            owner="OperationContract",
            field="role",
            error_type=InvalidOperationContractError,
        )
        mutation_policy_value = _coerce_mutation_policy(
            mutation_policy,
            owner="OperationContract",
            field="mutation_policy",
            error_type=InvalidOperationContractError,
        )
        side_effect_values = coerce_string_sequence(
            side_effects,
            owner="OperationContract",
            field="side_effects",
            expected="ordered non-empty string labels",
            error_type=InvalidOperationContractError,
            allow_none=True,
        )
        required_context_values = coerce_string_sequence(
            required_context,
            owner="OperationContract",
            field="required_context",
            expected="ordered non-empty string keys",
            error_type=InvalidOperationContractError,
            allow_none=True,
        )
        failure_mode_values = coerce_string_sequence(
            failure_modes,
            owner="OperationContract",
            field="failure_modes",
            expected="ordered non-empty string labels",
            error_type=InvalidOperationContractError,
            allow_none=True,
        )

        if mutation_policy_value in {
            OperationMutationPolicy.PURE,
            OperationMutationPolicy.MAY_MUTATE,
        } and side_effect_values:
            raise InvalidOperationContractError(
                "Pure and may-mutate operations cannot declare side effects.",
                field="side_effects",
                operation_name="OperationContract",
                role=role_value.value,
                expected="empty tuple",
                actual=side_effect_values,
            )

        if mutation_policy_value == OperationMutationPolicy.SIDE_EFFECTING:
            if not side_effect_values:
                raise InvalidOperationContractError(
                    "Side-effecting operations must declare non-empty side effects.",
                    field="side_effects",
                    operation_name="OperationContract",
                    role=role_value.value,
                    expected="non-empty tuple",
                    actual=side_effect_values,
                )

        object.__setattr__(self, "role", role_value)
        object.__setattr__(
            self,
            "input_type",
            coerce_type_expectation(
                input_type,
                owner="OperationContract",
                field="input_type",
                error_type=InvalidOperationContractError,
            ),
        )
        object.__setattr__(
            self,
            "output_type",
            coerce_type_expectation(
                output_type,
                owner="OperationContract",
                field="output_type",
                error_type=InvalidOperationContractError,
            ),
        )
        object.__setattr__(self, "mutation_policy", mutation_policy_value)
        object.__setattr__(self, "side_effects", side_effect_values)
        object.__setattr__(self, "required_context", required_context_values)
        object.__setattr__(self, "failure_modes", failure_mode_values)


def _coerce_role(
    value: object,
    *,
    owner: str,
    field: str,
    error_type: type[InvalidOperationContractError],
) -> OperationRole:
    """Convert a role input to ``OperationRole``."""

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


def _coerce_mutation_policy(
    value: object,
    *,
    owner: str,
    field: str,
    error_type: type[InvalidOperationContractError],
) -> OperationMutationPolicy:
    if isinstance(value, OperationMutationPolicy):
        return value
    try:
        return OperationMutationPolicy(value)
    except (TypeError, ValueError):
        raise error_type(
            f"{owner} {field} must be an OperationMutationPolicy.",
            owner=owner,
            field=field,
            expected=" | ".join(policy.value for policy in OperationMutationPolicy),
            actual=repr(value),
        )


OperationContract.__hash__ = None  # type: ignore[assignment]
