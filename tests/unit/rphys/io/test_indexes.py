from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.errors import InvalidFieldIndexError, UnsupportedFieldIndexError
from rphys.io.indexes import FieldIndex, TemporalIndexSlice


def test_temporal_index_slice_is_field_native_half_open_descriptor() -> None:
    index = TemporalIndexSlice(0, 10, step=2)

    assert isinstance(index, FieldIndex)
    assert index.start == 0
    assert index.stop == 10
    assert index.step == 2
    assert not hasattr(index, "seconds")
    assert not hasattr(index, "sample_rate")
    assert not hasattr(index, "alignment")


def test_temporal_index_slice_accepts_empty_half_open_slice() -> None:
    index = TemporalIndexSlice(5, 5)

    assert index.start == index.stop == 5
    assert index.step == 1


def test_temporal_index_slice_has_value_equality_without_public_hash_contract() -> None:
    index = TemporalIndexSlice(1, 9, 3)

    assert index == TemporalIndexSlice(1, 9, 3)
    with pytest.raises(FrozenInstanceError):
        index.start = 2  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(index)


def test_temporal_index_slice_round_trips_through_primitive_dict() -> None:
    index = TemporalIndexSlice(4, 40, 4)
    serialized = index.to_dict()

    assert serialized == {
        "type": "temporal_index_slice",
        "start": 4,
        "stop": 40,
        "step": 4,
    }
    assert TemporalIndexSlice.from_dict(serialized) == index
    assert "schema_version" not in serialized


@pytest.mark.parametrize(
    "args",
    [
        (-1, 10, 1),
        (0, -1, 1),
        (10, 1, 1),
        (0, 10, 0),
        (0, 10, -1),
        (True, 10, 1),
        (0, False, 1),
        (0, 10, True),
    ],
)
def test_temporal_index_slice_rejects_invalid_bounds(args: tuple[object, object, object]) -> None:
    with pytest.raises(InvalidFieldIndexError):
        TemporalIndexSlice(*args)  # type: ignore[arg-type]


def test_temporal_index_slice_from_dict_rejects_unknown_or_invalid_tags() -> None:
    with pytest.raises(UnsupportedFieldIndexError):
        TemporalIndexSlice.from_dict(
            {"type": "seconds", "start": 0, "stop": 1, "step": 1}
        )
    with pytest.raises(InvalidFieldIndexError):
        TemporalIndexSlice.from_dict({"type": "temporal_index_slice", "start": 0})


def test_field_index_base_class_is_not_a_public_registry_or_factory() -> None:
    with pytest.raises(TypeError):
        FieldIndex()

    assert not hasattr(FieldIndex, "registry")
    assert not hasattr(FieldIndex, "register")
    assert not hasattr(FieldIndex, "from_dict")
