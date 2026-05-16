from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.errors import RemotePhysMethodError
from rphys.methods import ParameterView, StateEntry, StateLoadResult, StateView


def test_state_entry_copies_and_freezes_primitive_metadata() -> None:
    metadata = {"shape": "scalar"}
    provenance = {"source": "unit"}

    entry = StateEntry("offset", 1.5, metadata=metadata, provenance=provenance)
    metadata["shape"] = "changed"
    provenance["source"] = "changed"

    assert entry.name == "offset"
    assert entry.value == 1.5
    assert entry.metadata == {"shape": "scalar"}
    assert entry.provenance == {"source": "unit"}
    with pytest.raises(TypeError):
        entry.metadata["new"] = "value"  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        entry.value = 2.0  # type: ignore[misc]


def test_state_view_stores_unique_entries_and_lookup_by_name() -> None:
    offset = StateEntry("offset", 1.5)
    scale = StateEntry("scale", 2.0)

    view = StateView([offset, scale], metadata={"format": "plain"})

    assert view.entries == (offset, scale)
    assert view.entry("offset") is offset
    assert view.by_name["scale"] is scale
    assert view.metadata == {"format": "plain"}
    with pytest.raises(TypeError):
        view.by_name["new"] = offset  # type: ignore[index]
    with pytest.raises(RemotePhysMethodError):
        view.entry("missing")
    with pytest.raises(RemotePhysMethodError, match="duplicate names"):
        StateView([offset, StateEntry("offset", 2.0)])


def test_state_load_result_reports_success_and_diagnostics() -> None:
    ok = StateLoadResult(loaded=["offset"], diagnostics={"strict": True})
    failed = StateLoadResult(
        loaded=["offset"],
        missing=["scale"],
        unexpected=["extra"],
        incompatible=["shape"],
        metadata={"source": "unit"},
        provenance={"loader": "fake"},
    )

    assert ok.success is True
    assert ok.loaded == ("offset",)
    assert ok.diagnostics == {"strict": True}
    assert failed.success is False
    assert failed.missing == ("scale",)
    assert failed.unexpected == ("extra",)
    assert failed.incompatible == ("shape",)
    assert failed.metadata == {"source": "unit"}
    assert failed.provenance == {"loader": "fake"}
    with pytest.raises(RemotePhysMethodError):
        StateLoadResult(loaded="offset")  # type: ignore[arg-type]


def test_parameter_view_records_backend_neutral_handles_and_flags() -> None:
    handle = object()
    parameter = ParameterView(
        "scale",
        handle,
        trainable=True,
        requires_update=False,
        metadata={"kind": "scalar"},
        provenance={"source": "fake"},
    )

    assert parameter.name == "scale"
    assert parameter.handle is handle
    assert parameter.trainable is True
    assert parameter.requires_update is False
    assert parameter.metadata == {"kind": "scalar"}
    assert parameter.provenance == {"source": "fake"}
    with pytest.raises(TypeError):
        parameter.metadata["kind"] = "changed"  # type: ignore[index]
    with pytest.raises(RemotePhysMethodError):
        ParameterView("bad", handle, trainable="yes")  # type: ignore[arg-type]
    with pytest.raises(RemotePhysMethodError):
        ParameterView("bad", handle, requires_update=1)  # type: ignore[arg-type]


def test_state_records_reject_non_primitive_metadata_and_placeholder_policy_fields() -> None:
    with pytest.raises(RemotePhysMethodError):
        StateEntry("bad", 1.0, metadata={"nested": {"not": "primitive"}})

    parameter = ParameterView("plain", object())
    for forbidden in [
        "optimizer_group",
        "scheduler",
        "checkpoint_path",
        "device",
        "distributed_rank",
        "torch_module",
    ]:
        assert not hasattr(parameter, forbidden)
