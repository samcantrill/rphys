from __future__ import annotations

import pytest

from rphys.data import (
    Batch,
    BatchCollater,
    CollatePolicy,
    FieldValue,
    Sample,
    uncollate_batch,
)
from rphys.data.locators import FieldLocator
from rphys.errors import CollatePolicyError


VIDEO = FieldLocator.parse("inputs/video.rgb")
BVP = FieldLocator.parse("targets/signal.bvp.reference")


def test_batch_collater_contract_returns_field_locator_keyed_batch() -> None:
    collater = BatchCollater()

    batch = collater(
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

    assert isinstance(batch, Batch)
    assert [locator for locator, _ in batch.field_items()] == [VIDEO, BVP]
    assert batch.field(VIDEO).collate_policy is CollatePolicy.LIST
    assert batch.require(VIDEO) == ["frame-0", "frame-1"]
    assert batch.require(BVP) == [[0.1], [0.2]]
    samples = uncollate_batch(batch)
    assert isinstance(samples, tuple)
    assert [locator for locator, _ in samples[0].field_items()] == [VIDEO, BVP]
    assert samples[0].require(VIDEO) == "frame-0"
    assert samples[1].require(BVP) == [0.2]


def test_batch_collater_contract_does_not_format_model_tuples_or_dicts() -> None:
    batch = BatchCollater()(
        [
            Sample({VIDEO: FieldValue("frame-0", schema="video.rgb.v1", collate_policy="list")}),
            Sample({VIDEO: FieldValue("frame-1", schema="video.rgb.v1", collate_policy="list")}),
        ]
    )

    assert not isinstance(batch, tuple)
    assert not isinstance(batch, dict)


def test_batch_collater_contract_preserves_list_only_fail_loud_policy() -> None:
    with pytest.raises(CollatePolicyError):
        BatchCollater()(
            [
                Sample({VIDEO: FieldValue("frame-0", schema="video.rgb.v1")}),
                Sample({VIDEO: FieldValue("frame-1", schema="video.rgb.v1")}),
            ]
        )
