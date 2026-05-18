from __future__ import annotations

import pytest

from rphys.data import Batch, BatchOutputFieldSpec, BatchOutputSpec, FieldValue, project_batch_fields
from rphys.data.locators import FieldLocator
from rphys.errors import FieldSchemaError, FieldTypeError, MissingFieldError, RemotePhysDataError


INPUT = FieldLocator.parse("inputs/signal.bvp.source")
TARGET = FieldLocator.parse("targets/signal.bvp.reference")
PREDICTION = FieldLocator.parse("predictions/signal.bvp.estimated")
REPRESENTATION = FieldLocator.parse("outputs/embedding.ppg.features")


def test_batch_output_spec_builds_and_validates_returned_batch() -> None:
    spec = BatchOutputSpec(
        [
            BatchOutputFieldSpec("bvp", PREDICTION, expected_type=list, schema="signal.bvp.v1"),
            BatchOutputFieldSpec("features", REPRESENTATION, expected_type=tuple),
        ]
    )

    batch = spec.build(
        {
            "bvp": [0.1, 0.2],
            "features": (1.0, 2.0),
        }
    )

    assert isinstance(batch, Batch)
    assert batch.require(PREDICTION) == [0.1, 0.2]
    assert batch.field(PREDICTION).schema == "signal.bvp.v1"
    assert batch.require(REPRESENTATION) == (1.0, 2.0)


def test_batch_output_spec_maps_sequence_and_single_raw_result() -> None:
    two_field = BatchOutputSpec(
        [
            BatchOutputFieldSpec("bvp", PREDICTION),
            BatchOutputFieldSpec("features", REPRESENTATION),
        ]
    )
    single_field = BatchOutputSpec([BatchOutputFieldSpec("bvp", PREDICTION, expected_type=list)])

    assert two_field.build(([0.1], (1.0,))).require(REPRESENTATION) == (1.0,)
    assert single_field.build([0.1, 0.2]).require(PREDICTION) == [0.1, 0.2]


def test_batch_output_spec_rejects_missing_invalid_or_extra_fields() -> None:
    spec = BatchOutputSpec(
        [BatchOutputFieldSpec("bvp", PREDICTION, expected_type=list, schema="signal.bvp.v1")],
        allow_extra_fields=False,
    )

    with pytest.raises(MissingFieldError):
        spec.validate(Batch())
    with pytest.raises(FieldTypeError):
        spec.build("not-list")
    with pytest.raises(FieldSchemaError):
        spec.validate(Batch({PREDICTION: FieldValue([], schema="signal.hr.v1")}))
    with pytest.raises(RemotePhysDataError) as extra_error:
        spec.validate(Batch({PREDICTION: FieldValue([], schema="signal.bvp.v1"), INPUT: FieldValue([0.0])}))
    assert extra_error.value.context["locators"] == [str(INPUT)]


def test_batch_output_spec_supports_explicit_pass_through_and_conflict_policy() -> None:
    spec = BatchOutputSpec(
        [BatchOutputFieldSpec("bvp", PREDICTION)],
        pass_through=(INPUT,),
        allow_extra_fields=False,
    )
    base = Batch({INPUT: FieldValue([0.1])})

    output = spec.build([0.2], base=base)

    assert output is not base
    assert output.require(INPUT) == [0.1]
    assert output.require(PREDICTION) == [0.2]
    assert not base.has(PREDICTION)

    with pytest.raises(RemotePhysDataError):
        spec.build([0.3], base=Batch({PREDICTION: FieldValue([0.1])}))
    replaced = spec.build([0.3], base=Batch({PREDICTION: FieldValue([0.1])}), on_conflict="replace")
    assert replaced.require(PREDICTION) == [0.3]


def test_project_batch_fields_excludes_target_fields_by_default() -> None:
    batch = Batch({INPUT: FieldValue([0.1]), TARGET: FieldValue([0.2])})

    projected = project_batch_fields(batch, include=(INPUT,))

    assert projected.require(INPUT) == [0.1]
    assert not projected.has(TARGET)
    with pytest.raises(RemotePhysDataError):
        project_batch_fields(batch)
