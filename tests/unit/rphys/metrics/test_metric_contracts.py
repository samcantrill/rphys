from __future__ import annotations

from dataclasses import dataclass

import pytest

from rphys.collections import CollectionItem
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
    MetricCollectionOperation,
    MetricContext,
    MetricContract,
    MetricInputSpec,
    MetricSampleOperation,
    MetricValue,
    collect_metric_fields,
)
from rphys.ops import OperationContext, SampleOperationContext


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


class FakeMetric:
    contract = MetricContract(
        "pulse-mae",
        (
            MetricInputSpec("predictions/signal.pulse", role="prediction"),
            MetricInputSpec("targets/signal.pulse", role="target"),
        ),
        level="sample",
        writes=("metrics/custom.stage13.pulse_mae",),
    )

    def __call__(self, context: MetricContext) -> MetricValue:
        prediction = context.fields.require("predictions/signal.pulse")  # type: ignore[union-attr]
        target = context.fields.require("targets/signal.pulse")  # type: ignore[union-attr]
        return MetricValue(
            FakeScalar(abs(prediction - target)),
            backend="fake",
            unit="bpm",
            metadata={"split": context.metadata.get("split")},
        )


def test_metric_specs_validate_locators_levels_and_grouping() -> None:
    input_spec = MetricInputSpec("predictions/signal.pulse", role="prediction")
    contract = MetricContract(
        "mae",
        (input_spec,),
        level="sample",
        writes=("metrics/custom.stage13.mae",),
    )
    grouping = GroupBySpec(("subject_id", "record_id"), level="group")

    assert str(input_spec.locator) == "predictions/signal.pulse"
    assert contract.inputs == (input_spec,)
    assert tuple(str(locator) for locator in contract.writes) == ("metrics/custom.stage13.mae",)
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


def test_collect_metric_fields_binds_single_value_to_declared_metric_field() -> None:
    sample = Sample(
        {
            "predictions/signal.pulse": FieldValue(1.0),
            "targets/signal.pulse": FieldValue(1.25),
        }
    )
    metric = FakeMetric()

    fields = collect_metric_fields(
        metric,
        MetricContext(metric.contract, fields=sample, metadata={"split": "test"}),
    )

    assert isinstance(metric, Metric)
    assert tuple(str(locator) for locator in fields) == ("metrics/custom.stage13.pulse_mae",)
    assert fields[next(iter(fields))].payload.value == FakeScalar(0.25)
    assert fields[next(iter(fields))].metadata["metric.unit"] == "bpm"


def test_collect_metric_fields_validates_declared_writes() -> None:
    class MissingMetric:
        contract = MetricContract(
            "missing",
            writes=("metrics/custom.stage13.first", "metrics/custom.stage13.second"),
        )

        def __call__(self, _context: MetricContext):
            return {"metrics/custom.stage13.first": MetricValue(FakeScalar(1.0))}

    class UndeclaredMetric:
        contract = MetricContract("undeclared", writes=("metrics/custom.stage13.first",))

        def __call__(self, _context: MetricContext):
            return {"metrics/custom.stage13.other": MetricValue(FakeScalar(1.0))}

    class NoWriteMetric:
        contract = MetricContract("no-write")

        def __call__(self, _context: MetricContext):
            return MetricValue(FakeScalar(1.0))

    for metric in (MissingMetric(), UndeclaredMetric(), NoWriteMetric()):
        with pytest.raises(InvalidMetricResultError):
            collect_metric_fields(metric, MetricContext(metric.contract))


def test_metric_sample_operation_writes_declared_metric_fields() -> None:
    sample = Sample(
        {
            "predictions/signal.pulse": FieldValue(1.0),
            "targets/signal.pulse": FieldValue(1.5),
        }
    )
    operation = MetricSampleOperation(FakeMetric())

    result = operation(sample, SampleOperationContext(metadata={"split": "valid"}))

    assert result.output is not sample
    assert result.output.require("metrics/custom.stage13.pulse_mae").value == FakeScalar(0.5)
    assert result.metadata["sample_field_effects"]["added"] == ("metrics/custom.stage13.pulse_mae",)
    assert not sample.has("metrics/custom.stage13.pulse_mae")


def test_metric_collection_operation_replicates_collection_level_metric_fields() -> None:
    class CollectionMetric:
        contract = MetricContract("window-count", level="record", writes=("metrics/custom.stage13.window_count",))

        def __call__(self, context: MetricContext) -> MetricValue:
            assert context.samples is not None
            return MetricValue(FakeScalar(float(len(context.samples))), backend="fake")

    entries = (
        CollectionItem(Sample({"inputs/signal.bvp": FieldValue([1])}), metadata={"record_id": "r1"}),
        CollectionItem(Sample({"inputs/signal.bvp": FieldValue([2])}), metadata={"record_id": "r1"}),
    )
    collection = SampleCollection(entries, metadata={"level": "window"})
    operation = MetricCollectionOperation(CollectionMetric())

    result = operation(collection, OperationContext(metadata={"split": "test"}))

    assert isinstance(result.output, SampleCollection)
    assert result.output.metadata["metric_binding"] == "replicated_collection_fields"
    assert [sample.require("metrics/custom.stage13.window_count").value for sample in result.output] == [
        FakeScalar(2.0),
        FakeScalar(2.0),
    ]
    assert not collection[0].has("metrics/custom.stage13.window_count")
