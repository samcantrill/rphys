from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

from rphys.analysis import ReportOperation, ReportTable, VisualizationOperation, VisualizationOutput
from rphys.collections import CollectionItem
from rphys.data import Batch, FieldValue, Sample, UncollatePlan, uncollate_batch_fields
from rphys.data.collections import (
    PlannedSampleCollectionView,
    SampleCollection,
    SampleCollectionConcatPlan,
    SampleCollectionGroupPlan,
    SampleCollectionViewPlan,
)
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
from rphys.metrics import MetricContext, MetricContract, MetricInputSpec, MetricSampleOperation, MetricValue
from rphys.ops import (
    OperationContext,
    OperationPipeline,
    SampleCollectionConcatOperation,
    SampleCollectionGroupOperation,
    SampleCollectionViewOperation,
    SampleOperationContext,
)
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
ERROR = "metrics/custom.stage13.reloaded.mae"
VISUALIZATION = "outputs/custom.stage13.visualization.reloaded"
DATASET_PREDICTION = "outputs/signal.bvp.dataset.predicted"


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

    report_table, formatted_records = _run_reloaded_artifact_recipes(tuple(reloaded))

    assert report_table.rows[0].cells["sample_id"].value == "sample-0"
    assert report_table.rows[0].cells["mae"].value.value == FakeScalar(0.01)
    assert report_table.rows[0].cells["figure"].value.codec == "fake.visualization.stage13.reloaded.v1"
    assert [sample.require(DATASET_PREDICTION) for sample in formatted_records] == [
        ("0.11", "0.19"),
        ("0.31", "0.29"),
    ]


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


class ReloadedMaeMetric:
    contract = MetricContract(
        "reloaded-sequence-mae",
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
            FakeScalar(round(absolute_error, 2)),
            backend="fake",
            unit="bpm",
            metadata={"scope": context.metadata["metric_scope"]},
        )


def _run_reloaded_artifact_recipes(samples: tuple[Sample, ...]) -> tuple[ReportTable, tuple[Sample, ...]]:
    metric_operation = MetricSampleOperation(ReloadedMaeMetric(), name="reloaded-mae")
    metric_items = []
    for index, sample in enumerate(samples):
        item_metadata = {
            "sample_id": f"sample-{index}",
            "subject_id": f"subject-{index + 1:03d}",
            "record_id": "record-001",
            "split": "test",
            "window_start": index,
        }
        metric_result = metric_operation(
            sample,
            SampleOperationContext(
                metadata={"split": "test"},
                provenance={"source": "reloaded-sample-artifact"},
                sample_id=item_metadata["sample_id"],
            ),
        )
        metric_items.append(
            CollectionItem(
                metric_result.output,
                metadata=item_metadata,
                provenance={"recipe": "reloaded-artifact"},
            )
        )

    metric_collection = SampleCollection(tuple(metric_items), metadata={"split": "test"})
    visualized = VisualizationOperation(
        lambda value, context: {
            VISUALIZATION: VisualizationOutput(
                "diagnostic-series",
                codec="fake.visualization.stage13.reloaded.v1",
                payload={
                    "sample_count": len(value),
                    "split": context.metadata["split"],
                },
            )
        },
        name="reloaded-diagnostic-visualization",
    )(metric_collection, OperationContext(metadata={"split": "test"})).output

    report_table = ReportOperation(_build_reloaded_report, name="reloaded-report")(
        visualized,
        OperationContext(metadata={"split": "test"}),
    ).output
    grouped = SampleCollectionGroupOperation(
        SampleCollectionGroupPlan("group-reloaded-records", group_keys=("subject_id", "record_id"))
    )(visualized.entries).output
    format_pipeline = OperationPipeline(
        (
            SampleCollectionViewOperation(
                PlannedSampleCollectionView(
                    SampleCollectionViewPlan("order-reloaded-windows", sort_keys=("window_start",))
                )
            ),
            SampleCollectionConcatOperation(
                SampleCollectionConcatPlan(
                    "format-reloaded-dataset-record",
                    field_map={PREDICTION: DATASET_PREDICTION},
                ),
                payload_joiner=lambda payloads: tuple(value for payload in payloads for value in payload),
            ),
        )
    )
    formatted_records = tuple(format_pipeline(collection).output for collection in grouped)
    return report_table, formatted_records


def _build_reloaded_report(value: object, context: OperationContext) -> ReportTable:
    assert isinstance(value, SampleCollection)
    return ReportTable(
        "reloaded-artifact-metrics",
        columns=("sample_id", "subject_id", "mae", "figure", "split"),
        rows=(
            {
                "sample_id": entry.metadata["sample_id"],
                "subject_id": entry.metadata["subject_id"],
                "mae": entry.value.require(ERROR),
                "figure": entry.value.require(VISUALIZATION),
                "split": context.metadata["split"],
            }
            for entry in value.entries
        ),
        metadata={"split": context.metadata["split"]},
        provenance={"source": "sample-artifact-datasource"},
    )


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
