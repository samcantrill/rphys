"""Validated schema identity names.

``SchemaName`` labels loaded interpretation, layout, units, coordinate meaning,
and version, for example ``video.rgb.v1``. It does not define a payload schema,
shape, unit conversion, coordinate frame, sample rate, codec, manifest entry,
Python dtype, tensor dtype, backend dtype, or config path.
"""

from __future__ import annotations

from typing import Self

from rphys.errors import InvalidSchemaNameError

from ._validation import contains_forbidden_separator, dotted_tokens

__all__ = ["SchemaName"]

_SCHEMA_NAME_EXPECTED = (
    "lowercase ASCII versioned schema name "
    "<family>.<layout_or_semantic>.v<int> with a positive version"
)


class SchemaName(str):
    """Validated versioned schema identity.

    Names use lowercase ASCII dotted tokens and end with ``v`` followed by a
    positive integer. The preceding tokens describe family and interpretation
    only; construction performs no payload validation or backend inspection.
    """

    def __new__(cls, value: str) -> Self:
        if not isinstance(value, str):
            raise InvalidSchemaNameError(
                "Schema names must be strings.",
                schema=value,
                expected=_SCHEMA_NAME_EXPECTED,
                actual=type(value).__name__,
            )

        tokens = dotted_tokens(value)
        if (
            tokens is None
            or len(tokens) < 3
            or contains_forbidden_separator(value, ("/", "#"))
        ):
            raise InvalidSchemaNameError(
                "Invalid schema-name grammar.",
                schema=value,
                expected=_SCHEMA_NAME_EXPECTED,
                actual=value,
            )

        version = tokens[-1]
        if not _is_positive_version(version):
            raise InvalidSchemaNameError(
                "Schema names require a positive version suffix.",
                schema=value,
                version=version,
                expected="v<int> where int is greater than zero",
                actual=version,
            )

        return super().__new__(cls, value)


def _is_positive_version(value: str) -> bool:
    if len(value) < 2 or value[0] != "v":
        return False
    digits = value[1:]
    if not digits.isdecimal() or int(digits) <= 0:
        return False
    return len(digits) == 1 or not digits.startswith("0")
