"""Dependency-light declarations for Stage 6 operations."""

from .contracts import (
    OperationContract,
    OperationMutationPolicy,
    OperationRole,
)
from .context import OperationContext, OperationResult
from .kernels import FunctionalKernel

__all__ = [
    "OperationRole",
    "OperationMutationPolicy",
    "OperationContract",
    "OperationContext",
    "OperationResult",
    "FunctionalKernel",
]
