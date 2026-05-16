"""Training plans, results, engines, and facade contracts."""

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
    "Trainer",
    "TrainingEngine",
    "TrainingEventSummary",
    "TrainingMetricSummary",
    "TrainingPlan",
    "TrainingResult",
    "TrainingStatus",
    "TrainingStepSummary",
]
