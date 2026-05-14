from __future__ import annotations

from collections import OrderedDict
import inspect

import pytest

from rphys.errors import (
    InvalidOperationContextError,
    InvalidOperationPipelineError,
    OperationPipelineExecutionError,
    InvalidOperationInputError,
)
from rphys.ops import (
    Operation,
    OperationContract,
    OperationContext,
    OperationPipeline,
    OperationResult,
)


def increment(value: int, *, context: OperationContext) -> int:
    return value + 1


def multiply(value: int, *, context: OperationContext) -> int:
    return value * 10


def failure(value: object, *, context: OperationContext) -> int:
    raise ValueError("boom")


def test_operation_pipeline_signature_is_fixed() -> None:
    ctor = inspect.signature(OperationPipeline.__init__)
    params = list(ctor.parameters.values())[1:]

    assert len(params) == 1
    assert params[0].name == "operations"
    assert params[0].annotation == "Sequence[Operation]"


def test_operation_pipeline_exposes_immutable_operations_tuple() -> None:
    op_a = Operation(increment, name="increment")
    op_b = Operation(multiply, name="multiply")
    pipeline = OperationPipeline([op_a, op_b])

    assert pipeline.operations == (op_a, op_b)
    with pytest.raises(AttributeError):
        pipeline.operations = ()


def test_operation_pipeline_runs_steps_and_forwards_result_output() -> None:
    seen: list[int] = []

    def record(value: int, *, context: OperationContext) -> int:
        seen.append(value)
        return value + 2

    pipeline = OperationPipeline(
        [
            Operation(record, name="record"),
            Operation(multiply, name="multiply", contract=OperationContract(input_type=int)),
        ]
    )

    result = pipeline.run(1)

    assert seen == [1]
    assert result.output == 30
    assert result.operation_name == "multiply"


def test_operation_pipeline_call_and_run_share_final_result_shape() -> None:
    pipeline = OperationPipeline(
        [
            Operation(increment, name="increment"),
            Operation(multiply, name="multiply", contract=OperationContract(input_type=int)),
        ]
    )

    assert pipeline.run(1).output == pipeline(1).output


def test_operation_pipeline_rejects_empty_sequence() -> None:
    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline([])


def test_operation_pipeline_rejects_non_sequence_and_named_entry_inputs() -> None:
    step = Operation(increment)

    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline("abc")
    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline(b"abc")
    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline({"a": step})
    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline(OrderedDict({"a": step}))
    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline([("increment", step)])
    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline(["bad", step])


def test_operation_pipeline_rejects_non_operation_entries() -> None:
    with pytest.raises(InvalidOperationPipelineError) as exc:
        OperationPipeline([object()])

    assert exc.value.context["step_index"] == 0


def test_adjacent_contract_types_must_be_compatible() -> None:
    upstream = Operation(increment, name="upstream", contract=OperationContract(output_type=object))
    downstream = Operation(multiply, name="downstream", contract=OperationContract(input_type=int))

    with pytest.raises(InvalidOperationPipelineError) as exc:
        OperationPipeline([upstream, downstream])

    assert exc.value.context["upstream_step_index"] == 0
    assert exc.value.context["downstream_step_index"] == 1
    assert exc.value.context["upstream_operation_name"] == "upstream"
    assert exc.value.context["downstream_operation_name"] == "downstream"
    assert exc.value.context["expected"] == ("int",)
    assert exc.value.context["actual"] == ("object",)


def test_partial_overlap_declared_outputs_fail() -> None:
    upstream = Operation(increment, name="upstream", contract=OperationContract(output_type=(int, str)))
    downstream = Operation(multiply, name="downstream", contract=OperationContract(input_type=int))

    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline([upstream, downstream])


def test_operation_pipeline_preserves_context_identity_for_explicit_context() -> None:
    contexts: list[OperationContext] = []

    def capture(value: int, *, context: OperationContext) -> int:
        contexts.append(context)
        return value + 1

    shared = OperationContext(metadata={"source": "unit"})
    pipeline = OperationPipeline(
        [
            Operation(capture, name="capture-1"),
            Operation(capture, name="capture-2"),
            Operation(capture, name="capture-3"),
        ]
    )
    pipeline.run(1, context=shared)

    assert contexts[0] is shared
    assert contexts[1] is shared
    assert contexts[2] is shared


def test_operation_pipeline_omits_context_and_creates_one_empty_context_once() -> None:
    observed: list[OperationContext] = []

    def capture(value: int, *, context: OperationContext) -> int:
        observed.append(context)
        return value + 1

    pipeline = OperationPipeline(
        [
            Operation(capture),
            Operation(capture),
        ]
    )
    pipeline.run(1)

    assert len(observed) == 2
    assert observed[0] is observed[1]
    assert observed[0].metadata == {}
    assert observed[0].provenance == {}


def test_invalid_provided_context_becomes_pipeline_execution_error() -> None:
    pipeline = OperationPipeline([Operation(increment)])

    with pytest.raises(OperationPipelineExecutionError) as exc:
        pipeline.run(1, context="bad")

    assert exc.value.context["step_index"] is None
    assert exc.value.context["phase"] == "validate_context"
    assert exc.value.context["cause_type"] == "InvalidOperationContextError"
    assert isinstance(exc.value.__cause__, InvalidOperationContextError)


def test_pipeline_execution_errors_wrap_cause_and_include_step() -> None:
    pipeline = OperationPipeline(
        [
            Operation(failure, name="failure"),
            Operation(increment),
        ]
    )

    with pytest.raises(OperationPipelineExecutionError) as exc:
        pipeline.run(1)

    assert exc.value.context["step_index"] == 0
    assert exc.value.context["operation_name"] == "failure"
    assert exc.value.context["phase"] == "run"
    assert exc.value.context["cause_type"] == "OperationExecutionError"
    assert exc.value.__cause__.__class__.__name__ == "OperationExecutionError"
    assert exc.value.__cause__.__cause__.__class__.__name__ == "ValueError"


def test_pipeline_wraps_runtime_step_input_mismatch() -> None:
    def source(value: object, *, context: OperationContext) -> str:
        return "not-an-int"

    upstream = Operation(
        source,
        name="source",
        contract=OperationContract(output_type=None),
    )
    downstream = Operation(
        multiply,
        name="typed-downstream",
        contract=OperationContract(input_type=int),
    )
    pipeline = OperationPipeline([upstream, downstream])

    with pytest.raises(OperationPipelineExecutionError) as exc:
        pipeline.run(1)

    assert exc.value.context["step_index"] == 1
    assert exc.value.context["operation_name"] == "typed-downstream"
    assert exc.value.context["cause_type"] == "InvalidOperationInputError"
    assert isinstance(exc.value.__cause__, InvalidOperationInputError)
