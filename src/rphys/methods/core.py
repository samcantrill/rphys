"""Structural contracts for batch-level methods."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from rphys.data import Batch

from .context import PredictionContext
from .output import MethodOutput

__all__ = ["Method"]


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
