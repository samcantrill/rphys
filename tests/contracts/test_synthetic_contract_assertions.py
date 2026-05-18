from __future__ import annotations

import json
from pathlib import Path

from rphys.data.metadata import GROUP, SPLIT, SUBJECT_ID
from rphys.data.sample_builders import SampleBuilder
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
from rphys.io.indexes import TemporalIndexSlice

from tests.support.contract_assertions import (
    assert_index_manifest_round_trips,
    assert_manifest_matches_golden,
    assert_record_ref_round_trips,
    assert_sample_materializes_expected_fields,
    assert_scan_report_passed,
)
from tests.support.synthetic_catalog import (
    BVP_KEY,
    REQUIRED_FIELD_KEYS,
    TIMESTAMPS_KEY,
    VIDEO_KEY,
    SyntheticScenario,
    make_synthetic_scenario,
)


GOLDEN_PATH = (
    Path(__file__).parent
    / "goldens"
    / "stage14_synthetic_index_manifest_fingerprint.json"
)


def test_private_contract_assertions_cover_public_descriptor_boundaries() -> None:
    scenario, index = _build_golden_index()
    record = scenario.records[0]
    scan_result = scenario.scan_result_for("synthetic-source-001")
    report = validate_scan_result(
        scan_result,
        spec=scenario.spec_for("synthetic-source-001"),
        policy=ValidationIOPolicy.no_io(),
        required_metadata=(SUBJECT_ID, GROUP, SPLIT),
    )

    assert_record_ref_round_trips(record, required_fields=REQUIRED_FIELD_KEYS)
    assert_scan_report_passed(
        report,
        expected_record_count=1,
        required_evidence={
            "fixture_catalog": "stage14.synthetic_catalog.v1",
            "scenario_id": "stage14-golden",
        },
    )
    manifest = assert_index_manifest_round_trips(
        index,
        expected_schema_version="rphys.datasource_index.v1",
    )
    assert_manifest_matches_golden(manifest, json.loads(GOLDEN_PATH.read_text()))

    sample = SampleBuilder(
        registry=scenario.codec_registry(
            record_id=record.record_id,
            field_keys=REQUIRED_FIELD_KEYS,
        )
    ).build(index[0])
    assert_sample_materializes_expected_fields(
        sample,
        {
            "inputs/video.rgb": scenario.payload_for(record.record_id, VIDEO_KEY)[:2],
            "targets/signal.bvp.reference": scenario.payload_for(record.record_id, BVP_KEY)[:2],
            "metadata/timestamps.video": scenario.payload_for(record.record_id, TIMESTAMPS_KEY)[:2],
        },
    )


def _build_golden_index() -> tuple[SyntheticScenario, DataSourceIndex]:
    scenario = make_synthetic_scenario(
        scenario_id="stage14-golden",
        datasource_count=1,
        subjects=("subject-001",),
        records_per_subject=1,
        include_optional_fields=False,
    )
    scan_result = scenario.scan_result_for("synthetic-source-001")
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
            metadata={"fixture_phase": "stage14_p2"},
        ),
    )
    groups = GroupBuilder(GroupPlan({"subject": SUBJECT_ID, "group": GROUP})).build(
        candidates.view
    )
    splits = SplitBuilder(
        SplitPlan(split_group="subject", group_to_split={"subject-001": "train"})
    ).build(groups)
    index = IndexBuilder(
        IndexPlan("stage14-golden-index", metadata={"fixture_phase": "stage14_p2"})
    ).build(
        candidates.view,
        group_result=groups,
        split_result=splits,
    ).index
    return scenario, index
