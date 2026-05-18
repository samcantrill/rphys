"""Training plans, results, engines, and facade contracts."""

from .backend import NativeTrainingEngine
from .core import Trainer, TrainingEngine
from .events import (
    TrainingCallback,
    TrainingEvent,
    TrainingEventLog,
    TrainingEventPhase,
    TrainingEventSink,
    emit_training_event,
)
from .experimental import run_train
from .plan import TrainingOutputSpec, TrainingPlan
from .profiling import (
    ProfileSpanSummary,
    TrainingProfile,
    TrainingProfileRecorder,
    TrainingProfiler,
    UnavailableProfileProbe,
)
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
    "ProfileSpanSummary",
    "TrainingEventLog",
    "NativeTrainingEngine",
    "Trainer",
    "TrainingCallback",
    "TrainingEngine",
    "TrainingEvent",
    "TrainingEventPhase",
    "TrainingEventSummary",
    "TrainingEventSink",
    "TrainingMetricSummary",
    "TrainingOutputSpec",
    "TrainingPlan",
    "TrainingProfiler",
    "TrainingProfile",
    "TrainingProfileRecorder",
    "TrainingResult",
    "TrainingStatus",
    "TrainingStepSummary",
    "UnavailableProfileProbe",
    "emit_training_event",
    "run_train",
]
