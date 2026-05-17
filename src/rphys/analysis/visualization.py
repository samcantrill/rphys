"""Visualization descriptors and operation-compatible field attachment."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from rphys.collections import CollectionItem
from rphys.data import Batch, FieldValue, Sample
from rphys.data.collections import SampleCollection
from rphys.data.locators import FieldLocator
from rphys.errors import (
    InvalidOperationContextError,
    InvalidOperationInputError,
    InvalidOperationResultError,
    OperationExecutionError,
    RemotePhysAnalysisError,
)
from rphys.ops import OperationContext, OperationContract, OperationResult, OperationRole, OperationStep

from ._validation import coerce_non_empty_string, coerce_optional_string, coerce_string_mapping

__all__ = [
    "VisualizationOperation",
    "VisualizationOutput",
    "attach_visualization_fields",
]

VisualizationBuilder = Callable[[object, OperationContext], Mapping[FieldLocator | str, "VisualizationOutput"]]


@dataclass(frozen=True, init=False, slots=True)
class VisualizationOutput:
    """Field-ready visualization descriptor with explicit codec/export hints.

    The descriptor is data only. It carries a lightweight payload and a codec
    key or hint for future export/render adapters, but it never imports plotting,
    image, dataframe, or video backends and never writes files.
    """

    kind: str
    codec: str
    payload: object
    title: str | None
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        kind: str,
        *,
        codec: str,
        payload: object,
        title: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        if payload is None:
            raise RemotePhysAnalysisError(
                "VisualizationOutput payload must be a field-ready descriptor value.",
                owner="VisualizationOutput",
                field="payload",
                expected="non-None descriptor payload",
                actual="None",
            )
        object.__setattr__(self, "kind", coerce_non_empty_string(kind, owner="VisualizationOutput", field="kind"))
        object.__setattr__(self, "codec", coerce_non_empty_string(codec, owner="VisualizationOutput", field="codec"))
        object.__setattr__(self, "payload", payload)
        object.__setattr__(self, "title", coerce_optional_string(title, owner="VisualizationOutput", field="title"))
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(metadata, owner="VisualizationOutput", field="metadata"),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(provenance, owner="VisualizationOutput", field="provenance"),
        )


class VisualizationOperation(OperationStep):
    """Attach visualization descriptor fields to runtime containers.

    Builders receive the input value and an ``OperationContext`` and must return
    a mapping from explicit output locators to ``VisualizationOutput`` values.
    ``Sample`` and ``Batch`` outputs are shallow copies. ``SampleCollection``
    outputs copy member samples and replicate descriptor fields with collection
    metadata that identifies the operation and field locators.
    """

    def __init__(
        self,
        builder: VisualizationBuilder,
        *,
        name: str = "visualization-operation",
    ) -> None:
        if not callable(builder):
            raise RemotePhysAnalysisError(
                "VisualizationOperation builder must be callable.",
                owner="VisualizationOperation",
                field="builder",
                expected="callable",
                actual=type(builder).__name__,
            )
        self._builder = builder
        self._name = coerce_non_empty_string(name, owner="VisualizationOperation", field="name")
        self._contract = OperationContract(
            input_type=(Sample, Batch, SampleCollection),
            output_type=(Sample, Batch, SampleCollection),
            failure_modes=(
                "visualization_builder_failed",
                "invalid_visualization_output",
                "visualization_field_conflict",
            ),
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def contract(self) -> OperationContract:
        return self._contract

    def run(self, input_value: object, context: OperationContext | None = None) -> OperationResult:
        if not isinstance(input_value, (Sample, Batch, SampleCollection)):
            raise InvalidOperationInputError(
                "VisualizationOperation input must be a Sample, Batch, or SampleCollection.",
                operation_name=self.name,
                field="input_value",
                expected="Sample | Batch | SampleCollection",
                actual=type(input_value).__name__,
            )
        execution_context = _coerce_operation_context(context, operation_name=self.name)
        try:
            builder_output = self._builder(input_value, execution_context)
        except Exception as exc:
            raise OperationExecutionError(
                "visualization builder failed during execution.",
                operation_name=self.name,
                role=self.contract.role.value,
                phase="run",
            ) from exc
        fields = _coerce_visualization_fields(builder_output)
        output = attach_visualization_fields(input_value, fields, operation_name=self.name)
        return OperationResult(
            output,
            operation_name=self.name,
            role=OperationRole.GENERIC,
            metadata={
                **execution_context.metadata,
                "visualization_fields": tuple(str(locator) for locator in fields),
            },
            provenance={**execution_context.provenance, "visualization_operation": self.name},
        )

    def __call__(self, input_value: object, context: OperationContext | None = None) -> OperationResult:
        return self.run(input_value, context=context)


def attach_visualization_fields(
    input_value: Sample | Batch | SampleCollection,
    fields: Mapping[FieldLocator | str, VisualizationOutput],
    *,
    operation_name: str = "attach-visualization-fields",
) -> Sample | Batch | SampleCollection:
    """Attach visualization descriptor fields without mutating the input."""

    resolved = _coerce_visualization_fields(fields)
    if isinstance(input_value, SampleCollection):
        entries = []
        for entry in input_value.entries:
            copied = entry.value.shallow_copy()
            _write_fields(copied, resolved, operation_name=operation_name)
            entries.append(
                CollectionItem(
                    copied,
                    metadata={
                        **entry.metadata,
                        "visualization_operation": operation_name,
                        "visualization_fields": tuple(str(locator) for locator in resolved),
                    },
                    provenance={**entry.provenance, "visualization_operation": operation_name},
                )
            )
        return SampleCollection(
            tuple(entries),
            metadata={
                **input_value.metadata,
                "visualization_operation": operation_name,
                "visualization_fields": tuple(str(locator) for locator in resolved),
            },
            provenance={**input_value.provenance, "visualization_operation": operation_name},
        )
    if isinstance(input_value, (Sample, Batch)):
        copied = input_value.shallow_copy()
        _write_fields(copied, resolved, operation_name=operation_name)
        return copied
    raise RemotePhysAnalysisError(
        "Visualization fields can only be attached to Sample, Batch, or SampleCollection.",
        owner="attach_visualization_fields",
        field="input_value",
        expected="Sample | Batch | SampleCollection",
        actual=type(input_value).__name__,
    )


def _coerce_visualization_fields(
    fields: Mapping[FieldLocator | str, VisualizationOutput],
) -> Mapping[FieldLocator, VisualizationOutput]:
    if not isinstance(fields, Mapping):
        raise InvalidOperationResultError(
            "visualization builder must return a mapping.",
            operation_name="VisualizationOperation",
            field="builder",
            expected="mapping of locator to VisualizationOutput",
            actual=type(fields).__name__,
        )
    resolved: dict[FieldLocator, VisualizationOutput] = {}
    for locator, output in fields.items():
        resolved_locator = locator if isinstance(locator, FieldLocator) else FieldLocator.parse(locator)
        if not isinstance(output, VisualizationOutput):
            raise InvalidOperationResultError(
                "visualization fields must contain VisualizationOutput values.",
                operation_name="VisualizationOperation",
                field="fields",
                locator=str(resolved_locator),
                expected="VisualizationOutput",
                actual=type(output).__name__,
            )
        resolved[resolved_locator] = output
    return MappingProxyType(resolved)


def _write_fields(
    container: Sample | Batch,
    fields: Mapping[FieldLocator, VisualizationOutput],
    *,
    operation_name: str,
) -> None:
    for locator, output in fields.items():
        if container.has(locator):
            raise RemotePhysAnalysisError(
                "Visualization operation output field conflicts with an existing field.",
                owner="VisualizationOperation",
                field="fields",
                locator=str(locator),
            )
        container.set_field(
            locator,
            FieldValue(
                output,
                metadata={
                    "analysis.kind": output.kind,
                    "analysis.codec": output.codec,
                    "analysis.operation": operation_name,
                    **output.metadata,
                },
            ),
        )


def _coerce_operation_context(context: OperationContext | None, *, operation_name: str) -> OperationContext:
    if context is None:
        return OperationContext()
    if isinstance(context, OperationContext):
        return context
    raise InvalidOperationContextError(
        "VisualizationOperation context must be None or OperationContext.",
        operation_name=operation_name,
        field="context",
        expected="OperationContext | None",
        actual=type(context).__name__,
    )


VisualizationOutput.__hash__ = None  # type: ignore[assignment]
