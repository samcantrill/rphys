from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse

from rphys.data import Batch, FieldValue, UncollatePlan, uncollate_batch_fields
from rphys.data.sample_builders import SampleBuilder
from rphys.data.sample_fields import SampleFieldState
from rphys.datasources.derived import DerivedDataSourceBuilder
from rphys.datasources.filters import DataSourceView
from rphys.datasources.indexes import (
    IndexBuilder,
    IndexCandidatePlan,
    IndexPlan,
    build_index_candidates,
)
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.io.codecs import CodecCapabilities, CodecLoadResult, CodecRegistry, CodecSaveResult
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef
from rphys.ops.export import (
    ExportSpec,
    ExportTarget,
    export_record_requests,
    sample_artifact_export_request,
)


PREDICTION = "predictions/signal.bvp.predicted"
PREDICTION_KEY = "signal.bvp.predicted"
TARGET = "targets/signal.bvp.reference"
TARGET_KEY = "signal.bvp.reference"


def test_stage13_uncollates_exports_and_reloads_sample_artifacts(tmp_path: Path) -> None:
    batch = Batch(
        {
            PREDICTION: FieldValue(
                [("0.11", "0.19"), ("0.31", "0.29")],
                schema="signal.bvp.v1",
            ),
            TARGET: FieldValue(
                [("0.10", "0.20"), ("0.30", "0.30")],
                schema="signal.bvp.v1",
            ),
        }
    )
    samples = uncollate_batch_fields(
        batch,
        UncollatePlan(2, (PREDICTION, TARGET)),
    )
    source_records = (_record("subject-001/record-001"), _record("subject-002/record-001"))
    target = ExportTarget(ResourceRef((tmp_path / "derived").as_uri(), "file"), "exp-001")
    spec = ExportSpec(
        (TARGET_KEY, PREDICTION_KEY),
        codec_requests={TARGET_KEY: "stage13-text", PREDICTION_KEY: "stage13-text"},
    )
    requests = tuple(
        sample_artifact_export_request(
            sample=sample,
            source_record=record,
            locators=(TARGET, PREDICTION),
            field_refs={
                PREDICTION_KEY: FieldRef(
                    PREDICTION_KEY,
                    (ResourceRef(f"memory://{record.record_id}/predicted", "memory"),),
                    schema="signal.bvp.v1",
                )
            },
            target=target,
            spec=spec,
        )
        for sample, record in zip(samples, source_records)
    )

    export_result = export_record_requests(requests, CodecRegistry((_LocalTextCodec(),)))
    assembly = DerivedDataSourceBuilder(
        "stage13-derived",
        source=target.root,
        metadata={"stage": 13},
    ).from_export_result(export_result)
    view = DataSourceView(assembly.datasource, assembly.records)
    candidates = build_index_candidates(
        view,
        IndexCandidatePlan(
            {
                TARGET: TARGET_KEY,
                PREDICTION: PREDICTION_KEY,
            }
        ),
    )
    index = IndexBuilder(IndexPlan("stage13-derived-index")).build(candidates.view).index
    registry = CodecRegistry((_LocalTextCodec(),))
    reloaded = [SampleBuilder(registry=registry).build(item) for item in index]

    assert len(samples) == 2
    assert assembly.record_count == 2
    assert len(index) == 2
    assert reloaded[0].field(PREDICTION).state is SampleFieldState.UNLOADED
    assert reloaded[0].require(PREDICTION) == ("0.11", "0.19")
    assert reloaded[1].require(TARGET) == ("0.30", "0.30")
    assert reloaded[0].field(PREDICTION).provenance.record == assembly.records[0]


class _LocalTextCodec:
    name = "stage13-text"
    capabilities = CodecCapabilities(can_load=True, can_save=True)

    def supports_load(self, context: object) -> bool:
        field_view = context.field_view  # type: ignore[attr-defined]
        return str(field_view.field_ref.key) in {TARGET_KEY, PREDICTION_KEY}

    def supports_save(self, value: FieldValue, context: object) -> bool:
        target = context.target  # type: ignore[attr-defined]
        return str(target.key) in {TARGET_KEY, PREDICTION_KEY}

    def load(self, context: object) -> CodecLoadResult:
        field_view = context.field_view  # type: ignore[attr-defined]
        path = _local_path(field_view.field_ref.resources[0])
        return CodecLoadResult(
            FieldValue(
                tuple(path.read_text(encoding="utf-8").splitlines()),
                schema=field_view.field_ref.schema,
            ),
            metadata={"codec": self.name},
        )

    def save(self, value: FieldValue, context: object) -> CodecSaveResult:
        target = context.target  # type: ignore[attr-defined]
        path = _local_path(target.resources[0])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(str(item) for item in value.payload), encoding="utf-8")
        return CodecSaveResult(target, metadata={"codec": self.name})


def _record(record_id: str) -> RecordRef:
    datasource = DataSourceRef("stage13-source")
    return RecordRef(
        datasource,
        record_id,
        {
            TARGET_KEY: FieldRef(
                TARGET_KEY,
                (ResourceRef(f"memory://{record_id}/reference", "memory"),),
                schema="signal.bvp.v1",
            )
        },
    )


def _local_path(resource: ResourceRef) -> Path:
    parsed = urlparse(resource.uri)
    if parsed.scheme == "file":
        return Path(unquote(parsed.path))
    return Path(resource.uri)
