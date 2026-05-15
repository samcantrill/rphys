from __future__ import annotations

import inspect
import pytest

from rphys.errors import InvalidOperationPipelineError
from rphys.data import Sample
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.ops import (
    Operation,
    OperationContract,
    OperationContext,
    OperationPipeline,
    SampleFieldPermissions,
    SampleOperationContract,
    SampleOperationPipeline,
    SampleTransform,
)


VIDEO = FieldLocator.parse("inputs/video.rgb")
VIEW_A = FieldLocator.parse("inputs/video.rgb.view_a")


def plus_one(value: int, *, context: OperationContext) -> int:
    return value + 1


def times_two(value: int, *, context: OperationContext) -> int:
    return value * 2


def write_view(sample: Sample, *, context) -> Sample:
    sample.set_field(VIEW_A, FieldValue("view", schema="video.rgb.view_a.v1"))
    return sample


def sample_step(name: str = "write-view") -> SampleTransform:
    return SampleTransform(
        write_view,
        name=name,
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(
                reads=(VIDEO,),
                writes=(VIEW_A,),
            ),
        ),
    )


def test_operation_pipeline_public_api_is_sequence_only() -> None:
    ctor = inspect.signature(OperationPipeline.__init__)
    params = list(ctor.parameters.values())[1:]

    assert len(params) == 1
    assert params[0].name == "operations"
    assert params[0].annotation == "Sequence[OperationStep]"


def test_operation_pipeline_exposes_only_operations_tuple() -> None:
    pipeline = OperationPipeline([
        Operation(plus_one),
        Operation(times_two, contract=OperationContract(input_type=int)),
    ])

    assert isinstance(pipeline.operations, tuple)
    assert len(pipeline.operations) == 2


def test_pipeline_contract_checks_sequential_type_compatibility() -> None:
    first = Operation(plus_one, contract=OperationContract(output_type=int))
    second = Operation(times_two, contract=OperationContract(input_type=(int, float)))
    contract_ok = OperationPipeline([first, second])

    assert isinstance(contract_ok.operations, tuple)

    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline(
            [
                Operation(plus_one, contract=OperationContract(output_type=object)),
                Operation(times_two, contract=OperationContract(input_type=int)),
            ]
        )


def test_pipeline_does_not_expose_stable_step_or_pipeline_name_apis() -> None:
    assert not hasattr(OperationPipeline, "steps")
    assert not hasattr(OperationPipeline, "name")
    assert not hasattr(OperationPipeline, "run_raw")
    assert not hasattr(OperationPipeline, "pipeline_name")


def test_sample_operation_pipeline_is_specialized_mapping_surface_only() -> None:
    step = sample_step()
    pipeline = SampleOperationPipeline({"diagnostic-step": step})
    sample = Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")})

    result = pipeline(sample)

    assert pipeline.operations == (step,)
    assert result.operation_name == "write-view"
    assert result.output.field(VIEW_A).payload == "view"

    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline({"diagnostic-step": Operation(plus_one)})


def test_sample_operation_pipeline_does_not_expose_step_identity_api() -> None:
    assert not hasattr(SampleOperationPipeline, "steps")
    assert not hasattr(SampleOperationPipeline, "step_names")
    assert not hasattr(SampleOperationPipeline, "name")
    assert not hasattr(SampleOperationPipeline, "pipeline_name")
