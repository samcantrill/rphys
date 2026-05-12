from __future__ import annotations

import pytest

from rphys.data.collation import CollateContext, CollatePolicy, collate_samples
from rphys.data.containers import Batch, Sample
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.data.metadata import MetadataKey
from rphys.errors import CollatePolicyError


VIDEO = FieldLocator.parse("inputs/video.rgb")
BVP = FieldLocator.parse("targets/signal.bvp.reference")


def _sample(
    video_payload: str,
    *,
    metadata: dict[str, object] | None = None,
    policy: object = CollatePolicy.LIST,
    schema: str = "video.rgb.v1",
) -> Sample:
    return Sample(
        {
            VIDEO: FieldValue(
                video_payload,
                schema=schema,
                metadata=metadata,
                collate_policy=policy,
            )
        }
    )


def test_collate_policy_list_has_public_identity_name_and_value() -> None:
    assert CollatePolicy.LIST.name == "LIST"
    assert CollatePolicy.LIST.value == "list"
    assert CollatePolicy("list") is CollatePolicy.LIST


def test_collate_context_is_minimal_and_has_no_policy_override() -> None:
    context = CollateContext(operation="fit", source="unit")

    assert context.operation == "fit"
    assert context.source == "unit"
    assert not hasattr(context, "policy")
    assert not hasattr(context, "policy_overrides")


def test_collate_samples_list_policy_builds_batch_payloads_and_metadata() -> None:
    batch = collate_samples(
        [
            _sample(
                "frame-0",
                metadata={
                    "subject_id": "s1",
                    "sample_id": "a",
                },
            ),
            _sample(
                "frame-1",
                metadata={
                    "source_id": "record-1",
                    "sample_id": "b",
                },
            ),
        ],
        context=CollateContext(operation="unit"),
    )

    assert isinstance(batch, Batch)
    field_value = batch.field(VIDEO)
    assert field_value.payload == ["frame-0", "frame-1"]
    assert field_value.schema == "video.rgb.v1"
    assert field_value.collate_policy is CollatePolicy.LIST
    assert list(field_value.metadata) == [
        MetadataKey("sample_id"),
        MetadataKey("source_id"),
        MetadataKey("subject_id"),
    ]
    assert field_value.metadata[MetadataKey("sample_id")] == ["a", "b"]
    assert field_value.metadata[MetadataKey("source_id")] == [None, "record-1"]
    assert field_value.metadata[MetadataKey("subject_id")] == ["s1", None]


def test_collate_samples_rejects_empty_and_empty_field_inputs() -> None:
    with pytest.raises(CollatePolicyError):
        collate_samples([])

    with pytest.raises(CollatePolicyError):
        collate_samples([Sample()])


def test_collate_samples_requires_homogeneous_field_sets() -> None:
    first = _sample("frame-0")
    second = Sample(
        {
            VIDEO: FieldValue("frame-1", schema="video.rgb.v1", collate_policy="list"),
            BVP: FieldValue([0.1], schema="signal.bvp.v1", collate_policy="list"),
        }
    )

    with pytest.raises(CollatePolicyError) as exc_info:
        collate_samples([first, second])

    assert str(BVP) in exc_info.value.context["extra"]


@pytest.mark.parametrize("policy", [None, "stack", object()])
def test_collate_samples_requires_explicit_supported_list_policy(policy: object) -> None:
    with pytest.raises(CollatePolicyError):
        collate_samples([_sample("frame-0", policy=policy), _sample("frame-1")])


def test_collate_samples_rejects_schema_mismatches() -> None:
    with pytest.raises(CollatePolicyError) as exc_info:
        collate_samples(
            [
                _sample("frame-0", schema="video.rgb.v1"),
                _sample("frame-1", schema="video.gray.v1"),
            ]
        )

    assert exc_info.value.context["locator"] == str(VIDEO)
    assert exc_info.value.context["expected"] == "video.rgb.v1"
