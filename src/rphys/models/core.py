"""Structural contracts for lower-level computational models."""

from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

__all__ = ["Model"]

InputT = TypeVar("InputT", contravariant=True)
OutputT = TypeVar("OutputT", covariant=True)


@runtime_checkable
class Model(Protocol[InputT, OutputT]):
    """Callable lower-level computation below runtime ``Batch`` containers.

    The model protocol intentionally avoids datasource, loader, method,
    trainer, loss, metric, export, torch, and Lightning lifecycle semantics.
    Adapters and methods own any conversion between ``Batch`` fields and the
    backend-native values accepted by a model.
    """

    def __call__(self, inputs: InputT) -> OutputT:
        ...
