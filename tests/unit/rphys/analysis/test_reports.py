from __future__ import annotations

from dataclasses import dataclass

import pytest

from rphys.analysis import (
    DiagnosticRenderOutput,
    DiagnosticRenderer,
    Report,
    ReportCell,
    ReportOperation,
    ReportRow,
    ReportSection,
    ReportTable,
    VisualizationOutput,
)
from rphys.collections import CollectionItem
from rphys.data import FieldValue, Sample
from rphys.data.collections import SampleCollection
from rphys.errors import RemotePhysAnalysisError
from rphys.metrics import MetricValue
from rphys.ops import OperationContext


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


def _visualization() -> VisualizationOutput:
    return VisualizationOutput("line", codec="fake.visualization.line.v1", payload={"points": (1, 2)})


def test_report_table_validates_columns_rows_and_cell_values() -> None:
    metric = MetricValue(FakeScalar(0.25), backend="fake", unit="bpm")
    row = ReportRow(
        {
            "sample_id": "w1",
            "metric": metric,
            "figure": _visualization(),
        },
        provenance={"sample_id": "w1"},
    )
    table = ReportTable(
        "sample-metrics",
        columns=("sample_id", "metric", "figure"),
        rows=(row,),
        metadata={"scope": "sample"},
    )

    assert table.rows[0].cells["metric"].value is metric
    assert table.rows[0].cells["figure"].value.kind == "line"
    assert table.metadata["scope"] == "sample"

    with pytest.raises(RemotePhysAnalysisError):
        ReportCell({"not": "primitive"})
    with pytest.raises(RemotePhysAnalysisError):
        ReportTable("bad", columns=("sample_id",), rows=({"sample_id": "w1", "extra": 1},))
    with pytest.raises(RemotePhysAnalysisError):
        ReportTable("bad", columns=("sample_id", "sample_id"), rows=())


def test_report_and_section_records_are_in_memory_only() -> None:
    table = ReportTable("summary", columns=("name", "value"), rows=({"name": "mae", "value": 0.25},))
    section = ReportSection("Metrics", tables=(table,), text="Synthetic summary")
    report = Report("Evaluation Summary", sections=(section,), diagnostics={"warnings": ()})

    assert report.sections[0].tables[0] is table
    assert report.diagnostics["warnings"] == ()
    assert not hasattr(report, "save")
    assert not hasattr(report, "to_dataframe")


def test_report_operation_builds_report_table_from_metric_field_samples() -> None:
    collection = SampleCollection(
        (
            CollectionItem(
                Sample({"metrics/custom.stage13.mae": FieldValue(MetricValue(FakeScalar(0.1), backend="fake"))}),
                metadata={"sample_id": "w1"},
            ),
            CollectionItem(
                Sample({"metrics/custom.stage13.mae": FieldValue(MetricValue(FakeScalar(0.2), backend="fake"))}),
                metadata={"sample_id": "w2"},
            ),
        )
    )

    def build_table(value: object, context: OperationContext) -> ReportTable:
        assert isinstance(value, SampleCollection)
        return ReportTable(
            "metric-fields",
            columns=("sample_id", "mae", "split"),
            rows=(
                {
                    "sample_id": entry.metadata["sample_id"],
                    "mae": entry.value.require("metrics/custom.stage13.mae"),
                    "split": context.metadata["split"],
                }
                for entry in value.entries
            ),
            provenance={"source": "metric-fields"},
        )

    operation = ReportOperation(build_table, name="metric-report")
    result = operation(collection, OperationContext(metadata={"split": "test"}))

    assert isinstance(result.output, ReportTable)
    assert [row.cells["sample_id"].value for row in result.output.rows] == ["w1", "w2"]
    assert result.output.rows[1].cells["mae"].value.value == FakeScalar(0.2)
    assert result.metadata["report_output"] == "ReportTable"


def test_diagnostic_renderer_output_is_data_record() -> None:
    table = ReportTable("summary", columns=("name", "value"), rows=({"name": "n", "value": 2},))

    class FakeRenderer:
        def __call__(self, value, context=None):
            return DiagnosticRenderOutput(
                "fake-renderer",
                value,
                metadata={"context": context is not None},
                diagnostics={"format": "memory"},
            )

    renderer = FakeRenderer()
    output = renderer(table, OperationContext())

    assert isinstance(renderer, DiagnosticRenderer)
    assert output.renderer == "fake-renderer"
    assert output.output is table
    assert output.diagnostics["format"] == "memory"
    with pytest.raises(RemotePhysAnalysisError):
        DiagnosticRenderOutput("bad", object())  # type: ignore[arg-type]
