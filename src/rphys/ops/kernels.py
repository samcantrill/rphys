"""Functional-kernel vocabulary for Stage 6 operation primitives.

Stage 6 treats kernels as simple callables with keyword context: ``kernel(
input_value, *, context=context)``. This vocabulary is intentionally generic and
does not include private helper call contracts or Stage 7/8/9 specialized call shapes.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeAlias

FunctionalKernel: TypeAlias = Callable[..., object]

__all__ = ["FunctionalKernel"]
