"""Structural contracts for batch-level methods."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from rphys.data import Batch

from .context import PredictionContext
from .output import MethodOutput
from .state import ParameterView, StateLoadResult, StateView

__all__ = ["Method", "StatefulMethod", "TrainableMethod"]


@runtime_checkable
class Method(Protocol):
    """Batch-level prediction or representation contract.

    Implementations consume a runtime ``Batch`` and return a patch-like
    ``MethodOutput``. The protocol does not require inheritance and does not
    define loss, metric, export, training, device, checkpoint, or split
    behavior.
    """

    def predict(
        self,
        batch: Batch,
        *,
        context: PredictionContext | None = None,
    ) -> MethodOutput:
        ...


@runtime_checkable
class StatefulMethod(Method, Protocol):
    """Method capability for inspectable backend-neutral state."""

    def state(self) -> StateView:
        ...

    def load_state(
        self,
        state: StateView,
        *,
        strict: bool = True,
    ) -> StateLoadResult:
        ...


@runtime_checkable
class TrainableMethod(StatefulMethod, Protocol):
    """Method capability for descriptive trainable parameter handles."""

    def parameters(self) -> tuple[ParameterView, ...]:
        ...
