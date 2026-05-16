from __future__ import annotations

from dataclasses import dataclass

import pytest

from rphys.data import FieldValue, Sample
from rphys.data.collections import SampleCollection
from rphys.errors import (
    InvalidMetricContextError,
    InvalidMetricResultError,
    InvalidMetricSpecError,
)
from rphys.metrics import (
    GroupBySpec,
    Metric,
    MetricContext,
    MetricContract,
    MetricInputSpec,
    MetricObservation,
    MetricObservationCollection,
    MetricResult,
    MetricValue,
)


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


class FakeMetric:
    contract = MetricContract(
        "pulse-mae",
        (MetricInputSpec("predictions/signal.pulse", role="prediction"),),
        level="sample",
        writes=("metrics/custom.stage11.pulse_mae",),
    )

    def __call__(self, context: MetricContext) -> MetricResult:
        observation = MetricObservation(
            "pulse-mae",
            MetricValue(FakeScalar(1.5), backend="fake", unit="bpm"),
            level=context.contract.level,
            groups={"subject_id": "s1", "record_id": "r1", "split": "test"},
        )
        return MetricResult(
            MetricObservationCollection((observation,)),
            fields={"metrics/custom.stage11.pulse_mae": FieldValue(FakeScalar(1.5))},
            contract=context.contract,
        )


def test_metric_specs_validate_locators_levels_and_grouping() -> None:
    input_spec = MetricInputSpec("predictions/signal.pulse", role="prediction")
    contract = MetricContract("mae", (input_spec,), level="sample")
    grouping = GroupBySpec(("subject_id", "record_id"), level="group")

    assert str(input_spec.locator) == "predictions/signal.pulse"
    assert contract.inputs == (input_spec,)
    assert grouping.keys == ("subject_id", "record_id")

    with pytest.raises(InvalidMetricSpecError):
        MetricInputSpec("predictions/signal.pulse", role="")
    with pytest.raises(InvalidMetricSpecError):
        MetricContract("bad", (input_spec,), level="epoch")
    with pytest.raises(InvalidMetricSpecError):
        GroupBySpec(("subject_id", "subject_id"))


def test_metric_context_accepts_field_containers_and_sample_collections() -> None:
    sample = Sample({"predictions/signal.pulse": FieldValue(72.0)})
    samples = SampleCollection((sample,), metadata={"source": "unit"})
    context = MetricContext(FakeMetric.contract, fields=sample, samples=samples)

    assert context.fields is sample
    assert context.samples is samples

    with pytest.raises(InvalidMetricContextError):
        MetricContext(object())  # type: ignore[arg-type]
    with pytest.raises(InvalidMetricContextError):
        MetricContext(FakeMetric.contract, samples=object())  # type: ignore[arg-type]


def test_metric_value_is_detached_and_non_differentiable() -> None:
    value = MetricValue(
        FakeScalar(0.1),
        backend="fake",
        detached=True,
        differentiable=False,
        unit="bpm",
        diagnostics={"flat_signal": False},
    )

    assert value.value == FakeScalar(0.1)
    assert value.detached is True
    assert value.differentiable is False
    assert value.diagnostics == {"flat_signal": False}

    with pytest.raises(InvalidMetricResultError):
        MetricValue(None)
    with pytest.raises(InvalidMetricResultError):
        MetricValue(FakeScalar(0.1), detached=False)
    with pytest.raises(InvalidMetricResultError):
        MetricValue(FakeScalar(0.1), differentiable=True)


def test_metric_observation_collection_preserves_groups_and_groups_by_spec() -> None:
    first = MetricObservation(
        "mae",
        MetricValue(FakeScalar(1.0)),
        level="window",
        groups={"subject_id": "s1", "record_id": "r1"},
        window={"start": 0, "stop": 1},
    )
    second = MetricObservation(
        "mae",
        MetricValue(FakeScalar(2.0)),
        level="window",
        groups={"subject_id": "s2", "record_id": "r2"},
    )
    collection = MetricObservationCollection((first, second), metadata={"scope": "window"})

    grouped = collection.grouped(GroupBySpec(("subject_id",)))

    assert list(collection) == [first, second]
    assert collection.entries[0].metadata["subject_id"] == "s1"
    assert tuple(grouped) == (("s1",), ("s2",))
    assert list(grouped[("s1",)]) == [first]
    with pytest.raises(TypeError):
        collection.metadata["scope"] = "record"  # type: ignore[index]


def test_metric_observation_collection_validates_duplicates_and_missing_groups() -> None:
    observation = MetricObservation(
        "mae",
        MetricValue(FakeScalar(1.0)),
        groups={"subject_id": "s1"},
    )

    with pytest.raises(InvalidMetricResultError):
        MetricObservationCollection((observation, observation))

    collection = MetricObservationCollection((observation,))
    with pytest.raises(InvalidMetricResultError):
        collection.grouped(GroupBySpec(("record_id",)))


def test_metric_result_validates_patch_fields_and_rejects_table_names() -> None:
    observation = MetricObservation("mae", MetricValue(FakeScalar(1.0)))
    collection = MetricObservationCollection((observation,))
    result = MetricResult(
        collection,
        fields={"metrics/custom.stage11.pulse_mae": FieldValue(FakeScalar(1.0))},
        contract=FakeMetric.contract,
    )

    assert result.observations is collection
    assert str(next(iter(result.fields))) == "metrics/custom.stage11.pulse_mae"
    with pytest.raises(TypeError):
        result.fields["metrics/custom.stage11.other"] = FieldValue(1.0)  # type: ignore[index]
    with pytest.raises(InvalidMetricResultError):
        MetricResult(collection, fields={"metrics/custom.stage11.pulse_mae": FieldValue(1.0)})
    with pytest.raises(InvalidMetricResultError):
        MetricResult(collection, fields={"metrics/custom.stage11.undeclared": FieldValue(1.0)}, contract=FakeMetric.contract)


def test_fake_metric_satisfies_protocol_and_returns_observation_collection() -> None:
    metric = FakeMetric()
    context = MetricContext(metric.contract)

    assert isinstance(metric, Metric)
    result = metric(context)

    assert isinstance(result, MetricResult)
    assert len(result.observations) == 1
    assert result.observations[0].value.value == FakeScalar(1.5)
    assert result.observations[0].groups["subject_id"] == "s1"
