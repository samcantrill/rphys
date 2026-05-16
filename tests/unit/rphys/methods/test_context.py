from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.errors import RemotePhysMethodError
from rphys.methods import PredictionContext


def test_prediction_context_copies_and_freezes_primitive_mappings() -> None:
    metadata = {"source": "unit", "attempt": 1, "valid": True}
    provenance = {"pipeline": "synthetic", "score": 0.25, "missing": None}

    context = PredictionContext(metadata=metadata, provenance=provenance)
    metadata["source"] = "changed"
    provenance["pipeline"] = "changed"

    assert context.metadata == {
        "source": "unit",
        "attempt": 1,
        "valid": True,
    }
    assert context.provenance == {
        "pipeline": "synthetic",
        "score": 0.25,
        "missing": None,
    }
    with pytest.raises(TypeError):
        context.metadata["new"] = "value"  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        context.metadata = {}  # type: ignore[misc]


def test_prediction_context_defaults_to_empty_read_only_mappings() -> None:
    context = PredictionContext()

    assert context.metadata == {}
    assert context.provenance == {}
    with pytest.raises(TypeError):
        context.provenance["new"] = "value"  # type: ignore[index]


def test_prediction_context_rejects_non_string_keys_and_object_values() -> None:
    with pytest.raises(RemotePhysMethodError) as key_error:
        PredictionContext(metadata={1: "value"})  # type: ignore[dict-item]
    assert key_error.value.context["field"] == "metadata"
    assert key_error.value.context["actual"] == "int"

    with pytest.raises(RemotePhysMethodError) as value_error:
        PredictionContext(provenance={"handle": object()})
    assert value_error.value.context["field"] == "provenance"
    assert value_error.value.context["key"] == "handle"
    assert value_error.value.context["actual"] == "object"


def test_prediction_context_has_no_first_class_domain_or_backend_fields() -> None:
    context = PredictionContext(metadata={"sample_id": "caller-owned"})

    assert context.metadata["sample_id"] == "caller-owned"
    for forbidden in [
        "sample_id",
        "batch_id",
        "record_id",
        "split",
        "mode",
        "device",
        "dtype",
        "checkpoint",
    ]:
        assert not hasattr(context, forbidden)
