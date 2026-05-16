from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.data import Batch, FieldValue
from rphys.data.locators import FieldLocator, FieldRole
from rphys.errors import RemotePhysMethodError
from rphys.methods import MethodOutput, apply_method_output


PREDICTION = FieldLocator.parse("predictions/signal.bvp.estimated")


def test_method_output_is_patch_like_and_freezes_mappings() -> None:
    field_value = FieldValue([0.1, 0.2], schema="signal.bvp.v1")
    fields = {PREDICTION: field_value}
    diagnostics = {"flat": False, "snr": 12.5}

    output = MethodOutput(
        fields=fields,
        diagnostics=diagnostics,
        metadata={"method": "synthetic"},
        provenance={"stage": "unit"},
    )
    fields[FieldLocator(FieldRole.PREDICTIONS, "signal.hr.estimated")] = FieldValue(72.0)
    diagnostics["snr"] = 0.0

    assert output.fields == {PREDICTION: field_value}
    assert output.diagnostics == {"flat": False, "snr": 12.5}
    assert output.metadata == {"method": "synthetic"}
    assert output.provenance == {"stage": "unit"}
    assert not isinstance(output, Batch)
    assert not hasattr(output, "apply")
    with pytest.raises(TypeError):
        output.fields[PREDICTION] = FieldValue([])  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        output.fields = {}  # type: ignore[misc]


def test_method_output_normalizes_string_locators() -> None:
    output = MethodOutput(
        fields={"predictions/signal.bvp.estimated": FieldValue([0.1])}
    )

    assert tuple(output.fields) == (PREDICTION,)


def test_method_output_rejects_duplicate_locators_after_normalization() -> None:
    with pytest.raises(RemotePhysMethodError) as exc_info:
        MethodOutput(
            fields={
                PREDICTION: FieldValue([0.1]),
                "predictions/signal.bvp.estimated": FieldValue([0.2]),
            }
        )

    assert exc_info.value.context["locator"] == str(PREDICTION)


def test_method_output_rejects_non_field_values_and_non_primitive_metadata() -> None:
    with pytest.raises(RemotePhysMethodError) as field_error:
        MethodOutput(fields={PREDICTION: [0.1]})  # type: ignore[dict-item]
    assert field_error.value.context["locator"] == str(PREDICTION)
    assert field_error.value.context["actual"] == "list"

    with pytest.raises(RemotePhysMethodError) as diagnostic_error:
        MethodOutput(diagnostics={"history": [1, 2, 3]})
    assert diagnostic_error.value.context["field"] == "diagnostics"
    assert diagnostic_error.value.context["key"] == "history"
    assert diagnostic_error.value.context["actual"] == "list"


def test_method_output_has_no_training_export_or_batch_fields() -> None:
    output = MethodOutput()

    for forbidden in [
        "batch",
        "loss",
        "metric",
        "objective",
        "optimizer",
        "checkpoint",
        "device",
        "export_path",
    ]:
        assert not hasattr(output, forbidden)


def test_apply_method_output_copies_batch_by_default_without_mutating_input() -> None:
    source = FieldLocator.parse("inputs/signal.bvp.source")
    batch = Batch({source: FieldValue([0.1], schema="signal.bvp.v1")})
    output = MethodOutput(fields={PREDICTION: FieldValue([0.2], schema="signal.bvp.v1")})

    applied = apply_method_output(output, batch)

    assert applied is not batch
    assert applied.require(source) == [0.1]
    assert applied.require(PREDICTION) == [0.2]
    assert not batch.has(PREDICTION)


def test_apply_method_output_can_mutate_when_explicitly_requested() -> None:
    batch = Batch()
    output = MethodOutput(fields={PREDICTION: FieldValue([0.2])})

    applied = apply_method_output(output, batch, copy_batch=False)

    assert applied is batch
    assert batch.require(PREDICTION) == [0.2]


def test_apply_method_output_conflict_policy_errors_or_replaces() -> None:
    batch = Batch({PREDICTION: FieldValue([0.1])})
    output = MethodOutput(fields={PREDICTION: FieldValue([0.2])})

    with pytest.raises(RemotePhysMethodError) as conflict_error:
        apply_method_output(output, batch)
    assert conflict_error.value.context["locator"] == str(PREDICTION)
    assert conflict_error.value.context["policy"] == "error"

    replaced = apply_method_output(output, batch, on_conflict="replace")
    assert replaced.require(PREDICTION) == [0.2]
    assert batch.require(PREDICTION) == [0.1]


def test_apply_method_output_rejects_invalid_inputs_and_policy() -> None:
    with pytest.raises(RemotePhysMethodError):
        apply_method_output(object(), Batch())  # type: ignore[arg-type]
    with pytest.raises(RemotePhysMethodError):
        apply_method_output(MethodOutput(), object())  # type: ignore[arg-type]
    with pytest.raises(RemotePhysMethodError) as policy_error:
        apply_method_output(MethodOutput(), Batch(), on_conflict="skip")  # type: ignore[arg-type]
    assert policy_error.value.context["expected"] == ["error", "replace"]
