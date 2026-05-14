from __future__ import annotations

import inspect

import pytest

from rphys.errors import (
    InvalidOperationContextError,
    InvalidOperationInputError,
    InvalidOperationResultError,
    OperationExecutionError,
)
from rphys.ops import (
    Operation,
    OperationContract,
    OperationContext,
    OperationResult,
)


def plain_kernel(value: int, *, context: OperationContext) -> int:
    return value + 1


def result_kernel(value: int, *, context: OperationContext) -> OperationResult:
    return OperationResult(
        output=value + 1,
        operation_name="result-kernel",
        role="generic",
        metadata={"returned": True},
        provenance={"source": "kernel"},
    )


def failing_kernel(value: int, *, context: OperationContext) -> int:
    raise ValueError("boom")


def side_effect_kernel(value: int, *, context: OperationContext) -> OperationResult:
    return OperationResult(
        output=value,
        operation_name="effects",
        role="generic",
        side_effect_evidence={"unexpected": "bad"},
    )


def test_operation_constructor_signature_is_fixed() -> None:
    ctor_signature = inspect.signature(Operation.__init__)
    params = list(ctor_signature.parameters.values())[1:]

    assert len(params) == 3
    assert params[0].name == "function"
    assert params[1].name == "name" and params[1].kind == inspect.Parameter.KEYWORD_ONLY
    assert params[2].name == "contract" and params[2].kind == inspect.Parameter.KEYWORD_ONLY
    assert params[1].default is None
    assert params[2].default is None


def test_operation_call_signature_is_fixed_and_returns_result() -> None:
    run_signature = inspect.signature(Operation.run)
    call_signature = inspect.signature(Operation.__call__)
    run_params = list(run_signature.parameters.values())[1:]
    call_params = list(call_signature.parameters.values())[1:]

    assert [param.name for param in run_params] == ["input_value", "context"]
    assert [param.name for param in call_params] == ["input_value", "context"]
    assert run_params[1].default is None
    assert call_params[1].default is None


def test_operation_context_key_checks_only_use_metadata() -> None:
    contract = OperationContract(required_context=("dataset_id",))
    operation = Operation(plain_kernel, name="plain_kernel", contract=contract)

    with pytest.raises(InvalidOperationContextError):
        operation(1, context=OperationContext(provenance={"dataset_id": "missing"}))


def test_operation_input_type_validation_precedes_callable_invocation() -> None:
    seen = []

    def guarded_kernel(value: int, *, context: OperationContext) -> int:
        seen.append(value)
        return value

    operation = Operation(
        guarded_kernel,
        contract=OperationContract(input_type=int),
    )

    with pytest.raises(InvalidOperationInputError):
        operation("bad", context=OperationContext())

    assert seen == []


def test_operation_run_bare_output_wraps_context_and_uses_empty_side_effect_evidence() -> None:
    operation = Operation(plain_kernel)
    context = OperationContext(metadata={"dataset_id": "u1"}, provenance={"source": "contract"})

    result = operation.run(1, context=context)

    assert result.operation_name == "plain_kernel"
    assert result.metadata == {"dataset_id": "u1"}
    assert result.provenance == {"source": "contract"}
    assert result.side_effect_evidence == {}


def test_operation_call_returns_result_with_declared_context_and_output_type() -> None:
    operation = Operation(
        plain_kernel,
        name="call",
        contract=OperationContract(output_type=int),
    )
    context = OperationContext(metadata={"k": "v"})

    result = operation(1, context=context)

    assert result.output == 2
    assert result.operation_name == "call"
    assert result.metadata == {"k": "v"}


def test_operation_contract_can_return_valid_result_without_context_merge() -> None:
    operation = Operation(result_kernel, name="result-kernel")
    context = OperationContext(metadata={"k": "v"})

    result = operation(3, context=context)

    assert result.operation_name == "result-kernel"
    assert result.role.value == "generic"
    assert result.metadata == {"returned": True}
    assert result.provenance == {"source": "kernel"}
    assert result.output == 4


def test_operation_result_evidence_and_output_rules_are_validated() -> None:
    with pytest.raises(InvalidOperationResultError):
        Operation(
            side_effect_kernel,
            name="effects",
            contract=OperationContract(role="generic"),
        )(1, context=OperationContext())

    with pytest.raises(InvalidOperationResultError):
        Operation(
            side_effect_kernel,
            name="effects",
            contract=OperationContract(
                mutation_policy="side_effecting",
                side_effects=["artifact_write"],
            ),
        )(1, context=OperationContext())


def test_calling_kernel_error_is_wrapped_and_causes_preserved() -> None:
    operation = Operation(failing_kernel)

    with pytest.raises(OperationExecutionError) as exc:
        operation(1, context=OperationContext())

    assert isinstance(exc.value.__cause__, ValueError)


def test_no_raw_output_api_is_exported_on_operation() -> None:
    operation = Operation(plain_kernel)

    for forbidden_name in ["run_raw", "execute_raw", "call_raw", "raw", "output"]:
        assert not hasattr(operation, forbidden_name)
