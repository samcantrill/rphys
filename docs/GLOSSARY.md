# rphys Glossary

This glossary standardizes language used across `rphys`. It is both
descriptive and normative: it records how the repository currently uses terms
and gives preferred wording for future code, docs, tests, and roadmap text.

This file summarizes vocabulary already established in `docs/roadmap.md` and
code-backed public contracts. If a specific public API, docstring, or roadmap
section disagrees with this file, the code-backed contract and roadmap win.

## How To Use This File

- Prefer canonical terms in public APIs, docstrings, tests, and user-facing
  docs.
- Use descriptive English terms in prose when helpful, but do not quietly
  promote them into new public API families.
- When deciding between `field` and `metadata`, use `field` for structured
  payloads that can be loaded, sliced, transformed, collated, saved, or
  analyzed, and use `metadata` for descriptive context.

## Repository And Workflow Terms

| Term | Preferred meaning | Avoid or distinguish from |
| --- | --- | --- |
| `DataSource` | Canonical term for datasource discovery, views, splits, indexes, and adapters. Public package home: `rphys.datasources`. | Do not replace this with `Dataset` in public API names. |
| `Dataset` | Descriptive English only, such as "raw dataset" or "license-safe dataset". | Do not introduce `rphys.datasets` or `DatasetRef` as canonical public APIs without an explicit roadmap decision. |
| `Contract` | Documented and tested behavior that downstream code may rely on. | Do not use it for rough notes, implementation sketches, or undocumented helpers. |
| Public API | The documented, tested extension surface. Public imports become contractual when code, tests, and docs agree on behavior. | Not every importable helper or implementation detail is public API. |
| `Artifact`, `Stage`, workflow runtime | Out of scope for `rphys` as canonical library vocabulary. Those concerns belong to downstream projects or `loom`. | Do not introduce generic workflow-runtime abstractions as core `rphys` terms. |

## Computation And Modeling Terms

| Term | Preferred meaning | Avoid or distinguish from |
| --- | --- | --- |
| `Operation` | Generic context-aware callable wrapper. | Do not use it as a synonym for every semantic role in the library. |
| `OperationStep` | Public execution protocol for operation-like objects with a name, contract, and `run()` method returning `OperationResult`. | Not a registry, workflow stage, persistence handle, or general plugin interface. Ordinary callables should normally be wrapped by concrete operation classes. |
| `SampleOp` | Roadmap shorthand for sample-side operation behavior. Code-facing public APIs use full names such as `SampleOperation`, `SampleTransform`, `SampleAugmentation`, `SampleCheck`, and `SampleOperationPipeline`. | Do not introduce abbreviated public aliases such as `SampleOp` or `SampleOpPipeline` without an explicit roadmap decision. |
| `BatchOp` | Roadmap shorthand for provisional batch-side operation behavior. Code-facing public APIs use full names such as `BatchOperation`, `BatchTransform`, `BatchAugmentation`, and `BatchOperationPipeline`. | Do not introduce abbreviated public aliases such as `BatchOp` or `BatchOpPipeline` without an explicit roadmap decision. |
| `SampleOperation` | A callable-first `Sample -> Sample` operation over runtime fields with declared `FieldLocator` reads/writes/deletes, copy mode, context, and field-effect enforcement. | Distinct from datasource discovery, lazy indexing, export/materialization, and training orchestration. It does not transparently track payload-internal mutation. |
| `SampleOperationPipeline` | Ordered composition of `SampleOperation` steps. Sequences use operation names; insertion-ordered mappings use keys as diagnostics only. | Not the generic sequence-only `OperationPipeline`, not a DAG/routing graph, and not a workflow engine. |
| `BatchOperation` | Provisional batch-side operation over collated `Batch` fields with explicit field permissions, descriptive dtype/device metadata, and optional equivalence evidence to sample-side behavior. | Not a DataLoader, model input adapter, device mover, tensor layout policy, export operation, or broad batch program. |
| `BatchOperationPipeline` | Ordered composition of provisional `BatchOperation` steps with sequence or insertion-ordered mapping construction and diagnostic mapping keys. | Not a backend execution planner, loader policy, or workflow runtime. |
| `Transform` | An `Operation` whose main purpose is transformed output. | Not every operation is best described as a transform. |
| Augmentation params | Lightweight runtime parameter evidence sampled before deterministic augmentation application. `SampleAugmentationParams` records sample-side values, linked fields, and view locators; `BatchAugmentationParams` records explicit batch or per-sample scope. | Not a cache key, export schema, RNG object, backend tensor, or durable experiment artifact. |
| Replay record | Runtime evidence for reproducing stochastic augmentation decisions, such as seed material, epoch, worker, item/sample identity, operation index, operation name, and view name when available. | Not a full provenance database, cache identity, or export manifest. |
| Batch equivalence report | Descriptive evidence for whether a `BatchOperation` can replace sample-side behavior exactly, approximately, diagnostically, or not at all. | Not a numeric proof engine, mask/alignment implementation, model adapter, or device policy. |
| `Method` | A batch-level prediction or representation algorithm whose `predict` method returns an ordinary `Batch` with prediction or representation fields. | Distinct from `Model`, `Loss`, `Objective`, and `Metric`. |
| `PredictionContext` | Generic primitive prediction-time metadata and provenance supplied to a `Method`. | Not a trainer context, dataloader handle, device policy, split policy, or first-class sample/batch identifier record. |
| `BatchOutputSpec` | Generic returned-`Batch` validation and construction policy over declared output locators, optional schema/type checks, pass-through fields, and extra-field policy. | Not a method-specific patch record, export manifest, metric result, trainer step result, or hidden mutation request. |
| `Model` | A lower-level computational object or callable adapter over backend-native values. | Do not use `Model` when the contract really includes prediction semantics, adapters, or batch-level behavior; that is usually a `Method`. Do not make `Model` imply one tensor framework. |
| `StateView` | Descriptive view of named method state entries with primitive metadata/provenance and opaque backend-native values. | Not a checkpoint schema, file writer, device mover, distributed-state protocol, or framework-specific `state_dict`. |
| `ParameterView` | Descriptive named handle for a trainable or inspectable backend-native method parameter. | Not an optimizer group, scheduler policy, device placement rule, checkpoint record, or mandatory torch/JAX/NumPy parameter. |
| `Loss` | A differentiable error or penalty term. | Distinct from `Metric`, which reports rather than optimizes. |
| `Objective` | The optimizer-facing aggregation that produces the scalar used for backward. | Do not collapse `Loss` and `Objective` into one term when aggregation semantics matter. |
| `Metric` | A detached measurement and reporting contract. | Not a differentiable optimization target by default. |
| `MetricValue` | A detached, non-differentiable metric payload that is written through declared `metrics/<key>` fields. | Not a metric row, metric result table, observation collection, evaluator lifecycle object, or dataframe record. |
| `MetricSampleOperation` | Adapter that runs a `Metric` against a `Sample` and writes the metric contract's declared fields onto the returned sample. | Not trainer-owned prediction capture, prediction storage, evaluator state, or a metric observation/result wrapper. |
| `MetricCollectionOperation` | Adapter that runs a collection-level `Metric` against a `SampleCollection` and returns metric-field-bearing samples with explicit replication metadata. | Not a public evaluation engine, metric catalog, report writer, or hidden aggregation lifecycle. |
| `Learner` | The object that owns mode-specific step semantics and returns a `Batch`, often composing `Method` plus optional `Objective` and `Metric` behavior. | Distinct from `Trainer`, which owns iteration and execution mechanics. |
| `LoopMode` | The active learner/training execution semantics: `train`, `validate`, `test`, or `predict`. | Not a datasource split, workflow stage, roadmap phase, or artifact stage. Use context `split` for data partition labels. |
| `LoopContext` | Primitive learner-step context carrying mode, optional split, epoch/step/batch indexes, metadata, and provenance. | Not a dataloader handle, framework trainer state, checkpoint reference, or artifact context. |
| `TrainingOutputSpec` | `TrainingPlan`-owned declaration of learner-returned objective, loss, metric, diagnostic, and mode-required `Batch` fields consumed by training engines. | Not a learner-owned result class, metric contract, export manifest, or prediction materialization policy. |
| `TrainingPlan` | Caller-assembled training inputs such as batch iterables, loop limits, backend hooks, output-field declarations, and observe-only event/profiler hooks. | Not a learner container, datasource scanner, dataloader builder, project config, artifact directory, or generic `engine_config`. |
| `Trainer` | Facade that delegates `fit`, `validate`, `test`, and `predict` to the selected `TrainingEngine`; by default this is the reference `NativeTrainingEngine`. | Do not put datasource logic, scientific metrics, prediction export policy, or framework-private behavior inside the `Trainer`. |
| `TrainingEngine` | Loop owner that receives `TrainingPlan` and `Learner` separately. | Not a registry, config schema, logger adapter, checkpoint writer, or required inheritance base. |
| `TrainingResult` | Primitive summary of engine outcome: status, mode, counts, failures, metric summaries, last-step evidence, events, profiles, and optional checkpoint identifiers. | Not raw framework trainer state, optimizer/scheduler state, callback internals, or checkpoint file contents. |
| `TrainingEvent` | Observe-only primitive event for native and adapter-owned training loops. | Events do not control loops, choose splits, compute metrics, or mutate learner semantics. |
| `TrainingProfiler` | Observer-only profiling capability that can produce primitive span summaries or unavailable probes. | Not a hidden synchronization policy, framework profiler timeline, or mandatory dependency on device APIs. |
| `Analysis` | Evaluation, summarization, interpretation, or reporting work over predictions, metrics, and provenance-aware outputs. | Distinct from training, checkpoint selection, or datasource crawling. |
| `VisualizationOutput` | In-memory, field-ready visualization descriptor carrying a kind, codec key or hint, payload, metadata, and provenance for later optional rendering/export. | Not a plotting backend object, image/video writer, file path, dashboard handle, or implicit export side effect. |
| `VisualizationOperation` | Operation-compatible adapter that attaches `VisualizationOutput` descriptor fields to copied `Sample`, `Batch`, or `SampleCollection` outputs. | Not a render engine, plotting registry, report writer, artifact store, or output directory convention. |
| `Report` | Side-effect-free structured report record containing ordered sections, metadata, diagnostics, and provenance. | Not a markdown/HTML/PDF writer, dataframe, dashboard, artifact manifest, or evaluation runner result. |
| `ReportSection` | Named in-memory report section that groups text and ordered `ReportTable` records. | Not a page layout, template engine, file section, or renderer-specific block. |
| `ReportTable` | Ordered in-memory table with validated primitive, metric, or visualization cells plus metadata, diagnostics, and provenance. | Not a pandas dataframe, CSV writer, metric result table family, or hidden aggregation lifecycle. |
| `ReportOperation` | Operation-compatible adapter that builds a `Report` or `ReportTable` from samples, collections, metric fields, summary fields, visualization fields, or primitives. | Not a generic analysis engine, evaluation runner, report save convention, or filesystem writer. |
| `DiagnosticRenderer` | Structural callable that returns diagnostic output records as data. | Not a backend renderer, GUI/dashboard adapter, file writer, or dependency-bearing visualization implementation. |
| `DiagnosticRenderOutput` | In-memory diagnostic renderer result containing the renderer name, report/table/visualization output, metadata, diagnostics, and provenance. | Not rendered bytes, a saved file, a dataframe, or a durable artifact record. |
| `Export` | An operation that writes fields or derived outputs through codecs and may emit derived refs or datasources. | Not datasource discovery and not implicit codec side effects. |

## Core Data And Naming Terms

| Term | Preferred meaning | Avoid or distinguish from |
| --- | --- | --- |
| `Field` | Any loadable, transformable, collatable, predictable, evaluable, or analyzable structured payload. Video is a common field, not a privileged field. | Do not reserve `field` for only tensors or only video-like payloads. |
| `Metadata` | Descriptive context about a datasource, record, sample, split, group, run, or global setting. | If it needs to be loaded, sliced, transformed, collated, saved, or analyzed as structured payload, it is usually a field instead. |
| Metadata field | A field whose content is metadata-like but operationally behaves like a normal field because it must be loaded, sliced, transformed, collated, saved, or analyzed. | Distinguish this from ordinary descriptive metadata. |
| Field metadata | Narrow metadata attached to a `FieldValue` or selected by `#<metadata-key>` on a `FieldLocator`. | Do not conflate this with sample-level, record-level, or global metadata. |
| `DataKey` | Intrinsic logical field identity, such as `video.rgb` or `signal.bvp.reference`. | Not a runtime role, filesystem path, schema name, codec key, metadata selector, config path, or container lookup. |
| `DataType` | A broad backend-agnostic field category such as `video`, `signal`, or `mask`. | Not a schema name, Python dtype, tensor dtype, backend dtype, or payload validator. |
| `SchemaName` | A versioned name for loaded interpretation, layout, units, coordinate meaning, and related semantic reading of a field, such as `video.rgb.v1`. | Not a `DataKey`, not a codec key, and not a full payload-validation engine by itself. |
| `FieldRole` | The runtime role vocabulary carried by `FieldLocator`, such as `inputs`, `targets`, `predictions`, `outputs`, `metrics`, or `diagnostics`. | Do not encode runtime role inside `DataKey`. |
| `FieldLocator` | A role-qualified field address of the form `<role>/<data-key>[#<metadata-key>]`. | Not sample lookup logic, mutation logic, routing logic, or datasource indexing. |
| `SplitName` | A partition or usage label such as `train`, `valid`, `test`, or `predict`. | Not trainer loop mode, leakage policy, or evaluation dispatch logic. |
| `Provenance` | Recoverable information about where data came from and what happened to it, including identities, splits, indexes, schemas, and operation order when relevant. | Not just a file path or one ID string. Provenance should remain inspectable. |

## Runtime And Lazy-IO Terms

| Term | Preferred meaning | Avoid or distinguish from |
| --- | --- | --- |
| Lazy IO | The phase and object family that describe what to load without loading payloads yet. | Not runtime processing and not transform or augmentation logic. |
| Runtime | The in-memory phase after payloads are loaded or wrapped and before operations, methods, losses, metrics, or analysis consume them. | Distinct from datasource discovery and lazy reference construction. |
| Record | A stable logical record before windowing. | Distinguish from `Sample`, which is a runtime item and may represent one whole record or one view or window from it. |
| `DataSourceRef` | The lazy descriptor for datasource identity, optional source resource, optional declaration schema, and datasource-level metadata. | Not a datasource scanner, filter, split builder, validation report, manifest, or fingerprint. |
| `RecordRef` | The lazy reference object for a stable logical record before windowing, including record identity, field presence, and leakage-sensitive metadata. | Not a loaded runtime sample. |
| `Sample` | The per-item runtime container after payloads are loaded or wrapped. | Not a fixed `(inputs, targets)` tuple and not necessarily the same thing as a record. |
| `SampleCollection` | Immutable-membership runtime collection of `Sample` entries with item metadata/provenance for grouping, sorting, filtering, metric binding, stitching, export, and report recipes. | Not `Batch`, not a datasource scan result, and not a prediction/metric-specific storage family. |
| `SampleCollectionGroupPlan` | Explicit runtime grouping descriptor for turning sample streams into grouped `SampleCollection` snapshots using item metadata and optional field keys. | Not split construction, datasource indexing, or tensor-axis inference. |
| `SampleCollectionConcatPlan` | Explicit descriptor for stitching or concatenating member sample fields into revised sample fields through an injected or default payload joiner. | Not a concrete physiological reconstruction algorithm, resampler, filter, or alignment policy by itself. |
| `Batch` | The collated runtime container. It exposes the same field access shape as `Sample`. | Do not treat it as merely a list of samples or as a subtype that erases the sample-vs-batch distinction in documentation. |
| `UncollatePlan` | Explicit policy for splitting, broadcasting, dropping, or rejecting returned `Batch` fields into one `Sample` per item before durable handoff. | Not tensor-axis inference, temporal stitching, datasource scanning, export writing, or physiological reconstruction. |
| Sample artifact record | Descriptor-backed per-`Sample` export/reload record assembled from a source `RecordRef` plus declared derived field refs. | Not prediction storage, a prediction manifest, a workflow artifact store, a batch-as-one-record export, or an implicit datasource scan. |
| `DataSourceSchema` | A declaration-only map from intrinsic `DataKey`s to `FieldSpec`s for fields a datasource is expected to expose. | Not observed payload validation, expected-versus-observed evidence, schema-version envelope, or manifest. |
| `ResourceRef` | A reference to an addressable storage target through URI, protocol, and storage options. | Not a parsed path, codec key, artifact-store handle, workflow lifecycle object, canonical identity, or fingerprint. |
| `FieldRef` | A serializable lazy reference to one complete logical field. | It does not contain runtime role, `FieldLocator`, temporal slice, loaded tensors, or open handles. |
| `TemporalIndexSlice` | A half-open `[start, stop)` integer slice in one field's native index space. | Not seconds, spatial crop, resampling instruction, padding rule, or cross-field alignment claim. |
| `FieldView` | A `FieldRef` plus optional field-native access behavior such as a `FieldIndex`. | Distinct from a loaded field payload and not a role-qualified sample field. |
| `IndexItem` | A mapping from role-qualified `FieldLocator`s to `FieldView`s with mandatory `RecordRef` provenance. This is the unit consumed by `SampleBuilder`. | It must remain pure lazy IO and must not contain item IDs, fingerprints, payloads, transforms, augmentations, method logic, export logic, or training logic. |
| `FieldCodec` | The structural codec shape for probing, loading, and saving logical fields and field views. | Not a mandatory base class, datasource scanner, split chooser, transform, or trainer concern. |
| `CodecRegistry` | An explicit instance-local ordered resolver for codec objects. | Not process-global discovery, symbolic config lookup, entry-point loading, or hidden priority policy. |
| `LoadContext` | Datasource-neutral context for probing or loading one `FieldView`, plus primitive operation metadata. | Not a `RecordRef`, `IndexItem`, split, locator, sample identity, member binding, alignment descriptor, or cache key. |
| `SaveContext` | Datasource-neutral context for saving one logical field target through a `FieldRef` and explicit metadata-save policy. | Not an export layout, manifest writer, datasource mutation, or implicit metadata persistence rule. |
| `Codec` | The boundary object that probes, loads, and saves logical fields and field views. | A codec does not choose splits, parse trainer concerns, or own transform logic. |
| `SampleField` | A `FieldValue`-compatible lazy runtime field handle stored directly in a `Sample`; payload access materializes once and retains success or failure state. | Not a cache policy, retry API, datasource record, export instruction, or model-formatted tuple. |
| `SampleBuilder` | The one-`IndexItem` bridge from role-qualified `FieldView`s to runtime `Sample` objects with lazy `SampleField` handles and builder-side provenance. | It should not scan datasources, choose splits, apply ops, move devices implicitly, cache, format for models, or push record provenance into codec contexts. |

## Common Identity And Grouping Metadata

| Term | Preferred meaning | Avoid or distinguish from |
| --- | --- | --- |
| `source_id` | A generic identifier for the upstream source, source system, or acquisition context. | Do not assume it is always the same as `subject_id` or `record_id`. |
| `subject_id` | Subject or participant identity when subject-disjoint reasoning matters. | Distinct from record identity and sample identity. |
| `record_id` | Stable logical record identity. | Do not use it for one window or one runtime item derived from that record. |
| `sample_id` | Identity for a sample, window, or other per-item unit when such an identifier is needed. | Distinct from `record_id`, which names the pre-window record. |
| `group` | Descriptive grouping metadata for grouping, filtering, reporting, or split-related context. | Not a synonym for `split`, and not a grouping algorithm by itself. |
| `split` | Descriptive partition or usage metadata. | Not a loop mode and not a promise about which code path must run. |

## Short Usage Rules

- Prefer `DataSource` over `Dataset` in public API names.
- Prefer `field` over modality-specific nouns when describing generic payload
  contracts.
- Prefer `metadata` for descriptive context and `field` for structured payloads.
- Keep `DataKey`, `FieldRole`, `FieldLocator`, `DataType`, and `SchemaName`
  separate in both naming and implementation.
- Use `record` for the stable pre-window logical item, `sample` for the runtime
  item, and `batch` for the collated runtime item.
- Treat lazy refs and runtime objects as different layers, even when they
  describe the same underlying data.
- Keep workflow-runtime language out of core `rphys` contracts unless the
  roadmap explicitly adds it.

## See Also

- `docs/roadmap.md`
- `tests/contracts/test_data_vocabulary_contract.py`
- `src/rphys/data/keys.py`
- `src/rphys/data/locators.py`
- `src/rphys/data/metadata.py`
- `src/rphys/data/schemas.py`
- `src/rphys/data/splits.py`
- `src/rphys/data/types.py`
