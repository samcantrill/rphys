from __future__ import annotations

from collections.abc import Mapping

import pytest

from rphys.datasources.prepared import (
    BatchCostMetadata,
    BatchSamplerPlan,
    BatchShapePolicy,
)
from rphys.errors import FieldTypeError
from tests.support.lazy_sample_builder_fixtures import BVP, VIDEO


def test_batch_planning_records_round_trip_as_descriptive_evidence() -> None:
    first_cost = BatchCostMetadata(
        position=0,
        cost=1.25,
        weight=0.5,
        length=32,
        group="subject-001",
        metadata={"split": "train"},
    )
    second_cost = BatchCostMetadata(position=1, cost=2, length=48, group="subject-001")
    policy = BatchShapePolicy(
        "fixed-8",
        mode="fixed",
        batch_size=8,
        drop_last=True,
        pad=False,
        field_locators=[VIDEO, BVP],
        metadata={"purpose": "unit"},
    )
    plan = BatchSamplerPlan(
        "sampler-0",
        shape_policy=policy,
        ordering="cost_aware",
        cost_metadata=[first_cost, second_cost],
        seed={"epoch": 1},
        metadata={"scope": "unit"},
    )

    loaded = BatchSamplerPlan.from_dict(plan.to_dict())

    assert loaded.to_dict() == plan.to_dict()
    assert loaded.fingerprint == plan.fingerprint
    assert loaded.shape_policy.field_locators == (VIDEO, BVP)
    assert loaded.cost_metadata[0].cost == 1.25
    assert isinstance(loaded.seed, Mapping)
    assert loaded.seed["epoch"] == 1


def test_batch_planning_fingerprints_change_with_cost_shape_and_ordering() -> None:
    baseline = _sampler_plan()

    assert baseline.fingerprint != _sampler_plan(cost=2.0).fingerprint
    assert baseline.fingerprint != _sampler_plan(batch_size=16).fingerprint
    assert baseline.fingerprint != _sampler_plan(ordering="shuffle").fingerprint


def test_batch_cost_metadata_rejects_invalid_cost_evidence() -> None:
    with pytest.raises(FieldTypeError, match="non-negative"):
        BatchCostMetadata(position=0, cost=-1)
    with pytest.raises(FieldTypeError, match="finite"):
        BatchCostMetadata(position=0, cost=float("nan"))
    with pytest.raises(FieldTypeError):
        BatchCostMetadata(position=True, cost=1.0)  # type: ignore[arg-type]
    with pytest.raises(FieldTypeError):
        BatchCostMetadata(position=0, cost=1.0, metadata={"bad": object()})


def test_batch_shape_policy_rejects_invalid_shape_evidence() -> None:
    with pytest.raises(FieldTypeError, match="positive"):
        BatchShapePolicy("zero", batch_size=0)
    with pytest.raises(FieldTypeError, match="unsupported"):
        BatchShapePolicy("bad-mode", mode="stack", batch_size=8)
    with pytest.raises(FieldTypeError, match="bool"):
        BatchShapePolicy("bad-bool", batch_size=8, drop_last=1)  # type: ignore[arg-type]
    with pytest.raises(FieldTypeError, match="must not be empty"):
        BatchShapePolicy("bad-fields", batch_size=8, field_locators=[])


def test_batch_sampler_plan_rejects_runtime_like_or_ambiguous_evidence() -> None:
    policy = BatchShapePolicy("fixed-8", batch_size=8)
    first = BatchCostMetadata(position=0, cost=1.0)
    duplicate = BatchCostMetadata(position=0, cost=2.0)

    with pytest.raises(FieldTypeError, match="unsupported"):
        BatchSamplerPlan("bad-order", shape_policy=policy, ordering="weighted")
    with pytest.raises(FieldTypeError, match="unique"):
        BatchSamplerPlan(
            "duplicate-cost",
            shape_policy=policy,
            cost_metadata=[first, duplicate],
        )
    with pytest.raises(FieldTypeError):
        BatchSamplerPlan("bad-policy", shape_policy=object())  # type: ignore[arg-type]


def _sampler_plan(
    *,
    cost: float = 1.0,
    batch_size: int = 8,
    ordering: str = "cost_aware",
) -> BatchSamplerPlan:
    return BatchSamplerPlan(
        "sampler-0",
        shape_policy=BatchShapePolicy(
            "fixed",
            batch_size=batch_size,
            field_locators=[VIDEO],
        ),
        ordering=ordering,
        cost_metadata=[BatchCostMetadata(position=0, cost=cost)],
        seed=123,
    )
