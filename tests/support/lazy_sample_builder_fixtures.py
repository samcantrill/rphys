"""Private fixtures for Stage 4 lazy sample builder tests."""

from __future__ import annotations

from dataclasses import dataclass

from rphys.data.locators import FieldLocator
from rphys.data.sample_builders import SampleBuilder
from rphys.datasources.index_items import IndexItem
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.io.codecs import CodecRegistry
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import FieldIndex, TemporalIndexSlice
from rphys.io.resources import ResourceRef
from tests.support.synthetic_codecs import SyntheticCodec

VIDEO = FieldLocator.parse("inputs/video.rgb")
BVP = FieldLocator.parse("targets/signal.bvp.reference")


@dataclass(frozen=True, slots=True)
class LazySampleBuilderFixture:
    item: IndexItem
    builder: SampleBuilder
    registry: CodecRegistry
    video_codec: SyntheticCodec
    bvp_codec: SyntheticCodec
    video_resources: tuple[ResourceRef, ...]
    bvp_resources: tuple[ResourceRef, ...]


def make_builder_fixture(
    *,
    video_index: FieldIndex | None = TemporalIndexSlice(1, 3),
    bvp_index: FieldIndex | None = TemporalIndexSlice(0, 3),
) -> LazySampleBuilderFixture:
    video_resources = (
        ResourceRef("archive://dataset.zip#records/r001/video.bin", "archive"),
        ResourceRef("archive://dataset.zip#records/r001/video.index.json", "archive"),
    )
    bvp_resources = (
        ResourceRef("file:///records/r001/bvp.csv", "file"),
    )
    video_ref = FieldRef(
        "video.rgb",
        video_resources,
        schema="video.rgb.v1",
        metadata={"source_id": "camera-front"},
    )
    bvp_ref = FieldRef(
        "signal.bvp.reference",
        bvp_resources,
        schema="signal.bvp.v1",
        metadata={"source_id": "pulse-oximeter"},
    )
    datasource = DataSourceRef(
        "synthetic-rphys",
        metadata={"split": "train", "license": "synthetic"},
    )
    record = RecordRef(
        datasource,
        "record-001",
        {
            "video.rgb": video_ref,
            "signal.bvp.reference": bvp_ref,
        },
        metadata={"subject_id": "subject-001"},
    )
    item = IndexItem(
        {
            VIDEO: FieldView(video_ref, video_index),
            BVP: FieldView(bvp_ref, bvp_index),
        },
        record,
        metadata={"window_id": "window-001", "split": "train"},
    )
    video_codec = SyntheticCodec(
        name="video",
        payload=("f0", "f1", "f2", "f3"),
    )
    bvp_codec = SyntheticCodec(
        name="bvp",
        key="signal.bvp.reference",
        data_type="signal",
        schema="signal.bvp.v1",
        payload=(0.1, 0.2, 0.3, 0.4),
    )
    registry = CodecRegistry([video_codec, bvp_codec])
    builder = SampleBuilder(
        registry=registry,
        metadata={"builder": "stage-4-unit", "sample_scope": "one-item"},
    )
    return LazySampleBuilderFixture(
        item=item,
        builder=builder,
        registry=registry,
        video_codec=video_codec,
        bvp_codec=bvp_codec,
        video_resources=video_resources,
        bvp_resources=bvp_resources,
    )
