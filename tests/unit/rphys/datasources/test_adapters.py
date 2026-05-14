from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.data.keys import DataKey
from rphys.data.metadata import MetadataKey
from rphys.datasources.adapters import (
    DataSourceAdapter,
    DataSourceScanResult,
    DataSourceSpec,
)
from rphys.datasources.refs import DataSourceRef
from rphys.errors import (
    InvalidDataSourceScanResultError,
    InvalidDataSourceSpecError,
)
from tests.support.synthetic_datasources import (
    SyntheticScanAdapter,
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def test_datasource_spec_preserves_descriptor_inputs_without_registry_state() -> None:
    datasource = synthetic_datasource_ref()
    spec = DataSourceSpec(
        datasource,
        required_fields=["video.rgb", "signal.bvp.reference"],
        metadata={"cohort": "tiny"},
    )

    assert spec.datasource is datasource
    assert spec.required_fields == (
        DataKey("video.rgb"),
        DataKey("signal.bvp.reference"),
    )
    assert spec.metadata[MetadataKey("cohort")] == "tiny"
    assert not hasattr(spec, "adapter_name")
    assert not hasattr(spec, "registry")


def test_datasource_spec_copies_metadata_and_round_trips() -> None:
    metadata = {"folds": [1, 2]}
    spec = DataSourceSpec(
        synthetic_datasource_ref(),
        required_fields=["video.rgb"],
        metadata=metadata,
    )
    metadata["folds"].append(3)

    payload = spec.to_dict()

    assert payload["required_fields"] == ["video.rgb"]
    assert payload["metadata"] == {"folds": [1, 2]}
    assert DataSourceSpec.from_dict(payload) == spec
    with pytest.raises(FrozenInstanceError):
        spec.required_fields = ()  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(spec)


def test_datasource_spec_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidDataSourceSpecError):
        DataSourceSpec("fixture")  # type: ignore[arg-type]
    with pytest.raises(InvalidDataSourceSpecError):
        DataSourceSpec(synthetic_datasource_ref(), required_fields="video.rgb")  # type: ignore[arg-type]
    with pytest.raises(InvalidDataSourceSpecError):
        DataSourceSpec(
            synthetic_datasource_ref(),
            required_fields=["video.rgb", "video.rgb"],
        )
    with pytest.raises(InvalidDataSourceSpecError):
        DataSourceSpec(synthetic_datasource_ref(), metadata={"bad": object()})


def test_structural_adapter_scan_returns_descriptor_only_scan_result() -> None:
    datasource = synthetic_datasource_ref()
    records = [synthetic_record_ref(datasource)]
    adapter = SyntheticScanAdapter(
        records,
        warnings=["non-critical metadata difference"],
        rejected_record_ids={"subject-002/record-001": "missing video"},
        validation_evidence={"manifest_records": 2},
    )
    spec = DataSourceSpec(datasource, required_fields=["video.rgb"])

    assert isinstance(adapter, DataSourceAdapter)

    result = adapter.scan(spec)

    assert isinstance(result, DataSourceScanResult)
    assert result.datasource == datasource
    assert result.records == tuple(records)
    assert result.metadata[MetadataKey("adapter")] == "synthetic"
    assert result.validation_evidence["manifest_records"] == 2
    assert result.warnings == ("non-critical metadata difference",)
    assert result.rejected_record_ids == {
        "subject-002/record-001": "missing video",
    }
    assert not hasattr(result, "view")
    assert not hasattr(result, "filters")
    assert not hasattr(result, "load")


def test_scan_result_round_trips_without_view_or_manifest_fields() -> None:
    datasource = synthetic_datasource_ref()
    result = DataSourceScanResult(
        datasource,
        [synthetic_record_ref(datasource)],
        metadata={"scanner": "synthetic"},
        validation_evidence={"records_seen": 1},
        warnings=["ok"],
    )

    payload = result.to_dict()

    assert "view" not in payload
    assert "manifest" not in payload
    assert "fingerprint" not in payload
    assert DataSourceScanResult.from_dict(payload) == result


def test_scan_result_rejects_records_from_other_datasources() -> None:
    datasource = synthetic_datasource_ref("source-a")
    other = synthetic_record_ref(synthetic_datasource_ref("source-b"))

    with pytest.raises(InvalidDataSourceScanResultError):
        DataSourceScanResult(datasource, [other])


def test_scan_result_rejects_invalid_diagnostics() -> None:
    datasource = synthetic_datasource_ref()

    with pytest.raises(InvalidDataSourceScanResultError):
        DataSourceScanResult(datasource, [object()])  # type: ignore[list-item]
    with pytest.raises(InvalidDataSourceScanResultError):
        DataSourceScanResult(datasource, warnings=[""])
    with pytest.raises(InvalidDataSourceScanResultError):
        DataSourceScanResult(datasource, rejected_record_ids={"": "missing"})
    with pytest.raises(InvalidDataSourceScanResultError):
        DataSourceScanResult(datasource, validation_evidence={"bad": object()})


def test_scan_result_does_not_import_view_layer() -> None:
    import sys

    sys.modules.pop("rphys.datasources.filters", None)

    datasource = DataSourceRef("minimal")
    DataSourceScanResult(datasource)

    assert "rphys.datasources.filters" not in sys.modules
