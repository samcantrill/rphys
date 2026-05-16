"""Prediction-time context for batch-level methods."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from ._records import freeze_primitive_mapping

__all__ = ["PredictionContext"]


@dataclass(frozen=True, slots=True)
class PredictionContext:
    """Generic primitive metadata/provenance supplied to ``Method.predict``.

    The context is intentionally small: it records only caller-owned primitive
    metadata and provenance, copied into read-only mappings at construction.
    It does not define first-class sample IDs, batch IDs, split labels,
    trainer modes, dtype/device choices, checkpoint handles, or export paths.
    """

    metadata: Mapping[str, object] | None = field(default_factory=dict)
    provenance: Mapping[str, object] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(self.metadata, field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(self.provenance, field="provenance"),
        )
