from __future__ import annotations

import pytest

from rphys.data import (
    Batch,
    FieldValue,
    UncollateFieldSpec,
    UncollatePlan,
    UncollatePolicy,
    uncollate_batch_fields,
)
from rphys.errors import CollatePolicyError


PREDICTION = "predictions/signal.bvp.predicted"
TARGET = "targets/signal.bvp.reference"
DIAGNOSTIC = "diagnostics/custom.stage13.debug"
OUTPUT = "outputs/embedding.features"


def test_uncollate_batch_fields_splits_payloads_and_metadata() -> None:
    batch = Batch(
        {
            PREDICTION: FieldValue(
                [0.11, 0.19],
                schema="signal.bvp.v1",
                metadata={"sample_id": ["s1", "s2"], "model": "fake"},
            ),
            TARGET: FieldValue(
                [0.10, 0.20],
                schema="signal.bvp.v1",
                metadata={"source": "reference"},
            ),
        }
    )
    plan = UncollatePlan(
        2,
        (
            UncollateFieldSpec(PREDICTION),
            UncollateFieldSpec(TARGET),
        ),
    )

    samples = uncollate_batch_fields(batch, plan)

    assert len(samples) == 2
    assert samples[0].require(PREDICTION) == 0.11
    assert samples[1].require(PREDICTION) == 0.19
    assert samples[0].field(PREDICTION).schema == "signal.bvp.v1"
    assert samples[0].field(PREDICTION).metadata["sample_id"] == "s1"
    assert samples[1].field(PREDICTION).metadata["sample_id"] == "s2"
    assert samples[0].field(PREDICTION).metadata["model"] == "fake"
    assert samples[1].field(TARGET).metadata["source"] == "reference"


def test_uncollate_batch_fields_supports_batch_axis_broadcast_drop_and_custom() -> None:
    batch = Batch(
        {
            PREDICTION: FieldValue(_AxisPayload(("a", "b"))),
            OUTPUT: FieldValue({"window": "whole"}),
            DIAGNOSTIC: FieldValue(["debug-a", "debug-b"]),
            TARGET: FieldValue(("x:y", "u:v")),
        }
    )
    plan = UncollatePlan(
        2,
        (
            UncollateFieldSpec(PREDICTION, policy=UncollatePolicy.BATCH_AXIS),
            UncollateFieldSpec(OUTPUT, policy=UncollatePolicy.BROADCAST),
            UncollateFieldSpec(DIAGNOSTIC, policy=UncollatePolicy.DROP),
            UncollateFieldSpec(
                TARGET,
                policy=UncollatePolicy.CUSTOM,
                splitter=lambda value, _count: [item.split(":") for item in value],
            ),
        ),
    )

    samples = uncollate_batch_fields(batch, plan)

    assert samples[0].require(PREDICTION) == "a"
    assert samples[1].require(PREDICTION) == "b"
    assert samples[0].require(OUTPUT) == {"window": "whole"}
    assert samples[1].require(OUTPUT) == {"window": "whole"}
    assert not samples[0].has(DIAGNOSTIC)
    assert samples[0].require(TARGET) == ["x", "y"]
    assert samples[1].require(TARGET) == ["u", "v"]


def test_uncollate_batch_fields_rejects_unplanned_or_misaligned_fields() -> None:
    with pytest.raises(CollatePolicyError):
        uncollate_batch_fields(
            Batch({PREDICTION: FieldValue([0.1, 0.2])}),
            UncollatePlan(2),
        )

    with pytest.raises(CollatePolicyError):
        uncollate_batch_fields(
            Batch({PREDICTION: FieldValue([0.1])}),
            UncollatePlan(2, (PREDICTION,)),
        )

    with pytest.raises(CollatePolicyError):
        uncollate_batch_fields(
            Batch({PREDICTION: FieldValue([0.1, 0.2], metadata={"sample_id": ["s1"]})}),
            UncollatePlan(2, (PREDICTION,)),
        )


def test_uncollate_plan_rejects_ambiguous_specs() -> None:
    with pytest.raises(CollatePolicyError):
        UncollatePlan(0)
    with pytest.raises(CollatePolicyError):
        UncollatePlan(2, (PREDICTION, PREDICTION))
    with pytest.raises(CollatePolicyError):
        UncollateFieldSpec(PREDICTION, policy=UncollatePolicy.CUSTOM)
    with pytest.raises(CollatePolicyError):
        UncollateFieldSpec(PREDICTION, splitter=lambda value, _count: [value])


class _AxisPayload:
    def __init__(self, values: tuple[object, ...]) -> None:
        self._values = values

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, index: int) -> object:
        return self._values[index]
