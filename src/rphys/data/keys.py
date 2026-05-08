"""Logical field keys for in-memory remote-physiology data.

``DataKey`` is the stable address used by runtime samples, batches, dataset IO,
transforms, methods, and evaluation code to refer to a logical field. The base
contract validates syntax and reserved namespaces only; it does not maintain a
global registry of every possible field name.
"""

from __future__ import annotations

import re

from rphys.errors import RemotePhysDataError

__all__ = [
    "ANNOTATION_NAMESPACE",
    "BODY_NAMESPACE",
    "CAMERA_NAMESPACE",
    "CUSTOM_NAMESPACE",
    "DataKey",
    "FACE_NAMESPACE",
    "LABEL_NAMESPACE",
    "PREDICTION_NAMESPACE",
    "QUALITY_NAMESPACE",
    "SIGNAL_NAMESPACE",
    "STANDARD_NAMESPACES",
    "TIMESTAMPS_NAMESPACE",
    "VIDEO_NAMESPACE",
    "VIEW_NAMESPACE",
]


VIDEO_NAMESPACE = "video"
SIGNAL_NAMESPACE = "signal"
TIMESTAMPS_NAMESPACE = "timestamps"
FACE_NAMESPACE = "face"
BODY_NAMESPACE = "body"
CAMERA_NAMESPACE = "camera"
LABEL_NAMESPACE = "label"
PREDICTION_NAMESPACE = "prediction"
QUALITY_NAMESPACE = "quality"
ANNOTATION_NAMESPACE = "annotation"
VIEW_NAMESPACE = "view"
CUSTOM_NAMESPACE = "custom"

STANDARD_NAMESPACES = frozenset(
    {
        VIDEO_NAMESPACE,
        SIGNAL_NAMESPACE,
        TIMESTAMPS_NAMESPACE,
        FACE_NAMESPACE,
        BODY_NAMESPACE,
        CAMERA_NAMESPACE,
        LABEL_NAMESPACE,
        PREDICTION_NAMESPACE,
        QUALITY_NAMESPACE,
        ANNOTATION_NAMESPACE,
        VIEW_NAMESPACE,
        CUSTOM_NAMESPACE,
    }
)

_TOKEN_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class DataKey(str):
    """Validated string key for a logical runtime data field.

    API stability: Stable.

    Format:
        Keys are lowercase ASCII tokens separated by dots. Standard keys use a
        reserved namespace plus at least one semantic token, for example
        ``video.rgb`` or ``signal.bvp.reference``. Project-local extensions use
        ``custom.<project>.<field...>``.

    Scientific contract:
        A key identifies *what logical field* a payload represents. It does not
        encode shape, units, sampling rate, coordinate frame, temporal alignment,
        source URI, codec, or loaded value type. Those semantics belong to
        specialized specs, data objects, contracts, dataset IO, or transform
        docs when concrete code needs them.

    Equality, hashing, copying, and serialization:
        Equality and hashing follow ``str`` semantics. Copying may return the
        same immutable object or an equal object; callers must rely on the
        string value rather than object identity. The stable serialization token
        is the key string itself.

    Failure behavior:
        Invalid syntax, unknown non-custom namespaces, and incomplete custom
        keys raise ``RemotePhysDataError``.
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "DataKey":
        if not isinstance(value, str):
            raise RemotePhysDataError("DataKey value must be a string.")

        _validate_key(value)
        return str.__new__(cls, value)

    @property
    def parts(self) -> tuple[str, ...]:
        """Return the dot-separated key tokens."""

        return tuple(str(self).split("."))

    @property
    def namespace(self) -> str:
        """Return the reserved namespace token."""

        return self.parts[0]

    @property
    def is_custom(self) -> bool:
        """Return whether this key belongs to the custom extension namespace."""

        return self.namespace == CUSTOM_NAMESPACE


def _validate_key(value: str) -> None:
    if value == "":
        raise RemotePhysDataError("DataKey value must not be empty.")

    tokens = value.split(".")
    if any(token == "" for token in tokens):
        raise RemotePhysDataError(
            f"DataKey {value!r} must use non-empty dot-separated tokens."
        )

    invalid_tokens = [token for token in tokens if _TOKEN_PATTERN.fullmatch(token) is None]
    if invalid_tokens:
        raise RemotePhysDataError(
            f"DataKey {value!r} contains invalid token(s): {', '.join(invalid_tokens)}."
        )

    namespace = tokens[0]
    if namespace not in STANDARD_NAMESPACES:
        raise RemotePhysDataError(
            f"DataKey namespace {namespace!r} is not reserved by rphys; "
            f"use {CUSTOM_NAMESPACE!r} for project-local fields."
        )

    if namespace == CUSTOM_NAMESPACE:
        if len(tokens) < 3:
            raise RemotePhysDataError(
                "Custom DataKey values must use 'custom.<project>.<field...>'."
            )
        return

    if len(tokens) < 2:
        raise RemotePhysDataError(
            f"Standard DataKey {value!r} must include a namespace and semantic token."
        )
