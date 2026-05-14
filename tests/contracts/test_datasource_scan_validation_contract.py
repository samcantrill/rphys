from __future__ import annotations

import importlib

from rphys.datasources.adapters import DataSourceAdapter, DataSourceSpec
from rphys.datasources.validation import ValidationIOPolicy, validate_scan_result
from tests.support.synthetic_datasources import (
    SyntheticScanAdapter,
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def test_structural_datasource_adapter_contract_is_registry_free() -> None:
    datasource = synthetic_datasource_ref()
    adapter = SyntheticScanAdapter([synthetic_record_ref(datasource)])
    spec = DataSourceSpec(datasource, required_fields=["video.rgb"])

    assert isinstance(adapter, DataSourceAdapter)

    result = adapter.scan(spec)
    report = validate_scan_result(result, spec=spec, policy=ValidationIOPolicy.no_io())

    assert report.passed
    assert report.record_count == 1
    assert not hasattr(importlib.import_module("rphys.datasources.adapters"), "registry")


def test_scan_result_contract_is_separate_from_view_and_filter_layers() -> None:
    adapters = importlib.import_module("rphys.datasources.adapters")
    validation = importlib.import_module("rphys.datasources.validation")

    assert not hasattr(adapters.DataSourceScanResult, "view")
    assert not hasattr(adapters.DataSourceScanResult, "filter")
    assert not hasattr(validation.DataSourceValidationReport, "view")
    assert not hasattr(validation.DataSourceValidationReport, "filter")
    assert "DataSourceView" not in adapters.__dict__
    assert "DataSourceView" not in validation.__dict__


def test_validation_contract_keeps_issue_codes_provisional_strings() -> None:
    datasource = synthetic_datasource_ref()
    result = SyntheticScanAdapter(
        [synthetic_record_ref(datasource, include_bvp=False)]
    ).scan(DataSourceSpec(datasource))

    report = validate_scan_result(result)

    assert [issue.code for issue in report.errors] == ["field.missing"]
    assert all(isinstance(issue.code, str) for issue in report.issues)
    assert not hasattr(importlib.import_module("rphys.datasources.validation"), "ValidationIssueCode")
