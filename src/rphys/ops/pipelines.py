"""Ordered generic operation composition for Stage 6."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from rphys.errors import (
    InvalidOperationContextError,
    InvalidOperationPipelineError,
    OperationPipelineExecutionError,
)

from .context import OperationContext, OperationResult
from .core import Operation

__all__ = ["OperationPipeline"]


class OperationPipeline:
    """Ordered composition over concrete :class:`Operation` steps."""

    __slots__ = ("_operations",)

    def __init__(self, operations: Sequence[Operation]) -> None:
        if isinstance(operations, (str, bytes, bytearray)):
            raise InvalidOperationPipelineError(
                "operation pipeline operations must be a sequence, not text.",
                field="operations",
                expected="non-empty sequence of Operation",
                actual=type(operations).__name__,
            )

        if isinstance(operations, Mapping):
            raise InvalidOperationPipelineError(
                "operation pipeline operations must be an ordered sequence, not a mapping.",
                field="operations",
                expected="sequence of Operation",
                actual=type(operations).__name__,
                includes_mapping=True,
            )

        if not isinstance(operations, Sequence):
            raise InvalidOperationPipelineError(
                "operation pipeline operations must be a sequence.",
                field="operations",
                expected="Sequence[Operation]",
                actual=type(operations).__name__,
            )

        self._operations = tuple(self._coerce_operation(entry, index) for index, entry in enumerate(operations))

        if len(self._operations) == 0:
            raise InvalidOperationPipelineError(
                "operation pipeline must contain at least one operation.",
                field="operations",
                expected="non-empty sequence of Operation",
                actual="empty sequence",
            )

        self._validate_compatibility()

    @property
    def operations(self) -> tuple[Operation, ...]:
        """Ordered tuple of composed operations."""
        return self._operations

    def run(self, input_value: object, context: OperationContext | None = None) -> OperationResult:
        """Execute each step and return the final ``OperationResult``."""
        try:
            execution_context = _coerce_context(context)
        except Exception as exc:
            raise OperationPipelineExecutionError(
                "operation pipeline context could not be validated.",
                step_index=None,
                phase="validate_context",
                cause_type=type(exc).__name__,
            ) from exc

        result = None
        current_value = input_value
        for step_index, operation in enumerate(self._operations):
            result = _run_step(
                operation,
                step_index,
                current_value,
                execution_context,
            )
            current_value = result.output
        return result

    def __call__(self, input_value: object, context: OperationContext | None = None) -> OperationResult:
        """Execute steps with the same semantics as ``run``."""
        return self.run(input_value, context=context)

    def _validate_compatibility(self) -> None:
        """Validate declared adjacent output/input compatibility."""
        for step_index in range(len(self._operations) - 1):
            current_step = self._operations[step_index]
            next_step = self._operations[step_index + 1]

            current_output = _normalize_type_tuple(current_step.contract.output_type)
            next_input = _normalize_type_tuple(next_step.contract.input_type)
            if current_output is None or next_input is None:
                continue

            if not _compatible_type_tuple_pairs(current_output, next_input):
                raise InvalidOperationPipelineError(
                    "operation pipeline adjacent declarations are not type-compatible.",
                    upstream_step_index=step_index,
                    upstream_operation_name=current_step.name,
                    downstream_step_index=step_index + 1,
                    downstream_operation_name=next_step.name,
                    expected=_render_type_tuple(next_input),
                    actual=_render_type_tuple(current_output),
                    field="operations",
                )

    @staticmethod
    def _coerce_operation(entry: object, index: int) -> Operation:
        if isinstance(entry, (tuple, list)) and len(entry) == 2 and isinstance(entry[0], str):
            raise InvalidOperationPipelineError(
                "operation pipeline entries must be concrete Operation instances.",
                field=f"operations[{index}]",
                expected="Operation",
                actual="tuple[str, Operation]",
                step_index=index,
            )

        if not isinstance(entry, Operation):
            raise InvalidOperationPipelineError(
                "operation pipeline entries must be concrete Operation instances.",
                field=f"operations[{index}]",
                expected="Operation",
                actual=type(entry).__name__,
                step_index=index,
            )

        return entry


def _coerce_context(context: OperationContext | None) -> OperationContext:
    if context is None:
        return OperationContext()
    if isinstance(context, OperationContext):
        return context

    raise InvalidOperationContextError(
        "operation pipeline context must be an OperationContext.",
        field="context",
        expected="OperationContext",
        actual=type(context).__name__,
    )


def _normalize_type_tuple(
    declared: type | tuple[type, ...] | None,
) -> tuple[type, ...] | None:
    if declared is None:
        return None
    if isinstance(declared, tuple):
        return declared
    return (declared,)


def _compatible_type_tuple_pairs(
    upstream_types: tuple[type, ...],
    downstream_types: tuple[type, ...],
) -> bool:
    return all(
        any(issubclass(upstream_type, downstream_type) for downstream_type in downstream_types)
        for upstream_type in upstream_types
    )


def _render_type_tuple(declared_types: tuple[type, ...]) -> tuple[str, ...]:
    return tuple(declared_type.__name__ for declared_type in declared_types)


def _run_step(
    operation: Operation,
    step_index: int,
    input_value: object,
    context: OperationContext,
) -> OperationResult:
    try:
        return operation.run(input_value, context=context)
    except Exception as exc:
        raise OperationPipelineExecutionError(
            "operation pipeline step failed during execution.",
            step_index=step_index,
            operation_name=operation.name,
            phase="run",
            cause_type=type(exc).__name__,
        ) from exc
