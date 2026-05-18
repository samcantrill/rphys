from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

from rphys.analysis import ReportOperation, ReportTable, VisualizationOperation, VisualizationOutput
from rphys.collections import CollectionItem
from rphys.data import (
    Batch,
    BatchCollater,
    BatchOutputFieldSpec,
    BatchOutputSpec,
    FieldValue,
    Sample,
    UncollatePlan,
    uncollate_batch_fields,
)
from rphys.data.collections import (
    PlannedSampleCollectionView,
    SampleCollection,
    SampleCollectionConcatPlan,
    SampleCollectionGroupPlan,
    SampleCollectionViewPlan,
)
from rphys.data.metadata import GROUP, SPLIT, SUBJECT_ID
from rphys.data.sample_builders import SampleBuilder
from rphys.data.sample_fields import SampleFieldState
from rphys.datasources.derived import DerivedDataSourceBuilder
from rphys.datasources.filters import DataSourceView
from rphys.datasources.indexes import (
    DataSourceIndex,
    IndexBuilder,
    IndexCandidatePlan,
    IndexPlan,
    build_index_candidates,
)
from rphys.datasources.splits import GroupBuilder, GroupPlan, SplitBuilder, SplitPlan
from rphys.datasources.validation import ValidationIOPolicy, validate_scan_result
from rphys.io.codecs import CodecCapabilities, CodecLoadResult, CodecRegistry, CodecSaveResult
from rphys.io.fields import FieldRef
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef
from rphys.learning import LoopContext, SupervisedLearner
from rphys.methods import Method, PredictionContext
from rphys.metrics import MetricContext, MetricContract, MetricInputSpec, MetricSampleOperation, MetricValue
from rphys.ops import (
    OperationContext,
    OperationPipeline,
    SampleCollectionConcatOperation,
    SampleCollectionGroupOperation,
    SampleCollectionViewOperation,
    SampleFieldPermissions,
    SampleOperationContract,
    SampleOperationContext,
    SampleOperationPipeline,
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
PREDICTION = "predictions/signal.bvp.stage14_tail"
PREDICTION_KEY = "signal.bvp.stage14_tail"
ERROR = "metrics/custom.stage14.tail_mae"
VISUALIZATION = "outputs/custom.stage14.tail_visualization"
DATASET_PREDICTION = "outputs/signal.bvp.stage14_record_prediction"


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


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


class ReloadedMaeMetric:
    contract = MetricContract(
        "stage14-tail-reloaded-mae",
        (
            MetricInputSpec(PREDICTION, role="prediction"),
            MetricInputSpec(TARGET, role="target"),
        ),
        level="sample",
        writes=(ERROR,),
    )

    def __call__(self, context: MetricContext) -> MetricValue:
        predicted = tuple(float(value) for value in context.fields.require(PREDICTION))
        target = tuple(float(value) for value in context.fields.require(TARGET))
        absolute_error = sum(abs(left - right) for left, right in zip(predicted, target)) / len(target)
        return MetricValue(
            FakeScalar(round(absolute_error, 6)),
            backend="fake",
            unit="bvp-amplitude",
            metadata={"scope": context.metadata["metric_scope"]},
        )


def test_stage14_scan_to_report_tail_uses_code_backed_stage13_apis(
    tmp_path: Path,
) -> None:
    scenario = make_synthetic_scenario(
        scenario_id="stage14-scan-to-report-tail",
        datasource_count=1,
        subjects=("subject-001", "subject-002"),
        records_per_subject=1,
        include_optional_fields=True,
    )
    index = _build_source_index(scenario)
    manifest = assert_index_manifest_round_trips(
        index,
        expected_schema_version="rphys.datasource_index.v1",
    )
    selected_items = (index[0], index[1])
    loaded_samples = tuple(
        SampleBuilder(
            registry=scenario.codec_registry(
                record_id=item.record.record_id,
                field_keys=REQUIRED_FIELD_KEYS,
            )
        ).build(item)
        for item in selected_items
    )
    prepared_samples = tuple(
        _prepare_pipeline()(
            sample,
            context=SampleOperationContext(metadata={"tier": "signal"}),
        ).output
        for sample in loaded_samples
    )
    batch = BatchCollater()(prepared_samples)
    method = ScaleBvpMethod(
        factor=1.05,
        output_spec=BatchOutputSpec(
            (
                BatchOutputFieldSpec(
                    "prediction",
                    PREDICTION,
                    expected_type=list,
                    schema="signal.bvp.v1",
                ),
            ),
            pass_through=(INPUT, TARGET),
        ),
    )
    learner = SupervisedLearner(method)
    prediction_batch = learner.step(
        batch,
        LoopContext(
            "predict",
            split="test",
            step_index=0,
            provenance={"scope": "stage14-scan-to-report-tail"},
        ),
    )
    uncollated = uncollate_batch_fields(
        prediction_batch,
        UncollatePlan(len(selected_items), (INPUT, PREDICTION, TARGET)),
    )
    reloaded = _export_and_reload_artifacts(
        tmp_path,
        samples=uncollated,
        source_records=tuple(item.record for item in selected_items),
    )
    assert reloaded[0].field(PREDICTION).state is SampleFieldState.UNLOADED
    report_table, formatted_records = _run_report_tail(
        reloaded,
        source_records=tuple(item.record for item in selected_items),
    )

    assert isinstance(method, Method)
    assert isinstance(prediction_batch, Batch)
    assert manifest.index_kind == "datasource_index"
    assert [sample.require(PREDICTION) for sample in uncollated] == prediction_batch.require(PREDICTION)
    assert reloaded[0].require(PREDICTION) == tuple(str(value) for value in uncollated[0].require(PREDICTION))
    assert report_table.name == "stage14-tail-report"
    assert report_table.metadata["stage14_phase"] == "scan_to_report_tail"
    assert [row.cells["subject_id"].value for row in report_table.rows] == ["subject-001", "subject-002"]
    assert all(
        row.cells["figure"].value.codec == "fake.visualization.stage14.tail.v1"
        for row in report_table.rows
    )
    assert [sample.require(DATASET_PREDICTION) for sample in formatted_records] == [
        reloaded[0].require(PREDICTION),
        reloaded[1].require(PREDICTION),
    ]
    _assert_legacy_stage13_surfaces_absent()


def _build_source_index(scenario) -> DataSourceIndex:
    datasource = scenario.datasources[0]
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
            metadata={"fixture_phase": "stage14_p4"},
        ),
    )
    groups = GroupBuilder(
        GroupPlan({"subject": SUBJECT_ID, "group": GROUP, "split": SPLIT})
    ).build(candidates.view)
    splits = SplitBuilder(
        SplitPlan(
            split_group="subject",
            group_to_split={
                str(record.metadata[SUBJECT_ID]): str(record.metadata[SPLIT])
                for record in scenario.records
            },
        )
    ).build(groups)
    return IndexBuilder(
        IndexPlan(
            "stage14-scan-to-report-tail-index",
            metadata={"fixture_phase": "stage14_p4"},
        )
    ).build(candidates.view, group_result=groups, split_result=splits).index


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
                name="prepare-stage14-tail-signal",
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


def _export_and_reload_artifacts(
    tmp_path: Path,
    *,
    samples: tuple[Sample, ...],
    source_records: tuple[object, ...],
) -> tuple[Sample, ...]:
    registry = CodecRegistry((_LocalTextCodec(),))
    target = ExportTarget(ResourceRef((tmp_path / "stage14-tail-derived").as_uri(), "file"), "tail-001")
    spec = ExportSpec(
        (BVP_KEY, PREDICTION_KEY),
        codec_requests={BVP_KEY: "stage14-tail-text", PREDICTION_KEY: "stage14-tail-text"},
    )
    requests = tuple(
        sample_artifact_export_request(
            sample=sample,
            source_record=record,
            locators=(TARGET, PREDICTION),
            field_refs={
                PREDICTION_KEY: FieldRef(
                    PREDICTION_KEY,
                    (ResourceRef(f"memory://{record.record_id}/stage14-tail", "memory"),),
                    schema="signal.bvp.v1",
                )
            },
            target=target,
            spec=spec,
            layout=OutputLayout(resource_suffix="txt"),
        )
        for sample, record in zip(samples, source_records)
    )
    export_result = export_record_requests(requests, registry)
    assembly = DerivedDataSourceBuilder(
        "stage14-tail-derived",
        source=target.root,
        metadata={"stage14_phase": "scan_to_report_tail"},
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
    index = IndexBuilder(IndexPlan("stage14-tail-derived-index")).build(candidates.view).index
    return tuple(SampleBuilder(registry=registry).build(item) for item in index)


def _run_report_tail(
    samples: tuple[Sample, ...],
    *,
    source_records: tuple[object, ...],
) -> tuple[ReportTable, tuple[Sample, ...]]:
    metric_operation = MetricSampleOperation(ReloadedMaeMetric(), name="stage14-tail-mae")
    metric_items = []
    for index, (sample, record) in enumerate(zip(samples, source_records)):
        item_metadata = {
            "sample_id": f"stage14-tail-sample-{index}",
            "subject_id": str(record.metadata[SUBJECT_ID]),
            "record_id": record.record_id,
            "split": str(record.metadata[SPLIT]),
            "window_start": index,
        }
        metric_result = metric_operation(
            sample,
            SampleOperationContext(
                metadata={"split": item_metadata["split"]},
                provenance={"source": "stage14-tail-derived"},
                sample_id=item_metadata["sample_id"],
            ),
        )
        metric_items.append(
            CollectionItem(
                metric_result.output,
                metadata=item_metadata,
                provenance={"recipe": "stage14-scan-to-report-tail"},
            )
        )

    metric_collection = SampleCollection(
        tuple(metric_items),
        metadata={"stage14_phase": "scan_to_report_tail"},
    )
    visualized = VisualizationOperation(
        lambda value, context: {
            VISUALIZATION: VisualizationOutput(
                "diagnostic-series",
                codec="fake.visualization.stage14.tail.v1",
                payload={
                    "sample_count": len(value),
                    "stage14_phase": context.metadata["stage14_phase"],
                },
                metadata={"stage14_phase": context.metadata["stage14_phase"]},
            )
        },
        name="stage14-tail-diagnostic-visualization",
    )(
        metric_collection,
        OperationContext(metadata={"stage14_phase": "scan_to_report_tail"}),
    ).output
    report_table = ReportOperation(_build_tail_report, name="stage14-tail-report")(
        visualized,
        OperationContext(metadata={"stage14_phase": "scan_to_report_tail"}),
    ).output
    grouped = SampleCollectionGroupOperation(
        SampleCollectionGroupPlan("group-stage14-tail-records", group_keys=("subject_id", "record_id"))
    )(visualized.entries).output
    format_pipeline = OperationPipeline(
        (
            SampleCollectionViewOperation(
                PlannedSampleCollectionView(
                    SampleCollectionViewPlan("order-stage14-tail-windows", sort_keys=("window_start",))
                )
            ),
            SampleCollectionConcatOperation(
                SampleCollectionConcatPlan(
                    "format-stage14-tail-record",
                    field_map={PREDICTION: DATASET_PREDICTION},
                ),
                payload_joiner=lambda payloads: tuple(value for payload in payloads for value in payload),
            ),
        )
    )
    formatted_records = tuple(format_pipeline(collection).output for collection in grouped)
    return report_table, formatted_records


def _build_tail_report(value: object, context: OperationContext) -> ReportTable:
    assert isinstance(value, SampleCollection)
    return ReportTable(
        "stage14-tail-report",
        columns=("sample_id", "subject_id", "mae", "figure", "split"),
        rows=(
            {
                "sample_id": entry.metadata["sample_id"],
                "subject_id": entry.metadata["subject_id"],
                "mae": entry.value.require(ERROR),
                "figure": entry.value.require(VISUALIZATION),
                "split": entry.metadata["split"],
            }
            for entry in value.entries
        ),
        metadata={"stage14_phase": context.metadata["stage14_phase"]},
        provenance={"source": "stage14-scan-to-report-tail"},
    )


class _LocalTextCodec:
    name = "stage14-tail-text"
    capabilities = CodecCapabilities(can_load=True, can_save=True)

    def supports_load(self, context: object) -> bool:
        field_view = context.field_view  # type: ignore[attr-defined]
        return str(field_view.field_ref.key) in {BVP_KEY, PREDICTION_KEY}

    def supports_save(self, value: FieldValue, context: object) -> bool:
        target = context.target  # type: ignore[attr-defined]
        return str(target.key) in {BVP_KEY, PREDICTION_KEY}

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


def _local_path(resource: ResourceRef) -> Path:
    parsed = urlparse(resource.uri)
    if parsed.scheme == "file":
        return Path(unquote(parsed.path))
    return Path(resource.uri)


def _assert_legacy_stage13_surfaces_absent() -> None:
    import rphys.analysis
    import rphys.evaluation
    import rphys.learning
    import rphys.methods
    import rphys.metrics
    import rphys.prediction

    modules = (
        rphys.analysis,
        rphys.evaluation,
        rphys.learning,
        rphys.methods,
        rphys.metrics,
        rphys.prediction,
    )
    for public_name in (
        "MethodOutput",
        "StepOutput",
        "MetricObservation",
        "MetricResult",
        "EvaluationRunner",
        "PredictionRunner",
        "ReportWriter",
    ):
        for module in modules:
            assert not hasattr(module, public_name)
