from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.datasources.prepared import (
    AccessPatternPlan,
    ChunkMetadata,
    MaterializationManifest,
    MaterializationPlan,
    OptimizedDataPlan,
    OptimizedStorageFormat,
    RecordLayoutMetadata,
    ShardManifest,
)
from rphys.errors import FieldTypeError, RemotePhysDataSourceError
from tests.support.lazy_sample_builder_fixtures import BVP, VIDEO

PREPARED_FP = "a" * 64
REQUEST_FP = "b" * 64


def test_materialization_records_round_trip_as_fingerprinted_primitives() -> None:
    storage_format = _storage_format()
    chunk = _chunk()
    shard = _shard(storage_format=storage_format, chunks=[chunk])
    access_pattern = _access_pattern()
    optimized_plan = _optimized_plan(
        storage_format=storage_format,
        access_pattern=access_pattern,
    )
    materialization_plan = _materialization_plan(optimized_plan=optimized_plan)
    record = _record()
    manifest = _manifest(
        storage_format=storage_format,
        shards=[shard],
        records=[record],
        plan_fingerprint=materialization_plan.fingerprint,
    )

    for descriptor in (
        storage_format,
        chunk,
        shard,
        access_pattern,
        optimized_plan,
        materialization_plan,
        record,
        manifest,
    ):
        loaded = type(descriptor).from_dict(descriptor.to_dict())

        assert loaded.to_dict() == descriptor.to_dict()
        assert loaded.fingerprint == descriptor.fingerprint

    assert manifest.shards[0].chunks[0].field_locators == (VIDEO, BVP)
    assert manifest.records[0].shard_id == "shard-0"


def test_materialization_fingerprints_change_with_layout_evidence() -> None:
    first = _manifest(checksums={"manifest": "sha256:v1"})
    changed_checksum = _manifest(checksums={"manifest": "sha256:v2"})
    changed_layout = _optimized_plan(layout={"shards": 2})

    assert first.fingerprint != changed_checksum.fingerprint
    assert _optimized_plan().fingerprint != changed_layout.fingerprint


def test_materialization_records_are_immutable() -> None:
    storage_format = _storage_format()

    with pytest.raises(FrozenInstanceError):
        storage_format.name = "other"  # type: ignore[misc]
    with pytest.raises(TypeError):
        storage_format.metadata["scope"] = "mutated"  # type: ignore[index]


def test_materialization_records_reject_invalid_layout_evidence() -> None:
    storage_format = _storage_format()

    with pytest.raises(FieldTypeError, match="non-negative"):
        _chunk(sample_start=-1)
    with pytest.raises(FieldTypeError, match="unique"):
        _shard(storage_format=storage_format, chunks=[_chunk("dup"), _chunk("dup")])
    with pytest.raises(RemotePhysDataSourceError, match="chunk ranges"):
        _shard(storage_format=storage_format, sample_count=2, chunks=[_chunk(sample_start=2)])
    with pytest.raises(FieldTypeError, match="unsupported"):
        AccessPatternPlan("bad-access", mode="streaming")
    with pytest.raises(FieldTypeError):
        OptimizedStorageFormat("fake-table", metadata={"bad": object()})


def test_materialization_plan_validates_optimized_plan_equivalence() -> None:
    optimized_plan = _optimized_plan()

    with pytest.raises(RemotePhysDataSourceError, match="optimized plan"):
        _materialization_plan(
            optimized_plan=optimized_plan,
            prepared_manifest_fingerprint="c" * 64,
        )

    with pytest.raises(RemotePhysDataSourceError, match="field locators"):
        _materialization_plan(
            optimized_plan=_optimized_plan(field_locators=[VIDEO]),
            field_locators=[VIDEO, BVP],
        )


def test_materialization_manifest_validates_declared_shards_records_and_fields() -> None:
    storage_format = _storage_format()
    shard = _shard(storage_format=storage_format)

    with pytest.raises(RemotePhysDataSourceError, match="storage formats"):
        _manifest(storage_format=storage_format, shards=[_shard(storage_format=_storage_format("other"))])

    with pytest.raises(RemotePhysDataSourceError, match="chunk locators"):
        _manifest(storage_format=storage_format, shards=[shard], field_locators=[VIDEO])

    with pytest.raises(RemotePhysDataSourceError, match="declared shards"):
        _manifest(
            storage_format=storage_format,
            shards=[shard],
            records=[_record(shard_id="missing")],
        )

    with pytest.raises(RemotePhysDataSourceError, match="declared shards"):
        _manifest(
            storage_format=storage_format,
            shards=[shard],
            records=[_record(position=4)],
        )


def _storage_format(name: str = "fake-table") -> OptimizedStorageFormat:
    return OptimizedStorageFormat(
        name,
        version="1",
        media_type="application/x.rphys.fake-table",
        capabilities={"mmap": False, "sharded": True},
        metadata={"scope": "unit"},
    )


def _chunk(
    chunk_id: str = "chunk-0",
    *,
    field_locators=(VIDEO, BVP),
    sample_start: int = 0,
    sample_count: int = 4,
) -> ChunkMetadata:
    return ChunkMetadata(
        chunk_id,
        field_locators=field_locators,
        sample_start=sample_start,
        sample_count=sample_count,
        byte_offset=0,
        byte_length=1024,
        checksum=f"sha256:{chunk_id}",
        compression={"codec": "none"},
        metadata={"scope": "unit"},
    )


def _shard(
    shard_id: str = "shard-0",
    *,
    storage_format: OptimizedStorageFormat | None = None,
    sample_count: int = 4,
    chunks: list[ChunkMetadata] | None = None,
) -> ShardManifest:
    return ShardManifest(
        shard_id,
        storage_format=storage_format or _storage_format(),
        uri=f"file:///prepared/{shard_id}.fake",
        sample_count=sample_count,
        chunks=chunks or [_chunk()],
        checksums={"sha256": f"checksum:{shard_id}"},
        metadata={"scope": "unit"},
    )


def _access_pattern() -> AccessPatternPlan:
    return AccessPatternPlan(
        "access-0",
        mode="sequential",
        prefetch=2,
        ordering="position",
        metadata={"scope": "unit"},
    )


def _optimized_plan(
    *,
    storage_format: OptimizedStorageFormat | None = None,
    field_locators=(VIDEO, BVP),
    access_pattern: AccessPatternPlan | None = None,
    layout: dict[str, object] | None = None,
) -> OptimizedDataPlan:
    return OptimizedDataPlan(
        "optimized-0",
        storage_format=storage_format or _storage_format(),
        prepared_manifest_fingerprint=PREPARED_FP,
        field_locators=field_locators,
        sample_count=4,
        access_pattern=access_pattern,
        layout=layout or {"shards": 1},
        runtime={"workers": 1},
        invalidation={"source_checksum": "v1"},
        metadata={"scope": "unit"},
    )


def _materialization_plan(
    *,
    optimized_plan: OptimizedDataPlan | None = None,
    prepared_manifest_fingerprint: str = PREPARED_FP,
    field_locators=(VIDEO, BVP),
) -> MaterializationPlan:
    return MaterializationPlan(
        "materialize-0",
        optimized_plan=optimized_plan or _optimized_plan(),
        prepared_manifest_fingerprint=prepared_manifest_fingerprint,
        request_fingerprint=REQUEST_FP,
        field_locators=field_locators,
        sample_count=4,
        split_counts={"train": 4},
        group_counts={"subject-001": 4},
        invalidation={"source_checksum": "v1"},
        metadata={"scope": "unit"},
    )


def _record(
    record_id: str = "record-0",
    *,
    shard_id: str = "shard-0",
    position: int = 0,
    field_locators=(VIDEO, BVP),
) -> RecordLayoutMetadata:
    return RecordLayoutMetadata(
        record_id,
        shard_id=shard_id,
        position=position,
        field_locators=field_locators,
        byte_offset=0,
        byte_length=128,
        checksum=f"sha256:{record_id}",
        metadata={"scope": "unit"},
    )


def _manifest(
    *,
    storage_format: OptimizedStorageFormat | None = None,
    plan_fingerprint: str = "c" * 64,
    prepared_manifest_fingerprint: str = PREPARED_FP,
    shards: list[ShardManifest] | None = None,
    records: list[RecordLayoutMetadata] | None = None,
    sample_count: int = 4,
    field_locators=(VIDEO, BVP),
    checksums: dict[str, object] | None = None,
) -> MaterializationManifest:
    resolved_format = storage_format or _storage_format()
    return MaterializationManifest(
        "materialization-0",
        plan_fingerprint=plan_fingerprint,
        storage_format=resolved_format,
        prepared_manifest_fingerprint=prepared_manifest_fingerprint,
        shards=shards or [_shard(storage_format=resolved_format)],
        records=records or [_record()],
        sample_count=sample_count,
        field_locators=field_locators,
        checksums=checksums or {"manifest": "sha256:manifest"},
        invalidation={"source_checksum": "v1"},
        metadata={"scope": "unit"},
    )
