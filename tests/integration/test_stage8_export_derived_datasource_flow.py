from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse

from rphys.data.fields import FieldValue
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
from rphys.datasources.refs import RecordRef
from rphys.io.codecs import (
    CodecCapabilities,
    CodecLoadResult,
    CodecRegistry,
    CodecSaveResult,
    MetadataSavePolicy,
)
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef
from rphys.ops.export import (
    CodecSelectionOperation,
    ExportResult,
    ExportSpec,
    ExportTarget,
    OutputLayout,
    RecordExportRequest,
    SaveOperation,
)
from tests.support.synthetic_datasources import (
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def test_stage8_export_derived_datasource_round_trips_to_lazy_sample(
    tmp_path: Path,
) -> None:
    source_record = _source_record_with_prediction()
    registry = CodecRegistry((_LocalTextCodec(),))
    request = RecordExportRequest(
        source_record=source_record,
        field_values={
            "signal.bvp.reference": FieldValue(
                ("0.10", "0.20"),
                schema="signal.bvp.v1",
            ),
            "signal.bvp.predicted": FieldValue(
                ("0.11", "0.19"),
                schema="signal.bvp.v1",
            ),
        },
        spec=ExportSpec(
            ("signal.bvp.reference", "signal.bvp.predicted"),
            codec_requests={
                "signal.bvp.reference": "stage8-text",
                "signal.bvp.predicted": "stage8-text",
            },
        ),
        target=ExportTarget(ResourceRef((tmp_path / "derived").as_uri(), "file"), "exp-001"),
        layout=OutputLayout(resource_suffix="txt"),
    )

    selection = CodecSelectionOperation(registry).run(request).output
    record_result = SaveOperation(registry).run(selection).output
    export_result = ExportResult(
        spec=request.spec,
        target=request.target,
        layout=request.layout,
        policy=request.policy,
        record_results=(record_result,),
    )
    assembly = DerivedDataSourceBuilder(
        "stage8-derived",
        source=request.target.root,
        metadata={"stage": 8},
    ).from_export_result(export_result)

    view = DataSourceView(assembly.datasource, assembly.records)
    candidates = build_index_candidates(
        view,
        IndexCandidatePlan(
            {
                "targets/signal.bvp.reference": "signal.bvp.reference",
                "predictions/signal.bvp.predicted": "signal.bvp.predicted",
            }
        ),
    )
    index = IndexBuilder(IndexPlan("stage8-derived-index")).build(candidates.view).index
    sample = SampleBuilder(registry=registry).build(index[0])

    assert len(index) == 1
    assert index.entry_at(0).datasource_id == "stage8-derived"
    assert sample.field("targets/signal.bvp.reference").state is SampleFieldState.UNLOADED
    assert sample.require("targets/signal.bvp.reference") == ("0.10", "0.20")
    assert sample.require("predictions/signal.bvp.predicted") == ("0.11", "0.19")
    assert (
        sample.field("targets/signal.bvp.reference").provenance.record
        == assembly.records[0]
    )
    assert source_record.datasource.datasource_id == "stage8-source"
    assert source_record.record_id == "subject-001/record-001"


class _LocalTextCodec:
    name = "stage8-text"
    capabilities = CodecCapabilities(
        can_load=True,
        can_save=True,
        metadata_policies=(MetadataSavePolicy.REFERENCE_ONLY,),
    )

    def supports_load(self, context: object) -> bool:
        field_view = context.field_view  # type: ignore[attr-defined]
        return str(field_view.field_ref.key) in {
            "signal.bvp.reference",
            "signal.bvp.predicted",
        }

    def supports_save(self, value: FieldValue, context: object) -> bool:
        return str(context.target.key) in {  # type: ignore[attr-defined]
            "signal.bvp.reference",
            "signal.bvp.predicted",
        }

    def load(self, context: object) -> CodecLoadResult:
        field_view = context.field_view  # type: ignore[attr-defined]
        path = _local_path(field_view.field_ref.resources[0])
        payload = tuple(path.read_text(encoding="utf-8").splitlines())
        return CodecLoadResult(
            FieldValue(
                payload,
                schema=field_view.field_ref.schema,
                metadata={"codec": self.name},
            ),
            metadata={"codec": self.name},
        )

    def save(self, value: FieldValue, context: object) -> CodecSaveResult:
        target = context.target  # type: ignore[attr-defined]
        path = _local_path(target.resources[0])
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value.payload, tuple):
            lines = [str(item) for item in value.payload]
        else:
            lines = [str(value.payload)]
        path.write_text("\n".join(lines), encoding="utf-8")
        return CodecSaveResult(target, metadata={"codec": self.name})


def _source_record_with_prediction() -> RecordRef:
    datasource = synthetic_datasource_ref("stage8-source")
    base = synthetic_record_ref(datasource, "subject-001/record-001")
    fields = dict(base.fields)
    fields["signal.bvp.predicted"] = FieldRef(
        "signal.bvp.predicted",
        (ResourceRef("memory://subject-001/record-001/predicted", "memory"),),
        schema="signal.bvp.v1",
    )
    return RecordRef(
        datasource,
        base.record_id,
        fields,
        metadata=base.metadata,
    )


def _local_path(resource: ResourceRef) -> Path:
    parsed = urlparse(resource.uri)
    if parsed.scheme == "file":
        return Path(unquote(parsed.path))
    return Path(resource.uri)
