"""Structural objective protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .context import ObjectiveContext
from .results import ObjectiveResult
from .specs import ObjectiveContract

__all__ = ["Objective"]


@runtime_checkable
class Objective(Protocol):
    """Backend-neutral objective behavior exposing an optimizer target."""

    @property
    def contract(self) -> ObjectiveContract:
        ...

    def __call__(self, context: ObjectiveContext) -> ObjectiveResult:
        ...
