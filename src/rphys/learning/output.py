"""Learner scalar boundary helpers."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from rphys.errors import RemotePhysLearningError

__all__ = [
    "BackwardableScalar",
    "require_backwardable_scalar",
]


@runtime_checkable
class BackwardableScalar(Protocol):
    """Minimal native scalar surface used by training engines.

    Stage 12 does not import torch, JAX, Lightning, or any other framework.
    Native execution can call ``backward()`` on an objective handle that already
    provides that method. Engines needing different behavior must supply an
    adapter-owned backward hook rather than widening the learner contract.
    """

    def backward(self) -> object:
        ...

def require_backwardable_scalar(value: object, *, field: str = "objective") -> BackwardableScalar:
    """Return ``value`` when native ``.backward()`` execution is supported."""

    if not isinstance(value, BackwardableScalar) or not callable(getattr(value, "backward", None)):
        raise RemotePhysLearningError(
            "Learner objective must expose a callable backward() method for native backward execution.",
            owner="BackwardableScalar",
            field=field,
            expected="object with backward()",
            actual=type(value).__name__,
        )
    return value
