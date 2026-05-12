from __future__ import annotations

from rphys.data import Batch, CollatePolicy, FieldValue, Sample, collate_samples
from rphys.data.locators import FieldLocator


VIDEO = FieldLocator.parse("inputs/video.rgb")
BVP = FieldLocator.parse("targets/signal.bvp.reference")


def test_sample_to_batch_list_collation_integration() -> None:
    samples = [
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

    batch = collate_samples(samples)

    assert isinstance(batch, Batch)
    assert batch.field(VIDEO).collate_policy is CollatePolicy.LIST
    assert batch.require(VIDEO) == ["frame-0", "frame-1"]
    assert batch.require(BVP) == [[0.1], [0.2]]
