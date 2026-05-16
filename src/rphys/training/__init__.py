"""Training plans, results, engines, and facade contracts."""

from .backend import NativeTrainingEngine
from .core import Trainer, TrainingEngine
from .plan import TrainingPlan
from .results import (
    ProfileSummary,
    TrainingEventSummary,
    TrainingMetricSummary,
    TrainingResult,
    TrainingStatus,
    TrainingStepSummary,
)

__all__ = [
    "ProfileSummary",
    "NativeTrainingEngine",
    "Trainer",
    "TrainingEngine",
    "TrainingEventSummary",
    "TrainingMetricSummary",
    "TrainingPlan",
    "TrainingResult",
    "TrainingStatus",
    "TrainingStepSummary",
]
