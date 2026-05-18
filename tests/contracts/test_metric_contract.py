from __future__ import annotations

from dataclasses import dataclass

from rphys.data import FieldValue, Sample
from rphys.metrics import MetricContext, MetricContract, MetricInputSpec, MetricValue, collect_metric_fields


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


class SyntheticMetric:
    contract = MetricContract(
        "synthetic-metric",
        (
            MetricInputSpec("predictions/signal.pulse", role="prediction"),
            MetricInputSpec("targets/signal.pulse", role="target"),
        ),
        level="window",
        writes=("metrics/custom.stage13.synthetic_metric",),
    )

    def __call__(self, context: MetricContext) -> MetricValue:
        return MetricValue(
            FakeScalar(
                abs(
                    context.fields.require("predictions/signal.pulse")  # type: ignore[union-attr]
                    - context.fields.require("targets/signal.pulse")  # type: ignore[union-attr]
                )
            ),
            backend="fake",
            unit="bpm",
        )


def test_metric_contract_binds_detached_values_to_declared_fields() -> None:
    sample = Sample(
        {
            "predictions/signal.pulse": FieldValue(1.0),
            "targets/signal.pulse": FieldValue(1.25),
        }
    )
    result = collect_metric_fields(
        SyntheticMetric(),
        MetricContext(SyntheticMetric.contract, fields=sample),
    )

    assert tuple(str(locator) for locator in result) == (
        "metrics/custom.stage13.synthetic_metric",
    )
    value = next(iter(result.values())).payload
    assert value.detached is True
    assert value.differentiable is False
    assert value.value == FakeScalar(0.25)
