"""Private scientific edge variants for Stage 14 fixture consumers."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from rphys.datasources.adapters import DataSourceScanResult, DataSourceSpec
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.io.fields import FieldRef

from tests.support.synthetic_catalog import (
    BVP_KEY,
    REQUIRED_FIELD_KEYS,
    TIMESTAMPS_KEY,
    VIDEO_KEY,
    SyntheticScenario,
    make_synthetic_scenario,
)


@dataclass(frozen=True, slots=True)
class SyntheticEdgeVariant:
    """Named generated edge case with inspectable failure evidence."""

    name: str
    scenario: SyntheticScenario
    datasource: DataSourceRef
    records: tuple[RecordRef, ...]
    affected_field: str
    expected_failure_family: str
    evidence: Mapping[str, object]
    invalid_payload: tuple[Any, ...] | None = None

    def spec(
        self,
        *,
        required_fields: Sequence[str] = REQUIRED_FIELD_KEYS,
    ) -> DataSourceSpec:
        """Build a public scan spec for consumers of this edge variant."""

        return DataSourceSpec(
            self.datasource,
            required_fields=required_fields,
            metadata={"edge_variant": self.name},
        )

    def scan_result(self) -> DataSourceScanResult:
        """Return descriptor-only scan evidence for public validation paths."""

        return DataSourceScanResult(
            self.datasource,
            self.records,
            metadata={"edge_variant": self.name},
            validation_evidence={
                "edge_variant": self.name,
                "affected_field": self.affected_field,
                "expected_failure_family": self.expected_failure_family,
            },
        )


def make_edge_variant(name: str) -> SyntheticEdgeVariant:
    """Create a named edge variant without repairing the invalid evidence."""

    scenario = make_synthetic_scenario(
        scenario_id=f"stage14-edge-{name}",
        datasource_count=1,
        subjects=("subject-001",),
        records_per_subject=1,
        include_optional_fields=True,
    )
    datasource = scenario.datasources[0]
    base_record = scenario.records[0]

    if name == "missing_field":
        record = _remove_field(base_record, BVP_KEY)
        return _variant(
            name,
            scenario,
            datasource,
            record,
            affected_field=BVP_KEY,
            expected_failure_family="missing_field",
            evidence={
                "required_field": BVP_KEY,
                "present_fields": sorted(str(key) for key in record.fields),
            },
        )
    if name == "short_record":
        payload = (0.11,)
        record = _replace_field_metadata(
            base_record,
            BVP_KEY,
            {
                "sample_count": 1,
                "edge.short_record": True,
            },
        )
        return _variant(
            name,
            scenario,
            datasource,
            record,
            affected_field=BVP_KEY,
            expected_failure_family="short_input",
            evidence={"sample_count": 1, "minimum_expected_samples": 2},
            invalid_payload=payload,
        )
    if name == "flat_signal":
        payload = (0.2, 0.2, 0.2, 0.2)
        record = _replace_field_metadata(
            base_record,
            BVP_KEY,
            {
                "waveform.amplitude": 0.0,
                "edge.flat_signal": True,
            },
        )
        return _variant(
            name,
            scenario,
            datasource,
            record,
            affected_field=BVP_KEY,
            expected_failure_family="flat_signal",
            evidence={"unique_values": 1, "sample_count": len(payload)},
            invalid_payload=payload,
        )
    if name == "nan_signal":
        payload = (0.1, math.nan, 0.3, 0.4)
        record = _replace_field_metadata(
            base_record,
            BVP_KEY,
            {"edge.invalid_values": "nan"},
        )
        return _variant(
            name,
            scenario,
            datasource,
            record,
            affected_field=BVP_KEY,
            expected_failure_family="invalid_value",
            evidence={"invalid_value": "nan", "invalid_positions": (1,)},
            invalid_payload=payload,
        )
    if name == "inf_signal":
        payload = (0.1, math.inf, 0.3, 0.4)
        record = _replace_field_metadata(
            base_record,
            BVP_KEY,
            {"edge.invalid_values": "inf"},
        )
        return _variant(
            name,
            scenario,
            datasource,
            record,
            affected_field=BVP_KEY,
            expected_failure_family="invalid_value",
            evidence={"invalid_value": "inf", "invalid_positions": (1,)},
            invalid_payload=payload,
        )
    if name == "invalid_sample_rate":
        record = _replace_field_metadata(
            base_record,
            BVP_KEY,
            {
                "sample_rate_hz": 0.0,
                "edge.invalid_sample_rate": True,
            },
        )
        return _variant(
            name,
            scenario,
            datasource,
            record,
            affected_field=BVP_KEY,
            expected_failure_family="invalid_sample_rate",
            evidence={"sample_rate_hz": 0.0, "valid_rate_required": "positive"},
        )
    if name == "timestamp_drift":
        timestamps = (0.0, 0.033333, 0.066667, 0.125)
        record = _replace_field_metadata(
            base_record,
            TIMESTAMPS_KEY,
            {
                "timestamp_drift_s": 0.025,
                "edge.timestamp_drift": True,
            },
        )
        return _variant(
            name,
            scenario,
            datasource,
            record,
            affected_field=TIMESTAMPS_KEY,
            expected_failure_family="timestamp_drift",
            evidence={"timestamps_s": timestamps, "drift_s": 0.025},
            invalid_payload=timestamps,
        )
    if name == "irregular_timestamps":
        timestamps = (0.0, 0.033333, 0.081, 0.116)
        record = _replace_field_metadata(
            base_record,
            TIMESTAMPS_KEY,
            {
                "timestamp_step_s": 0.0,
                "edge.irregular_timestamps": True,
            },
        )
        return _variant(
            name,
            scenario,
            datasource,
            record,
            affected_field=TIMESTAMPS_KEY,
            expected_failure_family="irregular_timestamps",
            evidence={"timestamps_s": timestamps, "regular_step_expected_s": 0.033333},
            invalid_payload=timestamps,
        )
    if name == "misalignment":
        record = _replace_field_metadata(
            base_record,
            BVP_KEY,
            {
                "sample_count": 3,
                "alignment_group": "misaligned",
                "edge.misalignment": True,
            },
        )
        return _variant(
            name,
            scenario,
            datasource,
            record,
            affected_field=BVP_KEY,
            expected_failure_family="field_misalignment",
            evidence={
                "reference_field": VIDEO_KEY,
                "reference_sample_count": 4,
                "affected_sample_count": 3,
            },
        )
    raise KeyError(f"unknown synthetic edge variant: {name}")


def _variant(
    name: str,
    scenario: SyntheticScenario,
    datasource: DataSourceRef,
    record: RecordRef,
    *,
    affected_field: str,
    expected_failure_family: str,
    evidence: Mapping[str, object],
    invalid_payload: tuple[Any, ...] | None = None,
) -> SyntheticEdgeVariant:
    return SyntheticEdgeVariant(
        name=name,
        scenario=scenario,
        datasource=datasource,
        records=(record,),
        affected_field=affected_field,
        expected_failure_family=expected_failure_family,
        evidence=MappingProxyType(dict(evidence)),
        invalid_payload=invalid_payload,
    )


def _remove_field(record: RecordRef, field_key: str) -> RecordRef:
    fields = {str(key): field for key, field in record.fields.items() if str(key) != field_key}
    return RecordRef(record.datasource, record.record_id, fields, metadata=record.metadata)


def _replace_field_metadata(
    record: RecordRef,
    field_key: str,
    metadata_updates: Mapping[str, object],
) -> RecordRef:
    fields = {str(key): field for key, field in record.fields.items()}
    field = fields[field_key]
    metadata = {str(key): value for key, value in field.metadata.items()}
    metadata.update(metadata_updates)
    fields[field_key] = FieldRef(
        field.key,
        field.resources,
        schema=field.schema,
        metadata=metadata,
    )
    return RecordRef(record.datasource, record.record_id, fields, metadata=record.metadata)
