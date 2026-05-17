"""Package home for analysis, visualization, and report records.

Stage 13 analysis is side-effect-free pipeline composition by default. Public
exports are added only when implemented records or operation-compatible builders
exist.
"""

from .reports import (
    DiagnosticRenderOutput,
    DiagnosticRenderer,
    Report,
    ReportCell,
    ReportOperation,
    ReportRow,
    ReportSection,
    ReportTable,
)
from .visualization import (
    VisualizationOperation,
    VisualizationOutput,
    attach_visualization_fields,
)

__all__ = [
    "DiagnosticRenderOutput",
    "DiagnosticRenderer",
    "Report",
    "ReportCell",
    "ReportOperation",
    "ReportRow",
    "ReportSection",
    "ReportTable",
    "VisualizationOperation",
    "VisualizationOutput",
    "attach_visualization_fields",
]
