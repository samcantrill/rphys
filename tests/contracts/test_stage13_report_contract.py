from __future__ import annotations

import rphys.analysis
from rphys.analysis import Report, ReportOperation, ReportSection, ReportTable
from rphys.collections import CollectionItem
from rphys.data import FieldValue, Sample
from rphys.data.collections import SampleCollection
from rphys.metrics import MetricValue


def test_report_operation_builds_in_memory_report_from_metric_field_collection() -> None:
    collection = SampleCollection(
        (
            CollectionItem(
                Sample({"metrics/custom.stage13.mae": FieldValue(MetricValue(0.1, backend="fake"))}),
                metadata={"sample_id": "w1", "scope": "window"},
            ),
        )
    )

    def build_report(value, _context):
        return Report(
            "Synthetic Report",
            sections=(
                ReportSection(
                    "Metrics",
                    tables=(
                        ReportTable(
                            "metric-table",
                            columns=("sample_id", "scope", "mae"),
                            rows=(
                                {
                                    "sample_id": entry.metadata["sample_id"],
                                    "scope": entry.metadata["scope"],
                                    "mae": entry.value.require("metrics/custom.stage13.mae"),
                                }
                                for entry in value.entries
                            ),
                        ),
                    ),
                ),
            ),
        )

    result = ReportOperation(build_report, name="synthetic-report")(collection)

    assert isinstance(result.output, Report)
    assert result.output.sections[0].tables[0].rows[0].cells["scope"].value == "window"
    assert not hasattr(result.output, "to_dataframe")
    assert not hasattr(result.output, "write")
    assert not hasattr(rphys.analysis, "AnalysisOp")
    assert not hasattr(rphys.analysis, "AnalysisContext")
    assert not hasattr(rphys.analysis, "AnalysisResult")
