from __future__ import annotations

import importlib


PLANNED_PACKAGE_NAMES = [
    "rphys.analysis",
    "rphys.data",
    "rphys.datasources",
    "rphys.evaluation",
    "rphys.io",
    "rphys.learning",
    "rphys.losses",
    "rphys.methods",
    "rphys.metrics",
    "rphys.models",
    "rphys.nn",
    "rphys.objectives",
    "rphys.ops",
    "rphys.prediction",
    "rphys.training",
]

BROAD_ERROR_NAMES = [
    "RemotePhysAnalysisError",
    "RemotePhysCodecError",
    "RemotePhysCollateError",
    "RemotePhysDataError",
    "RemotePhysDataSourceError",
    "RemotePhysDependencyError",
    "RemotePhysEvaluationError",
    "RemotePhysFieldError",
    "RemotePhysIOError",
    "RemotePhysLearningError",
    "RemotePhysMetadataError",
    "RemotePhysMethodError",
    "RemotePhysNameError",
    "RemotePhysOperationError",
    "RemotePhysPipelineError",
    "RemotePhysSliceError",
    "RemotePhysTrainingError",
]

STAGE_1_ERROR_NAMES = [
    "InvalidDataKeyError",
    "InvalidDataTypeError",
    "InvalidFieldLocatorError",
    "InvalidMetadataKeyError",
    "InvalidSchemaNameError",
    "InvalidSplitNameError",
]

STAGE_1_DATA_MODULES = {
    "rphys.data.keys": ["DataKey", "RESERVED_NAMESPACES"],
    "rphys.data.locators": ["FieldLocator", "FieldRole"],
    "rphys.data.metadata": [
        "MetadataKey",
        "GROUP",
        "RECORD_ID",
        "SAMPLE_ID",
        "SOURCE_ID",
        "SPLIT",
        "SUBJECT_ID",
    ],
    "rphys.data.schemas": ["SchemaName"],
    "rphys.data.splits": ["SplitName", "PREDICT", "TEST", "TRAIN", "VALID"],
    "rphys.data.types": [
        "DataType",
        "ANNOTATION",
        "EMBEDDING",
        "LABEL",
        "LANDMARKS",
        "MASK",
        "METADATA",
        "QUALITY",
        "SIGNAL",
        "TIMESTAMPS",
        "VIDEO",
    ],
}

STAGE_2_DATA_EXPORTS = [
    "Batch",
    "FieldContainer",
    "CollateContext",
    "CollatePolicy",
    "CompositeDataObjectBase",
    "DataObjectBase",
    "FieldRequirement",
    "FieldSpec",
    "FieldValue",
    "Sample",
    "SampleContract",
    "collate_samples",
]

STAGE_4_SAMPLE_FIELD_EXPORTS = [
    "SampleField",
    "SampleFieldState",
]

STAGE_4_SAMPLE_BUILDER_EXPORTS = [
    "SampleBuildContext",
    "SampleBuilder",
    "SampleFieldProvenance",
    "SampleProbeResult",
]

STAGE_4_DATA_EXPORTS = [
    *STAGE_4_SAMPLE_FIELD_EXPORTS,
    *STAGE_4_SAMPLE_BUILDER_EXPORTS,
]

STAGE_4_DATA_MODULES = {
    "rphys.data.sample_fields": STAGE_4_SAMPLE_FIELD_EXPORTS,
    "rphys.data.sample_builders": STAGE_4_SAMPLE_BUILDER_EXPORTS,
}

STAGE_2_ERROR_NAMES = [
    "CollatePolicyError",
    "FieldSchemaError",
    "FieldTypeError",
    "MissingFieldError",
]

STAGE_3_IO_EXPORTS = [
    "ResourceRef",
    "FieldRef",
    "FieldIndex",
    "TemporalIndexSlice",
    "FieldView",
]

STAGE_4_IO_EXPORTS = [
    "CodecCapabilities",
    "CodecLoadResult",
    "CodecProbeResult",
    "CodecRegistry",
    "CodecSaveResult",
    "FieldCodec",
    "IOContext",
    "LoadContext",
    "MetadataSavePolicy",
    "SaveContext",
]

STAGE_3_IO_MODULES = {
    "rphys.io.resources": ["ResourceRef"],
    "rphys.io.indexes": ["FieldIndex", "TemporalIndexSlice"],
    "rphys.io.fields": ["FieldRef", "FieldView"],
    "rphys.io.codecs": STAGE_4_IO_EXPORTS,
}

STAGE_3_IO_ERROR_NAMES = [
    "InvalidFieldIndexError",
    "InvalidFieldRefError",
    "InvalidFieldViewError",
    "InvalidResourceRefError",
    "UnsupportedFieldIndexError",
]

STAGE_4_CODEC_ERROR_NAMES = [
    "InvalidCodecError",
    "CodecResolutionError",
    "UnsupportedCodecOperationError",
    "UnsupportedCodecIndexError",
    "CodecDependencyError",
    "CodecOperationError",
]

STAGE_3_DATASOURCE_EXPORTS = [
    "DataSourceRef",
    "RecordRef",
    "DataSourceSchema",
    "IndexItem",
]

STAGE_3_DATASOURCE_MODULES = {
    "rphys.datasources.refs": ["DataSourceRef", "RecordRef"],
    "rphys.datasources.schemas": ["DataSourceSchema"],
    "rphys.datasources.index_items": ["IndexItem"],
}

STAGE_5_DATASOURCE_MODULES = {
    "rphys.datasources.adapters": [
        "DataSourceAdapter",
        "DataSourceScanResult",
        "DataSourceSpec",
    ],
    "rphys.datasources.validation": [
        "DataSourceValidationReport",
        "ValidationIOPolicy",
        "ValidationIssue",
        "validate_scan_result",
    ],
    "rphys.datasources.filters": [
        "DataSourceFilter",
        "DataSourceView",
        "DataSourceViewPlan",
        "DataSourceViewResult",
        "FilterChain",
        "FilterDecision",
        "FilterResult",
        "build_view",
    ],
    "rphys.datasources.splits": [
        "CandidateGroupAssignment",
        "GroupBuilder",
        "GroupPlan",
        "GroupResult",
        "SplitAssignment",
        "SplitBuilder",
        "SplitPlan",
        "SplitResult",
    ],
    "rphys.datasources.indexes": [
        "DataSourceIndex",
        "DataSourceIndexCodec",
        "DataSourceIndexEntry",
        "DataSourceIndexManifest",
        "CompositeDataSourceIndex",
        "IndexCandidate",
        "IndexCandidatePlan",
        "IndexCandidateResult",
        "IndexCandidateView",
        "IndexBuildReport",
        "IndexBuilder",
        "IndexPlan",
        "IndexResult",
        "build_index_candidates",
        "filter_index_candidates",
    ],
}

STAGE_3_DATASOURCE_ERROR_NAMES = [
    "InvalidDataSourceRefError",
    "InvalidDataSourceSchemaError",
    "InvalidIndexItemError",
    "InvalidRecordRefError",
]

STAGE_5_DATASOURCE_ERROR_NAMES = [
    "InvalidDataSourceSpecError",
    "InvalidDataSourceScanResultError",
    "InvalidDataSourceValidationError",
    "InvalidDataSourceViewError",
    "InvalidDataSourceFilterError",
    "InvalidIndexCandidateError",
    "InvalidGroupAssignmentError",
    "InvalidSplitAssignmentError",
]


def test_import_rphys() -> None:
    import rphys

    assert rphys.__doc__
    assert rphys.__all__ == []


def test_import_ops_public_all_exports() -> None:
    import rphys
    import rphys.ops as ops

    assert ops.__all__ == [
        "OperationRole",
        "OperationMutationPolicy",
        "OperationContract",
        "Operation",
        "OperationStep",
        "OperationContext",
        "OperationResult",
        "OperationPipeline",
        "FunctionalKernel",
        "SampleFieldPermissions",
        "SampleOperationContract",
        "SampleOperationContext",
        "SampleReplayRecord",
        "SampleOperation",
    ]
    assert not hasattr(rphys, "OperationRole")
    assert not hasattr(rphys, "OperationMutationPolicy")
    assert not hasattr(rphys, "OperationContract")
    assert not hasattr(rphys, "OperationContext")
    assert not hasattr(rphys, "OperationResult")
    assert not hasattr(rphys, "Operation")
    assert not hasattr(rphys, "OperationPipeline")
    assert not hasattr(rphys, "FunctionalKernel")
    assert not hasattr(rphys, "SampleOperation")
    assert not hasattr(rphys, "SampleOperationContract")
    assert not hasattr(rphys, "SampleFieldPermissions")
    assert not hasattr(rphys, "SampleOperationContext")
    assert not hasattr(rphys, "SampleReplayRecord")


def test_import_ops_module_exports_are_scoped() -> None:
    from rphys.ops import contracts, context, core, kernels, pipelines

    assert contracts.__all__ == [
        "OperationRole",
        "OperationMutationPolicy",
        "OperationContract",
    ]
    assert context.__all__ == ["OperationContext", "OperationResult"]
    assert core.__all__ == ["OperationStep", "Operation"]
    assert kernels.__all__ == ["FunctionalKernel"]
    assert pipelines.__all__ == ["OperationPipeline"]


def test_import_ops_sample_module_exports() -> None:
    sample_module = __import__("rphys.ops.sample", fromlist=["__all__"])

    assert sample_module.__all__ == [
        "SampleFieldPermissions",
        "SampleOperationContract",
        "SampleOperationContext",
        "SampleReplayRecord",
        "SampleOperation",
    ]


def test_import_errors_phase_6_exports_are_scoped() -> None:
    from rphys import errors

    STAGE_6_OPERATION_ERROR_NAMES = [
        "InvalidOperationContractError",
        "InvalidOperationContextError",
        "InvalidOperationResultError",
        "InvalidOperationInputError",
        "OperationExecutionError",
        "InvalidOperationPipelineError",
        "OperationPipelineExecutionError",
    ]

    assert errors.__all__ == [
        "RemotePhysError",
        *STAGE_1_ERROR_NAMES,
        *STAGE_2_ERROR_NAMES,
        *STAGE_3_DATASOURCE_ERROR_NAMES,
        *STAGE_5_DATASOURCE_ERROR_NAMES,
        *STAGE_3_IO_ERROR_NAMES,
        *STAGE_4_CODEC_ERROR_NAMES,
        *STAGE_6_OPERATION_ERROR_NAMES,
        *BROAD_ERROR_NAMES,
    ]


def test_deferred_package_homes_import_with_empty_public_surfaces() -> None:
    for package_name in PLANNED_PACKAGE_NAMES:
        if package_name in {"rphys.data", "rphys.io", "rphys.datasources", "rphys.ops"}:
            continue
        package = importlib.import_module(package_name)

        assert package.__doc__
        assert package.__all__ == []


def test_errors_import_and_expose_approved_error_categories() -> None:
    from rphys import errors

    STAGE_6_OPERATION_ERROR_NAMES = [
        "InvalidOperationContractError",
        "InvalidOperationContextError",
        "InvalidOperationResultError",
        "InvalidOperationInputError",
        "OperationExecutionError",
        "InvalidOperationPipelineError",
        "OperationPipelineExecutionError",
    ]

    assert errors.__all__ == [
        "RemotePhysError",
        *STAGE_1_ERROR_NAMES,
        *STAGE_2_ERROR_NAMES,
        *STAGE_3_DATASOURCE_ERROR_NAMES,
        *STAGE_5_DATASOURCE_ERROR_NAMES,
        *STAGE_3_IO_ERROR_NAMES,
        *STAGE_4_CODEC_ERROR_NAMES,
        *STAGE_6_OPERATION_ERROR_NAMES,
        *BROAD_ERROR_NAMES,
    ]

    for error_name in errors.__all__:
        error_type = getattr(errors, error_name)

        assert issubclass(error_type, errors.RemotePhysError)


def test_root_package_does_not_reexport_error_classes() -> None:
    import rphys

    assert not hasattr(rphys, "RemotePhysError")
    for error_name in [
        *BROAD_ERROR_NAMES,
        *STAGE_1_ERROR_NAMES,
        *STAGE_2_ERROR_NAMES,
        *STAGE_3_DATASOURCE_ERROR_NAMES,
        *STAGE_5_DATASOURCE_ERROR_NAMES,
        *STAGE_3_IO_ERROR_NAMES,
        *STAGE_4_CODEC_ERROR_NAMES,
        "InvalidOperationContractError",
        "InvalidOperationContextError",
        "InvalidOperationResultError",
        "InvalidOperationPipelineError",
        "OperationPipelineExecutionError",
    ]:
        assert not hasattr(rphys, error_name)


def test_root_package_does_not_reexport_stage_3_descriptor_names() -> None:
    import rphys

    for public_name in [
        *STAGE_4_DATA_EXPORTS,
        *STAGE_3_IO_EXPORTS,
        *STAGE_4_IO_EXPORTS,
        *STAGE_3_DATASOURCE_EXPORTS,
    ]:
        assert not hasattr(rphys, public_name)


def test_io_package_reexports_only_code_backed_stage_3_descriptor_names() -> None:
    import rphys.io

    assert rphys.io.__all__ == STAGE_3_IO_EXPORTS
    for public_name in STAGE_3_IO_EXPORTS:
        assert hasattr(rphys.io, public_name)
    for public_name in STAGE_4_IO_EXPORTS:
        assert not hasattr(rphys.io, public_name)


def test_io_submodules_export_only_code_backed_names() -> None:
    for module_name, expected_all in STAGE_3_IO_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all
        for public_name in expected_all:
            assert hasattr(module, public_name)


def test_datasource_package_reexports_only_code_backed_stage_3_names() -> None:
    import rphys.datasources

    assert rphys.datasources.__all__ == STAGE_3_DATASOURCE_EXPORTS
    for public_name in STAGE_3_DATASOURCE_EXPORTS:
        assert hasattr(rphys.datasources, public_name)


def test_stage_3_datasource_submodules_export_only_code_backed_names() -> None:
    for module_name, expected_all in STAGE_3_DATASOURCE_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all
        for public_name in expected_all:
            assert hasattr(module, public_name)


def test_stage_5_datasource_submodules_start_with_empty_public_surfaces() -> None:
    for module_name, expected_all in STAGE_5_DATASOURCE_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all


def test_stage_5_datasource_names_are_not_parent_or_root_exports() -> None:
    import rphys
    import rphys.datasources

    forbidden_names = [
        "DataSourceSpec",
        "DataSourceAdapter",
        "DataSourceScanResult",
        "ValidationIssue",
        "DataSourceValidationReport",
        "ValidationIOPolicy",
        "validate_scan_result",
        "DataSourceView",
        "DataSourceViewPlan",
        "DataSourceViewResult",
        "FilterChain",
        "FilterDecision",
        "FilterResult",
        "build_view",
        "IndexCandidate",
        "IndexCandidatePlan",
        "IndexCandidateResult",
        "IndexCandidateView",
        "build_index_candidates",
        "filter_index_candidates",
        "GroupPlan",
        "GroupBuilder",
        "GroupResult",
        "CandidateGroupAssignment",
        "SplitPlan",
        "SplitBuilder",
        "SplitResult",
        "SplitAssignment",
        "DataSourceIndex",
        "DataSourceIndexEntry",
        "DataSourceIndexManifest",
        "DataSourceIndexCodec",
        "CompositeDataSourceIndex",
        "ConcatDataSourceIndex",
        "SyntheticDataSource",
    ]

    for public_name in forbidden_names:
        assert not hasattr(rphys, public_name)
        assert not hasattr(rphys.datasources, public_name)


def test_stage_1_data_modules_import_with_intentional_public_surfaces() -> None:
    for module_name, expected_all in STAGE_1_DATA_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all

        for public_name in expected_all:
            assert hasattr(module, public_name)


def test_data_package_does_not_reexport_stage_1_vocabulary() -> None:
    import rphys.data

    for public_name in {
        name for expected_all in STAGE_1_DATA_MODULES.values() for name in expected_all
    }:
        assert not hasattr(rphys.data, public_name)


def test_stage_4_data_modules_import_with_intentional_public_surfaces() -> None:
    for module_name, expected_all in STAGE_4_DATA_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all
        for public_name in expected_all:
            assert hasattr(module, public_name)


def test_data_package_reexports_only_code_backed_stage_2_runtime_names() -> None:
    import rphys.data

    assert rphys.data.__all__ == STAGE_2_DATA_EXPORTS
    for public_name in STAGE_2_DATA_EXPORTS:
        assert hasattr(rphys.data, public_name)
    for public_name in STAGE_4_DATA_EXPORTS:
        assert not hasattr(rphys.data, public_name)
