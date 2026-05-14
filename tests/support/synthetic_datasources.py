"""Private synthetic datasource fixtures for Stage 5 tests.

This module is test support only. Public package code must not import it, and
`rphys` must not expose synthetic datasource helpers as library APIs.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from rphys.data.fields import FieldSpec
from rphys.data.metadata import SOURCE_ID, SUBJECT_ID
from rphys.datasources.adapters import DataSourceScanResult, DataSourceSpec
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.datasources.schemas import DataSourceSchema
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef

__all__ = [
    "SyntheticScanAdapter",
    "synthetic_datasource_ref",
    "synthetic_record_ref",
]


def synthetic_datasource_ref(
    datasource_id: str = "synthetic-rppg",
    *,
    with_schema: bool = True,
    with_source: bool = True,
) -> DataSourceRef:
    """Create a tiny descriptor-only datasource for tests."""

    schema = None
    if with_schema:
        schema = DataSourceSchema(
            {
                "video.rgb": FieldSpec("video.rgb", "video", "video.rgb.v1"),
                "signal.bvp.reference": FieldSpec(
                    "signal.bvp.reference",
                    "signal",
                    "signal.bvp.v1",
                ),
            },
            metadata={SOURCE_ID: "synthetic"},
        )
    source = (
        ResourceRef("memory://synthetic-datasource", "memory")
        if with_source
        else None
    )
    return DataSourceRef(
        datasource_id,
        source=source,
        schema=schema,
        metadata={SOURCE_ID: "synthetic"},
    )


def synthetic_record_ref(
    datasource: DataSourceRef | None = None,
    record_id: str = "subject-001/record-001",
    *,
    include_bvp: bool = True,
    subject_id: str = "subject-001",
) -> RecordRef:
    """Create a descriptor-only record with tiny memory resources."""

    source = datasource or synthetic_datasource_ref()
    fields = {
        "video.rgb": FieldRef(
            "video.rgb",
            [ResourceRef(f"memory://{record_id}/video.rgb", "memory")],
            schema="video.rgb.v1",
        )
    }
    if include_bvp:
        fields["signal.bvp.reference"] = FieldRef(
            "signal.bvp.reference",
            [ResourceRef(f"memory://{record_id}/bvp", "memory")],
            schema="signal.bvp.v1",
        )
    return RecordRef(
        source,
        record_id,
        fields,
        metadata={SUBJECT_ID: subject_id},
    )


class SyntheticScanAdapter:
    """Tiny structural adapter that returns prebuilt descriptor records."""

    def __init__(
        self,
        records: Sequence[RecordRef],
        *,
        warnings: Sequence[str] = (),
        rejected_record_ids: Mapping[str, str] | None = None,
        validation_evidence: Mapping[str, object] | None = None,
    ) -> None:
        self._records = tuple(records)
        self._warnings = tuple(warnings)
        self._rejected_record_ids = dict(rejected_record_ids or {})
        self._validation_evidence = dict(validation_evidence or {})

    def scan(self, spec: DataSourceSpec) -> DataSourceScanResult:
        """Return descriptor-only scan output for ``spec``."""

        return DataSourceScanResult(
            spec.datasource,
            self._records,
            metadata={"adapter": "synthetic"},
            validation_evidence=self._validation_evidence,
            warnings=self._warnings,
            rejected_record_ids=self._rejected_record_ids,
        )
