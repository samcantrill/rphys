from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.errors import InvalidDataKeyError, InvalidFieldLocatorError
from rphys.data.keys import DataKey
from rphys.data.locators import FieldLocator, FieldRole
from rphys.data.metadata import MetadataKey


def test_field_role_contains_approved_closed_set() -> None:
    assert [role.value for role in FieldRole] == [
        "inputs",
        "targets",
        "source",
        "predictions",
        "outputs",
        "losses",
        "objectives",
        "metrics",
        "metadata",
        "diagnostics",
    ]


def test_field_locator_direct_construction_coerces_components() -> None:
    locator = FieldLocator(
        role="diagnostics",
        key="quality.face_visibility",
        metadata_key="source_id",
    )

    assert locator.role is FieldRole.DIAGNOSTICS
    assert locator.key == DataKey("quality.face_visibility")
    assert isinstance(locator.key, DataKey)
    assert locator.metadata_key == MetadataKey("source_id")
    assert isinstance(locator.metadata_key, MetadataKey)
    assert str(locator) == "diagnostics/quality.face_visibility#source_id"


def test_field_locator_direct_component_failures_keep_component_errors() -> None:
    with pytest.raises(InvalidDataKeyError):
        FieldLocator(role=FieldRole.INPUTS, key="Video.RGB")


@pytest.mark.parametrize(
    "value",
    [
        "inputs/video.rgb",
        "targets/signal.bvp.reference",
        "predictions/signal.bvp",
        "metrics/quality.face_visibility",
        "diagnostics/quality.face_visibility#source_id",
    ],
)
def test_field_locator_parse_round_trips_approved_examples(value: str) -> None:
    locator = FieldLocator.parse(value)

    assert str(locator) == value
    assert isinstance(locator.role, FieldRole)
    assert isinstance(locator.key, DataKey)
    if "#" in value:
        assert isinstance(locator.metadata_key, MetadataKey)
    else:
        assert locator.metadata_key is None


@pytest.mark.parametrize(
    ("value", "component"),
    [
        ("unknown/video.rgb", "role"),
        ("inputs/Video.RGB", "key"),
        ("inputs/video.rgb#Source_ID", "metadata_key"),
    ],
)
def test_field_locator_parse_wraps_component_failures(
    value: str,
    component: str,
) -> None:
    with pytest.raises(InvalidFieldLocatorError) as exc_info:
        FieldLocator.parse(value)

    assert exc_info.value.context["locator"] == value
    assert exc_info.value.context["component"] == component


@pytest.mark.parametrize(
    "value",
    [
        "",
        "inputs",
        "inputs/",
        "/video.rgb",
        "inputs/video/rgb",
        "inputs/video.rgb#",
        "inputs/video.rgb#source_id#record_id",
        " inputs/video.rgb",
        "inputs/video.rgb ",
    ],
)
def test_field_locator_parse_rejects_malformed_locators(value: str) -> None:
    with pytest.raises(InvalidFieldLocatorError) as exc_info:
        FieldLocator.parse(value)

    assert exc_info.value.context["locator"] == value
    assert "expected" in exc_info.value.context


def test_field_locator_parse_rejects_non_string_values() -> None:
    with pytest.raises(InvalidFieldLocatorError) as exc_info:
        FieldLocator.parse(42)  # type: ignore[arg-type]

    assert exc_info.value.context["locator"] == 42
    assert exc_info.value.context["actual"] == "int"


def test_field_locator_is_frozen() -> None:
    locator = FieldLocator.parse("inputs/video.rgb")

    with pytest.raises(FrozenInstanceError):
        locator.key = DataKey("signal.bvp")  # type: ignore[misc]


def test_field_locator_does_not_define_runtime_lookup_behavior() -> None:
    assert not hasattr(FieldLocator, "lookup")
    assert not hasattr(FieldLocator, "resolve")
    assert not hasattr(FieldLocator, "load")
