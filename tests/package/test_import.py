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

STAGE_13_SCAFFOLD_PACKAGES = [
    "rphys.prediction",
    "rphys.evaluation",
]

STAGE_13_FORBIDDEN_PUBLIC_NAMES = [
    "PredictionRecord",
    "PredictionCollection",
    "PredictionCollector",
    "PredictionRunner",
    "PredictionResult",
    "PredictionDataSource",
    "EvaluationProtocol",
    "EvaluationPlan",
    "EvaluationResult",
    "EvaluationEngine",
    "InferenceEngine",
    "EvaluationRunner",
    "Evaluator",
    "ComparisonSpec",
    "PipelineJob",
    "JobPlan",
    "JobRunner",
    "AnalysisOp",
    "AnalysisContext",
    "AnalysisResult",
    "Report",
    "ReportTable",
    "DiagnosticRenderer",
]

STAGE_13_REMOVED_OUTPUT_NAMES = [
    "MethodOutput",
    "MethodOutputSpec",
    "MethodOutputAdapter",
    "apply_method_output",
    "StepOutput",
    "StepPrediction",
]

STAGE_13_ANALYSIS_EXPORTS = [
    "DiagnosticRenderOutput",
    "DiagnosticRenderer",
    "Report",
    "ReportCell",
    "ReportOperation",
    "ReportRow",
    "ReportSection",
    "ReportTable",
    "VisualizationOperation",
    "VisualizationOutput",
    "attach_visualization_fields",
]

STAGE_13_ANALYSIS_MODULES = {
    "rphys.analysis.reports": [
        "DiagnosticRenderOutput",
        "DiagnosticRenderer",
        "Report",
        "ReportCell",
        "ReportOperation",
        "ReportRow",
        "ReportSection",
        "ReportTable",
    ],
    "rphys.analysis.visualization": [
        "VisualizationOperation",
        "VisualizationOutput",
        "attach_visualization_fields",
    ],
}

STAGE_13_FINAL_FORBIDDEN_PUBLIC_NAMES = [
    "PredictionRecord",
    "PredictionCollection",
    "PredictionCollector",
    "PredictionRunner",
    "PredictionResult",
    "PredictionDataSource",
    "BatchCollection",
    "BatchCollector",
    "EvaluationProtocol",
    "EvaluationPlan",
    "EvaluationResult",
    "EvaluationEngine",
    "InferenceEngine",
    "EvaluationRunner",
    "Evaluator",
    "ComparisonSpec",
    "PipelineJob",
    "JobPlan",
    "JobRunner",
    "AnalysisOp",
    "AnalysisContext",
    "AnalysisResult",
    "MethodOutput",
    "StepOutput",
    "MetricObservation",
    "MetricObservationCollection",
    "MetricObservationView",
    "MetricResult",
    "ReportWriter",
    "ReportRenderer",
    "ReportOutputDirectory",
]

STAGE_11_COLLECTION_EXPORTS = [
    "Collection",
    "CollectionContext",
    "CollectionItem",
    "CollectionView",
    "CollectionViewPlan",
    "Collector",
    "CollectorResult",
]

STAGE_11_DATA_COLLECTION_EXPORTS = [
    "SampleCollection",
    "SampleCollectionView",
    "SampleCollectionViewPlan",
    "SampleCollectionConcatPlan",
    "SampleCollectionGroupPlan",
    "SampleCollectionSortPlan",
    "SampleCollector",
    "PlannedSampleCollectionView",
    "concat_sample_collection_fields",
    "filter_sample_collection",
    "group_sample_collections",
    "project_sample_collection",
    "sort_sample_collection",
]

STAGE_11_LOSS_EXPORTS = [
    "Loss",
    "LossContext",
    "LossContract",
    "LossInputSpec",
    "LossResult",
    "LossTerm",
]

STAGE_11_LOSS_MODULES = {
    "rphys.losses.context": ["LossContext"],
    "rphys.losses.core": ["Loss"],
    "rphys.losses.results": ["LossResult", "LossTerm"],
    "rphys.losses.specs": ["LossContract", "LossInputSpec"],
}

STAGE_11_OBJECTIVE_EXPORTS = [
    "Objective",
    "ObjectiveContext",
    "ObjectiveContract",
    "ObjectiveResult",
    "ObjectiveTerm",
    "ObjectiveTermSpec",
]

STAGE_11_OBJECTIVE_MODULES = {
    "rphys.objectives.context": ["ObjectiveContext"],
    "rphys.objectives.core": ["Objective"],
    "rphys.objectives.results": ["ObjectiveResult", "ObjectiveTerm"],
    "rphys.objectives.specs": ["ObjectiveContract", "ObjectiveTermSpec"],
}

STAGE_11_METRIC_EXPORTS = [
    "GroupBySpec",
    "Metric",
    "MetricCollectionOperation",
    "MetricContext",
    "MetricContract",
    "MetricInputSpec",
    "MetricOutput",
    "MetricSampleOperation",
    "MetricValue",
    "collect_metric_fields",
]

STAGE_11_METRIC_MODULES = {
    "rphys.metrics.context": ["MetricContext"],
    "rphys.metrics.core": ["Metric", "MetricOutput"],
    "rphys.metrics.operations": [
        "MetricCollectionOperation",
        "MetricSampleOperation",
        "collect_metric_fields",
    ],
    "rphys.metrics.results": [
        "MetricValue",
    ],
    "rphys.metrics.specs": [
        "GroupBySpec",
        "MetricContract",
        "MetricInputSpec",
    ],
}

STAGE_12_LEARNING_EXPORTS = [
    "BackwardableScalar",
    "Learner",
    "LoopContext",
    "LoopMode",
    "SupervisedLearner",
    "require_backwardable_scalar",
]

STAGE_12_LEARNING_MODULES = {
    "rphys.learning.context": ["LoopContext"],
    "rphys.learning.core": ["Learner"],
    "rphys.learning.modes": ["LoopMode"],
    "rphys.learning.output": [
        "BackwardableScalar",
        "require_backwardable_scalar",
    ],
    "rphys.learning.supervised": ["SupervisedLearner"],
}

STAGE_12_TRAINING_EXPORTS = [
    "ProfileSummary",
    "ProfileSpanSummary",
    "TrainingEventLog",
    "NativeTrainingEngine",
    "Trainer",
    "TrainingCallback",
    "TrainingEngine",
    "TrainingEvent",
    "TrainingEventPhase",
    "TrainingEventSummary",
    "TrainingEventSink",
    "TrainingMetricSummary",
    "TrainingOutputSpec",
    "TrainingPlan",
    "TrainingProfiler",
    "TrainingProfile",
    "TrainingProfileRecorder",
    "TrainingResult",
    "TrainingStatus",
    "TrainingStepSummary",
    "UnavailableProfileProbe",
    "emit_training_event",
    "run_train",
]

STAGE_12_TRAINING_MODULES = {
    "rphys.training.backend": ["NativeTrainingEngine"],
    "rphys.training.core": ["Trainer", "TrainingEngine"],
    "rphys.training.events": [
        "TrainingCallback",
        "TrainingEvent",
        "TrainingEventPhase",
        "TrainingEventLog",
        "TrainingEventSink",
        "emit_training_event",
    ],
    "rphys.training.experimental": ["run_train"],
    "rphys.training.plan": ["TrainingOutputSpec", "TrainingPlan"],
    "rphys.training.profiling": [
    "ProfileSpanSummary",
    "TrainingProfile",
    "TrainingProfileRecorder",
    "TrainingProfiler",
    "UnavailableProfileProbe",
],
    "rphys.training.results": [
        "ProfileSummary",
        "TrainingEventSummary",
        "TrainingMetricSummary",
        "TrainingResult",
        "TrainingStatus",
        "TrainingStepSummary",
    ],
}

STAGE_10_METHOD_EXPORTS = [
    "BatchOutputFieldSpec",
    "BatchOutputSpec",
    "Method",
    "MethodInputAdapter",
    "MethodInputSpec",
    "ParameterView",
    "PredictionContext",
    "StateEntry",
    "StateLoadResult",
    "StateView",
    "StatefulMethod",
    "TrainableMethod",
    "project_batch_fields",
]

STAGE_10_METHOD_MODULES = {
    "rphys.methods.adapters": [
        "MethodInputAdapter",
        "MethodInputSpec",
    ],
    "rphys.methods.context": ["PredictionContext"],
    "rphys.methods.core": ["Method", "StatefulMethod", "TrainableMethod"],
    "rphys.methods.output": [
        "BatchOutputFieldSpec",
        "BatchOutputSpec",
        "project_batch_fields",
    ],
    "rphys.methods.state": [
        "ParameterView",
        "StateEntry",
        "StateLoadResult",
        "StateView",
    ],
}

STAGE_10_MODEL_EXPORTS = ["Model"]

STAGE_10_MODEL_MODULES = {
    "rphys.models.core": STAGE_10_MODEL_EXPORTS,
}

BROAD_ERROR_NAMES = [
    "RemotePhysAnalysisError",
    "RemotePhysCodecError",
    "RemotePhysCollateError",
    "RemotePhysCollectionError",
    "RemotePhysDataError",
    "RemotePhysDataSourceError",
    "RemotePhysDependencyError",
    "RemotePhysEvaluationError",
    "RemotePhysFieldError",
    "RemotePhysIOError",
    "RemotePhysLearningError",
    "RemotePhysLossError",
    "RemotePhysMetadataError",
    "RemotePhysMethodError",
    "RemotePhysMetricError",
    "RemotePhysNameError",
    "RemotePhysObjectiveError",
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
    "BatchCollater",
    "BatchOutputFieldSpec",
    "BatchOutputSpec",
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
    *STAGE_11_DATA_COLLECTION_EXPORTS,
    "UncollateFieldSpec",
    "UncollatePlan",
    "UncollatePolicy",
    "collate_samples",
    "project_batch_fields",
    "uncollate_batch",
    "uncollate_batch_fields",
]

STAGE_2_COLLATION_EXPORTS = [
    "BatchCollater",
    "CollateContext",
    "CollatePolicy",
    "collate_samples",
    "uncollate_batch",
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
    "rphys.data.collections": STAGE_11_DATA_COLLECTION_EXPORTS,
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

STAGE_8_DATASOURCE_MODULES = {
    "rphys.datasources.derived": [
        "DerivedDataSourceAssembly",
        "DerivedDataSourceBuilder",
    ],
}

STAGE_9_DATASOURCE_SOURCE_EXPORTS = [
    "SampleRequest",
    "SampleRuntimeContext",
    "WorkerContextFactory",
    "SampleSource",
    "IndexSampleSource",
]

STAGE_9_DATASOURCE_TORCH_EXPORTS = [
    "TorchSampleSourceDataset",
    "TorchIndexSampleDataset",
    "TorchDataLoaderPlan",
    "TorchDataLoaderBuilder",
]

STAGE_9_DATASOURCE_CACHE_EXPORTS = [
    "CacheKey",
    "CachePolicy",
    "CacheContext",
    "CacheEntry",
    "CacheManifest",
    "CacheLookupResult",
    "CacheWriteResult",
    "CacheStore",
    "LocalCacheStore",
    "CachedSampleSource",
]

STAGE_9_DATASOURCE_PREPARED_EXPORTS = [
    "PreparedField",
    "PreparedDataManifest",
    "PreparedReadRequest",
    "PreparedReadResult",
    "PreparedSampleReader",
    "PreparedSampleSource",
    "OptimizedStorageFormat",
    "OptimizedDataPlan",
    "MaterializationPlan",
    "MaterializationManifest",
    "ShardManifest",
    "ChunkMetadata",
    "AccessPatternPlan",
    "RecordLayoutMetadata",
    "BatchCostMetadata",
    "BatchSamplerPlan",
    "BatchShapePolicy",
]

STAGE_9_DATASOURCE_DATAPATH_EXPORTS = [
    "StreamingReadPlan",
    "DataLoaderState",
    "DataPathProfile",
    "DataPathBenchmark",
]

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

STAGE_8_EXPORT_EXPORTS = [
    "CodecSelectionOperation",
    "ExportMaterialization",
    "ExportPolicy",
    "ExportReport",
    "ExportSelection",
    "ExportResult",
    "ExportSpec",
    "ExportTarget",
    "FieldExportOutcome",
    "FieldExportResult",
    "IdempotencyPolicy",
    "OutputLayout",
    "RecordExportResult",
    "RecordExportRequest",
    "SaveOperation",
    "SelectedFieldExport",
    "build_sample_artifact_record",
    "export_record_requests",
    "sample_artifact_export_request",
]

STAGE_6_OPERATION_ERROR_NAMES = [
    "InvalidOperationContractError",
    "InvalidOperationContextError",
    "InvalidOperationResultError",
    "InvalidOperationInputError",
    "OperationExecutionError",
    "InvalidOperationPipelineError",
    "OperationPipelineExecutionError",
    "UndeclaredSampleFieldMutationError",
]

STAGE_11_COLLECTION_ERROR_NAMES = [
    "InvalidCollectionContextError",
    "InvalidCollectionItemError",
    "InvalidCollectionViewPlanError",
    "InvalidCollectorResultError",
]

STAGE_11_LOSS_ERROR_NAMES = [
    "InvalidLossContextError",
    "InvalidLossResultError",
    "InvalidLossSpecError",
]

STAGE_11_OBJECTIVE_ERROR_NAMES = [
    "InvalidObjectiveContextError",
    "InvalidObjectiveResultError",
    "InvalidObjectiveSpecError",
]

STAGE_11_METRIC_ERROR_NAMES = [
    "InvalidMetricContextError",
    "InvalidMetricResultError",
    "InvalidMetricSpecError",
]


def test_import_rphys() -> None:
    import rphys

    assert rphys.__doc__
    assert rphys.__all__ == []
    for public_name in [
        "SyntheticScenario",
        "SyntheticEdgeVariant",
        "make_synthetic_scenario",
        "make_edge_variant",
        "assert_index_manifest_round_trips",
    ]:
        assert not hasattr(rphys, public_name)


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
        "SampleOperationPipeline",
        "BatchOperationPipeline",
        "FunctionalKernel",
        "SampleFieldPermissions",
        "SampleOperationContract",
        "SampleOperationContext",
        "SampleReplayRecord",
        "SampleAugmentationParams",
        "SampleAugmentation",
        "SampleOperation",
        "SampleTransform",
        "SampleCheck",
        "SampleDecision",
        "SampleRoute",
        "SampleCollectionGroupOperation",
        "SampleCollectionViewOperation",
        "SampleCollectionConcatOperation",
        "BatchParameterScope",
        "BatchEquivalenceClaim",
        "BatchFieldEffects",
        "BatchOperationContext",
        "BatchOperationContract",
        "BatchAugmentationParams",
        "BatchEquivalenceReport",
        "BatchOperation",
        "BatchTransform",
        "BatchAugmentation",
    ]
    assert not hasattr(rphys, "OperationRole")
    assert not hasattr(rphys, "OperationMutationPolicy")
    assert not hasattr(rphys, "OperationContract")
    assert not hasattr(rphys, "OperationContext")
    assert not hasattr(rphys, "OperationResult")
    assert not hasattr(rphys, "Operation")
    assert not hasattr(rphys, "OperationPipeline")
    assert not hasattr(rphys, "SampleOperationPipeline")
    assert not hasattr(rphys, "BatchOperationPipeline")
    assert not hasattr(rphys, "FunctionalKernel")
    assert not hasattr(rphys, "SampleOperation")
    assert not hasattr(rphys, "SampleOperationContract")
    assert not hasattr(rphys, "SampleFieldPermissions")
    assert not hasattr(rphys, "SampleOperationContext")
    assert not hasattr(rphys, "SampleReplayRecord")
    assert not hasattr(rphys, "SampleAugmentationParams")
    assert not hasattr(rphys, "SampleAugmentation")
    assert not hasattr(rphys, "SampleTransform")
    assert not hasattr(rphys, "SampleCheck")
    assert not hasattr(rphys, "SampleDecision")
    assert not hasattr(rphys, "SampleRoute")
    assert not hasattr(rphys, "SampleCollectionGroupOperation")
    assert not hasattr(rphys, "SampleCollectionViewOperation")
    assert not hasattr(rphys, "SampleCollectionConcatOperation")
    assert not hasattr(rphys, "BatchParameterScope")
    assert not hasattr(rphys, "BatchEquivalenceClaim")
    assert not hasattr(rphys, "BatchFieldEffects")
    assert not hasattr(rphys, "BatchOperationContext")
    assert not hasattr(rphys, "BatchOperationContract")
    assert not hasattr(rphys, "BatchAugmentationParams")
    assert not hasattr(rphys, "BatchEquivalenceReport")
    assert not hasattr(rphys, "BatchOperation")
    assert not hasattr(rphys, "BatchTransform")
    assert not hasattr(rphys, "BatchAugmentation")


def test_import_ops_module_exports_are_scoped() -> None:
    from rphys.ops import contracts, context, core, export, kernels, pipelines

    assert contracts.__all__ == [
        "OperationRole",
        "OperationMutationPolicy",
        "OperationContract",
    ]
    assert context.__all__ == ["OperationContext", "OperationResult"]
    assert core.__all__ == ["OperationStep", "Operation"]
    assert export.__all__ == STAGE_8_EXPORT_EXPORTS
    assert kernels.__all__ == ["FunctionalKernel"]
    assert pipelines.__all__ == ["OperationPipeline", "SampleOperationPipeline", "BatchOperationPipeline"]


def test_import_ops_sample_module_exports() -> None:
    sample_module = __import__("rphys.ops.sample", fromlist=["__all__"])

    assert sample_module.__all__ == [
        "SampleFieldPermissions",
        "SampleOperationContract",
        "SampleOperationContext",
        "SampleReplayRecord",
        "SampleAugmentationParams",
        "SampleAugmentation",
        "SampleOperation",
        "SampleTransform",
        "SampleCheck",
        "SampleDecision",
        "SampleRoute",
        "SampleCollectionGroupOperation",
        "SampleCollectionViewOperation",
        "SampleCollectionConcatOperation",
    ]


def test_import_ops_batch_module_exports() -> None:
    batch_module = __import__("rphys.ops.batch", fromlist=["__all__"])

    assert batch_module.__all__ == [
        "BatchParameterScope",
        "BatchEquivalenceClaim",
        "BatchFieldEffects",
        "BatchOperationContext",
        "BatchOperationContract",
        "BatchAugmentationParams",
        "BatchEquivalenceReport",
        "BatchOperation",
        "BatchTransform",
        "BatchAugmentation",
    ]


def test_import_errors_phase_6_exports_are_scoped() -> None:
    from rphys import errors

    assert errors.__all__ == [
        "RemotePhysError",
        *STAGE_1_ERROR_NAMES,
        *STAGE_2_ERROR_NAMES,
        *STAGE_3_DATASOURCE_ERROR_NAMES,
        *STAGE_5_DATASOURCE_ERROR_NAMES,
        *STAGE_3_IO_ERROR_NAMES,
        *STAGE_4_CODEC_ERROR_NAMES,
        *STAGE_6_OPERATION_ERROR_NAMES,
        *STAGE_11_COLLECTION_ERROR_NAMES,
        *STAGE_11_LOSS_ERROR_NAMES,
        *STAGE_11_METRIC_ERROR_NAMES,
        *STAGE_11_OBJECTIVE_ERROR_NAMES,
        *BROAD_ERROR_NAMES,
    ]


def test_stage_11_collection_module_exports_only_code_backed_names() -> None:
    import rphys

    module = importlib.import_module("rphys.collections")

    assert module.__doc__
    assert module.__all__ == STAGE_11_COLLECTION_EXPORTS
    for public_name in STAGE_11_COLLECTION_EXPORTS:
        assert hasattr(module, public_name)
        assert not hasattr(rphys, public_name)


def test_stage_11_loss_package_exports_only_code_backed_names() -> None:
    import rphys
    import rphys.losses

    assert rphys.losses.__all__ == STAGE_11_LOSS_EXPORTS
    for public_name in STAGE_11_LOSS_EXPORTS:
        assert hasattr(rphys.losses, public_name)
        assert not hasattr(rphys, public_name)


def test_stage_11_loss_modules_export_only_code_backed_names() -> None:
    for module_name, expected_all in STAGE_11_LOSS_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all
        for public_name in expected_all:
            assert hasattr(module, public_name)


def test_stage_11_objective_package_exports_only_code_backed_names() -> None:
    import rphys
    import rphys.objectives

    assert rphys.objectives.__all__ == STAGE_11_OBJECTIVE_EXPORTS
    for public_name in STAGE_11_OBJECTIVE_EXPORTS:
        assert hasattr(rphys.objectives, public_name)
        assert not hasattr(rphys, public_name)


def test_stage_11_objective_modules_export_only_code_backed_names() -> None:
    for module_name, expected_all in STAGE_11_OBJECTIVE_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all
        for public_name in expected_all:
            assert hasattr(module, public_name)


def test_stage_11_metric_package_exports_only_code_backed_names() -> None:
    import rphys
    import rphys.metrics

    assert rphys.metrics.__all__ == STAGE_11_METRIC_EXPORTS
    for public_name in STAGE_11_METRIC_EXPORTS:
        assert hasattr(rphys.metrics, public_name)
        assert not hasattr(rphys, public_name)


def test_stage_11_metric_modules_export_only_code_backed_names() -> None:
    for module_name, expected_all in STAGE_11_METRIC_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all
        for public_name in expected_all:
            assert hasattr(module, public_name)


def test_stage_11_does_not_expose_rejected_metric_table_names() -> None:
    import rphys.metrics

    for public_name in [
        "MetricObservation",
        "MetricObservationCollection",
        "MetricObservationView",
        "MetricObservationViewPlan",
        "MetricResult",
        "PlannedMetricObservationView",
        "MetricResultRow",
        "MetricResultTable",
        "MetricAggregationResult",
        "MetricObservationViewResult",
        "MetricObservationViewState",
    ]:
        assert not hasattr(rphys.metrics, public_name)


def test_deferred_package_homes_import_with_empty_public_surfaces() -> None:
    for package_name in PLANNED_PACKAGE_NAMES:
        if package_name in {
            "rphys.data",
            "rphys.io",
            "rphys.datasources",
            "rphys.learning",
            "rphys.methods",
            "rphys.models",
            "rphys.losses",
            "rphys.metrics",
            "rphys.objectives",
            "rphys.ops",
            "rphys.analysis",
            "rphys.training",
        }:
            continue
        package = importlib.import_module(package_name)

        assert package.__doc__
        assert package.__all__ == []


def test_stage_13_scaffold_packages_are_empty_and_code_backed() -> None:
    for package_name in STAGE_13_SCAFFOLD_PACKAGES:
        package = importlib.import_module(package_name)

        assert package.__doc__
        assert package.__all__ == []
        for public_name in STAGE_13_FORBIDDEN_PUBLIC_NAMES:
            assert not hasattr(package, public_name)


def test_stage_13_scaffold_uses_existing_broad_error_categories() -> None:
    from rphys import errors

    assert errors.RemotePhysEvaluationError.__doc__
    assert errors.RemotePhysAnalysisError.__doc__
    assert "RemotePhysEvaluationError" in errors.__all__
    assert "RemotePhysAnalysisError" in errors.__all__
    assert "RemotePhysPredictionError" not in errors.__all__
    assert not hasattr(errors, "RemotePhysPredictionError")


def test_stage_13_analysis_package_exports_only_code_backed_names() -> None:
    import rphys
    import rphys.analysis

    assert rphys.analysis.__all__ == STAGE_13_ANALYSIS_EXPORTS
    for public_name in STAGE_13_ANALYSIS_EXPORTS:
        assert hasattr(rphys.analysis, public_name)
        assert not hasattr(rphys, public_name)

    for rejected_name in ["AnalysisOp", "AnalysisContext", "AnalysisResult"]:
        assert rejected_name not in rphys.analysis.__all__
        assert not hasattr(rphys.analysis, rejected_name)


def test_stage_13_analysis_modules_export_only_code_backed_names() -> None:
    for module_name, expected_all in STAGE_13_ANALYSIS_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all
        for public_name in expected_all:
            assert hasattr(module, public_name)


def test_stage_13_final_forbidden_public_surfaces_remain_absent() -> None:
    modules = (
        importlib.import_module("rphys"),
        importlib.import_module("rphys.analysis"),
        importlib.import_module("rphys.evaluation"),
        importlib.import_module("rphys.learning"),
        importlib.import_module("rphys.methods"),
        importlib.import_module("rphys.metrics"),
        importlib.import_module("rphys.prediction"),
    )

    for public_name in STAGE_13_FINAL_FORBIDDEN_PUBLIC_NAMES:
        for module in modules:
            assert public_name not in getattr(module, "__all__", ())
            assert not hasattr(module, public_name)


def test_stage_13_removed_method_and_learner_output_names_are_absent() -> None:
    import rphys
    import rphys.learning
    import rphys.learning.output
    import rphys.methods
    import rphys.methods.adapters
    import rphys.methods.output

    modules = (
        rphys,
        rphys.methods,
        rphys.methods.output,
        rphys.methods.adapters,
        rphys.learning,
        rphys.learning.output,
    )
    for public_name in STAGE_13_REMOVED_OUTPUT_NAMES:
        for module in modules:
            assert public_name not in getattr(module, "__all__", ())
            assert not hasattr(module, public_name)


def test_stage_12_learning_package_exports_only_code_backed_contract_names() -> None:
    import rphys
    import rphys.learning

    assert rphys.learning.__all__ == STAGE_12_LEARNING_EXPORTS
    for public_name in STAGE_12_LEARNING_EXPORTS:
        assert hasattr(rphys.learning, public_name)
        assert not hasattr(rphys, public_name)


def test_stage_12_learning_modules_export_only_code_backed_names() -> None:
    for module_name, expected_all in STAGE_12_LEARNING_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all
        for public_name in expected_all:
            assert hasattr(module, public_name)


def test_stage_12_training_package_exports_only_code_backed_contract_names() -> None:
    import rphys
    import rphys.training

    assert rphys.training.__all__ == STAGE_12_TRAINING_EXPORTS
    for public_name in STAGE_12_TRAINING_EXPORTS:
        assert hasattr(rphys.training, public_name)
        assert not hasattr(rphys, public_name)


def test_stage_12_training_modules_export_only_code_backed_names() -> None:
    for module_name, expected_all in STAGE_12_TRAINING_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all
        for public_name in expected_all:
            assert hasattr(module, public_name)


def test_stage_10_method_package_exports_only_code_backed_contract_names() -> None:
    import rphys
    import rphys.methods

    assert rphys.methods.__all__ == STAGE_10_METHOD_EXPORTS
    for public_name in STAGE_10_METHOD_EXPORTS:
        assert hasattr(rphys.methods, public_name)
        assert not hasattr(rphys, public_name)


def test_stage_10_method_modules_export_only_code_backed_names() -> None:
    for module_name, expected_all in STAGE_10_METHOD_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all
        for public_name in expected_all:
            assert hasattr(module, public_name)


def test_stage_10_model_package_exports_only_code_backed_contract_names() -> None:
    import rphys
    import rphys.models

    assert rphys.models.__all__ == STAGE_10_MODEL_EXPORTS
    for public_name in STAGE_10_MODEL_EXPORTS:
        assert hasattr(rphys.models, public_name)
        assert not hasattr(rphys, public_name)


def test_stage_10_model_modules_export_only_code_backed_names() -> None:
    for module_name, expected_all in STAGE_10_MODEL_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all
        for public_name in expected_all:
            assert hasattr(module, public_name)


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
        "UndeclaredSampleFieldMutationError",
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
        *STAGE_11_COLLECTION_ERROR_NAMES,
        *STAGE_11_LOSS_ERROR_NAMES,
        *STAGE_11_METRIC_ERROR_NAMES,
        *STAGE_11_OBJECTIVE_ERROR_NAMES,
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
        "InvalidOperationInputError",
        "OperationExecutionError",
        "InvalidOperationPipelineError",
        "OperationPipelineExecutionError",
        "UndeclaredSampleFieldMutationError",
        *STAGE_11_COLLECTION_ERROR_NAMES,
        *STAGE_11_LOSS_ERROR_NAMES,
        *STAGE_11_METRIC_ERROR_NAMES,
        *STAGE_11_OBJECTIVE_ERROR_NAMES,
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


def test_stage_8_datasource_submodules_export_only_code_backed_names() -> None:
    for module_name, expected_all in STAGE_8_DATASOURCE_MODULES.items():
        module = importlib.import_module(module_name)

        assert module.__doc__
        assert module.__all__ == expected_all
        for public_name in expected_all:
            assert hasattr(module, public_name)


def test_stage_9_sample_source_module_exports_only_code_backed_names() -> None:
    module = importlib.import_module("rphys.datasources.sources")

    assert module.__all__ == STAGE_9_DATASOURCE_SOURCE_EXPORTS
    for public_name in STAGE_9_DATASOURCE_SOURCE_EXPORTS:
        assert hasattr(module, public_name)


def test_stage_9_torch_adapter_module_exports_only_code_backed_names() -> None:
    module = importlib.import_module("rphys.datasources.torch")

    assert module.__all__ == STAGE_9_DATASOURCE_TORCH_EXPORTS
    for public_name in STAGE_9_DATASOURCE_TORCH_EXPORTS:
        assert hasattr(module, public_name)


def test_stage_9_cache_module_exports_only_code_backed_names() -> None:
    module = importlib.import_module("rphys.datasources.cache")

    assert module.__all__ == STAGE_9_DATASOURCE_CACHE_EXPORTS
    for public_name in STAGE_9_DATASOURCE_CACHE_EXPORTS:
        assert hasattr(module, public_name)


def test_stage_9_prepared_module_exports_only_code_backed_names() -> None:
    module = importlib.import_module("rphys.datasources.prepared")

    assert module.__all__ == STAGE_9_DATASOURCE_PREPARED_EXPORTS
    for public_name in STAGE_9_DATASOURCE_PREPARED_EXPORTS:
        assert hasattr(module, public_name)


def test_stage_9_datapath_module_exports_only_code_backed_names() -> None:
    module = importlib.import_module("rphys.datasources.datapath")

    assert module.__all__ == STAGE_9_DATASOURCE_DATAPATH_EXPORTS
    for public_name in STAGE_9_DATASOURCE_DATAPATH_EXPORTS:
        assert hasattr(module, public_name)


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
        "DerivedDataSourceAssembly",
        "DerivedDataSourceBuilder",
        "SampleRequest",
        "SampleRuntimeContext",
        "WorkerContextFactory",
        "SampleSource",
        "IndexSampleSource",
        "TorchSampleSourceDataset",
        "TorchIndexSampleDataset",
        "TorchDataLoaderPlan",
        "TorchDataLoaderBuilder",
        "CacheKey",
        "CachePolicy",
        "CacheContext",
        "CacheEntry",
        "CacheManifest",
        "CacheLookupResult",
        "CacheWriteResult",
        "CacheStore",
        "LocalCacheStore",
        "CachedSampleSource",
        "PreparedField",
        "PreparedDataManifest",
        "PreparedReadRequest",
        "PreparedReadResult",
        "PreparedSampleReader",
        "PreparedSampleSource",
        "OptimizedStorageFormat",
        "OptimizedDataPlan",
        "MaterializationPlan",
        "MaterializationManifest",
        "ShardManifest",
        "ChunkMetadata",
        "AccessPatternPlan",
        "RecordLayoutMetadata",
        "BatchCostMetadata",
        "BatchSamplerPlan",
        "BatchShapePolicy",
        "StreamingReadPlan",
        "DataLoaderState",
        "DataPathProfile",
        "DataPathBenchmark",
    ]

    for public_name in forbidden_names:
        assert not hasattr(rphys, public_name)
        assert not hasattr(rphys.datasources, public_name)


def test_stage_8_export_names_are_scoped_to_export_module() -> None:
    import rphys
    import rphys.ops
    import rphys.ops.export

    assert rphys.ops.export.__all__ == STAGE_8_EXPORT_EXPORTS
    for public_name in STAGE_8_EXPORT_EXPORTS:
        assert hasattr(rphys.ops.export, public_name)
        assert not hasattr(rphys.ops, public_name)
        assert not hasattr(rphys, public_name)
    for shorthand_name in ["SaveOp", "CodecSelectionOp"]:
        assert not hasattr(rphys.ops.export, shorthand_name)
        assert not hasattr(rphys.ops, shorthand_name)
        assert not hasattr(rphys, shorthand_name)


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


def test_collation_module_exports_only_code_backed_names() -> None:
    import rphys.data.collation

    assert rphys.data.collation.__all__ == STAGE_2_COLLATION_EXPORTS
    for public_name in STAGE_2_COLLATION_EXPORTS:
        assert hasattr(rphys.data.collation, public_name)
