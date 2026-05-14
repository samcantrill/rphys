from __future__ import annotations

import pytest
from types import MappingProxyType

from rphys.errors import (
    InvalidOperationContextError,
    InvalidOperationResultError,
)
from rphys.ops import (
    OperationContext,
    OperationResult,
    OperationRole,
)


def test_operation_context_defaults_to_empty_immutable_mappings() -> None:
    context = OperationContext()

    assert context.metadata == MappingProxyType({})
    assert context.provenance == MappingProxyType({})


def test_operation_context_copies_input_mappings_and_is_immutable() -> None:
    metadata = {"source": "sample-a"}
    provenance = {"transform_label": "baseline-filter"}

    context = OperationContext(metadata=metadata, provenance=provenance)

    metadata["source"] = "mutated"
    provenance["transform_label"] = "mutated"

    assert context.metadata == {"source": "sample-a"}
    assert context.provenance == {"transform_label": "baseline-filter"}
    assert isinstance(context.metadata, MappingProxyType)
    assert isinstance(context.provenance, MappingProxyType)

    with pytest.raises(TypeError):
        context.metadata["source"] = "forbidden"

    with pytest.raises(TypeError):
        context.provenance["transform_label"] = "forbidden"


def test_operation_context_rejects_non_mapping_inputs() -> None:
    with pytest.raises(InvalidOperationContextError):
        OperationContext(metadata=[("source", "sample")])

    with pytest.raises(InvalidOperationContextError):
        OperationContext(provenance=("k", "v"))


def test_operation_result_defaults_and_immutability() -> None:
    result = OperationResult(output=123, operation_name="filter")

    assert result.output == 123
    assert result.operation_name == "filter"
    assert result.role == OperationRole.GENERIC
    assert result.side_effect_evidence == {}
    assert result.metadata == {}
    assert result.provenance == {}

    assert isinstance(result.side_effect_evidence, MappingProxyType)
    with pytest.raises(TypeError):
        result.metadata["x"] = "y"


def test_operation_result_accepts_custom_role_and_fields() -> None:
    result = OperationResult(
        output=(1, 2),
        operation_name="combine",
        role=OperationRole.GENERIC,
        metadata={"k": "v"},
        provenance={"phase": 1},
        side_effect_evidence={"effects": ["ok"]},
    )

    assert result.role == OperationRole.GENERIC
    assert result.operation_name == "combine"
    assert result.metadata == {"k": "v"}
    assert result.provenance == {"phase": 1}
    assert result.side_effect_evidence == {"effects": ["ok"]}


def test_operation_result_rejects_invalid_operation_name() -> None:
    with pytest.raises(InvalidOperationResultError):
        OperationResult(output="v", operation_name="   ")

    with pytest.raises(InvalidOperationResultError):
        OperationResult(output="v", operation_name=0)


def test_operation_result_rejects_non_mapping_optional_fields() -> None:
    with pytest.raises(InvalidOperationResultError):
        OperationResult(output="v", operation_name="op", metadata="bad")

    with pytest.raises(InvalidOperationResultError):
        OperationResult(output="v", operation_name="op", side_effect_evidence=[("k", "v")])


def test_context_and_result_only_expose_phase_1_fields() -> None:
    context = OperationContext()
    result = OperationResult(output=None, operation_name="noop")

    assert hasattr(context, "metadata")
    assert hasattr(context, "provenance")
    assert not hasattr(context, "input")
    assert not hasattr(context, "output")
    assert not hasattr(context, "operation_name")

    assert hasattr(result, "operation_name")
    assert hasattr(result, "side_effect_evidence")
    assert not hasattr(result, "latency_ms")
    assert not hasattr(result, "run_id")
    assert not hasattr(result, "input_id")
