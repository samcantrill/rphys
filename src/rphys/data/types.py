"""Validated backend-agnostic data category labels.

``DataType`` values describe broad field categories such as ``video`` and
``signal``. They are not schema names, codec keys, Python dtypes, tensor dtypes,
backend dtypes, runtime payload inspectors, or shape/unit validators.
"""

from __future__ import annotations

from typing import Self

from rphys.errors import InvalidDataTypeError

from ._validation import contains_forbidden_separator, single_token

__all__ = [
    "DataType",
    "ANNOTATION",
    "EMBEDDING",
    "LABEL",
    "LANDMARKS",
    "MASK",
    "METADATA",
    "QUALITY",
    "SIGNAL",
    "TIMESTAMPS",
    "VIDEO",
]

_DATA_TYPE_EXPECTED = "single lowercase ASCII backend-agnostic data category"
_FORBIDDEN_BACKEND_DTYPES = frozenset(
    {
        "bool",
        "complex64",
        "complex128",
        "float16",
        "float32",
        "float64",
        "int8",
        "int16",
        "int32",
        "int64",
        "uint8",
        "uint16",
        "uint32",
        "uint64",
    }
)


class DataType(str):
    """Validated broad data category.

    Data types are lowercase ASCII single tokens. Construction allows downstream
    category labels but rejects values that look like paths, schema names,
    metadata selectors, or common backend dtype spellings.
    """

    def __new__(cls, value: str) -> Self:
        if not isinstance(value, str):
            raise InvalidDataTypeError(
                "Data types must be strings.",
                data_type=value,
                expected=_DATA_TYPE_EXPECTED,
                actual=type(value).__name__,
            )

        if (
            not single_token(value)
            or contains_forbidden_separator(value, (".", "/", "#"))
            or value in _FORBIDDEN_BACKEND_DTYPES
        ):
            raise InvalidDataTypeError(
                "Invalid data type grammar.",
                data_type=value,
                expected=_DATA_TYPE_EXPECTED,
                actual=value,
            )

        return super().__new__(cls, value)


VIDEO = DataType("video")
SIGNAL = DataType("signal")
TIMESTAMPS = DataType("timestamps")
LANDMARKS = DataType("landmarks")
MASK = DataType("mask")
EMBEDDING = DataType("embedding")
LABEL = DataType("label")
QUALITY = DataType("quality")
ANNOTATION = DataType("annotation")
METADATA = DataType("metadata")
