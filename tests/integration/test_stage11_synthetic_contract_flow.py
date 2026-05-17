from __future__ import annotations

from dataclasses import dataclass

from rphys.collections import CollectionItem, CollectorResult
from rphys.data import FieldValue, Sample
from rphys.data.collections import (
    PlannedSampleCollectionView,
    SampleCollection,
    SampleCollectionConcatPlan,
    SampleCollectionGroupPlan,
    SampleCollectionViewPlan,
    SampleCollector,
)
from rphys.losses import LossContext, LossContract, LossInputSpec, LossResult, LossTerm
from rphys.metrics import MetricCollectionOperation, MetricContext, MetricContract, MetricValue
from rphys.objectives import (
    ObjectiveContext,
    ObjectiveContract,
    ObjectiveResult,
    ObjectiveTerm,
    ObjectiveTermSpec,
)
from rphys.ops import (
    OperationContext,
    OperationPipeline,
    SampleCollectionConcatOperation,
    SampleCollectionGroupOperation,
    SampleCollectionViewOperation,
)


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


def _entry(
    value: int,
    *,
    subject_id: str,
    record_id: str,
    window_start: int,
) -> CollectionItem[Sample]:
    return CollectionItem(
        Sample({"inputs/signal.bvp": FieldValue([value])}),
        metadata={
            "subject_id": subject_id,
            "record_id": record_id,
            "sample_id": f"{record_id}-{window_start}",
            "split": "valid",
            "window_start": window_start,
            "window_stop": window_start + 1,
        },
        provenance={"fixture": "integration"},
    )


class WindowCountMetric:
    contract = MetricContract(
        "stage13-window-count",
        level="record",
        writes=("metrics/custom.stage13.window_count",),
    )

    def __call__(self, context: MetricContext) -> MetricValue:
        assert context.samples is not None
        return MetricValue(FakeScalar(float(len(context.samples))), backend="fake")


class SyntheticLoss:
    contract = LossContract(
        "stage11-synthetic-l1",
        (
            LossInputSpec("predictions/signal.pulse", role="prediction"),
            LossInputSpec("targets/signal.pulse", role="target"),
        ),
        writes=("losses/custom.stage11.synthetic_l1",),
    )

    def __call__(self, context: LossContext) -> LossResult:
        assert context.fields is not None
        prediction = context.fields.get("predictions/signal.pulse")[0]
        target = context.fields.get("targets/signal.pulse")[0]
        value = FakeScalar(abs(prediction - target))
        return LossResult(
            (
                LossTerm(
                    "stage11-synthetic-l1",
                    value,
                    backend="fake",
                    reduction="mean",
                    gradient_path="prediction->l1",
                ),
            ),
            fields={"losses/custom.stage11.synthetic_l1": FieldValue(value)},
            contract=context.contract,
            provenance={"loss": "synthetic"},
        )


class SyntheticObjective:
    contract = ObjectiveContract(
        "stage11-synthetic-total",
        (ObjectiveTermSpec("l1", source="loss:stage11-synthetic-l1", weight=1.0),),
        writes=("objectives/custom.stage11.synthetic_total",),
    )

    def __call__(self, context: ObjectiveContext) -> ObjectiveResult:
        component = ObjectiveTerm.from_loss_term(context.loss_results[0].primary, name="l1")
        total = ObjectiveTerm(
            "total",
            component.value,
            backend=component.backend,
            source_terms=(component.name,),
            gradient_path=component.gradient_path,
        )
        return ObjectiveResult(
            total=total,
            terms=(component,),
            fields={"objectives/custom.stage11.synthetic_total": FieldValue(total.value)},
            contract=context.contract,
        )


def test_stage_11_records_compose_without_trainer_or_evaluator_lifecycle() -> None:
    collector_result = SampleCollector(
        required_metadata=("subject_id", "record_id", "sample_id", "window_start", "split")
    )(
        (
            _entry(2, subject_id="s1", record_id="r1", window_start=2),
            _entry(1, subject_id="s1", record_id="r1", window_start=1),
            _entry(4, subject_id="s2", record_id="r2", window_start=1),
        )
    )
    group = SampleCollectionGroupOperation(
        SampleCollectionGroupPlan("record-groups", group_keys=("subject_id", "record_id"))
    )
    sort = SampleCollectionViewOperation(
        PlannedSampleCollectionView(
            SampleCollectionViewPlan(
                "ordered-window-view",
                sort_keys=("window_start",),
                selected_fields=("inputs/signal.bvp",),
            )
        )
    )
    metric = MetricCollectionOperation(WindowCountMetric())
    stitch = SampleCollectionConcatOperation(
        SampleCollectionConcatPlan(
            "record-stitch",
            field_map={"inputs/signal.bvp": "outputs/signal.bvp"},
        ),
        payload_joiner=lambda payloads: tuple(payload[0] for payload in payloads),
    )

    grouped = group(collector_result.collection, OperationContext(metadata={"split": "valid"})).output
    record_collection = OperationPipeline((sort, metric))(grouped[0]).output
    stitched = stitch(record_collection).output

    fields = Sample(
        {
            "predictions/signal.pulse": FieldValue([1.0]),
            "targets/signal.pulse": FieldValue([1.25]),
        }
    )
    loss = SyntheticLoss()
    loss_result = loss(LossContext(loss.contract, fields))
    objective = SyntheticObjective()
    objective_result = objective(ObjectiveContext(objective.contract, loss_results=(loss_result,)))

    assert isinstance(collector_result, CollectorResult)
    assert isinstance(record_collection, SampleCollection)
    assert [sample.get("inputs/signal.bvp")[0] for sample in record_collection] == [1, 2]
    assert [sample.require("metrics/custom.stage13.window_count").value for sample in record_collection] == [
        FakeScalar(2.0),
        FakeScalar(2.0),
    ]
    assert stitched.get("outputs/signal.bvp") == (1, 2)
    assert objective_result.total.value == FakeScalar(0.25)
    assert tuple(str(locator) for locator in loss_result.fields) == (
        "losses/custom.stage11.synthetic_l1",
    )
    assert tuple(str(locator) for locator in objective_result.fields) == (
        "objectives/custom.stage11.synthetic_total",
    )
