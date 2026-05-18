from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

from rphys.data import (
    Batch,
    BatchCollater,
    BatchOutputFieldSpec,
    BatchOutputSpec,
    FieldValue,
    Sample,
)
from rphys.data.metadata import GROUP, SPLIT, SUBJECT_ID
from rphys.data.sample_builders import SampleBuilder
from rphys.data.sample_fields import SampleFieldState
from rphys.datasources.derived import DerivedDataSourceBuilder
from rphys.datasources.filters import DataSourceView
from rphys.datasources.indexes import (
    CompositeDataSourceIndex,
    DataSourceIndex,
    IndexBuilder,
    IndexCandidatePlan,
    IndexPlan,
    build_index_candidates,
)
from rphys.datasources.splits import GroupBuilder, GroupPlan, SplitBuilder, SplitPlan
from rphys.datasources.validation import ValidationIOPolicy, validate_scan_result
from rphys.io.codecs import (
    CodecCapabilities,
    CodecLoadResult,
    CodecRegistry,
    CodecSaveResult,
    MetadataSavePolicy,
)
from rphys.io.fields import FieldRef
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef
from rphys.methods import Method, PredictionContext
from rphys.ops import (
    SampleFieldPermissions,
    SampleOperationContract,
    SampleOperationPipeline,
    SampleOperationContext,
    SampleTransform,
)
from rphys.ops.export import (
    ExportSpec,
    ExportTarget,
    OutputLayout,
    export_record_requests,
    sample_artifact_export_request,
)

from tests.support.contract_assertions import assert_index_manifest_round_trips
from tests.support.synthetic_catalog import (
    BVP_KEY,
    REQUIRED_FIELD_KEYS,
    TIMESTAMPS_KEY,
    VIDEO_KEY,
    make_synthetic_scenario,
)


INPUT = "inputs/signal.bvp.source"
TARGET = "targets/signal.bvp.reference"
PREDICTION = "predictions/signal.bvp.upstream"
PREDICTION_KEY = "signal.bvp.upstream"


@dataclass(slots=True)
class ScaleBvpMethod:
    factor: float
    output_spec: BatchOutputSpec

    def predict(self, batch: Batch, *, context: PredictionContext | None = None) -> Batch:
        predictions = [
            tuple(round(float(value) * self.factor, 6) for value in window)
            for window in batch.require(INPUT)
        ]
        return self.output_spec.build({"prediction": predictions}, base=batch)


def test_stage14_upstream_smoke_uses_one_public_loader_path_before_stage13_tail(
    tmp_path: Path,
) -> None:
    scenario = make_synthetic_scenario(
        scenario_id="stage14-upstream-smoke",
        datasource_count=2,
        subjects=("subject-001", "subject-002"),
        records_per_subject=1,
        include_optional_fields=True,
    )
    child_indexes = _build_child_indexes(scenario)
    composite = CompositeDataSourceIndex(
        "stage14-upstream-smoke-composite",
        child_indexes,
        metadata={
            "stage14_phase": "upstream_smoke",
            "completion_scope": "incomplete_before_stage13_tail",
        },
    )
    manifest = assert_index_manifest_round_trips(
        child_indexes["synthetic-source-001"],
        expected_schema_version="rphys.datasource_index.v1",
    )
    assert manifest.index_kind == "datasource_index"

    selected_items = (composite[0], composite[1])
    samples = tuple(
        SampleBuilder(
            registry=scenario.codec_registry(
                record_id=item.record.record_id,
                field_keys=REQUIRED_FIELD_KEYS,
            )
        ).build(item)
        for item in selected_items
    )
    prepared = tuple(
        _prepare_pipeline()(
            sample,
            context=SampleOperationContext(metadata={"tier": "smoke"}),
        ).output
        for sample in samples
    )
    batch = BatchCollater()(prepared)
    method = ScaleBvpMethod(
        factor=1.1,
        output_spec=BatchOutputSpec(
            (
                BatchOutputFieldSpec(
                    "prediction",
                    PREDICTION,
                    expected_type=list,
                    schema="signal.bvp.v1",
                ),
            ),
            pass_through=(TARGET,),
        ),
    )
    prediction_batch = method.predict(
        batch,
        context=PredictionContext(
            provenance={"scope": "stage14-upstream-before-stage13-tail"}
        ),
    )
    reloaded = _export_and_reload_first_prediction(
        tmp_path,
        source_record=selected_items[0].record,
        target_values=prediction_batch.require(TARGET)[0],
        prediction_values=prediction_batch.require(PREDICTION)[0],
    )

    assert isinstance(method, Method)
    assert len(composite) == 4
    assert composite.entry_at(0).groups["subject"] == "subject-001"
    assert composite.entry_at(1).groups["subject"] == "subject-002"
    assert batch.require(INPUT) == [
        scenario.payload_for(selected_items[0].record.record_id, BVP_KEY)[:2],
        scenario.payload_for(selected_items[1].record.record_id, BVP_KEY)[:2],
    ]
    assert prediction_batch.require(PREDICTION)[0] == tuple(
        round(float(value) * 1.1, 6)
        for value in scenario.payload_for(selected_items[0].record.record_id, BVP_KEY)[:2]
    )
    assert reloaded.field("predictions/signal.bvp.upstream").state is SampleFieldState.UNLOADED
    assert reloaded.require("predictions/signal.bvp.upstream") == tuple(
        str(value) for value in prediction_batch.require(PREDICTION)[0]
    )


def _build_child_indexes(scenario) -> dict[str, DataSourceIndex]:
    split_by_subject = {
        str(record.metadata[SUBJECT_ID]): str(record.metadata[SPLIT])
        for record in scenario.records
    }
    indexes: dict[str, DataSourceIndex] = {}
    for datasource in scenario.datasources:
        scan_result = scenario.scan_result_for(datasource.datasource_id)
        report = validate_scan_result(
            scan_result,
            spec=scenario.spec_for(datasource.datasource_id),
            policy=ValidationIOPolicy.no_io(),
            required_metadata=(SUBJECT_ID, GROUP, SPLIT),
        )
        assert report.passed
        candidates = build_index_candidates(
            DataSourceView(scan_result.datasource, scan_result.records),
            IndexCandidatePlan(
                {
                    "inputs/video.rgb": VIDEO_KEY,
                    TARGET: BVP_KEY,
                    "metadata/timestamps.video": TIMESTAMPS_KEY,
                },
                field_indexes={
                    VIDEO_KEY: TemporalIndexSlice(0, 2),
                    BVP_KEY: TemporalIndexSlice(0, 2),
                    TIMESTAMPS_KEY: TemporalIndexSlice(0, 2),
                },
                metadata={"fixture_phase": "stage14_p3"},
            ),
        )
        groups = GroupBuilder(
            GroupPlan({"subject": SUBJECT_ID, "group": GROUP, "split": SPLIT})
        ).build(candidates.view)
        splits = SplitBuilder(
            SplitPlan(split_group="subject", group_to_split=split_by_subject)
        ).build(groups)
        indexes[datasource.datasource_id] = IndexBuilder(
            IndexPlan(
                f"{datasource.datasource_id}-stage14-upstream-index",
                metadata={"fixture_phase": "stage14_p3"},
            )
        ).build(
            candidates.view,
            group_result=groups,
            split_result=splits,
        ).index
    return indexes


def _prepare_pipeline() -> SampleOperationPipeline:
    def prepare_signal(sample, *, context) -> object:
        window = tuple(float(value) for value in sample.require(TARGET))
        sample.set_field(
            INPUT,
            FieldValue(
                window,
                schema="signal.bvp.v1",
                metadata={"prepared_by": context.metadata["tier"]},
                collate_policy="list",
            ),
        )
        sample.set_field(
            TARGET,
            FieldValue(
                window,
                schema="signal.bvp.v1",
                metadata={"prepared_by": context.metadata["tier"]},
                collate_policy="list",
            ),
        )
        sample.delete_field("inputs/video.rgb")
        sample.delete_field("metadata/timestamps.video")
        return sample

    return SampleOperationPipeline(
        {
            "prepare-signal": SampleTransform(
                prepare_signal,
                name="prepare-stage14-upstream-signal",
                contract=SampleOperationContract(
                    field_permissions=SampleFieldPermissions(
                        reads=(TARGET,),
                        writes=(INPUT, TARGET),
                        deletes=("inputs/video.rgb", "metadata/timestamps.video"),
                    ),
                    required_context=("tier",),
                ),
            )
        }
    )


def _export_and_reload_first_prediction(
    tmp_path: Path,
    *,
    source_record,
    target_values: tuple[float, ...],
    prediction_values: tuple[float, ...],
) -> object:
    registry = CodecRegistry((_LocalTextCodec(),))
    target = ExportTarget(ResourceRef((tmp_path / "upstream-derived").as_uri(), "file"), "smoke-001")
    sample = Sample(
        {
            TARGET: FieldValue(tuple(str(value) for value in target_values), schema="signal.bvp.v1"),
            PREDICTION: FieldValue(
                tuple(str(value) for value in prediction_values),
                schema="signal.bvp.v1",
            ),
        }
    )
    request = sample_artifact_export_request(
        sample=sample,
        source_record=source_record,
        locators=(TARGET, PREDICTION),
        field_refs={
            PREDICTION_KEY: FieldRef(
                PREDICTION_KEY,
                (ResourceRef(f"memory://{source_record.record_id}/upstream", "memory"),),
                schema="signal.bvp.v1",
            )
        },
        spec=ExportSpec(
            (BVP_KEY, PREDICTION_KEY),
            codec_requests={BVP_KEY: "stage14-text", PREDICTION_KEY: "stage14-text"},
        ),
        target=target,
        layout=OutputLayout(resource_suffix="txt"),
    )
    export_result = export_record_requests((request,), registry)
    assembly = DerivedDataSourceBuilder(
        "stage14-upstream-derived",
        source=target.root,
        metadata={"stage14_phase": "upstream_smoke"},
    ).from_export_result(export_result)
    candidates = build_index_candidates(
        DataSourceView(assembly.datasource, assembly.records),
        IndexCandidatePlan(
            {
                TARGET: BVP_KEY,
                PREDICTION: PREDICTION_KEY,
            }
        ),
    )
    index = IndexBuilder(IndexPlan("stage14-upstream-derived-index")).build(
        candidates.view
    ).index
    return SampleBuilder(registry=registry).build(index[0])


class _LocalTextCodec:
    name = "stage14-text"
    capabilities = CodecCapabilities(
        can_load=True,
        can_save=True,
        metadata_policies=(MetadataSavePolicy.REFERENCE_ONLY,),
    )

    def supports_load(self, context: object) -> bool:
        field_view = context.field_view  # type: ignore[attr-defined]
        return str(field_view.field_ref.key) in {BVP_KEY, PREDICTION_KEY}

    def supports_save(self, value: FieldValue, context: object) -> bool:
        return str(context.target.key) in {BVP_KEY, PREDICTION_KEY}  # type: ignore[attr-defined]

    def load(self, context: object) -> CodecLoadResult:
        field_view = context.field_view  # type: ignore[attr-defined]
        path = _local_path(field_view.field_ref.resources[0])
        return CodecLoadResult(
            FieldValue(
                tuple(path.read_text(encoding="utf-8").splitlines()),
                schema=field_view.field_ref.schema,
                metadata={"codec": self.name},
            ),
            metadata={"codec": self.name},
        )

    def save(self, value: FieldValue, context: object) -> CodecSaveResult:
        target = context.target  # type: ignore[attr-defined]
        path = _local_path(target.resources[0])
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [str(item) for item in value.payload]
        path.write_text("\n".join(lines), encoding="utf-8")
        return CodecSaveResult(target, metadata={"codec": self.name})


def _local_path(resource: ResourceRef) -> Path:
    parsed = urlparse(resource.uri)
    if parsed.scheme == "file":
        return Path(unquote(parsed.path))
    return Path(resource.uri)
