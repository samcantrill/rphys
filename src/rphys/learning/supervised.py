"""Supervised learner composition for methods, losses, objectives, and metrics."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from rphys.data import Batch
from rphys.errors import RemotePhysLearningError
from rphys.losses import Loss, LossContext, LossResult, LossTerm
from rphys.methods import Method, MethodOutput, PredictionContext, apply_method_output
from rphys.metrics import Metric, MetricContext, MetricResult, MetricValue
from rphys.objectives import Objective, ObjectiveContext, ObjectiveResult, ObjectiveTerm

from .context import LoopContext
from .modes import LoopMode
from .output import StepOutput

__all__ = ["SupervisedLearner"]


@dataclass(frozen=True, slots=True)
class SupervisedLearner:
    """Compose a batch-level method with optional supervised scoring.

    ``method.predict`` is always the source of predictions. When losses,
    objectives, or metrics are configured and the method returns a
    ``MethodOutput`` patch, the patch is applied to a shallow local batch copy
    for those calculations only. The returned ``StepOutput.predictions`` keeps
    the raw ``MethodOutput`` by default, so trainers do not materialize,
    uncollate, export, or route prediction fields.
    """

    method: Method
    objective: Objective | None = None
    losses: tuple[Loss, ...] = ()
    metrics: tuple[Metric, ...] = ()

    def __init__(
        self,
        method: Method,
        *,
        objective: Objective | None = None,
        losses: Iterable[Loss] = (),
        metrics: Iterable[Metric] = (),
    ) -> None:
        _validate_method(method)
        object.__setattr__(self, "method", method)
        _validate_objective(objective)
        object.__setattr__(self, "objective", objective)
        object.__setattr__(self, "losses", _coerce_callables(losses, field="losses"))
        object.__setattr__(self, "metrics", _coerce_callables(metrics, field="metrics"))

    def step(self, batch: Batch, context: LoopContext) -> StepOutput:
        """Run one supervised learner step for the requested loop mode."""

        if not isinstance(batch, Batch):
            raise RemotePhysLearningError(
                "SupervisedLearner.step requires a Batch.",
                owner="SupervisedLearner",
                field="batch",
                expected="Batch",
                actual=type(batch).__name__,
            )
        if not isinstance(context, LoopContext):
            raise RemotePhysLearningError(
                "SupervisedLearner.step requires a LoopContext.",
                owner="SupervisedLearner",
                field="context",
                expected="LoopContext",
                actual=type(context).__name__,
            )
        if context.mode is LoopMode.TRAIN and self.objective is None:
            raise RemotePhysLearningError(
                "Train mode requires a configured objective.",
                owner="SupervisedLearner",
                field="objective",
                mode=context.mode.value,
            )

        predictions = self.method.predict(
            batch,
            context=PredictionContext(
                metadata=_prediction_metadata(context),
                provenance=context.provenance,
            ),
        )
        if context.mode is LoopMode.PREDICT:
            return StepOutput(
                predictions=predictions,
                diagnostics=_diagnostics(
                    predictions=predictions,
                    loss_results=(),
                    objective_result=None,
                    metric_results=(),
                ),
                metadata={
                    "mode": context.mode.value,
                    "split": context.split,
                },
                provenance={"learner": "SupervisedLearner"},
            )
        working_batch = self._working_batch(batch, predictions)
        loss_results = self._evaluate_losses(working_batch, context)
        objective_result = self._evaluate_objective(loss_results, context)
        metric_results = self._evaluate_metrics(working_batch, context)

        return StepOutput(
            predictions=predictions,
            objective=None if objective_result is None else objective_result.total.value,
            loss_terms=_loss_terms(loss_results),
            objective_terms=_objective_terms(objective_result),
            metric_values=_metric_values(metric_results),
            diagnostics=_diagnostics(
                predictions=predictions,
                loss_results=loss_results,
                objective_result=objective_result,
                metric_results=metric_results,
            ),
            metadata={
                "mode": context.mode.value,
                "split": context.split,
            },
            provenance={"learner": "SupervisedLearner"},
        )

    def _working_batch(self, batch: Batch, predictions: MethodOutput) -> Batch:
        if not self.losses and self.objective is None and not self.metrics:
            return batch
        return apply_method_output(predictions, batch, copy_batch=True, on_conflict="error")

    def _evaluate_losses(
        self,
        fields: Batch,
        context: LoopContext,
    ) -> tuple[LossResult, ...]:
        results: list[LossResult] = []
        for loss in self.losses:
            result = loss(
                LossContext(
                    loss.contract,
                    fields,
                    metadata=_context_metadata(context),
                    provenance=context.provenance,
                )
            )
            if not isinstance(result, LossResult):
                raise RemotePhysLearningError(
                    "Loss callable must return a LossResult.",
                    owner="SupervisedLearner",
                    field="losses",
                    actual=type(result).__name__,
                )
            results.append(result)
        return tuple(results)

    def _evaluate_objective(
        self,
        loss_results: tuple[LossResult, ...],
        context: LoopContext,
    ) -> ObjectiveResult | None:
        if self.objective is None:
            return None
        result = self.objective(
            ObjectiveContext(
                self.objective.contract,
                loss_results=loss_results,
                metadata=_context_metadata(context),
                provenance=context.provenance,
            )
        )
        if not isinstance(result, ObjectiveResult):
            raise RemotePhysLearningError(
                "Objective callable must return an ObjectiveResult.",
                owner="SupervisedLearner",
                field="objective",
                actual=type(result).__name__,
            )
        return result

    def _evaluate_metrics(
        self,
        fields: Batch,
        context: LoopContext,
    ) -> tuple[MetricResult, ...]:
        results: list[MetricResult] = []
        for metric in self.metrics:
            result = metric(
                MetricContext(
                    metric.contract,
                    fields=fields,
                    metadata=_context_metadata(context),
                    provenance=context.provenance,
                )
            )
            if not isinstance(result, MetricResult):
                raise RemotePhysLearningError(
                    "Metric callable must return a MetricResult.",
                    owner="SupervisedLearner",
                    field="metrics",
                    actual=type(result).__name__,
                )
            results.append(result)
        return tuple(results)


def _validate_method(method: object) -> None:
    predict = getattr(method, "predict", None)
    if not callable(predict):
        raise RemotePhysLearningError(
            "SupervisedLearner method must provide predict(batch, context=...).",
            owner="SupervisedLearner",
            field="method",
            expected="Method",
            actual=type(method).__name__,
        )


def _validate_objective(objective: object | None) -> None:
    if objective is None:
        return
    if not callable(objective) or not hasattr(objective, "contract"):
        raise RemotePhysLearningError(
            "SupervisedLearner objective must provide a contract and be callable.",
            owner="SupervisedLearner",
            field="objective",
            expected="Objective | None",
            actual=type(objective).__name__,
        )


def _coerce_callables(values: Iterable[object], *, field: str) -> tuple[object, ...]:
    try:
        items = tuple(values)
    except TypeError as exc:
        raise RemotePhysLearningError(
            f"SupervisedLearner {field} must be iterable.",
            owner="SupervisedLearner",
            field=field,
            expected="iterable",
            actual=type(values).__name__,
        ) from exc
    for index, item in enumerate(items):
        if not callable(item) or not hasattr(item, "contract"):
            raise RemotePhysLearningError(
                f"SupervisedLearner {field} entries must provide a contract and be callable.",
                owner="SupervisedLearner",
                field=field,
                index=index,
                actual=type(item).__name__,
            )
    return items


def _prediction_metadata(context: LoopContext) -> Mapping[str, object]:
    return {
        "mode": context.mode.value,
        "split": context.split,
        "epoch_index": context.epoch_index,
        "step_index": context.step_index,
        "batch_index": context.batch_index,
    }


def _context_metadata(context: LoopContext) -> Mapping[str, object]:
    metadata = dict(context.metadata)
    metadata.update(_prediction_metadata(context))
    return metadata


def _loss_terms(results: Iterable[LossResult]) -> tuple[LossTerm, ...]:
    return tuple(term for result in results for term in result.terms)


def _objective_terms(result: ObjectiveResult | None) -> tuple[ObjectiveTerm, ...]:
    if result is None:
        return ()
    return (result.total, *result.terms)


def _metric_values(results: Iterable[MetricResult]) -> Mapping[str, MetricValue]:
    values: dict[str, MetricValue] = {}
    for result in results:
        for index, observation in enumerate(result.observations):
            key = observation.name
            if key in values:
                key = f"{observation.name}#{index}"
            values[key] = observation.value
    return values


def _diagnostics(
    *,
    predictions: MethodOutput,
    loss_results: tuple[LossResult, ...],
    objective_result: ObjectiveResult | None,
    metric_results: tuple[MetricResult, ...],
) -> Mapping[str, object]:
    diagnostics = dict(predictions.diagnostics)
    diagnostics.update(
        {
            "loss_result_count": len(loss_results),
            "objective_present": objective_result is not None,
            "metric_result_count": len(metric_results),
        }
    )
    return diagnostics
