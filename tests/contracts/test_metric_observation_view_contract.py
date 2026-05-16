from __future__ import annotations

from dataclasses import dataclass

from rphys.metrics import (
    MetricContext,
    MetricContract,
    MetricObservation,
    MetricObservationCollection,
    MetricObservationView,
    MetricObservationViewPlan,
    MetricResult,
    MetricValue,
    PlannedMetricObservationView,
)


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


class SyntheticMetric:
    contract = MetricContract("contract-metric", level="window")

    def __call__(self, _context: MetricContext) -> MetricResult:
        observations = MetricObservationCollection(
            (
                MetricObservation(
                    "contract-metric-w1",
                    MetricValue(FakeScalar(0.1), backend="fake", unit="bpm"),
                    level="window",
                    groups={"subject_id": "s1", "sample_id": "w1"},
                ),
                MetricObservation(
                    "contract-metric-w2",
                    MetricValue(FakeScalar(0.2), backend="fake", unit="bpm"),
                    level="window",
                    groups={"subject_id": "s1", "sample_id": "w2"},
                ),
            ),
            provenance={"metric": "synthetic"},
        )
        return MetricResult(observations, contract=self.contract)


class SubjectMetricObservationView:
    plan = MetricObservationViewPlan(
        "subject-contract-view",
        group_keys=("subject_id",),
        output_level="subject",
        source_levels=("window",),
    )

    def __call__(self, collection: MetricObservationCollection) -> MetricObservationCollection:
        return PlannedMetricObservationView(self.plan, projector=self._project)(collection)

    @staticmethod
    def _project(group_key, observations, plan):
        return MetricObservation(
            "contract-metric-subject",
            MetricValue(FakeScalar(float(len(observations))), backend="fake", unit="bpm"),
            level=plan.output_level,
            groups={"subject_id": group_key[0]},
            metadata={"source_count": len(observations)},
            provenance={"contract_view": plan.name},
        )


def test_fake_metric_result_observations_feed_metric_observation_view() -> None:
    metric = SyntheticMetric()
    metric_result = metric(MetricContext(metric.contract))
    view = SubjectMetricObservationView()

    output = view(metric_result.observations)

    assert isinstance(view, MetricObservationView)
    assert isinstance(output, MetricObservationCollection)
    assert len(output) == 1
    assert output[0].level == "subject"
    assert output[0].value.value == FakeScalar(2.0)
    assert output.entries[0].metadata["source_count"] == 2
    assert output.entries[0].provenance["source_observations"] == (
        "contract-metric-w1",
        "contract-metric-w2",
    )
