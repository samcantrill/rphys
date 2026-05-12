from __future__ import annotations

import pytest

from rphys.errors import InvalidMetadataKeyError
from rphys.data.metadata import (
    GROUP,
    RECORD_ID,
    SAMPLE_ID,
    SOURCE_ID,
    SPLIT,
    SUBJECT_ID,
    MetadataKey,
)


def test_metadata_constants_are_validated_instances() -> None:
    assert SOURCE_ID == "source_id"
    assert GROUP == "group"
    assert SPLIT == "split"
    assert SUBJECT_ID == "subject_id"
    assert RECORD_ID == "record_id"
    assert SAMPLE_ID == "sample_id"
    assert all(
        isinstance(value, MetadataKey)
        for value in [SOURCE_ID, GROUP, SPLIT, SUBJECT_ID, RECORD_ID, SAMPLE_ID]
    )


@pytest.mark.parametrize(
    "value",
    ["source_id", "camera.serial_number", "run.fold_id", "custom_context"],
)
def test_metadata_key_accepts_lowercase_tokens_and_dotted_namespaces(value: str) -> None:
    key = MetadataKey(value)

    assert key == value
    assert isinstance(key, str)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "Subject_ID",
        "subject id",
        "subject-id",
        "subject/id",
        "metadata/source_id",
        "source_id#camera",
        "metadata..source_id",
        ".source_id",
        "source_id.",
        "sourcé_id",
    ],
)
def test_metadata_key_rejects_invalid_values(value: str) -> None:
    with pytest.raises(InvalidMetadataKeyError) as exc_info:
        MetadataKey(value)

    assert exc_info.value.context["metadata_key"] == value
    assert "expected" in exc_info.value.context


def test_metadata_constants_do_not_define_policy() -> None:
    assert not hasattr(MetadataKey, "lookup")
    assert not hasattr(MetadataKey, "group_by")
    assert not hasattr(MetadataKey, "split_values")
