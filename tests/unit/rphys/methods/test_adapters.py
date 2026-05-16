from __future__ import annotations

import pytest

from rphys.data import Batch, FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import FieldSchemaError, FieldTypeError, MissingFieldError, RemotePhysMethodError
from rphys.methods import (
    MethodInputAdapter,
    MethodInputSpec,
    MethodOutputAdapter,
    MethodOutputSpec,
    MethodOutput,
)


VIDEO = FieldLocator.parse("inputs/video.rgb")
BVP = FieldLocator.parse("targets/signal.bvp.reference")
PREDICTION = FieldLocator.parse("predictions/signal.bvp.estimated")
REPRESENTATION = FieldLocator.parse("outputs/embedding.ppg.features")


def test_input_spec_normalizes_locators_and_validates_expected_type() -> None:
    spec = MethodInputSpec(
        "video",
        "inputs/video.rgb",
        expected_type=list,
        schema="video.rgb.v1",
    )

    assert spec.locator == VIDEO
    assert spec.expected_type is list
    assert str(spec.schema) == "video.rgb.v1"

    with pytest.raises(RemotePhysMethodError):
        MethodInputSpec("", VIDEO)
    with pytest.raises(RemotePhysMethodError):
        MethodInputSpec("bad", VIDEO, expected_type=())  # type: ignore[arg-type]


def test_input_adapter_extracts_declared_batch_payloads() -> None:
    adapter = MethodInputAdapter(
        [
            MethodInputSpec("video", VIDEO, expected_type=list, schema="video.rgb.v1"),
            MethodInputSpec("target", BVP, expected_type=list, schema="signal.bvp.v1"),
        ]
    )
    batch = Batch(
        {
            VIDEO: FieldValue(["frame-0", "frame-1"], schema="video.rgb.v1"),
            BVP: FieldValue([[0.1], [0.2]], schema="signal.bvp.v1"),
        }
    )

    assert adapter.extract(batch) == {
        "video": ["frame-0", "frame-1"],
        "target": [[0.1], [0.2]],
    }


def test_input_adapter_rejects_duplicates_missing_fields_and_type_schema_mismatch() -> None:
    with pytest.raises(RemotePhysMethodError, match="duplicate names"):
        MethodInputAdapter(
            [
                MethodInputSpec("video", VIDEO),
                MethodInputSpec("video", BVP),
            ]
        )
    with pytest.raises(RemotePhysMethodError, match="duplicate locators"):
        MethodInputAdapter(
            [
                MethodInputSpec("video", VIDEO),
                MethodInputSpec("again", "inputs/video.rgb"),
            ]
        )

    adapter = MethodInputAdapter(
        [MethodInputSpec("video", VIDEO, expected_type=list, schema="video.rgb.v1")]
    )
    with pytest.raises(MissingFieldError):
        adapter.extract(Batch())
    with pytest.raises(FieldTypeError):
        adapter.extract(Batch({VIDEO: FieldValue("not-list", schema="video.rgb.v1")}))
    with pytest.raises(FieldSchemaError):
        adapter.extract(Batch({VIDEO: FieldValue([], schema="video.gray.v1")}))


def test_output_spec_validates_prediction_or_output_roles() -> None:
    prediction = MethodOutputSpec(
        "bvp",
        "predictions/signal.bvp.estimated",
        expected_type=list,
        schema="signal.bvp.v1",
    )
    representation = MethodOutputSpec("features", REPRESENTATION)

    assert prediction.locator == PREDICTION
    assert prediction.expected_type is list
    assert str(prediction.schema) == "signal.bvp.v1"
    assert representation.locator == REPRESENTATION

    with pytest.raises(RemotePhysMethodError) as exc_info:
        MethodOutputSpec("bad", "inputs/signal.bvp.source")
    assert exc_info.value.context["role"] == "inputs"


def test_output_adapter_maps_named_mapping_results_to_method_output() -> None:
    adapter = MethodOutputAdapter(
        [
            MethodOutputSpec("bvp", PREDICTION, expected_type=list, schema="signal.bvp.v1"),
            MethodOutputSpec("features", REPRESENTATION, expected_type=tuple),
        ]
    )

    output = adapter.adapt(
        {
            "bvp": [0.1, 0.2],
            "features": (1.0, 2.0),
        },
        diagnostics={"flat": False},
        metadata={"method": "synthetic"},
        provenance={"adapter": "unit"},
    )

    assert isinstance(output, MethodOutput)
    assert output.fields[PREDICTION].payload == [0.1, 0.2]
    assert output.fields[PREDICTION].schema == "signal.bvp.v1"
    assert output.fields[REPRESENTATION].payload == (1.0, 2.0)
    assert output.diagnostics == {"flat": False}
    assert output.metadata == {"method": "synthetic"}
    assert output.provenance == {"adapter": "unit"}


def test_output_adapter_maps_sequence_results_by_spec_order() -> None:
    adapter = MethodOutputAdapter(
        [
            MethodOutputSpec("bvp", PREDICTION),
            MethodOutputSpec("features", REPRESENTATION),
        ]
    )

    output = adapter.adapt(([0.1], (1.0,)))

    assert output.fields[PREDICTION].payload == [0.1]
    assert output.fields[REPRESENTATION].payload == (1.0,)


def test_output_adapter_allows_single_raw_sequence_output() -> None:
    adapter = MethodOutputAdapter(
        [MethodOutputSpec("bvp", PREDICTION, expected_type=list)]
    )

    output = adapter.adapt([0.1, 0.2])

    assert output.fields[PREDICTION].payload == [0.1, 0.2]


def test_output_adapter_rejects_result_shape_and_type_schema_failures() -> None:
    adapter = MethodOutputAdapter(
        [
            MethodOutputSpec("bvp", PREDICTION, expected_type=list, schema="signal.bvp.v1"),
            MethodOutputSpec("features", REPRESENTATION),
        ]
    )

    with pytest.raises(RemotePhysMethodError) as missing_error:
        adapter.adapt({"bvp": [0.1]})
    assert missing_error.value.context["missing"] == ["features"]

    with pytest.raises(RemotePhysMethodError) as extra_error:
        adapter.adapt({"bvp": [0.1], "features": (1.0,), "extra": 1})
    assert extra_error.value.context["extra"] == ["extra"]

    with pytest.raises(RemotePhysMethodError) as arity_error:
        adapter.adapt(([0.1],))
    assert arity_error.value.context["expected"] == 2
    assert arity_error.value.context["actual"] == 1

    with pytest.raises(FieldTypeError):
        adapter.adapt({"bvp": "not-list", "features": (1.0,)})

    with pytest.raises(FieldSchemaError):
        adapter.adapt(
            {
                "bvp": FieldValue([0.1], schema="signal.hr.v1"),
                "features": (1.0,),
            }
        )
