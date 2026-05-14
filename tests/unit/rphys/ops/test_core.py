from __future__ import annotations

import pytest

from rphys.errors import (
    InvalidOperationContextError,
    InvalidOperationContractError,
    InvalidOperationInputError,
    InvalidOperationResultError,
    OperationExecutionError,
)
from rphys.ops import (
    Operation,
    OperationContext,
    OperationContract,
    OperationResult,
)


def plain_add(value: int, *, context: OperationContext) -> int:
    return value + context.metadata.get("offset", 0)


def plain_dict_result(value: int, *, context: OperationContext) -> OperationResult:
    return OperationResult(
        output=value + context.metadata.get("offset", 0),
        operation_name="named",
        role="generic",
        metadata={"from": "kernel"},
        provenance={"phase": "test"},
    )


class Adder:
    def __init__(self, offset: int) -> None:
        self.offset = offset
        self.calls: list[tuple[object, OperationContext]] = []

    def __call__(self, value: int, context: OperationContext) -> int:
        self.calls.append((value, context))
        return value + self.offset


def test_operation_constructor_infers_name_and_defaults_contract() -> None:
    operation = Operation(plain_add)

    assert operation.name == "plain_add"
    assert operation.contract == OperationContract()


def test_operation_constructor_allows_callable_objects_and_explicit_name() -> None:
    adder = Adder(offset=2)
    operation = Operation(adder, name="adder")

    assert operation.name == "adder"
    assert operation.contract == OperationContract()


def test_constructor_rejects_non_callable() -> None:
    with pytest.raises(InvalidOperationContractError):
        Operation("not-callable")  # type: ignore[arg-type]


def test_operation_run_wraps_bare_output_and_merges_context_metadata_provenance() -> None:
    context = OperationContext(
        metadata={"dataset_id": "ds-1"},
        provenance={"source": "unit"},
    )
    operation = Operation(plain_add)

    result = operation(1, context=context)

    assert result.operation_name == operation.name
    assert result.role.value == operation.contract.role.value
    assert result.output == 1
    assert result.metadata == {"dataset_id": "ds-1"}
    assert result.provenance == {"source": "unit"}
    assert result.side_effect_evidence == {}


def test_run_and_call_return_identical_types_and_default_context_shape() -> None:
    operation = Operation(plain_add, contract=OperationContract())

    run_result = operation.run(3)
    call_result = operation(3)

    assert run_result.output == 3
    assert run_result.metadata == {}
    assert run_result.provenance == {}
    assert call_result.output == 3
    assert run_result == call_result


def test_operation_rejects_missing_required_context_before_invocation() -> None:
    adder = Adder(offset=1)
    operation = Operation(
        adder,
        contract=OperationContract(
            input_type=int,
            required_context=("dataset_id",),
        ),
    )

    with pytest.raises(InvalidOperationContextError):
        operation(3, context=OperationContext(metadata={"phase": "train"}))

    assert adder.calls == []


def test_operation_rejects_invalid_input_type_before_invocation() -> None:
    calls = []

    def kernel(value: int, *, context: OperationContext) -> int:
        calls.append(value)
        return value

    operation = Operation(
        kernel,
        contract=OperationContract(input_type=int),
    )

    with pytest.raises(InvalidOperationInputError):
        operation("bad", context=OperationContext())

    assert calls == []


def test_operation_validates_callable_returned_result_name_role_and_output_type() -> None:
    def returns_invalid_output(value: int, *, context: OperationContext) -> OperationResult:
        return OperationResult(
            output=value,
            operation_name="named",
            role="generic",
        )

    operation = Operation(
        returns_invalid_output,
        name="named",
        contract=OperationContract(
            output_type=str,
        ),
    )

    with pytest.raises(InvalidOperationResultError):
        operation(1, context=OperationContext())


def test_callable_returned_result_is_preserved_without_context_merging() -> None:
    operation = Operation(
        plain_dict_result,
        name="named",
        contract=OperationContract(output_type=int, role="generic"),
    )

    result = operation(2, context=OperationContext(metadata={"dataset_id": "ds-1"}))

    assert result.metadata == {"from": "kernel"}
    assert result.provenance == {"phase": "test"}
    assert result.side_effect_evidence == {}


def test_invalid_side_effect_evidence_is_rejected_for_pure_policy() -> None:
    def pure_result(value: int, *, context: OperationContext) -> OperationResult:
        return OperationResult(
            output=value,
            operation_name="op",
            side_effect_evidence={"flag": "on"},
        )

    operation = Operation(
        pure_result,
        name="op",
        contract=OperationContract(mutation_policy="pure", input_type=int),
    )

    with pytest.raises(InvalidOperationResultError):
        operation(1, context=OperationContext())


def test_side_effect_labels_are_subset_for_side_effecting_contract() -> None:
    def side_effecting(value: int, *, context: OperationContext) -> OperationResult:
        return OperationResult(
            output=value,
            operation_name="effects",
            role="generic",
            side_effect_evidence={"artifact_write": "ok"},
        )

    operation = Operation(
        side_effecting,
        name="effects",
        contract=OperationContract(
            mutation_policy="side_effecting",
            side_effects=["artifact_write", "metric_emit"],
        ),
    )

    result = operation(1, context=OperationContext())

    assert result.side_effect_evidence == {"artifact_write": "ok"}


def test_operation_execution_error_preserves_original_cause() -> None:
    def failure(value: int, *, context: OperationContext) -> int:
        raise ValueError("boom")

    operation = Operation(failure)

    with pytest.raises(OperationExecutionError) as exc:
        operation(1, context=OperationContext())

    assert isinstance(exc.value.__cause__, ValueError)
