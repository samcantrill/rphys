from __future__ import annotations

import inspect
import pytest

from rphys.errors import InvalidOperationPipelineError
from rphys.ops import (
    Operation,
    OperationContract,
    OperationContext,
    OperationPipeline,
)


def plus_one(value: int, *, context: OperationContext) -> int:
    return value + 1


def times_two(value: int, *, context: OperationContext) -> int:
    return value * 2


def test_operation_pipeline_public_api_is_sequence_only() -> None:
    ctor = inspect.signature(OperationPipeline.__init__)
    params = list(ctor.parameters.values())[1:]

    assert len(params) == 1
    assert params[0].name == "operations"


def test_operation_pipeline_exposes_only_operations_tuple() -> None:
    pipeline = OperationPipeline([
        Operation(plus_one),
        Operation(times_two, contract=OperationContract(input_type=int)),
    ])

    assert isinstance(pipeline.operations, tuple)
    assert len(pipeline.operations) == 2


def test_pipeline_contract_checks_sequential_type_compatibility() -> None:
    first = Operation(plus_one, contract=OperationContract(output_type=int))
    second = Operation(times_two, contract=OperationContract(input_type=(int, float)))
    contract_ok = OperationPipeline([first, second])

    assert isinstance(contract_ok.operations, tuple)

    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline(
            [
                Operation(plus_one, contract=OperationContract(output_type=object)),
                Operation(times_two, contract=OperationContract(input_type=int)),
            ]
        )


def test_pipeline_does_not_expose_stable_step_or_pipeline_name_apis() -> None:
    assert not hasattr(OperationPipeline, "steps")
    assert not hasattr(OperationPipeline, "name")
    assert not hasattr(OperationPipeline, "run_raw")
    assert not hasattr(OperationPipeline, "pipeline_name")
