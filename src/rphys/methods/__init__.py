"""Package home for batch-level prediction and representation methods."""

from .adapters import (
    MethodInputAdapter,
    MethodInputSpec,
    MethodOutputAdapter,
    MethodOutputSpec,
)
from .context import PredictionContext
from .core import Method, StatefulMethod, TrainableMethod
from .output import MethodOutput, apply_method_output
from .state import ParameterView, StateEntry, StateLoadResult, StateView

__all__ = [
    "Method",
    "MethodInputAdapter",
    "MethodInputSpec",
    "MethodOutput",
    "MethodOutputAdapter",
    "MethodOutputSpec",
    "ParameterView",
    "PredictionContext",
    "StateEntry",
    "StateLoadResult",
    "StateView",
    "StatefulMethod",
    "TrainableMethod",
    "apply_method_output",
]
