from __future__ import annotations

from rphys.data.sample_fields import SampleFieldState
from rphys.data.sample_builders import SampleBuilder
from rphys.datasources.adapters import DataSourceScanResult
from rphys.datasources.filters import build_view
from rphys.datasources.indexes import (
    IndexBuilder,
    IndexCandidatePlan,
    IndexPlan,
    build_index_candidates,
)
from rphys.io.codecs import CodecRegistry
from tests.support.synthetic_codecs import SyntheticCodec
from tests.support.synthetic_datasources import (
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def test_datasource_index_item_builds_lazy_sample_with_sample_builder() -> None:
    datasource = synthetic_datasource_ref()
    record = synthetic_record_ref(datasource)
    candidates = build_index_candidates(
        build_view(DataSourceScanResult(datasource, [record])).view,
        IndexCandidatePlan(
            {
                "inputs/video.rgb": "video.rgb",
                "targets/signal.bvp.reference": "signal.bvp.reference",
            }
        ),
    ).view
    index = IndexBuilder(IndexPlan("idx")).build(candidates).index
    registry = CodecRegistry(
        [
            SyntheticCodec(name="video", payload=("f0", "f1")),
            SyntheticCodec(
                name="bvp",
                key="signal.bvp.reference",
                data_type="signal",
                schema="signal.bvp.v1",
                payload=(0.1, 0.2),
            ),
        ]
    )

    sample = SampleBuilder(registry=registry).build(index[0])

    assert sample.field("inputs/video.rgb").state is SampleFieldState.UNLOADED
    assert sample.require("inputs/video.rgb") == ("f0", "f1")
    assert sample.require("targets/signal.bvp.reference") == (0.1, 0.2)
    assert sample.field("inputs/video.rgb").provenance.record is record
    assert index.entry_at(0).record_id == record.record_id
