from __future__ import annotations

from dataclasses import dataclass

from rphys.data import FieldValue
from rphys.metrics import (
    GroupBySpec,
    MetricContext,
    MetricContract,
    MetricObservation,
    MetricObservationCollection,
    MetricResult,
    MetricValue,
)


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


class SyntheticMetric:
    contract = MetricContract(
        "synthetic-metric",
        level="window",
        writes=("metrics/custom.stage11.synthetic_metric",),
    )

    def __call__(self, context: MetricContext) -> MetricResult:
        observation = MetricObservation(
            "synthetic-metric",
            MetricValue(FakeScalar(0.3), backend="fake", unit="bpm"),
            level=context.contract.level,
            groups={"subject_id": "s1", "record_id": "r1", "split": "test"},
        )
        return MetricResult(
            MetricObservationCollection((observation,)),
            fields={"metrics/custom.stage11.synthetic_metric": FieldValue(FakeScalar(0.3))},
            contract=context.contract,
        )


def test_fake_metric_returns_detached_observation_collection_with_grouping_metadata() -> None:
    result = SyntheticMetric()(MetricContext(SyntheticMetric.contract))
    grouped = result.observations.grouped(GroupBySpec(("subject_id", "split")))

    assert result.observations[0].value.detached is True
    assert result.observations[0].value.differentiable is False
    assert tuple(grouped) == (("s1", "test"),)
    assert list(grouped[("s1", "test")]) == [result.observations[0]]
    assert tuple(str(locator) for locator in result.fields) == (
        "metrics/custom.stage11.synthetic_metric",
    )
