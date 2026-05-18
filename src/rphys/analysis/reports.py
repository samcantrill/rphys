"""In-memory report, table, and diagnostic render records."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol, TypeAlias, runtime_checkable

from rphys.errors import (
    InvalidOperationContextError,
    InvalidOperationResultError,
    OperationExecutionError,
    RemotePhysAnalysisError,
)
from rphys.metrics import MetricValue
from rphys.ops import OperationContext, OperationContract, OperationResult, OperationRole, OperationStep

from ._validation import (
    coerce_non_empty_string,
    coerce_optional_string,
    coerce_string_mapping,
    coerce_string_tuple,
)
from .visualization import VisualizationOutput

__all__ = [
    "DiagnosticRenderOutput",
    "DiagnosticRenderer",
    "Report",
    "ReportCell",
    "ReportOperation",
    "ReportRow",
    "ReportSection",
    "ReportTable",
]

ReportBuilder = Callable[[object, OperationContext], "Report | ReportTable"]
CellInput: TypeAlias = "ReportCell | VisualizationOutput | MetricValue | str | int | float | bool | None"


@dataclass(frozen=True, init=False, slots=True)
class ReportCell:
    """One primitive or descriptor-backed report table cell."""

    value: object
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        value: CellInput,
        *,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        if isinstance(value, ReportCell):
            object.__setattr__(self, "value", value.value)
            object.__setattr__(
                self,
                "metadata",
                value.metadata if metadata is None else coerce_string_mapping(metadata, owner="ReportCell", field="metadata"),
            )
            object.__setattr__(
                self,
                "provenance",
                value.provenance
                if provenance is None
                else coerce_string_mapping(provenance, owner="ReportCell", field="provenance"),
            )
            return
        if not _is_supported_cell_value(value):
            raise RemotePhysAnalysisError(
                "ReportCell value must be primitive, MetricValue, or VisualizationOutput.",
                owner="ReportCell",
                field="value",
                expected="primitive | MetricValue | VisualizationOutput | None",
                actual=type(value).__name__,
            )
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "metadata", coerce_string_mapping(metadata, owner="ReportCell", field="metadata"))
        object.__setattr__(self, "provenance", coerce_string_mapping(provenance, owner="ReportCell", field="provenance"))


@dataclass(frozen=True, init=False, slots=True)
class ReportRow:
    """One ordered report row keyed by table column names."""

    cells: Mapping[str, ReportCell]
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        cells: Mapping[object, CellInput],
        *,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        if not isinstance(cells, Mapping):
            raise RemotePhysAnalysisError(
                "ReportRow cells must be a mapping.",
                owner="ReportRow",
                field="cells",
                expected="mapping of column name to report cell",
                actual=type(cells).__name__,
            )
        resolved: dict[str, ReportCell] = {}
        for key, value in cells.items():
            column = coerce_non_empty_string(key, owner="ReportRow", field="cells")
            if column in resolved:
                raise RemotePhysAnalysisError(
                    "ReportRow cells must not repeat columns.",
                    owner="ReportRow",
                    field="cells",
                    duplicate=column,
                )
            resolved[column] = value if isinstance(value, ReportCell) else ReportCell(value)
        object.__setattr__(self, "cells", MappingProxyType(resolved))
        object.__setattr__(self, "metadata", coerce_string_mapping(metadata, owner="ReportRow", field="metadata"))
        object.__setattr__(self, "provenance", coerce_string_mapping(provenance, owner="ReportRow", field="provenance"))


@dataclass(frozen=True, init=False, slots=True)
class ReportTable:
    """In-memory table with validated primitive/descriptor cells."""

    name: str
    columns: tuple[str, ...]
    rows: tuple[ReportRow, ...]
    metadata: Mapping[str, object]
    diagnostics: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        *,
        columns: Iterable[str],
        rows: Iterable[ReportRow | Mapping[object, CellInput]],
        metadata: Mapping[object, object] | None = None,
        diagnostics: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        resolved_columns = coerce_string_tuple(columns, owner="ReportTable", field="columns")
        if not resolved_columns:
            raise RemotePhysAnalysisError(
                "ReportTable columns must not be empty.",
                owner="ReportTable",
                field="columns",
                expected="non-empty columns",
                actual="empty",
            )
        resolved_rows = tuple(row if isinstance(row, ReportRow) else ReportRow(row) for row in rows)
        for index, row in enumerate(resolved_rows):
            _validate_row_columns(row, resolved_columns, index=index)
        object.__setattr__(self, "name", coerce_non_empty_string(name, owner="ReportTable", field="name"))
        object.__setattr__(self, "columns", resolved_columns)
        object.__setattr__(self, "rows", resolved_rows)
        object.__setattr__(self, "metadata", coerce_string_mapping(metadata, owner="ReportTable", field="metadata"))
        object.__setattr__(
            self,
            "diagnostics",
            coerce_string_mapping(diagnostics, owner="ReportTable", field="diagnostics"),
        )
        object.__setattr__(self, "provenance", coerce_string_mapping(provenance, owner="ReportTable", field="provenance"))


@dataclass(frozen=True, init=False, slots=True)
class ReportSection:
    """Named in-memory report section containing tables."""

    title: str
    tables: tuple[ReportTable, ...]
    text: str | None
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        title: str,
        *,
        tables: Iterable[ReportTable] = (),
        text: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        resolved_tables = tuple(tables)
        for index, table in enumerate(resolved_tables):
            if not isinstance(table, ReportTable):
                raise RemotePhysAnalysisError(
                    "ReportSection tables must contain ReportTable records.",
                    owner="ReportSection",
                    field="tables",
                    index=index,
                    expected="ReportTable",
                    actual=type(table).__name__,
                )
        object.__setattr__(self, "title", coerce_non_empty_string(title, owner="ReportSection", field="title"))
        object.__setattr__(self, "tables", resolved_tables)
        object.__setattr__(self, "text", coerce_optional_string(text, owner="ReportSection", field="text"))
        object.__setattr__(self, "metadata", coerce_string_mapping(metadata, owner="ReportSection", field="metadata"))
        object.__setattr__(self, "provenance", coerce_string_mapping(provenance, owner="ReportSection", field="provenance"))


@dataclass(frozen=True, init=False, slots=True)
class Report:
    """Side-effect-free structured report record."""

    title: str
    sections: tuple[ReportSection, ...]
    metadata: Mapping[str, object]
    diagnostics: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        title: str,
        *,
        sections: Iterable[ReportSection],
        metadata: Mapping[object, object] | None = None,
        diagnostics: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        resolved_sections = tuple(sections)
        for index, section in enumerate(resolved_sections):
            if not isinstance(section, ReportSection):
                raise RemotePhysAnalysisError(
                    "Report sections must contain ReportSection records.",
                    owner="Report",
                    field="sections",
                    index=index,
                    expected="ReportSection",
                    actual=type(section).__name__,
                )
        object.__setattr__(self, "title", coerce_non_empty_string(title, owner="Report", field="title"))
        object.__setattr__(self, "sections", resolved_sections)
        object.__setattr__(self, "metadata", coerce_string_mapping(metadata, owner="Report", field="metadata"))
        object.__setattr__(self, "diagnostics", coerce_string_mapping(diagnostics, owner="Report", field="diagnostics"))
        object.__setattr__(self, "provenance", coerce_string_mapping(provenance, owner="Report", field="provenance"))


class ReportOperation(OperationStep):
    """Operation-compatible builder returning an in-memory report or table."""

    def __init__(self, builder: ReportBuilder, *, name: str = "report-operation") -> None:
        if not callable(builder):
            raise RemotePhysAnalysisError(
                "ReportOperation builder must be callable.",
                owner="ReportOperation",
                field="builder",
                expected="callable",
                actual=type(builder).__name__,
            )
        self._builder = builder
        self._name = coerce_non_empty_string(name, owner="ReportOperation", field="name")
        self._contract = OperationContract(
            output_type=(Report, ReportTable),
            failure_modes=("report_builder_failed", "invalid_report_output"),
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def contract(self) -> OperationContract:
        return self._contract

    def run(self, input_value: object, context: OperationContext | None = None) -> OperationResult:
        execution_context = _coerce_operation_context(context, operation_name=self.name)
        try:
            output = self._builder(input_value, execution_context)
        except Exception as exc:
            raise OperationExecutionError(
                "report builder failed during execution.",
                operation_name=self.name,
                role=self.contract.role.value,
                phase="run",
            ) from exc
        if not isinstance(output, (Report, ReportTable)):
            raise InvalidOperationResultError(
                "ReportOperation builder must return a Report or ReportTable.",
                operation_name=self.name,
                field="output",
                expected="Report | ReportTable",
                actual=type(output).__name__,
            )
        return OperationResult(
            output,
            operation_name=self.name,
            role=OperationRole.GENERIC,
            metadata={**execution_context.metadata, "report_output": type(output).__name__},
            provenance={**execution_context.provenance, "report_operation": self.name},
        )

    def __call__(self, input_value: object, context: OperationContext | None = None) -> OperationResult:
        return self.run(input_value, context=context)


@dataclass(frozen=True, init=False, slots=True)
class DiagnosticRenderOutput:
    """Diagnostic renderer output as data, not files or backend calls."""

    renderer: str
    output: Report | ReportTable | VisualizationOutput
    metadata: Mapping[str, object]
    diagnostics: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        renderer: str,
        output: Report | ReportTable | VisualizationOutput,
        *,
        metadata: Mapping[object, object] | None = None,
        diagnostics: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        if not isinstance(output, (Report, ReportTable, VisualizationOutput)):
            raise RemotePhysAnalysisError(
                "DiagnosticRenderOutput output must be report or visualization data.",
                owner="DiagnosticRenderOutput",
                field="output",
                expected="Report | ReportTable | VisualizationOutput",
                actual=type(output).__name__,
            )
        object.__setattr__(self, "renderer", coerce_non_empty_string(renderer, owner="DiagnosticRenderOutput", field="renderer"))
        object.__setattr__(self, "output", output)
        object.__setattr__(self, "metadata", coerce_string_mapping(metadata, owner="DiagnosticRenderOutput", field="metadata"))
        object.__setattr__(
            self,
            "diagnostics",
            coerce_string_mapping(diagnostics, owner="DiagnosticRenderOutput", field="diagnostics"),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(provenance, owner="DiagnosticRenderOutput", field="provenance"),
        )


@runtime_checkable
class DiagnosticRenderer(Protocol):
    """Structural renderer that returns diagnostic output records only."""

    def __call__(
        self,
        value: Report | ReportTable | VisualizationOutput,
        context: OperationContext | None = None,
    ) -> DiagnosticRenderOutput:
        ...


def _validate_row_columns(row: ReportRow, columns: tuple[str, ...], *, index: int) -> None:
    row_columns = tuple(row.cells)
    missing = tuple(column for column in columns if column not in row.cells)
    extra = tuple(column for column in row_columns if column not in columns)
    if missing or extra:
        raise RemotePhysAnalysisError(
            "ReportTable row columns must match table columns.",
            owner="ReportTable",
            field="rows",
            index=index,
            missing=missing,
            extra=extra,
        )


def _is_supported_cell_value(value: object) -> bool:
    return value is None or isinstance(value, (str, int, float, bool, MetricValue, VisualizationOutput))


def _coerce_operation_context(context: OperationContext | None, *, operation_name: str) -> OperationContext:
    if context is None:
        return OperationContext()
    if isinstance(context, OperationContext):
        return context
    raise InvalidOperationContextError(
        "ReportOperation context must be None or OperationContext.",
        operation_name=operation_name,
        field="context",
        expected="OperationContext | None",
        actual=type(context).__name__,
    )


ReportCell.__hash__ = None  # type: ignore[assignment]
ReportRow.__hash__ = None  # type: ignore[assignment]
ReportTable.__hash__ = None  # type: ignore[assignment]
ReportSection.__hash__ = None  # type: ignore[assignment]
Report.__hash__ = None  # type: ignore[assignment]
DiagnosticRenderOutput.__hash__ = None  # type: ignore[assignment]
