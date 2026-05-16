"""Training engine protocol and trainer facade."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from rphys.errors import RemotePhysTrainingError
from rphys.learning import Learner

from .plan import TrainingPlan
from .results import TrainingResult

__all__ = ["Trainer", "TrainingEngine"]


@runtime_checkable
class TrainingEngine(Protocol):
    """Loop owner selected by ``Trainer``.

    Engines receive the neutral ``TrainingPlan`` and ``Learner`` separately.
    The protocol is provisional and intentionally does not define a registry,
    config schema, logger framework, checkpoint writer, or external framework
    object model.
    """

    def fit(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        ...

    def validate(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        ...

    def test(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        ...

    def predict(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        ...


class Trainer:
    """RemotePhys facade that delegates loop control to a selected engine."""

    __slots__ = ("engine",)

    def __init__(self, *, engine: TrainingEngine | None = None) -> None:
        if engine is not None:
            _validate_engine(engine)
        self.engine = engine

    def fit(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        """Delegate fitting to the selected training engine."""

        return self._engine().fit(_require_plan(plan), learner)

    def validate(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        """Delegate validation to the selected training engine."""

        return self._engine().validate(_require_plan(plan), learner)

    def test(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        """Delegate testing to the selected training engine."""

        return self._engine().test(_require_plan(plan), learner)

    def predict(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        """Delegate prediction to the selected training engine."""

        return self._engine().predict(_require_plan(plan), learner)

    def _engine(self) -> TrainingEngine:
        if self.engine is None:
            raise RemotePhysTrainingError(
                "Trainer requires an explicit engine until NativeTrainingEngine is available.",
                owner="Trainer",
                field="engine",
                expected="TrainingEngine",
                actual="None",
            )
        return self.engine


def _require_plan(plan: object) -> TrainingPlan:
    if not isinstance(plan, TrainingPlan):
        raise RemotePhysTrainingError(
            "Trainer methods require a TrainingPlan.",
            owner="Trainer",
            field="plan",
            expected="TrainingPlan",
            actual=type(plan).__name__,
        )
    return plan


def _validate_engine(engine: object) -> None:
    for method_name in ("fit", "validate", "test", "predict"):
        method = getattr(engine, method_name, None)
        if not callable(method):
            raise RemotePhysTrainingError(
                "Training engine must implement fit, validate, test, and predict.",
                owner="Trainer",
                field="engine",
                method=method_name,
                expected="TrainingEngine",
                actual=type(engine).__name__,
            )
