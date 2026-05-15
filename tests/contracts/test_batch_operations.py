"""Contract tests for provisional Stage 7 batch operation behavior."""

from __future__ import annotations

from rphys.data import Batch, FieldValue
from rphys.data.locators import FieldLocator
from rphys.ops import (
    BatchEquivalenceReport,
    BatchOperation,
    BatchOperationPipeline,
    BatchParameterScope,
    BatchTransform,
    SampleFieldPermissions,
    BatchOperationContract,
)


VIDEO = FieldLocator.parse("inputs/video.rgb")
PRED = FieldLocator.parse("outputs/signal.bvp.predicted")


def _batch() -> Batch:
    return Batch({VIDEO: FieldValue(["a", "b"], schema="video.rgb.v1", collate_policy="list")})


def test_batch_operation_is_operation_step_and_records_public_equivalence_contract() -> None:
    def identity(batch: Batch, *, context) -> Batch:
        return batch

    report = BatchEquivalenceReport(
        claim="identical",
        reference_operation="sample-identity",
        sample_count=2,
    )
    operation = BatchOperation(identity, name="identity", contract=BatchOperationContract(equivalence=report))

    assert operation.name == "identity"
    assert operation.contract.input_type is Batch
    assert operation.contract.output_type is Batch
    assert operation.batch_contract.equivalence is report
    assert operation(_batch()).metadata["batch_equivalence"]["claim"] == "identical"


def test_batch_transform_public_contract_requires_declared_writes() -> None:
    def write_pred(batch: Batch, *, context) -> Batch:
        batch.set_field(PRED, FieldValue([1, 2], schema="signal.bvp.v1"))
        return batch

    transform = BatchTransform(
        write_pred,
        name="write-pred",
        contract=BatchOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,), writes=(PRED,)),
        ),
    )

    assert transform(_batch()).output.field(PRED).payload == [1, 2]


def test_batch_pipeline_is_specialized_mapping_surface_only() -> None:
    operation = BatchOperation(lambda batch, *, context: batch, name="identity")
    pipeline = BatchOperationPipeline({"diagnostic": operation})

    assert pipeline(_batch()).output.has(VIDEO)
    assert pipeline.operations == (operation,)


def test_batch_parameter_scope_is_explicit_public_vocabulary() -> None:
    assert BatchParameterScope.BATCH.value == "batch"
    assert BatchParameterScope.PER_SAMPLE.value == "per_sample"
