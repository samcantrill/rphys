# rphys Implementation Roadmap

Version: 1.4 roadmap draft  
Source architecture: field-centric `rphys` library plan  
Purpose: define a cohesive implementation plan for the core library contracts, data flow, IO boundaries, pipeline abstractions, and testing structure.

---

## 1. Roadmap summary

`rphys` should be implemented as a domain-specific remote physiological
measurement library. It should provide reusable objects for data references,
lazy IO, runtime samples and batches, sample and batch operations, pipelines,
models, losses, objectives, metrics, learning/training contracts, prediction,
evaluation, analysis contracts, and tests. It should not own experiment
orchestration, configuration systems, or workflow engines.

```text
rphys owns reusable library contracts and domain primitives.
Downstream projects own experiment configuration, workflow orchestration, and
project-specific experiment plans.
rphys public objects should be stage-friendly: serializable, typed,
provenance-aware, and easy for loom or downstream projects to wrap as
artifact-level stages.
rphys does not own generic Artifact, ArtifactRef, ArtifactContract, Stage,
StageContext, artifact stores, stage graphs, scheduling, or stage execution.
```

This roadmap translates the architecture into a staged delivery plan. The
sequencing is designed to protect the core public interfaces before
implementation spreads across datasources, IO codecs, pipelines, models,
analysis, or project-specific workflows.

The critical path is:

```text
1. Core public contracts and package skeleton
2. Field model and mutable Sample/Batch runtime interface
3. Field-aware lazy IO: DataSourceRef -> RecordRef -> FieldRef -> FieldView -> IndexItem
4. Codec registry and lazy Sample field construction
5. DataSource adapters, filters, splits, and index builders
6. Operation, OperationPipeline, SampleOp, Transform, and SampleOpPipeline base classes
7. Codec-driven save/export ops and derived datasource generation
8. Generic datasource indexes, chained indexes, Torch adapters, and DDP-safe datasource cache
9. Method/model, loss/objective/metric, learner/trainer base abstractions
10. Prediction/results-as-datasource evaluation and analysis flows
11. Synthetic fixtures, contract tests, integration tests, and smoke tests
```

The most important implementation rule is that the early phases should produce stable, well-documented public contracts before building many concrete datasources, transforms, models, or metrics.

## 2. Implementation principles

The implementation should follow these rules throughout all phases.

```text
Small public API, large implementation surface.
  Keep public contracts stable and documented.
  Let modality-specific implementations live behind those contracts.
  Treat the public API checklist as an acceptance checklist, not permission to
  expose every helper as stable immediately. A class or function is stable only
  when it is documented, tested, and intended as an extension contract.

Field-centric design.
  Every loadable, transformable, collatable, predictable, or evaluable item is a field.
  Video is a common field, not a privileged field.
  Sample and Batch are generic runtime pipeline components, not only data-loader
  inputs. They can carry inputs, targets, model outputs, prediction fields,
  intermediate representations, differentiable loss fields, objective terms,
  metric observations, diagnostics, and provenance when declared by contracts.
  Sample is the per-item lazy container; Batch is the collated container used by
  methods, losses, objectives, metrics, learners, trainers, prediction,
  evaluation, and analysis steps.

Field versus metadata rule.
  If a value can be loaded, sliced, transformed, validated, collated, saved,
  used by a model, used by a loss/objective, used by a metric, or analyzed as a
  structured payload, make it a field. If it only describes the datasource,
  record, sample, split, group, run, or global context, keep it as metadata.
  Ambiguous values such as skin tone, camera intrinsics, quality scores, and
  heart-rate labels become fields when consumed by methods, losses, objectives,
  metrics, transforms, or exports; otherwise they may remain metadata.

Lazy IO is separate from runtime data processing.
  FieldView and FieldIndex describe what to load.
  SampleTransform and SampleAugmentation describe what to do after loading.

Export is a sample operation, not datasource discovery logic.
  DataSource code discovers and indexes logical records and fields.
  Save/export ops write fields through codecs, create new FieldRefs, and can
  produce a new DataSourceRef that is loadable by the same machinery.

Pipelines are composable library objects.
  Data preprocessing, derived-field extraction, format conversion, prediction
  export, metric computation, analysis, and visualization should all be expressible
  as datasource/index iteration plus an OperationPipeline where possible.
  Operation is the generic context-aware callable shape. Do not introduce a
  second universal BatchOperator base; batch-level composition can use
  Operation[Batch, Batch] or a future narrow BatchTransform if implementation
  pressure justifies it.

Avoid duplicate abstractions.
  Prefer one small base protocol plus semantic specializations over parallel
  classes that do the same thing. Add a new class name only when it carries a
  real lifecycle, scientific, mutability, side-effect, or optimizer semantics
  difference. Keep adapters thin and specific instead of creating broad generic
  adapters before there is repeated need.

Mutable runtime path.
  Sample and Batch should be mutable by default to reduce hot-path allocation.
  Branching pipelines must copy explicitly.

Fail loudly by default.
  Missing fields, unsupported slices, ambiguous codecs, invalid schemas, and unclear collation should raise explicit errors.

Runtime outputs are field containers.
  Predictions, losses, objective terms, metric observations, analysis inputs,
  and diagnostics should be represented as declared Sample/Batch fields or
  typed result sidecars, not rigid waveform-specific prediction objects.

Losses are error terms; objectives are optimizer targets.
  A Loss computes one or more differentiable error/penalty terms over declared
  Sample/Batch fields and may return a mutated or derived runtime container plus
  structured differentiable term data.
  An Objective combines losses with other optimizer-relevant terms such as
  regularization, constraints, weights, schedules, parameter penalties, and
  auxiliary optimization values. Trainer code backpropagates an objective scalar,
  not an arbitrary metric.

Trainer is learning-style agnostic and optional.
  Learning code owns supervised, self-supervised, contrastive, masked-modeling,
  or other step semantics.
  Training code owns epoch, device, gradient mode, optimizer, scheduler,
  checkpoint, distributed, and callback orchestration.

Stage-friendly, not stage-owning.
  rphys domain refs, plans, builders, results, reports, and indexes should be
  easy for loom or downstream projects to wrap as artifacts/stages.
  Generic artifact/stage orchestration belongs outside rphys.
  Function-style entrypoints such as a future `run_train(...)` should be
  designed so loom can call them with explicit arguments and receive typed
  results, but the exact argument/config schema should remain flexible until the
  orchestration package needs it.
  Thin wrappers intended for downstream stage runtimes should consume typed
  refs/plans/results, delegate to existing rphys APIs, return all declared
  outputs, be safe to rerun, and never depend on in-memory outputs from previous
  workflow steps.

Traceability is part of the contract.
  Components that transform data or training state should expose stable names,
  parameter summaries or fingerprints, input/output field declarations, source
  lineage, run context, and warnings through existing metadata/provenance/result
  objects. Avoid inventing separate provenance classes per component until a
  shared record shape is justified.

No built-in configuration system.
  Do not include configuration frameworks, workflow engines, or project
  orchestration machinery in the core package. Downstream projects can configure
  public library objects however they want.
```

## 3. Roadmap structure

The roadmap is organized into milestones. Each milestone has:

```text
Goal
  The conceptual outcome.

Primary packages
  Where implementation should live.

Key interfaces
  Public contracts or classes to implement.

Deliverables
  Concrete source files, documentation, and tests.

Definition of done
  Conditions that must be true before depending on the milestone.

Dependencies
  Earlier milestones that must be completed first.
```

The phases are not intended to be date estimates. They are implementation dependency layers. Some implementation work can happen in parallel after the foundational contracts exist, but core contracts should be stabilized in order.

---

## 4. Milestone 0: Repository skeleton, governance, and API stability policy

### Goal

Create the package skeleton and establish which modules are stable public API versus implementation detail.

This should happen before implementing concrete datasources or training code. Otherwise, users and experiment code will start depending on unstable internals.

### Primary packages

```text
src/rphys/
  __init__.py
  errors.py
  data/
  io/
  datasources/
  ops/
  methods/
  models/
  nn/
  losses/
  objectives/
  metrics/
  learning/
  training/
  prediction/
  evaluation/
  analysis/
```

### Key decisions to encode

```text
Public contracts live in package-level or core modules.
Concrete implementations can live in deeper role/modality-specific modules.
Downstream projects own experiment configuration and orchestration.
Registries are only required where symbolic names are useful, such as codec keys
or optional datasource adapter aliases.
Core imports must stay lightweight and not import optional scientific or ML stacks.
Stable public API means documented extension contracts. Deep implementation
modules, concrete examples, adapters, and helpers are internal unless
`docs/public_api.md`, package exports, and contract tests explicitly mark them
stable.
Define optional dependency extras in `pyproject.toml` for dependency-heavy
surfaces such as video IO, signal processing, torch/training, analysis, and dev
tooling. Missing optional dependencies should fail through typed dependency
errors at the package boundary that needs them, not during `import rphys`.
Top-level modules are domain ownership boundaries:
  data: in-memory field, sample, batch, and data-object contracts
  io: codecs, storage references, load/save contexts, and Sample construction
  datasources: datasource discovery, plans/builders/results, indexes, Torch
    adapters, and datasource-owned caches
  ops: Operation contracts, pipelines, transforms, augmentations, checks, and
    functional wrappers
  methods/models/nn: prediction contracts and computational model boundaries
  losses: differentiable error and penalty term contracts and implementations
  objectives: optimizer-facing aggregation of losses plus regularization,
    constraints, schedules, parameter penalties, and auxiliary optimization terms
  metrics: detached reporting/evaluation measurements and aggregations
  learning: Learner, StepOutput, and learning-style step semantics
  training: loop execution, device movement, optimizer/scheduler specs,
    checkpointing, distributed context, callbacks, profiling, and optional
    stage-friendly function entrypoints such as `run_train`
  prediction: thin prediction runners, prediction-field collection, and
    prediction export helpers over Method/Learner/Trainer outputs
  evaluation: metric protocols, evaluation runners, result datasource flows,
    reports, and comparison protocols over shared contracts
  analysis: post-evaluation tables, diagnostics, summaries, and visualization
    result contracts without hidden plotting side effects
Infrastructure modules such as cache should start inside the owning domain
module. Promote them to top-level only if multiple domains need the same stable
public abstraction.
Generic artifact/stage orchestration belongs outside rphys. rphys exposes domain
refs and results such as ResourceRef, FieldRef, DataSourceRef, DataSourceIndex,
IndexResult, ExportReport, TrainingResult, AnalysisResult, and Report. These are
the objects a downstream stage runtime may treat as artifacts.
ResourceRef, if implemented in rphys, is only a minimal URI/protocol reference
for data resources used by FieldRef and codecs. It is not a generic ArtifactRef,
run artifact handle, stage output handle, artifact-store object, or workflow
lifecycle primitive. If loom later provides a generic ResourceRef, rphys should
wrap, alias, or interoperate with it without changing FieldRef semantics.
Do not add recipes or a public rphys testing-helper package in the initial
roadmap. Tests and test support live in the repository-level `tests/` tree.
Do not add a generic `rphys.stages` package unless the only contents are thin,
explicit callable interfaces needed by loom/downstream orchestration. Any such
interface must wrap existing plans/builders/runners and must not define a stage
DAG, artifact store, scheduler, or workflow runtime inside rphys.
```

### Deliverables

```text
pyproject.toml
README.md
docs/architecture.md
docs/roadmap.md
docs/features/
docs/public_api.md
src/rphys/__init__.py
src/rphys/errors.py
src/rphys/data/__init__.py
src/rphys/io/__init__.py
src/rphys/datasources/__init__.py
src/rphys/ops/__init__.py
src/rphys/methods/__init__.py
src/rphys/models/__init__.py
src/rphys/nn/__init__.py
src/rphys/losses/__init__.py
src/rphys/objectives/__init__.py
src/rphys/metrics/__init__.py
src/rphys/learning/__init__.py
src/rphys/training/__init__.py
src/rphys/prediction/__init__.py
src/rphys/evaluation/__init__.py
src/rphys/analysis/__init__.py
tests/test_imports.py
```

### Definition of done

```text
The package imports successfully.
The public API policy is documented.
Top-level package layout matches the library architecture.
Heavy dependencies are optional and not imported by core modules.
A user can import rphys without importing torch, cv2, av, matplotlib, or scipy unless explicitly using those subpackages.
Optional dependency extras and import boundaries are documented in
`pyproject.toml` and `docs/public_api.md`.
No project-configuration, workflow-engine, project-template, or workflow-phase package
exists in the core library.
No generic Artifact, ArtifactRef, Stage, StageContext, stage DAG, artifact store,
or workflow runtime API exists in rphys.
```

### Dependencies

```text
None.
```

---

## 5. Milestone 1: Core errors, keys, locators, and schema primitives

### Goal

Implement the minimal domain vocabulary needed by every later layer.

This milestone should define reusable primitives for the core object and data
flow model. It should not encode datasource-specific, method-specific, or
experiment-specific naming beyond examples needed to clarify the contract.

### Primary packages

```text
rphys.errors
rphys.data.keys
rphys.data.locators
rphys.data.schemas
```

### Key interfaces

```text
DataKey
FieldRole
FieldLocator / field locator string grammar
DataType constants
SchemaName / schema string grammar
MetadataKey constants
SplitName / split string constants
RPhysError and specific subclasses
```

### DataKey requirements

`DataKey` should be string-like but validated enough to prevent common mistakes.
It identifies an intrinsic logical field. It is not a filesystem path, runtime
role, metric path, transform path, or external-configuration locator.

Recommended grammar:

```text
<namespace>.<semantic>[.<qualifier>...]
```

Components should be lowercase snake_case tokens. Invalid keys should reject
empty components, slashes, whitespace, leading dots, trailing dots, and unknown
reserved namespaces.

Reserved namespaces:

```text
video
signal
timestamps
face
body
camera
landmarks
mesh
graph
mask
embedding
label
quality
annotation
metadata
custom
```

Custom keys must use the custom namespace:

```text
custom.<project>.<semantic>[.<qualifier>...]
```

Examples:

```text
video.rgb
video.rgb.raw
signal.bvp.reference
signal.ecg
signal.ppg
signal.eda
timestamps.video.seconds
landmarks.face.mediapipe_468
mesh.face.flame
mask.face.skin
graph.face_mesh.node_rgb
graph.face_mesh.node_orientation
metadata.heart_rate
quality.face_visibility
custom.my_project.embedding
```

### FieldRole and FieldLocator requirements

`FieldRole` describes where a field sits in runtime data flow. It is separate
from `DataKey` so the same logical field can be used as an input, target,
prediction, metric input, or exported output without changing its identity.

Initial roles:

```text
inputs
targets
source
predictions
outputs
losses
metrics
metadata
```

`FieldLocator` is the stable string form for external configuration, transform
declarations, metrics, losses, logging, and error messages when a role-qualified
field or metadata attribute must be addressed.
The `losses` and `metrics` roles are reserved for explicitly declared diagnostic
or result fields. They may carry differentiable error terms, objective
components, detached metric observations, or monitoring values when a component
declares those writes. Typed result objects remain the stable optimizer and
aggregation contract, so training/evaluation code must not depend on ad hoc
field names such as `loss.total`.

Recommended grammar:

```text
<role>/<data-key>[#<metadata-key>]
```

Examples:

```text
inputs/video.rgb
targets/label.class
targets/signal.bvp.reference
source/metadata.record
predictions/label.logits
predictions/signal.bvp
predictions/signal.bvp#sampling_rate_hz
outputs/embedding.video
```

Do not use dot suffixes for metadata selection because `DataKey` itself uses
dots. Proposal-style keys such as `input.video` or `prediction.signal` should be
translated into role-qualified `FieldLocator`s such as `inputs/video.rgb` and
`predictions/signal.bvp`.

### Schema, metadata, and split constants

`SchemaName` describes loaded payload interpretation, layout, units, coordinate
meaning, and version. It is not a `DataKey` and not a `codec_key`.

Recommended grammar:

```text
<family>.<layout_or_semantic>.v<int>
```

Examples:

```text
video.rgb_thwc.v1
signal.samples_t.v1
timestamps.seconds_t.v1
landmarks.tvd.v1
graph.node_features_tvc.v1
metadata.attrs.v1
```

Initial `DataType` constants should cover broad payload families rather than
specific algorithms:

```text
video
signal
timestamps
landmarks
mask
mesh
graph
image
scalar
table
metadata
quality
annotation
```

Initial `MetadataKey` constants should cover fields that affect data flow,
scientific interpretation, leakage control, provenance, and reproducibility:

```text
datasource_id
datasource_name
record_id
source_id
subject_id
scenario
split
group
source_uri
start_index
stop_index
sample_index
sample_key
sampling_rate_hz
timestamps_unit
device_name
units
coordinate_frame
method_id
model_id
run_id
```

Initial split constants:

```text
train
valid
test
predict
```

These constants are metadata values for indexing, filtering, training, and
analysis. They are not tied to a datasource implementation and should not cause
sample loading or mutation by themselves.
Split is data partition or usage metadata, not loop mode. Validation can run on
`split="valid"`, prediction can run over any split, and downstream projects may
define additional split values without changing `LoopMode`.

### Error hierarchy

Implement explicit errors for loud failures:

```text
RPhysError
RPhysDataError
RPhysFieldError
RPhysDataSourceError
RPhysIOError
RPhysCodecError
RPhysSliceError
RPhysCollateError
RPhysTransformError
RPhysPipelineError
RPhysMethodError
RPhysLearningError
RPhysTrainingError
RPhysAnalysisError
RPhysNameError
RPhysMetadataError

MissingFieldError
FieldTypeError
FieldSchemaError
CodecResolutionError
SliceUnsupportedError
SliceOutOfBoundsError
CollatePolicyError
TransformContractError
InvalidDataKeyError
InvalidFieldLocatorError
InvalidSchemaNameError
InvalidMetadataKeyError
MissingMetadataError
```

Every `RPhysError` should accept a message plus optional structured context,
such as `key`, `role`, `locator`, `schema`, `metadata_key`, `expected`,
`actual`, `path`, and `cause`.

### Deliverables

```text
src/rphys/errors.py
src/rphys/data/keys.py
src/rphys/data/locators.py
src/rphys/data/namespaces.py
src/rphys/data/schemas.py
src/rphys/data/metadata.py
src/rphys/data/splits.py
tests/test_data_keys.py
tests/test_field_locators.py
tests/test_schema_names.py
tests/test_metadata_keys.py
tests/test_errors.py
docs/public_api.md section: Keys, schemas, and errors
```

### Definition of done

```text
Standard field keys are defined as constants.
Custom keys are allowed through the custom namespace.
Invalid keys fail with clear errors.
DataKey rejects role-prefixed paths and metadata selectors.
FieldLocator parses role, DataKey, and optional MetadataKey without importing heavy packages.
SchemaName validation keeps layout, unit, coordinate, and version meaning separate from DataKey.
Core metadata and split constants are documented.
Core errors are used in tests.
Core errors preserve structured context in tests.
No datasource, codec, transform, or model implementation defines its own duplicate error vocabulary.
```

### Dependencies

```text
Milestone 0.
```

---

## 6. Milestone 2: FieldSpec, FieldRef, FieldView, FieldIndex, and DataSourceRef structure

### Goal

Implement the reference model that represents datasource structure and lazy IO
without loading field payloads.

This milestone answers the datasource structure question explicitly:

```text
DataSourceRef defines a datasource or datasource view.
DataSourceRef returns or contains RecordRefs.
RecordRef represents an individual item, trial, session, or entry.
RecordRef contains FieldRefs.
FieldRef describes a complete logical field and how it can be loaded.
FieldView specializes FieldRef with an optional FieldIndex.
IndexItem contains FieldViews and is the unit consumed by SampleBuilder.
```

### Primary packages

```text
rphys.data.core
rphys.io.core
rphys.datasources.core
```

### Key interfaces

```text
ResourceRef
FieldSpec
MetadataSpec
FieldRef
FieldIndex
TemporalIndexSlice
FieldView
DataSourceRef
RecordRef
IndexItem
DataSourceSchema
```

### Object boundary rules

```text
ResourceRef identifies physical storage. It is serializable and never owns an open handle.
It should store URI/protocol/storage options rather than assuming local files so
future S3, HTTP, database, or object-store resources are not blocked.

DataSourceRef represents a datasource or datasource view without loaded payloads.

RecordRef represents a stable logical record before windowing. It owns record identity,
field presence, and leakage-sensitive metadata such as datasource_id, record_id, source_id,
subject_id, split, and group.

FieldRef is a self-contained lazy reference to one complete logical field on one record.
It owns the intrinsic DataKey and must not contain FieldRole or FieldLocator.
It does not own imposed index or slicing behavior.

FieldView is a lazy FieldRef specialization that adds imposed access behavior
such as a field-native FieldIndex. It should satisfy the FieldRef loading
interface, but its access is restricted by the view index/slice.

IndexItem is a lazy runtime request. It maps role-qualified FieldLocators to FieldViews.
The FieldLocator determines runtime role; the FieldRef.key remains the intrinsic DataKey.

Loaded payloads, FieldValue, Sample, Batch, transforms, augmentations, and model logic
are outside this milestone.
```

### FieldIndex and TemporalIndexSlice semantics

`FieldIndex` is the base class/protocol for imposed access behavior on a
`FieldRef`. Only one concrete FieldIndex should exist initially:

```text
FieldIndex
  Base access restriction or index request.
  Does not define a global temporal coordinate system by itself.
  Must be explicit when attached to a FieldView.

TemporalIndexSlice
  Inherits FieldIndex.
  Index-based.
  Half-open: [start, stop).
  Field-native temporal index space.
  start and stop are non-negative integers.
  stop must be greater than start.
  step is a positive integer and defaults to 1.
  No seconds-based slicing.
  No spatial slicing.
```

Initial implementations may reject `step != 1` with `SliceUnsupportedError`.
The same numeric slice on two fields does not imply temporal alignment.
Multi-field `IndexItem`s may use different field-native slices per field.
Any cross-field alignment assumption must be explicit metadata, not implicit shared start/stop.

Examples:

```text
video.rgb slice indexes frames.
signal.bvp slice indexes signal samples.
face.landmarks.mediapipe_468 slice indexes landmark rows/frames.
timestamps.video slice indexes timestamp entries.
```

A field view may have no imposed index:

```text
FieldView(field_ref=..., field_index=None)
```

`None` means load the complete logical field.

### DataSourceRef and RecordRef

Recommended shape:

```python
@dataclass(slots=True)
class DataSourceRef:
    datasource_id: str
    records: Mapping[str, RecordRef]
    schema: DataSourceSchema
    metadata: MutableMapping[str, Any]

@dataclass(slots=True)
class RecordRef:
    record_id: str
    fields: Mapping[DataKey, FieldRef]
    metadata: MutableMapping[str, Any]
```

`DataSourceRef` may later be backed by a manifest, remote listing, or lazy
record store rather than a large in-memory dictionary, but the public behavior
should be the same.

### ResourceRef and FieldSpec

Recommended shape:

```python
@dataclass(slots=True, frozen=True)
class ResourceRef:
    uri: str
    protocol: str | None = None
    storage_options: Mapping[str, Any] | None = None
    metadata: Mapping[MetadataKey, Any] | None = None

@dataclass(slots=True)
class FieldSpec:
    key: DataKey
    data_type: str
    schema: SchemaName | None
    shape: tuple[int | None, ...] | None
    dtype: str | None
    metadata: MutableMapping[MetadataKey, Any]
```

`FieldSpec` describes only minimal common loaded interpretation without holding
payload data. Do not force every field to declare temporal axes, lengths,
sampling rates, coordinate frames, or modality-specific assumptions. Those
belong in explicit modality-specific specs/classes when a component requires
them.

### FieldRef

Recommended shape:

```python
@dataclass(slots=True)
class FieldRef:
    key: DataKey
    data_type: str
    ref: ResourceRef | None
    resources: Mapping[str, ResourceRef] | None
    codec_key: str | None
    selector: Mapping[str, Any] | None
    schema: SchemaName | None
    spec: FieldSpec | None
    metadata: MutableMapping[MetadataKey, Any]
```

Rules:

```text
FieldRef is serializable.
FieldRef describes a complete logical field.
FieldRef does not hold open files or loaded tensors.
FieldRef may reference one ResourceRef or a named set of ResourceRefs when a
logical field is compound, such as video frames plus sidecar metadata.
selector selects part of a physical resource, such as a CSV column.
selector is not a DataKey or FieldLocator.
codec_key resolves the loader.
schema describes the loaded interpretation.
FieldRef does not encode runtime role.
FieldRef does not encode slicing.
FieldRef metadata keys should use MetadataKey where standardized.
```

### FieldView and IndexItem

Recommended shape:

```python
@dataclass(slots=True)
class FieldView(FieldRef):
    field_index: FieldIndex | None = None

@dataclass(slots=True, frozen=True)
class IndexItem:
    item_id: str
    datasource_id: str
    record_id: str
    views: Mapping[FieldLocator, FieldView]
    metadata: Mapping[MetadataKey, Any]
```

Rules:

```text
IndexItem contains no loaded data.
IndexItem view locators should not use metadata selectors.
IndexItem identity should preserve parent datasource and record identity.
```

### Deliverables

```text
src/rphys/data/core/fields.py
src/rphys/io/core/fields.py
src/rphys/datasources/core/refs.py
src/rphys/datasources/core/schemas.py
src/rphys/datasources/core/indexing.py
tests/test_resource_refs.py
tests/test_field_specs.py
tests/test_field_refs.py
tests/test_field_views.py
tests/test_index_items.py
tests/test_temporal_index_slice.py
tests/test_field_index.py
tests/test_datasource_refs.py
docs/public_api.md section: DataSourceRef, RecordRef, FieldRef, FieldView, IndexItem
```

### Definition of done

```text
DataSourceRef -> RecordRef -> FieldRef -> FieldView -> IndexItem flow is implemented and documented.
Each IndexItem is a pure lazy IO plan.
No IndexItem contains transform, augmentation, method, or training logic.
FieldIndex is the base access restriction contract.
TemporalIndexSlice validates start/stop/length/step.
Unsupported slice semantics are not implemented silently.
ResourceRef, FieldRef, FieldView, and IndexItem serialize without open handles or loaded arrays.
FieldSpec records minimal loaded interpretation without payload data or unnecessary temporal assumptions.
IndexItem uses FieldLocator for runtime role and never mutates FieldRef.key.
Record identity and parent record metadata survive window/index construction.
Different fields in one IndexItem can carry different field-native FieldIndexes.
No code assumes one sample-level start/stop applies to all fields unless explicit alignment metadata records that contract.
Compound logical fields can reference multiple resources and still load through one FieldRef/codec boundary.
ResourceRef does not assume local filesystem paths.
```

### Dependencies

```text
Milestone 1.
```

---

## 7. Milestone 3: Runtime SampleField, Sample, Batch, and CollatePolicy

### Goal

Implement the runtime container layer used after an `IndexItem` is converted
into lazy runtime field handles and before ops, models, metrics, writers, or
evaluation consume data.

This milestone defines loaded object semantics, role-qualified sample access,
mutation contracts, and collation boundaries. It does not implement
`FieldCodec` IO; tests should construct small synthetic field handles and loaded
payloads directly.

### Primary packages

```text
rphys.data.core
rphys.data.modalities
```

### Key interfaces

```text
FieldValue
SampleField
FieldLoadState
Sample
Batch
DataObjectBase
CollatePolicy
CollateContext
generic_collate
SampleContract
BundleSpec
```

### Object boundary rules

```text
FieldValue wraps one loaded payload plus its intrinsic DataKey, DataType, schema,
minimal FieldSpec-derived interpretation, metadata, and optional source
FieldView provenance.

SampleField is the runtime field handle stored inside a Sample. It may be
unloaded or loaded. It owns the FieldLocator, intrinsic FieldRef/FieldView
provenance, FieldSpec, metadata, load state, optional cache key, and a loader
callable supplied by the IO layer.

Sample stores SampleFields in a MutableMapping keyed by FieldLocator, not by
bare DataKey. The FieldLocator supplies runtime role; the SampleField and loaded
FieldValue preserve intrinsic field identity.

Sample is an arbitrary container component. It should provide stable interfaces
for field lookup, mutation, metadata, tensor traversal, and copy behavior without
assuming a fixed set of roles or modalities.

Sample and Batch are the two runtime field containers. Sample is the per-item
container and may hold lazy `SampleField`s. Batch is the collated container used
after batching by methods, losses, objectives, metrics, learners, trainers,
and evaluation steps. Do not make Batch the only root runtime abstraction; lazy IO and
per-record provenance remain Sample responsibilities.

Both Sample and Batch remain generic runtime pipeline components throughout the
library. They are allowed to carry declared model outputs, prediction fields,
loss/error-term fields, objective components, metric observations, diagnostics,
and analysis-ready intermediate results when that simplifies composition. The
constraint is declared field ownership and provenance, not a fixed list of
allowed runtime roles.

DataObjectBase is a loaded-payload protocol or base class, not an IO abstraction.
It supports tensor traversal, metadata access, device movement, pinning, and
optional custom collation, but dump/load/codec behavior belongs to later milestones.

Field metadata describes a loaded field, its schema, coordinate meaning,
sampling rate, units, layout, provenance, and collation behavior. Sample or
Batch metadata describes the runtime item, group, split, datasource, run, or
loop context. If metadata grows into a structured payload that must be loaded,
transformed, collated, saved, used by a Method/Loss/Objective/Metric, or
analyzed as data, model it as a field rather than hiding it in metadata.

The IO layer is the planned bridge from IndexItem/FieldView to SampleField.
Sample itself should not know how to scan datasources or resolve codecs. It only
delegates to the SampleField when the user asks for payload data.
```

### Sample rules

```text
Sample is mutable by default.
Sample accessors accept FieldLocator or a string parsed as FieldLocator.
Sample.get(locator) returns the loaded payload value and may incur IO.
Sample.peek(locator) returns the SampleField handle without forcing IO.
Sample.field(locator) returns the SampleField handle.
Sample.require(locator, expected_type) returns the payload or raises FieldTypeError.
Sample.set_field(locator, field_or_payload, ...) mutates the sample and returns it.
Sample.copy(deep=False) copies the mapping and SampleField handles only.
Sample.copy(deep=True) also deep-copies payloads and mutable metadata where supported.
Branching pipelines must explicitly copy.
Transforms must declare read/write/delete locators before mutating fields.
Transforms must not mutate undeclared fields.
```

Recommended API:

```python
sample.has("inputs/video.rgb")
sample.peek("inputs/video.rgb")
sample.field("inputs/video.rgb")
sample.get("inputs/video.rgb")
sample.require("targets/signal.bvp.reference", SignalData)
sample.set_field("predictions/signal.bvp", signal_data, data_type="signal")
sample.delete_field("inputs/face.mask.skin")
sample.rename_field("inputs/video.rgb.raw", "inputs/video.rgb")
sample.copy(deep=False)
sample.copy(deep=True)
sample.role("inputs")
sample.map_tensors_(fn, locators=None)
```

### Batch rules

```text
Batch uses the same field access API as Sample and is keyed by FieldLocator.
Batch fields contain batched DataObject payloads where a policy permits batching.
Batch metadata is collated deterministically.
Batch records batch_size plus per-item identity metadata such as item_id, datasource_id,
record_id, source_id, subject_id, split, and group when present.
Batch.role(role) returns a role-filtered view without changing stored locators.
Batch.to(...), Batch.pin_memory(...), and tensor mapping operate by field predicate
or all tensor-bearing fields, not hard-coded inputs/targets.
Downstream code should consume FieldLocator-addressed fields rather than unpacking
a fixed inputs/targets/source tuple.
Batch.set_field(locator, field_or_payload, *, data_type=None, schema=None,
metadata=None, provenance=None) mutates and returns the Batch while preserving
the same FieldValue, metadata, provenance, and role-separation rules as Sample.
Runtime role is supplied by FieldLocator and should not be duplicated as an
independent mutable role inside the stored field.
```

Recommended Batch API:

```python
batch.has("inputs/video.rgb")
batch.get("inputs/video.rgb")
batch.require("targets/signal.bvp.reference", SignalData)
batch.set_field(
    "predictions/signal.bvp",
    signal_batch,
    data_type="signal",
    schema="signal.samples_bt.v1",
)
batch.role("predictions")
batch.map_tensors_(fn, locators=None)
```

### Collate policy

Keep collation deliberately small at first. The exact list can grow later, but
the existence and behavior of field-level `CollatePolicy` should be implemented
now.

Policy resolution order:

```text
1. Explicit policy for the FieldLocator or matching DataKey/DataType/schema.
2. DataObjectBase custom collation hook.
3. Strict default failure.
```

`CollateContext` should include locator, role, data key, data type, schema,
field spec, sample count, item identities, batch axis, device/pin options, and
metadata policy.

Collation must distinguish payload collation from metadata collation. Metadata
may be stacked, listed, copied from an identical value, converted to
`valid_lengths` or `valid_mask`, dropped by explicit policy, or fail if
ambiguous. Silent metadata truncation, implicit timestamp alignment, and
implicit sampling-rate agreement are not allowed.

Minimal policies:

```text
STACK
  Require equal shape and stack on a batch dimension.

LIST
  Keep values as a list.

CUSTOM
  Delegate to data object or registered callable.
```

Default should be strict:

```text
Shape mismatch fails unless a policy explicitly permits padding or listing.
Missing fields fail unless a caller explicitly pre-filters, fills, or lists them.
Implicit truncation should not occur.
```

### Initial modality objects

Implement only thin modality objects needed to exercise the generic contracts.
They should document payload access, dtype/device expectations, metadata keys,
tensor traversal, and collation behavior, but should not encode datasource-, model-,
or algorithm-specific behavior. Do not force every field into these modality
classes.

```text
VideoData
SignalData
TimestampData
LandmarkData
MaskData
ArrayData
LabelData
```

These should all inherit from `DataObjectBase` or satisfy the same protocol.
Reserve mesh, ROI, event, and metadata data objects in the design vocabulary,
but do not implement them until concrete package components need them.

Initial public shape conventions should be documented even if implementations
remain thin:

```text
VideoData
  single video: [T, C, H, W]
  batched video: [B, T, C, H, W]

SignalData
  single signal: [T] or [C, T]
  batched signal: [B, T] or [B, C, T]

TimestampData
  single timestamp sequence: [T]
  batched timestamp sequence: [B, T] or list when temporal lengths differ

LandmarkData
  single landmark sequence: [T, N, 2] or [T, N, 3]
  batched landmark sequence: [B, T, N, 2] or [B, T, N, 3]

MaskData
  single mask sequence: [T, H, W] or [T, C, H, W]
  batched mask sequence: [B, T, H, W] or [B, T, C, H, W]
```

Shape conventions must also state layout, temporal axis, units, coordinate
frame, timestamps/fps/sample-rate behavior, dtype/device expectations, and
validity mask semantics where relevant.

### Deliverables

```text
src/rphys/data/core/field_values.py
src/rphys/data/core/sample_fields.py
src/rphys/data/core/sample.py
src/rphys/data/core/batch.py
src/rphys/data/core/collate.py
src/rphys/data/core/contracts.py
src/rphys/data/modalities/video/data.py
src/rphys/data/modalities/signal/data.py
src/rphys/data/modalities/timestamps/data.py
src/rphys/data/modalities/landmarks/data.py
src/rphys/data/modalities/masks/data.py
src/rphys/data/modalities/arrays/data.py
src/rphys/data/modalities/labels/data.py
tests/test_sample.py
tests/test_batch.py
tests/test_collate.py
tests/test_data_modalities.py
docs/public_api.md section: Sample, Batch, DataObjectBase, CollatePolicy
docs/extension_guides/new_modality.md
docs/features/samples_batches_and_collation.md section: modality shape conventions
```

### Definition of done

```text
A Sample can contain arbitrary typed SampleFields.
A Batch preserves the same access API.
Collate handles fixed-shape stack, list collation, and custom collation.
Missing fields and ambiguous collation fail loudly by default.
DataObjectBase supports tensor traversal and device movement.
Initial modality shape conventions are documented with layout, temporal axis,
units, coordinate frame, timestamp/fps/sample-rate, dtype/device, and validity
mask expectations where relevant.
Sample keys are FieldLocators and never mutate SampleField.data_key.
FieldValue preserves intrinsic DataKey and loaded interpretation separately from role.
SampleField defers IO until payload access and exposes loaded/unloaded/error state.
SampleContract declares required/optional locators, expected data object types,
schema/data_type constraints, collate policy, and allowed mutations.
BundleSpec groups role-qualified locators for consumers without imposing storage layout.
Copy, rename, delete, and set_field behavior are tested for shallow and deep copies.
Collate tests cover stack, list, custom, metadata preservation, missing fields,
role preservation, and item identity preservation.
Device movement and pinning traverse payload tensors and tensor metadata without
hard-coded role names.
No Milestone 3 code directly opens ResourceRef, FieldRef, or FieldView resources.
```

### Dependencies

```text
Milestone 2.
```

---

## 8. Milestone 4: FieldCodec registry and lazy Sample construction

### Goal

Implement the storage-adapter boundary that turns an `IndexItem` of
`FieldView`s into a mutable `Sample` containing lazy `SampleField` handles.

This is the first layer allowed to incur field payload IO, but it should still
keep IO as lazy as practical. Lightweight metadata/header inspection may happen
through explicit non-loading codec methods.

### Primary packages

```text
rphys.io.core
rphys.io.codecs
rphys.data.core
```

### Key interfaces

```text
FieldCodec
CodecRegistry
CodecCapabilities
CodecLoadResult
CodecSaveResult
SampleFieldFactory
SampleBuilder
SampleBuildContext
LoadContext
SaveContext
IOContext
MetadataSavePolicy
```

### Codec responsibilities

A codec loads a `FieldView`, not a path and not a role-qualified sample field.

```python
class CodecLoadResult:
    value: Any
    spec: FieldSpec | None = None
    metadata: Mapping[MetadataKey | str, Any] = {}

class FieldCodec(Protocol):
    codec_key: str
    capabilities: CodecCapabilities

    def probe(self, field_ref: FieldRef, context: LoadContext) -> FieldSpec:
        ...

    def load(self, field_view: FieldView, context: LoadContext) -> CodecLoadResult:
        ...

    def save(self, value: FieldValue | Any, target: FieldRef, context: SaveContext) -> CodecSaveResult:
        ...

    def supports(self, field_ref: FieldRef, context: LoadContext) -> bool:
        ...
```

`save` is part of the codec contract, but a codec may advertise unsupported
save capability and raise a typed error when asked to save. This keeps reading
and writing behavior discoverable through one codec registry without requiring
every codec to support every direction.

Rules:

```text
CodecRegistry resolves codecs by explicit codec_key when present, otherwise by declared capabilities.
Duplicate codec keys fail at registration time.
Missing optional codec dependencies fail with a codec-specific dependency error.
probe returns a normalized FieldSpec and must not load the full payload.
load receives FieldView and must respect FieldView.field_index.
load may read from one ResourceRef or a named set of ResourceRefs for compound
logical fields, such as video plus sidecar metadata.
If a slice is requested and unsupported, raise SliceUnsupportedError.
If a slice is out of bounds, raise SliceOutOfBoundsError.
If the registry cannot resolve a field, raise CodecResolutionError.
Do not silently fall back to full-resource loading unless explicitly configured.
Do not convert time to index inside FieldView; slices are already index-based.
Do not use FieldLocator, split, transform, augmentation, or model concerns inside a codec.
save writes one logical field value to one target FieldRef or target resource
description and returns CodecSaveResult with written resources, resulting spec,
codec metadata, and provenance.
```

### SampleBuilder

Recommended behavior:

```text
Input: IndexItem plus optional requested locators.
For each requested FieldLocator -> FieldView entry, resolve a codec from the FieldView.
Create a SampleField that knows how to load itself through the resolved codec.
Do not load the payload unless eager=True is explicitly requested.
Merge FieldRef metadata and codec probe/load metadata using documented precedence.
Store the SampleField under the original FieldLocator.
Return mutable Sample.
```

Recommended API:

```python
sample = sample_builder.build(index_item, locators=None, context=None, lazy=True)
spec = sample_builder.probe(index_item, locators=None, context=None)
field = sample_builder.build_field(index_item, "inputs/video.rgb", context=None, lazy=True)
```

File organization should keep IO core cohesive:

```text
context.py
  LoadContext, SaveContext, IOContext, and related context helpers.

sample.py
  SampleBuilder, SampleBuildContext, SampleFieldFactory, and construction helpers.

codecs.py / registry.py
  FieldCodec, CodecLoadResult, CodecSaveResult, CodecRegistry, and capabilities.
```

`SampleBuilder` is deliberately thin. It may keep per-build resource handles or
memoized probes in `SampleBuildContext`, and it may attach a cache policy to
created SampleFields. It must not own datasource discovery, indexing, splitting,
transforms, augmentations, dtype/device conversion, or model preparation.

`locators=None` means include every field in the `IndexItem`. Passing a locator
subset allows pipelines to probe or build only the components they need.
SampleFields should defer codec `load` until payload access.

### Metadata persistence

Metadata has two distinct persistence paths:

```text
Manifest metadata
  Small serializable metadata attached to DataSourceRef, RecordRef, FieldRef,
  IndexItem, SampleField, or export results. DataSourceManifestWriter persists
  this metadata according to a MetadataSavePolicy.

Metadata fields
  Structured, large, versioned, or analysis-ready metadata that should be loaded,
  sliced, transformed, cached, or exported like data. These should be normal
  fields such as metadata.record, quality.face_visibility, timestamps.video, or
  custom.project.sidecar and should be saved through a FieldCodec.
```

Metadata saving is triggered by `ExportSpec` / `SaveOp`, not implicitly by a
codec. The export spec should declare whether metadata is saved to the manifest,
as normal fields, both, or not at all. This avoids hidden leakage of runtime
metadata while still allowing reproducible derived datasources.

### Initial codecs

Implement only dependency-light codecs needed to test the abstraction:

```text
synthetic/in-memory codec for unit tests
one local array codec with temporal slice support
one metadata/json codec
optional dependency-free sequence/video-tensor test codec
```

Concrete domain formats, heavy video containers, and project-specific storage
layouts can come later.

### Deliverables

```text
src/rphys/io/core/codecs.py
src/rphys/io/core/registry.py
src/rphys/io/core/context.py
src/rphys/io/core/sample.py
src/rphys/io/codecs/testing.py
tests/test_codec_registry.py
tests/test_sample_builder.py
tests/test_lazy_slice_loading.py
tests/test_sample_field_loading.py
tests/test_sample_builder_subset.py
tests/test_codec_compound_resources.py
tests/test_codec_metadata_provenance.py
tests/test_codec_save.py
tests/test_metadata_save_policy.py
```

### Definition of done

```text
An IndexItem can be built into a Sample through FieldViews and codecs.
SampleBuilder can build all fields, a requested subset, or a single field.
SampleBuilder can probe specs without loading full payloads.
Sample keys come from FieldLocator, while SampleField preserves intrinsic FieldRef.key.
SampleField provenance points back to the loaded FieldView.
SampleField does not load payload data until accessed.
TemporalIndexSlice FieldIndex is respected for dependency-light array/sequence test fields.
Unsupported slice requests fail loudly.
Codec probe/load behavior is tested without requiring full payload loading during probe.
Compound fields with multiple resources are loaded through one logical FieldRef.
At least one codec supports saving and returns CodecSaveResult.
Metadata save policy distinguishes manifest metadata from metadata fields.
Codec resolution is deterministic and errors are typed.
SampleBuilder does not scan datasources, choose splits, apply ops, move devices,
cache without explicit CachePolicy, or perform model-specific formatting.
```

### Dependencies

```text
Milestones 2 and 3.
```

---

## 9. Milestone 5: DataSource adapters, filters, splits, and index builders

### Goal

Implement datasource discovery, validation, view construction, split assignment,
and index construction around logical fields.

Data flow:

```text
DataSourceSpec -> DataSourceAdapter.scan -> DataSourceRef/RecordRef/FieldRef
-> DataSourceViewPlan -> DataSourceViewBuilder -> DataSourceView
-> SplitPlan -> SplitBuilder -> Split
-> IndexPlan -> IndexBuilder -> DataSourceIndex
-> IndexItem -> SampleBuilder
```

DataSource code should discover, validate, filter, split, group, and index lazy
FieldRefs. It should not format data, perform runtime transforms, apply
training-time augmentation, or load payloads except through documented
validation/probe hooks.

### Primary packages

```text
rphys.datasources.core
rphys.datasources.adapters
rphys.datasources.filters
rphys.datasources.splits
rphys.datasources.validation
```

### Key interfaces

```text
DataSourceSpec
DataSourceAdapter
DataSourceSchema
DataSourceValidationReport
DataSourceViewPlan
DataSourceView
DataSourceViewBuilder
DataSourceViewResult
Filter
FilterPlan
FilterChain
FilterResult
GroupPlan
GroupBuilder
GroupResult
SplitPlan
Split
SplitBuilder
SplitResult
IndexPlan
IndexBuilder
WindowIndexBuilder
IndexResult
IndexBuildReport
DataSourceIndex
DataSourceIndexManifest
DataSourceIndexCodec
CompositeDataSourceIndex
```

### Plan, builder, result pattern

Datasource construction should use a consistent pattern:

```text
Plan
  Serializable request with parameters, selectors, policies, seed material,
  validation requirements, and provenance inputs.

Builder
  Stateless or lightly stateful executor that consumes a Plan and source object,
  performs validation, and returns a Result. Builders may use adapters/codecs for
  probes but should not hide payload loading.

Result
  Typed output plus report, warnings, rejected items, provenance, and stable
  fingerprint. Results are what later stages consume, not unstructured tuples.
```

Plans, builders, and results should be directly wrap-friendly by loom or
downstream stages: plans are serializable inputs, builders are plain Python
executors, and results carry typed outputs, provenance, warnings, reports, and
fingerprints. rphys does not provide `BuildIndexStage` or a generic artifact
runtime; loom/downstream code can wrap `IndexBuilder` and related builders.

Core examples:

```text
DataSourceViewPlan -> DataSourceViewBuilder -> DataSourceViewResult
GroupPlan -> GroupBuilder -> GroupResult
SplitPlan -> SplitBuilder -> SplitResult
IndexPlan -> IndexBuilder -> IndexResult
```

### DataSourceAdapter

Recommended protocol:

```python
class DataSourceAdapter(Protocol):
    datasource_name: str

    def schema(self) -> DataSourceSchema:
        ...

    def scan(self, source: DataSourceSpec) -> DataSourceRef:
        ...
```

`DataSourceSpec` owns discovery inputs only: roots, URI/path rules, glob/regex
patterns, include/exclude predicates, and optional source metadata. It should
not know rPPG field names, runtime roles, transforms, or model requirements.
It should support URI-like sources and storage options without assuming local
files.

`DataSourceAdapter.scan` converts discovered source items into `RecordRef`s and
`FieldRef`s. It may validate presence, shape metadata, sampling metadata, and
field compatibility, but it should report exclusions in
`DataSourceValidationReport` rather than silently dropping records.

The adapter should emit `RecordRef`s with arbitrary logical `FieldRef`s:

```text
video.rgb
signal.bvp
timestamps.video
face.landmarks.mediapipe_468
face.mesh.flame
quality.face_visibility
custom.my_project.some_field
```

### Filters

Keep filters minimal at first. A `Filter` is a composable predicate over a
declared scope and returns a typed `FilterResult`. It should not be split into a
large class taxonomy until the use cases force it.

Ref/index filtering belongs here when it can be decided from datasource
metadata, field specs, cheap probes, or index candidates before loading samples.
Filtering creates `DataSourceView`s or candidate `IndexItem` lists; it should
not mutate `DataSourceRef`, `RecordRef`, `FieldRef`, or `IndexItem` objects.

Sample-level inclusion/exclusion based on loaded payloads can be represented
later as `SampleOp`s that mark metadata or drop/route samples in a pipeline.
Keep the boundary explicit: datasource filters do not load payload data unless
declared as probe/validation filters.

Filter contract:

```text
Filter
  scope: record, field, index_item, or datasource_view
  requires: metadata keys, field keys, specs, or cheap probe declarations
  io_policy: no_io, probe_only, or explicit_validation_io
  __call__(item, context) -> FilterResult

FilterChain
  Composes filters with and/or/not semantics while preserving rejection reasons.

FilterResult
  accepted/skipped/rejected plus reason code, message, and optional structured
  metadata.
```

Example filter names, not required initial classes:

```text
DataSourceIn
SubjectIn
SubjectNotIn
HasField
HasAllFields
MinDuration
SplitEquals
QualityAtLeast
HasPrecomputedLandmarks
WindowHasSignalCoverage
WindowHasFaceCoverage
```

Filters must declare whether they are pure metadata filters or IO/probe
filters. IO/probe filters may use codec probe metadata or cheap field
attributes, but full payload loading remains `SampleBuilder`'s boundary unless
a validation hook explicitly documents the exception.

### Groups

Groups are derived metadata used to reason about records and samples across
datasources. They are useful for leakage-safe splits, stratified sampling,
per-stratum monitoring, and training analysis.

Examples:

```text
subject group
session/source group
dataset/datasource group
skin-tone or lighting group, when available and ethically/legally appropriate
quality-bin group
record-family group
```

`GroupPlan` declares which metadata keys or derived rules create groups.
`GroupBuilder` computes group assignments from `DataSourceRef`, `DataSourceView`,
or `DataSourceIndex` metadata. `GroupResult` records assignments, missing group
values, group counts, warnings, provenance, and a stable fingerprint.

Group assignments should be copied into `IndexItem` metadata and later
`SampleRuntimeContext` metadata so training and evaluation can compute losses,
metrics, sampling rates, and reports by group. This enables analysis such as
"loss by subject group over epochs" or "metric degradation by quality bin"
without changing the loaded field payloads.

### Splits

```text
SplitPlan is a serializable request describing split policy, grouping keys,
seed material, requested fractions or labels, and leakage constraints.

SplitBuilder returns a SplitResult containing a Split sidecar mapping stable record ids or
group ids to split labels. It should not attach mutable split/runtime fields to
RecordRefs or IndexItems.

SplitBuilder should consume GroupResult when group-disjoint behavior is required
rather than recomputing grouping ad hoc. Subject-disjoint and group-disjoint
split builders must assign whole groups before window indexing unless explicitly
documented otherwise.

SplitResult should record seed, policy, input counts, output counts,
unassigned records, duplicate assignments, and leakage checks.
```

### IndexBuilder

The index builder should create a `DataSourceIndex` containing or referencing
`IndexItem`s with `FieldView`s.

Rules:

```text
IndexItem is a lazy IO request.
IndexItem does not contain transform or augmentation logic.
Self-supervised wide-window loading should be represented as a wider TemporalIndexSlice FieldIndex.
Subwindow/view creation happens later inside SampleOpPipeline.
IndexPlan should define required fields, output FieldLocators, anchor field,
window length/stride/units, temporal-slice coordinate convention, alignment policy
across fields, and short-input/drop behavior.
WindowIndexBuilder should create FieldViews with field-native FieldIndexes.
It should preserve datasource id, record id, group keys, split label, window id,
start/stop indexes, and build provenance in IndexItem identity or metadata.
IndexResult should contain a DataSourceIndex plus IndexBuildReport. The report
should count candidates, accepted items, rejected items, and
rejection reasons.
```

`DataSourceIndex` is the generic runtime/index protocol. It may be in-memory,
manifest-backed, database-backed, remote, concatenated, or lazily paged, but it
must expose common item access:

```text
__len__()
get_item(position) -> IndexItem
iter_items()
fingerprint()
metadata
```

### Index serialization

Do not pickle the index as the default durable format. Pickle is acceptable only
for temporary local caches because it couples durability to Python code layout.

Durable indexes should be serialized through a `DataSourceIndexCodec`:

```text
DataSourceIndexCodec
  save(index, target, context) -> DataSourceIndexManifest
  load(manifest_or_resource, context) -> DataSourceIndex
  supports_version(schema_version) -> bool
```

The default initial codec should be a JSON/JSONL manifest codec with explicit
schema version, item records, child-index records, source maps, provenance,
fingerprints, and ResourceRef URIs. This lets an index be reloaded even if the
internal Python classes change, as long as the manifest schema remains
supported.

A Torch-compatible adapter should consume `DataSourceIndex`, not a specific
manifest format.

### Chained and composite indexes

Chaining datasources should happen at the index layer. Multiple datasources can
be scanned and indexed independently, then exposed through a composite index:

```text
CompositeDataSourceIndex
  Dict-backed store for now: Mapping[str, DataSourceIndex] plus a stable source
  map from global item position to child index key and local item position.
  get_item returns the child IndexItem with metadata that records the child
  index key, child datasource id, local position, and combination policy.

ConcatDataSourceIndex
  Appends child indexes in deterministic order.

Combination policies
  concat: deterministic append
  round_robin: deterministic interleave by child index
  weighted: later, sampling/balancing policy without mutating child indexes
  filtered: later, exposes a filtered view over child indexes
```

The abstract Torch dataset in Milestone 9 should only require the
`DataSourceIndex` protocol and a SampleBuilder. It should not need to know how
many underlying datasources exist.

### Deliverables

```text
src/rphys/datasources/core/adapters.py
src/rphys/datasources/core/sources.py
src/rphys/datasources/core/views.py
src/rphys/datasources/core/indexing.py
src/rphys/datasources/core/reports.py
src/rphys/datasources/core/groups.py
src/rphys/datasources/core/splits.py
src/rphys/datasources/core/filters.py
src/rphys/datasources/core/index_codecs.py
src/rphys/datasources/splits/subject.py
src/rphys/datasources/splits/explicit.py
src/rphys/datasources/validation/records.py
src/rphys/datasources/adapters/synthetic.py
tests/test_datasource_adapter_synthetic.py
tests/test_datasource_views.py
tests/test_datasource_filters.py
tests/test_datasource_splits.py
tests/test_datasource_groups.py
tests/test_index_builder.py
tests/test_index_build_reports.py
tests/test_index_codec_roundtrip.py
tests/test_composite_datasource_index.py
```

### Definition of done

```text
DataSourceAdapter emits DataSourceRef/RecordRef/FieldRef plus DataSourceValidationReport.
Synthetic datasource adapter emits a DataSourceRef with multiple fields.
DataSourceViewBuilder filters without mutating source refs.
DataSource filters compose through a minimal Filter/FilterChain contract.
GroupBuilder consumes GroupPlan and returns GroupResult with assignments,
counts, warnings, and provenance.
SplitBuilder consumes SplitPlan and GroupResult and returns SplitResult with a
non-mutating Split that can enforce group-disjoint splits.
IndexBuilder consumes DataSourceRef or DataSourceView plus an IndexPlan and
returns IndexResult containing DataSourceIndex plus IndexBuildReport.
IndexItems preserve datasource, record, group, split, and window provenance while remaining lazy IO requests.
IndexBuilder can create index-based temporal slices for selected fields.
DataSourceIndex exposes common access methods independent of storage format.
DataSourceIndexCodec serializes and reloads IndexItems without serializing loaded Samples or relying on pickle.
CompositeDataSourceIndex uses a dict-backed child store initially and preserves
child index key, child datasource identity, local position, and combination
policy in returned item metadata.
SampleBuilder can load the resulting IndexItems.
No formatting/export/transform/augmentation code lives under rphys.datasources.
```

### Dependencies

```text
Milestones 2 and 4.
```

---

## 10. Milestone 6: Operation foundations and functional kernels

### Goal

Implement only the minimal operation contracts and functional-code placement
rules needed for future SampleOps, transforms, augmentations, checks, export
ops, metric ops, and evaluation ops.

This milestone should not implement model-specific, algorithm-specific, or
domain-processing ops such as CHROM, POS, video normalization, landmark
detection, or graph pooling. Those can be added later once the base library
contracts are stable.

### Primary package

```text
rphys.ops
```

### Core public objects

```text
Operation
OperationContract
OperationContext
OperationResult
OperationPlan, optional
FunctionalKernel
```

Keep this milestone focused on operation behavior, context, contracts, and
results. Axis/layout/coordinate/grid/graph specs are deferred until concrete
functional kernels need them.

### Functional code placement

Pure functional code should be easy to call without constructing operation
objects:

```text
rphys.ops.functional
  Generic reusable functions with no Sample, FieldRef, datasource, or file IO
  access.

rphys.metrics.functional
  Metric numerical kernels that are useful outside Metric wrappers.

rphys.nn.functional
  Neural-network tensor helpers when a stable nn namespace exists.
```

`Operation` classes wrap functional kernels when the function needs declared
contracts, context, provenance, deterministic randomness, sample field access,
or pipeline composition. Do not hide important numerical behavior only inside an
operation class when it could be a small pure function with a clear scientific
contract.

Tensor/array kernels with no Sample, Batch, context, provenance, randomness, or
IO belong in functional modules. Learnable or architectural tensor computation
belongs in `Model` or `rphys.nn`. Future signal-processing algorithms such as
CHROM/POS should expose pure numerical kernels under `rphys.ops.functional` or a
later signal-specific functional subnamespace. Those kernels accept arrays or
tensors plus parameter objects and metadata values such as sampling rate; they
do not accept Batch, Sample, FieldLocator strings, IndexItems, or datasource
objects. Method wrappers live under `rphys.methods` and adapt Batch fields to
those kernels.

### Operation contract

```text
Operation
  Generic protocol for context-aware callable behavior.
  __call__(input, context) -> output or OperationResult.

OperationContract
  Declares input type, output type, required context, deterministic behavior,
  mutation behavior, side effects, and failure modes.

OperationContext
  Carries run id, seed material, worker/rank information, mode, provenance, and
  optional cache context. It is not a global config object.

OperationResult
  Optional structured wrapper for output, reports, warnings, provenance,
  metrics, cache hits/misses, and side-effect summaries.

OperationPipeline
  Ordered composition of Operations with explicit context propagation,
  deterministic stochastic behavior, and contract checks.
```

Batch-level composition is represented as `Operation[Batch, Batch]` when a
generic operation shape is useful. A public `BatchOperator`, `BatchProgram`, or
`BatchOpPipeline` should be deferred until repeated Batch-native non-method
operations justify the additional API. It must not replace `Operation`,
`SampleOp`, `Transform`, `Method`, `Loss`, `Metric`, or `MetricOp`.

### Recommended structure

```text
rphys/ops/core/base.py
rphys/ops/core/contracts.py
rphys/ops/core/context.py
rphys/ops/core/results.py
rphys/ops/functional/
```

### Deliverables

```text
src/rphys/ops/core/base.py
src/rphys/ops/core/contracts.py
src/rphys/ops/core/context.py
src/rphys/ops/core/results.py
src/rphys/ops/functional/__init__.py
tests/test_ops_contracts.py
tests/test_operation_context.py
tests/test_operation_result.py
tests/test_ops_functional_boundaries.py
```

### Definition of done

```text
Functional kernels are usable without Sample or datasource objects.
Operation wrappers can call functional kernels.
Losses, objectives, and metrics can reuse the same functional kernels.
No functional kernel performs file IO or hidden random sampling.
No public functional kernel accepts Sample, FieldRef, IndexItem, DataModel, or pipeline key strings.
Operation, OperationContract, OperationContext, OperationResult, and
OperationPipeline are enough to build specialized operation families later.
No public BatchOperator or BatchProgram API is required in the initial milestone.
No CHROM/POS/model-specific/data-processing ops are required in the initial milestone.
```

### Dependencies

```text
Milestone 1.
Can proceed in parallel with Milestones 4 and 5 once basic modality objects exist.
```

---

## 11. Milestone 7: SampleOps, transforms, augmentation, checks, and operation pipelines

### Goal

Implement a unified operation system that can express sample
preprocessing, derived-field extraction, filtering/annotation, export/save
steps, analysis, and visualization through composable operations.

### Primary packages

```text
rphys.ops.core
rphys.ops.sample
rphys.ops.pipelines
```

### Core public types

```text
Operation
Transform
OperationRole
OperationPipeline
OperationContext
PipelineContext
SampleOp
SampleTransform
BaseSampleTransform
Augmentation
SampleAugmentation
SampleCheck
SampleOpPipeline
SampleContext
AugmentationParams
SampleDecision / SampleRoute, optional
```

### Minimal operation contract

`Operation[In, Out]` is the generic base protocol from Milestone 6. It receives
an input object and context and returns an output object or `OperationResult`.
`OperationPipeline` chains operations.

`SampleOp` is the `Sample -> Sample` specialization used by runtime data
pipelines.

Batch-level preprocessing or postprocessing after collation should reuse
`Operation[Batch, Batch]` rather than introduce a separate public BatchProgram
API. `SampleOpPipeline` remains the Sample-specific pipeline for runtime sample
mutation, lazy field access, augmentation, checks, routing, and export.

`Transform` is an `Operation` whose primary purpose is to return a transformed
version of the input. It may be pure or declared-mutating.

`SampleTransform` is both a `SampleOp` and a `Transform`: it changes sample
fields or metadata according to declared contracts.

`Augmentation` is a stochastic `Transform` with replayable parameters.
`SampleAugmentation` is the sample-specific specialization.

`SampleCheck` is a deterministic assertion/report op. Save/export, metric,
analysis, and visualization ops should be `SampleOp`s, not `SampleTransform`s,
when their primary behavior is side-effect, measurement, or report generation.

Each operation declares:

```text
operation_id
role or kind
contract
deterministic
mutates
side_effects
```

`OperationRole` is lightweight classification metadata, not necessarily a
separate base class. Initial roles should cover deterministic processing,
stochastic augmentation, extraction/derived-field generation, checks,
filtering/routing, export/save, metric/evaluation, analysis, and visualization.
The role is used for navigation, policy checks, provenance, and documentation;
semantics still come from the operation contract, side-effect declaration,
input/output types, and result type.

SampleOp contracts add:

```text
reads: FieldLocator or BundleSpec declarations
writes: FieldLocator or BundleSpec declarations
deletes: FieldLocator declarations
input_sample_contract and output_sample_contract
```

Rules:

```text
All field references are FieldLocators parsed at construction time, not bare keys.
SampleOps may only read, write, rename, or delete declared locators unless the output contract explicitly permits dynamic fields.
SampleOps use Sample.peek/get/require/set_field/delete_field/rename_field for Sample access.
Lower-level rphys.ops.functional functions receive payloads and parameter objects only.
Default behavior is in-place mutation and returning the same Sample.
Non-mutating behavior must explicitly copy the Sample before writing.
Branching pipelines, paired views, and before/after comparisons must copy explicitly.
Side-effecting ops such as save/export must declare side effects and return or attach typed result metadata.
Contrastive and self-supervised view construction is a SampleOpPipeline concern
when it depends on per-sample randomness or lazy fields. SampleAugmentation ops
should read a wide-window Sample and write declared view locators such as
inputs/video.rgb.view_a and inputs/video.rgb.view_b before collation.
```

### SampleAugmentation

`Augmentation` is the stochastic specialization of Transform.
`SampleAugmentation` is the sample-specific specialization with
`deterministic = False`. Stochastic operations must make randomness explicit:

```python
class SampleAugmentation(BaseSampleTransform):
    deterministic = False

    def should_apply(self, sample: Sample, context: SampleContext) -> bool:
        ...

    def sample_params(self, sample: Sample, context: SampleContext) -> AugmentationParams:
        ...

    def apply_params(self, sample: Sample, params: AugmentationParams, context: SampleContext) -> Sample:
        ...
```

The pipeline should provide reproducible context and RNG streams derived from:

```text
run seed
epoch
worker ID
item ID or sample ID
transform index
transform name
view name, when relevant
```

`sample_params` must draw only from RNG streams provided by `SampleContext`.
`apply_params` must be deterministic for a fixed `Sample` and
`AugmentationParams`. `AugmentationParams` should record the apply decision,
sampled values, affected locators or `BundleSpec` group, operation name/index,
and seed fingerprint needed for audit or replay.

Synchronized augmentations should sample one parameter object per declared field
group and apply it consistently to all linked locators. No augmentation may use
global `random`, `numpy.random`, or the torch default RNG directly.

### Operation pipelines

`OperationPipeline` chains arbitrary operations. `SampleOpPipeline` chains
runtime sample operations and accepts either an ordered
`Sequence[SampleOp]` or an ordered `Mapping[str, SampleOp]`.
Mapping keys are stable operation names for external configuration, debugging,
and provenance.

```python
pipeline = SampleOpPipeline([
    required_field_check,
    deterministic_sample_transform,
    optional_sample_augmentation,
    output_contract_check,
])

sample = pipeline(sample, context)
```

`SampleOpPipeline` derives per-operation `SampleContext` from `PipelineContext`:

```text
run seed
usage label
epoch
worker ID
item ID or sample ID
split/group metadata when available
operation index
operation name
transform name
view name, when relevant
```

Rules:

```text
OperationPipeline applies operations in order.
OperationPipeline validates declared input/output contracts according to policy.
OperationPipeline derives reproducible RNG streams for stochastic operations.
OperationPipeline enforces deterministic/export/evaluation policy by rejecting or skipping stochastic operations unless explicitly enabled.
OperationPipeline may record transform provenance and augmentation params.
OperationPipeline should be usable in training, inference, preprocessing, export,
analysis, visualization, and metric computation.
OperationPipeline never scans datasources, chooses splits, or maps over datasources by
itself. Individual lazy fields may load when an op accesses their payload.
```

### SampleCheck

`SampleCheck` is a `SampleOp` used for runtime assertions.

Rules:

```text
deterministic = True
no writes by default
failures raise typed rphys errors unless configured to emit a declared report field
checks may inspect declared locators and context only
checks are not datasource filters. Sample-level routing/filter decisions should
be represented by explicit SampleOp outputs or metadata, not hidden mutation.
```

### Sample filtering and routing

Datasource/index filters remain separate when they can operate before loading.
Sample-level filters are operations over loaded or lazy samples:

```text
SampleAnnotateOp
  Adds inclusion/exclusion, quality, split, or usage metadata.

SampleFilterOp
  Returns a SampleDecision or raises a configured skip signal.

SampleRouteOp
  Routes samples to named downstream pipelines.
```

Use datasource filters for split/index construction. Use SampleOps when the
decision depends on loaded payloads, computed quality, or previous operations.

### Implementation organization

Organize sample operations by behavior, then modality when useful:

```text
rphys/ops/
  core/
    base.py
    context.py
    contracts.py

  pipelines/
    operation_pipeline.py
    sample_op_pipeline.py

  sample/
    ops.py
    transforms.py
    augmentation.py
    checks.py
    routing.py
    provenance.py

  export/
    save.py
    codec_selection.py
```

Behavior-first organization makes it easier to find transforms, augmentation,
checks, routing/filter ops, and export-related operations. Modality-specific
packages can be added later when there is real reusable implementation.
The behavior-first package layout should mirror `OperationRole` enough that a
user can tell whether code is training-time augmentation, deterministic
processing, extraction, checking, export, evaluation, analysis, or visualization
without inspecting implementation details.

### Deliverables

```text
src/rphys/ops/core/base.py
src/rphys/ops/core/context.py
src/rphys/ops/core/contracts.py
src/rphys/ops/core/roles.py
src/rphys/ops/pipelines/operation_pipeline.py
src/rphys/ops/pipelines/sample_op_pipeline.py
src/rphys/ops/sample/ops.py
src/rphys/ops/sample/transforms.py
src/rphys/ops/sample/augmentation.py
src/rphys/ops/sample/checks.py
src/rphys/ops/sample/routing.py
src/rphys/ops/sample/provenance.py
tests/test_pipeline_base.py
tests/test_sample_op_contracts.py
tests/test_sample_transform.py
tests/test_sample_op_pipeline.py
tests/test_sample_op_pipeline_named_operations.py
tests/test_sample_augmentation_reproducibility.py
tests/test_sample_augmentation_replay.py
tests/test_transform_mutation_contracts.py
tests/test_sample_filter_ops.py
tests/test_sample_checks.py
```

### Definition of done

```text
An OperationPipeline can chain generic operations with context.
A role/kind is recorded for operations and used by policy/provenance checks
without forcing one base class per behavior.
A SampleOpPipeline can chain named SampleOps, deterministic transforms, augmentations, checks, and routing/filter ops.
Sequence and mapping construction both preserve operation order.
SampleOps declare read/write/delete FieldLocators and undeclared mutation fails.
Operation contracts fail loudly when required fields are missing or malformed.
SampleTransforms mutate Samples by default and explicit copy behavior is tested.
Augmentations are reproducible from PipelineContext and replayable from AugmentationParams.
Stochastic operations do not use global RNG.
Checks raise typed errors or write declared report fields.
Sample-level filter/routing behavior is explicit and tested.
OperationPipeline deterministic/export/evaluation policy is tested.
No SampleOpPipeline code scans datasources, chooses splits, or implements raw ops logic.
SampleFields only load when an operation accesses payload data.
```

### Dependencies

```text
Milestones 3 and 6.
```

---

## 12. Milestone 8: Save/export ops and derived datasource generation

### Goal

Represent formatting, offline derived fields, prediction export, and format
conversion as normal datasource processing pipelines whose final operations
write fields through codecs and emit a new `DataSourceRef`.

This milestone replaces a separate offline-output subsystem with one reusable
mechanism:

```text
DataSourceRef / DataSourceView
  -> IndexItems
  -> SampleBuilder creates lazy Samples
  -> SampleOpPipeline applies SampleOps
  -> CodecSelectionOp marks how fields should be written
  -> SaveOp writes selected fields through codecs
  -> new FieldRefs
  -> new RecordRefs
  -> new DataSourceRef
```

### Primary packages

```text
rphys.ops.export
rphys.io.core
rphys.datasources.manifest
```

### Key interfaces

```text
ExportSpec
ExportTarget / OutputLayout
ExportPolicy
CodecSelectionOp
SampleSaveOp / SaveOp
FieldExportResult
RecordExportResult
ExportResult
ExportReport
DataSourceManifestWriter
DerivedDataSourceBuilder
```

### Object boundary rules

`ExportSpec` maps input `FieldLocator`s or `DataKey`s to output fields, codec
keys, output layout, and write policy. It is data, not an orchestrator.

`CodecSelectionOp` annotates selected sample fields with output codec,
schema/resource target, and save metadata. It should not write files.

`SampleSaveOp` writes declared loaded or lazy fields to `ExportTarget`s through
`FieldCodec` save support. It returns `FieldExportResult`s and may attach export
result metadata to the sample.

`OutputLayout` derives stable target URIs from datasource id, record id, field
key, run/export id, and `ExportSpec`. It must not depend on mutable loaded
payload attributes as the only naming source.

`DataSourceManifestWriter` assembles new `RecordRef`s and a new `DataSourceRef`
from `FieldExportResult`s. It records source datasource id, source record id,
source field lineage, export id, spec fingerprint, and report counts.

A derived `DataSourceRef` is the durable rphys artifact boundary for exported
fields and predictions. Generic artifact registration, artifact stores, and
workflow-stage materialization belong to loom or downstream code.

Symlink/copy behavior is an export policy and/or save codec capability, not a
separate datasource adapter. Links and copies must record source `ResourceRef`,
target `ResourceRef`, and link/copy policy in the new `FieldRef` metadata.

### Use cases

```text
Repackage existing fields into a canonical storage layout.
Create symlinks or copies while preserving source ResourceRef lineage.
Convert video or signal fields to a different codec/container.
Run a SampleOpPipeline that detects landmarks and then saves landmark fields.
Export prediction Samples as records in a manifest-backed DataSourceRef.
Emit a derived DataSourceRef that can be filtered, indexed, and loaded like any other datasource.
```

### Important rule

Formatting/export is not a datasource discovery component.
Prediction, validation, or test outputs become durable only by composing returned
Sample/Batch fields with `CodecSelectionOp`, `SaveOp`, and
`DataSourceManifestWriter`; Method, Learner, Trainer, Loss, and Metric objects
must not write prediction artifacts implicitly.

DataSource code answers:

```text
What fields exist?
Which records should be selected?
Which slices should be indexed?
```

Export ops answer:

```text
Which fields should be saved?
Which codec and target layout should each field use?
What new FieldRefs describe the written outputs?
What lineage links the new FieldRefs to source FieldViews?
What was written, skipped, copied, linked, replaced, or failed?
```

### Deliverables

```text
src/rphys/ops/export/specs.py
src/rphys/ops/export/layout.py
src/rphys/ops/export/save_ops.py
src/rphys/ops/export/results.py
src/rphys/io/core/context.py
src/rphys/datasources/core/manifest_writer.py
tests/test_export_spec.py
tests/test_codec_selection_op.py
tests/test_sample_save_op.py
tests/test_export_lineage.py
tests/test_derived_datasource_manifest_writer.py
tests/test_export_idempotency.py
tests/test_formatting_is_not_datasource_layer.py
docs/features/export_and_derived_datasources.md
```

### Definition of done

```text
A datasource/index can be processed by SampleOpPipeline and exported into a new DataSourceRef.
ExportSpec declares input locators, output field keys, target layout, codec selection,
and write policy.
ExportResult includes per-field, per-record, and datasource-level results.
New FieldRefs preserve source lineage and export metadata.
DataSourceManifestWriter creates the output DataSourceRef from export results without
rescanning output directories.
Output layout is deterministic and tested.
Write policy covers skip, overwrite, fail-if-exists, symlink/link fallback, and copy fallback.
ExportReport counts written, skipped, linked, copied, replaced, and failed fields.
At least one save path writes through FieldCodec save support.
At least one export path creates a manifest-backed derived DataSourceRef.
Save/export ops do not scan datasources, choose splits, or build indexes.
DataSource adapters do not invoke export code.
No formatting/export module lives under rphys.datasources.
```

### Dependencies

```text
Milestones 4, 5, and 7.
```

---

## 13. Milestone 9: DataSourceIndex adapters, Torch datasets, and DDP-safe cache

### Goal

Implement thin iteration adapters over the generic `DataSourceIndex` protocol.
This milestone is the runtime bridge from datasource indexing into framework
iteration: it obtains an `IndexItem` from a `DataSourceIndex`, builds a lazy
`Sample` through `SampleBuilder`, optionally applies a `SampleOpPipeline` with
deterministic context, and collates `Sample`s into the generic `Batch` object.

The Torch adapter must not become a datasource discovery, split, indexing,
cache-implementation, formatting, or model-input preparation layer.

### Primary packages

```text
rphys.datasources.indexes
rphys.datasources.torch
rphys.datasources.cache
```

### Key interfaces

```text
DataSourceIndex
IndexItemStore
CompositeDataSourceIndex
ConcatDataSourceIndex
TorchIndexSampleDataset
PipelineIndexSampleDataset wrapper, optional
BatchCollater
TorchDataLoaderPlan
TorchDataLoaderBuilder
WorkerContextFactory
SampleRuntimeContext
CachePolicy
CacheKey
CacheStore
CacheEntry
CacheManifest
CacheContext
DistributedCacheCoordinator
```

### Object boundary rules

`DataSourceIndex` is the common index protocol. A Torch dataset, custom
iterator, or downstream framework adapter should need only this protocol, not a
specific manifest implementation.

`TorchIndexSampleDataset` owns a `DataSourceIndex`, a `SampleBuilder`, an
optional `SampleOpPipeline`, a split/usage label, optional `Split` / view
metadata, and a `WorkerContextFactory`. It does not own `DataSourceAdapter`,
`IndexBuilder`, or `SplitBuilder` instances.

`__getitem__` resolves only the integer position to an `IndexItem`, builds a
`Sample` through `SampleBuilder`, attaches runtime identity metadata, derives a
`SampleRuntimeContext`, applies the optional `SampleOpPipeline`, and returns a
`Sample`.

`SampleRuntimeContext` should include datasource id, view id, split/usage, sample
position, stable item id, record id when available, worker id, epoch when
available, run seed, operation-safe seed material, and distributed rank/world
size when available.

`BatchCollater` delegates to the generic `Batch` / `CollatePolicy` from
milestone 3. It must preserve `FieldLocator` keys and per-item metadata. It
should not parse roles with string splits or hard-code inputs/targets/source
behavior.
Do not add a broad public `BatchAdapter` in this milestone. `BatchCollater` is
the core bridge from Samples to Batch; arbitrary external batch conversion is a
later framework-boundary concern and should happen before Trainer/Learner
entrypoints.

`TorchDataLoaderPlan` is a serializable description of PyTorch `DataLoader` options
such as `batch_size`, `shuffle`, `sampler`, `drop_last`, `num_workers`,
`pin_memory`, `prefetch_factor`, `persistent_workers`,
`multiprocessing_context`, `generator`, and `worker_init_fn` policy.

`TorchDataLoaderBuilder` converts a sample dataset plus `TorchDataLoaderPlan` into a PyTorch
`DataLoader`. It may provide sensible split/usage defaults, but it does not choose
splits, construct `IndexItem`s, or infer scientific preprocessing.

Caching is in scope but lives under `rphys.datasources.cache` initially because
the first cache consumer is datasource-index sample loading. Promote it later
only if cache contracts become shared outside datasource/index workflows.

Cache behavior is controlled by
`CachePolicy`, keyed by index item identity, FieldView/resource fingerprints,
codec version, optional operation/pipeline fingerprint, run context, and
software versions where relevant. No cache may change scientific data flow
without provenance and invalidation rules.

DDP-safe cache behavior must support:

```text
rank-aware CacheContext with rank, local_rank, world_size, worker_id, and run id
atomic write to temporary location followed by commit/rename
pending/committed/failed entry states
file locks or storage-backend compare-and-swap where supported
rank-zero-write/broadcast or first-writer-wins policies
barrier/wait policies with timeout and stale-lock recovery
fingerprint validation before reuse
read-only shared cache plus optional per-rank local cache
provenance and invalidation metadata for resources, codecs, ops, and software
```

### Runtime flow

```text
TorchIndexSampleDataset.__getitem__(idx)
  -> DataSourceIndex.get_item(idx)
  -> derive SampleRuntimeContext
  -> if cache policy says hit: load cached Sample or cached fields
  -> else:
       SampleBuilder.build(IndexItem, LoadContext)
       optional precache SampleOpPipeline(sample, context)
       save cache entry through CacheStore when policy permits
  -> optional augmentation SampleOpPipeline(sample, context)
  -> optional postaugmentation SampleOpPipeline(sample, context)
  -> Sample

BatchCollater.__call__(samples)
  -> Batch.from_samples(samples, CollatePolicy)

TorchDataLoaderBuilder.build(dataset, plan)
  -> torch.utils.data.DataLoader(dataset, collate_fn=BatchCollater(...), ...)
```

### Rules

```text
The adapter does not scan raw directories.
The adapter does not choose splits.
The adapter does not construct IndexItems or windows.
The adapter does not export or manage offline derived fields.
The adapter does not format Samples for a specific model, loss, or trainer.
The adapter may apply SampleOpPipeline on the loaded or lazy Sample.
The adapter must pass deterministic SampleRuntimeContext to SampleOpPipeline.
The adapter must expose stable item identity for reproducibility and debugging.
The collater must use FieldLocator-aware Batch/CollatePolicy behavior.
Worker seeding must not rely only on global random, numpy, torch, or framework state.
Caching loaded fields, probed metadata, or deterministic operation outputs is
allowed only through explicit CachePolicy.
Precache operations must be deterministic and cache-safe. Augmentations should
run after cache retrieval/build unless explicitly replayed and fingerprinted as
part of the cache key. Postaugmentation operations run after augmentation and
are normally not cached unless declared deterministic and cache-safe.
Composite indexes must preserve source datasource/view/item metadata instead of
mutating samples in place.
```

### Deliverables

```text
src/rphys/datasources/indexes/base.py
src/rphys/datasources/indexes/composite.py
src/rphys/datasources/torch/dataset.py
src/rphys/datasources/torch/dataloader_plan.py
src/rphys/datasources/torch/dataloaders.py
src/rphys/datasources/torch/worker_context.py
src/rphys/datasources/cache/policy.py
src/rphys/datasources/cache/keys.py
src/rphys/datasources/cache/stores.py
src/rphys/datasources/cache/context.py
src/rphys/datasources/cache/distributed.py
tests/test_index_dataset.py
tests/test_index_dataset_context.py
tests/test_datasource_index_protocol.py
tests/test_composite_datasource_index.py
tests/test_dataloader_collate.py
tests/test_dataloader_spec.py
tests/test_dataloader_no_discovery_or_split.py
tests/test_dataloader_augmentation_reproducibility.py
tests/test_cache_policy.py
tests/test_cache_fingerprint_invalidation.py
tests/test_cache_atomic_commit.py
tests/test_cache_ddp_coordination.py
```

### Definition of done

```text
A PyTorch DataLoader can load ordered IndexItems lazily into Samples.
TorchIndexSampleDataset can consume any DataSourceIndex implementation.
TorchIndexSampleDataset returns Samples keyed by FieldLocator.
Batch collation uses the generic Batch and CollatePolicy interfaces.
SampleOpPipeline receives deterministic SampleRuntimeContext in single-worker and multi-worker tests where practical.
Split, usage, datasource, record, item, worker, and rank metadata are available for provenance without mutating FieldRefs or IndexItems.
TorchDataLoaderPlan covers common PyTorch DataLoader options and split/usage defaults.
Collation does not hard-code inputs/targets/source transfer behavior.
Tests show TorchIndexSampleDataset does not scan, split, index, export, or perform model-specific formatting.
CachePolicy, CacheKey, CacheStore, and DistributedCacheCoordinator are tested
for deterministic keys, atomic writes, stale entry invalidation, and rank-safe
coordination.
```

### Dependencies

```text
Milestones 3, 4, 5, and 7.
```

---

## 14. Milestone 10: Models, methods, and nn base contracts

### Goal

Define the abstraction boundary between generic loaded `Batch`es, prediction
methods, and computational models.

This milestone should implement base classes and protocols only. Do not
implement CHROM, POS, neural baselines, or any concrete method/model yet.
Models/ops compute tensors or structured model inputs. Methods adapt `Batch`
fields into those computations and return a `Batch` with added prediction
fields and metadata.

### Primary packages

```text
rphys.methods
rphys.models
rphys.nn
```

### Concepts

```text
Model
  Lower-level computational object, often but not necessarily torch.nn.Module.
  It should operate on tensors or structured model inputs, not directly on
  DataSourceRef, IndexItem, SampleBuilder, DataLoader, artifact paths, or
  datasource discovery objects. A Model is not a Method by inheritance.

Method
  Semantic batch-level prediction or representation algorithm over Batch fields.
  It declares input/output contracts, owns input/output field semantics, uses
  typed adapters, may contain zero, one, or many Models, differentiable ops, or
  classical signal-processing algorithms, and emits prediction fields under
  FieldLocator keys. A Method may be trainable or non-trainable.

MethodInputAdapter
  Extracts declared FieldLocator values from Batch and converts them into
  model/op inputs with explicit layout, dtype, device, and metadata assumptions.
  It exposes typed read selectors, parses FieldLocator and MetadataKey values at
  construction, and does not parse locator strings at call time.

MethodOutputAdapter
  Converts raw model/op outputs into FieldValues or a prediction Batch with
  declared DataKeys, FieldLocators, FieldSpecs, metadata, and provenance.
  It exposes typed write selectors, declares output FieldSpecs and mutation
  policy, and does not parse locator strings at call time.

MethodOutput
  Optional sidecar wrapper for a prediction Batch plus diagnostics/provenance
  when callers need more than the returned Batch. Predictions are not a special
  rigid object; they are normal field containers with different roles, locators,
  and metadata.

nn base namespace
  Optional location for future reusable neural-network modules, layers, and
  tensor utilities. The initial milestone should provide only lightweight base
  protocols or namespace scaffolding, not a model zoo.
```

### Object boundary rules

Methods must not parse raw slash strings at call time. `FieldLocator`s and
`MetadataKey`s are parsed at construction and stored as typed selectors.

Models should not know about `Batch` roles unless the model itself is explicitly
a `Batch`-native model. The default neural path is `Batch` ->
`MethodInputAdapter` -> model inputs -> model -> `MethodOutputAdapter` ->
prediction `Batch`.

`Method.predict` must not mutate the input `Batch` unless declared. It should
return a new or derived `Batch` where each sample has additional prediction or
representation fields under locators such as `predictions/signal.bvp`,
`predictions/label.logits`, or `outputs/embedding.video`. Conceptually, a
Method converts a Batch into a Batch with added fields. Output adapters may
receive the input Batch for metadata alignment, but must not mutate it unless
the Method explicitly declares an in-place mutation policy.

Methods should not export predictions to files, update metrics, train models,
or decide splits. Downstream pipelines can save prediction fields through
normal save/export ops.

A Method may expose trainable state or parameters, but it must not perform
optimizer stepping, scheduler stepping, checkpoint writing, or training-loop
control. Trainer/OptimizerSpec consumes explicit method parameters and state;
optimizer, scheduler, checkpoint, device, and distributed behavior remain
outside Method.

Base contracts must support methods with no neural Model, including future
CHROM/POS-style signal-processing methods, but Milestone 10 still implements no
concrete CHROM/POS/neural baseline. Concrete signal-processing Methods must
document input layout, color space, shape, dtype/device, sampling rate, temporal
alignment, windowing/filtering, normalization order, NaN/flat/short-input
behavior, output units, output sampling rate, metadata/provenance, and citations.

Prediction composition may be implemented as optional batch pre-processing
`OperationPipeline[Batch, Batch]` -> `Method.predict` -> optional batch
post-processing `OperationPipeline[Batch, Batch]`. Method remains the public
semantic prediction contract; the pipeline is composition machinery, not a
replacement for Method.

### Method protocol

```python
class Method(Protocol):
    name: str
    input_contract: SampleContract
    output_contract: SampleContract
    reads: tuple[FieldLocator, ...]
    writes: tuple[FieldLocator, ...]

    def predict(self, batch: Batch, context: PredictionContext) -> Batch:
        ...
```

Optional capability protocols:

```python
class StatefulMethod(Method, Protocol):
    def state_dict(self) -> Mapping[str, Any]:
        ...

    def load_state_dict(
        self,
        state: Mapping[str, Any],
        *,
        strict: bool = True,
    ) -> StateLoadReport | None:
        ...


class TrainableMethod(StatefulMethod, Protocol):
    def parameters(self) -> Iterable[Any]:
        ...

    def train(self, mode: bool = True) -> None:
        ...

    def eval(self) -> None:
        ...
```

Torch-specific refinements may narrow `parameters()` to
`Iterable[torch.nn.Parameter]` only in optional torch-dependent modules.

```python
@dataclass(frozen=True)
class MethodOutput:
    predictions: Batch
    diagnostics: Mapping[FieldLocator, FieldValue] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)
```

### Initial scope

```text
Base Method protocol.
Optional StatefulMethod and TrainableMethod capability protocols.
Base Model protocol or lightweight wrapper.
MethodInputAdapter and MethodOutputAdapter base classes.
Optional MethodOutput sidecar container.
PredictionContext.
rphys.nn namespace scaffolding for future common neural modules.
No concrete methods, models, losses, objectives, metrics, learners, or trainers.
```

### Deliverables

```text
src/rphys/methods/core/base.py
src/rphys/methods/core/adapters.py
src/rphys/methods/core/context.py
src/rphys/methods/core/output.py
src/rphys/models/core/base.py
src/rphys/nn/__init__.py
src/rphys/nn/core.py
tests/test_method_protocol.py
tests/test_method_adapters.py
tests/test_method_no_batch_mutation.py
tests/test_method_output.py
tests/test_model_protocol.py
```

### Definition of done

```text
Base Method can consume Batch fields through typed adapters and emit prediction
fields under FieldLocator keys.
MethodInputAdapter and MethodOutputAdapter parse selectors at construction.
Method.predict returns a new or declared-mutating Batch with added prediction or
representation fields.
MethodOutput is an optional Batch plus diagnostics/provenance sidecar.
Models are testable independently from Batch, DataSourceRef, SampleBuilder,
DataLoader, Learner, Trainer, and artifact paths.
Stateful/trainable method capabilities do not import torch in core modules and
do not own optimizer, scheduler, checkpoint, device, or distributed behavior.
No concrete CHROM/POS/neural baseline method is implemented in this milestone.
rphys.nn imports without optional heavy dependencies beyond what the chosen base protocol requires.
```

### Dependencies

```text
Milestones 3, 6, 7, and 9.
```

---

## 15. Milestone 11: Loss, objective, and metric base contracts

### Goal

Define base contracts for loss/error terms, optimizer objectives, and metrics
without implementing concrete numerical algorithms yet.

Losses, objectives, and metrics all read declared fields and metadata from
`Sample` or `Batch` containers, but they serve different purposes.

```text
Loss
  Computes one or more differentiable error or penalty terms from declared
  runtime fields. A Loss may return the same or derived Sample/Batch with
  declared loss fields attached plus structured LossTerm data.

Objective
  Combines losses with everything else the optimizer cares about: term weights,
  regularization, constraints, parameter penalties, schedules, auxiliary
  optimization values, and the final scalar used for backward/optimizer steps.

Metric
  Computes detached measurement observations or result tables for monitoring,
  evaluation, analysis, or reporting. Metrics are not optimizer targets.
```

They may use `rphys.ops.functional`, `rphys.losses.functional`, and
`rphys.metrics.functional` kernels, but must not own training loops, datasource
discovery, sample loading, optimizer stepping, or file export.

### Primary packages

```text
rphys.losses
rphys.losses.functional
rphys.objectives
rphys.metrics
rphys.metrics.functional
```

### Key interfaces

```text
Measure
Loss
LossInputSpec
LossContract
LossTerm
LossResult
LossContext
Objective
ObjectiveInputSpec
ObjectiveContract
ObjectiveTerm
ObjectiveResult
ObjectiveContext
CompositeObjective
Metric
MetricValue
MetricInputSpec
MetricContract
MetricObservation
MetricResultTable
MetricContext
GroupBySpec
MetricAggregationPlan
MetricAggregator
TorchMetricAdapter, optional
```

### Object boundary rules

Losses, objectives, and metrics must parse `FieldLocator`s and `MetadataKey`s at
construction time and store typed selectors.

`Measure` is the shared contract for declared inputs, metadata selectors,
units, shape expectations, and failure behavior. It should remain small and
abstract. `Loss`, `Objective`, and `Metric` are the public semantic
specializations.

Losses return structured `LossResult` / `LossTerm` objects. `LossResult` should
carry the same or derived `Sample | Batch` plus differentiable term data, so a
loss can be used either as a pure computation or as a declared runtime-field
writer in an `OperationPipeline`. Avoid a separate `CompositeLoss` abstraction
unless implementation pressure shows it is not covered by `Objective`.

Loss contracts should declare whether returned `LossTerm` values are
differentiable, whether they reduce per-sample or across the batch, how masking
works, how missing fields or metadata fail, and whether gradients are expected
through predictions, targets, both, or neither.

Objectives return structured `ObjectiveResult` / `ObjectiveTerm` objects.
`ObjectiveResult.total` is the optimizer-facing scalar. It may include loss
terms, weighted loss terms, regularization terms, constraints, parameter
penalties, auxiliary differentiable terms, or schedule-dependent weights. The
objective owns the aggregation policy; the Trainer only sees a backwardable
scalar and structured term metadata.

Core Loss, Objective, and Metric objects consume Sample/Batch field containers
and return typed result objects. They may also return a container with declared
`losses/*`, `objectives/*`, `metrics/*`, or diagnostic fields when that improves
pipeline composition. Those writes must be explicit in the contract and must
preserve provenance. Training code must still consume `ObjectiveResult.total`,
not infer optimizer behavior from a string field such as `loss.total`.

Target selection is part of `LossInputSpec`, `ObjectiveInputSpec`, or
`MetricInputSpec`. Optional loss/objective/metric input adapters may exist only
as pure field-selector helpers owned by the implementation, especially when
wrapping external tensor kernels. They must not mutate Batch, log, write files,
or depend on Trainer state.

Metrics return `MetricObservation`s or `MetricResultTable` rows. They may return
declared metric fields when useful for a pipeline, but they should not log,
write files, update trainer state, parse strings at runtime, or influence
optimizer gradients.
Metrics should compute under detached/no-grad semantics unless explicitly
documented otherwise, and metric outputs are never used directly for optimizer
gradients.

Metrics may be applied in normal `OperationPipeline`/`SampleOpPipeline`
evaluation flows.
Metric aggregation can group rows by typed metadata such as datasource, subject,
record, split, usage, method, run id, or arbitrary metadata keys.

`TorchMetricAdapter` can be considered later to simplify distributed metric
state, but it should adapt to the `Metric` contract rather than define the core
API.

Stateful `update` / `compute` / `reset` behavior may be provided by
`MetricAggregator`, `MetricAccumulator`, or adapters such as `TorchMetricAdapter`.
The core Metric contract should preserve per-sample/per-window observations and
grouping metadata before aggregation.

Recommended protocol shapes:

```python
class Loss(Protocol):
    name: str
    contract: LossContract
    reads: tuple[FieldLocator, ...]
    writes: tuple[FieldLocator, ...] = ()

    def __call__(self, data: Sample | Batch, context: LossContext) -> LossResult:
        ...


class Objective(Protocol):
    name: str
    contract: ObjectiveContract
    losses: Mapping[str, Loss]

    def __call__(self, batch: Batch, context: ObjectiveContext) -> ObjectiveResult:
        ...


class Metric(Protocol):
    name: str
    contract: MetricContract
    reads: tuple[FieldLocator, ...]

    def observe(self, batch: Batch, context: MetricContext) -> MetricResultTable:
        ...
```

### Metric computation and aggregation patterns

Support both patterns through normal pipelines and result tables:

```text
A. Compute metric per sample/window, then aggregate metric values.
B. Aggregate prediction Samples first, then compute metrics.
```

Examples:

```text
Per-window metric -> average by subject/datasource.
Window predictions -> overlap-average into record-level waveform -> compute heart-rate MAE.
```

### Deliverables

```text
src/rphys/losses/core/base.py
src/rphys/losses/core/contracts.py
src/rphys/losses/core/terms.py
src/rphys/losses/functional/__init__.py
src/rphys/objectives/core/base.py
src/rphys/objectives/core/contracts.py
src/rphys/objectives/core/terms.py
src/rphys/objectives/core/composite.py
src/rphys/metrics/core/base.py
src/rphys/metrics/core/contracts.py
src/rphys/metrics/core/results.py
src/rphys/metrics/core/grouping.py
src/rphys/metrics/core/aggregation.py
src/rphys/metrics/functional/__init__.py
tests/test_loss_base.py
tests/test_loss_terms.py
tests/test_objective_base.py
tests/test_objective_terms.py
tests/test_composite_objective.py
tests/test_metric_base.py
tests/test_metric_contracts.py
tests/test_metric_result_table.py
tests/test_metric_groupby_metadata.py
tests/test_losses_objectives_metrics_no_filesystem_coupling.py
```

### Definition of done

```text
Losses, objectives, and metrics address fields by FieldLocator, not ad hoc strings.
Losses declare typed input selectors, metadata requirements, reduction behavior,
per-sample versus cross-batch behavior, differentiability, masking, and failure
behavior.
Losses return LossResult/LossTerm values with a Sample/Batch container and do
not rely on a `loss.total` Batch field as the public training contract.
Objectives combine LossResults and optimizer-relevant terms into an
ObjectiveResult with a scalar total and named term metadata.
Metrics declare typed input selectors, metadata requirements, units, shapes,
sampling rates, masks, reductions, and failure behavior.
MetricResultTable can store per-sample/per-window observations and aggregated
rows with grouping metadata.
Metric aggregation groups by typed metadata rather than metric-name prefixes.
Metric state, if needed, lives in aggregators/adapters rather than hidden
mutation inside the core Metric.
Losses, objectives, and metrics do not depend on trainer hooks, logger state,
datasource scanning, SampleBuilder, optimizer stepping, or direct filesystem
export.
```

### Dependencies

```text
Milestones 3, 6, 7, and 10.
```

---

## 16. Milestone 12: Learner and trainer base contracts

### Goal

Define optional learning and training abstractions that keep step semantics
separate from optimization/runtime loops.

This milestone should implement base classes/protocols and one minimal concrete
`SupervisedLearner` because supervised rPPG is the first expected learning
style. It should not include concrete contrastive/self-supervised learners, a
large trainer framework, Lightning adapter, or experiment framework integration.

### Primary packages

```text
rphys.learning
rphys.training
```

### Core interfaces

```text
Learner
SupervisedLearner
StepOutput
TrainingContext
PredictionContext
LoopContext
Trainer
TrainingPlan
TrainingResult
LoopMode
LoopState
BackwardableScalar
DeviceMover
OptimizerSpec
SchedulerSpec
CheckpointMetadata
DistributedContext
run_train, experimental
CallbackHook, optional
```

### Object boundary rules

`Learner` owns mode-specific learning semantics such as supervised,
self-supervised, contrastive, masked, or adaptation learning. It couples a
`Method` to an optional optimizer `Objective` and monitoring/evaluation
`Metric`s. It calls `Method.predict`, evaluates the Objective when appropriate,
derives any LossContext/ObjectiveContext/MetricContext views needed by those
contracts, and returns `StepOutput`.

`Trainer` owns execution mechanics: iteration, device movement, grad/no-grad
mode, backward, gradient accumulation, optimizer/scheduler stepping, clipping,
precision/autocast policy, distributed context, checkpoint hooks,
loop-level logging, and callback dispatch. It delegates scientific step
semantics to `Learner`.

Prediction does not require an Objective or Loss. `Method.predict` and
`Learner.predict_step` should work when no training objective is configured.

`Learner` should not call `optimizer.step`, `scheduler.step`, checkpoint
writers, dataloader builders, `SampleBuilder`, datasource adapters, or save/export ops.

`Trainer` should not parse input/target/prediction locators, compute scientific
losses directly, build `IndexItem`s, run `SampleBuilder`, export outputs, or
assume supervised learning.

Optimizer, scheduler, checkpoint, device, distributed, profiler, and logging
behavior should be explicit specs or hooks. Do not hide them inside Model,
Method, DataSourceAdapter, Metric, Loss, or Objective objects.

`run_train(...)` may be added as an experimental function-style entrypoint for
loom/downstream wrappers. It should delegate to `TrainingPlan`, `Trainer`, and
`Learner` rather than define a workflow runtime. Its argument schema should
remain flexible until the orchestration layer has concrete needs, but its return
value should be a typed `TrainingResult` with checkpoint, resume, traceability,
and validation summaries.

Framework adapters can be added later in downstream packages. They are not the
core API. If external framework batches must be consumed, conversion to rphys
Batch happens before Trainer/Learner entrypoints through an explicit framework
adapter. Trainer and Learner still operate on Batch and do not own model,
target, or metric formatting.

`LoopMode` describes active runtime loop semantics for learner/trainer
execution:

```python
class LoopMode(str, Enum):
    TRAIN = "train"
    VALIDATE = "validate"
    TEST = "test"
    PREDICT = "predict"
```

`LoopMode` is not a datasource split, workflow stage, roadmap phase, or
artifact-processing stage. `TrainingContext` and `PredictionContext` may
specialize or wrap `LoopContext`, but loop contexts should expose mode, optional
split, optional device, gradient-enabled state, loop step, global step, and
metadata. `context.split` records the data partition or usage label when known;
it must not be inferred as equivalent to `context.mode`.

Validation measures during training for monitoring, early stopping, or
checkpoint selection. It must not perform optimizer or scheduler updates.
Selection/checkpoint effects are allowed only through explicit
TrainingPlan/checkpoint hooks. Testing is final held-out assessment. It may
compute metrics and return predictions, but must not update model-selection
state, early-stopping state, or best-checkpoint state. Prediction/inference
produces prediction fields without requiring targets or losses; durable outputs
are produced only by composing returned fields with SaveOp and
DataSourceManifestWriter.

### Learner protocol

```python
class Learner(Protocol):
    method: Method
    objective: Objective | None
    metrics: Mapping[str, Metric]

    def setup(self, context: TrainingContext) -> None:
        ...

    def training_step(self, batch: Batch, context: TrainingContext) -> StepOutput:
        ...

    def validation_step(self, batch: Batch, context: TrainingContext) -> StepOutput:
        ...

    def test_step(self, batch: Batch, context: PredictionContext) -> StepOutput:
        ...

    def predict_step(self, batch: Batch, context: PredictionContext) -> Batch:
        ...
```

```python
@dataclass(frozen=True)
class StepOutput:
    predictions: Sample | Batch | None
    objective: BackwardableScalar | None
    loss_terms: Mapping[str, LossTerm]
    objective_terms: Mapping[str, ObjectiveTerm] = field(default_factory=dict)
    metric_values: Mapping[str, MetricValue] = field(default_factory=dict)
    diagnostics: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[MetadataKey, Any] = field(default_factory=dict)
```

`BackwardableScalar` must avoid importing torch in core modules. Torch tensors
can satisfy it when torch is installed.

`SupervisedLearner` is the only concrete learner planned for the initial
implementation. It should remain small: `training_step` calls `Method.predict`,
evaluates the configured `Objective` to an `ObjectiveResult`, computes named
monitoring `MetricValue` or `MetricObservation` outputs, and returns
`StepOutput(predictions=prediction_batch, objective=objective_result.total,
loss_terms=objective_result.loss_terms,
objective_terms=objective_result.objective_terms,
metric_values=metric_values)`. Validation/test use the same semantic
computation under trainer-owned loop mode and gradient context. `predict_step`
calls only `Method.predict` and must work without losses or objectives.

A contrastive learner example may illustrate:

```text
Batch with declared view fields -> Method.predict -> Loss terms
  -> Objective -> MetricValue observations -> StepOutput
```

The example is documentation and contract testing guidance, not an initial
concrete learner implementation. Initial contrastive/self-supervised view
construction remains a SampleOpPipeline/SampleAugmentation concern before
collation, not a hidden batch-level view builder inside Trainer.

### Trainer protocol

The trainer should expose explicit loop entrypoints while keeping the step
semantics in the Learner:

```python
class Trainer(Protocol):
    def setup(self, plan: TrainingPlan) -> None:
        ...

    def fit(self, learner: Learner, train_data, val_data=None) -> TrainingResult:
        ...

    def validate(self, learner: Learner, val_data) -> TrainingResult:
        ...

    def test(self, learner: Learner, test_data) -> TrainingResult:
        ...

    def predict(self, method_or_learner: Method | Learner, data) -> Iterable[Batch]:
        ...
```

The `data` arguments should be framework iterables over `Batch` objects, not
datasource specs or raw indexes. Datasource indexing and Torch adapter creation
remain outside `Trainer`.

### Trainer rule

The trainer should look structurally like:

```python
for batch in train_loader:
    batch = device_mover.to_device(batch, context.device)
    set_framework_grad_enabled(context.grad_enabled)
    step_output = learner.training_step(batch, context)
    if step_output.objective is not None:
        step_output.objective.backward()
        optimizer_stepper.step(step_output, context)
```

`Trainer` constructs the loop context, moves batches through `DeviceMover`, sets
the framework gradient mode from `context.grad_enabled`, and owns
backward/optimizer stepping. `Learner` may inspect `grad_enabled` but must not
own global gradient-mode policy.

### Deliverables

```text
src/rphys/learning/context.py
src/rphys/learning/learners/base.py
src/rphys/learning/learners/supervised.py
src/rphys/learning/step_output.py
src/rphys/training/trainers/base.py
src/rphys/training/entrypoints.py
src/rphys/training/loops.py
src/rphys/training/optimization.py
src/rphys/training/checkpoints.py
src/rphys/training/distributed.py
tests/test_learning_learner_protocol.py
tests/test_supervised_learner.py
tests/test_learning_step_output.py
tests/test_trainer_loop_boundary.py
tests/test_training_runtime_specs.py
tests/test_learning_prediction_without_loss.py
tests/test_run_train_entrypoint_contract.py
```

### Definition of done

```text
Base Learner returns StepOutput with optional predictions, optional scalar
objective, named LossTerms, ObjectiveTerms, MetricValues, diagnostics, and
metadata.
Learner owns Method + Objective + Metric coupling for train/validation/test
steps.
Learner converts ObjectiveResult into StepOutput.objective,
StepOutput.loss_terms, and StepOutput.objective_terms, and converts metric
observations or summaries into StepOutput.metric_values when useful for
monitoring.
Method.predict remains loss-free.
Trainer can run fit/validate/test/predict loops over a Learner or Method without
hard-coded inputs, targets, predictions, source fields, or supervised-only
assumptions.
Trainer consumes StepOutput.objective only for backward decisions; it must not
parse Batch fields such as `loss.total`, manage metric state directly, or infer
field semantics.
OptimizerSpec, SchedulerSpec, CheckpointMetadata, DeviceMover, and
DistributedContext are typed but minimal.
SupervisedLearner works with Method + Objective + Metrics without hard-coded
field names beyond its configured selectors.
`run_train` is an experimental stage-friendly function entrypoint that delegates
to the same Trainer/Learner contracts and returns TrainingResult; it does not
define a workflow runtime or stable project configuration schema.
No concrete contrastive/self-supervised learner, concrete trainer, Lightning
adapter, or experiment framework integration is implemented in this milestone.
```

### Dependencies

```text
Milestones 9, 10, and 11.
```

---

## 17. Milestone 13: Prediction, evaluation, analysis, result datasources, and reports

### Goal

Treat model outputs, predictions, processed outputs, diagnostics, losses,
objective summaries, metric observations, and analysis inputs as normal
`Sample` or `Batch` objects that can be exported to and loaded from derived
`DataSourceRef` objects.

`evaluation` is the library counterpart to `training`, but it should remain a
thin composition layer. Metric computation, analysis, visualization, and reports
must be built from the same datasource index, sample, operation pipeline, codec,
save, grouping, metric, and loss contracts used elsewhere.

Prediction and analysis get top-level packages because they are useful library
surfaces, but both remain thin. Prediction is produced by `Method.predict`,
`Learner.predict_step`, `Trainer.predict`, or a small prediction runner; durable
prediction outputs are normal Sample/Batch fields exported through ops/export
into derived DataSourceRefs. Analysis consumes MetricResultTables, Reports,
AnalysisResults, prediction/reference Samples, and explicit diagnostics without
introducing hidden plotting side effects or a separate workflow runtime.

### Primary packages

```text
rphys.prediction
rphys.evaluation
rphys.evaluation.reports
rphys.analysis
rphys.ops.evaluation
```

### Core interfaces

```text
ResultDataSourceSpec
ResultDataSourceBuilder
ResultRecordSpec
PredictionRunner
PredictionResult
EvaluationProtocol
EvaluationPlan
EvaluationRunner
AnalysisOp
MetricOp
SampleAggregatorOp
MetricAggregatorOp
AnalysisContext
AnalysisResult
Report
ReportTable
DiagnosticRenderer
VisualizationOp
```

### Object rules

```text
Method predictions are ordinary Batch fields, not a special prediction object.
Predictions and references are ordinary fields in Samples/Batches or durable
derived DataSourceRefs. Metric and analysis outputs are MetricResultTable,
AnalysisResult, and Report objects. A downstream EvaluateStage may wrap these,
but rphys does not define an evaluation stage runtime.
Prediction helpers must not introduce rigid waveform-specific prediction sets.
They should iterate over Batch-producing data, call Method/Learner/Trainer
prediction entrypoints, attach declared metadata/provenance, and return
Samples/Batches, PredictionResult summaries, or exported DataSourceRefs.
Prediction and processed-output samples may carry metadata describing their
origin, role, source datasource id, source record id, method id, run id, and
provenance.
Durable predictions are exported by SaveOp and DataSourceManifestWriter from
Milestone 8, producing a derived DataSourceRef that can be scanned, indexed,
filtered, grouped, loaded, and analyzed like any other datasource.
AnalysisOp and VisualizationOp consume loaded Samples, Batches, MetricResultTable
objects, or Report objects and return typed AnalysisResult or Report values.
Analysis interprets MetricResultTables, Reports, AnalysisResults,
prediction/reference Samples, and explicit diagnostics. It must not train
models, select checkpoints, mutate predictions, discover ad hoc log files, or
write plot files outside report/export contracts.
MetricOp adapts a Metric contract into a pipeline operation where useful, but
the Metric itself remains independent of filesystem writes, plotting, training,
and datasource scanning.
Report and DiagnosticRenderer interfaces are structured output contracts. They
must not discover files by path assumption or mutate datasource objects.
EvaluationRunner, if implemented, is only a thin loop over existing indexes,
SampleBuilder, SampleOpPipeline, MetricOps, and report builders. It must not
own datasource scanning, split construction, training losses, codec logic,
or custom report file conventions.
Top-level `rphys.analysis` should mostly re-export or organize structured
analysis operations, result tables, diagnostics, and report builders. It should
not become a notebook automation layer, ad hoc log-file crawler, or plotting
side-effect system.
Generic artifact graph execution, artifact registries, stage scheduling, and
cross-project workflow lifecycle belong to loom or downstream orchestration.
```

Evaluation compares prediction and reference field containers under an explicit
protocol. `EvaluationProtocol` is the scientific contract: which prediction and
reference fields are compared, which grouping metadata define records,
subjects, datasources, and splits, whether predictions are aggregated before
metrics, which metrics run per sample/window/record/group, and how metric rows
are aggregated into reports. `EvaluationPlan` is the executable form of that
protocol for a concrete datasource/index/run. `EvaluationRunner`, if present,
is only a thin loop over the plan and existing operations.

Evaluation may run over loaded Samples/Batches or exported derived
DataSourceRefs, and may include prediction aggregation, record reconstruction,
metric computation, and metric aggregation. `EvaluationProtocol` /
`EvaluationPlan` / `EvaluationRunner` may compose Method/Learner-produced
predictions or loaded prediction samples with postprocessing, MetricOps,
aggregators, analysis, and reports. This should not become a broad public
evaluator runtime separate from the existing operation, metric, datasource, and
report contracts.

### Reusable flow

```text
training/testing/inference code produces Sample or Batch predictions
  -> SampleOpPipeline attaches metadata or applies formatting operations
  -> CodecSelectionOp chooses field codecs
  -> SaveOp writes fields through FieldCodec.save
  -> DataSourceManifestWriter emits derived DataSourceRef
  -> DataSourceAdapter/IndexBuilder reuses the same datasource machinery
  -> SampleOpPipeline or OperationPipeline applies metrics, grouping, analysis, or rendering
```

### Deliverables

```text
src/rphys/prediction/core.py
src/rphys/prediction/runner.py
src/rphys/prediction/results.py
src/rphys/evaluation/core.py
src/rphys/evaluation/protocols.py
src/rphys/evaluation/runner.py
src/rphys/evaluation/results.py
src/rphys/evaluation/reports.py
src/rphys/analysis/core.py
src/rphys/analysis/reports.py
src/rphys/analysis/diagnostics.py
src/rphys/ops/evaluation/metrics.py
src/rphys/ops/evaluation/analysis.py
tests/test_predictions_as_samples.py
tests/test_prediction_runner_contract.py
tests/test_prediction_export_datasource_roundtrip.py
tests/test_evaluation_protocol_contract.py
tests/test_evaluation_pipeline_contract.py
tests/test_analysis_contracts.py
tests/test_report_contracts.py
```

### Definition of done

```text
Prediction Samples can be exported as a derived DataSourceRef and loaded again
through the normal SampleBuilder path.
Prediction helpers return field containers or typed summaries, not rigid
prediction-set objects.
Analysis and metric operations can run over loaded prediction/reference samples
without a standalone scoring runtime.
EvaluationProtocol records prediction/reference field selectors, grouping,
pre-metric sample aggregation, metric computation, post-metric aggregation, and
report requirements without owning datasource scanning or workflow execution.
Report and visualization objects return structured results and never write
ad hoc files from loaded sample attributes.
EvaluationRunner and PredictionRunner are optional and thin; no
prediction-specific datasource, alternate metric runtime, or workflow-specific
analysis machinery is introduced.
```

### Dependencies

```text
Milestones 5, 7, 8, 10, and 11.
```

---

## 18. Milestone 14: Root test scaffold and synthetic fixtures

### Goal

Create the test structure, synthetic fixtures, and reusable contract helpers
needed to keep the object model scientifically and architecturally stable as
the library grows.

Testing support should live under the repository-level `tests/` tree for now.
Do not add a public testing-helper package until there is a clear downstream
need and the helper API has stabilized.

### Primary locations

```text
tests/
tests/support/
tests/unit/
tests/contract/
tests/integration/
tests/end_to_end/
```

### Core testing support

```text
SyntheticDataSourceSpec
SyntheticDataSourceFactory
SyntheticFieldFactory
SyntheticWaveformFactory
SyntheticResourceFactory
SyntheticFixtureManifest
ContractCase
ContractSuite
ContractViolation
PublicApiImportCheck
DeterminismCheck
ScientificEdgeCaseMatrix
```

### Synthetic fixture requirements

```text
Synthetic fixtures are declarative and license-safe.
They must not require external data, network access, GPUs, or large binary
artifacts.

Required fixture capabilities:
  multiple datasources, records, subjects, and groups
  stable datasource_id, record_id, subject_id, split, and group metadata
  tiny deterministic video-like arrays
  waveform fields with known frequency, phase, amplitude, and optional heart rate
  timestamp fields with configurable rates, offsets, drift, and irregularity
  optional landmarks, masks, quality fields, metadata sidecars, and compound fields
  missing-field, short-record, flat-signal, NaN, inf, invalid-rate, and
  misalignment variants
  URI-based ResourceRefs to avoid local Path lock-in
  tiny manifests for codec, export, and derived datasource round trips
```

### Deliverables

```text
tests/support/synthetic_datasources.py
tests/support/synthetic_fields.py
tests/support/synthetic_waveforms.py
tests/support/contracts.py
tests/support/assertions.py
tests/support/public_api.py
tests/support/scientific_edges.py
tests/unit/test_testing_support.py
tests/contract/test_contract_helpers.py
```

### Definition of done

```text
The tests tree has clear unit, contract, integration, and end-to-end locations.
Synthetic fixture factories can produce DataSourceRefs, RecordRefs, FieldRefs,
IndexItems, lazy Samples, Batches, exported DataSourceRefs, and basic result
Samples without real data.
Fixture manifests record expected keys, schemas, metadata, resources, indexes,
known edge cases, and seed material.
Contract helpers are private to tests and import only public rphys APIs.
```

### Dependencies

```text
Milestones 0-5, with continued expansion as later milestones land.
```

---

## 19. Milestone 15: Contract, integration, and smoke hardening

### Goal

Harden the public object model and data-flow contracts with focused tests,
synthetic integration flows, smoke pipelines, CI tiers, public API checks, and
scientific edge-case coverage.

This milestone should make it difficult for future work to regress into hidden
string parsing, eager IO, datasource/model coupling, ad hoc export paths,
global RNG, private API imports, or experiment orchestration inside the base
library.

### Test layers

```text
Unit tests
  DataKey, FieldLocator, MetadataKey, SchemaName, errors, ResourceRef,
  FieldSpec, FieldRef, FieldView, FieldIndex, TemporalIndexSlice, FieldValue, SampleField,
  Sample, Batch, CollatePolicy, ops specs, operation contexts, losses,
  objectives, metrics, reports, and result objects.

Contract tests
  DataSourceAdapter, DataSourceViewBuilder, SplitBuilder, IndexBuilder,
  DataSourceIndex, composite index, index manifest, FieldCodec, SampleBuilder,
  Operation, Transform, OperationPipeline, SampleOp, SampleTransform,
  SampleAugmentation, SampleCheck, SampleOpPipeline, CodecSelectionOp, SaveOp,
  DataSourceManifestWriter, TorchIndexSampleDataset, CacheStore, Method, Model,
  MethodInputAdapter, MethodOutputAdapter, Loss, Objective, Metric, Learner,
  SupervisedLearner, Trainer boundary, PredictionRunner, EvaluationRunner,
  AnalysisOp, and Report.

Synthetic integration tests
  DataSourceSpec -> DataSourceAdapter.scan -> DataSourceRef/RecordRef/FieldRef
  -> DataSourceView/Split -> IndexBuilder -> DataSourceIndex
  -> SampleBuilder -> SampleOpPipeline -> Batch.

Export and analysis integration tests
  DataSourceView + DataSourceIndex -> SampleBuilder -> SampleOpPipeline -> SaveOp
  -> derived DataSourceRef -> TorchIndexSampleDataset -> prediction Batches
  -> MetricOp/AnalysisOp -> Report.

Smoke operation-pipeline tests
  Synthetic scan -> split -> index manifest -> dataloader -> Method.predict or
  tiny learner/trainer boundary -> export predictions -> reload predictions
  -> metric table/report. The default smoke path must run on CPU, without
  external data, network, or heavy optional dependencies.
```

### Contract test expectations

```text
Selectors are parsed at construction, not inside runtime loops.
Refs, views, specs, and manifests serialize without open file handles or loaded
payload arrays.
FieldRef does not own a temporal slice; FieldView imposes additional access
behavior.
FieldSpec stays minimal and modality-specific assumptions are explicit.
SampleBuilder can probe or build only requested fields and keeps IO lazy until
field access where practical.
DataSourceAdapter scanning is separate from Torch dataset item loading.
Save/export flows use FieldCodec save support and emit derived DataSourceRefs.
Operation and OperationPipeline contexts control deterministic stochastic behavior.
Collation behavior is limited to stack, list, or custom policy initially.
Losses, objectives, metrics, methods, and trainers do not scan datasources or
write files.
Cache behavior is explicit, provenance-aware, invalidation-aware, and rank-safe
in distributed contexts.
```

### Scientific hardening matrix

```text
Maintain an explicit edge-case matrix for datasources, codecs, SampleBuilder,
pipelines, ops, losses, objectives, metrics, export, evaluation, and training
boundaries.

The matrix should cover NaNs, infinities, flat signals, all-zero masks, empty
masks, short windows, uneven timestamps, duplicate timestamps, missing frames,
invalid sampling rates, mismatched temporal grids, subject leakage, missing
targets, missing predictions, CPU/GPU dtype/device mismatch where applicable,
non-contiguous tensors, dtype promotion, gradient/backward checks for
differentiable components, deterministic replay, distributed worker seeds, and
cache invalidation behavior.
```

### CI tiers

```text
Fast tier
  Pure Python unit and contract tests on CPU with synthetic fixtures.

Smoke tier
  End-to-end synthetic operation pipeline on CPU, including scan, split, index, lazy load,
  operation pipeline, collate, prediction or tiny training boundary, export, reload,
  metric table, and report.

Optional dependency tier
  Tests requiring torch, video/image libraries, HDF5, optional codecs, or
  framework adapters. These skip clearly when dependencies are missing.

Slow/research tier
  Larger numerical parity, gradient, stress, or distributed cache tests. These
  should not be the default gate for small core changes.

Public API tier
  Import-boundary checks, public API snapshots, documentation examples that are
  in scope, and unstable/deprecation marker checks.
```

### Definition of done

```text
CI runs core unit, contract, and smoke tests.
Reusable synthetic fixtures cover the core flow from DataKey/FieldLocator
through DataSourceRef, IndexItem, lazy Sample, Batch, SaveOp-derived
DataSourceRef, prediction Batch, MetricResultTable, AnalysisResult, and Report.
Determinism tests cover split construction, worker context, SampleOpPipeline
augmentation replay, export layout/idempotency, metric grouping, and optional
cache behavior.
Scientific edge-case tests cover NaNs, flat signals, short inputs, missing
fields, invalid sampling rates, temporal misalignment, dtype/device mismatch,
and leakage-prone splits.
Public API/import checks ensure tests and documentation examples do not import
private rphys internals.
No root-level smoke path depends on external workflow tooling, real data,
network access, or private project code.
```

### Dependencies

```text
All earlier milestones, but tests should be developed continuously.
```

---

## 20. Critical path dependency graph

The implementation critical path is:

```text
M0 Package and docs skeleton
  -> M1 Keys, locators, schemas, errors
    -> M2 Field refs, field views, datasource refs, index item structure
      -> M3 SampleField, FieldValue, Sample, Batch, collation
        -> M4 Codecs and lazy Sample construction
          -> M5 DataSource adapters, views, splits, indexes
            -> M9 DataSourceIndex adapters, Torch datasets, and cache
              -> M10 Method/model base contracts
              -> M11 Loss/objective/metric base contracts
              -> M12 Learner/trainer base contracts
                -> M13 Prediction, evaluation, analysis, result datasources, and reports
                  -> M15 Contract, integration, and smoke hardening

M6 Operation foundations and functional kernels
  -> M7 Operation, Transform, SampleOp, and operation pipeline bases
    -> M8 Save/export ops and derived datasource generation
      -> M13 Evaluation and result datasource flows
```

Parallelizable work after the core contracts are stable:

```text
Testing support can grow alongside every milestone.
Minimal ops specs can proceed alongside datasource adapter work.
Operation pipeline bases can proceed once Sample and lazy access semantics are stable.
Export ops can proceed once codecs and SampleOpPipeline are stable.
Learning/training base contracts can proceed once Batch, prediction-field,
LossResult, ObjectiveResult, MetricValue, and MetricResultTable shapes are clear.
Concrete datasources, models, methods, metrics, and losses should wait until
the base contracts and synthetic fixtures are stable.
```

---

## 21. Implementation backlog by workstream

### Core data contracts workstream

```text
Implement DataKey, FieldLocator, MetadataKey, SchemaName, and typed errors.
Implement ResourceRef with URI/protocol/storage_options rather than local paths.
Implement minimal FieldSpec.
Implement FieldRef without temporal slicing.
Implement FieldView as imposed access behavior over a FieldRef.
Implement DataSourceRef, RecordRef, DataSourceSchema, and IndexItem.
Implement SampleField, FieldValue, Sample, Batch, and stack/list/custom
collation.
Defer generic axis, layout, temporal-grid, frequency-grid, coordinate-frame,
graph, and geometry metadata specs until concrete components require them.
```

### IO workstream

```text
Implement FieldCodec protocol.
Implement CodecRegistry.
Implement LoadContext, SaveContext, CodecSaveResult, and codec capability checks.
Implement lazy SampleField construction through SampleBuilder.
Implement compound-field loading from one or more ResourceRefs.
Implement codec save support used by SaveOp.
Implement MetadataSavePolicy for manifest metadata versus metadata fields.
```

### Datasource workstream

```text
Implement DataSourceSpec and DataSourceAdapter protocol.
Implement DataSourceValidationReport and DataSourceViewBuilder.
Implement minimal Filter, FilterChain, FilterResult, group resolvers,
SplitPlan/SplitBuilder/Split, and IndexPlan/IndexBuilder/DataSourceIndex.
Implement index manifest export/import.
Implement CompositeDataSourceIndex and deterministic child source maps.
Implement a synthetic DataSourceAdapter before any real datasource adapter.
Design ResourceRefs so remote stores such as S3 are possible later without
changing the object model.
```

### Ops workstream

```text
Implement Operation, Transform, OperationPipeline, OperationContext, and PipelineContext.
Implement SampleOp, SampleTransform, SampleAugmentation, SampleCheck, and
SampleOpPipeline.
Implement rphys.ops.functional for pure reusable kernels.
Implement deterministic stochastic behavior through explicit context and seed
material.
Implement sample filtering/routing operations only as base contracts.
Keep concrete model-specific, method-specific, and heavy preprocessing ops out
of the initial implementation.
```

### Export workstream

```text
Implement ExportSpec, OutputLayout, ExportPolicy, CodecSelectionOp, SaveOp,
FieldExportResult, RecordExportResult, ExportReport, DataSourceManifestWriter,
and DerivedDataSourceBuilder.
Treat export as a final SampleOp/OperationPipeline operation that writes through codecs
and emits a new DataSourceRef.
Do not create a separate offline-output module or datasource-specific formatting
subsystem.
```

### Index, Torch adapter, and cache workstream

```text
Implement DataSourceIndex protocol over arbitrary index storage.
Implement TorchIndexSampleDataset over DataSourceIndex.
Implement PipelineIndexSampleDataset only as a thin wrapper that applies
SampleOpPipeline after SampleBuilder.
Implement BatchCollater, TorchDataLoaderPlan, WorkerContextFactory, and
SampleRuntimeContext.
Keep scanning, split construction, and index construction out of __getitem__.
Implement CachePolicy, CacheKey, CacheStore, CacheContext, and
DistributedCacheCoordinator with atomic commit and fingerprint invalidation.
```

### Learning and training contracts workstream

```text
Implement Method, Model, MethodInputAdapter, MethodOutputAdapter, MethodOutput,
and lightweight rphys.nn namespace.
Implement Loss, LossResult, LossTerm, Objective, ObjectiveResult,
ObjectiveTerm, Metric, MetricObservation, MetricResultTable, GroupBySpec, and
MetricAggregator.
Implement Learner, SupervisedLearner, StepOutput, LoopMode, LoopContext,
TrainingContext, and PredictionContext under rphys.learning.
Implement Trainer, TrainingPlan, TrainingResult, DeviceMover, OptimizerSpec,
SchedulerSpec, CheckpointMetadata, and DistributedContext under rphys.training.
Add experimental `run_train` only as a thin function entrypoint over the same
training contracts; keep its argument schema flexible until loom integration
needs are concrete.
Do not implement concrete CHROM/POS methods, neural baselines, losses,
objectives, metrics, or non-supervised learners in the initial roadmap.
```

### Evaluation workstream

```text
Represent predictions and processed outputs as Samples or Batches.
Export prediction Samples through SaveOp into derived DataSourceRefs.
Implement thin rphys.prediction helpers without rigid prediction-set objects.
Reload and analyze prediction/reference samples through normal datasource and
operation pipeline machinery.
Implement rphys.analysis/evaluation analysis and report base objects without a
separate scoring runtime.
```

### Testing workstream

```text
Build tests/support synthetic fixtures and contract helpers.
Add unit tests as each base object lands.
Add contract tests for each public protocol.
Add synthetic integration and smoke tests once DataSourceRef -> Sample -> Batch
and export round trips exist.
Add public API/import-boundary checks before stabilizing.
```

---

## 22. Core design decisions to lock before large implementation

These decisions should be finalized before concrete implementations proliferate.

```text
1. DataKey grammar and reserved namespaces.
2. Key, locator, schema, and metadata primitives live under rphys.data, not a
   generic shared-naming package.
3. DataSourceRef -> RecordRef -> FieldRef -> FieldView -> IndexItem behavior.
4. FieldRef does not include a FieldIndex by default.
5. FieldView inherits or wraps FieldRef semantics and imposes slice/access
   behavior explicitly.
6. FieldSpec contains only minimum common metadata; modality-specific temporal,
   rate, coordinate, and shape assumptions require explicit specs/classes.
7. ResourceRef is URI/protocol oriented and can represent remote storage later.
   It is not an ArtifactRef, stage output handle, artifact-store object, or
   workflow lifecycle primitive.
8. Sample is an arbitrary container with typed access interfaces, not a fixed
   video/signal object.
9. SampleBuilder creates SampleFields and should keep IO lazy until
   SampleField payload access.
10. Collation starts with stack, list, and custom only.
11. Filters use a minimal composable Filter/FilterChain contract. Payload
    dependent decisions are SampleOps that annotate, drop, or route samples.
12. DataSourceIndex is the standard index protocol; composite/chained indexes
    combine multiple underlying datasources without changing Torch adapters.
13. Operation, Transform, SampleOp, and OperationPipeline are separate enough to
    express non-transforming operations such as save/export, checks, filters,
    evaluation, analysis, and visualization.
    Batch-level composition uses Operation[Batch, Batch] initially; no public
    BatchOperator, BatchProgram, or BatchOpPipeline is part of the first pass.
14. Pure functional kernels live in functional modules and are wrapped by
    Operation classes only when contracts/context/provenance are needed.
15. Augmentation is a stochastic Transform with explicit context and seed
    control.
16. Export is a codec-backed SampleOp/OperationPipeline concern, not datasource scanning
    or a separate offline-output subsystem.
17. Metadata persistence is explicit: small manifest metadata is saved by
    DataSourceManifestWriter, while structured metadata that needs loading or
    transformation is a normal field saved through a codec.
18. Predictions, processed outputs, and analysis inputs are Samples/Batches with
    metadata and can be exported as derived DataSourceRefs.
19. Method, Model, Loss, Objective, Metric, Learner, and Trainer are distinct
    contracts and should be milestone-separated.
    Loss means differentiable error/penalty terms. Objective means the
    optimizer-facing aggregation of losses plus all other optimizer-relevant
    terms.
20. Learner couples Method + Objective + Metrics for training/evaluation steps;
    Method.predict remains loss-free and objective-free, and Trainer stays
    loop-focused.
21. SupervisedLearner is the only concrete learner planned initially; other
    learning styles remain design patterns and contract tests until needed.
22. Prediction and analysis can be top-level packages, but they remain thin
    helpers over field containers, result datasources, metrics, reports, and
    operation pipelines.
23. EvaluationProtocol names the scientific comparison contract: prediction and
    reference selectors, grouping, pre-metric sample aggregation, metric
    computation, post-metric aggregation, and reporting. EvaluationRunner, if
    implemented, is only a thin executor of that contract over existing
    datasource, operation, metric, analysis, and report contracts.
24. DDP-safe caching is explicit, provenance-aware, and invalidation-aware.
25. No generic Stage, ArtifactRef, ArtifactContract, StageContext, artifact
    store, project configuration, workflow-engine, project-template, or
    workflow-phase package belongs in the base library roadmap. rphys domain
    contracts should remain serializable and provenance-rich so loom/downstream
    projects can wrap them.
26. Registries are used only where symbolic names are genuinely needed.
27. Public API means documented and tested extension contracts, not every helper
    listed in implementation deliverables.
28. Modality shape conventions, coordinate frames, units, sampling rates,
    dtype/device expectations, and validity-mask semantics must be documented
    before concrete modality implementations are treated as stable.
29. Optional dependency extras and import boundaries are part of the API
    contract, not packaging afterthoughts.
```

### Notes-to-roadmap mapping

| Notes term | Roadmap decision |
| --- | --- |
| `Field` | `FieldValue`, `SampleField`, `FieldRef`, `FieldView`, and role-qualified `FieldLocator`, depending on whether the context is runtime, reference, or loaded payload. |
| `Batch` | `Batch` remains the collated runtime field container; `Sample` remains the per-item lazy runtime field container. Both can carry inputs, predictions, losses, objective terms, metrics, diagnostics, and provenance. |
| `BatchOperator` | Use `Operation[Batch, Batch]` initially. Add a public batch-specialized alias only when repeated code needs it. |
| `BatchProgram` | Use `OperationPipeline` and semantic objects (`Method`, `Loss`, `Objective`, `Metric`, `Learner`) rather than a separate public program class. |
| `Objective / Loss` | `Loss` computes differentiable error/penalty terms. `Objective` combines losses with regularization, constraints, schedules, and auxiliary optimizer terms into the scalar used by the optimizer. |
| `Metric` | Detached measurement contract producing observations/tables and optional declared metric fields; never the optimizer target. |
| `Method` | Batch-level prediction or representation algorithm that adapts fields into models/kernels and returns prediction/output fields. |
| `Model` | Lower-level tensor or structured-input computation, not a Method by inheritance. |
| `Learner` | Owns step semantics and composes Method + Objective + Metrics. |
| `Trainer` | Owns loop/runtime mechanics and backpropagates `StepOutput.objective`. |
| `Evaluator` | `EvaluationProtocol` for the scientific comparison contract plus a thin `EvaluationRunner` and metric/report operations, not a broad alternate runtime. |
| `Analyzer` | Top-level `rphys.analysis` helpers and `AnalysisOp`/`Report` contracts without hidden file or plotting side effects. |
| `Prediction` package | Top-level `rphys.prediction` is allowed as thin runners/helpers over prediction fields and export, not rigid prediction-set objects. |
| `Stage` / `ArtifactRef` | Excluded from core rphys. rphys remains stage-friendly through serializable plans/results and callable entrypoints such as experimental `run_train`. |

### Abstraction simplification rules

Use these rules when implementation pressure creates a new class name:

```text
Prefer Operation over a new callable base when the signature and lifecycle are
the same.
Prefer FieldLocator and selector specs over separate input-adapter classes for
Loss, Objective, and Metric unless an external framework adapter needs code.
Prefer Objective over CompositeLoss for aggregating weighted loss terms into an
optimizer scalar.
Prefer typed result objects over manager classes that only hold the same data.
Prefer Sample/Batch fields over rigid prediction/loss/metric containers when
field-shaped runtime composition is enough.
Prefer top-level prediction/analysis helpers only when they remove repeated
caller code without introducing alternate data containers or hidden workflows.
Add a semantic class only when it changes lifecycle rules, side effects,
scientific contracts, mutability, optimizer semantics, aggregation behavior, or
artifact boundaries.
```

---

## 23. Decisions that can be deferred

These should not block implementation of the core architecture.

```text
Exact full list of codecs.
Spatial slices.
Time-based slices.
Nested multi-view Sample representation.
Multi-member IndexItems for advanced contrastive sampling.
Full mesh, point-cloud, bounding-box, segmentation-mask, or renderer libraries.
Concrete preprocessing operations such as landmark detection or rPPG algorithms.
Concrete CHROM/POS methods, neural baselines, model zoo, losses, and metrics.
Large library of self-supervised learners.
Plugin discovery through Python entry points.
Public testing-helper package.
Advanced cache backends beyond the initial DDP-safe CacheStore contract.
Broad optimizer/scheduler factory library.
Framework-specific distributed, accelerator, profiler, and logger adapters.
Project configuration systems, workflow engines, and CLIs.
Extension guides, worked examples, and downstream template projects.
Advanced publication/report generation.
Advanced UI/dashboard tooling.
```

The architecture should leave room for these, but they do not need to be solved
before the core package is useful.

---

## 24. Recommended initial implementation order within each milestone

A practical development order is:

```text
1. Define interfaces as dataclasses/protocols with minimal behavior.
2. Write narrow unit or contract tests for expected behavior.
3. Add synthetic fixtures before concrete research functionality.
4. Add lazy/probe paths before eager convenience behavior.
5. Add one small integration flow before expanding options.
6. Document the scientific contract for public behavior as it stabilizes.
7. Defer concrete algorithms, real datasources, and training templates until the
   base object model is proven.
```

This avoids debugging datasource-specific or trainer-specific issues before the
core public contracts are tested.

---

## 25. Example end-to-end implementation target

The first complete vertical slice should be synthetic but architecturally
representative.

```text
SyntheticDataSourceAdapter
  -> DataSourceRef with RecordRefs and FieldRefs
  -> metadata/probe-based filters and split
  -> IndexBuilder creates DataSourceIndex with IndexItems and FieldViews
  -> index manifest export/import
  -> TorchIndexSampleDataset uses SampleBuilder to create lazy Samples
  -> SampleOpPipeline applies a simple deterministic SampleOp
  -> BatchCollater creates Batch
  -> trivial base Method test returns a prediction Batch
  -> SaveOp exports predictions into a derived DataSourceRef
  -> derived DataSourceRef is reloaded and analyzed by MetricOp/AnalysisOp
```

Success means the architecture works end to end without relying on a real
real datasource, concrete rPPG algorithm, trainer, workflow engine, or project
configuration.

---

## 26. Real datasource integration sequence

After the synthetic flow works, add real datasources in this order:

```text
1. Choose the simplest datasource with video-like data and a reference signal.
2. Implement DataSourceAdapter that emits DataSourceRef/RecordRef/FieldRef only.
3. Implement or reuse codecs needed by the adapter.
4. Add validation reports for missing files, metadata, and sidecars.
5. Add official or subject-disjoint split support through DataSourceViewBuilder.
6. Add index construction using explicit FieldView/FieldIndex behavior.
7. Add smoke tests that load a tiny license-safe subset or synthetic equivalent.
8. Add export only through SaveOp and DataSourceManifestWriter.
```

Do not start by implementing a full preprocessing pipeline for the datasource.
First make it discoverable, referenceable, indexable, and lazily loadable.

---

## 27. Export and derived datasource implementation sequence

Save/export should be added after lazy loading and SampleOpPipeline are stable.

```text
1. Implement OutputLayout and ExportSpec.
2. Implement CodecSelectionOp that annotates fields with intended codecs.
3. Implement FieldCodec.save for one simple field type.
4. Implement SaveOp over Samples.
5. Emit FieldExportResults and RecordExportResults.
6. Emit new FieldRefs, RecordRefs, and a derived DataSourceRef.
7. Export and reload an index manifest for the derived datasource.
8. Add deterministic export layout, idempotency, and provenance tests.
```

This supports formatting as:

```text
load or lazily reference field -> optionally apply SampleOps -> choose codec
  -> save field -> emit new references -> build derived datasource
```

without embedding formatting logic inside datasource adapters.

---

## 28. Self-supervised and contrastive implementation path

For the first implementation, do not add complex multi-member index items.

Use wide-window loading:

```text
IndexBuilder creates a wider TemporalIndexSlice FieldIndex.
SampleBuilder creates a lazy Sample for that wider window.
SampleOpPipeline applies SampleAugmentation that loads when needed and writes
declared subview locators.
Learner consumes those view fields.
```

For initial contrastive/self-supervised support, view construction is a
SampleOpPipeline concern, usually implemented by one or more SampleAugmentation
ops that read a wide-window Sample and write declared view FieldLocators such as
inputs/video.rgb.view_a and inputs/video.rgb.view_b. Learners consume those view
fields after collation; they do not build IndexItems or hide view sampling
inside Trainer. Contrastive training remains a design pattern initially:
contrastive losses return named LossTerms, an Objective combines those terms
with any weights or regularization, and StepOutput.objective receives the scalar
optimization value. StepOutput.loss_terms, objective_terms, and metric_values
carry structured results.

Implementation sequence, when this becomes in scope:

```text
1. Implement a deterministic temporal crop SampleAugmentation.
2. Implement a two-view crop that writes declared output locators with view
   qualifiers, such as inputs/video.rgb.view_a and inputs/video.rgb.view_b.
3. Implement learner tests around those fields without changing IndexItem.
4. Later, consider nested view Samples or multi-member IndexItems if needed.
```

This keeps lazy IO separate from self-supervised learning logic.

---

## 29. Anti-patterns to avoid during implementation

```text
Do not let a PyTorch Dataset scan raw directories.
Do not put formatting under datasource adapters.
Do not add a separate offline-output subsystem.
Do not let IndexItem contain transforms or augmentations.
Do not build contrastive/self-supervised views as ad hoc BatchOperators after
collation when per-sample RNG, provenance, caching, or lazy loading matters.
Do not silently load full files when a slice is unsupported.
Do not silently pad or truncate during collation.
Do not hard-code video as a special Sample attribute.
Do not put concrete CHROM/POS, landmark detection, or model-specific ops into
the base operation layer.
Do not put optimizer, scheduler, checkpoint, distributed, or profiler behavior
inside Model or Method objects.
Do not put learning-style logic inside Trainer or datasource logic inside
Learner.
Do not let Method, Learner, Trainer, Loss, Objective, or Metric write
prediction/test artifacts implicitly; durable outputs must go through explicit
export/report contracts.
Do not make Prediction objects fixed to waveform/heart-rate only.
Do not require users to edit rphys internals for custom datasources, codecs,
ops, methods, losses, objectives, or metrics.
Do not let visualization or analysis code write ad hoc files from loaded attrs;
route durable artifacts through SaveOp, evaluation reports, or explicit user code.
Do not add implicit caches. Cache behavior must be explicit, provenance-aware,
rank-safe, and invalidation-aware.
Do not introduce project-level configuration or workflow orchestration inside
the base library.
Do not add generic Stage, ArtifactRef, ArtifactContract, BatchProgram, or
universal BatchOperator APIs to rphys before concrete repeated library needs
justify them.
```

---

## 30. Documentation deliverables

Documentation should be implemented as part of the roadmap, but keep it focused
on feature design and public contracts. Full step-by-step extension guides and
worked examples are deferred until the relevant public contracts exist, but the
feature docs should still identify the extension surface, required protocols,
serializability rules, field-key expectations, contract declarations, tests, and
common anti-patterns for each area.

Recommended docs tree:

```text
docs/
  rphys_implementation_roadmap_v1.md
  architecture.md
  public_api.md
  features/
    data_keys_and_locators.md
    datasource_refs_and_indexing.md
    samples_batches_and_collation.md
    lazy_io_and_codecs.md
    operations_transforms_and_pipelines.md
    export_and_derived_datasources.md
    methods_models_and_outputs.md
    losses_objectives_metrics_and_evaluation.md
    learners_trainers_and_runtime_boundaries.md
    prediction_and_analysis.md
    indexes_torch_adapters_and_cache.md
    testing_and_synthetic_fixtures.md
```

Each feature document should explain the design principle, object boundaries,
scientific contract, failure behavior, and what is intentionally out of scope.
When a feature document describes an extension point, it should also state which
protocol/base class to implement, which methods are required, what must be
serializable, how to declare field and metadata selectors, what tests establish
the contract, and which responsibilities belong to loom or downstream projects.

---

## 31. Public API checklist

Before declaring the first stable package release, ensure these are documented
and tested:

```text
DataKey
FieldLocator
MetadataKey
SchemaName
ResourceRef
FieldSpec
MetadataSpec
FieldRef
TemporalIndexSlice
FieldIndex
FieldView
DataSourceRef
RecordRef
DataSourceSchema
DataSourceViewPlan
DataSourceView
DataSourceViewResult
Filter
FilterPlan
FilterChain
FilterResult
GroupPlan
GroupBuilder
GroupResult
SplitPlan
SplitBuilder
Split
SplitResult
IndexPlan
IndexBuilder
DataSourceIndex
DataSourceIndexCodec
DataSourceIndexManifest
CompositeDataSourceIndex
IndexItem
SampleField
FieldValue
Sample
Batch
CollatePolicy
SampleContract
FieldCodec
CodecRegistry
LoadContext
SaveContext
IOContext
CodecSaveResult
SampleBuilder
DataSourceSpec
DataSourceAdapter
DataSourceValidationReport
Operation
OperationRole
Transform
OperationPipeline
OperationContext
PipelineContext
SampleOp
SampleTransform
SampleAugmentation
SampleCheck
SampleOpPipeline
ExportSpec
OutputLayout
ExportPolicy
CodecSelectionOp
SaveOp
FieldExportResult
RecordExportResult
ExportReport
DataSourceManifestWriter
TorchIndexSampleDataset
PipelineIndexSampleDataset
BatchCollater
TorchDataLoaderPlan
WorkerContextFactory
SampleRuntimeContext
CachePolicy
CacheKey
CacheStore
CacheContext
DistributedCacheCoordinator
Method
Model
MethodInputAdapter
MethodOutputAdapter
MethodOutput
StatefulMethod
TrainableMethod
Measure
MetricInputSpec
MetricContract
Metric
MetricValue
MetricObservation
MetricResultTable
MetricContext
MetricAggregationPlan
MetricAggregator
Loss
LossInputSpec
LossContract
LossContext
LossTerm
LossResult
Objective
ObjectiveInputSpec
ObjectiveContract
ObjectiveContext
ObjectiveTerm
ObjectiveResult
CompositeObjective
Learner
SupervisedLearner
StepOutput
LoopMode
LoopContext
TrainingContext
PredictionContext
BackwardableScalar
Trainer
TrainingPlan
TrainingResult
run_train, experimental
OptimizerSpec
SchedulerSpec
CheckpointMetadata
DistributedContext
PredictionRunner
PredictionResult
EvaluationProtocol
EvaluationPlan
EvaluationRunner
AnalysisOp
AnalysisResult
Report
ReportTable
DiagnosticRenderer
SyntheticDataSourceSpec
```

---

## 32. Release readiness gates

### Internal alpha gate

```text
Core data contracts implemented.
Field-versus-metadata rule is documented in public API docs.
Synthetic DataSourceRef can be indexed and serialized as an index manifest.
SampleBuilder can create Samples with lazy SampleFields and load requested fields on access.
SampleOpPipeline can apply deterministic SampleOps.
Collate produces Batch using stack/list/custom policies.
Basic unit and contract tests pass.
```

### Developer alpha gate

```text
Synthetic end-to-end library flow works without real data.
SaveOp can export a derived DataSourceRef and reload it.
Base Method, Loss, Objective, Metric, Learner, SupervisedLearner, and Trainer
contracts have tests.
Feature docs exist for datasource, sample, lazy IO, operation pipeline, export, and
learning boundaries.
```

### Research-use beta gate

```text
At least one real datasource adapter works with license-safe or externally
provided data.
Subject-disjoint split and index construction work.
Export works for at least one common field format through codecs.
Prediction fields/Samples can be exported, reloaded, grouped, and scored by metrics.
Synthetic smoke pipeline runs in CI.
```

### Stable public API gate

```text
Public contracts have tests and documentation.
Core behavior is strict and predictable.
Deprecation and experimental API policy exists.
Public API/import-boundary checks pass.
Optional dependency extras and import boundaries are documented and tested.
Stable public API excludes undocumented deep helpers by default.
Scientific edge-case coverage is documented.
```

---

## 33. Recommended immediate next actions

The next implementation actions should be:

```text
1. Create the package skeleton and docs/features skeleton.
2. Implement DataKey, FieldLocator, MetadataKey, SchemaName, and error classes.
3. Implement ResourceRef, FieldSpec, FieldRef, FieldIndex, TemporalIndexSlice, FieldView,
   DataSourceRef, RecordRef, and IndexItem.
4. Implement SampleField, FieldValue, Sample, Batch, and CollatePolicy.
5. Implement FieldCodec protocol, CodecRegistry, LoadContext, SaveContext, and
   SampleBuilder with probe/subset/lazy behavior.
6. Implement synthetic DataSourceAdapter, DataSourceViewBuilder, SplitBuilder,
   IndexBuilder, DataSourceIndex, and index manifest round trip.
7. Implement Operation, Transform, SampleOp, SampleOpPipeline, and deterministic
   context behavior.
8. Implement explicit CachePolicy/CacheStore basics and DDP-safe cache commit
   semantics.
9. Implement SaveOp and derived DataSourceRef round trip.
10. Build a synthetic lazy-load-to-batch-to-export-to-reload smoke test.
```

These actions establish the public framework before adding larger concrete
libraries of datasources, codecs, transforms, models, losses, objectives, and metrics.

---

## 34. Final implementation strategy

The implementation should not start with a real datasource, a model, a trainer,
or a project workflow system. It should start with the public data/reference
contracts and prove that those contracts compose.

The safest build order is:

```text
contracts first
synthetic datasource and lazy sample vertical slice second
operation pipeline and export round trip third
index-backed Torch adapter and DDP-safe cache fourth
method/loss/objective/metric/learner/trainer base contracts fifth
prediction-as-datasource evaluation and analysis sixth
real datasources and concrete research components later
```

This approach creates a package that can support data preprocessing pipelines,
format conversion, prediction export, analysis, supervised learning,
self-supervised learning, signal-processing methods, custom datasources, remote
storage, and arbitrary future fields without forcing those concerns into the
same abstraction.

---

## 35. Reference-codebase core module gap review

The reference repository contains several useful object families beyond the
main `DataSource -> Sample -> Batch -> Method -> Metric` path. The roadmap
should preserve the useful ideas without copying the project orchestration
shape.

```text
Geometry and spatial payloads
  Defer generic layout, axis, coordinate-frame, graph, and geometry contracts
  until concrete components require them. Keep heavy geometry implementations
  optional and dependency-light when they are eventually introduced.

Visualization and diagnostics
  Do not make plotting a SampleTransform or Metric side effect. Add report or
  diagnostic renderer interfaces that consume Reports, AnalysisResults,
  MetricResultTables, or typed Samples. Durable outputs should use SaveOp or
  explicit user code, not hidden path assumptions.

Analysis pipelines beyond scalar metrics
  Represent error tables, grouped summaries, time/frequency summaries, and
  qualitative overlays as structured AnalysisResult or Report outputs under
  rphys.evaluation. They can be final operations in a normal OperationPipeline.

Training runtime utilities
  Keep optimizer, scheduler, checkpoint, device, distributed, profiler, logger,
  and callback behavior in typed training/framework-adapter specs. Do not hide
  these concerns inside Model, Method, DataSourceAdapter, or Metric objects.

Cache and distributed behavior
  Datasource caches, transformed-sample caches, export resume, and artifact reuse
  use explicit CachePolicy/IdempotencyPolicy, provenance, invalidation, atomic
  writes, rank-safe coordination, and worker/rank seed handling.

Metadata repair and sidecar injection
  Reference-style injection operations map to datasource validation reports,
  explicit DataSource repair utilities, or SampleOps that annotate samples. They
  should not mutate FieldRefs silently or hide assumptions such as default
  sampling rates.

Compound fields
  Logical fields may reference multiple ResourceRefs, such as video frames plus
  metadata sidecars. The FieldCodec and FieldSpec should describe how to load
  and validate the compound value without forcing every field into a modality
  class.

Neural component libraries
  Common neural utilities may later live under rphys.nn, but the initial library
  should expose the Method/Model adapter boundary first. Graph convolutions,
  attention blocks, pooling, positional encodings, and model-zoo modules should
  be admitted only when stable and broadly reusable.

Configuration and orchestration
  The reference codebase's workflow and parameterization conveniences are useful
  evidence for downstream projects, but core rphys should remain a Python
  library. Project orchestration should not be part of this roadmap.
```

The main architectural conclusion from the reference codebase is that most
capabilities are worth preserving as object boundaries, not as shared mutable
workflow machinery. They should enter `rphys` through typed refs, specs,
selectors, SampleFields, OperationPipelines, codecs, export results, result
datasources, and structured evaluation reports.
