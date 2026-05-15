"""Integration checks for sample-operation lazy boundaries."""

from __future__ import annotations

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
    SampleFieldPermissions,
    SampleOperation,
    SampleOperationContract,
    SampleOperationContext,
    SampleTransform,
)

VIDEO = FieldLocator.parse("inputs/video.rgb")


def _load_context() -> LoadContext:
    return LoadContext(
        FieldView(
            FieldRef(
                "video.rgb",
                [ResourceRef("file:///unit/video.bin", "file")],
                schema="video.rgb.v1",
            ),
            TemporalIndexSlice(0, 4),
        )
    )


def _load_result(payload: object = (0, 1, 2)) -> CodecLoadResult:
    return CodecLoadResult(
        FieldValue(payload, schema="video.rgb.v1"),
        metadata={"codec": "integration"},
    )


class CountingLoader:
    def __init__(self, result: object) -> None:
        self.result = result
        self.calls = 0

    def __call__(self, context: LoadContext) -> CodecLoadResult:
        self.calls += 1
        return self.result if isinstance(self.result, CodecLoadResult) else self.result  # type: ignore[return-value]


@pytest.mark.parametrize("copy_mode", ["in_place", "shallow", "deep"])
def test_sample_operation_copy_modes_do_not_materialize_lazy_field_payload(copy_mode: str) -> None:
    def no_payload_kernel(payload: Sample, *, context: SampleOperationContext) -> Sample:
        return payload

    loader = CountingLoader(_load_result())
    field = SampleField(_load_context(), loader)
    sample = Sample({VIDEO: field})

    operation = SampleOperation(
        no_payload_kernel,
        name="integration-copy",
        copy_mode=copy_mode,
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,))
        ),
    )

    result = operation(sample)

    assert loader.calls == 0
    assert result.metadata["sample_field_effects"]["copy_mode"] == copy_mode
    assert result.output.field(VIDEO).state is SampleFieldState.UNLOADED
    if copy_mode == "in_place":
        assert result.output is sample
    else:
        assert result.output is not sample


def test_sample_transform_path_keeps_lazy_fields_unloaded_without_payload_access() -> None:
    loader = CountingLoader(_load_result())
    field = SampleField(_load_context(), loader)
    sample = Sample({VIDEO: field})

    transform = SampleTransform(
        lambda payload, *, context: payload,
        name="integration-transform",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(
                reads=(VIDEO,),
                writes=(VIDEO,),
            ),
        ),
    )

    result = transform(sample)

    assert loader.calls == 0
    assert result.output.field(VIDEO).state is SampleFieldState.UNLOADED
    assert result.metadata["sample_field_effects"]["copy_mode"] == "in_place"


def test_sample_operation_payload_access_loads_from_lazy_field() -> None:
    loader = CountingLoader(_load_result(("loaded",)))
    field = SampleField(_load_context(), loader)
    sample = Sample({VIDEO: field})

    def require_kernel(payload: Sample, *, context: SampleOperationContext) -> Sample:
        payload.require(VIDEO)
        return payload

    operation = SampleOperation(
        require_kernel,
        name="integration-load",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,))
        ),
    )

    result = operation(sample)

    assert loader.calls == 1
    assert result.output.field(VIDEO).state is SampleFieldState.LOADED
    assert result.output.require(VIDEO) == ("loaded",)
