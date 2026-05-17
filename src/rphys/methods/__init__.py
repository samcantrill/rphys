"""Package home for batch-level prediction and representation methods."""

from rphys.data.output import BatchOutputFieldSpec, BatchOutputSpec, project_batch_fields

from .adapters import MethodInputAdapter, MethodInputSpec
from .context import PredictionContext
from .core import Method, StatefulMethod, TrainableMethod
from .state import ParameterView, StateEntry, StateLoadResult, StateView

__all__ = [
    "BatchOutputFieldSpec",
    "BatchOutputSpec",
    "Method",
    "MethodInputAdapter",
    "MethodInputSpec",
    "ParameterView",
    "PredictionContext",
    "StateEntry",
    "StateLoadResult",
    "StateView",
    "StatefulMethod",
    "TrainableMethod",
    "project_batch_fields",
]
