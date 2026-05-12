# rphys Implementation Roadmap

Version: 2.0 canonical roadmap
Status: canonical planning source
Scope: public contracts, implementation order, extension boundaries, and
validation strategy for the rebuilt `rphys` base library.

This roadmap supersedes all earlier architecture drafts, notes, roadmap indexes,
planning notes, implementation ledgers, and feature documents that previously
lived under `docs/`. After this cleanup, this file is the only documentation
source of truth in the repository.

For a contributor-facing vocabulary summary derived from this roadmap and
code-backed contracts, see `docs/GLOSSARY.md`. That glossary is a guide for
consistent wording and does not override this roadmap.

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

### Training Performance Objective

Domain-agnostic training performance is governed by one objective:

```text
maximize valid experiment decisions per unit cost
```

Samples per second, GPU utilization, and benchmark throughput are diagnostic
signals, not isolated goals. The system should minimize time spent on work that
does not advance a training step, validate a contract, or produce a decision
about an experiment.

Training-time code should mostly:

```text
read a prepared batch
apply only necessary runtime randomness
move the batch to device
compute forward, backward, and update
record minimal metrics
```

Deterministic work that can be done once and saved should move out of the
training loop. That includes raw parsing, expensive normalization, format
conversion, indexing, metadata lookup, validation, filtering, fixed
transforms, static feature construction, and schema conversion.

Optimizations must attach to measured bottlenecks. Better throughput is useful
only when it improves decision quality, decision latency, or experiment cost
without weakening scientific contracts, provenance, restartability, or
reproducibility.

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
  groups, splits, indexes, index codecs, Torch adapters, datasource-owned
  caches, and prepared training-data manifests that reference approved fields
  and sources.

ops
  Operation contracts, functional kernels, SampleOps, BatchOps, transforms,
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
  Training also owns native profiling spans, training events, callbacks, sinks,
  and optional framework adapter contracts.

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

Batch-level composition starts as Operation[Batch, Batch] until Sample, Batch,
and Operation contracts are stable. After those contracts are finalized,
Milestone 7 may introduce provisional BatchOp contracts for vectorized,
batch-level, or fused processing. Do not add a broad BatchProgram or universal
batch execution language until repeated concrete needs justify it.
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

## 15. Milestone 7: SampleOps, BatchOps, Transforms, Augmentations, Checks, And Pipelines

Goal:

```text
Implement composable runtime operations over Samples and Batches.
```

Primary packages:

```text
rphys.ops.sample
rphys.ops.batch
rphys.ops.pipelines
```

Key interfaces:

```text
SampleOp
SampleTransform
SampleAugmentation
SampleCheck
BatchOp
BatchTransform
BatchAugmentation
SampleOpPipeline
SampleContext
BatchContext
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

SampleOps remain the correctness and provenance reference path for operations
whose behavior is naturally per sample.

BatchOps are provisional optimization contracts for processing collated fields
in batches. They may replace Python-heavy per-sample transforms when they can
preserve the same scientific meaning, field addressing, masking, alignment,
and provenance.

BatchOps declare read, write, delete, mutation, randomness, device, dtype, and
side-effect behavior over Batch fields. They must not assume model-specific
input layouts, parse selectors in hot loops, build DataLoaders, scan
datasources, export fields, or hide device movement.

When a BatchOp is intended to replace one or more SampleOps, its equivalence
contract must define what remains identical, what is allowed to differ
numerically, and how per-sample diagnostics or provenance can be recovered.

Transform placement follows the training performance objective. Deterministic
transforms that can be materialized should be represented so they can run
before training and be saved through export/materialization flows. Runtime
SampleOps and BatchOps should do only work that depends on loaded context,
epoch/state, stochastic augmentation, or a non-materialized experimental
choice.

The batch should become the primary runtime unit where possible. Prefer bulk
reads, batched collation, batched transforms, vectorized kernels, and
precomputed indices over one parser, metadata lookup, transform pipeline,
allocation-heavy object, or file open per sample.
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
BatchAugmentation may sample one batch-level parameter object or per-sample
parameter objects, but the choice must be explicit and replayable.
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
SampleOpPipeline and BatchOps do not scan datasources, choose splits, export
fields, or hide raw numerical kernels.
BatchOp equivalence, RNG replay, synchronized-field behavior, and provenance
are tested where batch-level execution replaces sample-level behavior.
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
OptimizedDataPlan
MaterializationPlan
MaterializationManifest
ShardManifest
ChunkMetadata
AccessPatternPlan
RecordLayoutMetadata
BatchCostMetadata
BatchSamplerPlan
BatchShapePolicy
StreamingReadPlan
DataLoaderState
DataPathProfile
DataPathBenchmark
```

Adapter rules:

```text
TorchIndexSampleDataset owns a DataSourceIndex, SampleBuilder, optional
SampleOpPipelines, usage/split metadata, and WorkerContextFactory.
__getitem__ resolves an integer position to an IndexItem, derives context,
builds a Sample, applies optional pipelines, and returns a Sample.
It does not scan directories, choose splits, build indexes, export fields, or
format model inputs.
__getitem__ must not become a hidden preprocessing pipeline. Expensive
deterministic work should be moved into materialized training data when it can
be done once and saved.

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
Cache invalidation keys must include the inputs that affect correctness, such
as raw data version, preprocessing code version, configuration, schema, split
definition, random seed when relevant, and library/tool versions where they can
change outputs.
Prepared training data and expensive intermediate caches should be immutable by
version. Do not mutate a training data product in place during experimentation.
```

Optimized data layout planning:

```text
Prepared training data is a derived, immutable, manifest-backed data product
over approved datasource, IO, codec, cache, and operation contracts. It is not
a generic artifact runtime, a second datasource discovery path, or a bypass
around FieldRef, FieldView, SampleBuilder, and provenance rules.

Materialization plans describe which fields, temporal slices, deterministic
operations, shard/chunk boundaries, compression choices, cache limits, and
metadata are written for fast training. If an operation produces the same
result every time and can be saved, the plan should make it eligible for
offline materialization rather than training-loop execution.

Materialization manifests record source identity, raw data version,
preprocessing version, schema, dtypes, record/unit counts, field fingerprints,
operation fingerprints, split definitions, group metadata, shard/chunk list,
offsets/lengths for variable-size records, checksums, compression, runtime
assumptions, software versions, and invalidation inputs.

AccessPatternPlan records how training consumes the data: random indexed reads,
sequential streaming, fixed-size contiguous arrays, memory-mapped layouts,
variable-size offset tables, bucketing, packing, or dynamic batch sizing.

RecordLayoutMetadata and BatchCostMetadata may include length, size, shape,
number of elements, estimated memory footprint, estimated compute cost, shard
assignment, split assignment, optional bucket id, and optional quality/filter
flags. The loader should not need to inspect raw content to know how to batch
records.

Streaming read plans and resumable DataLoader state may be introduced only as
explicit contracts. They must preserve deterministic split/rank/worker
behavior and expose what was skipped, resumed, cached, or re-read.
```

Batch planning rules:

```text
Batch construction is a first-class optimization surface. Dataset/index objects
describe where prepared data lives; sampler plans decide which records form a
batch; collators turn records into Batch fields; BatchOps apply runtime
transforms; device movers transfer whole batches; learners consume whole
batches.

BatchSamplerPlan should support fixed-size batches, cost-aware buckets,
dynamic batch sizing, packing and padding policies, drop/remainder policy,
batch ordering, shuffle granularity, and physical versus effective batch size
metadata.

Batch by training cost when count-based batches create high variance.
Controlled variation is acceptable; unbounded shape, memory, or cost variance
that creates stragglers or compiler/allocator churn should be visible in
metadata and benchmark reports.
```

LitData is relevant prior art for this milestone:

```text
Consider LitData-style ideas such as optimized chunked storage, raw and
optimized streaming, local and remote sources, cache-size limits, compression,
parallel data preparation, shared work queues, distributed-aware streaming,
and resumable dataloader state.

Use these ideas to shape rphys contracts and benchmarks first. Do not add a
LitData runtime dependency or public adapter until the rphys materialization,
cache, and loading contracts are stable enough to evaluate that integration.
```

Implementation order for cache:

```text
1. Deterministic CacheKey and CachePolicy.
2. Local CacheStore with atomic temp-write then commit/rename semantics.
3. Manifest metadata, hit/miss reporting, and invalidation tests.
4. Format-agnostic materialization and shard/chunk manifest contracts.
5. Streaming/resumable loader state contracts.
6. Distributed coordination only after local semantics are stable.
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
Optimized data layout contracts can represent shard/chunk manifests,
compression metadata, cache limits, resumable loader state, and benchmark
summaries without committing to a concrete storage format.
Prepared training data manifests cover source/preprocessing versions, schema,
dtypes, counts, splits, checksums, offsets/lengths, cost metadata, and runtime
assumptions.
Batch planning can use precomputed layout and cost metadata without inspecting
raw content at runtime.
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
TrainingProfiler
TrainingEvent
TrainingEventSink
TrainingCallback
run_train, experimental
```

Rules:

```text
Learner owns mode-specific step semantics and composes Method + optional
Objective + Metrics.
Trainer owns iteration, device movement, grad/no-grad mode, backward, gradient
accumulation, optimizer/scheduler stepping, clipping, precision policy,
distributed context, checkpoint hooks, loop logging, callbacks, and default
profiling spans.
Learner does not call optimizer.step, scheduler.step, checkpoint writers,
dataloader builders, SampleBuilder, datasource adapters, or export ops.
Trainer does not parse input/target/prediction locators, compute scientific
losses, build IndexItems, export outputs, or assume supervised learning.
```

Profiling and callback rules:

```text
Trainer-owned profiling is the default path when it is sufficient to diagnose
training-loop bottlenecks. It records structured spans for dataloader wait,
device transfer, forward, objective/loss, backward, optimizer step,
callbacks/logging, checkpointing, and whole-step timing.

TrainingEvent, TrainingEventSink, TrainingCallback, and TrainingProfiler form a
cohesive observer boundary for native rphys Trainer and framework-backed
execution. Sinks and callbacks consume events; they do not control learner
semantics, parse field selectors, choose data splits, or force a logger or
profiler backend.

PyTorch Lightning Trainer integration is a first-class design target but an
optional dependency. A Lightning adapter should map Lightning loop hooks into
the same rphys event schema and profiling records as the native Trainer,
without making Lightning the canonical training runtime.

Profiler implementations must make synchronization behavior explicit. Default
CPU timing must not hide CUDA synchronization; synchronized device timings are
opt-in and reported as measurement overhead where relevant.
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
Native Trainer and Lightning-backed execution can expose the same provisional
event/profiling schema without making Lightning, Fabric, accelerator, or logger
packages core dependencies.
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
prepared training data manifests and batch-cost metadata
debug/smoke/signal tiers using the same loader path
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

## 23. Milestone 15: Training Performance Profiling And Data-Path Optimization

Goal:

```text
Make training performance diagnosable and optimize the data path without
weakening scientific contracts, provenance, or import boundaries. The objective
is valid experiment decisions per unit cost, not raw throughput in isolation.
```

Primary packages:

```text
rphys.training
rphys.datasources.torch
rphys.datasources.cache
rphys.ops.batch
rphys.io
```

Key interfaces:

```text
TrainingProfiler
TrainingEvent
TrainingEventSink
TrainingCallback
TrainingStepProfile
ResourceSample
RunDecisionMetrics
PrecisionPolicy
CompilePolicy
KernelPolicy
DataPathProfile
DataPathBenchmark
MaterializationPlan
MaterializationManifest
ShardManifest
ChunkMetadata
StreamingReadPlan
DataLoaderState
ExperimentTierSpec
RestartState
BatchOp
BatchTransform
BatchAugmentation
```

Profiling rules:

```text
Trainer-owned profiling is preferred when it can identify the relevant
bottleneck. It should report step_time, dataloader_wait, device_transfer_time,
forward_time, objective_or_loss_time, backward_time, optimizer_step_time,
callback_or_logging_time, checkpoint_time, validation_time, records/sec,
units/sec, useful_units/sec, memory allocated/reserved, CPU utilization, GPU
utilization, unavailable probes, and measurement overhead where applicable.

TrainingEvent sinks and callbacks extend observability when trainer-local spans
are insufficient or when a framework adapter such as Lightning supplies loop
events. Native Trainer and Lightning-backed execution should produce the same
event schema for equivalent phases.

Profiling must avoid hidden CPU-GPU synchronization on the hot path. Any
synchronized timing, memory snapshot, or utilization probe that may perturb
training must be opt-in and documented in the resulting profile.

M15 profiling has four levels:

1. always-on run metrics for coarse timing, useful units, memory, validation,
   checkpointing, and decision cost;
2. data-pipeline benchmarks independent of the model for read time, batch
   construction, transform time, queue wait, worker utilization, and loader
   throughput;
3. optional framework-level profiling for operator timelines, CPU/GPU overlap,
   allocation, kernel time, synchronization points, and shape-dependent
   slowdowns;
4. optional system-level profiling for GPU, CPU, disk, network, host memory,
   shared memory, PCIe/device transfer bandwidth, and process contention.
```

Data-path optimization rules:

```text
Optimized training data is created through explicit materialization plans and
manifests, not implicit caches or datasource adapter side effects.

Materialized layouts should help avoid millions of small files, redundant
decoding, expensive random per-sample IO, and repeated deterministic
preprocessing while preserving source identity, FieldView semantics,
operation fingerprints, split/group metadata, and invalidation inputs.

Data-path benchmarks should use the same loader and prepared-data path that
training uses. Small debug or smoke runs may scale down record counts, shards,
or steps, but they should not switch to a simplified data path that hides
throughput or shape problems.

LitData remains prior art, not a dependency in this milestone. Evaluate its
ideas for chunked optimized storage, raw and optimized streaming, cache-size
limits, compression, parallel data preparation, shared queues,
distributed-aware streaming, and resumable dataloader state before choosing any
concrete rphys storage format or optional adapter.
```

Execution optimization rules:

```text
BatchOps are the preferred path for avoiding Python-heavy per-sample transforms
inside __getitem__ when batch-level, vectorized, or fused execution preserves
the operation contract.

Mixed precision, torch.compile, fused kernels, and backend-specific fast paths
must be represented as explicit policies with fallback behavior, unsupported
case diagnostics, and numerical/scientific equivalence expectations.

Compile and precision policies must not hide dtype/device conversions,
masking/alignment changes, or silent graph breaks that affect interpretation.

Optimization order should normally be: remove offline work from training,
improve prepared-data layout, batch/vectorize transforms, tune loader
parallelism and prefetch, reduce padding/waste/variance, remove synchronization,
improve device transfer, improve compute kernels/precision/compilation, scale
devices, then introduce advanced distributed/sharded systems.

Every optimization must be attached to a measured bottleneck. Data wait points
to storage, workers, prefetch, or preprocessing; transfer time points to pinned
memory, batch format, asynchronous copies, dtype, or size; forward/backward time
points to kernels, precision, shapes, or batch size; optimizer time points to
optimizer implementation or update frequency; checkpoint or validation time
points to cadence, async writes, subsets, or separate evaluation paths.
```

Experiment tiers and restartability:

```text
Support fast experiment tiers through scale over the same data path: debug for
code and shape errors, smoke for end-to-end training, signal for promising
ideas, comparison for fair ablations, and full for final confirmation.

Downstream projects or loom own experiment managers, cost dashboards, and
workflow orchestration. rphys should expose enough typed profiles, prepared-data
metadata, and tier-compatible selectors for those systems to compute
cost-to-decision without adding a generic workflow runtime.

Training systems should assume interruption. Prepared-data writes, shard
generation, logging, checkpointing, and data iteration should support
idempotency, atomic completion markers, partial-shard detection, artifact
version pinning, deterministic splits, restart-safe logging, and resumable
iteration.
```

Observability overhead rules:

```text
Normal training should avoid per-step blocking scalar extraction, printing,
host copies, full validation, expensive logging, large artifact writing, and
debug assertions over full batches. Aggregate, sample, or move expensive
diagnostics to profiling runs when possible.
```

Definition of done:

```text
Synthetic CPU smoke profiles produce structured timing records without optional
GPU, Lightning, logger, or profiler dependencies.
Optional GPU/profile acceptance checks can report utilization, memory, and
synchronized timings with explicit measurement overhead.
Native Trainer and Lightning-backed execution share a provisional event schema.
Data-path benchmarks report dataloader wait, cache hit/miss, materialization,
streaming, queue wait, worker utilization, batch construction time, transform
time, and throughput summaries without machine-specific CI thresholds.
BatchOp tests cover equivalence, replay, provenance, masking, and failure
behavior for optimized transforms.
Batch planning tests cover cost metadata, bucketing, dynamic sizing, controlled
shape variation, packing/padding policy, physical/effective batch size, and
restartable iteration.
Debug, smoke, signal, comparison, and full tiers can share the same prepared
data and loader path while scaling data volume or step count.
AMP, torch.compile, and fused-kernel pathways are documented as policies with
fallback and diagnostic behavior.
```

## 24. Critical Path

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
                    -> M15 training performance profiling and data-path optimization

M6 operation foundations
  -> M7 SampleOps, BatchOps, and pipelines
    -> M8 export and derived DataSources
      -> M13 prediction/evaluation/analysis/reports
```

Testing support grows continuously after M1.

Concrete datasources, codecs, algorithms, models, losses, metrics, and learners
should wait until their public contract layer and synthetic tests are stable.

## 25. First Vertical Slice

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

## 26. Real Datasource Sequence

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

## 27. Deferred Decisions

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
concrete optimized training-data storage format
optional LitData adapter or dependency
advanced framework-specific distributed, accelerator, and logger adapters beyond
the native profiling/event contracts and first-class Lightning event mapping
project configuration systems, workflow engines, and CLIs
worked examples and downstream template projects
advanced publication/report generation
advanced UI/dashboard tooling
```

The roadmap should leave room for these without freezing their APIs early.

## 28. Anti-Patterns

Do not:

```text
let a Torch Dataset scan raw directories
do raw parsing, disk metadata scans, format conversion, fixed normalization, or
expensive validation inside the training loop when it can be done once
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
hide training profiling exclusively inside a logger or callback when the Trainer
can own the relevant timing span directly
force CUDA synchronization or expensive utilization probes on the hot path
without explicit opt-in profiling policy
optimize for raw samples/sec, GPU utilization, or benchmark throughput without
checking whether valid experiment decisions per unit cost improved
put datasource logic inside Learner
let Method, Learner, Trainer, Loss, Objective, or Metric write prediction
artifacts implicitly
make Prediction objects waveform-only
require users to edit rphys internals for extensions
let visualization or analysis write ad hoc files from loaded attributes
add implicit caches
materialize optimized training data without shard/chunk manifests, source
fingerprints, operation fingerprints, split/group metadata, and invalidation
inputs
keep Python-heavy per-sample transforms in __getitem__ when an equivalent
BatchOp can preserve semantics, replay, provenance, and diagnostics
use a separate simplified data path for debug or smoke tiers that hides
throughput, batching, shape, or restartability failures from the real path
introduce project-level configuration or workflow orchestration inside rphys
add generic Stage, ArtifactRef, ArtifactContract, StageContext, BatchProgram, or
universal BatchOperator APIs before concrete repeated library needs justify them
```

## 29. Release Readiness Gates

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
Trainer profiling/event contracts and optional Lightning event mapping are
documented as provisional extension points.
Prepared training data manifest and batch-planning contracts are documented as
provisional extension points.
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
Synthetic training profiles and data-path benchmark summaries can identify
dataloader wait, cache behavior, and step timing without external data.
Debug and smoke tiers use the same prepared-data and loader path as larger
training tiers.
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
Performance profiling, optimized materialization, BatchOp, precision, compile,
and fast-kernel contracts have documented failure and fallback behavior.
Cost-to-decision metrics, restart/resume behavior, and strict cache
invalidation are documented for training-facing contracts.
```

## 30. Immediate Implementation Order

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
   augmentation replay; introduce provisional BatchOp contracts only after
   Sample, Batch, and Operation behavior is stable.
9. Implement SaveOp and derived DataSourceRef round trip.
10. Implement index-backed Torch adapter, explicit local cache primitives, and
    format-agnostic prepared-data manifests, access-pattern plans, and
    cost-aware batch-planning metadata.
11. Implement base Method/Model, Loss/Objective/Metric, Learner/Trainer, and
    prediction/evaluation/analysis contracts, including provisional
    training-event and profiling contracts.
12. Build the synthetic lazy-load-to-batch-to-export-to-reload smoke test.
13. Harden training performance through M15 profiling, data-path benchmarks,
    BatchOp optimization, AMP/compile/fused-kernel policies, and CPU-GPU sync
    audits across debug, smoke, signal, comparison, and full tiers.
```

This order proves the public object model before concrete research components
arrive.

## 31. Final Strategy

Start with contracts, synthetic refs, lazy samples, and export round trips. Do
not start with a real datasource, a model, a trainer, or a workflow system.
Training-performance work should optimize valid experiment decisions per unit
cost by shortening the critical path, moving deterministic work offline,
batching runtime work, and measuring bottlenecks before adding complexity.

The target architecture is:

```text
contracts first
synthetic datasource and lazy sample vertical slice second
operation pipeline and export round trip third
index-backed framework adapter and explicit cache fourth
method/loss/objective/metric/learner/trainer contracts fifth
prediction-as-derived-datasource evaluation and analysis sixth
training performance and optimized data-path hardening seventh
real datasources and concrete research components later
```

Most reference-codebase capabilities should be preserved as object boundaries,
not as shared mutable workflow machinery. They should enter `rphys` through
typed refs, specs, selectors, SampleFields, OperationPipelines, codecs, export
results, derived DataSources, metric tables, and structured reports.
