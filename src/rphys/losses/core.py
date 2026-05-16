"""Structural loss protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .context import LossContext
from .results import LossResult
from .specs import LossContract

__all__ = ["Loss"]


@runtime_checkable
class Loss(Protocol):
    """Backend-neutral loss behavior over declared fields."""

    @property
    def contract(self) -> LossContract:
        ...

    def __call__(self, context: LossContext) -> LossResult:
        ...
