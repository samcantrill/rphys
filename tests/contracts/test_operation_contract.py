from __future__ import annotations

import pytest

from rphys.errors import (
    InvalidOperationContractError,
    InvalidOperationResultError,
)
from rphys.ops import OperationContract, OperationContext, OperationResult


def test_operation_context_and_result_are_runtime_records() -> None:
    context = OperationContext(metadata={"split": "train"}, provenance={"version": "1.0"})
    result = OperationResult(
        output=1,
        operation_name="demo",
        metadata={"elapsed_ms": 1},
        provenance={"stage": "contract"},
        side_effect_evidence={"status": "ok"},
    )

    assert context.metadata["split"] == "train"
    assert context.provenance["version"] == "1.0"
    assert result.operation_name == "demo"
    assert result.metadata["elapsed_ms"] == 1


def test_operation_contract_failure_modes_are_rejectable_and_tuple_normalized() -> None:
    with pytest.raises(InvalidOperationContractError):
        OperationContract(side_effects=[""])
    with pytest.raises(InvalidOperationResultError):
        OperationResult(output=None, operation_name="")


def test_operation_contract_records_do_not_expose_deferred_fields() -> None:
    context = OperationContext()
    result = OperationResult(output={"payload": 1}, operation_name="demo")

    assert not hasattr(context, "operation_name")
    assert not hasattr(context, "side_effect_evidence")
    assert not hasattr(result, "required_context")
    assert not hasattr(result, "side_effects")
