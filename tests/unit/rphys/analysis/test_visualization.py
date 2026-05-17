from __future__ import annotations

import pytest

from rphys.analysis import VisualizationOperation, VisualizationOutput, attach_visualization_fields
from rphys.collections import CollectionItem
from rphys.data import Batch, FieldValue, Sample
from rphys.data.collections import SampleCollection
from rphys.errors import RemotePhysAnalysisError
from rphys.ops import OperationContext


def _output() -> VisualizationOutput:
    return VisualizationOutput(
        "line",
        codec="fake.visualization.line.v1",
        payload={"x": (0, 1), "y": (72, 73)},
        title="Pulse",
        metadata={"scope": "sample"},
        provenance={"test": "unit"},
    )


def test_visualization_output_is_field_ready_data_not_backend_rendering() -> None:
    output = _output()

    assert output.kind == "line"
    assert output.codec == "fake.visualization.line.v1"
    assert output.payload["y"] == (72, 73)

    with pytest.raises(RemotePhysAnalysisError):
        VisualizationOutput("", codec="fake", payload={})
    with pytest.raises(RemotePhysAnalysisError):
        VisualizationOutput("line", codec="", payload={})
    with pytest.raises(RemotePhysAnalysisError):
        VisualizationOutput("line", codec="fake", payload=None)


def test_attach_visualization_fields_copies_sample_and_batch_outputs() -> None:
    sample = Sample({"inputs/signal.bvp": FieldValue([1])})
    batch = Batch({"inputs/signal.bvp": FieldValue([[1]])})

    sample_output = attach_visualization_fields(
        sample,
        {"outputs/custom.stage13.visualization.pulse": _output()},
        operation_name="plot-pulse",
    )
    batch_output = attach_visualization_fields(
        batch,
        {"outputs/custom.stage13.visualization.batch": _output()},
        operation_name="plot-batch",
    )

    assert sample_output is not sample
    assert sample_output.require("outputs/custom.stage13.visualization.pulse").codec == "fake.visualization.line.v1"
    assert sample_output.field("outputs/custom.stage13.visualization.pulse").metadata["analysis.operation"] == "plot-pulse"
    assert not sample.has("outputs/custom.stage13.visualization.pulse")
    assert batch_output.require("outputs/custom.stage13.visualization.batch").kind == "line"


def test_visualization_operation_attaches_collection_fields_with_provenance() -> None:
    collection = SampleCollection(
        (
            CollectionItem(Sample({"inputs/signal.bvp": FieldValue([1])}), metadata={"sample_id": "w1"}),
            CollectionItem(Sample({"inputs/signal.bvp": FieldValue([2])}), metadata={"sample_id": "w2"}),
        ),
        metadata={"level": "window"},
    )
    operation = VisualizationOperation(
        lambda _value, _context: {"outputs/custom.stage13.visualization.window": _output()},
        name="window-plot",
    )

    result = operation(collection, OperationContext(metadata={"split": "valid"}))

    assert isinstance(result.output, SampleCollection)
    assert result.output.metadata["visualization_operation"] == "window-plot"
    assert result.output.entries[0].metadata["visualization_fields"] == (
        "outputs/custom.stage13.visualization.window",
    )
    assert result.output[0].require("outputs/custom.stage13.visualization.window").kind == "line"
    assert not collection[0].has("outputs/custom.stage13.visualization.window")


def test_visualization_field_conflicts_fail_loudly() -> None:
    sample = Sample({"outputs/custom.stage13.visualization.pulse": FieldValue(_output())})

    with pytest.raises(RemotePhysAnalysisError):
        attach_visualization_fields(
            sample,
            {"outputs/custom.stage13.visualization.pulse": _output()},
            operation_name="plot-pulse",
        )
