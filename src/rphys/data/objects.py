"""Backend-free bases for loaded runtime data objects.

These bases provide explicit validation and declared tensor traversal hooks
without importing tensor, array, video, plotting, or dataset SDK packages. They
do not inspect arbitrary attributes, model sibling fields in a ``Sample``, or
perform scientific alignment checks across video, signal, landmark, or
timestamp payloads.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, ClassVar, Self

from rphys.errors import RemotePhysDataError

__all__ = ["CompositeDataObjectBase", "DataObjectBase"]


class DataObjectBase:
    """Minimal base for loaded payload objects with declared tensor leaves.

    Subclasses may declare local tensor-like leaves with ``tensor_fields``.
    Helpers return the object callers should keep using; Stage 2 does not
    promise immutable copies or in-place semantics beyond that return value.
    """

    tensor_fields: ClassVar[tuple[str, ...]] = ()

    def validate(self) -> Self:
        """Validate declared local structure and return ``self``."""

        for field_name in _declared_names(self, "tensor_fields"):
            _get_declared_attribute(self, field_name)
        return self

    def map_tensors(self, mapper: Callable[[object], object]) -> Self:
        """Apply ``mapper`` to each declared tensor leaf and return ``self``."""

        for field_name in _declared_names(self, "tensor_fields"):
            leaf = _get_declared_attribute(self, field_name)
            setattr(self, field_name, mapper(leaf))
        return self

    def to(self, *args: object, **kwargs: object) -> Self:
        """Call ``.to(*args, **kwargs)`` on declared tensor leaves."""

        return self.map_tensors(
            lambda leaf: _call_leaf_method(self, leaf, "to", args, kwargs)
        )

    def detach(self) -> Self:
        """Call ``.detach()`` on declared tensor leaves."""

        return self.map_tensors(
            lambda leaf: _call_leaf_method(self, leaf, "detach", (), {})
        )

    def pin_memory(self, *args: object, **kwargs: object) -> Self:
        """Call ``.pin_memory(*args, **kwargs)`` on declared tensor leaves."""

        return self.map_tensors(
            lambda leaf: _call_leaf_method(self, leaf, "pin_memory", args, kwargs)
        )


class CompositeDataObjectBase(DataObjectBase):
    """Loaded payload object composed from explicitly declared child objects.

    Subclasses declare local child data-object attributes with ``child_fields``.
    Validation and tensor traversal recurse only through those declared
    children; no parent ``Sample`` or sibling-field references are modeled.
    """

    child_fields: ClassVar[tuple[str, ...]] = ()

    def validate(self) -> Self:
        super().validate()
        for field_name, child in _iter_child_objects(self):
            try:
                child.validate()
            except Exception as exc:
                if isinstance(exc, RemotePhysDataError):
                    raise
                raise RemotePhysDataError(
                    "Declared child data object failed validation.",
                    object_type=type(self).__name__,
                    child_field=field_name,
                    child_type=type(child).__name__,
                ) from exc
        return self

    def map_tensors(self, mapper: Callable[[object], object]) -> Self:
        super().map_tensors(mapper)
        for field_name, child in _iter_child_objects(self):
            mapped_child = child.map_tensors(mapper)
            if not isinstance(mapped_child, DataObjectBase):
                raise RemotePhysDataError(
                    "Child data-object tensor mapping must return a data object.",
                    object_type=type(self).__name__,
                    child_field=field_name,
                    child_type=type(mapped_child).__name__,
                )
            setattr(self, field_name, mapped_child)
        return self


def _declared_names(instance: object, attribute: str) -> tuple[str, ...]:
    raw_names = getattr(type(instance), attribute, ())
    if isinstance(raw_names, str) or not isinstance(raw_names, Iterable):
        raise RemotePhysDataError(
            "Declared data-object fields must be an iterable of attribute names.",
            object_type=type(instance).__name__,
            declaration=attribute,
            actual=type(raw_names).__name__,
        )

    names = tuple(raw_names)
    for name in names:
        if not isinstance(name, str) or not name:
            raise RemotePhysDataError(
                "Declared data-object field names must be non-empty strings.",
                object_type=type(instance).__name__,
                declaration=attribute,
                actual=name,
            )
    return names


def _get_declared_attribute(instance: object, field_name: str) -> Any:
    if not hasattr(instance, field_name):
        raise RemotePhysDataError(
            "Declared data-object field is missing.",
            object_type=type(instance).__name__,
            field=field_name,
        )
    return getattr(instance, field_name)


def _iter_child_objects(
    instance: CompositeDataObjectBase,
) -> Iterable[tuple[str, DataObjectBase]]:
    for field_name in _declared_names(instance, "child_fields"):
        child = _get_declared_attribute(instance, field_name)
        if not isinstance(child, DataObjectBase):
            raise RemotePhysDataError(
                "Declared child data-object field must contain a DataObjectBase.",
                object_type=type(instance).__name__,
                field=field_name,
                actual=type(child).__name__,
            )
        yield field_name, child


def _call_leaf_method(
    owner: DataObjectBase,
    leaf: object,
    method_name: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
) -> object:
    method = getattr(leaf, method_name, None)
    if method is None or not callable(method):
        raise RemotePhysDataError(
            "Declared tensor leaf does not support the requested operation.",
            object_type=type(owner).__name__,
            leaf_type=type(leaf).__name__,
            operation=method_name,
        )
    return method(*args, **kwargs)
