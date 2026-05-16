"""Experimental training entrypoints reserved for downstream wrappers."""

from __future__ import annotations

from rphys.errors import RemotePhysTrainingError
from rphys.learning import Learner

from .core import Trainer, TrainingEngine
from .plan import TrainingPlan
from .results import TrainingResult

__all__ = ["run_train"]


def run_train(
    plan: TrainingPlan,
    learner: Learner,
    *,
    trainer: Trainer | None = None,
    engine: TrainingEngine | None = None,
) -> TrainingResult:
    """Run ``Trainer.fit`` through a thin experimental function.

    This helper exists for downstream wrappers that prefer a function call. It
    accepts already-assembled ``TrainingPlan`` and ``Learner`` objects and
    delegates to ``Trainer.fit``. It does not parse project config, build
    dataloaders, create artifacts, manage checkpoints, or define a workflow
    runtime.
    """

    if trainer is not None and engine is not None:
        raise RemotePhysTrainingError(
            "run_train accepts either trainer or engine, not both.",
            owner="run_train",
            field="trainer",
        )
    selected_trainer = trainer if trainer is not None else Trainer(engine=engine)
    return selected_trainer.fit(plan, learner)
