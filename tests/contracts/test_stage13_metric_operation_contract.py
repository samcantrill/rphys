from __future__ import annotations

from dataclasses import dataclass

from rphys.data import FieldValue, Sample
from rphys.metrics import (
    MetricContext,
    MetricContract,
    MetricInputSpec,
    MetricSampleOperation,
    MetricValue,
)


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


class SampleMaeMetric:
    contract = MetricContract(
        "sample-mae",
        (
            MetricInputSpec("predictions/signal.pulse", role="prediction"),
            MetricInputSpec("targets/signal.pulse", role="target"),
        ),
        level="sample",
        writes=("metrics/custom.stage13.sample_mae",),
    )

    def __call__(self, context: MetricContext) -> MetricValue:
        assert context.fields is not None
        return MetricValue(
            FakeScalar(
                abs(
                    context.fields.require("predictions/signal.pulse")
                    - context.fields.require("targets/signal.pulse")
                )
            ),
            backend="fake",
            unit="bpm",
        )


def test_metric_sample_operation_writes_metric_fields_without_result_rows() -> None:
    sample = Sample(
        {
            "predictions/signal.pulse": FieldValue(1.0),
            "targets/signal.pulse": FieldValue(1.5),
        }
    )
    operation = MetricSampleOperation(SampleMaeMetric())

    result = operation(sample)

    assert result.output.require("metrics/custom.stage13.sample_mae").value == FakeScalar(0.5)
    assert "MetricResult" not in dir(__import__("rphys.metrics").metrics)
