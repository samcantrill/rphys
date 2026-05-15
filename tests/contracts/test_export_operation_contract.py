from __future__ import annotations

from pathlib import Path

from rphys.data.fields import FieldValue
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.io.codecs import (
    CodecCapabilities,
    CodecRegistry,
    CodecSaveResult,
    MetadataSavePolicy,
)
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef
from rphys.ops import Operation, OperationPipeline, OperationStep
from rphys.ops.contracts import OperationContract, OperationMutationPolicy
from rphys.ops.context import OperationResult
from rphys.ops.export import (
    CodecSelectionOperation,
    ExportSelection,
    ExportSpec,
    ExportTarget,
    RecordExportRequest,
)


class _Codec:
    name = "synthetic"
    capabilities = CodecCapabilities(
        can_save=True,
        metadata_policies=(MetadataSavePolicy.REFERENCE_ONLY,),
    )

    def supports_save(self, value: FieldValue, context) -> bool:
        return str(context.target.key) == "signal.bvp"

    def save(self, value: FieldValue, context) -> CodecSaveResult:
        raise AssertionError("selection must not call codec.save")


def _request(tmp_path: Path) -> RecordExportRequest:
    source = ResourceRef("file:///source/r001/signal.bvp.bin", "file")
    source_field = FieldRef("signal.bvp", (source,), schema="signal.bvp.v1")
    return RecordExportRequest(
        source_record=RecordRef(
            DataSourceRef("synthetic"),
            "record-001",
            {"signal.bvp": source_field},
        ),
        field_values={"signal.bvp": FieldValue([1.0], schema="signal.bvp.v1")},
        spec=ExportSpec(("signal.bvp",), codec_requests={"signal.bvp": "synthetic"}),
        target=ExportTarget(ResourceRef(tmp_path.as_uri(), "file"), "exp-001"),
    )


def test_codec_selection_operation_satisfies_operation_step_contract(
    tmp_path: Path,
) -> None:
    operation = CodecSelectionOperation(CodecRegistry((_Codec(),)))

    assert isinstance(operation, OperationStep)
    assert isinstance(operation.contract, OperationContract)
    assert operation.contract.input_type is RecordExportRequest
    assert operation.contract.output_type is ExportSelection
    assert operation.contract.mutation_policy == OperationMutationPolicy.PURE
    assert operation.contract.side_effects == ()

    result = operation(_request(tmp_path))

    assert isinstance(result, OperationResult)
    assert result.operation_name == operation.name
    assert isinstance(result.output, ExportSelection)
    assert result.side_effect_evidence == {}


def test_codec_selection_operation_pipeline_forwards_output(
    tmp_path: Path,
) -> None:
    selection = CodecSelectionOperation(CodecRegistry((_Codec(),)))

    def downstream(input_value: ExportSelection, *, context) -> OperationResult:
        return OperationResult(
            input_value.selected_fields[0].target,
            operation_name="downstream",
        )

    pipeline = OperationPipeline(
        (
            selection,
            Operation(
                downstream,
                name="downstream",
                contract=OperationContract(
                    input_type=ExportSelection,
                    output_type=FieldRef,
                ),
            ),
        )
    )

    result = pipeline.run(_request(tmp_path))

    assert isinstance(result.output, FieldRef)
    assert result.output.key == "signal.bvp"
