"""Single-operation execution wrappers for Stage 6.

Plain functional kernels stay plain callables. Wrapping a kernel in
:class:`Operation` adds:

- typed payload declarations,
- optional context checks,
- :class:`OperationResult` normalization.

Operation payloads are ordinary Python objects, including runtime containers such as
`Sample` and `Batch` when the contract declares those types.
"""

from __future__ import annotations

from collections.abc import Mapping

from rphys.errors import (
    InvalidOperationContextError,
    InvalidOperationContractError,
    InvalidOperationInputError,
    InvalidOperationResultError,
    OperationExecutionError,
)

from .context import OperationContext, OperationResult
from .contracts import (
    OperationContract,
    OperationMutationPolicy,
    OperationRole,
)
from .kernels import FunctionalKernel

__all__ = ["Operation"]


class Operation:
    """Concrete wrapper around a callable that returns :class:`OperationResult`.

    Plain kernel call sites should still call the underlying function directly when
    declaration, context, and output normalization are not required.

    Wrapped execution always returns ``OperationResult``; call sites must unwrap the
    payload via ``result.output``.
    """

    def __init__(
        self,
        function: FunctionalKernel,
        *,
        name: str | None = None,
        contract: OperationContract | None = None,
    ) -> None:
        if not callable(function):
            raise InvalidOperationContractError(
                "operation function must be callable.",
                owner="Operation",
                field="function",
                expected="callable",
                actual=type(function).__name__,
            )

        resolved_contract = (
            OperationContract() if contract is None else contract
        )
        if not isinstance(resolved_contract, OperationContract):
            raise InvalidOperationContractError(
                "operation contract must be an OperationContract.",
                owner="Operation",
                field="contract",
                expected="OperationContract",
                actual=type(contract).__name__,
            )

        resolved_name = _infer_name(name, function)
        if not isinstance(resolved_name, str) or not resolved_name.strip():
            raise InvalidOperationContractError(
                "operation name must be a non-empty string.",
                owner="Operation",
                field="name",
                expected="non-empty string",
                actual=repr(resolved_name),
            )

        self._function = function
        self._name = resolved_name
        self._contract = resolved_contract

    @property
    def name(self) -> str:
        """Name inferred from the wrapped function/class or explicitly set."""
        return self._name

    @property
    def contract(self) -> OperationContract:
        """Current operation contract."""
        return self._contract

    def run(self, input_value: object, context: OperationContext | None = None) -> OperationResult:
        """Execute the wrapped callable and always return ``OperationResult``."""
        execution_context = _coerce_context(context)
        _validate_required_context(
            self._contract.required_context,
            execution_context.metadata,
            operation_name=self._name,
            role=self._contract.role,
        )
        _validate_input(self._contract.input_type, input_value, operation_name=self._name)

        try:
            result = self._function(input_value, context=execution_context)
        except Exception as exc:
            raise OperationExecutionError(
                "operation callable raised during execution.",
                operation_name=self._name,
                role=self._contract.role.value,
                phase="run",
            ) from exc

        return _coerce_and_validate_result(
            result,
            operation_name=self._name,
            contract=self._contract,
            context=execution_context,
        )

    def __call__(self, input_value: object, context: OperationContext | None = None) -> OperationResult:
        """Execute the wrapped callable and return :class:`OperationResult`."""
        return self.run(input_value, context=context)


def _infer_name(
    explicit_name: str | None,
    function: FunctionalKernel,
) -> str:
    if explicit_name is not None:
        return explicit_name

    explicit_name = getattr(function, "__name__", None)
    if isinstance(explicit_name, str) and explicit_name.strip():
        return explicit_name

    return function.__class__.__name__


def _coerce_context(
    context: OperationContext | None,
) -> OperationContext:
    if context is None:
        return OperationContext()
    if not isinstance(context, OperationContext):
        raise InvalidOperationContextError(
            "operation context must be an OperationContext.",
            field="context",
            expected="OperationContext",
            actual=type(context).__name__,
        )
    return context


def _validate_input(
    expected_input_type: type | tuple[type, ...] | None,
    input_value: object,
    *,
    operation_name: str,
) -> None:
    if expected_input_type is None:
        return
    if not isinstance(input_value, expected_input_type):
        raise InvalidOperationInputError(
            "operation input does not match contract input_type.",
            operation_name=operation_name,
            field="input_value",
            expected=repr(expected_input_type),
            actual=type(input_value).__name__,
        )


def _validate_required_context(
    required_context: tuple[str, ...],
    metadata: Mapping[str, object],
    *,
    operation_name: str,
    role: OperationRole,
) -> None:
    missing = tuple(
        key for key in required_context
        if key not in metadata
    )
    if missing:
        raise InvalidOperationContextError(
            "operation context is missing required metadata keys.",
            operation_name=operation_name,
            role=role.value,
            field="context.metadata",
            expected=required_context,
            missing=missing,
        )

def _coerce_and_validate_result(
    result: object,
    *,
    operation_name: str,
    contract: OperationContract,
    context: OperationContext,
) -> OperationResult:
    if isinstance(result, OperationResult):
        if result.operation_name != operation_name:
            raise InvalidOperationResultError(
                "operation result operation_name does not match wrapper name.",
                operation_name=operation_name,
                field="operation_name",
                expected=operation_name,
                actual=result.operation_name,
            )
        if result.role != contract.role:
            raise InvalidOperationResultError(
                "operation result role does not match contract role.",
                operation_name=operation_name,
                field="role",
                expected=contract.role.value,
                actual=result.role.value,
            )
        _validate_result_output_type(
            contract.output_type,
            result.output,
            operation_name=operation_name,
        )
        _validate_side_effect_evidence(
            contract,
            result.side_effect_evidence,
            operation_name=operation_name,
        )
        return result

    wrapped = OperationResult(
        output=result,
        operation_name=operation_name,
        role=contract.role,
        metadata=context.metadata,
        provenance=context.provenance,
        side_effect_evidence=None,
    )
    _validate_result_output_type(
        contract.output_type,
        wrapped.output,
        operation_name=operation_name,
    )
    _validate_side_effect_evidence(
        contract,
        wrapped.side_effect_evidence,
        operation_name=operation_name,
    )
    return wrapped


def _validate_result_output_type(
    expected_output_type: type | tuple[type, ...] | None,
    output: object,
    *,
    operation_name: str,
) -> None:
    if expected_output_type is None:
        return
    if not isinstance(output, expected_output_type):
        raise InvalidOperationResultError(
            "operation result output does not match contract output_type.",
            operation_name=operation_name,
            field="output",
            expected=repr(expected_output_type),
            actual=type(output).__name__,
        )


def _validate_side_effect_evidence(
    contract: OperationContract,
    side_effect_evidence: Mapping[str, object],
    *,
    operation_name: str,
) -> None:
    if contract.mutation_policy in {
        OperationMutationPolicy.PURE,
        OperationMutationPolicy.MAY_MUTATE,
    } and len(side_effect_evidence) > 0:
        raise InvalidOperationResultError(
            "operation result side_effect_evidence is invalid for non-side-effecting contract.",
            operation_name=operation_name,
            field="side_effect_evidence",
            expected="empty mapping",
            actual=dict(side_effect_evidence),
        )

    if contract.mutation_policy == OperationMutationPolicy.SIDE_EFFECTING:
        unexpected = tuple(
            key for key in side_effect_evidence
            if key not in contract.side_effects
        )
        if unexpected:
            raise InvalidOperationResultError(
                "operation result side_effect_evidence keys must be declared side effects.",
                operation_name=operation_name,
                field="side_effect_evidence.keys",
                expected=contract.side_effects,
                actual=unexpected,
            )
