"""Dependency-light declarations for Stage 6 operations."""

from .contracts import (
    OperationContract,
    OperationMutationPolicy,
    OperationRole,
)
from .core import Operation
from .context import OperationContext, OperationResult
from .kernels import FunctionalKernel

__all__ = [
    "OperationRole",
    "OperationMutationPolicy",
    "OperationContract",
    "Operation",
    "OperationContext",
    "OperationResult",
    "FunctionalKernel",
]
