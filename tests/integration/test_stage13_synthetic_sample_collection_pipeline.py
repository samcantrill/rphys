from __future__ import annotations

from dataclasses import dataclass

from rphys.collections import CollectionItem
from rphys.data import FieldValue, Sample
from rphys.data.collections import (
    PlannedSampleCollectionView,
    SampleCollectionConcatPlan,
    SampleCollectionGroupPlan,
    SampleCollectionViewPlan,
)
from rphys.metrics import MetricCollectionOperation, MetricContext, MetricContract, MetricValue
from rphys.ops import (
    OperationPipeline,
    SampleCollectionConcatOperation,
    SampleCollectionGroupOperation,
    SampleCollectionViewOperation,
)


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


def _artifact_sample(value: int, record_id: str, window_start: int) -> CollectionItem[Sample]:
    return CollectionItem(
        Sample({"inputs/signal.bvp": FieldValue([value])}),
        metadata={
            "datasource": "sample-artifact",
            "subject_id": "s1",
            "record_id": record_id,
            "window_start": window_start,
        },
    )


class MeanWindowMetric:
    contract = MetricContract(
        "mean-window-value",
        level="record",
        writes=("metrics/custom.stage13.mean_window_value",),
    )

    def __call__(self, context: MetricContext) -> MetricValue:
        assert context.samples is not None
        values = [entry.value.get("inputs/signal.bvp")[0] for entry in context.samples.entries]
        return MetricValue(FakeScalar(sum(values) / len(values)), backend="fake")


def test_evaluation_like_recipe_uses_generic_operations_without_runner_names() -> None:
    source = (
        _artifact_sample(2, "r1", 2),
        _artifact_sample(1, "r1", 1),
        _artifact_sample(5, "r2", 1),
    )
    group = SampleCollectionGroupOperation(
        SampleCollectionGroupPlan("group-artifacts", group_keys=("subject_id", "record_id"))
    )
    sort = SampleCollectionViewOperation(
        PlannedSampleCollectionView(SampleCollectionViewPlan("sort-windows", sort_keys=("window_start",)))
    )
    metric = MetricCollectionOperation(MeanWindowMetric())
    stitch = SampleCollectionConcatOperation(
        SampleCollectionConcatPlan(
            "stitch-record",
            field_map={"inputs/signal.bvp": "outputs/signal.bvp"},
        ),
        payload_joiner=lambda payloads: tuple(payload[0] for payload in payloads),
    )

    grouped = group(source).output
    pipeline = OperationPipeline((sort, metric, stitch))
    record_samples = tuple(pipeline(collection).output for collection in grouped)

    assert [sample.get("outputs/signal.bvp") for sample in record_samples] == [(1, 2), (5,)]
    assert record_samples[0].field("outputs/signal.bvp").metadata["collection.operation"] == "stitch-record"
    assert "EvaluationRunner" not in dir(__import__("rphys.evaluation").evaluation)
    assert "EvaluationPlan" not in dir(__import__("rphys.evaluation").evaluation)
