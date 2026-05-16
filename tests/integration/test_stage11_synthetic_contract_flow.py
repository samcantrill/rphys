from __future__ import annotations

from dataclasses import dataclass

from rphys.collections import CollectionItem, CollectorResult
from rphys.data import FieldValue, Sample
from rphys.data.collections import (
    PlannedSampleCollectionView,
    SampleCollection,
    SampleCollectionViewPlan,
    SampleCollector,
)
from rphys.losses import LossContext, LossContract, LossInputSpec, LossResult, LossTerm
from rphys.metrics import (
    MetricContext,
    MetricContract,
    MetricObservation,
    MetricObservationCollection,
    MetricObservationViewPlan,
    MetricResult,
    MetricValue,
    PlannedMetricObservationView,
)
from rphys.objectives import (
    ObjectiveContext,
    ObjectiveContract,
    ObjectiveResult,
    ObjectiveTerm,
    ObjectiveTermSpec,
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


class SyntheticWindowMetric:
    contract = MetricContract(
        "stage11-pulse-mae",
        level="window",
        writes=("metrics/custom.stage11.pulse_mae",),
    )

    def __call__(self, context: MetricContext) -> MetricResult:
        assert context.samples is not None
        observations = []
        for index, entry in enumerate(context.samples.entries):
            observations.append(
                MetricObservation(
                    f"stage11-pulse-mae-{entry.metadata['sample_id']}",
                    MetricValue(
                        FakeScalar(float(entry.value.get("inputs/signal.bvp")[0])),
                        backend="fake",
                        unit="bpm",
                    ),
                    level="window",
                    groups={
                        "subject_id": entry.metadata["subject_id"],
                        "record_id": entry.metadata["record_id"],
                        "sample_id": entry.metadata["sample_id"],
                        "split": entry.metadata["split"],
                    },
                    window={
                        "start": entry.metadata["window_start"],
                        "stop": entry.metadata["window_stop"],
                    },
                    metadata={"sample_index": index},
                    provenance={"metric": self.contract.name},
                )
            )
        return MetricResult(
            MetricObservationCollection(
                observations,
                metadata={"source": "sample_collection"},
                provenance={"sample_view": context.samples.provenance.get("view")},
            ),
            contract=self.contract,
        )


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


def _project_subject(
    group_key: tuple[object, ...],
    observations: tuple[MetricObservation, ...],
    plan: MetricObservationViewPlan,
) -> MetricObservation:
    total = sum(observation.value.value.value for observation in observations)
    return MetricObservation(
        "stage11-pulse-mae-subject",
        MetricValue(FakeScalar(total), backend="fake", unit="bpm"),
        level=plan.output_level,
        groups={"subject_id": group_key[0]},
        window={"source_count": len(observations)},
        metadata={"source_observation_count": len(observations)},
        provenance={"view": plan.name},
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
    sample_view = PlannedSampleCollectionView(
        SampleCollectionViewPlan(
            "ordered-window-view",
            group_keys=("subject_id", "record_id"),
            sort_keys=("window_start",),
            selected_fields=("inputs/signal.bvp",),
        )
    )
    ordered_samples = sample_view(collector_result.collection)
    metric = SyntheticWindowMetric()
    metric_result = metric(MetricContext(metric.contract, samples=ordered_samples))
    observation_view = PlannedMetricObservationView(
        MetricObservationViewPlan(
            "subject-metric-view",
            group_keys=("subject_id",),
            output_level="subject",
            source_levels=("window",),
        ),
        projector=_project_subject,
    )
    subject_observations = observation_view(metric_result.observations)

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
    assert isinstance(ordered_samples, SampleCollection)
    assert [sample.get("inputs/signal.bvp")[0] for sample in ordered_samples] == [1, 2, 4]
    assert isinstance(metric_result.observations, MetricObservationCollection)
    assert [observation.groups["subject_id"] for observation in subject_observations] == [
        "s1",
        "s2",
    ]
    assert [observation.value.value for observation in subject_observations] == [
        FakeScalar(3.0),
        FakeScalar(4.0),
    ]
    assert subject_observations.entries[0].metadata["source_count"] == 2
    assert objective_result.total.value == FakeScalar(0.25)
    assert tuple(str(locator) for locator in loss_result.fields) == (
        "losses/custom.stage11.synthetic_l1",
    )
    assert tuple(str(locator) for locator in objective_result.fields) == (
        "objectives/custom.stage11.synthetic_total",
    )
