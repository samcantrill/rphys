"""Validated descriptive metadata keys.

``MetadataKey`` names context about a datasource, record, sample, split, group,
run, or global setting. Metadata keys do not describe loadable field payloads
and do not define missing-value policy, grouping algorithms, leakage checks,
split construction, or mandatory subject/record/sample semantics.
"""

from __future__ import annotations

from typing import Self

from rphys.errors import InvalidMetadataKeyError

from ._validation import contains_forbidden_separator, dotted_tokens

__all__ = [
    "MetadataKey",
    "GROUP",
    "RECORD_ID",
    "SAMPLE_ID",
    "SOURCE_ID",
    "SPLIT",
    "SUBJECT_ID",
]

_METADATA_KEY_EXPECTED = (
    "lowercase ASCII metadata key token or dotted metadata namespace"
)


class MetadataKey(str):
    """Validated descriptive metadata key.

    Metadata keys use lowercase ASCII tokens separated by dots. The constants
    group generic context keys such as ``source_id``, ``group``, and ``split``
    separately from rphys domain-context identifiers such as ``subject_id``.
    """

    def __new__(cls, value: str) -> Self:
        if not isinstance(value, str):
            raise InvalidMetadataKeyError(
                "Metadata keys must be strings.",
                metadata_key=value,
                expected=_METADATA_KEY_EXPECTED,
                actual=type(value).__name__,
            )

        tokens = dotted_tokens(value)
        if tokens is None or contains_forbidden_separator(value, ("/", "#")):
            raise InvalidMetadataKeyError(
                "Invalid metadata key grammar.",
                metadata_key=value,
                expected=_METADATA_KEY_EXPECTED,
                actual=value,
            )

        return super().__new__(cls, value)


# Generic/core metadata keys.
SOURCE_ID = MetadataKey("source_id")
GROUP = MetadataKey("group")
SPLIT = MetadataKey("split")

# rphys domain-context metadata keys.
SUBJECT_ID = MetadataKey("subject_id")
RECORD_ID = MetadataKey("record_id")
SAMPLE_ID = MetadataKey("sample_id")
