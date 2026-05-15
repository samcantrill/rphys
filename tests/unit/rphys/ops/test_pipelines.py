from __future__ import annotations

from collections import OrderedDict
import inspect

import pytest

from rphys.errors import (
    InvalidOperationContextError,
    InvalidOperationPipelineError,
    OperationPipelineExecutionError,
    InvalidOperationInputError,
)
from rphys.data import Sample
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.ops import (
    Operation,
    OperationContract,
    OperationContext,
    OperationPipeline,
    OperationResult,
    SampleFieldPermissions,
    SampleOperationContext,
    SampleOperationContract,
    SampleOperationPipeline,
    SampleTransform,
)


VIDEO = FieldLocator.parse("inputs/video.rgb")
VIEW_A = FieldLocator.parse("inputs/video.rgb.view_a")
VIEW_B = FieldLocator.parse("inputs/video.rgb.view_b")


def increment(value: int, *, context: OperationContext) -> int:
    return value + 1


def multiply(value: int, *, context: OperationContext) -> int:
    return value * 10


def failure(value: object, *, context: OperationContext) -> int:
    raise ValueError("boom")


def _sample_with_video() -> Sample:
    return Sample({VIDEO: FieldValue((1, 2, 3), schema="video.rgb.v1")})


def _write_view_a(sample: Sample, *, context: SampleOperationContext) -> Sample:
    sample.set_field(
        VIEW_A,
        FieldValue((context.operation_name, context.run_seed), schema="video.rgb.view_a.v1"),
    )
    return sample


def _write_view_b(sample: Sample, *, context: SampleOperationContext) -> Sample:
    sample.set_field(
        VIEW_B,
        FieldValue(sample.field(VIEW_A).payload, schema="video.rgb.view_b.v1"),
    )
    return sample


def _sample_transform(
    function,
    *,
    name: str,
    reads: tuple[FieldLocator, ...] = (VIDEO,),
    writes: tuple[FieldLocator, ...],
) -> SampleTransform:
    return SampleTransform(
        function,
        name=name,
        contract=SampleOperationContract(
            field_permissions=SampleFieldPermissions(
                reads=reads,
                writes=writes,
            ),
        ),
    )


def test_operation_pipeline_signature_is_fixed() -> None:
    ctor = inspect.signature(OperationPipeline.__init__)
    params = list(ctor.parameters.values())[1:]

    assert len(params) == 1
    assert params[0].name == "operations"
    assert params[0].annotation == "Sequence[OperationStep]"


def test_operation_pipeline_exposes_immutable_operations_tuple() -> None:
    op_a = Operation(increment, name="increment")
    op_b = Operation(multiply, name="multiply")
    pipeline = OperationPipeline([op_a, op_b])

    assert pipeline.operations == (op_a, op_b)
    with pytest.raises(AttributeError):
        pipeline.operations = ()


def test_operation_pipeline_accepts_direct_operation_step_entries() -> None:
    captured: list[OperationContext] = []

    class ConstantAdder:
        def __init__(self, offset: int) -> None:
            self._offset = offset

        @property
        def name(self) -> str:
            return "constant-adder"

        @property
        def contract(self) -> OperationContract:
            return OperationContract(
                input_type=int,
                output_type=int,
            )

        def run(self, input_value: object, context: OperationContext | None = None) -> OperationResult:
            assert context is not None
            captured.append(context)
            return OperationResult(
                output=input_value + self._offset,  # type: ignore[arg-type]
                operation_name=self.name,
                metadata=context.metadata,
                provenance=context.provenance,
            )

    pipeline = OperationPipeline(
        [
            ConstantAdder(offset=4),
            Operation(multiply, name="multiply", contract=OperationContract(input_type=int)),
        ]
    )
    context = OperationContext(metadata={"dataset_id": "ops"})
    result = pipeline.run(1, context=context)

    assert result.output == 50
    assert captured == [context]


def test_operation_pipeline_runs_steps_and_forwards_result_output() -> None:
    seen: list[int] = []

    def record(value: int, *, context: OperationContext) -> int:
        seen.append(value)
        return value + 2

    pipeline = OperationPipeline(
        [
            Operation(record, name="record"),
            Operation(multiply, name="multiply", contract=OperationContract(input_type=int)),
        ]
    )

    result = pipeline.run(1)

    assert seen == [1]
    assert result.output == 30
    assert result.operation_name == "multiply"


def test_operation_pipeline_call_and_run_share_final_result_shape() -> None:
    pipeline = OperationPipeline(
        [
            Operation(increment, name="increment"),
            Operation(multiply, name="multiply", contract=OperationContract(input_type=int)),
        ]
    )

    assert pipeline.run(1).output == pipeline(1).output


def test_operation_pipeline_rejects_empty_sequence() -> None:
    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline([])


def test_operation_pipeline_rejects_non_sequence_and_named_entry_inputs() -> None:
    step = Operation(increment)

    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline("abc")
    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline(b"abc")
    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline({"a": step})
    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline(OrderedDict({"a": step}))
    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline([("increment", step)])
    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline(["bad", step])


def test_operation_pipeline_rejects_non_operation_entries() -> None:
    with pytest.raises(InvalidOperationPipelineError) as exc:
        OperationPipeline([object()])

    assert exc.value.context["step_index"] == 0


def test_operation_pipeline_rejects_raw_callable_entries_as_invalid_steps() -> None:
    with pytest.raises(InvalidOperationPipelineError) as exc:
        OperationPipeline([increment])

    assert exc.value.context["field"] == "operations[0]"
    assert exc.value.context["expected"] == "OperationStep"
    assert exc.value.context["actual"] == "function"
    assert exc.value.context["step_index"] == 0


@pytest.mark.parametrize(
    ("step", "expected", "actual"),
    [
        (
            type(
                "BlankNameStep",
                (),
                {
                    "name": " ",
                    "contract": OperationContract(),
                    "run": lambda self, input_value, context=None: OperationResult(
                        output=input_value,
                        operation_name="blank",
                    ),
                },
            )(),
            "OperationStep with non-empty str name",
            "' '",
        ),
        (
            type(
                "NonStringNameStep",
                (),
                {
                    "name": 123,
                    "contract": OperationContract(),
                    "run": lambda self, input_value, context=None: OperationResult(
                        output=input_value,
                        operation_name="non-string",
                    ),
                },
            )(),
            "OperationStep with non-empty str name",
            "123",
        ),
        (
            type(
                "InvalidContractStep",
                (),
                {
                    "name": "invalid-contract",
                    "contract": object(),
                    "run": lambda self, input_value, context=None: OperationResult(
                        output=input_value,
                        operation_name="invalid-contract",
                    ),
                },
            )(),
            "OperationContract",
            "object",
        ),
    ],
)
def test_operation_pipeline_rejects_malformed_structural_steps(
    step: object,
    expected: str,
    actual: str,
) -> None:
    with pytest.raises(InvalidOperationPipelineError) as exc:
        OperationPipeline([step])

    assert exc.value.context["field"] == "operations[0]"
    assert exc.value.context["expected"] == expected
    assert exc.value.context["actual"] == actual
    assert exc.value.context["step_index"] == 0


def test_adjacent_contract_types_must_be_compatible() -> None:
    upstream = Operation(increment, name="upstream", contract=OperationContract(output_type=object))
    downstream = Operation(multiply, name="downstream", contract=OperationContract(input_type=int))

    with pytest.raises(InvalidOperationPipelineError) as exc:
        OperationPipeline([upstream, downstream])

    assert exc.value.context["upstream_step_index"] == 0
    assert exc.value.context["downstream_step_index"] == 1
    assert exc.value.context["upstream_operation_name"] == "upstream"
    assert exc.value.context["downstream_operation_name"] == "downstream"
    assert exc.value.context["expected"] == ("int",)
    assert exc.value.context["actual"] == ("object",)


def test_partial_overlap_declared_outputs_fail() -> None:
    upstream = Operation(increment, name="upstream", contract=OperationContract(output_type=(int, str)))
    downstream = Operation(multiply, name="downstream", contract=OperationContract(input_type=int))

    with pytest.raises(InvalidOperationPipelineError):
        OperationPipeline([upstream, downstream])


def test_operation_pipeline_preserves_context_identity_for_explicit_context() -> None:
    contexts: list[OperationContext] = []

    def capture(value: int, *, context: OperationContext) -> int:
        contexts.append(context)
        return value + 1

    shared = OperationContext(metadata={"source": "unit"})
    pipeline = OperationPipeline(
        [
            Operation(capture, name="capture-1"),
            Operation(capture, name="capture-2"),
            Operation(capture, name="capture-3"),
        ]
    )
    pipeline.run(1, context=shared)

    assert contexts[0] is shared
    assert contexts[1] is shared
    assert contexts[2] is shared


def test_operation_pipeline_omits_context_and_creates_one_empty_context_once() -> None:
    observed: list[OperationContext] = []

    def capture(value: int, *, context: OperationContext) -> int:
        observed.append(context)
        return value + 1

    pipeline = OperationPipeline(
        [
            Operation(capture),
            Operation(capture),
        ]
    )
    pipeline.run(1)

    assert len(observed) == 2
    assert observed[0] is observed[1]
    assert observed[0].metadata == {}
    assert observed[0].provenance == {}


def test_invalid_provided_context_becomes_pipeline_execution_error() -> None:
    pipeline = OperationPipeline([Operation(increment)])

    with pytest.raises(OperationPipelineExecutionError) as exc:
        pipeline.run(1, context="bad")

    assert exc.value.context["step_index"] is None
    assert exc.value.context["phase"] == "validate_context"
    assert exc.value.context["cause_type"] == "InvalidOperationContextError"
    assert isinstance(exc.value.__cause__, InvalidOperationContextError)


def test_pipeline_execution_errors_wrap_cause_and_include_step() -> None:
    pipeline = OperationPipeline(
        [
            Operation(failure, name="failure"),
            Operation(increment),
        ]
    )

    with pytest.raises(OperationPipelineExecutionError) as exc:
        pipeline.run(1)

    assert exc.value.context["step_index"] == 0
    assert exc.value.context["operation_name"] == "failure"
    assert exc.value.context["phase"] == "run"
    assert exc.value.context["cause_type"] == "OperationExecutionError"
    assert exc.value.__cause__.__class__.__name__ == "OperationExecutionError"
    assert exc.value.__cause__.__cause__.__class__.__name__ == "ValueError"


def test_pipeline_wraps_direct_step_non_operation_result_return() -> None:
    class BadReturnStep:
        @property
        def name(self) -> str:
            return "bad-return"

        @property
        def contract(self) -> OperationContract:
            return OperationContract(input_type=int)

        def run(self, input_value: object, context: OperationContext | None = None) -> object:
            return input_value

    pipeline = OperationPipeline([BadReturnStep()])

    with pytest.raises(OperationPipelineExecutionError) as exc:
        pipeline.run(1)

    assert exc.value.context["step_index"] == 0
    assert exc.value.context["operation_name"] == "bad-return"
    assert exc.value.context["phase"] == "run"
    assert exc.value.context["cause_type"] == "TypeError"
    assert isinstance(exc.value.__cause__, TypeError)


def test_pipeline_wraps_runtime_step_input_mismatch() -> None:
    def source(value: object, *, context: OperationContext) -> str:
        return "not-an-int"

    upstream = Operation(
        source,
        name="source",
        contract=OperationContract(output_type=None),
    )
    downstream = Operation(
        multiply,
        name="typed-downstream",
        contract=OperationContract(input_type=int),
    )
    pipeline = OperationPipeline([upstream, downstream])

    with pytest.raises(OperationPipelineExecutionError) as exc:
        pipeline.run(1)

    assert exc.value.context["step_index"] == 1
    assert exc.value.context["operation_name"] == "typed-downstream"
    assert exc.value.context["cause_type"] == "InvalidOperationInputError"
    assert isinstance(exc.value.__cause__, InvalidOperationInputError)


def test_sample_operation_pipeline_runs_sequence_and_forwards_outputs() -> None:
    first = _sample_transform(_write_view_a, name="write-view-a", writes=(VIEW_A,))
    second = _sample_transform(_write_view_b, name="write-view-b", reads=(VIEW_A,), writes=(VIEW_B,))
    context = SampleOperationContext(metadata={"dataset": "synthetic"}, run_seed="seed-1")
    pipeline = SampleOperationPipeline([first, second])
    sample = _sample_with_video()

    result = pipeline.run(sample, context=context)

    assert pipeline.operations == (first, second)
    assert result.output is sample
    assert result.operation_name == "write-view-b"
    assert result.output.field(VIEW_A).payload == ("write-view-a", "seed-1")
    assert result.output.field(VIEW_B).payload == ("write-view-a", "seed-1")
    assert result.metadata["sample_field_effects"]["added"] == (str(VIEW_B),)


def test_sample_operation_pipeline_preserves_ordered_mapping_and_diagnostic_names() -> None:
    first = _sample_transform(_write_view_a, name="write-view-a", writes=(VIEW_A,))

    def fail_missing(sample: Sample, *, context: SampleOperationContext) -> Sample:
        return sample

    missing = _sample_transform(
        fail_missing,
        name="needs-view-b",
        reads=(VIEW_B,),
        writes=(VIEW_A,),
    )
    pipeline = SampleOperationPipeline(
        OrderedDict(
            [
                ("alias-write-a", first),
                ("alias-needs-b", missing),
            ]
        )
    )

    with pytest.raises(OperationPipelineExecutionError) as exc:
        pipeline.run(_sample_with_video())

    assert pipeline.operations == (first, missing)
    assert exc.value.context["step_index"] == 1
    assert exc.value.context["operation_name"] == "needs-view-b"
    assert exc.value.context["step_name"] == "alias-needs-b"
    assert exc.value.context["cause_type"] == "MissingFieldError"


def test_sample_operation_pipeline_propagates_sample_context_per_operation() -> None:
    contexts: list[SampleOperationContext] = []

    def capture_a(sample: Sample, *, context: SampleOperationContext) -> Sample:
        contexts.append(context)
        sample.set_field(VIEW_A, FieldValue(context.metadata["dataset"], schema="video.rgb.view_a.v1"))
        return sample

    def capture_b(sample: Sample, *, context: SampleOperationContext) -> Sample:
        contexts.append(context)
        sample.set_field(VIEW_B, FieldValue(context.run_seed, schema="video.rgb.view_b.v1"))
        return sample

    pipeline = SampleOperationPipeline(
        [
            _sample_transform(capture_a, name="capture-a", writes=(VIEW_A,)),
            _sample_transform(capture_b, name="capture-b", writes=(VIEW_B,)),
        ]
    )
    pipeline(
        _sample_with_video(),
        context=SampleOperationContext(metadata={"dataset": "unit"}, run_seed="seed"),
    )

    assert [context.operation_name for context in contexts] == ["capture-a", "capture-b"]
    assert [context.metadata["dataset"] for context in contexts] == ["unit", "unit"]
    assert [context.run_seed for context in contexts] == ["seed", "seed"]


def test_sample_operation_pipeline_adapts_generic_context() -> None:
    seen: list[SampleOperationContext] = []

    def capture(sample: Sample, *, context: SampleOperationContext) -> Sample:
        seen.append(context)
        sample.set_field(VIEW_A, FieldValue(context.metadata["dataset"], schema="video.rgb.view_a.v1"))
        return sample

    pipeline = SampleOperationPipeline([
        _sample_transform(capture, name="capture", writes=(VIEW_A,)),
    ])

    pipeline(_sample_with_video(), context=OperationContext(metadata={"dataset": "generic"}))

    assert seen[0].metadata["dataset"] == "generic"
    assert seen[0].operation_name == "capture"


def test_sample_operation_pipeline_rejects_invalid_construction_inputs() -> None:
    sample_step = _sample_transform(_write_view_a, name="write-view-a", writes=(VIEW_A,))

    with pytest.raises(InvalidOperationPipelineError):
        SampleOperationPipeline([])
    with pytest.raises(InvalidOperationPipelineError):
        SampleOperationPipeline("abc")
    with pytest.raises(InvalidOperationPipelineError):
        SampleOperationPipeline([("alias", sample_step)])
    with pytest.raises(InvalidOperationPipelineError) as generic_exc:
        SampleOperationPipeline([Operation(increment)])
    with pytest.raises(InvalidOperationPipelineError) as callable_exc:
        SampleOperationPipeline([increment])
    with pytest.raises(InvalidOperationPipelineError) as key_exc:
        SampleOperationPipeline({1: sample_step})  # type: ignore[dict-item]

    assert generic_exc.value.context["expected"] == "SampleOperation"
    assert generic_exc.value.context["actual"] == "Operation"
    assert callable_exc.value.context["actual"] == "function"
    assert key_exc.value.context["field"] == "operations[0].key"


def test_sample_operation_pipeline_rejects_context_with_operation_name() -> None:
    pipeline = SampleOperationPipeline([
        _sample_transform(_write_view_a, name="write-view-a", writes=(VIEW_A,)),
    ])

    with pytest.raises(OperationPipelineExecutionError) as exc:
        pipeline(_sample_with_video(), context=SampleOperationContext(operation_name="prebound"))

    assert exc.value.context["step_index"] is None
    assert exc.value.context["phase"] == "validate_context"
    assert exc.value.context["cause_type"] == "InvalidOperationContextError"


def test_sample_operation_pipeline_wraps_undeclared_mutation_with_step_diagnostics() -> None:
    def undeclared(sample: Sample, *, context: SampleOperationContext) -> Sample:
        sample.set_field(VIEW_A, FieldValue("bad", schema="video.rgb.view_a.v1"))
        return sample

    pipeline = SampleOperationPipeline(
        OrderedDict(
            [
                (
                    "mutates-without-declaration",
                    SampleTransform(
                        undeclared,
                        name="bad-transform",
                        contract=SampleOperationContract(
                            field_permissions=SampleFieldPermissions(reads=(VIDEO,), writes=(VIEW_B,)),
                        ),
                    ),
                )
            ]
        )
    )

    with pytest.raises(OperationPipelineExecutionError) as exc:
        pipeline(_sample_with_video())

    assert exc.value.context["step_index"] == 0
    assert exc.value.context["operation_name"] == "bad-transform"
    assert exc.value.context["step_name"] == "mutates-without-declaration"
    assert exc.value.context["cause_type"] == "UndeclaredSampleFieldMutationError"
