"""Supervised learner composition for methods, losses, objectives, and metrics."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from rphys.data import Batch, FieldValue
from rphys.errors import RemotePhysLearningError
from rphys.losses import Loss, LossContext, LossResult
from rphys.methods import Method, PredictionContext
from rphys.metrics import Metric, MetricContext, collect_metric_fields
from rphys.objectives import Objective, ObjectiveContext, ObjectiveResult

from .context import LoopContext
from .modes import LoopMode

__all__ = ["SupervisedLearner"]

_DEFAULT_OBJECTIVE_LOCATOR = "objectives/custom.training.total"


@dataclass(frozen=True, slots=True)
class SupervisedLearner:
    """Compose a batch-level method with optional supervised scoring.

    ``method.predict`` is always the source of predictions and must return a
    ``Batch``. Loss, objective, and metric records are converted to ordinary
    ``losses/*``, ``objectives/*``, and ``metrics/*`` fields on the returned
    batch. Training engines decide which fields to read through a
    ``TrainingPlan``-owned output spec.
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

    def step(self, batch: Batch, context: LoopContext) -> Batch:
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
        if not isinstance(predictions, Batch):
            raise RemotePhysLearningError(
                "SupervisedLearner method.predict must return a Batch.",
                owner="SupervisedLearner",
                field="method",
                expected="Batch",
                actual=type(predictions).__name__,
            )
        if context.mode is LoopMode.PREDICT:
            return predictions
        working_batch = predictions
        loss_results = self._evaluate_losses(working_batch, context)
        objective_result = self._evaluate_objective(loss_results, context)
        metric_results = self._evaluate_metrics(working_batch, context)

        output = predictions.shallow_copy()
        _add_loss_fields(output, loss_results)
        _add_objective_fields(output, objective_result)
        _add_metric_fields(output, metric_results)
        return output

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
    ) -> tuple[Mapping[object, FieldValue], ...]:
        results: list[Mapping[object, FieldValue]] = []
        for metric in self.metrics:
            fields = collect_metric_fields(
                metric,
                MetricContext(
                    metric.contract,
                    fields=fields,
                    metadata=_context_metadata(context),
                    provenance=context.provenance,
                ),
            )
            results.append(fields)
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


def _add_loss_fields(batch: Batch, results: Iterable[LossResult]) -> None:
    for result in results:
        for locator, field_value in result.fields.items():
            _set_new_field(batch, locator, field_value)
        for term in result.terms:
            _set_new_field(
                batch,
                f"losses/custom.training.{_field_key_suffix(term.name)}",
                FieldValue(
                    term.value,
                    metadata={
                        "name": term.name,
                        "backend": term.backend,
                        "reduction": term.reduction,
                        "differentiable": term.differentiable,
                    },
                ),
            )


def _add_objective_fields(batch: Batch, result: ObjectiveResult | None) -> None:
    if result is None:
        return
    for locator, field_value in result.fields.items():
        _set_new_field(batch, locator, field_value)
    _set_new_field(
        batch,
        _DEFAULT_OBJECTIVE_LOCATOR,
        FieldValue(
            result.total.value,
            metadata={
                "name": result.total.name,
                "backend": result.total.backend,
                "weight": result.total.weight,
                "reduction": result.total.reduction,
                "differentiable": result.total.differentiable,
            },
        ),
    )
    for term in result.terms:
        _set_new_field(
            batch,
            f"objectives/custom.training.{_field_key_suffix(term.name)}",
            FieldValue(
                term.value,
                metadata={
                    "name": term.name,
                    "backend": term.backend,
                    "weight": term.weight,
                    "reduction": term.reduction,
                    "differentiable": term.differentiable,
                },
            ),
        )


def _add_metric_fields(batch: Batch, results: Iterable[Mapping[object, FieldValue]]) -> None:
    for fields in results:
        for locator, field_value in fields.items():
            _set_new_field(batch, locator, field_value)


def _set_new_field(batch: Batch, locator: object, field_value: FieldValue) -> None:
    if batch.has(locator):  # type: ignore[arg-type]
        raise RemotePhysLearningError(
            "SupervisedLearner output field conflicts with an existing batch field.",
            owner="SupervisedLearner",
            locator=str(locator),
        )
    batch.set_field(locator, field_value)  # type: ignore[arg-type]


def _field_key_suffix(name: str) -> str:
    lowered = name.lower()
    chars = [char if "a" <= char <= "z" or "0" <= char <= "9" else "." for char in lowered]
    tokens = [token for token in "".join(chars).split(".") if token]
    return ".".join(tokens) if tokens else "value"
