"""Focused tests for Stage 7 sample augmentation behavior."""

from __future__ import annotations

from types import MappingProxyType

import pytest

from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import (
    InvalidOperationContractError,
    InvalidOperationInputError,
    InvalidOperationResultError,
    MissingFieldError,
    OperationExecutionError,
    UndeclaredSampleFieldMutationError,
)
from rphys.ops import (
    OperationContext,
    OperationResult,
    SampleAugmentation,
    SampleAugmentationParams,
    SampleFieldPermissions,
    SampleOperationContract,
    SampleOperationContext,
)

VIDEO = FieldLocator.parse("inputs/video.rgb")
VIEW_A = FieldLocator.parse("inputs/video.rgb.view_a")
VIEW_B = FieldLocator.parse("inputs/video.rgb.view_b")


def test_sample_augmentation_params_coerces_supported_structures() -> None:
    params = SampleAugmentationParams(
        values={
            "enabled": True,
            "gain": 1,
            "scale": 0.25,
            "name": "contrastive",
            "schedule": [0.1, 0.2, (0.3, 0.4)],
            "meta": {"path": ["a", "b"]},
        },
        linked_fields=(
            (
                "inputs/video.rgb.view_a",
                VIEW_B,
            ),
        ),
        view_locators={
            "view_a": "inputs/video.rgb.view_a",
            "view_b": VIEW_B,
        },
    )

    assert isinstance(params.values, MappingProxyType)
    assert params.values["schedule"] == (0.1, 0.2, (0.3, 0.4))
    assert isinstance(params.values["meta"], MappingProxyType)
    assert params.values["meta"]["path"] == ("a", "b")
    assert params.linked_fields == ((VIEW_A, VIEW_B),)
    assert params.view_locators == {"view_a": VIEW_A, "view_b": VIEW_B}
    assert isinstance(params.to_mapping()["values"], MappingProxyType)
    assert params.to_mapping()["linked_fields"] == ((str(VIEW_A), str(VIEW_B)),)


def test_sample_augmentation_params_rejects_invalid_values_and_linked_fields() -> None:
    with pytest.raises(InvalidOperationInputError):
        SampleAugmentationParams(values={"payload": object()})

    with pytest.raises(InvalidOperationInputError):
        SampleAugmentationParams(
            linked_fields=(("inputs/video.rgb.view_a",),),
        )

    with pytest.raises(InvalidOperationInputError):
        SampleAugmentationParams(
            linked_fields=(
                ("inputs/video.rgb.view_a", "inputs/video.rgb.view_b"),
                (VIEW_B, "inputs/video.rgb.view_b"),
            ),
        )


def test_sample_augmentation_params_rejects_duplicate_view_locators() -> None:
    with pytest.raises(InvalidOperationInputError) as exc:
        SampleAugmentationParams(
            view_locators={
                "view_a": VIEW_A,
                "view_b": "inputs/video.rgb.view_a",
            },
        )

    assert exc.value.context["field"] == "view_locators"
    assert exc.value.context["expected"] == "unique view locators"
    assert exc.value.context["actual"] == str(VIEW_A)


def test_sample_augmentation_constructor_requires_callable_params_functions() -> None:
    def sampler(sample: Sample, *, context: SampleOperationContext) -> SampleAugmentationParams:
        return SampleAugmentationParams()

    def applier(
        sample: Sample,
        params: SampleAugmentationParams,
        *,
        context: SampleOperationContext,
    ) -> Sample:
        return sample

    with pytest.raises(InvalidOperationContractError) as sample_exc:
        SampleAugmentation(object(), applier)  # type: ignore[arg-type]
    assert sample_exc.value.context["field"] == "sample_params"

    with pytest.raises(InvalidOperationContractError) as apply_exc:
        SampleAugmentation(sampler, object())  # type: ignore[arg-type]
    assert apply_exc.value.context["field"] == "apply_params"


def test_sample_augmentation_read_preflight_halts_before_sampling() -> None:
    sample_calls: list[str] = []

    def sampler(sample: Sample, *, context: SampleOperationContext) -> SampleAugmentationParams:
        sample_calls.append("sample")
        return SampleAugmentationParams(values={"k": 1})

    def applier(
        sample: Sample,
        params: SampleAugmentationParams,
        *,
        context: SampleOperationContext,
    ) -> Sample:
        return sample

    operation = SampleAugmentation(
        sampler,
        applier,
        name="missing-read",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,)),
        ),
    )
    with pytest.raises(MissingFieldError):
        operation(Sample(), context=SampleOperationContext())

    assert sample_calls == []


def test_sample_augmentation_run_calls_sample_params_and_apply_params_once_and_attaches_replay_metadata() -> None:
    calls: list[str] = []

    def sampler(sample: Sample, *, context: SampleOperationContext) -> SampleAugmentationParams:
        calls.append("sample")
        return SampleAugmentationParams(
            values={"offset": 3},
            linked_fields=((VIEW_A, VIEW_B),),
            view_locators={
                "view_a": "inputs/video.rgb.view_a",
                "view_b": "inputs/video.rgb.view_b",
            },
        )

    def applier(
        sample: Sample,
        params: SampleAugmentationParams,
        *,
        context: SampleOperationContext,
    ) -> Sample:
        calls.append("apply")
        sample.set_field(
            VIEW_A,
            FieldValue((params.values["offset"], "a"), schema="video.rgb.view_a.v1"),
        )
        sample.set_field(
            VIEW_B,
            FieldValue((params.values["offset"], "b"), schema="video.rgb.view_b.v1"),
        )
        return sample

    operation = SampleAugmentation(
        sampler,
        applier,
        name="augment-views",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(
                reads=(VIDEO,),
                writes=(VIEW_A, VIEW_B),
            ),
        ),
    )
    sample = Sample({VIDEO: FieldValue((1, 2), schema="video.rgb.v1")})

    result = operation(sample, context=SampleOperationContext(run_seed="seed"))

    assert calls == ["sample", "apply"]
    assert result.output is sample
    assert result.output.field(VIEW_A).payload == (3, "a")
    assert result.output.field(VIEW_B).payload == (3, "b")
    assert result.metadata["sample_field_effects"]["added"] == (
        str(VIEW_A),
        str(VIEW_B),
    )
    replay = result.metadata["sample_augmentation_replay"]
    assert replay["operation_name"] == "augment-views"
    assert replay["params"]["values"]["offset"] == 3
    assert replay["linked_fields"] == ((str(VIEW_A), str(VIEW_B)),)
    assert replay["view_locators"] == {
        "view_a": str(VIEW_A),
        "view_b": str(VIEW_B),
    }
    assert "sample_augmentation_replay" not in result.metadata["sample_field_effects"]


def test_sample_augmentation_run_rejects_sampler_non_params_output() -> None:
    def sampler(sample: Sample, *, context: SampleOperationContext) -> object:
        return {"bad": 1}

    def applier(sample: Sample, params: object, *, context: SampleOperationContext) -> Sample:
        return sample

    operation = SampleAugmentation(sampler, applier)
    sample = Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")})

    with pytest.raises(InvalidOperationResultError):
        operation(sample)


def test_sample_augmentation_run_rejects_reserved_sample_augmentation_replay_metadata_collision() -> None:
    def sampler(sample: Sample, *, context: SampleOperationContext) -> SampleAugmentationParams:
        return SampleAugmentationParams(values={"seed": 1})

    def applier(
        sample: Sample,
        params: SampleAugmentationParams,
        *,
        context: SampleOperationContext,
    ) -> OperationResult:
        return OperationResult(
            output=sample,
            operation_name="augment",
            metadata={"sample_augmentation_replay": {"preexisting": True}},
        )

    operation = SampleAugmentation(
        sampler,
        applier,
        name="augment",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(),
        ),
    )
    sample = Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")})

    with pytest.raises(InvalidOperationResultError):
        operation(sample)


def test_sample_augmentation_run_rejects_undeclared_view_field_write() -> None:
    def sampler(sample: Sample, *, context: SampleOperationContext) -> SampleAugmentationParams:
        return SampleAugmentationParams(
            view_locators={"view_a": VIEW_A},
        )

    def applier(
        sample: Sample,
        params: SampleAugmentationParams,
        *,
        context: SampleOperationContext,
    ) -> Sample:
        sample.set_field(VIEW_A, FieldValue("view", schema="video.rgb.view_a.v1"))
        return sample

    operation = SampleAugmentation(sampler, applier, name="undeclared-view")
    sample = Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")})

    with pytest.raises(UndeclaredSampleFieldMutationError) as exc:
        operation(sample)

    assert exc.value.context["effect_type"] == "added"
    assert exc.value.context["locator"] == str(VIEW_A)
    assert str(VIEW_A) in exc.value.context["detected_added"]


def test_sample_augmentation_direct_apply_is_deterministic_and_skips_sampler() -> None:
    apply_calls: list[str] = []

    def sampler(sample: Sample, *, context: SampleOperationContext) -> SampleAugmentationParams:
        raise RuntimeError("should not be called")

    def applier(sample: Sample, params: SampleAugmentationParams, *, context: SampleOperationContext) -> Sample:
        apply_calls.append("apply")
        sample.set_field(VIEW_A, FieldValue(params.values["seed"], schema="video.rgb.view_a.v1"))
        return sample

    operation = SampleAugmentation(sampler, applier)
    params = SampleAugmentationParams(values={"seed": 2})
    context = OperationContext()

    sample = Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")})
    first = operation.apply_params(sample, params, context=context)
    second = operation.apply_params(sample, params, context=context)

    assert first is sample is second
    assert sample.field(VIEW_A).payload == 2
    assert apply_calls == ["apply", "apply"]

    with pytest.raises(InvalidOperationInputError):
        operation.apply_params(sample, {"seed": 1}, context=context)


def test_sample_augmentation_run_wraps_sampler_errors() -> None:
    def sampler(sample: Sample, *, context: SampleOperationContext) -> SampleAugmentationParams:
        raise RuntimeError("sampler failed")

    def applier(sample: Sample, params: SampleAugmentationParams, *, context: SampleOperationContext) -> Sample:
        return sample

    operation = SampleAugmentation(sampler, applier)
    sample = Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")})

    with pytest.raises(OperationExecutionError):
        operation(sample)


def test_sample_augmentation_apply_params_wraps_callable_errors_with_phase_context() -> None:
    def sampler(sample: Sample, *, context: SampleOperationContext) -> SampleAugmentationParams:
        return SampleAugmentationParams(values={"seed": 1})

    def applier(
        sample: Sample,
        params: SampleAugmentationParams,
        *,
        context: SampleOperationContext,
    ) -> Sample:
        raise ValueError("apply failed")

    operation = SampleAugmentation(sampler, applier, name="failing-apply")
    sample = Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")})
    params = SampleAugmentationParams(values={"seed": 1})

    with pytest.raises(OperationExecutionError) as exc:
        operation.apply_params(sample, params, context=SampleOperationContext())

    assert exc.value.context["phase"] == "apply_params"
    assert isinstance(exc.value.__cause__, ValueError)
