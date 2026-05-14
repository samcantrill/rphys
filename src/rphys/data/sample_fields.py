"""Lazy runtime field handles backed by codec load results.

``SampleField`` is a ``FieldValue``-compatible object that can be stored
directly in a ``Sample``. Accessing the handle itself does not load payload
data; reading ``payload`` or calling ``load`` materializes the field once and
retains either the codec result or the failure for later inspection.
"""

from __future__ import annotations

import copy
from collections.abc import Callable
from enum import StrEnum

from rphys.errors import CodecOperationError
from rphys.io.codecs import CodecLoadResult, LoadContext

from .fields import FieldValue
from .metadata import MetadataKey
from .schemas import SchemaName

__all__ = ["SampleField", "SampleFieldState"]


class SampleFieldState(StrEnum):
    """Inspectable lazy field materialization state."""

    UNLOADED = "unloaded"
    LOADED = "loaded"
    FAILED = "failed"


class SampleField(FieldValue):
    """Lazy ``FieldValue``-compatible handle for one codec-loaded field.

    The handle keeps the datasource-neutral ``LoadContext`` and a private
    loader callable. It does not know about datasource records, index items,
    retry policy, caches, builders, or export behavior.
    """

    __slots__ = (
        "_load_context",
        "_loader",
        "_state",
        "_load_result",
        "_load_error",
    )

    def __init__(
        self,
        load_context: LoadContext,
        loader: Callable[[LoadContext], CodecLoadResult],
        *,
        collate_policy: object | None = None,
    ) -> None:
        if not isinstance(load_context, LoadContext):
            raise CodecOperationError(
                "SampleField load_context must be a LoadContext.",
                field="load_context",
                actual=type(load_context).__name__,
            )
        if not callable(loader):
            raise CodecOperationError(
                "SampleField loader must be callable.",
                field="loader",
                actual=type(loader).__name__,
            )

        self._load_context = load_context
        self._loader = loader
        self._state = SampleFieldState.UNLOADED
        self._load_result: CodecLoadResult | None = None
        self._load_error: BaseException | None = None
        self.schema = load_context.field_view.field_ref.schema
        self.metadata = {
            MetadataKey(key): value
            for key, value in load_context.field_view.field_ref.metadata.items()
        }
        self.collate_policy = collate_policy

    @property
    def payload(self) -> object:
        """Return the materialized payload, loading once on first demand."""

        return self.load().field_value.payload

    @payload.setter
    def payload(self, value: object) -> None:
        loaded = FieldValue(
            value,
            schema=self.schema,
            metadata=self.metadata,
            collate_policy=self.collate_policy,
        )
        self._retain_result(CodecLoadResult(loaded))

    @property
    def load_context(self) -> LoadContext:
        """Datasource-neutral context used by the loader."""

        return self._load_context

    @property
    def state(self) -> SampleFieldState:
        """Current lazy field state."""

        return self._state

    @property
    def loaded(self) -> bool:
        """Whether the payload has been materialized successfully."""

        return self._state is SampleFieldState.LOADED

    @property
    def failed(self) -> bool:
        """Whether loading failed and the error is retained."""

        return self._state is SampleFieldState.FAILED

    @property
    def load_result(self) -> CodecLoadResult | None:
        """Retained codec load result, if loading succeeded."""

        return self._load_result

    @property
    def load_error(self) -> BaseException | None:
        """Retained loading error, if loading failed."""

        return self._load_error

    @property
    def field_value(self) -> FieldValue | None:
        """Loaded field value, if materialization has succeeded."""

        return self._load_result.field_value if self._load_result is not None else None

    def load(self) -> CodecLoadResult:
        """Materialize the field once and return the retained codec result."""

        if self._state is SampleFieldState.LOADED:
            assert self._load_result is not None
            return self._load_result
        if self._state is SampleFieldState.FAILED:
            assert self._load_error is not None
            raise self._load_error

        try:
            result = self._loader(self._load_context)
        except BaseException as exc:
            self._state = SampleFieldState.FAILED
            self._load_error = exc
            raise

        if not isinstance(result, CodecLoadResult):
            error = CodecOperationError(
                "SampleField loader must return a CodecLoadResult.",
                actual=type(result).__name__,
            )
            self._state = SampleFieldState.FAILED
            self._load_error = error
            raise error

        self._retain_result(result)
        return result

    def eager_load(self) -> CodecLoadResult:
        """Materialize through the same state machine as ``payload`` access."""

        return self.load()

    def __copy__(self) -> "SampleField":
        clone = type(self)(
            self._load_context,
            self._loader,
            collate_policy=self.collate_policy,
        )
        clone.schema = self.schema
        clone.metadata = dict(self.metadata)
        clone._state = self._state
        clone._load_result = self._load_result
        clone._load_error = self._load_error
        return clone

    def __deepcopy__(self, memo: dict[int, object]) -> "SampleField":
        clone = type(self)(
            self._load_context,
            self._loader,
            collate_policy=copy.deepcopy(self.collate_policy, memo),
        )
        clone.schema = copy.deepcopy(self.schema, memo)
        clone.metadata = copy.deepcopy(self.metadata, memo)
        clone._state = self._state
        clone._load_result = (
            CodecLoadResult(
                copy.deepcopy(self._load_result.field_value, memo),
                metadata=dict(self._load_result.metadata),
            )
            if self._load_result is not None
            else None
        )
        clone._load_error = self._load_error
        return clone

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"state={self._state.value!r}, "
            f"schema={self.schema!r}, "
            f"metadata={self.metadata!r}, "
            f"collate_policy={self.collate_policy!r})"
        )

    def _retain_result(self, result: CodecLoadResult) -> None:
        field_value = result.field_value
        self._load_result = result
        self._load_error = None
        self._state = SampleFieldState.LOADED
        self.schema = field_value.schema
        self.metadata = dict(field_value.metadata)
        self.collate_policy = field_value.collate_policy
