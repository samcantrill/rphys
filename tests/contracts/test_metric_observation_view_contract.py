from __future__ import annotations


def test_stage13_metric_contract_exposes_no_observation_view_family() -> None:
    import rphys.metrics as metrics

    for public_name in [
        "MetricObservation",
        "MetricObservationCollection",
        "MetricObservationView",
        "MetricObservationViewPlan",
        "MetricResult",
        "PlannedMetricObservationView",
    ]:
        assert public_name not in metrics.__all__
        assert not hasattr(metrics, public_name)
