"""Functional-kernel vocabulary for Stage 6 operation primitives."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeAlias

FunctionalKernel: TypeAlias = Callable[..., object]

__all__ = ["FunctionalKernel"]
