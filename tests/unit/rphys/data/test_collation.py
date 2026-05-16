from __future__ import annotations

import pytest

from rphys.data.collation import (
    BatchCollater,
    CollateContext,
    CollatePolicy,
    collate_samples,
    uncollate_batch,
)
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


class PublicFieldContainer:
    def __init__(
        self,
        *,
        payload: object,
        schema: str = "video.rgb.v1",
        metadata: dict[str, object] | None = None,
        policy: object = CollatePolicy.LIST,
    ) -> None:
        self._items = (
            FieldLocator.parse("inputs/video.rgb"),
            FieldValue(
                payload,
                schema=schema,
                metadata=metadata,
                collate_policy=policy,
            ),
        )

    def has(self, locator: FieldLocator | str) -> bool:
        return locator == self._items[0] or str(locator) == str(self._items[0])

    def field(
        self,
        locator: FieldLocator | str,
        *,
        expected_type: type | tuple[type, ...] | None = None,
        schema: str | None = None,
    ) -> FieldValue:
        if locator == self._items[0] or str(locator) == str(self._items[0]):
            return self._items[1]
        raise KeyError(locator)

    def get(
        self,
        locator: FieldLocator | str,
        default: object = None,
        *,
        expected_type: type | tuple[type, ...] | None = None,
        schema: str | None = None,
    ) -> object:
        if locator == self._items[0] or str(locator) == str(self._items[0]):
            return self._items[1].payload
        return default

    def require(
        self,
        locator: FieldLocator | str,
        *,
        expected_type: type | tuple[type, ...] | None = None,
        schema: str | None = None,
    ) -> object:
        if locator == self._items[0] or str(locator) == str(self._items[0]):
            return self._items[1].payload
        raise KeyError(locator)

    def role(self, role) -> dict[str, object]:
        return {}

    def field_items(self) -> tuple[tuple[FieldLocator, FieldValue], ...]:
        return (self._items,)

    def _field_items(self) -> tuple[tuple[FieldLocator, FieldValue]]:
        raise AssertionError("Private field-items hook should not be required.")


class NonCallableFieldItemsContainer(PublicFieldContainer):
    def __init__(self) -> None:
        super().__init__(payload="frame-0")
        self.field_items = 1


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


def test_batch_collater_delegates_to_list_collation_with_context() -> None:
    collater = BatchCollater(context=CollateContext(operation="unit", source="loader"))

    batch = collater(
        [
            _sample("frame-0", metadata={"sample_id": "a"}),
            _sample("frame-1", metadata={"sample_id": "b"}),
        ]
    )

    assert isinstance(batch, Batch)
    assert batch.require(VIDEO) == ["frame-0", "frame-1"]
    assert batch.field(VIDEO).metadata[MetadataKey("sample_id")] == ["a", "b"]


def test_batch_collater_rejects_invalid_context() -> None:
    with pytest.raises(CollatePolicyError):
        BatchCollater(context=object())  # type: ignore[arg-type]


def test_batch_collater_preserves_collate_samples_failures() -> None:
    collater = BatchCollater()

    with pytest.raises(CollatePolicyError):
        collater([])

    with pytest.raises(CollatePolicyError):
        collater([_sample("frame-0", policy=None), _sample("frame-1")])


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


def test_uncollate_batch_reconstructs_tuple_of_samples_and_sparse_metadata() -> None:
    samples = (
        Sample(
            {
                VIDEO: FieldValue(
                    "frame-0",
                    schema="video.rgb.v1",
                    metadata={"sample_id": "a", "optional": None},
                    collate_policy=CollatePolicy.LIST,
                ),
                BVP: FieldValue(
                    [0.1],
                    schema="signal.bvp.v1",
                    metadata={"quality": None},
                    collate_policy=CollatePolicy.LIST,
                ),
            }
        ),
        Sample(
            {
                VIDEO: FieldValue(
                    "frame-1",
                    schema="video.rgb.v1",
                    metadata={"sample_id": "b"},
                    collate_policy=CollatePolicy.LIST,
                ),
                BVP: FieldValue(
                    [0.2],
                    schema="signal.bvp.v1",
                    metadata={},
                    collate_policy=CollatePolicy.LIST,
                ),
            }
        ),
    )

    batch = collate_samples(samples)
    round_tripped = uncollate_batch(batch)

    assert isinstance(round_tripped, tuple)
    assert len(round_tripped) == 2
    assert round_tripped[0] is not samples[0]
    assert round_tripped[0].require(VIDEO) == "frame-0"
    assert round_tripped[1].require(VIDEO) == "frame-1"
    assert round_tripped[0].field(VIDEO).schema == "video.rgb.v1"
    assert round_tripped[0].field(VIDEO).collate_policy is CollatePolicy.LIST
    assert round_tripped[0].field(VIDEO).metadata[MetadataKey("sample_id")] == "a"
    assert round_tripped[1].field(VIDEO).metadata[MetadataKey("sample_id")] == "b"
    assert MetadataKey("optional") in round_tripped[0].field(VIDEO).metadata
    assert round_tripped[0].field(VIDEO).metadata[MetadataKey("optional")] is None
    assert MetadataKey("optional") not in round_tripped[1].field(VIDEO).metadata
    assert MetadataKey("quality") in round_tripped[0].field(BVP).metadata
    assert round_tripped[0].field(BVP).metadata[MetadataKey("quality")] is None
    assert MetadataKey("quality") not in round_tripped[1].field(BVP).metadata


def test_uncollate_batch_rejects_batches_without_list_evidence() -> None:
    batch = Batch(
        {
            VIDEO: FieldValue(
                ["frame-0", "frame-1"],
                schema="video.rgb.v1",
                metadata={"sample_id": ["a", "b"]},
                collate_policy=CollatePolicy.LIST,
            )
        }
    )

    with pytest.raises(CollatePolicyError, match="LIST collation evidence"):
        uncollate_batch(batch)


def test_uncollate_batch_rejects_non_list_fields() -> None:
    batch = collate_samples([_sample("frame-0"), _sample("frame-1")])
    batch.field(VIDEO).collate_policy = "stack"

    with pytest.raises(CollatePolicyError) as exc_info:
        uncollate_batch(batch)

    assert exc_info.value.context["locator"] == str(VIDEO)
    assert exc_info.value.context["supported"] == [CollatePolicy.LIST.value]


def test_uncollate_batch_rejects_payload_length_mismatch() -> None:
    batch = collate_samples([_sample("frame-0"), _sample("frame-1")])
    batch.field(VIDEO).payload = ["frame-0"]

    with pytest.raises(CollatePolicyError) as exc_info:
        uncollate_batch(batch)

    assert exc_info.value.context["locator"] == str(VIDEO)
    assert exc_info.value.context["expected"] == 2
    assert exc_info.value.context["actual"] == 1


def test_uncollate_batch_rejects_metadata_alignment_mismatch() -> None:
    batch = collate_samples(
        [
            _sample("frame-0", metadata={"sample_id": "a"}),
            _sample("frame-1", metadata={"sample_id": "b"}),
        ]
    )
    batch.field(VIDEO).metadata[MetadataKey("sample_id")] = ["a"]

    with pytest.raises(CollatePolicyError) as exc_info:
        uncollate_batch(batch)

    assert exc_info.value.context["locator"] == str(VIDEO)
    assert exc_info.value.context["metadata_key"] == "sample_id"
    assert exc_info.value.context["expected"] == 2
    assert exc_info.value.context["actual"] == 1


def test_uncollate_batch_rejects_batch_level_scalar_metadata() -> None:
    batch = collate_samples(
        [
            _sample("frame-0", metadata={"sample_id": "a"}),
            _sample("frame-1", metadata={"sample_id": "b"}),
        ]
    )
    batch.field(VIDEO).metadata[MetadataKey("sample_id")] = "batch-scalar"

    with pytest.raises(CollatePolicyError) as exc_info:
        uncollate_batch(batch)

    assert exc_info.value.context["locator"] == str(VIDEO)
    assert exc_info.value.context["metadata_key"] == "sample_id"
    assert exc_info.value.context["actual"] == "str"


def test_collate_samples_rejects_empty_and_empty_field_inputs() -> None:
    with pytest.raises(CollatePolicyError):
        collate_samples([])

    with pytest.raises(CollatePolicyError):
        collate_samples([Sample()])


def test_collate_samples_uses_public_field_items_protocol() -> None:
    batch = collate_samples(
        [
            PublicFieldContainer(payload="frame-0", metadata={"source_id": "s1"}),
            PublicFieldContainer(payload="frame-1", metadata={"source_id": "s2"}),
        ],
        context=CollateContext(operation="unit"),
    )

    field_value = batch.field(VIDEO)
    assert field_value.payload == ["frame-0", "frame-1"]
    assert field_value.metadata[MetadataKey("source_id")] == ["s1", "s2"]


def test_collate_samples_rejects_non_callable_public_field_items() -> None:
    with pytest.raises(CollatePolicyError) as exc_info:
        collate_samples([NonCallableFieldItemsContainer()])

    assert exc_info.value.context["actual"] == "NonCallableFieldItemsContainer"


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
