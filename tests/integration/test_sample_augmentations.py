"""Integration checks for sample augmentation lazy-field view writes."""

from __future__ import annotations

from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.data.sample_fields import SampleField, SampleFieldState
from rphys.io.codecs import CodecLoadResult, LoadContext
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef
from rphys.ops import (
    SampleAugmentation,
    SampleAugmentationParams,
    SampleFieldPermissions,
    SampleOperationContract,
    SampleOperationContext,
)

VIDEO = FieldLocator.parse("inputs/video.rgb")
VIEW_A = FieldLocator.parse("inputs/video.rgb.view_a")
VIEW_B = FieldLocator.parse("inputs/video.rgb.view_b")


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


def test_sample_augmentation_writes_view_fields_on_required_lazy_sample() -> None:
    def sample_params(sample, *, context: SampleOperationContext) -> SampleAugmentationParams:
        return SampleAugmentationParams(
            values={"seed": 42},
            linked_fields=((VIEW_A, VIEW_B),),
            view_locators={"view_a": "inputs/video.rgb.view_a", "view_b": "inputs/video.rgb.view_b"},
        )

    def apply_params(
        sample: Sample,
        params: SampleAugmentationParams,
        *,
        context: SampleOperationContext,
    ) -> Sample:
        sample.set_field(
            VIEW_A,
            FieldValue((params.values["seed"], "left"), schema="video.rgb.view_a.v1"),
        )
        sample.set_field(
            VIEW_B,
            FieldValue((params.values["seed"], "right"), schema="video.rgb.view_b.v1"),
        )
        return sample

    loader = CountingLoader(_load_result())
    field = SampleField(_load_context(), loader)
    sample = Sample({VIDEO: field})
    operation = SampleAugmentation(
        sample_params,
        apply_params,
        name="wide-window-views",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(
                reads=(VIDEO,),
                writes=(VIEW_A, VIEW_B),
            ),
        ),
    )

    result = operation(sample)

    assert loader.calls == 0
    assert result.output.field(VIDEO).state is SampleFieldState.UNLOADED
    assert result.output.field(VIEW_A).payload == (42, "left")
    assert result.output.field(VIEW_B).payload == (42, "right")
    assert result.metadata["sample_augmentation_replay"]["operation_name"] == "wide-window-views"
