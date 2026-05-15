"""Focused tests for provisional Stage 7 batch operations."""

from __future__ import annotations

from collections import OrderedDict
from types import MappingProxyType

import pytest

from rphys.data import Batch, FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import (
    InvalidOperationContractError,
    InvalidOperationInputError,
    InvalidOperationPipelineError,
    InvalidOperationResultError,
    MissingFieldError,
    OperationPipelineExecutionError,
    UndeclaredSampleFieldMutationError,
)
from rphys.ops import (
    BatchAugmentation,
    BatchAugmentationParams,
    BatchEquivalenceClaim,
    BatchEquivalenceReport,
    BatchOperation,
    BatchOperationContext,
    BatchOperationContract,
    BatchOperationPipeline,
    BatchParameterScope,
    BatchTransform,
    Operation,
    OperationContext,
    OperationPipeline,
    SampleFieldPermissions,
)


VIDEO = FieldLocator.parse("inputs/video.rgb")
BVP = FieldLocator.parse("targets/signal.bvp.reference")
PRED = FieldLocator.parse("outputs/signal.bvp.predicted")
VIEW = FieldLocator.parse("inputs/video.rgb.view")


def _batch() -> Batch:
    return Batch(
        {
            VIDEO: FieldValue(["frame-0", "frame-1"], schema="video.rgb.v1", collate_policy="list"),
            BVP: FieldValue([[0.1], [0.2]], schema="signal.bvp.v1", collate_policy="list"),
        }
    )


def test_batch_context_and_contract_are_inspectable_and_dependency_light() -> None:
    context = BatchOperationContext(
        metadata={"dataset": "synthetic"},
        run_seed="seed",
        batch_size=2,
        dtype="float32",
        device="cpu",
        parameter_scope="batch",
    )
    contract = BatchOperationContract(
        field_permissions=SampleFieldPermissions(reads=(VIDEO,), writes=(PRED,)),
        parameter_scope=BatchParameterScope.BATCH,
        dtype="float32",
        device="cpu",
        equivalence=BatchEquivalenceReport(
            claim=BatchEquivalenceClaim.IDENTICAL,
            reference_operation="sample-predict",
            sample_count=2,
        ),
    )

    assert isinstance(context.metadata, MappingProxyType)
    assert context.to_mapping()["parameter_scope"] == "batch"
    assert contract.contract.input_type is Batch
    assert contract.contract.output_type is Batch
    assert contract.field_permissions.reads == (VIDEO,)
    assert contract.equivalence.to_mapping()["claim"] == "identical"


def test_batch_equivalence_report_requires_diagnostics_for_non_replacement_claims() -> None:
    with pytest.raises(InvalidOperationResultError):
        BatchEquivalenceReport(claim="approximate")
    with pytest.raises(InvalidOperationResultError):
        BatchEquivalenceReport(claim="unsupported")
    with pytest.raises(InvalidOperationResultError):
        BatchEquivalenceReport(claim="diagnostic", tolerances={"payload": object()})

    report = BatchEquivalenceReport(
        claim="approximate",
        diagnostics=("max_abs_error <= 0.01",),
        tolerances={"max_abs_error": 0.01},
    )

    assert report.claim is BatchEquivalenceClaim.APPROXIMATE
    assert report.to_mapping()["tolerances"]["max_abs_error"] == 0.01


def test_batch_augmentation_params_validate_scope_and_lightweight_values() -> None:
    params = BatchAugmentationParams(
        scope="per_sample",
        values={"window": [0, 4]},
        per_sample=({"offset": 1}, {"offset": 2}),
    )

    assert params.scope is BatchParameterScope.PER_SAMPLE
    assert params.values["window"] == (0, 4)
    assert params.to_mapping()["per_sample"][1]["offset"] == 2

    with pytest.raises(InvalidOperationInputError):
        BatchAugmentationParams(scope="per_sample")
    with pytest.raises(InvalidOperationInputError):
        BatchAugmentationParams(scope="batch", per_sample=({"offset": 1},))
    with pytest.raises(InvalidOperationInputError):
        BatchAugmentationParams(values={"payload": object()})


def test_batch_operation_declared_write_records_field_effects_and_equivalence() -> None:
    def predict(batch: Batch, *, context: BatchOperationContext) -> Batch:
        batch.set_field(PRED, FieldValue([0.1, 0.2], schema="signal.bvp.v1", collate_policy="list"))
        return batch

    operation = BatchOperation(
        predict,
        name="batch-predict",
        contract=BatchOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,), writes=(PRED,)),
            equivalence=BatchEquivalenceReport(
                claim="identical",
                reference_operation="sample-predict",
                sample_count=2,
            ),
        ),
    )
    batch = _batch()

    result = operation(batch)

    assert result.output is batch
    assert result.output.require(PRED) == [0.1, 0.2]
    assert result.metadata["batch_field_effects"]["added"] == (str(PRED),)
    assert result.metadata["batch_equivalence"]["claim"] == "identical"
    assert result.metadata["batch_equivalence"]["sample_count"] == 2


def test_batch_operation_rejects_missing_reads_and_undeclared_mutation() -> None:
    def mutate(batch: Batch, *, context: BatchOperationContext) -> Batch:
        batch.set_field(PRED, FieldValue([0.1, 0.2], schema="signal.bvp.v1"))
        return batch

    operation = BatchOperation(
        mutate,
        name="undeclared",
        contract=BatchOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIEW,), writes=(BVP,)),
        ),
    )
    with pytest.raises(MissingFieldError):
        operation(_batch())

    operation = BatchOperation(
        mutate,
        name="undeclared",
        contract=BatchOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,), writes=(BVP,)),
        ),
    )
    with pytest.raises(UndeclaredSampleFieldMutationError):
        operation(_batch())


def test_batch_transform_requires_declared_outputs() -> None:
    def identity(batch: Batch, *, context: BatchOperationContext) -> Batch:
        return batch

    with pytest.raises(InvalidOperationContractError):
        BatchTransform(identity)


def test_batch_augmentation_splits_sampling_from_application_and_records_replay() -> None:
    calls: list[str] = []

    def sample_params(batch: Batch, *, context: BatchOperationContext) -> BatchAugmentationParams:
        calls.append("sample")
        return BatchAugmentationParams(scope="batch", values={"suffix": "view"})

    def apply_params(
        batch: Batch,
        params: BatchAugmentationParams,
        *,
        context: BatchOperationContext,
    ) -> Batch:
        calls.append("apply")
        batch.set_field(VIEW, FieldValue(params.values["suffix"], schema="video.rgb.view.v1"))
        return batch

    operation = BatchAugmentation(
        sample_params,
        apply_params,
        name="batch-view",
        contract=BatchOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,), writes=(VIEW,)),
        ),
    )

    result = operation(_batch(), context=BatchOperationContext(run_seed="seed"))

    assert calls == ["sample", "apply"]
    assert result.output.require(VIEW) == "view"
    assert result.metadata["batch_augmentation_replay"]["params"]["values"]["suffix"] == "view"
    assert result.metadata["batch_augmentation_replay"]["context"]["run_seed"] == "seed"


def test_batch_augmentation_rejects_sampler_field_mutation_before_apply() -> None:
    def sample_params(batch: Batch, *, context: BatchOperationContext) -> BatchAugmentationParams:
        batch.set_field(VIEW, FieldValue("bad", schema="video.rgb.view.v1"))
        return BatchAugmentationParams(scope="batch", values={"suffix": "view"})

    def apply_params(batch: Batch, params: BatchAugmentationParams, *, context: BatchOperationContext) -> Batch:
        return batch

    operation = BatchAugmentation(
        sample_params,
        apply_params,
        name="bad-sampler",
        contract=BatchOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,), writes=(VIEW,)),
        ),
    )

    with pytest.raises(InvalidOperationResultError) as exc:
        operation(_batch())

    assert exc.value.context["field"] == "sample_params"
    assert exc.value.context["expected"] == "no batch field mutations"


def test_batch_augmentation_enforces_declared_parameter_scope() -> None:
    apply_calls: list[str] = []

    def sample_params(batch: Batch, *, context: BatchOperationContext) -> BatchAugmentationParams:
        return BatchAugmentationParams(scope="per_sample", per_sample=({"offset": 1}, {"offset": 2}))

    def apply_params(batch: Batch, params: BatchAugmentationParams, *, context: BatchOperationContext) -> Batch:
        apply_calls.append("apply")
        return batch

    operation = BatchAugmentation(
        sample_params,
        apply_params,
        name="scope-mismatch",
        contract=BatchOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,), writes=(VIEW,)),
            parameter_scope="batch",
        ),
    )

    with pytest.raises(InvalidOperationResultError) as exc:
        operation(_batch())

    assert exc.value.context["field"] == "sample_params.scope"
    assert exc.value.context["expected"] == "batch"
    assert exc.value.context["actual"] == "per_sample"
    assert apply_calls == []


def test_batch_augmentation_context_parameter_scope_is_enforced_when_contract_scope_is_unset() -> None:
    def sample_params(batch: Batch, *, context: BatchOperationContext) -> BatchAugmentationParams:
        return BatchAugmentationParams(scope="batch", values={"gain": 1})

    def apply_params(batch: Batch, params: BatchAugmentationParams, *, context: BatchOperationContext) -> Batch:
        return batch

    operation = BatchAugmentation(
        sample_params,
        apply_params,
        name="context-scope-mismatch",
        contract=BatchOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,), writes=(VIEW,)),
        ),
    )

    with pytest.raises(InvalidOperationResultError) as exc:
        operation(_batch(), context=BatchOperationContext(parameter_scope="per_sample"))

    assert exc.value.context["expected"] == "per_sample"
    assert exc.value.context["actual"] == "batch"


def test_batch_pipeline_runs_ordered_mapping_and_wraps_step_diagnostics() -> None:
    def write_pred(batch: Batch, *, context: BatchOperationContext) -> Batch:
        batch.set_field(PRED, FieldValue([1, 2], schema="signal.bvp.v1"))
        return batch

    def needs_view(batch: Batch, *, context: BatchOperationContext) -> Batch:
        return batch

    first = BatchTransform(
        write_pred,
        name="write-pred",
        contract=BatchOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,), writes=(PRED,)),
        ),
    )
    second = BatchTransform(
        needs_view,
        name="needs-view",
        contract=BatchOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIEW,), writes=(PRED,)),
        ),
    )
    pipeline = BatchOperationPipeline(OrderedDict([("predict", first), ("view-step", second)]))

    with pytest.raises(OperationPipelineExecutionError) as exc:
        pipeline(_batch())

    assert pipeline.operations == (first, second)
    assert exc.value.context["step_index"] == 1
    assert exc.value.context["operation_name"] == "needs-view"
    assert exc.value.context["step_name"] == "view-step"
    assert exc.value.context["cause_type"] == "MissingFieldError"


def test_batch_pipeline_rejects_generic_operations_and_generic_pipeline_still_rejects_mapping() -> None:
    batch_operation = BatchOperation(lambda batch, *, context: batch, name="identity")

    with pytest.raises(InvalidOperationPipelineError):
        BatchOperationPipeline([Operation(lambda value, *, context: value)])
    with pytest.raises(InvalidOperationPipelineError):
        BatchOperationPipeline([("identity", batch_operation)])
    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline({"identity": Operation(lambda value, *, context: value)})
