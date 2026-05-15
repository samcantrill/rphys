"""Focused tests for Stage 7 sample operation foundations."""

from __future__ import annotations

from types import MappingProxyType

import pytest

from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.data.sample_fields import SampleField, SampleFieldState
from rphys.errors import (
    InvalidFieldLocatorError,
    InvalidOperationContractError,
    InvalidOperationContextError,
    InvalidOperationInputError,
    InvalidOperationResultError,
    MissingFieldError,
    OperationExecutionError,
)
from rphys.io.codecs import CodecLoadResult, LoadContext
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef
from rphys.ops import (
    OperationContext,
    OperationResult,
    SampleFieldPermissions,
    SampleOperation,
    SampleOperationContext,
    SampleOperationContract,
    SampleReplayRecord,
)


VIDEO = FieldLocator.parse("inputs/video.rgb")
SECONDARY = FieldLocator.parse("inputs/video.mask")
ANOTHER = FieldLocator.parse("inputs/mask.rgb")


def _identity(payload: Sample, *, context: SampleOperationContext) -> Sample:
    return payload


def _typed_result(payload: Sample, *, context: SampleOperationContext) -> OperationResult:
    return OperationResult(
        output=payload,
        operation_name="op",
        metadata={"kernel": "explicit"},
        provenance={"path": "test"},
    )


def _load_context() -> LoadContext:
    return LoadContext(
        FieldView(
            FieldRef(
                "video.rgb",
                [ResourceRef("file:///samples/1.bin", "file")],
                schema="video.rgb.v1",
            ),
            TemporalIndexSlice(0, 4),
        )
    )


def _load_result(payload: object = ("frame-1", "frame-2")) -> CodecLoadResult:
    return CodecLoadResult(
        FieldValue(payload, schema="video.rgb.v1"),
        metadata={"codec": "unit"},
    )


class CountingLoader:
    def __init__(self, result: object) -> None:
        self.result = result
        self.calls = 0

    def __call__(self, context: LoadContext) -> CodecLoadResult:
        self.calls += 1
        return self.result if isinstance(self.result, CodecLoadResult) else self.result  # type: ignore[return-value]


def test_field_permissions_normalizes_and_freezes_declarations() -> None:
    permissions = SampleFieldPermissions(
        reads=[VIDEO, "inputs/mask.rgb"],
        writes=(ANOTHER,),
        deletes="inputs/video.mask",
        dynamic_writes=[VIDEO],
    )

    assert permissions.reads == (VIDEO, ANOTHER)
    assert permissions.writes == (ANOTHER,)
    assert permissions.deletes == (SECONDARY,)
    assert permissions.dynamic_writes == (VIDEO,)


def test_field_permissions_rejects_invalid_locator_declarations() -> None:
    with pytest.raises(InvalidFieldLocatorError):
        SampleFieldPermissions(reads=[123])  # type: ignore[list-item]

    with pytest.raises(InvalidFieldLocatorError):
        SampleFieldPermissions(writes=["bad-locator"])


def test_field_permissions_rejects_duplicate_and_contradictory_declarations() -> None:
    with pytest.raises(InvalidOperationContractError):
        SampleFieldPermissions(reads=(VIDEO, VIDEO))

    with pytest.raises(InvalidOperationContractError):
        SampleFieldPermissions(writes=(VIDEO,), deletes=(VIDEO,))

    with pytest.raises(InvalidOperationContractError):
        SampleFieldPermissions(writes=(VIDEO,), dynamic_writes=(VIDEO,))


def test_sample_operation_contract_defaults_and_generic_contract_binding() -> None:
    contract = SampleOperationContract()
    generic = contract.contract

    assert contract.field_permissions == SampleFieldPermissions()
    assert generic.input_type is Sample
    assert generic.output_type is Sample
    assert generic.role.value == "generic"
    assert contract.operation_contract is generic


def test_sample_operation_context_coercion_paths() -> None:
    base = SampleOperationContext(
        metadata={"dataset_id": "synth"},
        provenance={"phase": "test"},
    )
    assert base.metadata == {"dataset_id": "synth"}
    assert isinstance(base.metadata, MappingProxyType)
    assert base.operation_name is None

    none_context = SampleOperationContext()
    assert none_context.operation_name is None
    assert none_context.metadata == {}
    assert none_context.provenance == {}

    generic = OperationContext(metadata={"dataset_id": "synth"}, provenance={"source": "unit"})
    sample_context = SampleOperationContext(
        metadata=generic.metadata,
        provenance=generic.provenance,
    )
    assert sample_context.metadata == generic.metadata
    assert sample_context.provenance == generic.provenance


def test_sample_operation_context_infers_operation_name_from_run_context() -> None:
    op = SampleOperation(_identity, name="op-run")
    context = SampleOperationContext(epoch=3)
    result = op(Sample(), context=context)

    assert result.operation_name == "op-run"
    assert op.contract.input_type is Sample


def test_sample_operation_replay_record_is_immutable_mapping() -> None:
    record = SampleReplayRecord(
        run_seed="seed",
        epoch=1,
        operation_name="op",
    )
    mapping = record.to_mapping()

    assert mapping["run_seed"] == "seed"
    assert mapping["operation_name"] == "op"
    assert isinstance(mapping, MappingProxyType)

    with pytest.raises(TypeError):
        mapping["run_seed"] = "bad"


def test_sample_operation_run_wraps_bare_sample_output() -> None:
    sample = Sample({VIDEO: FieldValue(("frame",), schema="video.rgb.v1")})
    operation = SampleOperation(_identity, name="identity")
    context = SampleOperationContext(metadata={"ds": "unit"}, provenance={"source": "sample"})

    result = operation(sample, context=context)

    assert result.operation_name == "identity"
    assert result.output is sample
    assert result.metadata == {"ds": "unit"}
    assert result.provenance == {"source": "sample"}
    assert result.role.value == "generic"


def test_sample_operation_explicit_result_preserves_operation_and_role_and_output_type() -> None:
    sample = Sample()
    operation = SampleOperation(_typed_result, name="op")

    wrong_name = SampleOperation(
        _typed_result,
        name="other",
        contract=SampleOperationContract(),
    )
    with pytest.raises(InvalidOperationResultError):
        wrong_name(sample)

    # explicit result with matching name and role succeeds
    operation = SampleOperation(_typed_result, name="op")
    result = operation(sample, context=SampleOperationContext())

    assert result.operation_name == "op"
    assert result.metadata == {"kernel": "explicit"}
    assert result.provenance == {"path": "test"}


def test_sample_operation_missing_required_read_raises_before_call() -> None:
    calls = []

    def read_kernel(payload: Sample, *, context: SampleOperationContext) -> Sample:
        calls.append("called")
        return payload

    contract = SampleOperationContract(
        field_permissions=SampleFieldPermissions(reads=(VIDEO,)),
    )
    operation = SampleOperation(
        read_kernel,
        name="requires-video",
        contract=contract,
    )
    sample = Sample()

    with pytest.raises(MissingFieldError):
        operation(sample, context=SampleOperationContext())

    assert calls == []


def test_sample_operation_uses_has_preflight_without_materializing_lazy_fields() -> None:
    call_count = []

    def no_payload_kernel(payload: Sample, *, context: SampleOperationContext) -> Sample:
        call_count.append("invoked")
        return payload

    loader = CountingLoader(_load_result())
    field = SampleField(_load_context(), loader)
    sample = Sample({VIDEO: field})
    operation = SampleOperation(
        no_payload_kernel,
        name="no-payload-read",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,)),
        ),
    )

    result = operation(sample)

    assert result.output is sample
    assert call_count == ["invoked"]
    assert loader.calls == 0
    assert field.state is SampleFieldState.UNLOADED


def test_sample_operation_rejects_invalid_input_type_before_call() -> None:
    operation = SampleOperation(
        _identity,
        name="identity",
        contract=SampleOperationContract(),
    )

    with pytest.raises(InvalidOperationInputError):
        operation({"not": "sample"}, context=SampleOperationContext())


def test_sample_operation_invalid_context_type() -> None:
    operation = SampleOperation(_identity, name="identity")

    with pytest.raises(InvalidOperationContextError):
        operation(Sample(), context="bad")  # type: ignore[arg-type]


def test_sample_operation_callable_error_is_wrapped() -> None:
    def failing(payload: Sample, *, context: SampleOperationContext) -> Sample:
        raise ValueError("boom")

    operation = SampleOperation(failing, name="failing")
    with pytest.raises(OperationExecutionError) as exc:
        operation(Sample())

    assert isinstance(exc.value.__cause__, ValueError)
