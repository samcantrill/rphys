from __future__ import annotations

import pytest

from rphys.errors import InvalidSplitNameError
from rphys.data.splits import PREDICT, TEST, TRAIN, VALID, SplitName


def test_split_constants_are_validated_instances() -> None:
    assert TRAIN == "train"
    assert VALID == "valid"
    assert TEST == "test"
    assert PREDICT == "predict"
    assert all(isinstance(value, SplitName) for value in [TRAIN, VALID, TEST, PREDICT])


@pytest.mark.parametrize("value", ["calibration", "holdout_1", "fold2"])
def test_split_name_accepts_downstream_single_token_values(value: str) -> None:
    split = SplitName(value)

    assert split == value
    assert isinstance(split, str)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "Train",
        "valid split",
        "valid-split",
        "valid/test",
        "inputs/train",
        "train.valid",
        "train#source_id",
        "válid",
        "1train",
    ],
)
def test_split_name_rejects_invalid_values(value: str) -> None:
    with pytest.raises(InvalidSplitNameError) as exc_info:
        SplitName(value)

    assert exc_info.value.context["split"] == value
    assert "expected" in exc_info.value.context


def test_split_names_do_not_define_runtime_loop_behavior() -> None:
    assert not hasattr(SplitName, "build")
    assert not hasattr(SplitName, "loop_mode")
    assert not hasattr(SplitName, "route")
