"""Loop mode vocabulary for learner step semantics."""

from __future__ import annotations

from enum import StrEnum

from rphys.errors import RemotePhysLearningError

__all__ = ["LoopMode"]


class LoopMode(StrEnum):
    """Execution semantics requested from a learner step.

    A loop mode is not a datasource split, workflow stage, roadmap phase, or
    artifact stage. Use ``LoopContext.split`` for the data partition or usage
    label when that label is known.
    """

    TRAIN = "train"
    VALIDATE = "validate"
    TEST = "test"
    PREDICT = "predict"

    @classmethod
    def coerce(cls, value: "LoopMode | str") -> "LoopMode":
        """Return a ``LoopMode`` from an enum value or string label."""

        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysLearningError(
                    "Unsupported learner loop mode.",
                    owner="LoopMode",
                    field="mode",
                    expected=tuple(mode.value for mode in cls),
                    actual=value,
                ) from exc
        raise RemotePhysLearningError(
            "Loop mode must be a LoopMode or string.",
            owner="LoopMode",
            field="mode",
            expected="LoopMode | str",
            actual=type(value).__name__,
        )
