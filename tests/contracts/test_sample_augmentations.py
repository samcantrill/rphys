"""Contract tests for Stage 7 sample augmentation behavior."""

from __future__ import annotations

from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.ops import (
    SampleAugmentation,
    SampleAugmentationParams,
    SampleOperation,
    SampleFieldPermissions,
    SampleOperationContract,
    SampleOperationContext,
)


VIDEO = FieldLocator.parse("inputs/video.rgb")
VIEW_A = FieldLocator.parse("inputs/video.rgb.view_a")
VIEW_B = FieldLocator.parse("inputs/video.rgb.view_b")


def test_sample_augmentation_is_a_sample_operation_and_pipeline_compatible() -> None:
    operation = SampleAugmentation(
        lambda sample, context: SampleAugmentationParams(values={"v": 1}),
        lambda sample, params, context: sample,
    )

    assert isinstance(operation, SampleAugmentation)
    assert isinstance(operation, SampleOperation)


def test_sample_augmentation_run_is_deterministic_for_fixed_sample_and_context() -> None:
    def sample_params(sample: Sample, *, context: SampleOperationContext) -> SampleAugmentationParams:
        return SampleAugmentationParams(
            values={"seed": 7},
            linked_fields=((VIEW_A, VIEW_B),),
        )

    def apply_params(sample: Sample, params: SampleAugmentationParams, *, context: SampleOperationContext) -> Sample:
        sample.set_field(VIEW_A, FieldValue(("a", params.values["seed"]), schema="video.rgb.view_a.v1"))
        sample.set_field(VIEW_B, FieldValue(("b", params.values["seed"]), schema="video.rgb.view_b.v1"))
        return sample

    operation = SampleAugmentation(
        sample_params,
        apply_params,
        name="deterministic",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(
                reads=(VIDEO,),
                writes=(VIEW_A, VIEW_B),
            ),
        ),
    )
    sample_one = Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")})
    sample_two = Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")})
    context = SampleOperationContext(run_seed="seed")

    first = operation(sample_one, context=context)
    second = operation(sample_two, context=context)

    assert first.output.field(VIEW_A).payload == ("a", 7)
    assert first.output.field(VIEW_B).payload == ("b", 7)
    assert second.output.field(VIEW_A).payload == ("a", 7)
    assert second.metadata["sample_augmentation_replay"] == first.metadata["sample_augmentation_replay"]


def test_sample_augmentation_runtime_replay_records_linked_fields_and_view_locators() -> None:
    def sample_params(sample: Sample, *, context: SampleOperationContext) -> SampleAugmentationParams:
        return SampleAugmentationParams(
            values={"seed": context.run_seed},
            linked_fields=((VIEW_A, VIEW_B),),
            view_locators={"view_a": "inputs/video.rgb.view_a", "view_b": "inputs/video.rgb.view_b"},
        )

    def apply_params(
        sample: Sample,
        params: SampleAugmentationParams,
        *,
        context: SampleOperationContext,
    ) -> Sample:
        sample.set_field(VIEW_A, FieldValue((params.values["seed"], 0), schema="video.rgb.view_a.v1"))
        sample.set_field(VIEW_B, FieldValue((params.values["seed"], 1), schema="video.rgb.view_b.v1"))
        return sample

    operation = SampleAugmentation(
        sample_params,
        apply_params,
        name="replay-record",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(
                reads=(VIDEO,),
                writes=(VIEW_A, VIEW_B),
            ),
        ),
    )
    result = operation(
        Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")}),
        context=SampleOperationContext(run_seed="seed-key"),
    )

    replay = result.metadata["sample_augmentation_replay"]
    assert replay["linked_fields"] == ((str(VIEW_A), str(VIEW_B)),)
    assert replay["view_locators"] == {
        "view_a": str(VIEW_A),
        "view_b": str(VIEW_B),
    }
    assert replay["context"]["run_seed"] == "seed-key"
