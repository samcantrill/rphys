from __future__ import annotations

from rphys.analysis import VisualizationOperation, VisualizationOutput
from rphys.data import FieldValue, Sample
from rphys.errors import InvalidOperationResultError


def test_visualization_operation_attaches_descriptor_fields_without_backend_api() -> None:
    operation = VisualizationOperation(
        lambda _value, _context: {
            "outputs/custom.stage13.visualization.pulse": VisualizationOutput(
                "line",
                codec="fake.visualization.line.v1",
                payload={"points": (1, 2, 3)},
            )
        },
        name="pulse-visualization",
    )
    result = operation(Sample({"inputs/signal.bvp": FieldValue([1, 2, 3])}))

    output = result.output.require("outputs/custom.stage13.visualization.pulse")
    assert output.codec == "fake.visualization.line.v1"
    assert result.metadata["visualization_fields"] == ("outputs/custom.stage13.visualization.pulse",)
    assert not hasattr(output, "save")
    assert not hasattr(output, "render")


def test_visualization_operation_invalid_builder_output_is_result_error() -> None:
    operation = VisualizationOperation(
        lambda _value, _context: {"outputs/custom.stage13.visualization.pulse": object()},
        name="bad-visualization",
    )

    try:
        operation(Sample({"inputs/signal.bvp": FieldValue([1])}))
    except InvalidOperationResultError as exc:
        assert exc.context["operation_name"] == "VisualizationOperation"
        assert exc.context["expected"] == "VisualizationOutput"
    else:  # pragma: no cover
        raise AssertionError("invalid visualization output did not fail")
