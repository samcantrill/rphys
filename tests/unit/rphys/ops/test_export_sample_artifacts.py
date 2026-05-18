from __future__ import annotations

from pathlib import Path

import pytest

from rphys.data import FieldValue, Sample
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.errors import RemotePhysOperationError
from rphys.io.codecs import CodecRegistry
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef
from rphys.ops.export import (
    ExportResult,
    ExportSpec,
    ExportTarget,
    FieldExportOutcome,
    build_sample_artifact_record,
    export_record_requests,
    sample_artifact_export_request,
)
from tests.support.synthetic_codecs import SyntheticCodec


PREDICTION = "predictions/signal.bvp.predicted"
PREDICTION_KEY = "signal.bvp.predicted"


def test_sample_artifact_export_request_requires_descriptor_for_new_fields(
    tmp_path: Path,
) -> None:
    sample = Sample({PREDICTION: FieldValue(0.11, schema="signal.bvp.v1")})
    source_record = _record("record-001")
    prediction_ref = _field_ref(PREDICTION_KEY, "memory://record-001/predicted")

    request = sample_artifact_export_request(
        sample=sample,
        source_record=source_record,
        locators=(PREDICTION,),
        field_refs={PREDICTION_KEY: prediction_ref},
        target=ExportTarget(ResourceRef(tmp_path.as_uri(), "file"), "exp-001"),
        spec=ExportSpec((PREDICTION_KEY,), codec_requests={PREDICTION_KEY: "bvp"}),
    )

    assert request.source_record.fields[PREDICTION_KEY] == prediction_ref
    assert request.field_values[PREDICTION_KEY].payload == 0.11
    assert request.source_record.metadata["sample_artifact.field_count"] == 1


def test_sample_artifact_export_request_rejects_loaded_fields_without_descriptor(
    tmp_path: Path,
) -> None:
    sample = Sample({PREDICTION: FieldValue(0.11)})

    with pytest.raises(RemotePhysOperationError):
        sample_artifact_export_request(
            sample=sample,
            source_record=_record("record-001"),
            locators=(PREDICTION,),
            target=ExportTarget(ResourceRef(tmp_path.as_uri(), "file"), "exp-001"),
        )


def test_export_record_requests_runs_existing_selection_and_save_operations(
    tmp_path: Path,
) -> None:
    target = ExportTarget(ResourceRef(tmp_path.as_uri(), "file"), "exp-001")
    spec = ExportSpec((PREDICTION_KEY,), codec_requests={PREDICTION_KEY: "bvp"})
    requests = tuple(
        sample_artifact_export_request(
            sample=Sample({PREDICTION: FieldValue(index / 100, schema="signal.bvp.v1")}),
            source_record=_record(f"record-00{index}"),
            locators=(PREDICTION,),
            field_refs={
                PREDICTION_KEY: _field_ref(
                    PREDICTION_KEY,
                    f"memory://record-00{index}/predicted",
                )
            },
            target=target,
            spec=spec,
        )
        for index in (1, 2)
    )
    codec = SyntheticCodec(
        name="bvp",
        key=PREDICTION_KEY,
        data_type="signal",
        schema="signal.bvp.v1",
    )

    result = export_record_requests(requests, CodecRegistry((codec,)))

    assert isinstance(result, ExportResult)
    assert len(result.record_results) == 2
    assert result.count(FieldExportOutcome.WRITTEN) == 2
    assert codec.save_calls == 2


def test_sample_artifact_export_record_rejects_metadata_selectors() -> None:
    with pytest.raises(RemotePhysOperationError):
        build_sample_artifact_record(
            sample=Sample({"predictions/signal.bvp.predicted": FieldValue(0.1)}),
            source_record=_record("record-001"),
            locators=("predictions/signal.bvp.predicted#confidence",),
        )


def _record(record_id: str) -> RecordRef:
    datasource = DataSourceRef("stage13-source")
    source = _field_ref("signal.bvp.reference", f"memory://{record_id}/reference")
    return RecordRef(datasource, record_id, {"signal.bvp.reference": source})


def _field_ref(key: str, uri: str) -> FieldRef:
    return FieldRef(
        key,
        (ResourceRef(uri, "memory"),),
        schema="signal.bvp.v1",
    )
