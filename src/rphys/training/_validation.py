"""Private validation helpers for training records."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TypeAlias

from rphys.errors import RemotePhysTrainingError

PrimitiveValue: TypeAlias = str | int | float | bool | None
PrimitiveMapping: TypeAlias = Mapping[str, PrimitiveValue]

_PRIMITIVE_TYPES = (str, int, float, bool)


class FrozenMapping(dict[object, object]):
    """Dict-compatible immutable mapping for dataclass inspection."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._frozen = True

    def _blocked(self, *args: object, **kwargs: object) -> None:
        raise TypeError("FrozenMapping does not support mutation.")

    def __setitem__(self, key: object, value: object) -> None:
        if getattr(self, "_frozen", False):
            self._blocked()
        super().__setitem__(key, value)

    def __delitem__(self, key: object) -> None:
        self._blocked()

    def clear(self) -> None:  # type: ignore[override]
        self._blocked()

    def pop(self, key: object, default: object = None) -> object:  # type: ignore[override]
        self._blocked()

    def popitem(self) -> tuple[object, object]:  # type: ignore[override]
        self._blocked()

    def setdefault(self, key: object, default: object = None) -> object:  # type: ignore[override]
        self._blocked()

    def update(self, *args: object, **kwargs: object) -> None:  # type: ignore[override]
        self._blocked()

    def copy(self) -> "FrozenMapping":  # type: ignore[override]
        return type(self)(self)


def freeze_primitive_mapping(
    value: Mapping[object, object] | None,
    *,
    owner: str,
    field: str,
) -> PrimitiveMapping:
    if value is None:
        return FrozenMapping({})
    if not isinstance(value, Mapping):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            actual=type(value).__name__,
        )
    frozen: dict[str, PrimitiveValue] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise RemotePhysTrainingError(
                f"{owner} {field} keys must be non-empty strings.",
                owner=owner,
                field=field,
                key=repr(key),
                actual=type(key).__name__,
            )
        if item is not None and not isinstance(item, _PRIMITIVE_TYPES):
            raise RemotePhysTrainingError(
                f"{owner} {field} values must be primitive.",
                owner=owner,
                field=field,
                key=key,
                actual=type(item).__name__,
            )
        frozen[key] = item
    return FrozenMapping(frozen)


def coerce_optional_non_empty_string(
    value: str | None,
    *,
    owner: str,
    field: str,
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a non-empty string when provided.",
            owner=owner,
            field=field,
            expected="non-empty string | None",
            actual=type(value).__name__,
        )
    return value


def coerce_non_negative_int(
    value: int,
    *,
    owner: str,
    field: str,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a non-negative integer.",
            owner=owner,
            field=field,
            expected="non-negative integer",
            actual=type(value).__name__,
            value=value,
        )
    return value


def coerce_positive_int(
    value: int,
    *,
    owner: str,
    field: str,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a positive integer.",
            owner=owner,
            field=field,
            expected="positive integer",
            actual=type(value).__name__,
            value=value,
        )
    return value


def coerce_optional_positive_int(
    value: int | None,
    *,
    owner: str,
    field: str,
) -> int | None:
    if value is None:
        return None
    return coerce_positive_int(value, owner=owner, field=field)


def coerce_tuple(
    values: Iterable[object] | None,
    *,
    owner: str,
    field: str,
) -> tuple[object, ...] | None:
    if values is None:
        return None
    try:
        return tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be iterable when provided.",
            owner=owner,
            field=field,
            expected="iterable | None",
            actual=type(values).__name__,
        ) from exc
