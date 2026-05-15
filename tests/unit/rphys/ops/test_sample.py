"""Focused tests for Stage 7 sample operation foundations."""

from __future__ import annotations

from types import MappingProxyType

import pytest

from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.data.sample_fields import SampleField, SampleFieldState
from rphys.errors import (
    InvalidFieldLocatorError,
    InvalidOperationContractError,
    InvalidOperationContextError,
    InvalidOperationInputError,
    InvalidOperationResultError,
    MissingFieldError,
    UndeclaredSampleFieldMutationError,
    OperationExecutionError,
)
from rphys.io.codecs import CodecLoadResult, LoadContext
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef
from rphys.ops import (
    OperationContext,
    OperationResult,
    SampleFieldPermissions,
    SampleDecision,
    SampleRoute,
    SampleOperation,
    SampleOperationContext,
    SampleOperationContract,
    SampleReplayRecord,
    SampleTransform,
    SampleCheck,
)


VIDEO = FieldLocator.parse("inputs/video.rgb")
SECONDARY = FieldLocator.parse("inputs/video.mask")
ANOTHER = FieldLocator.parse("inputs/mask.rgb")
REPORT = FieldLocator.parse("diagnostics/quality.face_visibility")


def _identity(payload: Sample, *, context: SampleOperationContext) -> Sample:
    return payload


def _typed_result(payload: Sample, *, context: SampleOperationContext) -> OperationResult:
    return OperationResult(
        output=payload,
        operation_name="op",
        metadata={"kernel": "explicit"},
        provenance={"path": "test"},
    )


def _load_context() -> LoadContext:
    return LoadContext(
        FieldView(
            FieldRef(
                "video.rgb",
                [ResourceRef("file:///samples/1.bin", "file")],
                schema="video.rgb.v1",
            ),
            TemporalIndexSlice(0, 4),
        )
    )


def _load_result(payload: object = ("frame-1", "frame-2")) -> CodecLoadResult:
    return CodecLoadResult(
        FieldValue(payload, schema="video.rgb.v1"),
        metadata={"codec": "unit"},
    )


class CountingLoader:
    def __init__(self, result: object) -> None:
        self.result = result
        self.calls = 0

    def __call__(self, context: LoadContext) -> CodecLoadResult:
        self.calls += 1
        return self.result if isinstance(self.result, CodecLoadResult) else self.result  # type: ignore[return-value]


def test_field_permissions_normalizes_and_freezes_declarations() -> None:
    permissions = SampleFieldPermissions(
        reads=[VIDEO, "inputs/mask.rgb"],
        writes=(ANOTHER,),
        deletes="inputs/video.mask",
        dynamic_writes=[VIDEO],
    )

    assert permissions.reads == (VIDEO, ANOTHER)
    assert permissions.writes == (ANOTHER,)
    assert permissions.deletes == (SECONDARY,)
    assert permissions.dynamic_writes == (VIDEO,)


def test_field_permissions_rejects_invalid_locator_declarations() -> None:
    with pytest.raises(InvalidFieldLocatorError):
        SampleFieldPermissions(reads=[123])  # type: ignore[list-item]

    with pytest.raises(InvalidFieldLocatorError):
        SampleFieldPermissions(writes=["bad-locator"])


def test_field_permissions_rejects_duplicate_and_contradictory_declarations() -> None:
    with pytest.raises(InvalidOperationContractError):
        SampleFieldPermissions(reads=(VIDEO, VIDEO))

    with pytest.raises(InvalidOperationContractError):
        SampleFieldPermissions(writes=(VIDEO,), deletes=(VIDEO,))

    with pytest.raises(InvalidOperationContractError):
        SampleFieldPermissions(writes=(VIDEO,), dynamic_writes=(VIDEO,))


def test_sample_operation_contract_defaults_and_generic_contract_binding() -> None:
    contract = SampleOperationContract()
    generic = contract.contract

    assert contract.field_permissions == SampleFieldPermissions()
    assert generic.input_type is Sample
    assert generic.output_type is Sample
    assert generic.role.value == "generic"
    assert contract.operation_contract is generic


def test_sample_operation_contract_rejects_invalid_field_permissions_record() -> None:
    with pytest.raises(InvalidOperationContractError):
        SampleOperationContract(field_permissions={"reads": (VIDEO,)})  # type: ignore[arg-type]


def test_sample_operation_context_coercion_paths() -> None:
    base = SampleOperationContext(
        metadata={"dataset_id": "synth"},
        provenance={"phase": "test"},
    )
    assert base.metadata == {"dataset_id": "synth"}
    assert isinstance(base.metadata, MappingProxyType)
    assert base.operation_name is None

    none_context = SampleOperationContext()
    assert none_context.operation_name is None
    assert none_context.metadata == {}
    assert none_context.provenance == {}

    generic = OperationContext(metadata={"dataset_id": "synth"}, provenance={"source": "unit"})
    sample_context = SampleOperationContext(
        metadata=generic.metadata,
        provenance=generic.provenance,
    )
    assert sample_context.metadata == generic.metadata
    assert sample_context.provenance == generic.provenance


def test_sample_operation_context_infers_operation_name_from_run_context() -> None:
    op = SampleOperation(_identity, name="op-run")
    context = SampleOperationContext(epoch=3)
    result = op(Sample(), context=context)

    assert result.operation_name == "op-run"
    assert op.contract.input_type is Sample


def test_sample_operation_context_accepts_matching_operation_name() -> None:
    op = SampleOperation(_identity, name="op-run")
    context = SampleOperationContext(operation_name="op-run", epoch=3)

    result = op(Sample(), context=context)

    assert result.operation_name == "op-run"


def test_sample_operation_context_rejects_mismatched_operation_name() -> None:
    op = SampleOperation(_identity, name="op-run")
    context = SampleOperationContext(operation_name="other-op", epoch=3)

    with pytest.raises(InvalidOperationContextError) as exc:
        op(Sample(), context=context)

    assert exc.value.context["field"] == "context.operation_name"
    assert exc.value.context["expected"] == "op-run"
    assert exc.value.context["actual"] == "other-op"


def test_sample_operation_replay_record_is_immutable_mapping() -> None:
    record = SampleReplayRecord(
        run_seed="seed",
        epoch=1,
        operation_name="op",
    )
    mapping = record.to_mapping()

    assert mapping["run_seed"] == "seed"
    assert mapping["operation_name"] == "op"
    assert isinstance(mapping, MappingProxyType)

    with pytest.raises(TypeError):
        mapping["run_seed"] = "bad"


@pytest.mark.parametrize("field_name", ["epoch", "operation_index"])
def test_sample_replay_record_rejects_non_integer_context_fields(field_name: str) -> None:
    with pytest.raises(InvalidOperationContextError):
        SampleReplayRecord(**{field_name: "1"})  # type: ignore[arg-type]


@pytest.mark.parametrize("field_name", ["operation_name", "view_name"])
def test_sample_replay_record_rejects_blank_context_names(field_name: str) -> None:
    with pytest.raises(InvalidOperationContextError):
        SampleReplayRecord(**{field_name: "   "})  # type: ignore[arg-type]


def test_sample_operation_run_wraps_bare_sample_output() -> None:
    sample = Sample({VIDEO: FieldValue(("frame",), schema="video.rgb.v1")})
    operation = SampleOperation(_identity, name="identity")
    context = SampleOperationContext(metadata={"ds": "unit"}, provenance={"source": "sample"})

    result = operation(sample, context=context)

    assert result.operation_name == "identity"
    assert result.output is sample
    assert result.metadata["ds"] == "unit"
    assert result.metadata["sample_field_effects"]["copy_mode"] == "in_place"
    assert result.provenance == {"source": "sample"}
    assert result.role.value == "generic"


def test_sample_operation_explicit_result_preserves_operation_and_role_and_output_type() -> None:
    sample = Sample()
    operation = SampleOperation(_typed_result, name="op")

    wrong_name = SampleOperation(
        _typed_result,
        name="other",
        contract=SampleOperationContract(),
    )
    with pytest.raises(InvalidOperationResultError):
        wrong_name(sample)

    # explicit result with matching name and role succeeds
    operation = SampleOperation(_typed_result, name="op")
    result = operation(sample, context=SampleOperationContext())

    assert result.operation_name == "op"
    assert result.metadata["kernel"] == "explicit"
    assert result.metadata["sample_field_effects"]["copy_mode"] == "in_place"
    assert result.provenance == {"path": "test"}


def test_sample_operation_missing_required_read_raises_before_call() -> None:
    calls = []

    def read_kernel(payload: Sample, *, context: SampleOperationContext) -> Sample:
        calls.append("called")
        return payload

    contract = SampleOperationContract(
        field_permissions=SampleFieldPermissions(reads=(VIDEO,)),
    )
    operation = SampleOperation(
        read_kernel,
        name="requires-video",
        contract=contract,
    )
    sample = Sample()

    with pytest.raises(MissingFieldError):
        operation(sample, context=SampleOperationContext())

    assert calls == []


def test_sample_operation_uses_has_preflight_without_materializing_lazy_fields() -> None:
    call_count = []

    def no_payload_kernel(payload: Sample, *, context: SampleOperationContext) -> Sample:
        call_count.append("invoked")
        return payload

    loader = CountingLoader(_load_result())
    field = SampleField(_load_context(), loader)
    sample = Sample({VIDEO: field})
    operation = SampleOperation(
        no_payload_kernel,
        name="no-payload-read",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(reads=(VIDEO,)),
        ),
    )

    result = operation(sample)

    assert result.output is sample
    assert call_count == ["invoked"]
    assert loader.calls == 0
    assert field.state is SampleFieldState.UNLOADED


def test_sample_operation_rejects_invalid_input_type_before_call() -> None:
    operation = SampleOperation(
        _identity,
        name="identity",
        contract=SampleOperationContract(),
    )

    with pytest.raises(InvalidOperationInputError):
        operation({"not": "sample"}, context=SampleOperationContext())


def test_sample_operation_invalid_context_type() -> None:
    operation = SampleOperation(_identity, name="identity")

    with pytest.raises(InvalidOperationContextError):
        operation(Sample(), context="bad")  # type: ignore[arg-type]


def test_sample_operation_callable_error_is_wrapped() -> None:
    def failing(payload: Sample, *, context: SampleOperationContext) -> Sample:
        raise ValueError("boom")

    operation = SampleOperation(failing, name="failing")
    with pytest.raises(OperationExecutionError) as exc:
        operation(Sample())

    assert isinstance(exc.value.__cause__, ValueError)


def test_sample_operation_copy_mode_uses_expected_input_object() -> None:
    def passthrough(payload: Sample, *, context: SampleOperationContext) -> Sample:
        return payload

    sample = Sample({VIDEO: FieldValue((1, 2), schema="video.rgb.v1")})

    in_place = SampleOperation(passthrough, name="in-place", copy_mode="in_place")
    in_place_result = in_place(sample)
    assert in_place_result.output is sample
    assert in_place_result.metadata["sample_field_effects"]["copy_mode"] == "in_place"

    shallow = SampleOperation(passthrough, name="shallow", copy_mode="shallow")
    shallow_result = shallow(sample)
    assert shallow_result.output is not sample
    assert shallow_result.output is not sample
    assert shallow_result.output.field(VIDEO) is sample.field(VIDEO)
    assert shallow_result.metadata["sample_field_effects"]["copy_mode"] == "shallow"

    deep = SampleOperation(passthrough, name="deep", copy_mode="deep")
    deep_result = deep(sample)
    assert deep_result.output is not sample
    assert deep_result.output.field(VIDEO) is not sample.field(VIDEO)
    assert deep_result.metadata["sample_field_effects"]["copy_mode"] == "deep"


def test_sample_operation_rejects_invalid_copy_mode_inputs() -> None:
    sample = Sample({VIDEO: FieldValue((1, 2), schema="video.rgb.v1")})
    SampleOperation(_identity, copy_mode="in_place")

    with pytest.raises(InvalidOperationContractError) as exc_info:
        SampleOperation(_identity, copy_mode="bad")
    assert exc_info.value.context["owner"] == "SampleOperation"

    with pytest.raises(InvalidOperationContractError):
        SampleOperation(
            _identity,
            contract=SampleOperationContract(copy_mode="shallow"),
            copy_mode="deep",
        )

    result = SampleOperation(
        _identity,
        name="contract-mode",
        contract=SampleOperationContract(copy_mode="shallow"),
    )(sample)
    assert result.metadata["sample_field_effects"]["copy_mode"] == "shallow"


def test_sample_operation_detects_and_reports_allowed_field_addition_replacement_and_removal() -> None:
    def add_kernel(payload: Sample, *, context: SampleOperationContext) -> Sample:
        payload.set_field(ANOTHER, FieldValue((0, 0), schema="video.mask.v1"))
        return payload

    def replace_kernel(payload: Sample, *, context: SampleOperationContext) -> Sample:
        payload.set_field(
            VIDEO,
            FieldValue((9, 9), schema="video.rgb.v1"),
        )
        return payload

    def rename_kernel(payload: Sample, *, context: SampleOperationContext) -> Sample:
        payload.rename_field(VIDEO, ANOTHER)
        return payload

    sample = Sample({VIDEO: FieldValue((1, 2), schema="video.rgb.v1")})

    allowed_add = SampleOperation(
        add_kernel,
        name="add",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(
                writes=(ANOTHER,),
            )
        ),
    )
    added_result = allowed_add(sample)
    sample_effects = added_result.metadata["sample_field_effects"]
    assert sample_effects["added"] == (str(ANOTHER),)
    assert sample_effects["removed"] == ()
    assert sample_effects["replaced"] == ()

    sample = Sample({VIDEO: FieldValue((1, 2), schema="video.rgb.v1")})
    allowed_replace = SampleOperation(
        replace_kernel,
        name="replace",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(writes=(VIDEO,)),
        ),
    )
    replace_result = allowed_replace(sample)
    replace_effects = replace_result.metadata["sample_field_effects"]
    assert replace_effects["replaced"] == (str(VIDEO),)

    sample = Sample({VIDEO: FieldValue((1, 2), schema="video.rgb.v1")})
    allowed_rename = SampleOperation(
        rename_kernel,
        name="rename",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(
                writes=(ANOTHER,),
                deletes=(VIDEO,),
            )
        ),
    )
    rename_effects = allowed_rename(sample).metadata["sample_field_effects"]
    assert rename_effects["added"] == (str(ANOTHER),)
    assert rename_effects["removed"] == (str(VIDEO),)
    assert rename_effects["replaced"] == ()

    denied_add = SampleOperation(
        add_kernel,
        name="deny-add",
    )
    with pytest.raises(UndeclaredSampleFieldMutationError) as exc:
        denied_add(Sample({VIDEO: FieldValue((1, 2), schema="video.rgb.v1")}))
    assert exc.value.context["effect_type"] == "added"
    assert "inputs/mask.rgb" in exc.value.context["detected_added"]

    denied_remove = SampleOperation(
        rename_kernel,
        name="deny-rename",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(writes=(ANOTHER,)),
        ),
    )
    with pytest.raises(UndeclaredSampleFieldMutationError) as exc:
        denied_remove(Sample({VIDEO: FieldValue((1, 2), schema="video.rgb.v1")}))
    assert exc.value.context["effect_type"] == "removed"

    denied_replace = SampleOperation(
        replace_kernel,
        name="deny-replace",
    )
    with pytest.raises(UndeclaredSampleFieldMutationError) as exc:
        denied_replace(Sample({VIDEO: FieldValue((1, 2), schema="video.rgb.v1")}))
    assert exc.value.context["effect_type"] == "replaced"


def test_sample_operation_dynamic_writes_are_exact_locator_permissions_only() -> None:
    def dynamic_add_kernel(payload: Sample, *, context: SampleOperationContext) -> Sample:
        payload.set_field("inputs/video.mask", FieldValue((0, 0), schema="video.mask.v1"))
        return payload

    with pytest.raises(UndeclaredSampleFieldMutationError):
        SampleOperation(
            dynamic_add_kernel,
            name="dynamic-bad-add",
            contract=SampleOperationContract(
                field_permissions=SampleFieldPermissions(
                    dynamic_writes=(VIDEO,),
                )
            ),
        )(Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")}))

    SampleOperation(
        dynamic_add_kernel,
        name="dynamic-good-add",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(
                dynamic_writes=(FieldLocator.parse("inputs/video.mask"),),
            )
        ),
    )(Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")}))


def test_sample_operation_requires_exact_output_sample_object() -> None:
    def replace_sample(payload: Sample, *, context: SampleOperationContext) -> Sample:
        return Sample()

    with pytest.raises(InvalidOperationResultError):
        SampleOperation(
            replace_sample,
            name="replace-output",
        )(Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")}))


def test_sample_operation_metadata_collision_for_sample_field_effects_is_invalid() -> None:
    def with_collision(payload: Sample, *, context: SampleOperationContext) -> OperationResult:
        return OperationResult(
            output=payload,
            operation_name="with-collision",
            metadata={"sample_field_effects": {"bad": "collision"}},
        )

    with pytest.raises(InvalidOperationResultError):
        SampleOperation(with_collision, name="with-collision")(Sample())


def test_sample_operation_does_not_detect_payload_internal_mutation() -> None:
    payload_data = [1]

    def mutate_payload(payload: Sample, *, context: SampleOperationContext) -> Sample:
        payload.require(VIDEO).append(2)
        return payload

    sample = Sample({VIDEO: FieldValue(payload_data, schema="video.rgb.v1")})
    result = SampleOperation(mutate_payload, name="mutate")(sample)
    effects = result.metadata["sample_field_effects"]
    assert effects["added"] == ()
    assert effects["removed"] == ()
    assert effects["replaced"] == ()


def test_sample_transform_requires_output_write_or_dynamic_writes() -> None:
    with pytest.raises(InvalidOperationContractError):
        SampleTransform(_identity, name="transform-invalid")

    with pytest.raises(InvalidOperationContractError) as exc_info:
        SampleTransform(_identity, name="bad-contract", contract={})  # type: ignore[arg-type]
    assert exc_info.value.context["owner"] == "SampleTransform"
    assert exc_info.value.context["field"] == "contract"

    result = SampleTransform(
        _identity,
        name="transform-valid",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(writes=(ANOTHER,)),
        ),
    )(Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1"), ANOTHER: FieldValue((2,), schema="video.mask.v1")}))
    assert result.operation_name == "transform-valid"


def test_sample_check_validates_sample_decision_and_route_records() -> None:
    def decision_kernel(payload: Sample, *, context: SampleOperationContext) -> OperationResult:
        return OperationResult(
            output=payload,
            operation_name="decide",
            metadata={
                "sample_decision": SampleDecision(
                    label="accept",
                    reason="valid",
                    metadata={"score": 0.95},
                ),
                "sample_route": (
                    SampleRoute(label="continue", reason="safe"),
                    SampleRoute(label="audit", reason="logged"),
                ),
            },
        )

    result = SampleCheck(
        decision_kernel,
        name="decide",
    )(Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")}))
    assert isinstance(result.metadata["sample_decision"], SampleDecision)
    assert isinstance(result.metadata["sample_route"], tuple)
    assert len(result.metadata["sample_route"]) == 2


def test_sample_check_allows_declared_report_field_writes() -> None:
    def report_kernel(payload: Sample, *, context: SampleOperationContext) -> Sample:
        payload.set_field(REPORT, FieldValue(True, schema="quality.face_visibility.v1"))
        return payload

    result = SampleCheck(
        report_kernel,
        name="report-check",
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(writes=(REPORT,)),
        ),
    )(Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")}))

    assert result.output.field(REPORT).payload is True
    assert result.metadata["sample_field_effects"]["added"] == (str(REPORT),)


def test_sample_check_undeclared_report_field_write_fails_through_mutation_enforcement() -> None:
    def report_kernel(payload: Sample, *, context: SampleOperationContext) -> Sample:
        payload.set_field(REPORT, FieldValue(True, schema="quality.face_visibility.v1"))
        return payload

    with pytest.raises(UndeclaredSampleFieldMutationError) as exc:
        SampleCheck(report_kernel, name="undeclared-report")(
            Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")})
        )

    assert exc.value.context["operation_name"] == "undeclared-report"
    assert exc.value.context["effect_type"] == "added"
    assert str(REPORT) in exc.value.context["detected_added"]


def test_sample_check_route_labels_are_opaque_non_policy_metadata() -> None:
    arbitrary_label = "route:send_to_review_queue/without_policy_lookup"

    def route_kernel(payload: Sample, *, context: SampleOperationContext) -> OperationResult:
        return OperationResult(
            output=payload,
            operation_name="opaque-route",
            metadata={
                "sample_route": SampleRoute(
                    label=arbitrary_label,
                    reason="caller-defined",
                )
            },
        )

    result = SampleCheck(route_kernel, name="opaque-route")(
        Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")})
    )

    assert result.metadata["sample_route"].label == arbitrary_label


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("sample_decision", None),
        ("sample_decision", []),
        ("sample_decision", {}),
        ("sample_decision", "accept"),
        ("sample_decision", True),
        ("sample_decision", ()),
        (
            "sample_decision",
            (SampleDecision(label="accept"), SampleRoute(label="audit")),
        ),
        ("sample_route", None),
        ("sample_route", []),
        ("sample_route", {}),
        ("sample_route", "continue"),
        ("sample_route", False),
        ("sample_route", ()),
        (
            "sample_route",
            (SampleRoute(label="continue"), SampleDecision(label="accept")),
        ),
    ],
)
def test_sample_check_rejects_present_invalid_reserved_metadata_values(
    field_name: str,
    value: object,
) -> None:
    def invalid_metadata(payload: Sample, *, context: SampleOperationContext) -> OperationResult:
        return OperationResult(
            output=payload,
            operation_name="invalid-reserved-metadata",
            metadata={field_name: value},
        )

    with pytest.raises(InvalidOperationResultError):
        SampleCheck(
            invalid_metadata,
            name="invalid-reserved-metadata",
        )(Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")}))


def test_sample_check_rejects_invalid_decision_and_route_metadata_shapes() -> None:
    def invalid_sample_decision(payload: Sample, *, context: SampleOperationContext) -> OperationResult:
        return OperationResult(
            output=payload,
            operation_name="invalid",
            metadata={"sample_decision": ("bad",)},
        )

    def mixed_route_tuple(payload: Sample, *, context: SampleOperationContext) -> OperationResult:
        return OperationResult(
            output=payload,
            operation_name="invalid",
            metadata={
                "sample_route": (
                    SampleRoute(label="ok", reason="good"),
                    "not-route",
                )
            },
        )

    with pytest.raises(InvalidOperationResultError):
        SampleCheck(invalid_sample_decision, name="invalid")(Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")}))

    with pytest.raises(InvalidOperationResultError):
        SampleCheck(
            mixed_route_tuple,
            name="mixed-route",
        )(Sample({VIDEO: FieldValue((1,), schema="video.rgb.v1")}))
