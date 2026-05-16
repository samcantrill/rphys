"""Learner step outputs and scalar boundary helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol, TypeAlias, runtime_checkable

from rphys.data import Batch, Sample
from rphys.errors import RemotePhysLearningError
from rphys.losses import LossTerm
from rphys.methods import MethodOutput
from rphys.metrics import MetricValue
from rphys.objectives import ObjectiveTerm

from ._validation import PrimitiveMapping, freeze_primitive_mapping

__all__ = [
    "BackwardableScalar",
    "StepOutput",
    "StepPrediction",
    "require_backwardable_scalar",
]

StepPrediction: TypeAlias = MethodOutput | Sample | Batch | None


@runtime_checkable
class BackwardableScalar(Protocol):
    """Minimal native scalar surface used by training engines.

    Stage 12 does not import torch, JAX, Lightning, or any other framework.
    Native execution can call ``backward()`` on an objective handle that already
    provides that method. Engines needing different behavior must supply an
    adapter-owned backward hook rather than widening the learner contract.
    """

    def backward(self) -> object:
        ...


@dataclass(frozen=True, init=False, slots=True)
class StepOutput:
    """Result of one learner step.

    Predictions remain opaque to the trainer. A supervised learner may return a
    ``MethodOutput`` patch, ``Sample``, ``Batch``, or ``None``; Stage 12 does
    not materialize predictions, uncollate samples, export fields, or run
    post-model batch pipelines in this record.
    """

    predictions: StepPrediction
    objective: BackwardableScalar | None
    loss_terms: tuple[LossTerm, ...]
    objective_terms: tuple[ObjectiveTerm, ...]
    metric_values: Mapping[str, MetricValue]
    diagnostics: PrimitiveMapping
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        *,
        predictions: StepPrediction = None,
        objective: object | None = None,
        loss_terms: Iterable[LossTerm] = (),
        objective_terms: Iterable[ObjectiveTerm] = (),
        metric_values: Mapping[str, MetricValue] | None = None,
        diagnostics: Mapping[object, object] | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(self, "predictions", _coerce_predictions(predictions))
        object.__setattr__(self, "objective", _coerce_objective(objective))
        object.__setattr__(self, "loss_terms", _coerce_loss_terms(loss_terms))
        object.__setattr__(
            self,
            "objective_terms",
            _coerce_objective_terms(objective_terms),
        )
        object.__setattr__(
            self,
            "metric_values",
            _coerce_metric_values(metric_values),
        )
        object.__setattr__(
            self,
            "diagnostics",
            freeze_primitive_mapping(
                diagnostics,
                owner="StepOutput",
                field="diagnostics",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(
                metadata,
                owner="StepOutput",
                field="metadata",
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(
                provenance,
                owner="StepOutput",
                field="provenance",
            ),
        )


def require_backwardable_scalar(value: object, *, field: str = "objective") -> BackwardableScalar:
    """Return ``value`` when native ``.backward()`` execution is supported."""

    if not isinstance(value, BackwardableScalar) or not callable(getattr(value, "backward", None)):
        raise RemotePhysLearningError(
            "Learner objective must expose a callable backward() method for native backward execution.",
            owner="BackwardableScalar",
            field=field,
            expected="object with backward()",
            actual=type(value).__name__,
        )
    return value


def _coerce_predictions(value: object) -> StepPrediction:
    if value is None or isinstance(value, (MethodOutput, Sample, Batch)):
        return value
    raise RemotePhysLearningError(
        "StepOutput predictions must be a MethodOutput, Sample, Batch, or None.",
        owner="StepOutput",
        field="predictions",
        expected="MethodOutput | Sample | Batch | None",
        actual=type(value).__name__,
    )


def _coerce_objective(value: object | None) -> BackwardableScalar | None:
    if value is None:
        return None
    return require_backwardable_scalar(value)


def _coerce_loss_terms(values: Iterable[LossTerm]) -> tuple[LossTerm, ...]:
    try:
        terms = tuple(values)
    except TypeError as exc:
        raise RemotePhysLearningError(
            "StepOutput loss_terms must be iterable.",
            owner="StepOutput",
            field="loss_terms",
            expected="iterable of LossTerm",
            actual=type(values).__name__,
        ) from exc
    for index, term in enumerate(terms):
        if not isinstance(term, LossTerm):
            raise RemotePhysLearningError(
                "StepOutput loss_terms must contain LossTerm records.",
                owner="StepOutput",
                field="loss_terms",
                index=index,
                actual=type(term).__name__,
            )
    return terms


def _coerce_objective_terms(values: Iterable[ObjectiveTerm]) -> tuple[ObjectiveTerm, ...]:
    try:
        terms = tuple(values)
    except TypeError as exc:
        raise RemotePhysLearningError(
            "StepOutput objective_terms must be iterable.",
            owner="StepOutput",
            field="objective_terms",
            expected="iterable of ObjectiveTerm",
            actual=type(values).__name__,
        ) from exc
    for index, term in enumerate(terms):
        if not isinstance(term, ObjectiveTerm):
            raise RemotePhysLearningError(
                "StepOutput objective_terms must contain ObjectiveTerm records.",
                owner="StepOutput",
                field="objective_terms",
                index=index,
                actual=type(term).__name__,
            )
    return terms


def _coerce_metric_values(
    values: Mapping[str, MetricValue] | None,
) -> Mapping[str, MetricValue]:
    if values is None:
        return MappingProxyType({})
    if not isinstance(values, Mapping):
        raise RemotePhysLearningError(
            "StepOutput metric_values must be a mapping.",
            owner="StepOutput",
            field="metric_values",
            expected="mapping[str, MetricValue]",
            actual=type(values).__name__,
        )
    coerced: dict[str, MetricValue] = {}
    for name, value in values.items():
        if not isinstance(name, str) or not name:
            raise RemotePhysLearningError(
                "StepOutput metric_values keys must be non-empty strings.",
                owner="StepOutput",
                field="metric_values",
                key=repr(name),
                actual=type(name).__name__,
            )
        if not isinstance(value, MetricValue):
            raise RemotePhysLearningError(
                "StepOutput metric_values must contain MetricValue records.",
                owner="StepOutput",
                field="metric_values",
                key=name,
                actual=type(value).__name__,
            )
        coerced[name] = value
    return MappingProxyType(coerced)


StepOutput.__hash__ = None  # type: ignore[assignment]
