from __future__ import annotations

import pytest

from rphys.errors import InvalidOperationContractError
from rphys.ops import (
    OperationContract,
    OperationMutationPolicy,
    OperationRole,
)


def test_contract_defaults_are_minimal_and_frozen_shape() -> None:
    contract = OperationContract()

    assert contract == OperationContract(
        role=OperationRole.GENERIC,
        mutation_policy=OperationMutationPolicy.PURE,
    )
    assert contract.role == OperationRole.GENERIC
    assert contract.input_type is None
    assert contract.output_type is None
    assert contract.mutation_policy == OperationMutationPolicy.PURE
    assert contract.side_effects == ()
    assert contract.required_context == ()
    assert contract.failure_modes == ()


def test_contract_accepts_type_sequences_and_text_roles() -> None:
    contract = OperationContract(
        role="generic",
        input_type=(str, bytes),
        output_type=(list,),
        mutation_policy="side_effecting",
        side_effects=["artifact_write", "metric_emit"],
        required_context=("dataset_id", "subject_id"),
        failure_modes=("schema_violation", "execution_failed"),
    )

    assert contract.role is OperationRole.GENERIC
    assert contract.mutation_policy is OperationMutationPolicy.SIDE_EFFECTING
    assert contract.side_effects == ("artifact_write", "metric_emit")
    assert contract.required_context == ("dataset_id", "subject_id")
    assert contract.failure_modes == ("schema_violation", "execution_failed")


def test_contract_rejects_invalid_role_and_mutation_policy() -> None:
    with pytest.raises(InvalidOperationContractError):
        OperationContract(role="unknown")

    with pytest.raises(InvalidOperationContractError):
        OperationContract(mutation_policy="random")


def test_contract_rejects_type_expectation_shapes() -> None:
    with pytest.raises(InvalidOperationContractError):
        OperationContract(input_type=[str, int])

    with pytest.raises(InvalidOperationContractError):
        OperationContract(output_type=(str, "type"))


def test_contract_mutation_side_effect_rules() -> None:
    with pytest.raises(InvalidOperationContractError):
        OperationContract(mutation_policy=OperationMutationPolicy.PURE, side_effects=["log"])

    with pytest.raises(InvalidOperationContractError):
        OperationContract(mutation_policy=OperationMutationPolicy.MAY_MUTATE, side_effects=["log"])

    with pytest.raises(InvalidOperationContractError):
        OperationContract(mutation_policy=OperationMutationPolicy.SIDE_EFFECTING)

    contract = OperationContract(
        mutation_policy=OperationMutationPolicy.SIDE_EFFECTING,
        side_effects=["cache_update"],
    )
    assert contract.side_effects == ("cache_update",)


def test_contract_rejects_blank_and_duplicate_labels() -> None:
    with pytest.raises(InvalidOperationContractError):
        OperationContract(side_effects=[""])

    with pytest.raises(InvalidOperationContractError):
        OperationContract(required_context=["source", "source"])


def test_contract_normalizes_sequences_and_copies_inputs() -> None:
    source_context = ["subject_id", "segment_id"]
    source_failures = ["type_error", "shape_error"]
    contract = OperationContract(
        side_effects=["metric_emit"],
        mutation_policy=OperationMutationPolicy.SIDE_EFFECTING,
        required_context=source_context,
        failure_modes=source_failures,
    )

    assert isinstance(contract.required_context, tuple)
    assert contract.required_context == ("subject_id", "segment_id")
    assert isinstance(contract.failure_modes, tuple)
    assert contract.failure_modes == ("type_error", "shape_error")

    source_context.append("mutated")
    source_failures.append("mutated")

    assert contract.required_context == ("subject_id", "segment_id")
    assert contract.failure_modes == ("type_error", "shape_error")


def test_contract_fields_are_exactly_declared() -> None:
    contract = OperationContract()

    assert list(type(contract).__dataclass_fields__) == [
        "role",
        "input_type",
        "output_type",
        "mutation_policy",
        "side_effects",
        "required_context",
        "failure_modes",
    ]


def test_contract_rejects_string_sequence_members_that_are_not_string_mapping_like() -> None:
    with pytest.raises(InvalidOperationContractError):
        OperationContract(side_effects=(1, 2))
