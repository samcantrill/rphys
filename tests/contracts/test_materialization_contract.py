from __future__ import annotations

import json

from rphys.datasources.prepared import (
    BatchCostMetadata,
    BatchSamplerPlan,
    BatchShapePolicy,
    ChunkMetadata,
    MaterializationManifest,
    OptimizedStorageFormat,
    RecordLayoutMetadata,
    ShardManifest,
)
from tests.support.lazy_sample_builder_fixtures import VIDEO

PREPARED_FP = "a" * 64
PLAN_FP = "b" * 64


def test_materialization_contract_is_backend_neutral_primitive_evidence() -> None:
    storage_format = OptimizedStorageFormat(
        "contract-table",
        version="1",
        media_type="application/x.rphys.contract",
        capabilities={"sharded": True},
    )
    shard = ShardManifest(
        "shard-0",
        storage_format=storage_format,
        uri="contract://prepared/shard-0",
        sample_count=1,
        chunks=[
            ChunkMetadata(
                "chunk-0",
                field_locators=[VIDEO],
                sample_start=0,
                sample_count=1,
                byte_offset=0,
                byte_length=128,
            )
        ],
    )
    manifest = MaterializationManifest(
        "materialization-0",
        plan_fingerprint=PLAN_FP,
        storage_format=storage_format,
        prepared_manifest_fingerprint=PREPARED_FP,
        shards=[shard],
        records=[
            RecordLayoutMetadata(
                "record-0",
                shard_id="shard-0",
                position=0,
                field_locators=[VIDEO],
                byte_offset=0,
                byte_length=128,
            )
        ],
        sample_count=1,
        field_locators=[VIDEO],
        checksums={"manifest": "sha256:contract"},
    )

    payload = manifest.to_dict()
    serialized = json.dumps(payload, sort_keys=True)
    loaded = MaterializationManifest.from_dict(payload)

    assert "contract://prepared/shard-0" in serialized
    assert loaded.fingerprint == manifest.fingerprint
    assert loaded.shards[0].uri == "contract://prepared/shard-0"


def test_batch_sampler_plan_contract_is_descriptive_only() -> None:
    plan = BatchSamplerPlan(
        "sampler-0",
        shape_policy=BatchShapePolicy(
            "shape-0",
            mode="fixed",
            batch_size=2,
            field_locators=[VIDEO],
        ),
        ordering="cost_aware",
        cost_metadata=[BatchCostMetadata(position=0, cost=1.0, length=16)],
        seed={"epoch": 1},
    )

    loaded = BatchSamplerPlan.from_dict(plan.to_dict())

    json.dumps(plan.to_dict(), sort_keys=True)
    assert loaded.fingerprint == plan.fingerprint
    for runtime_method in ("sample", "materialize", "write", "open", "__iter__", "__next__"):
        assert not hasattr(plan, runtime_method)
