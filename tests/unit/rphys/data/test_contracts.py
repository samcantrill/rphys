from __future__ import annotations

import copy

import pytest

from rphys.data.containers import Sample
from rphys.data.contracts import FieldRequirement, SampleContract
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.data.schemas import SchemaName
from rphys.errors import FieldSchemaError, FieldTypeError, MissingFieldError


VIDEO = FieldLocator.parse("inputs/video.rgb")
BVP = FieldLocator.parse("targets/signal.bvp.reference")
QUALITY = FieldLocator.parse("diagnostics/quality.face_visibility")


def _loc(locator: FieldLocator | str) -> FieldLocator:
    if isinstance(locator, FieldLocator):
        return locator
    return FieldLocator.parse(locator)


class PublicShapeContainer:
    def __init__(self, value: object, schema: str) -> None:
        self._value = value
        self._schema = schema

    def has(self, locator: FieldLocator | str) -> bool:
        return _loc(locator) == QUALITY

    def field(
        self,
        locator: FieldLocator | str,
        *,
        expected_type=None,
        schema=None,
    ) -> FieldValue:
        if _loc(locator) == QUALITY:
            return FieldValue(self._value, schema=self._schema)
        raise MissingFieldError(
            "Required field is missing.",
            locator=str(locator),
        )

    def get(
        self,
        locator: FieldLocator | str,
        default: object = None,
        *,
        expected_type=None,
        schema=None,
    ) -> object:
        if _loc(locator) == QUALITY:
            return self._value
        return default

    def require(
        self,
        locator: FieldLocator | str,
        *,
        expected_type=None,
        schema=None,
    ) -> object:
        if _loc(locator) == QUALITY:
            return self._value
        raise MissingFieldError(
            "Required field is missing.",
            locator=str(locator),
        )

    def role(self, role) -> dict[str, object]:
        return {}

    def field_items(self):
        return ((QUALITY, FieldValue(self._value, schema=self._schema)),)


class MissingFieldItemsContainer:
    def has(self, locator: FieldLocator | str) -> bool:
        return _loc(locator) == QUALITY

    def field(
        self,
        locator: FieldLocator | str,
        *,
        expected_type=None,
        schema=None,
    ) -> FieldValue:
        if _loc(locator) == QUALITY:
            return FieldValue("payload", schema="quality.face_visibility")
        raise MissingFieldError(
            "Required field is missing.",
            locator=str(locator),
        )

    def get(
        self,
        locator: FieldLocator | str,
        default: object = None,
        *,
        expected_type=None,
        schema=None,
    ) -> object:
        if _loc(locator) == QUALITY:
            return "payload"
        return default

    def require(
        self,
        locator: FieldLocator | str,
        *,
        expected_type=None,
        schema=None,
    ) -> object:
        if _loc(locator) == QUALITY:
            return "payload"
        raise MissingFieldError(
            "Required field is missing.",
            locator=str(locator),
        )

    def role(self, role) -> dict[str, object]:
        return {}


class NonCallablePublicShapeContainer(PublicShapeContainer):
    def __init__(self) -> None:
        super().__init__("payload", "quality.face_visibility")
        self.field_items = 1


def test_field_requirement_coerces_locator_and_schema_and_compares_by_value() -> None:
    requirement = FieldRequirement(
        "inputs/video.rgb",
        expected_type=list,
        schema="video.rgb.v1",
    )

    assert requirement == FieldRequirement(VIDEO, list, SchemaName("video.rgb.v1"))
    assert requirement.locator == VIDEO
    assert requirement.schema == SchemaName("video.rgb.v1")


def test_sample_contract_validates_required_and_optional_fields() -> None:
    sample = Sample(
        {
            VIDEO: FieldValue([], schema="video.rgb.v1"),
            BVP: FieldValue([0.1], schema="signal.bvp.v1"),
        }
    )
    contract = SampleContract(
        required=[
            FieldRequirement(VIDEO, expected_type=list, schema="video.rgb.v1"),
            FieldRequirement(BVP, expected_type=list, schema="signal.bvp.v1"),
        ],
        optional=[FieldRequirement(QUALITY, expected_type=float)],
    )

    assert contract.validate(sample) is sample


def test_sample_contract_optional_field_is_checked_only_when_present() -> None:
    contract = SampleContract(optional=[FieldRequirement(QUALITY, expected_type=float)])

    assert contract.validate(Sample({VIDEO: FieldValue("video")})) is not None

    with pytest.raises(FieldTypeError):
        contract.validate(
            Sample(
                {
                    QUALITY: FieldValue("not-a-float"),
                }
            )
        )


def test_sample_contract_failures_are_typed() -> None:
    contract = SampleContract(
        required=[
            FieldRequirement(VIDEO, expected_type=list, schema="video.rgb.v1"),
            FieldRequirement(BVP, expected_type=list, schema="signal.bvp.v1"),
        ]
    )

    with pytest.raises(MissingFieldError):
        contract.validate(Sample({VIDEO: FieldValue([], schema="video.rgb.v1")}))

    with pytest.raises(FieldTypeError):
        contract.validate(
            Sample(
                {
                    VIDEO: FieldValue("not-a-list", schema="video.rgb.v1"),
                    BVP: FieldValue([0.1], schema="signal.bvp.v1"),
                }
            )
        )

    with pytest.raises(FieldSchemaError):
        contract.validate(
            Sample(
                {
                    VIDEO: FieldValue([], schema="video.gray.v1"),
                    BVP: FieldValue([0.1], schema="signal.bvp.v1"),
                }
            )
        )


def test_sample_contract_is_copyable_without_scientific_schema_fields() -> None:
    contract = SampleContract(
        required=[FieldRequirement(VIDEO, expected_type=list, schema="video.rgb.v1")]
    )

    assert copy.copy(contract) == contract
    assert copy.deepcopy(contract) == contract
    assert not hasattr(contract, "shape")
    assert not hasattr(contract, "sample_rate")
    assert not hasattr(contract, "units")


def test_invalid_requirement_expected_type_fails_loudly() -> None:
    with pytest.raises(FieldTypeError):
        FieldRequirement(VIDEO, expected_type="list")  # type: ignore[arg-type]


def test_sample_contract_uses_public_protocol_shape_for_validation() -> None:
    contract = SampleContract(required=[FieldRequirement(QUALITY, expected_type=str)])

    assert contract.validate(PublicShapeContainer("value", "quality.face_visibility"))

    with pytest.raises(FieldTypeError) as exc:
        contract.validate(MissingFieldItemsContainer())

    assert exc.value.context["method"] == "field_items"

    with pytest.raises(FieldTypeError) as non_callable:
        contract.validate(NonCallablePublicShapeContainer())

    assert non_callable.value.context["method"] == "field_items"
