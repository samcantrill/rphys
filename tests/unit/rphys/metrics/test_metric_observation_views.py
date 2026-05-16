from __future__ import annotations

from dataclasses import dataclass

import pytest

from rphys.errors import InvalidMetricResultError, InvalidMetricSpecError
from rphys.metrics import (
    MetricObservation,
    MetricObservationCollection,
    MetricObservationView,
    MetricObservationViewPlan,
    MetricValue,
    PlannedMetricObservationView,
)


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


def _observation(
    name: str,
    *,
    subject_id: str = "s1",
    sample_id: str = "w1",
    level: str = "window",
    groups: dict[str, object] | None = None,
) -> MetricObservation:
    resolved_groups = {
        "subject_id": subject_id,
        "sample_id": sample_id,
        "split": "train",
    }
    if groups is not None:
        resolved_groups = groups
    return MetricObservation(
        name,
        MetricValue(FakeScalar(1.0), backend="fake", unit="bpm"),
        level=level,
        groups=resolved_groups,
        window={"start": sample_id, "stop": f"{sample_id}-stop"},
        metadata={"fixture": "unit"},
        provenance={"source": "metric"},
    )


def _project_subject(
    group_key: tuple[object, ...],
    observations: tuple[MetricObservation, ...],
    plan: MetricObservationViewPlan,
) -> MetricObservation:
    return MetricObservation(
        "pulse-mae.subject",
        MetricValue(FakeScalar(float(len(observations))), backend="fake", unit="bpm"),
        level=plan.output_level,
        groups={"subject_id": group_key[0]},
        window={"source_level": observations[0].level},
        metadata={"projected": True},
        provenance={"projector": "fake"},
    )


def test_metric_observation_view_plan_validates_grouping_and_policies() -> None:
    plan = MetricObservationViewPlan(
        "subject-summary",
        group_keys=("subject_id", "split"),
        output_level="subject",
        source_levels=("window",),
        missing_policy="allow",
        empty_policy="allow",
        mixed_level_policy="allow",
        metadata={"purpose": "coarse-view"},
        provenance={"stage": "11"},
    )

    assert plan.group_keys == ("subject_id", "split")
    assert plan.output_level == "subject"
    assert plan.source_levels == ("window",)
    assert plan.metadata == {"purpose": "coarse-view"}

    with pytest.raises(InvalidMetricSpecError):
        MetricObservationViewPlan("", group_keys=("subject_id",))
    with pytest.raises(InvalidMetricSpecError):
        MetricObservationViewPlan("bad", group_keys=("subject_id", "subject_id"))
    with pytest.raises(InvalidMetricSpecError):
        MetricObservationViewPlan("bad", output_level="epoch")
    with pytest.raises(InvalidMetricSpecError):
        MetricObservationViewPlan("bad", source_levels=("window", "window"))
    with pytest.raises(InvalidMetricSpecError):
        MetricObservationViewPlan("bad", missing_policy="skip")
    with pytest.raises(InvalidMetricSpecError):
        MetricObservationViewPlan("bad", empty_policy="drop")
    with pytest.raises(InvalidMetricSpecError):
        MetricObservationViewPlan("bad", mixed_level_policy="coerce")


def test_planned_metric_observation_view_groups_with_injected_projector() -> None:
    source = MetricObservationCollection(
        (
            _observation("pulse-mae-w1", subject_id="s1", sample_id="w1"),
            _observation("pulse-mae-w2", subject_id="s1", sample_id="w2"),
            _observation("pulse-mae-w3", subject_id="s2", sample_id="w3"),
        ),
        metadata={"level": "window"},
        provenance={"metric": "fake"},
    )
    plan = MetricObservationViewPlan(
        "subject-view",
        group_keys=("subject_id",),
        output_level="subject",
        source_levels=("window",),
        metadata={"view_scope": "subject"},
        provenance={"owner": "unit"},
    )
    calls: list[tuple[tuple[object, ...], tuple[str, ...]]] = []

    def projector(group_key, observations, view_plan):
        assert view_plan is plan
        calls.append((group_key, tuple(observation.name for observation in observations)))
        return _project_subject(group_key, observations, view_plan)

    view = PlannedMetricObservationView(plan, projector=projector)
    output = view(source)

    assert isinstance(view, MetricObservationView)
    assert len(output) == 2
    assert calls == [
        (("s1",), ("pulse-mae-w1", "pulse-mae-w2")),
        (("s2",), ("pulse-mae-w3",)),
    ]
    assert [observation.value.value for observation in output] == [
        FakeScalar(2.0),
        FakeScalar(1.0),
    ]
    assert output[0].level == "subject"
    assert output[0].groups == {"subject_id": "s1"}
    assert output.metadata["view"] == "subject-view"
    assert output.metadata["source_count"] == 3
    assert output.entries[0].metadata["source_count"] == 2
    assert output.entries[0].metadata["group_key"] == ("s1",)
    assert output.entries[0].provenance["source_observations"] == (
        "pulse-mae-w1",
        "pulse-mae-w2",
    )


def test_planned_metric_observation_view_missing_group_policy_is_explicit() -> None:
    source = MetricObservationCollection(
        (_observation("pulse-mae-w1", groups={"sample_id": "w1"}),)
    )
    default_view = PlannedMetricObservationView(
        MetricObservationViewPlan(
            "subject-view",
            group_keys=("subject_id",),
            output_level="subject",
        ),
        projector=_project_subject,
    )
    with pytest.raises(InvalidMetricResultError):
        default_view(source)

    allowing_view = PlannedMetricObservationView(
        MetricObservationViewPlan(
            "subject-view",
            group_keys=("subject_id",),
            output_level="subject",
            missing_policy="allow",
        ),
        projector=_project_subject,
    )

    output = allowing_view(source)

    assert output[0].groups == {"subject_id": None}
    assert output.entries[0].metadata["group_key"] == (None,)


def test_planned_metric_observation_view_empty_input_policy_is_explicit() -> None:
    empty = MetricObservationCollection(())
    default_view = PlannedMetricObservationView(
        MetricObservationViewPlan("dataset-view", output_level="dataset"),
        projector=lambda group_key, observations, plan: _project_subject(group_key, observations, plan),
    )
    with pytest.raises(InvalidMetricResultError):
        default_view(empty)

    allowing_view = PlannedMetricObservationView(
        MetricObservationViewPlan(
            "dataset-view",
            output_level="dataset",
            empty_policy="allow",
        ),
        projector=lambda group_key, observations, plan: _project_subject(group_key, observations, plan),
    )
    output = allowing_view(empty)

    assert len(output) == 0
    assert output.metadata["view"] == "dataset-view"


def test_planned_metric_observation_view_rejects_source_level_ambiguity() -> None:
    source = MetricObservationCollection(
        (
            _observation("pulse-mae-window", sample_id="w1", level="window"),
            _observation("pulse-mae-sample", sample_id="w2", level="sample"),
        )
    )
    mixed_view = PlannedMetricObservationView(
        MetricObservationViewPlan(
            "subject-view",
            group_keys=("subject_id",),
            output_level="subject",
        ),
        projector=_project_subject,
    )
    with pytest.raises(InvalidMetricResultError):
        mixed_view(source)

    source_level_view = PlannedMetricObservationView(
        MetricObservationViewPlan(
            "window-only-view",
            group_keys=("subject_id",),
            output_level="subject",
            source_levels=("window",),
            mixed_level_policy="allow",
        ),
        projector=_project_subject,
    )
    with pytest.raises(InvalidMetricResultError):
        source_level_view(source)


def test_planned_metric_observation_view_validates_projector_shape() -> None:
    source = MetricObservationCollection((_observation("pulse-mae-w1"),))
    plan = MetricObservationViewPlan(
        "subject-view",
        group_keys=("subject_id",),
        output_level="subject",
    )

    with pytest.raises(InvalidMetricSpecError):
        PlannedMetricObservationView(plan, projector=None)  # type: ignore[arg-type]

    bad_shape = PlannedMetricObservationView(
        plan,
        projector=lambda _group_key, _observations, _plan: object(),  # type: ignore[return-value]
    )
    with pytest.raises(InvalidMetricResultError):
        bad_shape(source)

    bad_level = PlannedMetricObservationView(
        plan,
        projector=lambda group_key, observations, _plan: MetricObservation(
            "pulse-mae.dataset",
            MetricValue(FakeScalar(float(len(observations))), backend="fake"),
            level="dataset",
            groups={"subject_id": group_key[0]},
        ),
    )
    with pytest.raises(InvalidMetricResultError):
        bad_level(source)


def test_metric_observation_view_does_not_create_public_result_or_state_classes() -> None:
    import rphys.metrics as metrics

    for public_name in [
        "MetricObservationViewResult",
        "MetricObservationViewState",
        "MetricAggregationResult",
        "MetricResultTable",
    ]:
        assert not hasattr(metrics, public_name)
