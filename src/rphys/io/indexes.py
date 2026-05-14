"""Field-native lazy index descriptors.

``TemporalIndexSlice`` stores half-open ``[start, stop)`` integer offsets in a
field's own native sample/index space. Equal numeric slices on different fields
do not imply temporal alignment, resampling, padding, or seconds conversion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from rphys.errors import InvalidFieldIndexError, UnsupportedFieldIndexError

from ._primitives import require_exact_keys, require_mapping

__all__ = ["FieldIndex", "TemporalIndexSlice"]

_TEMPORAL_INDEX_SLICE = "temporal_index_slice"


class FieldIndex:
    """Base class for Stage 3 field-native index descriptors."""

    def __init__(self) -> None:
        if type(self) is FieldIndex:
            raise TypeError("FieldIndex is a base class and cannot be instantiated.")

    def to_dict(self) -> dict[str, object]:
        """Serialize the supported Stage 3 index descriptor."""

        raise NotImplementedError


@dataclass(frozen=True, init=False, slots=True)
class TemporalIndexSlice(FieldIndex):
    """Half-open field-native temporal index slice.

    Bounds are non-negative integer indices in the referenced field's own
    native index space. ``step`` is accepted as descriptor data; Stage 3 does
    not promise that every future codec can materialize non-unit steps.
    """

    start: int
    stop: int
    step: int

    def __init__(self, start: int, stop: int, step: int = 1) -> None:
        start_value = _non_negative_int(start, field="start")
        stop_value = _non_negative_int(stop, field="stop")
        step_value = _positive_int(step, field="step")
        if stop_value < start_value:
            raise InvalidFieldIndexError(
                "TemporalIndexSlice stop must be greater than or equal to start.",
                start=start_value,
                stop=stop_value,
            )

        object.__setattr__(self, "start", start_value)
        object.__setattr__(self, "stop", stop_value)
        object.__setattr__(self, "step", step_value)

    def to_dict(self) -> dict[str, object]:
        """Serialize with a Stage 3 type tag and no schema-version envelope."""

        return {
            "type": _TEMPORAL_INDEX_SLICE,
            "start": self.start,
            "stop": self.stop,
            "step": self.step,
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct a temporal slice from ``to_dict`` output."""

        data = require_mapping(
            value,
            error_type=InvalidFieldIndexError,
            field="field_index",
        )
        require_exact_keys(
            data,
            {"type", "start", "stop", "step"},
            error_type=InvalidFieldIndexError,
            descriptor="TemporalIndexSlice",
        )
        if data["type"] != _TEMPORAL_INDEX_SLICE:
            raise UnsupportedFieldIndexError(
                "Unsupported Stage 3 field index type tag.",
                type=data["type"],
                supported=[_TEMPORAL_INDEX_SLICE],
            )
        return cls(
            data["start"],  # type: ignore[arg-type]
            data["stop"],  # type: ignore[arg-type]
            data["step"],  # type: ignore[arg-type]
        )


TemporalIndexSlice.__hash__ = None  # type: ignore[assignment]


def _field_index_from_dict(value: object) -> FieldIndex:
    data = require_mapping(
        value,
        error_type=InvalidFieldIndexError,
        field="field_index",
    )
    type_tag = data.get("type")
    if type_tag != _TEMPORAL_INDEX_SLICE:
        raise UnsupportedFieldIndexError(
            "Unsupported Stage 3 field index type tag.",
            type=type_tag,
            supported=[_TEMPORAL_INDEX_SLICE],
        )
    return TemporalIndexSlice.from_dict(data)


def _non_negative_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise InvalidFieldIndexError(
            "TemporalIndexSlice bounds must be non-negative integers.",
            field=field,
            actual=type(value).__name__,
            value=value,
        )
    return value


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise InvalidFieldIndexError(
            "TemporalIndexSlice step must be a positive integer.",
            field=field,
            actual=type(value).__name__,
            value=value,
        )
    return value
