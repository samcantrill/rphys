"""Validated intrinsic field identities for remote-physiology data.

``DataKey`` names what a field intrinsically is, such as ``video.rgb`` or
``signal.bvp.reference``. It is not a runtime role, filesystem path, schema
name, codec key, metadata selector, config route, or field container lookup.
Construction is strict and fail-loud: names are not stripped, lowercased, or
otherwise normalized.
"""

from __future__ import annotations

from typing import Self

from rphys.errors import InvalidDataKeyError

from ._validation import contains_forbidden_separator, dotted_tokens

__all__ = ["DataKey", "RESERVED_NAMESPACES"]

RESERVED_NAMESPACES = frozenset(
    {
        "video",
        "signal",
        "timestamps",
        "face",
        "body",
        "camera",
        "landmarks",
        "mesh",
        "graph",
        "mask",
        "embedding",
        "label",
        "quality",
        "annotation",
        "metadata",
        "custom",
    }
)

_DATA_KEY_EXPECTED = (
    "lowercase ASCII dotted data key "
    "<namespace>.<semantic>[.<qualifier>...] using a reserved namespace, "
    "or custom.<project>.<semantic>[.<qualifier>...]"
)


class DataKey(str):
    """Validated intrinsic logical field identity.

    Valid keys use lowercase ASCII tokens separated by dots. Non-custom keys
    start with a reserved namespace and include at least one semantic token.
    Custom downstream keys use ``custom.<project>.<semantic>`` plus optional
    qualifiers. The object inherits normal ``str`` equality, hashing, and
    ordering behavior after construction.
    """

    def __new__(cls, value: str) -> Self:
        if not isinstance(value, str):
            raise InvalidDataKeyError(
                "Data keys must be strings.",
                key=value,
                expected=_DATA_KEY_EXPECTED,
                actual=type(value).__name__,
            )

        tokens = dotted_tokens(value)
        if tokens is None or contains_forbidden_separator(value, ("/", "#")):
            raise InvalidDataKeyError(
                "Invalid data key grammar.",
                key=value,
                expected=_DATA_KEY_EXPECTED,
                actual=value,
            )

        namespace = tokens[0]
        if namespace not in RESERVED_NAMESPACES:
            raise InvalidDataKeyError(
                "Data key namespace is not reserved.",
                key=value,
                namespace=namespace,
                expected=sorted(RESERVED_NAMESPACES),
                actual=namespace,
            )

        if namespace == "custom":
            if len(tokens) < 3:
                raise InvalidDataKeyError(
                    "Custom data keys require project and semantic tokens.",
                    key=value,
                    namespace=namespace,
                    expected="custom.<project>.<semantic>[.<qualifier>...]",
                    actual=value,
                )
        elif len(tokens) < 2:
            raise InvalidDataKeyError(
                "Data keys require a namespace and semantic token.",
                key=value,
                namespace=namespace,
                expected=_DATA_KEY_EXPECTED,
                actual=value,
            )

        return super().__new__(cls, value)
