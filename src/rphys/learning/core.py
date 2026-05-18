"""Structural learner contract."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from rphys.data import Batch

from .context import LoopContext

__all__ = ["Learner"]


@runtime_checkable
class Learner(Protocol):
    """Mode-aware scientific step semantics consumed by training engines.

    Learners interpret a prepared ``Batch`` under a ``LoopContext`` and return
    a ``Batch`` carrying prediction, loss, objective, metric, or diagnostic
    fields. They do not own optimizer steps, scheduler steps, checkpoint
    writers, dataloader construction, export/materialization, or framework
    lifecycle.
    """

    def step(self, batch: Batch, context: LoopContext) -> Batch:
        ...
