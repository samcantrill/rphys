"""Runtime-boundary contracts for generic operations.

These tests prove that Stage 6 :class:`Operation` treats loaded runtime containers
as ordinary payloads and that lazy loading stays demand-driven by container APIs.
"""

from __future__ import annotations

from rphys.data.containers import Batch, Sample
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.data.metadata import MetadataKey
from rphys.data.sample_fields import SampleField, SampleFieldState
from rphys.io.codecs import CodecLoadResult, LoadContext
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef
from rphys.ops import (
    Operation,
    OperationContract,
    OperationContext,
    OperationResult,
)

VIDEO = FieldLocator.parse("inputs/video.rgb")


def _identity_sample(payload: Sample, *, context: OperationContext) -> Sample:
    return payload


def _identity_batch(payload: Batch, *, context: OperationContext) -> Batch:
    return payload


def _inspect_sample_field(payload: Sample, *, context: OperationContext) -> Sample:
    payload.field(VIDEO)
    return payload


def _demand_sample_payload(payload: Sample, *, context: OperationContext) -> Sample:
    assert payload.require(VIDEO, expected_type=tuple) == ("f0", "f1")
    return payload


def test_operation_treats_loaded_sample_and_batch_as_ordinary_payload() -> None:
    sample = Sample(
        {
            VIDEO: FieldValue((0.2, 0.4), schema="signal.bvp.v1"),
        }
    )
    batch = Batch(
        {
            VIDEO: FieldValue((("a",), ("b",)), schema="signal.bvp.v1"),
        }
    )

    sample_result = Operation(
        _identity_sample,
        name="identity-sample",
        contract=OperationContract(input_type=Sample, output_type=Sample),
    )(sample)
    batch_result = Operation(
        _identity_batch,
        name="identity-batch",
        contract=OperationContract(input_type=Batch, output_type=Batch),
    )(batch)

    assert isinstance(sample_result, OperationResult)
    assert sample_result.operation_name == "identity-sample"
    assert sample_result.output is sample
    assert isinstance(batch_result, OperationResult)
    assert batch_result.operation_name == "identity-batch"
    assert batch_result.output is batch


class CountingLoader:
    def __init__(self, result: CodecLoadResult | BaseException | object) -> None:
        self.result = result
        self.calls = 0
        self.contexts: list[LoadContext] = []

    def __call__(self, context: LoadContext) -> CodecLoadResult:
        self.calls += 1
        self.contexts.append(context)
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result  # type: ignore[return-value]


def _load_context(
    key: str = "video.rgb",
    *,
    schema: str = "video.rgb.v1",
) -> LoadContext:
    return LoadContext(
        FieldView(
            FieldRef(
                key,
                [ResourceRef("file:///records/r001/video.bin", "file")],
                schema=schema,
                metadata={"source_id": "camera-front"},
            ),
            TemporalIndexSlice(0, 2),
        )
    )


def _load_result(
    payload: object = ("f0", "f1"),
    *,
    schema: str = "video.rgb.v1",
) -> CodecLoadResult:
    return CodecLoadResult(
        FieldValue(
            payload,
            schema=schema,
            metadata={"loaded_by": "contract"},
        ),
        metadata={"codec": "contract"},
    )


def _sample_field(
    loader: CountingLoader | None = None,
) -> tuple[SampleField, CountingLoader]:
    actual_loader = loader or CountingLoader(_load_result())
    return (
        SampleField(
            _load_context(),
            actual_loader,
        ),
        actual_loader,
    )


def test_lazy_samplefield_not_materialized_by_plain_field_access_within_operation() -> None:
    field, loader = _sample_field()
    sample = Sample({VIDEO: field})

    result = Operation(
        _inspect_sample_field,
        name="inspect-field",
        contract=OperationContract(input_type=Sample, output_type=Sample),
    )(sample)

    assert result.output is sample
    assert loader.calls == 0
    assert sample.field(VIDEO) is field
    assert field.state is SampleFieldState.UNLOADED


def test_lazy_samplefield_is_materialized_only_when_payload_is_demanded_in_kernel() -> None:
    field, loader = _sample_field()
    sample = Sample({VIDEO: field})

    result = Operation(
        _demand_sample_payload,
        name="require-payload",
        contract=OperationContract(input_type=Sample, output_type=Sample),
    )(sample)

    assert result.output is sample
    assert loader.calls == 1
    assert field.state is SampleFieldState.LOADED
    assert sample.field(VIDEO).metadata[MetadataKey("loaded_by")] == "contract"
    assert loader.contexts == [field.load_context]
