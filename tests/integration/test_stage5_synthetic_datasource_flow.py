from __future__ import annotations

from dataclasses import dataclass

from rphys.data.metadata import SOURCE_ID, SUBJECT_ID
from rphys.data.sample_builders import SampleBuilder
from rphys.data.sample_fields import SampleFieldState
from rphys.datasources.adapters import DataSourceSpec
from rphys.datasources.filters import (
    DataSourceView,
    FilterChain,
    FilterDecision,
    build_view,
)
from rphys.datasources.indexes import (
    CompositeDataSourceIndex,
    DataSourceIndex,
    DataSourceIndexCodec,
    IndexBuilder,
    IndexCandidate,
    IndexCandidatePlan,
    IndexPlan,
    build_index_candidates,
    filter_index_candidates,
)
from rphys.datasources.refs import RecordRef
from rphys.datasources.splits import GroupBuilder, GroupPlan, SplitBuilder, SplitPlan
from rphys.datasources.validation import ValidationIOPolicy, validate_scan_result
from rphys.io.codecs import CodecRegistry
from rphys.io.indexes import TemporalIndexSlice
from tests.support.synthetic_codecs import SyntheticCodec
from tests.support.synthetic_datasources import (
    SyntheticScanAdapter,
    synthetic_datasource_ref,
    synthetic_record_ref,
)


@dataclass(frozen=True, slots=True)
class _ChildFlow:
    index: DataSourceIndex
    report_record_count: int
    view_excluded_ids: dict[str, str]
    candidate_excluded_ids: dict[str, str]


class _SubjectFilter:
    def __init__(self, subject_id: str) -> None:
        self.subject_id = subject_id

    def evaluate(self, record: object) -> FilterDecision:
        if not isinstance(record, RecordRef):
            return FilterDecision(False, "not_record")
        return FilterDecision(
            record.metadata.get(SUBJECT_ID) == self.subject_id,
            "subject_not_selected",
        )


class _FirstRecordCandidateFilter:
    def evaluate(self, candidate: object) -> FilterDecision:
        if not isinstance(candidate, IndexCandidate):
            return FilterDecision(False, "not_candidate")
        return FilterDecision(
            candidate.record.record_id.endswith("record-001"),
            "candidate_not_selected",
        )


def test_stage5_synthetic_datasource_vertical_slice_round_trips_to_sample() -> None:
    codec = DataSourceIndexCodec()
    left = _build_child_index(
        "left-index",
        datasource_id="left-source",
        subject_id="subject-left",
        split="train",
        codec=codec,
    )
    right = _build_child_index(
        "right-index",
        datasource_id="right-source",
        subject_id="subject-right",
        split="valid",
        codec=codec,
    )
    composite = CompositeDataSourceIndex(
        "stage-5-composite",
        {"left": left.index, "right": right.index},
        metadata={"stage": 5},
    )

    loaded = codec.loads(codec.dumps(composite))

    assert isinstance(loaded, CompositeDataSourceIndex)
    assert left.report_record_count == 3
    assert left.view_excluded_ids == {"unused-left/record-001": "subject_not_selected"}
    assert left.candidate_excluded_ids == {
        "subject-left/record-002": "candidate_not_selected"
    }
    assert loaded.entry_at(0).source_key == "left"
    assert loaded.entry_at(0).child_index_id == "left-index"
    assert loaded.entry_at(0).child_position == 0
    assert loaded.entry_at(0).split == "train"
    assert loaded.entry_at(1).source_key == "right"
    assert loaded.entry_at(1).split == "valid"
    assert "source_key" not in loaded[0].to_dict()["metadata"]

    sample = SampleBuilder(registry=_registry()).build(loaded[0])

    assert sample.field("inputs/video.rgb").state is SampleFieldState.UNLOADED
    assert sample.require("inputs/video.rgb") == ("f0", "f1")
    assert sample.require("targets/signal.bvp.reference") == (0.1, 0.2)
    assert sample.field("inputs/video.rgb").provenance.record.to_dict() == loaded[
        0
    ].record.to_dict()


def _build_child_index(
    index_id: str,
    *,
    datasource_id: str,
    subject_id: str,
    split: str,
    codec: DataSourceIndexCodec,
) -> _ChildFlow:
    datasource = synthetic_datasource_ref(datasource_id)
    records = [
        synthetic_record_ref(
            datasource,
            f"{subject_id}/record-001",
            subject_id=subject_id,
        ),
        synthetic_record_ref(
            datasource,
            f"{subject_id}/record-002",
            subject_id=subject_id,
        ),
        synthetic_record_ref(
            datasource,
            f"unused-{datasource_id.split('-')[0]}/record-001",
            subject_id=f"unused-{datasource_id}",
        ),
    ]
    spec = DataSourceSpec(
        datasource,
        required_fields=("video.rgb", "signal.bvp.reference"),
        metadata={"stage": 5},
    )
    scan_result = SyntheticScanAdapter(records).scan(spec)
    report = validate_scan_result(
        scan_result,
        spec=spec,
        policy=ValidationIOPolicy.no_io(),
        required_metadata=(SUBJECT_ID,),
    )
    view_result = build_view(scan_result)
    filtered_records = FilterChain(
        [_SubjectFilter(subject_id)],
        target_kind="record",
    ).apply(
        view_result.view.records,
        id_of=lambda record: record.record_id,  # type: ignore[attr-defined]
    )
    filtered_view = DataSourceView(scan_result.datasource, filtered_records.included)
    candidate_result = build_index_candidates(
        filtered_view,
        IndexCandidatePlan(
            {
                "inputs/video.rgb": "video.rgb",
                "targets/signal.bvp.reference": "signal.bvp.reference",
            },
            field_indexes={
                "video.rgb": TemporalIndexSlice(0, 2),
                "signal.bvp.reference": TemporalIndexSlice(0, 2),
            },
            metadata={"flow": "stage-5"},
        ),
    )
    selected_candidates = filter_index_candidates(
        candidate_result.view,
        FilterChain([_FirstRecordCandidateFilter()], target_kind="candidate"),
    )
    groups = GroupBuilder(GroupPlan({"subject": SUBJECT_ID, "source": SOURCE_ID})).build(
        selected_candidates.view
    )
    splits = SplitBuilder(
        SplitPlan(
            split_group="subject",
            group_to_split={subject_id: split},
        )
    ).build(groups)
    index = IndexBuilder(IndexPlan(index_id, metadata={"source": datasource_id})).build(
        selected_candidates.view,
        group_result=groups,
        split_result=splits,
    ).index
    loaded_index = codec.loads(codec.dumps(index))

    assert report.passed
    assert isinstance(loaded_index, DataSourceIndex)
    assert loaded_index.entry_at(0).groups["subject"] == subject_id

    return _ChildFlow(
        index=loaded_index,
        report_record_count=report.record_count,
        view_excluded_ids=dict(filtered_records.excluded_ids),
        candidate_excluded_ids=dict(selected_candidates.rejected_candidate_ids),
    )


def _registry() -> CodecRegistry:
    return CodecRegistry(
        [
            SyntheticCodec(name="video", payload=("f0", "f1", "f2", "f3")),
            SyntheticCodec(
                name="bvp",
                key="signal.bvp.reference",
                data_type="signal",
                schema="signal.bvp.v1",
                payload=(0.1, 0.2, 0.3, 0.4),
            ),
        ]
    )
