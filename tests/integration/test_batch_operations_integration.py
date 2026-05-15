"""Integration checks for provisional batch operations over LIST-collated fields."""

from __future__ import annotations

from rphys.data import Batch, FieldValue, Sample, collate_samples
from rphys.data.locators import FieldLocator
from rphys.ops import (
    BatchEquivalenceReport,
    BatchOperationContract,
    BatchTransform,
    SampleFieldPermissions,
)


VIDEO = FieldLocator.parse("inputs/video.rgb")
BVP = FieldLocator.parse("targets/signal.bvp.reference")
PRED = FieldLocator.parse("outputs/signal.bvp.predicted")


def _collated_batch() -> Batch:
    return collate_samples(
        [
            Sample(
                {
                    VIDEO: FieldValue("frame-0", schema="video.rgb.v1", collate_policy="list"),
                    BVP: FieldValue([0.1], schema="signal.bvp.v1", collate_policy="list"),
                }
            ),
            Sample(
                {
                    VIDEO: FieldValue("frame-1", schema="video.rgb.v1", collate_policy="list"),
                    BVP: FieldValue([0.2], schema="signal.bvp.v1", collate_policy="list"),
                }
            ),
        ]
    )


def test_batch_transform_reports_identical_equivalence_over_list_collated_fields() -> None:
    def copy_reference(batch: Batch, *, context) -> Batch:
        batch.set_field(
            PRED,
            FieldValue(
                list(batch.require(BVP)),
                schema="signal.bvp.v1",
                collate_policy="list",
            ),
        )
        return batch

    operation = BatchTransform(
        copy_reference,
        name="copy-reference",
        contract=BatchOperationContract(
            field_permissions=SampleFieldPermissions(reads=(BVP,), writes=(PRED,)),
            equivalence=BatchEquivalenceReport(
                claim="identical",
                reference_operation="sample-copy-reference",
                sample_count=2,
            ),
        ),
    )

    result = operation(_collated_batch())

    assert result.output.require(PRED) == [[0.1], [0.2]]
    assert result.metadata["batch_equivalence"]["claim"] == "identical"
    assert result.metadata["batch_equivalence"]["reference_operation"] == "sample-copy-reference"
    assert result.metadata["batch_field_effects"]["added"] == (str(PRED),)


def test_batch_transform_reports_approximate_equivalence_diagnostics() -> None:
    def approximate(batch: Batch, *, context) -> Batch:
        batch.set_field(PRED, FieldValue([0.1, 0.21], schema="signal.bvp.v1", collate_policy="list"))
        return batch

    operation = BatchTransform(
        approximate,
        name="approximate-reference",
        contract=BatchOperationContract(
            field_permissions=SampleFieldPermissions(reads=(BVP,), writes=(PRED,)),
            equivalence=BatchEquivalenceReport(
                claim="approximate",
                reference_operation="sample-copy-reference",
                diagnostics=("second sample differs by 0.01",),
                tolerances={"max_abs_error": 0.01},
                sample_count=2,
            ),
        ),
    )

    result = operation(_collated_batch())

    assert result.metadata["batch_equivalence"]["claim"] == "approximate"
    assert result.metadata["batch_equivalence"]["diagnostics"] == ("second sample differs by 0.01",)
    assert result.metadata["batch_equivalence"]["tolerances"]["max_abs_error"] == 0.01
