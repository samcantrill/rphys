from __future__ import annotations

import importlib


def test_metric_observation_result_family_is_not_public() -> None:
    import rphys.metrics as metrics

    forbidden = [
        "MetricObservation",
        "MetricObservationCollection",
        "MetricObservationView",
        "MetricObservationViewPlan",
        "MetricResult",
        "PlannedMetricObservationView",
    ]
    for public_name in forbidden:
        assert public_name not in metrics.__all__
        assert not hasattr(metrics, public_name)


def test_metric_modules_do_not_re_export_observation_or_result_family() -> None:
    forbidden = [
        "MetricObservation",
        "MetricObservationCollection",
        "MetricObservationView",
        "MetricObservationViewPlan",
        "MetricResult",
        "PlannedMetricObservationView",
    ]
    for module_name in ("rphys.metrics.core", "rphys.metrics.results", "rphys.metrics.specs"):
        module = importlib.import_module(module_name)
        for public_name in forbidden:
            assert public_name not in module.__all__
            assert not hasattr(module, public_name)
