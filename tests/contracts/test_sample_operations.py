"""Contract tests for Stage 7 sample operation foundations."""

from __future__ import annotations

from types import MappingProxyType

import pytest

from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.data.sample_fields import SampleField, SampleFieldState
from rphys.io.codecs import CodecLoadResult, LoadContext
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef
from rphys.ops import (
    OperationPipeline,
    OperationResult,
    SampleFieldPermissions,
    SampleOperation,
    SampleOperationContract,
    SampleOperationContext,
    SampleTransform,
    SampleCheck,
    SampleDecision,
    SampleRoute,
)
from rphys.errors import (
    InvalidOperationContractError,
    UndeclaredSampleFieldMutationError,
)

VIDEO = FieldLocator.parse("inputs/video.rgb")


def _identity(payload: Sample, *, context: SampleOperationContext) -> Sample:
    return payload


def _passthrough(payload: Sample, *, context: SampleOperationContext) -> Sample:
    return payload


def _explicit_result(payload: Sample, *, context: SampleOperationContext) -> OperationResult:
    return OperationResult(
        output=payload,
        operation_name="result-op",
        metadata={"from": "kernel"},
        provenance={"phase": "contract"},
    )


class CountingLoader:
    def __init__(self, result: object) -> None:
        self.result = result
        self.calls = 0

    def __call__(self, context: LoadContext) -> CodecLoadResult:
        self.calls += 1
        return self.result if isinstance(self.result, CodecLoadResult) else self.result  # type: ignore[return-value]


def _load_context() -> LoadContext:
    return LoadContext(
        FieldView(
            FieldRef(
                "video.rgb",
                [ResourceRef("file:///records/unit/video.bin", "file")],
                schema="video.rgb.v1",
            ),
            TemporalIndexSlice(0, 4),
        )
    )


def _load_result(payload: object = ("f0", "f1")) -> CodecLoadResult:
    return CodecLoadResult(
        FieldValue(payload, schema="video.rgb.v1"),
        metadata={"codec": "contract"},
    )


def test_sample_operation_is_operation_step_and_pipeline_compatible() -> None:
    operation = SampleOperation(_identity, name="identity")
    assert isinstance(operation, SampleOperation)
    assert operation.sample_contract is operation.sample_contract

    pipeline = OperationPipeline(
        [
            SampleOperation(_identity, name="identity"),
            SampleOperation(_passthrough, name="passthrough"),
        ]
    )

    sample = Sample({VIDEO: FieldValue(("frame",), schema="video.rgb.v1")})
    result = pipeline(sample)

    assert isinstance(result, OperationResult)
    assert result.output is sample
    assert result.operation_name == "passthrough"


def test_sample_operation_preflight_missing_reads_halts_before_materialization() -> None:
    calls: list[str] = []

    def kernel(payload: Sample, *, context: SampleOperationContext) -> Sample:
        calls.append("invoked")
        payload.require(VIDEO)
        return payload

    sample = Sample(
        {VIDEO: FieldValue(("frame",), schema="video.rgb.v1")}
    )
    operation = SampleOperation(
        kernel,
        name="require-and-demand",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(
                reads=(VIDEO,)
            )
        ),
    )
    result = operation(sample)
    assert calls == ["invoked"]
    assert result.output is sample


def test_sample_operation_required_read_preflight_uses_non_payload_access() -> None:
    loader = CountingLoader(_load_result())
    field = SampleField(_load_context(), loader)
    sample = Sample({VIDEO: field})

    operation = SampleOperation(
        _identity,
        name="has-only",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,))
        ),
    )

    result = operation(sample)

    assert result.output is sample
    assert loader.calls == 0
    assert field.state is SampleFieldState.UNLOADED


def test_sample_operation_explicit_result_without_context_merge_is_preserved() -> None:
    operation = SampleOperation(
        _explicit_result,
        name="result-op",
    )
    sample = Sample({VIDEO: FieldValue(("frame",), schema="video.rgb.v1")})

    result = operation(sample, context=SampleOperationContext(metadata={"from": "sample"}))

    assert result.metadata["from"] == "kernel"
    assert result.metadata["sample_field_effects"]["copy_mode"] == "in_place"
    assert result.provenance == {"phase": "contract"}
    assert isinstance(result.side_effect_evidence, MappingProxyType)


def test_sample_transform_requires_output_permissions() -> None:
    with pytest.raises(InvalidOperationContractError):
        SampleTransform(_identity, name="transform-invalid")


def test_sample_transform_and_check_are_sample_operations() -> None:
    transform = SampleTransform(
        _identity,
        name="transform",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(writes=(VIDEO,)),
        ),
    )
    check = SampleCheck(_identity, name="check")

    assert isinstance(transform, SampleOperation)
    assert isinstance(check, SampleOperation)

    sample = Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")})

    assert transform(sample).operation_name == "transform"
    check_result = check(sample)
    assert check_result.operation_name == "check"
    assert check_result.metadata["sample_field_effects"]["copy_mode"] == "in_place"


def test_sample_check_declares_optional_decision_records() -> None:
    def decision_kernel(payload: Sample, *, context: SampleOperationContext) -> OperationResult:
        return OperationResult(
            output=payload,
            operation_name="decision",
            metadata={
                "sample_decision": SampleDecision(
                    label="accept",
                    reason="valid",
                ),
                "sample_route": (
                    SampleRoute(label="continue", reason="ready"),
                ),
            },
        )

    result = SampleCheck(
        decision_kernel,
        name="decision",
    )(Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")}))

    assert isinstance(result.metadata["sample_decision"], SampleDecision)
    assert isinstance(result.metadata["sample_route"], tuple)
    assert result.metadata["sample_route"][0].label == "continue"


def test_sample_transform_fails_with_undeclared_mutation() -> None:
    def add_flag(payload: Sample, *, context: SampleOperationContext) -> Sample:
        payload.set_field("outputs/quality.flag", FieldValue(1, schema="quality.flag.v1"))
        return payload

    operation = SampleTransform(
        add_flag,
        name="add-flag",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(
                writes=(VIDEO,),
            )
        ),
    )

    with pytest.raises(UndeclaredSampleFieldMutationError) as exc:
        operation(Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")}))

    assert exc.value.context["effect_type"] == "added"
