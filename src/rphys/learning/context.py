"""Learner step context records."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ._validation import (
    PrimitiveMapping,
    coerce_non_negative_index,
    coerce_optional_label,
    freeze_primitive_mapping,
)
from .modes import LoopMode

__all__ = ["LoopContext"]


@dataclass(frozen=True, init=False, slots=True)
class LoopContext:
    """Immutable context supplied to ``Learner.step``.

    ``mode`` describes step semantics such as training or prediction.
    ``split`` is a separate data partition or usage label, for example
    ``"train"``, ``"valid"``, or ``"heldout-subjects"``. Index fields are
    optional zero-based loop counters; they preserve epoch, step, and batch
    position without implying a datasource identity.
    """

    mode: LoopMode
    split: str | None
    epoch_index: int | None
    step_index: int | None
    batch_index: int | None
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        mode: LoopMode | str,
        *,
        split: str | None = None,
        epoch_index: int | None = None,
        step_index: int | None = None,
        batch_index: int | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(self, "mode", LoopMode.coerce(mode))
        object.__setattr__(
            self,
            "split",
            coerce_optional_label(split, owner="LoopContext", field="split"),
        )
        object.__setattr__(
            self,
            "epoch_index",
            coerce_non_negative_index(
                epoch_index,
                owner="LoopContext",
                field="epoch_index",
            ),
        )
        object.__setattr__(
            self,
            "step_index",
            coerce_non_negative_index(
                step_index,
                owner="LoopContext",
                field="step_index",
            ),
        )
        object.__setattr__(
            self,
            "batch_index",
            coerce_non_negative_index(
                batch_index,
                owner="LoopContext",
                field="batch_index",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(
                metadata,
                owner="LoopContext",
                field="metadata",
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(
                provenance,
                owner="LoopContext",
                field="provenance",
            ),
        )


LoopContext.__hash__ = None  # type: ignore[assignment]
