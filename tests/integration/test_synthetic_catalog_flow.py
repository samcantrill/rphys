from __future__ import annotations

from rphys.data.metadata import GROUP, SPLIT, SUBJECT_ID
from rphys.data.sample_builders import SampleBuilder
from rphys.data.sample_fields import SampleFieldState
from rphys.datasources.filters import DataSourceView
from rphys.datasources.indexes import (
    CompositeDataSourceIndex,
    IndexBuilder,
    IndexCandidatePlan,
    IndexPlan,
    build_index_candidates,
)
from rphys.datasources.splits import GroupBuilder, GroupPlan, SplitBuilder, SplitPlan
from rphys.datasources.validation import ValidationIOPolicy, validate_scan_result
from rphys.io.indexes import TemporalIndexSlice

from tests.support.synthetic_catalog import (
    BVP_KEY,
    REQUIRED_FIELD_KEYS,
    TIMESTAMPS_KEY,
    VIDEO_KEY,
    make_synthetic_scenario,
)


def test_synthetic_catalog_composes_through_scan_index_and_sample_builder() -> None:
    scenario = make_synthetic_scenario(
        datasource_count=2,
        subjects=("subject-001", "subject-002"),
        records_per_subject=2,
        include_optional_fields=True,
    )
    split_by_subject = {
        str(record.metadata[SUBJECT_ID]): str(record.metadata[SPLIT])
        for record in scenario.records
    }
    child_indexes = {}

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
                    "targets/signal.bvp.reference": BVP_KEY,
                    "metadata/timestamps.video": TIMESTAMPS_KEY,
                },
                field_indexes={
                    VIDEO_KEY: TemporalIndexSlice(0, 2),
                    BVP_KEY: TemporalIndexSlice(0, 2),
                    TIMESTAMPS_KEY: TemporalIndexSlice(0, 2),
                },
                metadata={"fixture_phase": "stage14_p1"},
            ),
        )
        groups = GroupBuilder(
            GroupPlan({"subject": SUBJECT_ID, "group": GROUP, "split": SPLIT})
        ).build(candidates.view)
        splits = SplitBuilder(
            SplitPlan(split_group="subject", group_to_split=split_by_subject)
        ).build(groups)
        child_indexes[datasource.datasource_id] = IndexBuilder(
            IndexPlan(f"{datasource.datasource_id}-index")
        ).build(
            candidates.view,
            group_result=groups,
            split_result=splits,
        ).index

    composite = CompositeDataSourceIndex("stage14-catalog-composite", child_indexes)
    first_item = composite[0]
    first_entry = composite.entry_at(0)
    first_record_id = first_item.record.record_id
    sample = SampleBuilder(
        registry=scenario.codec_registry(
            record_id=first_record_id,
            field_keys=REQUIRED_FIELD_KEYS,
        )
    ).build(first_item)

    assert len(composite) == 8
    assert first_entry.source_key == "synthetic-source-001"
    assert first_entry.groups["subject"] == "subject-001"
    assert first_entry.groups["group"] == "cohort-1"
    assert first_entry.split == "train"
    assert sample.field("inputs/video.rgb").state is SampleFieldState.UNLOADED
    assert sample.require("inputs/video.rgb") == scenario.payload_for(
        first_record_id,
        VIDEO_KEY,
    )[:2]
    assert sample.require("targets/signal.bvp.reference") == scenario.payload_for(
        first_record_id,
        BVP_KEY,
    )[:2]
    assert sample.require("metadata/timestamps.video") == scenario.payload_for(
        first_record_id,
        TIMESTAMPS_KEY,
    )[:2]
    assert (
        sample.field("targets/signal.bvp.reference").provenance.record.record_id
        == first_record_id
    )
