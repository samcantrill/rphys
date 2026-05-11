# rphys Implementation Roadmap

Version: 2.0 canonical roadmap
Status: canonical planning source
Scope: public contracts, implementation order, extension boundaries, and
validation strategy for the rebuilt `rphys` base library.

This roadmap supersedes all earlier architecture drafts, notes, roadmap indexes,
planning notes, implementation ledgers, and feature documents that previously
lived under `docs/`. After this cleanup, this file is the only documentation
source of truth in the repository.

## 1. Purpose and Boundary

`rphys` is a Python package for remote physiological measurement research. It
owns domain-specific library contracts and reusable components for fields,
datasources, lazy IO, runtime samples and batches, operations, prediction
methods, models, losses, objectives, metrics, learning, training, evaluation,
analysis, and synthetic validation.

`rphys` does not own project orchestration. Downstream projects or `loom` own
experiment configuration, artifact stores, stage DAGs, scheduling, generic
stage execution, project templates, workflow lifecycle, sweeps, resume logic,
and generic artifact references.

```text
rphys owns reusable remote-physiology contracts and domain primitives.
Downstream projects own experiment plans, workflow orchestration, and config.
loom may wrap rphys plans/results as artifacts, but rphys does not define a
generic workflow runtime.
```

The package should remain stage-friendly but not stage-owning. Public objects
should be typed, serializable where appropriate, provenance-aware, and easy for
downstream stage systems to call. `rphys` must not define generic `Artifact`,
`ArtifactRef`, `ArtifactContract`, `Stage`, `StageContext`, artifact stores,
stage graphs, schedulers, or workflow runtimes.

## 2. Canonical Naming

Use the names below consistently in implementation and public documentation.

```text
DataSource
  Canonical term for datasource discovery, views, splits, indexes, and adapters.
  Public package: rphys.datasources.

Dataset
  Descriptive English only, such as "raw dataset" or "license-safe dataset".
  Do not introduce rphys.datasets or DatasetRef as canonical public APIs.

Operation
  Generic context-aware callable contract.

SampleOp
  Sample -> Sample operation over runtime fields.

Transform
  Operation whose main purpose is transformed output.

Method
  Batch-level prediction or representation algorithm.

Model
  Lower-level computational object, often a tensor or neural module.

Loss
  Differentiable error or penalty term.

Objective
  Optimizer-facing aggregation that produces the scalar used for backward.

Metric
  Detached measurement and reporting contract.
```

Public errors use readable `RemotePhys*Error` names. Do not use `RPhys*Error`
as a new public naming pattern.

## 3. API Governance

Every public component needs a stability label before downstream code relies on
it.

```text
Stable
  Compatibility is expected across normal minor releases. Breaking changes
  require migration notes and tests.

Provisional
  Public enough for experimentation, but names, signatures, or semantics may
  change before promotion.

Private/internal
  Implementation detail. Names beginning with "_" are private unless a public
  contract explicitly says otherwise.
```

Undocumented imports are not stable. A public import becomes a contract only
when code, tests, and the roadmap or docstrings agree on its behavior. Public
API is the documented, tested extension surface, not every helper listed in an
implementation deliverable.

Top-level imports must stay lightweight. Importing `rphys` or lightweight core
modules must not import heavy optional stacks such as torch, OpenCV, PyAV,
scipy, pandas, matplotlib, dataset SDKs, or plotting libraries.

The repository uses `uv`, Python 3.12, `requires-python = ">=3.12"`, and a
committed lockfile. The current rights status is all rights reserved until a
real public-use license is selected. Package metadata must not advertise an
open-source license while that status remains.

Registries are limited to cases where a symbolic name is part of the contract,
such as codec keys, optional datasource adapter aliases, backend names, or a
future recipe catalog. Ordinary extension should work through importable Python
objects and downstream config targets without editing `rphys` internals.

## 4. Scientific Contract Rules

Scientific components must document enough behavior to make their outputs
interpretable and reproducible.

Public datasets, preprocessing operations, signal-processing kernels, models,
losses, metrics, evaluation routines, and analysis components should document:

```text
inputs and outputs
shapes, units, dtypes, devices, and coordinate conventions
sampling rates, timestamps, temporal alignment, windowing, and resampling
filtering, masking, interpolation, padding, and validity-mask behavior
normalization order and statistics scope
subject identity, split behavior, leakage risks, and label availability
failure behavior for NaNs, flat signals, short inputs, missing values, invalid
rates, empty masks, unsupported slices, and dtype/device mismatches
citations for non-obvious scientific algorithms or assumptions
```

Raw datasets must not be committed. Tests use synthetic fixtures or tiny
license-safe fixtures only.

## 5. Core Design Principles

### Field-Centric Design

Every loadable, transformable, collatable, predictable, evaluable, or analyzable
payload is a field. Video is a common field, not a privileged field.

`DataKey` identifies intrinsic logical field identity. Runtime role is separate
and is expressed by `FieldLocator`.

```text
DataKey examples:
  video.rgb
  signal.bvp.reference
  timestamps.video.seconds
  landmarks.face.mediapipe_468
  mask.face.skin
  quality.face_visibility
  custom.my_project.embedding

FieldLocator examples:
  inputs/video.rgb
  targets/signal.bvp.reference
  predictions/signal.bvp
  outputs/embedding.video
  metrics/quality.face_visibility
```

### Field Versus Metadata

If a value can be loaded, sliced, transformed, validated, collated, saved, used
by a method, used by a loss/objective, used by a metric, or analyzed as a
structured payload, make it a field.

If it only describes the datasource, record, sample, split, group, run, or
global context, keep it as metadata.

Ambiguous values such as skin tone, camera intrinsics, quality scores, and
heart-rate labels become fields when consumed by methods, losses, objectives,
metrics, transforms, or exports. Otherwise they may remain metadata.

### Lazy IO Is Not Runtime Processing

`FieldRef`, `FieldIndex`, `TemporalIndexSlice`, `FieldView`, and `IndexItem`
describe what to load. `SampleOp`, `SampleTransform`, and `SampleAugmentation`
describe what to do after loading or lazy sample construction.

An `IndexItem` must not contain transforms, augmentations, formatting logic,
learning-method logic, or stochastic view construction.

### Export Is An Operation

Datasource code discovers, validates, filters, splits, groups, and indexes
logical records and fields. Save/export code writes fields through codecs,
emits new `FieldRef`s, and assembles derived `DataSourceRef`s.

Formatting, symlinking, prediction export, and materialized derived fields are
export/materialization use cases, not datasource adapter behavior.

### Mutable Runtime Path

`Sample` and `Batch` are mutable by default for hot-path efficiency. Branching
pipelines must copy explicitly. Transform contracts must declare reads, writes,
deletes, mutation behavior, and side effects.

### Fail Loudly

Missing fields, invalid field locators, unsupported slices, ambiguous codecs,
invalid schemas, unclear collation, wrong payload types, hidden full-load
fallbacks, silent padding, silent truncation, and hidden coordinate conversions
raise typed errors by default.

### Thin Semantic Objects

Use semantic names when lifecycle or scientific meaning differs. Do not collapse
`Method`, `Loss`, `Objective`, `Metric`, `Learner`, and `Trainer` into one
generic callable. They may share lower-level `Operation` machinery, but their
contracts, side effects, and scientific responsibilities differ.

## 6. Package Boundaries

Initial package homes:

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

Ownership boundaries:

```text
data
  Keys, locators, schema names, metadata keys, loaded FieldValue wrappers,
  runtime Sample/Batch containers, data object hooks, and collation contracts.

io
  ResourceRef, FieldRef, FieldIndex, TemporalIndexSlice, FieldView, codecs,
  load/save contexts, and SampleBuilder.

datasources
  DataSourceSpec, DataSourceRef, RecordRef, validation reports, views, filters,
  groups, splits, indexes, index codecs, Torch adapters, and datasource-owned
  caches.

ops
  Operation contracts, functional kernels, SampleOps, transforms,
  augmentations, checks, routing, pipelines, export/save ops, and provenance.

methods/models/nn
  Prediction-method boundaries, lower-level computational model contracts, and
  optional neural-network helpers.

losses/objectives/metrics
  Differentiable error terms, optimizer targets, detached measurements,
  observations, result tables, grouping, and aggregation.

learning/training
  Learners define step semantics. Trainers define loop mechanics, devices,
  gradient mode, optimizers, schedulers, checkpointing, distributed context, and
  optional stage-friendly callable entrypoints such as experimental run_train.

prediction/evaluation/analysis
  Thin helpers over field containers, result datasources, metric/report
  contracts, analysis operations, and structured report outputs.
```

Do not add a top-level `rphys.transforms` package in the initial design.
Transforms are `ops` specializations. Do not add a generic public
`rphys.stages` package.

## 7. Error Contract

Broad public errors:

```text
RemotePhysError
RemotePhysDataError
RemotePhysFieldError
RemotePhysDataSourceError
RemotePhysIOError
RemotePhysCodecError
RemotePhysSliceError
RemotePhysCollateError
RemotePhysOperationError
RemotePhysPipelineError
RemotePhysMethodError
RemotePhysLearningError
RemotePhysTrainingError
RemotePhysEvaluationError
RemotePhysAnalysisError
RemotePhysDependencyError
RemotePhysNameError
RemotePhysMetadataError
```

Specific subclasses may use shorter domain names when useful:

```text
MissingFieldError
FieldTypeError
FieldSchemaError
InvalidDataKeyError
InvalidFieldLocatorError
InvalidSchemaNameError
InvalidMetadataKeyError
MissingMetadataError
CodecResolutionError
SliceUnsupportedError
SliceOutOfBoundsError
CollatePolicyError
TransformContractError
TemporalAlignmentError
CoordinateFrameError
```

Every `RemotePhysError` should accept a message plus optional structured
context, such as `key`, `role`, `locator`, `schema`, `metadata_key`, `expected`,
`actual`, `path`, and `cause`.

## 8. Milestone 0: Repository Skeleton And Governance

Goal:

```text
Create the package skeleton and enforce public API, dependency, tooling, and
rights-status policy before broad implementation spreads.
```

Key decisions:

```text
Core imports stay lightweight.
Stable API means documented and tested extension contract.
Deep helpers are internal until explicitly documented and tested.
Optional dependencies are grouped by capability.
No generic project config, workflow engine, artifact store, or stage runtime is
implemented in rphys.
```

Deliverables:

```text
pyproject.toml
README.md
src/rphys/__init__.py
src/rphys/errors.py
package __init__.py files for planned homes
tests for lightweight imports and dependency boundaries
roadmap sections documenting public governance
```

Definition of done:

```text
The package imports successfully.
Core imports do not load optional scientific or ML stacks.
The public API policy is documented in this roadmap and enforced by tests.
No generic workflow or artifact runtime exists in rphys.
```

## 9. Milestone 1: Naming, Locators, Schemas, Metadata, And Errors

Goal:

```text
Implement the shared vocabulary used by every later layer.
```

Primary packages:

```text
rphys.errors
rphys.data.keys
rphys.data.locators
rphys.data.schemas
rphys.data.metadata
rphys.data.splits
```

Key interfaces:

```text
DataKey
FieldRole
FieldLocator
DataType constants
SchemaName
MetadataKey constants
SplitName constants
RemotePhysError hierarchy
```

`DataKey` is a validated `str` subclass for intrinsic logical field identity.
It is not a path, runtime role, metric path, transform path, or external-config
locator.

Recommended grammar:

```text
<namespace>.<semantic>[.<qualifier>...]
```

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

Custom keys use:

```text
custom.<project>.<semantic>[.<qualifier>...]
```

Initial runtime roles:

```text
inputs
targets
source
predictions
outputs
losses
objectives
metrics
metadata
diagnostics
```

`FieldLocator` addresses a role-qualified field and optional field metadata.

```text
<role>/<data-key>[#<metadata-key>]
```

`SchemaName` describes loaded interpretation, layout, units, coordinate meaning,
and version. It is not a `DataKey` or `codec_key`.

```text
<family>.<layout_or_semantic>.v<int>
```

Initial split constants:

```text
train
valid
test
predict
```

Split is partition or usage metadata, not loop mode. Validation can run on
`split="valid"`, prediction can run over any split, and downstream projects may
define additional split values without changing `LoopMode`.

Definition of done:

```text
Keys, locators, schemas, metadata keys, split constants, and errors validate
deterministically and fail with typed diagnostics.
DataKey rejects role-prefixed paths and metadata selectors.
FieldLocator preserves DataKey identity and runtime role separately.
No datasource, codec, transform, model, loss, metric, or trainer defines a
duplicate naming or error vocabulary.
```

## 10. Milestone 2: Loaded Runtime Core

Goal:

```text
Implement the in-memory runtime contract used after payloads are loaded or
wrapped and before operations, models, losses, metrics, and analysis consume
data.
```

Primary package:

```text
rphys.data
```

Key interfaces:

```text
FieldSpec
FieldValue
DataObjectBase
Sample
Batch
SampleContract
CollatePolicy
CollateContext
collate_samples
```

### FieldSpec

`FieldSpec` is intentionally minimal:

```text
key: DataKey
data_type: lowercase ASCII data category
schema: optional schema identifier
```

The base spec must not include `shape`, `dtype`, `description`, `runtime_type`,
coordinate frame, temporal axis, units, layout, sample rate, required metadata,
or integration-specific fields. Those details belong in future specialized
specs, data objects, datasource schemas, operation contracts, or docstrings when
concrete behavior requires them.

Public semantics:

```text
Value equality covers key, data_type, and schema.
Hashability is not public.
Copy and deep copy are value-preserving over primitive fields.
No dict, JSON, registry, or manifest round trip is public in this milestone.
```

### FieldValue

`FieldValue` wraps a loaded payload with narrow field-level metadata:

```text
value
schema: optional schema identifier
metadata: shallow-copied mapping with string or MetadataKey-compatible keys
collate_policy: optional explicit CollatePolicy
```

It does not duplicate `data_type`; broad field identity belongs to `DataKey` and
`FieldSpec`.

Public semantics:

```text
Equality is object identity to avoid accidental tensor payload comparison.
Hashability is not public.
Construction shallow-copies metadata.
Shallow copy shares payload and nested metadata values.
Deep copy uses normal Python deep-copy behavior and may fail for non-copyable
payloads with the underlying payload error.
No arbitrary payload serialization contract exists.
```

### DataObjectBase

`DataObjectBase` is a loaded-payload base or protocol, not an IO abstraction.
It supports explicit validation, subclass-declared tensor traversal, device
movement, detaching, pinning, and optional future collation hooks without
importing backend libraries.

Public semantics:

```text
Validation is explicit-call only.
The base does not inspect arbitrary attributes.
The base does not import torch, numpy, pandas, OpenCV, scipy, or plotting libs.
Device/detach/pin operations return the object callers must use.
No in-place mutation guarantee is public.
No-op is allowed when no tensor-like leaves are declared.
Unsupported operations on declared leaves raise RemotePhysDataError.
Base equality is object identity and hashability is not public.
Generic copy/deep-copy are not public base guarantees.
```

Optional torch-aware helpers may be added later only in import-gated optional
modules.

### Sample And Batch

`Sample` is the per-item runtime container. `Batch` is the collated runtime
container. Both are generic field containers keyed by `FieldLocator`, not fixed
`inputs` / `targets` tuples and not video-specific objects.

Expected API shape:

```text
has(locator)
field(locator)        -> FieldValue or runtime field wrapper
get(locator)          -> payload value
require(locator, expected_type=None) -> payload value or typed error
set_field(locator, field_or_payload, ...)
delete_field(locator)
rename_field(old, new)
role(role)
shallow_copy()
deep_copy()
map_tensors_(fn, locators=None)
```

Rules:

```text
Samples and Batches are mutable by default.
Batch exposes the same field access API as Sample.
Batch may initially subclass Sample if that keeps behavior simple.
Runtime role is supplied by FieldLocator and must not mutate DataKey identity.
Branching workflows should use explicit deep copy unless a later operation
contract documents payload sharing.
Sample and Batch equality is object identity and hashability is not public.
Sample persistence and payload serialization are deferred to IO/datasource
plans.
```

### SampleContract

`SampleContract` is an explicit-call runtime validator. It checks required and
optional locators, expected payload types, and schema constraints. It does not
validate shapes, axes, units, coordinate frames, sample rates, or full scientific
schema catalogs until specialized contracts exist.

Public semantics:

```text
Value equality covers declared requirements and options.
Hashability is not public.
Copy and deep copy are value-preserving.
It is not a durable schema serialization format.
```

### Collation

Initial collation is deliberately narrow.

```text
Supported initial policy:
  CollatePolicy.LIST

Unsupported until accepted later:
  stack
  padding
  allow-missing
  drop-if-missing
  custom callable
  object-delegated collation
```

Absent policy fails. Inconsistent field sets fail. Missing fields fail. Shape
mismatch is not interpreted by the base collator. Metadata collates
deterministically as lists, with explicit `None` for missing metadata values
when that behavior is accepted by the collation contract.

Public `CollatePolicy.LIST` semantics:

```text
Enum member identity, equality, hashing, copy, deep copy, name, and value token
are public for LIST.
Reserved or future policy names fail if used before implementation.
```

Definition of done:

```text
rphys.data exports only code-backed runtime contracts.
Invalid keys, missing fields, wrong payload types, schema mismatches, absent
collation policies, and unsupported policies fail loudly.
No lazy IO refs, codecs, datasource scanning, transforms, methods, or training
logic live in rphys.data.
Core imports remain dependency-free.
```

## 11. Milestone 3: Lazy References And Index Items

Goal:

```text
Implement the reference model that represents storage, datasource structure,
and lazy IO requests without loading payloads.
```

Primary packages:

```text
rphys.io
rphys.datasources
```

Key interfaces:

```text
ResourceRef
FieldRef
FieldIndex
TemporalIndexSlice
FieldView
DataSourceRef
RecordRef
IndexItem
DataSourceSchema
```

Object rules:

```text
ResourceRef identifies physical storage through URI/protocol/storage options.
It is not an ArtifactRef, stage output handle, artifact store object, or
workflow lifecycle primitive.

DataSourceRef represents a datasource or datasource view without loaded payloads.

RecordRef represents a stable logical record before windowing. It owns record
identity, field presence, and leakage-sensitive metadata such as datasource_id,
record_id, source_id, subject_id, split, and group.

FieldRef is a serializable lazy reference to one complete logical field. It
does not contain runtime role, FieldLocator, temporal slice, loaded tensors, or
open handles.

FieldView combines a FieldRef with optional imposed access behavior such as a
FieldIndex. It is the lazy request loaded by codecs.

IndexItem maps role-qualified FieldLocators to FieldViews and is the unit
consumed by SampleBuilder.
```

`TemporalIndexSlice` is the only initial concrete `FieldIndex`.

```text
index-based
field-native temporal index space
half-open [start, stop)
non-negative start and stop
positive step, with step != 1 allowed to fail initially
no seconds-based slicing
no spatial slicing
```

The same numeric slice on two fields does not imply temporal alignment.
Cross-field alignment assumptions must be explicit metadata or operation
contracts.

Definition of done:

```text
DataSourceRef -> RecordRef -> FieldRef -> FieldView -> IndexItem is implemented
and documented by tests and docstrings.
Refs and views serialize without open handles or loaded arrays.
Different fields in one IndexItem can carry different field-native indexes.
IndexItem remains pure lazy IO and never contains transform, augmentation,
method, export, or training logic.
```

## 12. Milestone 4: Codecs And Lazy Sample Construction

Goal:

```text
Implement the bridge from IndexItem FieldViews to mutable runtime Samples with
lazy SampleField handles.
```

Primary packages:

```text
rphys.io
rphys.io.codecs
rphys.data
```

Key interfaces:

```text
FieldCodec
CodecRegistry
CodecCapabilities
CodecLoadResult
CodecSaveResult
LoadContext
SaveContext
IOContext
SampleField
SampleBuilder
SampleBuildContext
MetadataSavePolicy
```

Codec rules:

```text
A codec loads a FieldView, not a path and not a role-qualified sample field.
probe returns normalized lightweight metadata or FieldSpec without full payload
loading.
load respects FieldView.field_index.
save writes one logical FieldValue or payload to a target FieldRef/resource
description and returns typed save results.
Unsupported slices fail loudly.
Missing optional codec dependencies fail at the boundary that needs them.
No silent full-resource loading occurs when slicing is requested but unsupported.
No codec parses FieldLocator, split, transform, augmentation, model, or trainer
concerns.
```

SampleBuilder behavior:

```text
Input: IndexItem plus optional requested locators.
Resolve codecs for requested FieldViews.
Create SampleFields that load through codecs only on payload access unless
eager loading is explicitly requested.
Preserve FieldLocator role keys and intrinsic DataKey provenance separately.
Support building all fields, a subset, or one field.
Support probe paths without full payload load.
```

Metadata persistence:

```text
Manifest metadata is small serializable metadata attached to refs, index items,
sample fields, or export results.
Metadata fields are structured payloads that should be loaded, sliced,
transformed, collated, saved, or analyzed like normal fields.
```

Metadata saving is triggered by export/save specifications, not implicitly by
codec load.

Definition of done:

```text
IndexItems build into Samples with lazy SampleFields.
SampleField load states and error states are explicit.
Codec resolution is deterministic and typed.
At least one dependency-light test codec loads and saves.
Compound logical fields can reference multiple ResourceRefs behind one FieldRef.
SampleBuilder does not scan datasources, choose splits, apply ops, move devices,
cache implicitly, or perform model formatting.
```

## 13. Milestone 5: DataSource Discovery, Views, Filters, Splits, And Indexes

Goal:

```text
Implement datasource discovery, validation, filtering, grouping, split
assignment, and index construction around lazy logical fields.
```

Primary packages:

```text
rphys.datasources
rphys.datasources.adapters
rphys.datasources.filters
rphys.datasources.splits
rphys.datasources.validation
rphys.datasources.indexes
```

Key interfaces:

```text
DataSourceSpec
DataSourceAdapter
DataSourceValidationReport
DataSourceViewPlan
DataSourceView
DataSourceViewBuilder
DataSourceViewResult
Filter
FilterChain
FilterResult
GroupPlan
GroupBuilder
GroupResult
SplitPlan
SplitBuilder
SplitResult
IndexPlan
IndexBuilder
IndexResult
IndexBuildReport
DataSourceIndex
DataSourceIndexCodec
DataSourceIndexManifest
CompositeDataSourceIndex
ConcatDataSourceIndex
```

Plan, builder, result pattern:

```text
Plan
  Serializable request with parameters, policies, seeds, validation
  requirements, and provenance inputs.

Builder
  Stateless or lightly stateful executor that consumes a plan and source object.

Result
  Typed output plus report, warnings, rejected items, provenance, and stable
  fingerprint.
```

These are wrap-friendly by downstream stage runtimes, but rphys does not define
generic stages around them.

Datasource rules:

```text
DataSourceAdapter.scan emits DataSourceRef, RecordRefs, FieldRefs, and
validation reports. It should not decode full videos or signals except through
explicit probe or validation hooks.
DataSourceSpec owns discovery inputs such as roots, URI rules, include/exclude
patterns, and source metadata. It does not know runtime roles, transforms, or
model requirements.
Filters operate over records, fields, index candidates, or datasource views.
Filters declare no_io, probe_only, or explicit_validation_io policy.
Filters do not mutate DataSourceRef, RecordRef, FieldRef, or IndexItem.
Groups are metadata assignments used for leakage-safe splits, stratification,
monitoring, and analysis.
SplitBuilder consumes GroupResult for group-disjoint behavior.
IndexBuilder creates DataSourceIndex items with FieldViews only.
Durable indexes use schema-versioned JSON/JSONL-like manifests, not pickle.
```

Definition of done:

```text
Synthetic DataSourceAdapter emits multiple logical fields.
DataSourceViewBuilder filters without mutating source refs.
GroupBuilder and SplitBuilder produce typed results with counts, warnings, and
leakage checks.
IndexBuilder creates lazy IndexItems with datasource, record, group, split, and
window provenance.
DataSourceIndex exposes length, item access, iteration, fingerprint, and
metadata independent of storage format.
CompositeDataSourceIndex preserves child index identity and local item position.
No formatting, export, transform, augmentation, or model logic lives under
rphys.datasources.
```

## 14. Milestone 6: Operation Foundations And Functional Kernels

Goal:

```text
Define the generic operation contract and placement rules for pure numerical
kernels before specialized sample, export, metric, or analysis operations land.
```

Primary package:

```text
rphys.ops
```

Key interfaces:

```text
Operation
OperationContract
OperationContext
OperationResult
OperationPipeline
OperationRole
FunctionalKernel
```

Rules:

```text
Functional kernels have no Sample, Batch, FieldRef, IndexItem, datasource, file
IO, hidden randomness, hidden device movement, or hidden schema conversion.
They accept payloads, parameter objects, and explicit metadata values.

Operation classes wrap kernels when contracts, context, provenance, declared
randomness, mutation policy, or pipeline composition are needed.

Batch-level composition uses Operation[Batch, Batch] initially. Do not add a
public BatchOperator, BatchProgram, or BatchOpPipeline until repeated concrete
needs justify it.
```

Definition of done:

```text
Functional kernels are callable without runtime containers.
Operations can declare input/output types, deterministic behavior, mutation,
side effects, context requirements, and failure modes.
OperationPipeline propagates context and validates contracts.
No concrete CHROM/POS/model-specific preprocessing kernels are required in this
milestone.
```

## 15. Milestone 7: SampleOps, Transforms, Augmentations, Checks, And Pipelines

Goal:

```text
Implement composable runtime operations over Samples.
```

Primary packages:

```text
rphys.ops.sample
rphys.ops.pipelines
```

Key interfaces:

```text
SampleOp
SampleTransform
SampleAugmentation
SampleCheck
SampleOpPipeline
SampleContext
PipelineContext
AugmentationParams
SampleDecision
SampleRoute
```

Rules:

```text
SampleOps declare read, write, delete, and optional dynamic-field permissions
using parsed FieldLocators.
SampleOps may only mutate declared fields unless explicitly permitted.
Default runtime behavior may mutate in place and return the same Sample.
Non-mutating behavior copies explicitly.
Side-effecting ops declare side effects and return typed result metadata.
SampleCheck is deterministic and raises typed errors or writes declared report
fields.
Datasource/index filters remain separate when decisions can be made before
loading. Sample-level filtering/routing is an explicit SampleOp when decisions
depend on loaded data or earlier operations.
```

Stochastic augmentation:

```text
SampleAugmentation samples parameters only from context-provided RNG streams.
apply_params is deterministic for fixed sample and params.
Seed material includes run seed, epoch, worker id, item/sample id, operation
index, operation name, and view name when relevant.
Global random, numpy default RNG, and torch default RNG are not used directly.
Synchronized augmentations apply one parameter object consistently to linked
fields.
```

Self-supervised and contrastive initial path:

```text
IndexBuilder creates a wider TemporalIndexSlice.
SampleBuilder creates one lazy wide-window Sample.
SampleAugmentation writes declared view locators such as
inputs/video.rgb.view_a and inputs/video.rgb.view_b.
Learners consume those view fields after collation.
Do not add multi-member IndexItems or nested view Samples initially.
```

Definition of done:

```text
SampleOpPipeline preserves operation order for sequences and ordered mappings.
Contract checks catch missing or malformed fields.
Undeclared mutation fails.
Augmentation replay and deterministic-policy behavior are tested.
SampleFields load only when an operation accesses payload data.
SampleOpPipeline does not scan datasources, choose splits, export fields, or
hide raw numerical kernels.
```

## 16. Milestone 8: Save/Export Ops And Derived DataSources

Goal:

```text
Represent formatting, symlinking, derived fields, and prediction export as
normal SampleOp/OperationPipeline flows that write fields through codecs and
emit derived DataSourceRefs.
```

Primary packages:

```text
rphys.ops.export
rphys.io
rphys.datasources
```

Key interfaces:

```text
ExportSpec
ExportTarget
OutputLayout
ExportPolicy
CodecSelectionOp
SaveOp
FieldExportResult
RecordExportResult
ExportResult
ExportReport
DataSourceManifestWriter
DerivedDataSourceBuilder
IdempotencyPolicy
```

Object rules:

```text
ExportSpec is data, not an orchestrator.
CodecSelectionOp annotates intended output codec/schema/resource targets but
does not write files.
SaveOp writes declared fields through FieldCodec.save and returns field and
record export results.
OutputLayout derives stable target URIs from datasource id, record id, field
key, export id, and export spec fingerprint.
DataSourceManifestWriter assembles new RecordRefs and a derived DataSourceRef
from export results without rescanning output directories.
Symlink/copy is an export policy or codec capability and must preserve source
ResourceRef lineage.
```

Important boundary:

```text
Method, Learner, Trainer, Loss, Objective, and Metric objects must not write
prediction/test artifacts implicitly.
Durable predictions and processed outputs are normal fields exported through
SaveOp and DataSourceManifestWriter.
```

Definition of done:

```text
A datasource/index can be processed by SampleOpPipeline and exported into a
derived DataSourceRef.
Export reports count written, skipped, linked, copied, replaced, and failed
fields.
Export layout is deterministic and idempotency policy is tested.
Derived DataSourceRefs can be filtered, indexed, and loaded through normal
machinery.
No formatting/export module lives under rphys.datasources and datasource
adapters do not invoke export code.
```

## 17. Milestone 9: Index Adapters, Torch Data Loading, And Cache

Goal:

```text
Bridge DataSourceIndex to framework iteration without turning adapters into
datasource discovery, split construction, cache orchestration, export, or model
formatting layers.
```

Primary packages:

```text
rphys.datasources.indexes
rphys.datasources.torch
rphys.datasources.cache
```

Key interfaces:

```text
TorchIndexSampleDataset
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

Adapter rules:

```text
TorchIndexSampleDataset owns a DataSourceIndex, SampleBuilder, optional
SampleOpPipelines, usage/split metadata, and WorkerContextFactory.
__getitem__ resolves an integer position to an IndexItem, derives context,
builds a Sample, applies optional pipelines, and returns a Sample.
It does not scan directories, choose splits, build indexes, export fields, or
format model inputs.

BatchCollater delegates to generic Batch and CollatePolicy behavior. It
preserves FieldLocator keys and per-item metadata. It does not hard-code
inputs, targets, or source behavior.
```

Cache design:

```text
Caching is explicit through CachePolicy.
Cache keys include index item identity, FieldView/resource fingerprints, codec
version, optional deterministic operation fingerprints, relevant run context,
and software versions where needed.
Cache reuse must preserve scientific data flow and provenance.
```

Implementation order for cache:

```text
1. Deterministic CacheKey and CachePolicy.
2. Local CacheStore with atomic temp-write then commit/rename semantics.
3. Manifest metadata, hit/miss reporting, and invalidation tests.
4. Distributed coordination only after local semantics are stable.
```

DDP-safe coordination must eventually support rank/world/worker context,
pending/committed/failed states, file locks or compare-and-swap where
available, first-writer-wins or rank-zero-write policies, barrier/wait policy
with timeout, stale-lock recovery, and read-only shared cache plus optional
per-rank local cache.

Definition of done:

```text
Torch-compatible data loading consumes any DataSourceIndex implementation.
Single-worker and multi-worker context derivation is deterministic where
practical.
Collation remains FieldLocator-aware.
Cache primitives are deterministic, provenance-aware, invalidation-aware, and
atomic for local stores.
DDP cache behavior is not labeled stable until rank-safe coordination tests
exist.
```

## 18. Milestone 10: Models, Methods, And NN Base Contracts

Goal:

```text
Define the boundary between generic Batches, prediction methods, and lower-level
computational models without implementing concrete algorithms yet.
```

Primary packages:

```text
rphys.methods
rphys.models
rphys.nn
```

Key interfaces:

```text
Method
StatefulMethod
TrainableMethod
Model
MethodInputAdapter
MethodOutputAdapter
MethodOutput
PredictionContext
```

Rules:

```text
Methods consume Batch fields through typed selectors/adapters and emit
prediction or representation fields under FieldLocators.
FieldLocators and MetadataKeys are parsed at construction, not inside hot
runtime loops.
Models operate on tensors or structured model inputs, not DataSourceRefs,
IndexItems, SampleBuilders, DataLoaders, artifact paths, or datasource
discovery objects.
Method.predict is loss-free and objective-free.
Method.predict must not mutate its input Batch unless declared.
Methods do not export predictions, update metrics, train models, choose splits,
write checkpoints, or step optimizers.
Trainable capability protocols do not import torch in core modules.
```

No concrete CHROM, POS, neural baseline, model zoo, or algorithm-specific method
is implemented in this milestone.

Definition of done:

```text
Base Method can adapt Batch fields to model/op inputs and return prediction
fields.
Input/output adapters store typed selectors.
Models are independently testable from runtime Batch and datasource machinery.
Stateful/trainable capabilities expose parameters and state without owning
optimizer, scheduler, checkpoint, device, or distributed behavior.
```

## 19. Milestone 11: Loss, Objective, And Metric Contracts

Goal:

```text
Define optimizer error terms, optimizer targets, and detached measurements
without implementing concrete numerical algorithms yet.
```

Primary packages:

```text
rphys.losses
rphys.objectives
rphys.metrics
```

Key interfaces:

```text
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
Metric
MetricInputSpec
MetricContract
MetricValue
MetricObservation
MetricResultTable
MetricContext
GroupBySpec
MetricAggregationPlan
MetricAggregator
```

Rules:

```text
Losses compute differentiable error or penalty terms from declared fields.
LossResult carries the same or derived Sample/Batch plus differentiable term
data when field writing helps composition.
Loss contracts declare differentiability, reduction, masking, missing-field
behavior, and gradient expectations through predictions, targets, both, or
neither.

Objectives aggregate losses plus optimizer-relevant terms such as weights,
regularization, constraints, schedules, parameter penalties, and auxiliary
values. ObjectiveResult.total is the scalar used for backward. Trainer consumes
ObjectiveResult.total, not a string field such as loss.total.

Metrics compute detached observations or result tables. They may write declared
metric fields, but never influence optimizer gradients directly.
Metric state, if needed, lives in explicit aggregators/adapters rather than
hidden mutation inside core Metric.
```

Avoid a broad public `Measure` base and broad input adapters unless repeated
implementation pressure justifies them. Selector specs and small internal
helpers should cover the first implementation.

Metric evaluation supports both orders:

```text
per-sample/window metric -> aggregate metric rows
prediction samples -> aggregate/reconstruct record-level samples -> compute metric
```

Definition of done:

```text
Losses, objectives, and metrics address fields by typed FieldLocators.
ObjectiveResult provides the optimizer scalar and structured terms.
MetricResultTable stores per-sample/per-window and aggregated rows with grouping
metadata.
No loss, objective, metric, or aggregator scans datasources, loads samples,
writes files, owns trainer hooks, or depends on logger state.
```

## 20. Milestone 12: Learner And Trainer Contracts

Goal:

```text
Keep learning semantics separate from loop mechanics.
```

Primary packages:

```text
rphys.learning
rphys.training
```

Key interfaces:

```text
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
DeviceMover
OptimizerSpec
SchedulerSpec
CheckpointMetadata
DistributedContext
run_train, experimental
```

Rules:

```text
Learner owns mode-specific step semantics and composes Method + optional
Objective + Metrics.
Trainer owns iteration, device movement, grad/no-grad mode, backward, gradient
accumulation, optimizer/scheduler stepping, clipping, precision policy,
distributed context, checkpoint hooks, loop logging, and callbacks.
Learner does not call optimizer.step, scheduler.step, checkpoint writers,
dataloader builders, SampleBuilder, datasource adapters, or export ops.
Trainer does not parse input/target/prediction locators, compute scientific
losses, build IndexItems, export outputs, or assume supervised learning.
```

`LoopMode` describes active execution semantics:

```text
train
validate
test
predict
```

It is not a datasource split, workflow stage, roadmap phase, or artifact stage.
`context.split` records data partition or usage label when known and must not be
treated as equivalent to mode.

`StepOutput` should carry:

```text
predictions: Sample | Batch | None
objective: BackwardableScalar | None
loss_terms
objective_terms
metric_values
diagnostics
metadata
```

`SupervisedLearner` is the only initial concrete learner. Contrastive,
self-supervised, masked-modeling, and multitask learning remain design patterns
and contract tests until implementation pressure justifies concrete classes.

`run_train` may be an experimental function-style entrypoint for downstream
wrappers. It delegates to `TrainingPlan`, `Trainer`, and `Learner`, returns a
typed `TrainingResult`, and does not define a workflow runtime or stable project
configuration schema.

Definition of done:

```text
Trainer can run fit/validate/test/predict over Batch iterables without
hard-coded fields or supervised-only assumptions.
Trainer backpropagates only StepOutput.objective.
SupervisedLearner works with configured Method, Objective, and Metrics.
Prediction works without objective or targets.
No framework-specific Lightning/Fabric/accelerator integration is part of the
core milestone.
```

## 21. Milestone 13: Prediction, Evaluation, Analysis, And Reports

Goal:

```text
Treat predictions, processed outputs, diagnostics, metric observations, and
analysis inputs as normal field containers and structured result objects.
```

Primary packages:

```text
rphys.prediction
rphys.evaluation
rphys.analysis
rphys.ops.evaluation
```

Key interfaces:

```text
PredictionRunner
PredictionResult
EvaluationProtocol
EvaluationPlan
EvaluationRunner
MetricOp
SampleAggregatorOp
MetricAggregatorOp
AnalysisOp
VisualizationOp
AnalysisContext
AnalysisResult
Report
ReportTable
DiagnosticRenderer
```

Rules:

```text
Predictions are ordinary Sample or Batch fields, not rigid waveform-specific
objects.
Durable predictions are exported through SaveOp and DataSourceManifestWriter
into derived DataSourceRefs.
Prediction helpers iterate over Batch-producing data, call Method/Learner/
Trainer prediction entrypoints, attach metadata/provenance, and return field
containers, typed summaries, or exported derived DataSourceRefs.
Prediction helpers do not introduce prediction-specific datasources or a second
storage path.
```

`EvaluationProtocol` is the scientific comparison contract. It names:

```text
prediction selectors
reference selectors
grouping metadata
pre-metric sample aggregation or reconstruction
metric computation
post-metric aggregation
report requirements
failure behavior
```

`EvaluationPlan` binds a protocol to concrete datasource/index/run inputs.
`EvaluationRunner`, if present, is only a thin executor over existing indexes,
SampleBuilder, SampleOpPipeline, MetricOps, aggregators, and report builders.
It must not own datasource scanning, split construction, training losses, codec
logic, or custom report file conventions.

Analysis/reporting rules:

```text
AnalysisOp and VisualizationOp consume Samples, Batches, MetricResultTables,
AnalysisResults, or Reports and return structured outputs.
Analysis does not train models, select checkpoints, mutate predictions, crawl ad
hoc log files, or write plot files outside explicit report/export contracts.
Report and DiagnosticRenderer return structured result objects. Durable files,
when needed, are written by explicit export/report save behavior or user code.
```

Definition of done:

```text
Prediction Samples can be exported as derived DataSourceRefs and loaded again.
EvaluationProtocol records selector, grouping, aggregation, metric, and report
semantics without owning workflow execution.
Analysis and visualization outputs are structured and side-effect free by
default.
No alternate scoring runtime, hidden plotting system, or waveform-only
prediction object is introduced.
```

## 22. Milestone 14: Synthetic Fixtures, Contract Tests, And Smoke Hardening

Goal:

```text
Make the public object model difficult to regress by building synthetic
fixtures, contract helpers, integration flows, smoke tests, and public API
checks.
```

Testing support lives under repository-level `tests/` for now. Do not add a
public testing-helper package until downstream need and API stability justify
it.

Fixture requirements:

```text
multiple datasources, records, subjects, and groups
stable datasource_id, record_id, subject_id, split, and group metadata
tiny deterministic video-like arrays
waveform fields with known frequency, phase, amplitude, and optional heart rate
timestamp fields with rates, offsets, drift, and irregularity
optional landmarks, masks, quality fields, metadata sidecars, and compound
fields
missing-field, short-record, flat-signal, NaN, inf, invalid-rate, and
misalignment variants
URI-based ResourceRefs
tiny manifests for codec, export, and derived datasource round trips
```

Contract tests should cover:

```text
selectors parsed at construction, not hot runtime loops
refs and manifests serialize without open handles or loaded arrays
FieldRef does not own temporal slice
FieldView imposes access behavior
SampleBuilder probe/build subset behavior
operation deterministic context and stochastic replay
SaveOp-derived datasource round trip
Method/Loss/Objective/Metric/Learner/Trainer boundaries
cache key determinism and invalidation
public import and dependency boundaries
```

Root smoke flow:

```text
synthetic scan
-> filter/group/split
-> index manifest
-> lazy SampleBuilder
-> SampleOpPipeline
-> BatchCollater
-> trivial Method prediction
-> SaveOp derived DataSourceRef
-> reload predictions
-> MetricOp / AnalysisOp
-> Report
```

The default smoke path must run on CPU without external data, network access,
GPUs, heavy optional dependencies, workflow tooling, or private project code.

## 23. Critical Path

```text
M0 skeleton and governance
  -> M1 naming, locators, schemas, metadata, errors
    -> M2 loaded runtime core
      -> M3 lazy references and index items
        -> M4 codecs and lazy Sample construction
          -> M5 datasource discovery, views, splits, indexes
            -> M9 index adapters, Torch loading, cache
              -> M10 methods/models
              -> M11 losses/objectives/metrics
              -> M12 learners/trainers
                -> M13 prediction/evaluation/analysis/reports
                  -> M14 synthetic contract and smoke hardening

M6 operation foundations
  -> M7 SampleOps and pipelines
    -> M8 export and derived DataSources
      -> M13 prediction/evaluation/analysis/reports
```

Testing support grows continuously after M1.

Concrete datasources, codecs, algorithms, models, losses, metrics, and learners
should wait until their public contract layer and synthetic tests are stable.

## 24. First Vertical Slice

The first complete vertical slice should be synthetic:

```text
SyntheticDataSourceAdapter
  -> DataSourceRef with RecordRefs and FieldRefs
  -> metadata/probe-based filters and group-safe split
  -> IndexBuilder creates DataSourceIndex with IndexItems and FieldViews
  -> DataSourceIndexCodec round trip
  -> SampleBuilder creates lazy Samples
  -> SampleOpPipeline applies one deterministic SampleOp
  -> BatchCollater creates Batch using explicit LIST collation
  -> trivial Method returns prediction Batch
  -> SaveOp exports predictions into derived DataSourceRef
  -> derived DataSourceRef reloads
  -> MetricOp/AnalysisOp produces MetricResultTable and Report
```

Success means the architecture composes without real data, concrete rPPG
algorithms, trainers, workflow engines, or project configuration.

## 25. Real Datasource Sequence

After the synthetic flow works:

```text
1. Choose the simplest datasource with video-like data and a reference signal.
2. Implement DataSourceAdapter.scan to emit refs only.
3. Implement or reuse codecs.
4. Add validation reports for missing files, metadata, and sidecars.
5. Add official or subject-disjoint split support through datasource builders.
6. Add index construction using explicit FieldView and FieldIndex behavior.
7. Add tiny license-safe or synthetic-equivalent smoke tests.
8. Add export only through SaveOp and DataSourceManifestWriter.
```

Do not start with a full preprocessing pipeline for a real datasource. First
make it discoverable, referenceable, indexable, and lazily loadable.

## 26. Deferred Decisions

These should not block core implementation:

```text
exact full codec catalog
spatial slices
time-based slices
nested multi-view Sample representation
multi-member IndexItems for advanced contrastive sampling
full mesh, point-cloud, renderer, segmentation, or geometry libraries
concrete CHROM/POS methods and neural baselines
model zoo
concrete loss and metric catalog
large library of self-supervised learners
plugin discovery through Python entry points
public testing-helper package
advanced cache backends
broad optimizer/scheduler factory library
framework-specific distributed, accelerator, profiler, logger adapters
project configuration systems, workflow engines, and CLIs
worked examples and downstream template projects
advanced publication/report generation
advanced UI/dashboard tooling
```

The roadmap should leave room for these without freezing their APIs early.

## 27. Anti-Patterns

Do not:

```text
let a Torch Dataset scan raw directories
put formatting under datasource adapters
add a separate offline-output subsystem
let IndexItem contain transforms or augmentations
build self-supervised views inside Trainer
silently load full files when a slice is unsupported
silently pad or truncate during collation
hard-code video as a Sample attribute
put concrete algorithms into the base operation layer
put optimizer, scheduler, checkpoint, distributed, profiler, or logger behavior
inside Model or Method
put learning-style logic inside Trainer
put datasource logic inside Learner
let Method, Learner, Trainer, Loss, Objective, or Metric write prediction
artifacts implicitly
make Prediction objects waveform-only
require users to edit rphys internals for extensions
let visualization or analysis write ad hoc files from loaded attributes
add implicit caches
introduce project-level configuration or workflow orchestration inside rphys
add generic Stage, ArtifactRef, ArtifactContract, StageContext, BatchProgram, or
universal BatchOperator APIs before concrete repeated library needs justify them
```

## 28. Release Readiness Gates

Internal alpha:

```text
Core naming and runtime contracts implemented.
Field-versus-metadata rule is documented.
Synthetic DataSourceRef can be indexed and serialized as an index manifest.
SampleBuilder can create Samples with lazy SampleFields.
SampleOpPipeline can apply deterministic SampleOps.
Batch collation works with explicit LIST policy.
Basic unit and contract tests pass.
```

Developer alpha:

```text
Synthetic end-to-end library flow works without real data.
SaveOp can export a derived DataSourceRef and reload it.
Base Method, Loss, Objective, Metric, Learner, SupervisedLearner, and Trainer
contracts have tests.
Dependency-boundary and public API checks pass.
```

Research-use beta:

```text
At least one real datasource adapter works with license-safe or externally
provided data.
Subject-disjoint split and index construction work.
Export works for at least one common field format through codecs.
Prediction fields can be exported, reloaded, grouped, and scored by metrics.
Synthetic smoke pipeline runs in CI.
```

Stable public API:

```text
Stable contracts have tests and documentation.
Core behavior is strict and predictable.
Deprecation and experimental API policy exists.
Public API/import-boundary checks pass.
Optional dependency extras and import boundaries are documented and tested.
Stable public API excludes undocumented deep helpers by default.
Scientific edge-case coverage is documented.
```

## 29. Immediate Implementation Order

Recommended next actions:

```text
1. Implement package skeleton and lightweight import tests.
2. Implement RemotePhys* errors, DataKey, FieldLocator, MetadataKey, SchemaName,
   and split constants.
3. Implement minimal FieldSpec, narrow FieldValue, and CollatePolicy.LIST.
4. Implement Sample, Batch, DataObjectBase, SampleContract, and list-only
   collation.
5. Implement ResourceRef, FieldRef, FieldIndex, TemporalIndexSlice, FieldView,
   DataSourceRef, RecordRef, and IndexItem.
6. Implement FieldCodec, CodecRegistry, load/save contexts, and lazy
   SampleBuilder.
7. Implement synthetic DataSourceAdapter, view/filter/group/split builders,
   DataSourceIndex, and index manifest round trip.
8. Implement Operation, SampleOp, SampleOpPipeline, deterministic context, and
   augmentation replay.
9. Implement SaveOp and derived DataSourceRef round trip.
10. Implement index-backed Torch adapter and explicit local cache primitives.
11. Implement base Method/Model, Loss/Objective/Metric, Learner/Trainer, and
    prediction/evaluation/analysis contracts.
12. Build the synthetic lazy-load-to-batch-to-export-to-reload smoke test.
```

This order proves the public object model before concrete research components
arrive.

## 30. Final Strategy

Start with contracts, synthetic refs, lazy samples, and export round trips. Do
not start with a real datasource, a model, a trainer, or a workflow system.

The target architecture is:

```text
contracts first
synthetic datasource and lazy sample vertical slice second
operation pipeline and export round trip third
index-backed framework adapter and explicit cache fourth
method/loss/objective/metric/learner/trainer contracts fifth
prediction-as-derived-datasource evaluation and analysis sixth
real datasources and concrete research components later
```

Most reference-codebase capabilities should be preserved as object boundaries,
not as shared mutable workflow machinery. They should enter `rphys` through
typed refs, specs, selectors, SampleFields, OperationPipelines, codecs, export
results, derived DataSources, metric tables, and structured reports.
