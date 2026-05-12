"""Validated split labels as partition or usage metadata.

``SplitName`` values label partitions or usage contexts such as ``train`` and
``predict``. They are not trainer loop modes, datasource split builders,
leakage policies, or prediction/evaluation dispatch rules.
"""

from __future__ import annotations

from typing import Self

from rphys.errors import InvalidSplitNameError

from ._validation import contains_forbidden_separator, single_token

__all__ = ["SplitName", "PREDICT", "TEST", "TRAIN", "VALID"]

_SPLIT_NAME_EXPECTED = "single lowercase ASCII split-name token"


class SplitName(str):
    """Validated split label.

    Split names are lowercase ASCII single tokens. Dotted metadata-style names,
    paths, and role-prefixed strings are rejected so split labels remain simple
    descriptive metadata rather than routes into trainer or datasource logic.
    """

    def __new__(cls, value: str) -> Self:
        if not isinstance(value, str):
            raise InvalidSplitNameError(
                "Split names must be strings.",
                split=value,
                expected=_SPLIT_NAME_EXPECTED,
                actual=type(value).__name__,
            )

        if not single_token(value) or contains_forbidden_separator(value, (".", "/", "#")):
            raise InvalidSplitNameError(
                "Invalid split-name grammar.",
                split=value,
                expected=_SPLIT_NAME_EXPECTED,
                actual=value,
            )

        return super().__new__(cls, value)


TRAIN = SplitName("train")
VALID = SplitName("valid")
TEST = SplitName("test")
PREDICT = SplitName("predict")
