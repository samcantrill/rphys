"""Ordered operation composition for generic, sample, and batch operations.

Generic :class:`OperationPipeline` stages are composed from a sequence only;
mapping- and name-based construction remains intentionally unsupported there.

Execution forwards each upstream step's :attr:`OperationResult.output` as the next
step input and returns the final :class:`OperationResult`.

Stage 7 specialized :class:`SampleOperationPipeline` and
:class:`BatchOperationPipeline` also accept insertion-ordered mappings. Mapping
keys are diagnostic step names only; they are not durable artifact identities,
routing labels, or workflow policy.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from rphys.errors import (
    InvalidOperationContextError,
    InvalidOperationPipelineError,
    OperationPipelineExecutionError,
)
from ._validation import coerce_non_empty_string
from .core import OperationStep

from .context import OperationContext, OperationResult
from .contracts import OperationContract

__all__ = ["OperationPipeline", "SampleOperationPipeline", "BatchOperationPipeline"]


class OperationPipeline:
    """Ordered composition over :class:`OperationStep` entries."""

    __slots__ = ("_operations",)

    def __init__(self, operations: Sequence[OperationStep]) -> None:
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

        self._operations = tuple(
            self._validate_operation_step(self._coerce_operation(entry, index), index)
            for index, entry in enumerate(operations)
        )

        if len(self._operations) == 0:
            raise InvalidOperationPipelineError(
                "operation pipeline must contain at least one operation.",
                field="operations",
                expected="non-empty sequence of Operation",
                actual="empty sequence",
            )

        self._validate_compatibility()

    @property
    def operations(self) -> tuple[OperationStep, ...]:
        """Ordered tuple of composed operation steps."""
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
    def _coerce_operation(entry: object, index: int) -> OperationStep:
        if isinstance(entry, (tuple, list)) and len(entry) == 2 and isinstance(entry[0], str):
            raise InvalidOperationPipelineError(
                "operation pipeline entries must be OperationStep instances.",
                field=f"operations[{index}]",
                expected="OperationStep",
                actual="tuple[str, Operation]",
                step_index=index,
            )

        if not isinstance(entry, OperationStep):
            raise InvalidOperationPipelineError(
                "operation pipeline entries must be OperationStep instances.",
                field=f"operations[{index}]",
                expected="OperationStep",
                actual=type(entry).__name__,
                step_index=index,
            )

        return entry

    @staticmethod
    def _validate_operation_step(operation: OperationStep, index: int) -> OperationStep:
        if not isinstance(operation.name, str) or not operation.name.strip():
            raise InvalidOperationPipelineError(
                "operation pipeline entries must expose non-empty string names.",
                field=f"operations[{index}]",
                expected="OperationStep with non-empty str name",
                actual=repr(operation.name),
                step_index=index,
            )

        if not isinstance(operation.contract, OperationContract):
            raise InvalidOperationPipelineError(
                "operation pipeline entries must expose OperationContract objects.",
                field=f"operations[{index}]",
                expected="OperationContract",
                actual=type(operation.contract).__name__,
                step_index=index,
            )

        if not hasattr(operation, "run") or not callable(getattr(operation, "run")):
            raise InvalidOperationPipelineError(
                "operation pipeline entries must expose a callable run method.",
                field=f"operations[{index}]",
                expected="OperationStep.run",
                actual=type(operation).__name__,
                step_index=index,
            )

        return operation

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
    operation: OperationStep,
    step_index: int,
    input_value: object,
    context: OperationContext,
) -> OperationResult:
    try:
        result = operation.run(input_value, context=context)
        if not isinstance(result, OperationResult):
            raise TypeError("step.run() must return OperationResult.")
        return result
    except AttributeError as exc:
        raise OperationPipelineExecutionError(
            "operation pipeline step failed to return an operation result.",
            step_index=step_index,
            operation_name=operation.name,
            phase="run",
            cause_type=type(exc).__name__,
        ) from exc
    except Exception as exc:
        raise OperationPipelineExecutionError(
            "operation pipeline step failed during execution.",
            step_index=step_index,
            operation_name=operation.name,
            phase="run",
            cause_type=type(exc).__name__,
        ) from exc


@dataclass(frozen=True, slots=True)
class _SamplePipelineStep:
    operation: OperationStep
    diagnostic_name: str


@dataclass(frozen=True, slots=True)
class _BatchPipelineStep:
    operation: OperationStep
    diagnostic_name: str


class SampleOperationPipeline:
    """Ordered composition over sample operation steps.

    Sequences use each operation's own name as the diagnostic step name.
    Mappings preserve insertion order and use keys only as diagnostics; mapping
    keys do not replace operation identities and are not durable artifact names.
    """

    __slots__ = ("_steps",)

    def __init__(self, operations: Sequence[object] | Mapping[str, object]) -> None:
        self._steps = _normalize_sample_pipeline_steps(operations)
        if len(self._steps) == 0:
            raise InvalidOperationPipelineError(
                "sample operation pipeline must contain at least one operation.",
                field="operations",
                expected="non-empty sequence or mapping of SampleOperation",
                actual="empty collection",
            )
        self._validate_compatibility()

    @property
    def operations(self) -> tuple[OperationStep, ...]:
        """Ordered tuple of composed sample operation steps."""

        return tuple(step.operation for step in self._steps)

    def run(
        self,
        input_value: object,
        context: object | None = None,
    ) -> OperationResult:
        """Execute sample steps in order and return the final result."""

        try:
            execution_context = _coerce_sample_pipeline_context(context)
        except Exception as exc:
            raise OperationPipelineExecutionError(
                "sample operation pipeline context could not be validated.",
                step_index=None,
                phase="validate_context",
                cause_type=type(exc).__name__,
            ) from exc

        result = None
        current_value = input_value
        for step_index, step in enumerate(self._steps):
            result = _run_sample_step(
                step,
                step_index,
                current_value,
                execution_context,
            )
            current_value = result.output
        return result

    def __call__(
        self,
        input_value: object,
        context: object | None = None,
    ) -> OperationResult:
        """Execute steps with the same semantics as ``run``."""

        return self.run(input_value, context=context)

    def _validate_compatibility(self) -> None:
        for step_index in range(len(self._steps) - 1):
            current_step = self._steps[step_index]
            next_step = self._steps[step_index + 1]

            current_output = _normalize_type_tuple(current_step.operation.contract.output_type)
            next_input = _normalize_type_tuple(next_step.operation.contract.input_type)
            if current_output is None or next_input is None:
                continue

            if not _compatible_type_tuple_pairs(current_output, next_input):
                raise InvalidOperationPipelineError(
                    "sample operation pipeline adjacent declarations are not type-compatible.",
                    upstream_step_index=step_index,
                    upstream_operation_name=current_step.operation.name,
                    upstream_step_name=current_step.diagnostic_name,
                    downstream_step_index=step_index + 1,
                    downstream_operation_name=next_step.operation.name,
                    downstream_step_name=next_step.diagnostic_name,
                    expected=_render_type_tuple(next_input),
                    actual=_render_type_tuple(current_output),
                    field="operations",
                )


def _normalize_sample_pipeline_steps(
    operations: Sequence[object] | Mapping[str, object],
) -> tuple[_SamplePipelineStep, ...]:
    if isinstance(operations, (str, bytes, bytearray)):
        raise InvalidOperationPipelineError(
            "sample operation pipeline operations must be a sequence or mapping, not text.",
            field="operations",
            expected="non-empty sequence or mapping of SampleOperation",
            actual=type(operations).__name__,
        )

    if isinstance(operations, Mapping):
        return tuple(
            _SamplePipelineStep(
                operation=_coerce_sample_pipeline_operation(
                    entry,
                    index,
                    diagnostic_name=diagnostic_name,
                ),
                diagnostic_name=diagnostic_name,
            )
            for index, (name, entry) in enumerate(operations.items())
            for diagnostic_name in (
                coerce_non_empty_string(
                    name,
                    owner="SampleOperationPipeline",
                    field=f"operations[{index}].key",
                    expected="non-empty string mapping key",
                    error_type=InvalidOperationPipelineError,
                ),
            )
        )

    if not isinstance(operations, Sequence):
        raise InvalidOperationPipelineError(
            "sample operation pipeline operations must be a sequence or mapping.",
            field="operations",
            expected="Sequence[SampleOperation] | Mapping[str, SampleOperation]",
            actual=type(operations).__name__,
        )

    steps: list[_SamplePipelineStep] = []
    for index, entry in enumerate(operations):
        operation = _coerce_sample_pipeline_operation(entry, index)
        steps.append(
            _SamplePipelineStep(
                operation=operation,
                diagnostic_name=operation.name,
            )
        )
    return tuple(steps)


def _coerce_sample_pipeline_operation(
    entry: object,
    index: int,
    *,
    diagnostic_name: str | None = None,
) -> OperationStep:
    from .sample import SampleOperation

    if isinstance(entry, (tuple, list)) and len(entry) == 2 and isinstance(entry[0], str):
        raise InvalidOperationPipelineError(
            "sample operation pipeline entries must be SampleOperation instances.",
            field=f"operations[{index}]",
            expected="SampleOperation",
            actual="tuple[str, SampleOperation]",
            step_index=index,
            step_name=diagnostic_name,
        )

    if not isinstance(entry, SampleOperation):
        raise InvalidOperationPipelineError(
            "sample operation pipeline entries must be SampleOperation instances.",
            field=f"operations[{index}]",
            expected="SampleOperation",
            actual=type(entry).__name__,
            step_index=index,
            step_name=diagnostic_name,
        )

    OperationPipeline._validate_operation_step(entry, index)
    return entry


def _coerce_sample_pipeline_context(context: object | None) -> object:
    from .sample import SampleOperationContext

    if context is None:
        return SampleOperationContext()
    if isinstance(context, SampleOperationContext):
        if context.operation_name is not None:
            raise InvalidOperationContextError(
                "sample operation pipeline context operation_name must be unset.",
                field="context.operation_name",
                expected="None",
                actual=context.operation_name,
            )
        return context
    if isinstance(context, OperationContext):
        return SampleOperationContext(
            metadata=context.metadata,
            provenance=context.provenance,
        )

    raise InvalidOperationContextError(
        "sample operation pipeline context must be None, OperationContext, or SampleOperationContext.",
        field="context",
        expected="OperationContext | SampleOperationContext | None",
        actual=type(context).__name__,
    )


def _run_sample_step(
    step: _SamplePipelineStep,
    step_index: int,
    input_value: object,
    context: object,
) -> OperationResult:
    try:
        result = step.operation.run(input_value, context=context)
        if not isinstance(result, OperationResult):
            raise TypeError("step.run() must return OperationResult.")
        return result
    except AttributeError as exc:
        raise OperationPipelineExecutionError(
            "sample operation pipeline step failed to return an operation result.",
            step_index=step_index,
            operation_name=step.operation.name,
            step_name=step.diagnostic_name,
            phase="run",
            cause_type=type(exc).__name__,
        ) from exc
    except Exception as exc:
        raise OperationPipelineExecutionError(
            "sample operation pipeline step failed during execution.",
            step_index=step_index,
            operation_name=step.operation.name,
            step_name=step.diagnostic_name,
            phase="run",
            cause_type=type(exc).__name__,
        ) from exc


class BatchOperationPipeline:
    """Ordered composition over provisional batch operation steps."""

    __slots__ = ("_steps",)

    def __init__(self, operations: Sequence[object] | Mapping[str, object]) -> None:
        self._steps = _normalize_batch_pipeline_steps(operations)
        if len(self._steps) == 0:
            raise InvalidOperationPipelineError(
                "batch operation pipeline must contain at least one operation.",
                field="operations",
                expected="non-empty sequence or mapping of BatchOperation",
                actual="empty collection",
            )
        self._validate_compatibility()

    @property
    def operations(self) -> tuple[OperationStep, ...]:
        """Ordered tuple of composed batch operation steps."""

        return tuple(step.operation for step in self._steps)

    def run(self, input_value: object, context: object | None = None) -> OperationResult:
        """Execute batch steps in order and return the final result."""

        try:
            execution_context = _coerce_batch_pipeline_context(context)
        except Exception as exc:
            raise OperationPipelineExecutionError(
                "batch operation pipeline context could not be validated.",
                step_index=None,
                phase="validate_context",
                cause_type=type(exc).__name__,
            ) from exc

        result = None
        current_value = input_value
        for step_index, step in enumerate(self._steps):
            result = _run_batch_step(step, step_index, current_value, execution_context)
            current_value = result.output
        return result

    def __call__(self, input_value: object, context: object | None = None) -> OperationResult:
        """Execute steps with the same semantics as ``run``."""

        return self.run(input_value, context=context)

    def _validate_compatibility(self) -> None:
        for step_index in range(len(self._steps) - 1):
            current_step = self._steps[step_index]
            next_step = self._steps[step_index + 1]

            current_output = _normalize_type_tuple(current_step.operation.contract.output_type)
            next_input = _normalize_type_tuple(next_step.operation.contract.input_type)
            if current_output is None or next_input is None:
                continue

            if not _compatible_type_tuple_pairs(current_output, next_input):
                raise InvalidOperationPipelineError(
                    "batch operation pipeline adjacent declarations are not type-compatible.",
                    upstream_step_index=step_index,
                    upstream_operation_name=current_step.operation.name,
                    upstream_step_name=current_step.diagnostic_name,
                    downstream_step_index=step_index + 1,
                    downstream_operation_name=next_step.operation.name,
                    downstream_step_name=next_step.diagnostic_name,
                    expected=_render_type_tuple(next_input),
                    actual=_render_type_tuple(current_output),
                    field="operations",
                )


def _normalize_batch_pipeline_steps(
    operations: Sequence[object] | Mapping[str, object],
) -> tuple[_BatchPipelineStep, ...]:
    if isinstance(operations, (str, bytes, bytearray)):
        raise InvalidOperationPipelineError(
            "batch operation pipeline operations must be a sequence or mapping, not text.",
            field="operations",
            expected="non-empty sequence or mapping of BatchOperation",
            actual=type(operations).__name__,
        )

    if isinstance(operations, Mapping):
        return tuple(
            _BatchPipelineStep(
                operation=_coerce_batch_pipeline_operation(
                    entry,
                    index,
                    diagnostic_name=diagnostic_name,
                ),
                diagnostic_name=diagnostic_name,
            )
            for index, (name, entry) in enumerate(operations.items())
            for diagnostic_name in (
                coerce_non_empty_string(
                    name,
                    owner="BatchOperationPipeline",
                    field=f"operations[{index}].key",
                    expected="non-empty string mapping key",
                    error_type=InvalidOperationPipelineError,
                ),
            )
        )

    if not isinstance(operations, Sequence):
        raise InvalidOperationPipelineError(
            "batch operation pipeline operations must be a sequence or mapping.",
            field="operations",
            expected="Sequence[BatchOperation] | Mapping[str, BatchOperation]",
            actual=type(operations).__name__,
        )

    steps: list[_BatchPipelineStep] = []
    for index, entry in enumerate(operations):
        operation = _coerce_batch_pipeline_operation(entry, index)
        steps.append(_BatchPipelineStep(operation=operation, diagnostic_name=operation.name))
    return tuple(steps)


def _coerce_batch_pipeline_operation(
    entry: object,
    index: int,
    *,
    diagnostic_name: str | None = None,
) -> OperationStep:
    from .batch import BatchOperation

    if isinstance(entry, (tuple, list)) and len(entry) == 2 and isinstance(entry[0], str):
        raise InvalidOperationPipelineError(
            "batch operation pipeline entries must be BatchOperation instances.",
            field=f"operations[{index}]",
            expected="BatchOperation",
            actual="tuple[str, BatchOperation]",
            step_index=index,
            step_name=diagnostic_name,
        )

    if not isinstance(entry, BatchOperation):
        raise InvalidOperationPipelineError(
            "batch operation pipeline entries must be BatchOperation instances.",
            field=f"operations[{index}]",
            expected="BatchOperation",
            actual=type(entry).__name__,
            step_index=index,
            step_name=diagnostic_name,
        )

    OperationPipeline._validate_operation_step(entry, index)
    return entry


def _coerce_batch_pipeline_context(context: object | None) -> object:
    from .batch import BatchOperationContext

    if context is None:
        return BatchOperationContext()
    if isinstance(context, BatchOperationContext):
        if context.operation_name is not None:
            raise InvalidOperationContextError(
                "batch operation pipeline context operation_name must be unset.",
                field="context.operation_name",
                expected="None",
                actual=context.operation_name,
            )
        return context
    if isinstance(context, OperationContext):
        return BatchOperationContext(metadata=context.metadata, provenance=context.provenance)

    raise InvalidOperationContextError(
        "batch operation pipeline context must be None, OperationContext, or BatchOperationContext.",
        field="context",
        expected="OperationContext | BatchOperationContext | None",
        actual=type(context).__name__,
    )


def _run_batch_step(
    step: _BatchPipelineStep,
    step_index: int,
    input_value: object,
    context: object,
) -> OperationResult:
    try:
        result = step.operation.run(input_value, context=context)
        if not isinstance(result, OperationResult):
            raise TypeError("step.run() must return OperationResult.")
        return result
    except AttributeError as exc:
        raise OperationPipelineExecutionError(
            "batch operation pipeline step failed to return an operation result.",
            step_index=step_index,
            operation_name=step.operation.name,
            step_name=step.diagnostic_name,
            phase="run",
            cause_type=type(exc).__name__,
        ) from exc
    except Exception as exc:
        raise OperationPipelineExecutionError(
            "batch operation pipeline step failed during execution.",
            step_index=step_index,
            operation_name=step.operation.name,
            step_name=step.diagnostic_name,
            phase="run",
            cause_type=type(exc).__name__,
        ) from exc
