# rphys Revised Architecture Plan

Version: 3.0 draft  
Scope: structure, design choices, public interfaces, extension model, and lifecycle rules for the `rphys` package  
Relationship: domain-specific remote physiological measurement package built on top of the generic `loom` experiment infrastructure

---

## 1. Executive summary

`rphys` is the domain package for remote physiological measurement research. It should provide the concepts, data objects, field-aware dataset references, codecs, transformations, materialization/export procedures, methods, models, losses, evaluation protocols, analysis utilities, and domain stages needed for remote physiological measurement. It should not duplicate generic experiment infrastructure that belongs in `loom`.

The central boundary is:

```text
loom knows how to run reproducible artifact-based experiments.
rphys knows what a remote physiological measurement experiment is.
```

The architecture should be built around a small set of stable public contracts:

```text
DataKey
FieldSpec
DatasetRef
RecordRef
FieldRef
TemporalIndexSlice
FieldView
FieldValue
Sample
Batch
CollatePolicy
SampleContract
DatasetAdapter
FieldCodec
IndexItem
SampleBuilder
SampleTransform
SampleAugmentation
SampleCheck
SamplePipeline
SampleExporter
MaterializationPipeline
Method
Learner
Trainer
Loss
Metric
EvaluationProtocol
```

The most important design decision is to separate five concerns that are often accidentally merged:

```text
Dataset structure:
  DatasetRef -> RecordRef -> FieldRef

Lazy IO selection:
  FieldRef + optional TemporalIndexSlice -> FieldView -> IndexItem

Runtime data operations:
  Sample -> Sample through SampleTransform and SampleAugmentation

Offline formatting/materialization/export:
  FieldViews -> SampleBuilder -> optional SamplePipeline -> SampleExporter
  -> new FieldRefs, RecordRefs, and DatasetRefs

Learning and evaluation logic:
  Method, Learner, Trainer, Prediction Samples, Metrics, and EvaluationProtocols
```

The index/view/slice system is only a lazy IO description. It is not a transform system, not an augmentation system, not a formatting system, and not a learning-method abstraction.

Formatting is not a component of `rphys.datasets`. Dataset code discovers, validates, filters, splits, and indexes existing logical fields. Formatting is an offline materialization/export process: it loads fields lazily through FieldViews, optionally applies deterministic SampleTransforms, then writes data to a target format or creates symlinks and emits new FieldRefs. The result is a new DatasetRef or manifest, not a special dataset-layer side effect.

The runtime data object is a mutable, generic `Sample` containing arbitrary typed fields. Video is a standard field, not a privileged special case. A dataset can expose RGB video, BVP, timestamps, landmarks, meshes, masks, quality traces, calibration, labels, or custom embeddings through the same field interface.

Predictions are also Samples or Batches. Evaluation metrics consume prediction and reference fields by key. This allows the same evaluation machinery to support waveform prediction, heart-rate regression, representation learning, signal-processing baselines, masks, landmarks, quality prediction, and multi-task models.

## 2. Design goals

`rphys` should be:

```text
Domain-specific
  Contains remote physiological measurement concepts such as video, BVP, PPG,
  face ROI, timestamps, landmarks, masks, meshes, physiological signals,
  rPPG models, heart-rate metrics, and cross-dataset protocols.

Built on loom
  Uses loom for generic config, artifacts, pipeline execution, stage execution,
  recipe expansion, run stores, artifact stores, executors, and resume logic.

Field-centric
  Represents every loadable or transformable data item as a logical field.
  Video, BVP, timestamps, landmarks, meshes, masks, labels, predictions,
  quality traces, and custom values use the same public field interface.

Reference-oriented
  Uses DatasetRef, RecordRef, FieldRef, FieldView, and IndexItem to describe
  dataset structure and lazy IO without loading data.

Lazy by default
  Dataset adapters emit serializable FieldRefs inside RecordRefs. IndexItems
  contain FieldViews. A FieldView may define an index-based TemporalIndexSlice.
  IO is not incurred until a SampleBuilder loads an IndexItem.

Composable
  Dataset discovery, filtering, indexing, sample building, runtime pipelines,
  export/materialization, methods, learners, training loops, evaluation, and
  analysis are separable.

Pipeline-friendly
  Runtime operations share a common Sample -> Sample interface, so they can be
  composed into SamplePipelines for training, evaluation, inference, and offline
  materialization.

Role-organized
  Transform implementations should be organized by role first where useful:
  deterministic processing, augmentation, extraction, checks, and export.
  Modality-specific code lives underneath those roles.

Explicit
  Missing fields, unsupported slices, ambiguous schemas, mismatched layouts,
  unsupported collation, and codec failures should fail loudly by default.

Mutable on the hot path
  Runtime Sample containers are mutable by default to avoid unnecessary object
  copying during training-time pipelines.

Extensible
  Users should be able to add fields, datasets, codecs, modalities, transforms,
  augmentations, extractors, exporters, methods, models, learners, losses,
  metrics, stages, and recipes without editing rphys internals.

Suitable for multiple learning styles
  Supports standard supervised learning, pretraining, self-supervised learning,
  contrastive learning, masked modeling, signal-processing methods, classical
  methods, and neural methods.
```

## 3. Non-goals

`rphys` should not own generic infrastructure already handled by `loom`.

Do not put these in `rphys`:

```text
configuration composition engine
recursive _target_ instantiation engine
recipe expansion mechanism
pipeline DAG runner
run store
artifact store base implementation
stage status machine
resume planner
executor implementation
sweep runner
run locking
generic ArtifactRef definitions
generic ResourceRef definitions, if provided by loom
generic Record/Manifest infrastructure, if provided by loom
```

`rphys` may define domain-specific stages and artifact payload schemas, but not the generic machinery that executes pipeline graphs.

---

## 4. Relationship to loom

`rphys` depends on `loom`. `loom` must not depend on `rphys`.

Recommended boundary:

```text
loom owns:
  ResourceRef
  ArtifactRef
  Config composition
  _target_ instantiation
  _recipe_ expansion
  PipelineSpec
  StageSpec
  Stage protocol
  StageContext
  ArtifactStore
  RunStore
  Executors
  Resume/fingerprint logic
  Generic Record/Manifest infrastructure if provided by loom

rphys owns:
  Domain field naming conventions
  FieldSpec and rphys field schemas
  DatasetRef and RecordRef wrappers/conventions over generic loom records/manifests
  FieldRef, FieldView, and TemporalIndexSlice semantics for rphys data
  Video/signal/timestamp/landmark/mask/mesh data objects
  Field-aware codecs
  Remote-phys dataset adapters
  Record filters, field filters, and index builders
  Runtime Sample and Batch objects
  SampleTransform, SampleAugmentation, SampleCheck, and SamplePipeline implementations
  Export/materialization procedures for formatting or symlinking datasets
  rPPG and physiology ops
  Methods, models, learners, losses, and metrics
  Evaluation protocols and reports
  Analysis utilities
  Domain recipes
  Concrete rphys pipeline stages
```

A stage class can live in `rphys`, but stage execution belongs to `loom`.

Example:

```yaml
pipeline:
  stages:
    - name: scan_dataset
      target:
        _target_: rphys.stages.datasets.ScanDatasetStage

    - name: materialize_dataset
      target:
        _target_: rphys.stages.materialization.MaterializeDatasetStage

    - name: train
      target:
        _target_: rphys.stages.training.TrainRPhysMethodStage
```

If loom already provides generic `Record` and `Manifest` classes, `rphys` should not duplicate their generic mechanics. Instead, `rphys` should define the domain semantics of DatasetRefs, RecordRefs, FieldRefs, fields, schemas, and indexes that may be serialized into loom manifests or artifact payloads.

## 5. Revised conceptual flow

The full data flow should be described as:

```text
Native dataset
  -> DatasetAdapter scans a source
  -> DatasetRef describes the dataset collection and schema
  -> DatasetRef returns RecordRefs for individual records/items
  -> RecordRefs expose arbitrary FieldRefs
  -> Dataset filters and splitters select RecordRefs
  -> IndexBuilder creates IndexItems with FieldViews
  -> each FieldView has a FieldRef and optional TemporalIndexSlice
  -> SampleBuilder lazily loads FieldViews through codecs
  -> loaded Sample contains mutable FieldValues
  -> SamplePipeline applies SampleTransforms, SampleAugmentations, and SampleChecks
  -> collate converts Samples into Batch with the same field API
  -> Method predicts fields
  -> Learner defines training behavior if the method is trainable
  -> Trainer orchestrates device, epoch, checkpoint, and loop mechanics
  -> Predictions are Samples or Batches containing prediction fields
  -> EvaluationProtocol aggregates Samples and computes Metrics
  -> Analysis consumes reports and artifacts
```

A separate offline materialization/export flow should be available:

```text
DatasetRef or DatasetView
  -> IndexItems with FieldViews
  -> SampleBuilder lazily loads original fields
  -> optional deterministic SamplePipeline performs processing/extraction
  -> SampleExporter writes fields to target codecs or creates symlinks
  -> emitted FieldRefs replace or augment original FieldRefs
  -> new RecordRefs and DatasetRef are written as a manifest/artifact
```

The central corrections from earlier drafts are:

```text
DatasetRef/RecordRef/FieldRef logic describes dataset structure.
IndexItem/FieldView/TemporalIndexSlice logic describes lazy IO only.
SampleTransform/SampleAugmentation logic describes runtime Sample modification.
SampleExporter/MaterializationPipeline logic describes offline formatting/export.
Filtering logic describes constructing records/views/indexes, not runtime transforms.
```

Self-supervised or contrastive samples can be created without changing the index model. The index can define a wider index-based slice, incur IO once, and then a runtime SampleAugmentation can split the loaded window into subwindows or views.

## 6. Core terminology

### 6.1 DatasetRef

A `DatasetRef` is a serializable reference to a dataset collection, dataset view, or manifest-like object. It describes the dataset schema, dataset-level metadata, and the available RecordRefs.

It answers:

```text
What dataset or dataset view is this?
What records/items are available?
What fields can records expose?
What schema and metadata conventions apply?
Where is the manifest or backing storage?
```

A `DatasetRef` should not load videos, signals, landmarks, or other field payloads. It may be backed by a loom Manifest, a local manifest file, or another artifact payload.

### 6.2 RecordRef

A `RecordRef` is a serializable reference to one logical dataset item or entry. Depending on the dataset, a record might represent a subject trial, session, video recording, physiological recording, clip, or other unit of indexing.

A RecordRef contains:

```text
record_id
mapping of DataKey -> FieldRef
record-level metadata
optional validation/status metadata
```

A RecordRef should not contain loaded data. It exposes FieldRefs for the logical fields available for that record.

### 6.3 FieldSpec

A `FieldSpec` declares what a logical field means and how it should behave. It belongs to dataset schemas, standard rphys field registries, or custom extension packages.

It answers:

```text
What is this field called?
What data type does it contain?
What runtime object should it load into?
What schema/layout/coordinate frame does it follow?
Can it be temporally sliced?
How should it collate?
What metadata is required?
```

### 6.4 FieldRef

A `FieldRef` is a serializable reference to a complete logical field. It is emitted by dataset adapters and stored in RecordRefs/manifests.

A `FieldRef` should not contain loaded tensors, open file handles, decoded videos, or runtime objects. It describes how to locate and interpret a field. Each FieldRef can specify its own codec, selector, schema, and metadata.

### 6.5 TemporalIndexSlice

A `TemporalIndexSlice` is an index-based temporal slice over a field. For now, this is the only supported slice type.

It is not time-based. It is not spatial. It is not a general region. It only describes temporal indices in the native index space of the field.

### 6.6 FieldView

A `FieldView` is a lazy IO request. It combines a `FieldRef` with an optional `TemporalIndexSlice`.

```text
FieldView = FieldRef + optional TemporalIndexSlice
```

If the slice is `None`, the complete logical field is loaded.

### 6.7 IndexItem

An `IndexItem` is the unit consumed by a `SampleBuilder`. It defines which field views should be loaded to create one runtime `Sample`.

The index item is only a lazy IO request. It is not a transform plan, formatting plan, or learning-method plan.

### 6.8 FieldValue

A `FieldValue` is a loaded runtime field inside a `Sample`. It wraps the actual value and stores field-level metadata, schema, data type, and collation policy.

### 6.9 Sample

A `Sample` is the central mutable runtime container. It contains arbitrary named `FieldValue`s and sample-level metadata.

All runtime transforms operate on Samples:

```text
Sample -> Sample
```

### 6.10 Batch

A `Batch` is the result of collating multiple Samples. It should expose the same field access API as `Sample`.

### 6.11 Ops

Ops are pure or mostly pure functional operations. They perform tensor/data computation without IO, Sample plumbing, manifests, records, or hidden randomness.

### 6.12 SampleTransform

A `SampleTransform` is a runtime data operation:

```text
Sample -> Sample
```

It may read one or more fields and write one or more fields.

### 6.13 SampleAugmentation

A `SampleAugmentation` is a stochastic `SampleTransform` with explicit reproducible parameter sampling.

### 6.14 SampleCheck

A `SampleCheck` validates a Sample and either raises, annotates, or warns. It is not the normal mechanism for filtering datasets.

### 6.15 SampleExporter

A `SampleExporter` is an offline export-style operation used during materialization or formatting. It writes selected Sample fields to a target location through codecs, creates symlinks, or otherwise emits new FieldRefs.

A SampleExporter has IO side effects and is not a hot-path SampleTransform.

### 6.16 MaterializationPipeline

A `MaterializationPipeline` is an offline process that loads FieldViews, applies optional deterministic SampleTransforms, and exports selected fields to produce new RecordRefs and DatasetRefs.

Dataset formatting is a MaterializationPipeline use case.

### 6.17 Method

A `Method` is a prediction or estimation algorithm. It consumes Samples or Batches and emits prediction fields. A method can wrap a neural model, signal-processing algorithm, classical estimator, or hybrid pipeline.

### 6.18 Learner

A `Learner` defines training and validation steps for a learning style, such as supervised learning, contrastive learning, masked modeling, or self-supervised pretraining.

### 6.19 Trainer

A `Trainer` handles loops, device movement, gradient stepping, checkpointing, logging hooks, and distributed mechanics. It should not know the details of the learning style.

## 7. Package structure

Recommended broad package structure:

```text
src/rphys/
  __init__.py
  conventions.py
  errors.py
  registry.py
  types.py

  data/
    core/
      keys.py
      fields.py
      sample.py
      batch.py
      collate.py
      contracts.py
      schemas.py
      tensor_tree.py

    modalities/
      video/
      signal/
      timestamps/
      landmarks/
      masks/
      meshes/
      roi/
      labels/
      events/
      arrays/
      metadata/

  io/
    core/
      field_refs.py
      views.py
      slices.py
      codecs.py
      registry.py
      probing.py
      cache.py

    codecs/
      video/
      signal/
      timestamps/
      landmarks/
      masks/
      meshes/
      arrays/
      metadata/

  datasets/
    core/
      adapters.py
      dataset_refs.py
      record_refs.py
      schemas.py
      manifests.py
      views.py
      indexing.py
      sample_specs.py
      validation.py

    discovery/
    filters/
    splits/
    validation/
    adapters/

  ops/
    tensor/
    temporal/
    geometry/
    video/
    signal/
    landmarks/
    masks/
    meshes/
    physiology/
    rppg/
    multimodal/

  transforms/
    core/
      base.py
      context.py
      pipeline.py
      contracts.py
      augmentation.py
      checks.py
      export.py
      roles.py

    deterministic/
      video/
      signal/
      landmarks/
      masks/
      meshes/
      multimodal/
      rppg/

    augmentation/
      video/
      signal/
      landmarks/
      masks/
      meshes/
      multimodal/

    extraction/
      video/
      signal/
      landmarks/
      masks/
      meshes/
      multimodal/
      rppg/

    checks/
      video/
      signal/
      landmarks/
      masks/
      meshes/
      multimodal/

    export/
      video/
      signal/
      timestamps/
      landmarks/
      masks/
      meshes/
      arrays/
      metadata/
      symlink.py

  methods/
    core/
    neural/
    signal_processing/
    self_supervised/
    classical/

  models/
    core/
    architectures/
    layers/
    heads/
    adapters/

  losses/
    core/
    waveform/
    spectral/
    temporal/
    physiological/
    contrastive/
    multitask/
    regularization/

  training/
    learners/
    trainers/
    objectives/
    input_adapters.py
    target_adapters.py
    optim.py
    checkpointing.py

  evaluation/
    predictions.py
    metrics/
    aggregation/
    protocols.py
    reports.py

  analysis/
    plots.py
    tables.py
    statistics.py
    reports.py
    diagnostics.py

  recipes/
    data.py
    preprocessing.py
    materialization.py
    training.py
    evaluation.py
    experiments.py

  stages/
    datasets.py
    materialization.py
    preprocessing.py
    training.py
    evaluation.py
    analysis.py
    inference.py

  testing/
    synthetic_data.py
    fixtures.py
    smoke.py
```

Important package-structure decisions:

```text
datasets/
  Dataset discovery, DatasetRef/RecordRef construction, schemas, validation,
  filters, splits, and index construction. No dataset formatting subpackage.

transforms/
  Runtime Sample -> Sample operations, stochastic augmentations, extraction
  transforms, checks, and export-style operations used by materialization.

stages/materialization.py
  Offline artifact-producing stages for formatting, symlinking, converting,
  and materializing fields into new DatasetRefs/manifests.
```

This structure is broad, but the stable public API should remain small. Deep modality-specific modules are implementation locations, not necessarily public extension contracts.

## 8. Public API boundary

The package should explicitly document stable public contracts. Users should extend `rphys` through these contracts rather than importing unstable internals.

Stable public contracts should include:

```text
rphys.data
  DataKey
  FieldSpec
  FieldRef
  TemporalIndexSlice
  FieldView
  FieldValue
  Sample
  Batch
  DataObjectBase
  CollatePolicy
  SampleContract
  BundleSpec

rphys.io
  FieldCodec
  CodecRegistry
  CodecCapabilities

rphys.datasets
  DatasetRef
  RecordRef
  DatasetAdapter
  DatasetSchema
  RecordFilter
  FieldFilter
  IndexItemFilter
  IndexBuilder
  IndexItem
  SampleSpec

rphys.transforms
  TransformRole
  SampleTransform
  BaseSampleTransform
  SampleAugmentation
  SampleCheck
  SamplePipeline
  SampleContext
  PipelineContext
  SampleExporter
  MaterializationPipeline

rphys.methods
  Method
  TrainableMethod
  SignalProcessingMethod
  TorchMethod

rphys.training
  Learner
  SupervisedLearner
  SelfSupervisedLearner
  ContrastiveLearner
  MaskedModelingLearner
  Trainer
  InputAdapter
  TargetAdapter

rphys.losses
  TensorLoss
  FieldLoss
  BatchLoss
  CompositeLoss

rphys.evaluation
  Metric
  SampleAggregator
  MetricAggregator
  EvaluationProtocol
  MetricResult
```

Deep implementation classes can be public in practice, but these contracts should be the main extension surface.

## 9. DataKey naming policy

A `DataKey` is a structured string identifying a logical field.

Recommended grammar:

```text
<namespace>.<semantic>[.<variant>][.<role>]
```

Standard namespaces:

```text
video
signal
timestamps
face
body
camera
label
prediction
quality
annotation
view
custom
```

Examples:

```text
video.rgb
video.rgb.raw
video.rgb.face_crop
video.nir
video.depth
video.thermal

signal.bvp
signal.bvp.reference
signal.bvp.predicted
signal.ecg
signal.ppg
signal.respiration

timestamps.video
timestamps.signal.bvp

face.landmarks.mediapipe_468
face.landmarks.openface_68
face.mesh.flame
face.mask.skin
face.mask.face
face.roi.left_cheek
face.roi.right_cheek
face.roi.forehead

label.hr
label.respiration_rate

prediction.signal.bvp
prediction.hr
prediction.embedding.video
prediction.quality.signal_snr

quality.face_visibility
quality.signal_snr
quality.motion

view.a.video.rgb
view.b.video.rgb

custom.my_project.some_field
```

User-defined fields should use:

```text
custom.<project_or_package>.<field_name>
```

This prevents collisions with future standard `rphys` fields.

Design rules:

```text
DataKey should be usable as a string-like key.
Standard keys should be available as constants.
Custom keys must not require editing rphys internals.
Transforms should accept configurable input/output keys.
Field aliases may be supported later but should not be required initially.
```

---

## 10. Field model

The field model should separate declaration, reference, lazy view, and loaded value.

### 10.1 FieldSpec

```python
@dataclass(slots=True)
class FieldSpec:
    key: DataKey
    data_type: str
    runtime_type: type | str | None = None
    schema: str | None = None
    description: str = ""
    supports_temporal_index_slice: bool = False
    default_collate_policy: CollatePolicy | None = None
    required_metadata: tuple[str, ...] = ()
    layout: str | None = None
    axes: tuple[str, ...] | None = None
    units: str | None = None
    role: str | None = None
```

Example:

```python
FieldSpec(
    key=DataKey("video.rgb"),
    data_type="video",
    runtime_type="rphys.data.modalities.video.VideoData",
    schema="rgb_video_tchw.v1",
    supports_temporal_index_slice=True,
    default_collate_policy=CollatePolicy.STACK,
    layout="TCHW",
    axes=("time", "channel", "height", "width"),
    role="raw",
)
```

### 10.2 FieldRef

```python
@dataclass(slots=True)
class FieldRef:
    key: DataKey
    data_type: str
    ref: ResourceRef | None = None
    codec_key: str | None = None
    selector: Mapping[str, Any] | None = None
    schema: str | None = None
    metadata: MutableMapping[str, Any] = field(default_factory=dict)
```

A `FieldRef` points to a complete logical field. Multiple logical fields may point to the same physical resource with different selectors.

Example:

```python
FieldRef(
    key=DataKey("signal.bvp"),
    data_type="signal",
    ref=ResourceRef(uri="/data/subject01/signals.csv"),
    codec_key="signal.csv.v1",
    selector={"column": "bvp"},
    schema="bvp_signal.v1",
    metadata={"sample_rate": 64.0, "units": "a.u."},
)
```

### 10.3 TemporalIndexSlice

```python
@dataclass(slots=True)
class TemporalIndexSlice:
    start: int
    stop: int | None = None
    length: int | None = None
    step: int = 1
```

Rules:

```text
Only index-based temporal slices are supported for now.
Use half-open semantics: [start, stop).
Exactly one of stop or length should be provided.
start must be non-negative.
step must be positive.
A slice is interpreted in the native temporal index space of the field.
No time-based or spatial slicing is supported initially.
```

### 10.4 FieldView

```python
@dataclass(slots=True)
class FieldView:
    field_ref: FieldRef
    temporal_slice: TemporalIndexSlice | None = None
```

Rules:

```text
FieldView is a lazy IO request.
FieldView should be serializable as part of an index.
FieldView should not contain loaded data.
None slice means load the complete logical field.
Unsupported slicing should fail loudly.
```

### 10.5 FieldValue

```python
@dataclass(slots=True)
class FieldValue:
    value: Any
    data_type: str | None = None
    schema: str | None = None
    metadata: MutableMapping[str, Any] = field(default_factory=dict)
    collate_policy: CollatePolicy | None = None
```

Rules:

```text
Standard rphys fields should usually contain DataObjectBase payloads.
Custom fields may contain arbitrary tensor-like or serializable payloads.
FieldValue metadata describes the field, not the whole sample.
FieldValue may store collate policy overrides.
```

---

## 11. Field attributes and metadata

Fields need enough metadata to make pipelines explicit and interpretable.

A field should be able to specify:

```text
key
data_type
runtime_type
schema
role
layout
axes
dtype
units
sample_rate
fps
temporal_axis
supports_temporal_index_slice
spatial_coordinate_frame
temporal_coordinate_frame
collate_policy
codec_key
selector
provenance
```

Examples:

```text
video.rgb
  data_type: video
  runtime_type: VideoData
  schema: rgb_video_tchw.v1
  role: raw
  layout: TCHW
  temporal_axis: 0
  supports_temporal_index_slice: true
  collate_policy: stack

signal.bvp
  data_type: signal
  runtime_type: SignalData
  schema: bvp_signal.v1
  role: reference
  units: a.u.
  temporal_axis: 0
  supports_temporal_index_slice: true

face.landmarks.mediapipe_468
  data_type: landmarks
  runtime_type: LandmarkData
  schema: mediapipe_face_468.v1
  coordinate_frame: video.rgb.pixel
  temporal_axis: 0
  supports_temporal_index_slice: true
```

Operations should fail loudly if required attributes are missing. For example, a spatial crop that consumes landmarks should not proceed if the landmark coordinate frame is unknown.

---

## 12. Metadata versus fields

Use this rule:

```text
If it is a payload that can be loaded, sliced, transformed, validated, collated,
saved, used by a model, used by a loss, or used by a metric, make it a field.

If it only describes the record or sample globally, make it metadata.
```

Usually metadata:

```text
record_id
sample_id
item_id
dataset
subject_id
session_id
trial_id
split
scenario
protocol
window_start_index
window_stop_index
source dataset version
```

Usually fields:

```text
video
BVP
PPG
ECG
timestamps
landmarks
meshes
masks
ROI traces
quality time series
per-frame labels
heart-rate labels used as targets
camera calibration if used by transforms/models
skin segmentation masks
predictions
embeddings
```

Ambiguous examples:

```text
skin tone:
  metadata if used only for stratified reporting
  field if used as input, target, conditioning variable, or fairness objective

camera intrinsics:
  metadata if purely descriptive
  field if consumed by transforms/models

quality score:
  metadata if one scalar used only for filtering/reporting
  field if per-frame, collated, or used by models/losses/metrics
```

---

## 13. Runtime data objects

Typed data objects live inside `FieldValue.value`. They provide validation, tensor traversal, device movement, and class-level collation.

Common base:

```python
class DataObjectBase:
    schema: str | None
    metadata: MutableMapping[str, Any]

    def validate(self) -> None:
        ...

    def map_tensors_(self, fn) -> Self:
        ...

    def to(self, device, *, non_blocking: bool = True) -> Self:
        ...

    def cpu(self) -> Self:
        ...

    def detach(self) -> Self:
        ...

    def pin_memory(self) -> Self:
        ...

    @classmethod
    def collate(
        cls,
        values: Sequence[Self],
        *,
        policy: CollatePolicy,
        context: CollateContext,
    ) -> Self:
        ...
```

Recommended standard data objects:

```text
VideoData
SignalData
TimestampData
LandmarkData
MaskData
MeshData
ROIData
LabelData
EventData
ArrayData
MetadataData
```

### 13.1 VideoData

Recommended fields:

```text
frames
timestamps
fps
layout
color_space
valid_mask
metadata
```

Shape convention:

```text
single video: [T, C, H, W]
batched video: [B, T, C, H, W]
```

### 13.2 SignalData

Recommended fields:

```text
values
timestamps
sample_rate
units
signal_type
valid_mask
metadata
```

Shape convention:

```text
single signal: [T] or [C, T]
batched signal: [B, T] or [B, C, T]
```

### 13.3 TimestampData

Recommended fields:

```text
values
units
clock
source
metadata
```

### 13.4 LandmarkData

Recommended fields:

```text
points
visibility/confidence
timestamps
schema
coordinate_frame
metadata
```

Shape convention:

```text
single landmark sequence: [T, N, 2] or [T, N, 3]
batched landmark sequence: [B, T, N, 2] or [B, T, N, 3]
```

### 13.5 MaskData

Recommended fields:

```text
mask
timestamps
coordinate_frame
classes or mask_type
metadata
```

### 13.6 MeshData

Recommended fields:

```text
vertices
faces
topology
pose, optional
timestamps
coordinate_frame
schema
metadata
```

Mesh support can be implemented later, but the architecture should reserve the modality and field model.

---

## 14. Sample and Batch

### 14.1 Sample

`Sample` is the central mutable runtime object.

```python
@dataclass(slots=True)
class Sample:
    fields: MutableMapping[DataKey, FieldValue]
    metadata: MutableMapping[str, Any] = field(default_factory=dict)

    def has(self, key: str | DataKey) -> bool:
        ...

    def field(self, key: str | DataKey) -> FieldValue:
        ...

    def get(self, key: str | DataKey, default: Any = None) -> Any:
        ...

    def require(
        self,
        key: str | DataKey,
        expected_type: type | tuple[type, ...] | None = None,
    ) -> Any:
        ...

    def set_field(
        self,
        key: str | DataKey,
        value: Any,
        *,
        data_type: str | None = None,
        schema: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        collate_policy: CollatePolicy | None = None,
    ) -> Self:
        ...

    def delete_field(self, key: str | DataKey) -> Self:
        ...

    def rename_field(self, old_key: str | DataKey, new_key: str | DataKey) -> Self:
        ...

    def shallow_copy(self) -> "Sample":
        ...

    def map_tensors_(self, fn) -> Self:
        ...
```

Recommended semantics:

```text
sample.get(key) returns the payload value.
sample.field(key) returns the FieldValue wrapper.
sample.require(key, type) returns the payload or raises.
sample.set_field(...) mutates and returns the same Sample.
```

### 14.2 Mutability

Samples should be mutable by default.

Rationale:

```text
Runtime pipelines may run on the hot training path.
Avoiding unnecessary container copies is important.
Most transforms naturally update fields in place.
```

Rules:

```text
Transforms may mutate the Sample they receive.
Transforms should declare mutates=True if they mutate.
Branching pipelines must explicitly copy Samples before divergent mutation.
No transform should silently mutate fields not declared in its output contract.
In-place tensor mutation should be explicit.
Debug/provenance modes may optionally snapshot metadata or shallow-copy containers.
```

Use PyTorch-like naming conventions in ops:

```text
normalize_video(...)
  may allocate/return a new tensor

normalize_video_(...)
  mutates the tensor in place
```

### 14.3 Batch

`Batch` should be Sample-like.

```python
@dataclass(slots=True)
class Batch(Sample):
    batch_size: int = 0
```

If inheritance is undesirable, duplicate the same public field access API.

Downstream code should use the same access pattern:

```python
video = sample.require("video.rgb", VideoData)
video = batch.require("video.rgb", VideoData)
```

---

## 15. Collation

Collation converts:

```text
Sequence[Sample] -> Batch
```

The output Batch should preserve the same public field access API as Sample.

Collation is a fundamental design decision. The exact policy list can grow later, but the system must be field-level and explicit from the beginning.

### 15.1 CollatePolicy

Recommended initial concepts:

```text
STACK
  Require equal shapes and stack along batch dimension.

PAD_TEMPORAL
  Pad temporal dimension and record lengths or masks.

LIST
  Keep Python list.

ALLOW_MISSING
  Permit missing optional fields.

DROP_FIELD_IF_ANY_MISSING
  Omit field from batch if not present in all samples.

CUSTOM
  Delegate to data object or custom callable.
```

Rules:

```text
The collator checks FieldValue.collate_policy first.
If absent, it checks the runtime data object's default policy.
If still absent, it uses strict defaults.
Shape mismatch fails unless policy explicitly permits padding/listing.
Missing fields fail unless policy explicitly permits optional/missing fields.
Padding should produce lengths or validity masks.
Metadata collation should be deterministic and documented.
```

### 15.2 Padding

Padding should not silently truncate or reshape data. If temporal padding is used, the batch should preserve validity information.

Options:

```text
Store valid lengths/masks inside the data object.
Store an adjacent field such as video.rgb.valid_mask.
```

Preferred default:

```text
For standard typed data objects, store lengths/masks inside the data object.
```

### 15.3 Metadata collation

Sample metadata should collate predictably.

Examples:

```python
batch.metadata["record_id"] == ["s01/t01", "s02/t01", ...]
batch.metadata["subject_id"] == ["s01", "s02", ...]
batch.metadata["item_id"] == ["item000", "item001", ...]
```

Numeric metadata can remain lists initially unless a specific policy promotes it to tensors.

---

## 16. DatasetRef, RecordRef, and arbitrary fields

Dataset adapters should expose logical fields through DatasetRefs and RecordRefs, not only resources.

A `DatasetRef` defines the dataset or dataset view structure. It should provide access to individual `RecordRef`s and the schema for the fields that those records may expose.

Conceptual interface:

```python
@dataclass(slots=True)
class DatasetRef:
    dataset_id: str
    schema: DatasetSchema
    records_uri: str | None = None
    metadata: MutableMapping[str, Any] = field(default_factory=dict)

    def records(self) -> Iterable[RecordRef]:
        ...

    def record(self, record_id: str) -> RecordRef:
        ...
```

A `RecordRef` defines an individual item/entry in the dataset. It exposes a mapping of logical DataKeys to FieldRefs:

```python
@dataclass(slots=True)
class RecordRef:
    record_id: str
    fields: Mapping[DataKey, FieldRef]
    metadata: MutableMapping[str, Any] = field(default_factory=dict)

    def has_field(self, key: str | DataKey) -> bool:
        ...

    def field(self, key: str | DataKey) -> FieldRef:
        ...

    def require_field(self, key: str | DataKey) -> FieldRef:
        ...
```

A RecordRef should look conceptually like:

```python
RecordRef(
    record_id="ubfc/s01/t01",
    fields={
        "video.rgb": FieldRef(...),
        "signal.bvp": FieldRef(...),
        "timestamps.video": FieldRef(...),
        "face.landmarks.mediapipe_468": FieldRef(...),
        "face.mesh.flame": FieldRef(...),
        "face.mask.skin": FieldRef(...),
    },
    metadata={
        "dataset": "ubfc",
        "subject_id": "s01",
        "trial_id": "t01",
    },
)
```

Default video fields are just standard field keys. They should not receive special loading paths.

Each FieldRef can specify its own codec:

```python
FieldRef(
    key=DataKey("face.landmarks.mediapipe_468"),
    data_type="landmarks",
    ref=ResourceRef(uri="/cache/ubfc/s01/t01/landmarks.parquet"),
    codec_key="landmarks.mediapipe_parquet.v1",
    schema="mediapipe_face_468.v1",
)
```

Dataset adapter interface:

```python
class DatasetAdapter(Protocol):
    dataset_name: str

    def schema(self) -> DatasetSchema:
        ...

    def scan(self, source: DatasetSource) -> DatasetRef | Iterable[RecordRef]:
        ...

    def validate_record(self, record: RecordRef) -> ValidationReport:
        ...
```

The adapter may return a DatasetRef directly or stream RecordRefs that a stage packages into a DatasetRef/manifest. The public behavior should still be DatasetRef -> RecordRef -> FieldRef.

Dataset schema:

```python
@dataclass(slots=True)
class DatasetSchema:
    dataset_name: str
    fields: Mapping[DataKey, FieldSpec]
    metadata: Mapping[str, MetadataSpec]
```

Extension path for arbitrary additional fields:

```text
1. Define a DataKey.
2. Add a FieldSpec to the dataset schema.
3. Emit a FieldRef from the RecordRef.
4. Provide a FieldCodec if the field is stored externally.
5. Request the field in a SampleSpec or IndexBuilder.
6. Consume it through sample.require(field_key).
```

This supports:

```text
landmarks
meshes
masks
camera calibration
quality traces
auxiliary physiological signals
optical flow
embeddings
custom labels
annotations
```

without modifying the core Sample, dataset, or IO interfaces.

## 17. Dataset filtering and index construction

Filtering should happen before finalizing the index. Filtering is not a SampleTransform.

Use separate concepts:

```text
RecordFilter
  Operates on records and metadata before indexing.

FieldFilter
  Operates on field availability, specs, and metadata.

IndexItemFilter
  Operates on candidate index items and their slice/view metadata.
```

Examples:

```text
DatasetIn
SubjectIn
SubjectNotIn
HasField
HasAllFields
HasAnyField
MinDuration
OfficialSplit
QualityAtLeast
HasPrecomputedLandmarks
WindowHasFaceCoverage
WindowHasSignalCoverage
```

Rules:

```text
Training datasets should not repeatedly decode invalid windows just to drop them.
If a window should be excluded, exclude it during index construction.
Runtime validation can still catch errors, but it should not be the main filter path.
```

---

## 18. IndexItem, FieldView, and lazy IO

An `IndexItem` is the unit consumed by a SampleBuilder.

```python
@dataclass(slots=True)
class IndexItem:
    item_id: str
    record_id: str
    fields: Mapping[DataKey, FieldView]
    metadata: MutableMapping[str, Any]
```

The IndexBuilder consumes DatasetRefs/RecordRefs and produces IndexItems. It converts selected RecordRef fields into FieldViews by attaching an optional TemporalIndexSlice.

Example:

```python
IndexItem(
    item_id="ubfc/s01/t01/window_007",
    record_id="ubfc/s01/t01",
    fields={
        "video.rgb": FieldView(video_ref, TemporalIndexSlice(start=900, length=300)),
        "signal.bvp": FieldView(bvp_ref, TemporalIndexSlice(start=1920, length=640)),
        "timestamps.video": FieldView(ts_ref, TemporalIndexSlice(start=900, length=300)),
        "face.landmarks.mediapipe_468": FieldView(lm_ref, TemporalIndexSlice(start=900, length=300)),
    },
    metadata={
        "subject_id": "s01",
        "split": "train",
    },
)
```

Rules:

```text
The RecordRef defines what fields exist for a record.
The IndexItem defines which field views to load.
The FieldView defines whether the complete field or an index-based temporal slice is loaded.
The index item does not define how to transform data.
The index item does not define formatting/export behavior.
The index item does not define stochastic views.
The index item does not define contrastive positives/negatives initially.
```

Self-supervised or contrastive samples can be built by loading a wider slice first:

```text
1. IndexItem defines a wide temporal slice.
2. SampleBuilder loads the wide slice once.
3. Runtime SampleAugmentation splits the loaded window into subwindows/views.
```

This avoids making the index responsible for learning-method logic.

## 19. SampleSpec and SampleBuilder

A `SampleSpec` declares which fields are required or optional for a given runtime path.

```python
@dataclass(slots=True)
class SampleSpec:
    required: Mapping[DataKey, FieldRequirement]
    optional: Mapping[DataKey, FieldRequirement] = field(default_factory=dict)
    allow_extra_fields: bool = True
```

A `FieldRequirement` can specify:

```text
key or accepted alternatives
data_type
runtime_type
schema
whether temporal slicing is required
required metadata
```

SampleBuilder:

```python
class SampleBuilder:
    def build(self, item: IndexItem, spec: SampleSpec | None = None) -> Sample:
        ...
```

Expected behavior:

```text
Validate required field views exist.
Resolve the codec for each FieldView.
Load each FieldView using its FieldRef and optional TemporalIndexSlice.
Wrap loaded values in FieldValues.
Copy relevant item/record metadata into Sample.metadata.
Fail loudly on missing fields, unsupported slices, codec errors, or schema mismatches.
```

---

## 20. IO and codecs

A codec loads a `FieldView`, not just a file path.

```python
class FieldCodec(Protocol):
    codec_key: str
    capabilities: CodecCapabilities

    def probe(self, field_ref: FieldRef) -> FieldMetadata:
        ...

    def load(self, view: FieldView) -> Any:
        ...

    def save(self, value: Any, field_ref: FieldRef) -> None:
        ...
```

Codec capabilities:

```python
@dataclass(slots=True)
class CodecCapabilities:
    supports_probe: bool = True
    supports_save: bool = False
    supports_temporal_index_slice: bool = False
    random_access: bool = False
```

Rules:

```text
Codecs should not silently ignore requested slices.
Codecs should not silently load the full field if slicing is unsupported.
Codecs should not silently convert time units to indices.
Codecs should not silently repair ambiguous metadata.
Fallbacks must be explicit config choices.
```

Default failure behavior:

```text
Missing field -> MissingFieldError
Unsupported slice -> SliceUnsupportedError
Slice out of bounds -> SliceOutOfBoundsError
Codec not found -> CodecResolutionError
Schema mismatch -> FieldSchemaError
Unexpected shape/layout -> FieldValidationError
```

Potential codec groups:

```text
video:
  mp4/avi via pyav or opencv
  frame directory
  zarr tensor store
  torch tensor store

signal:
  csv
  txt
  parquet
  zarr
  dataset-specific text formats

timestamps:
  csv
  json
  synthetic constant fps

landmarks:
  parquet
  json
  mediapipe-specific formats

masks:
  image directory
  zarr

meshes:
  npz
  obj/ply sequences, later

arrays:
  numpy
  torch
  zarr

metadata:
  json
  yaml
  csv
```

---

## 21. Ops layer

`rphys.ops` is the functional layer.

Rules:

```text
No IO.
No Sample plumbing.
No Dataset, Record, Manifest, or Artifact dependencies.
No hidden randomness.
No hidden device movement.
No hidden schema conversion.
Explicit shape/layout assumptions.
Explicit coordinate-frame assumptions.
Return plain tensors, data objects, tuples, or simple values.
Mutating functions should use a clear naming convention.
```

Recommended structure:

```text
rphys/ops/
  tensor/
    layout.py
    padding.py
    masking.py
    statistics.py

  temporal/
    slicing.py
    windows.py
    interpolation.py
    alignment.py

  geometry/
    boxes.py
    affine.py
    coordinates.py
    transforms.py

  video/
    resize.py
    crop.py
    normalize.py
    color.py
    temporal.py
    quality.py

  signal/
    filtering.py
    resampling.py
    normalization.py
    detrending.py
    spectral.py
    quality.py

  landmarks/
    geometry.py
    smoothing.py
    interpolation.py
    visibility.py

  masks/
    morphology.py
    resizing.py
    coverage.py

  meshes/
    geometry.py
    projection.py
    rasterization.py

  physiology/
    heart_rate.py
    bvp.py
    ppg.py
    snr.py
    spectral.py

  rppg/
    chrom.py
    pos.py
    green.py
    pbv.py

  multimodal/
    temporal_alignment.py
    spatial_alignment.py
    roi.py
    consistency.py
```

CHROM/POS example:

```text
rphys.ops.rppg.chrom.estimate_bvp
  pure implementation

rphys.transforms.rppg.CHROMTraceTransform
  Sample(video.rgb) -> Sample(signal.bvp.chrom)

rphys.methods.signal_processing.CHROMMethod
  Batch(video.rgb) -> Batch(prediction.signal.bvp)
```

The same op can be wrapped as a transform or as a method depending on use.

---

## 22. Runtime transforms, roles, and pipelines

The core runtime operation is `SampleTransform`.

```text
SampleTransform:
  Sample -> Sample
```

Keep public base types few:

```text
SampleTransform
  deterministic or non-random Sample -> Sample operation

SampleAugmentation
  stochastic SampleTransform with reproducible parameter sampling

SampleCheck
  validation/checking operation that raises, annotates, or warns, but does not filter

SampleExporter
  offline export-style operation that writes fields or creates symlinks and emits FieldRefs

Fittable
  optional mixin for transforms that need dataset-level fitting
```

Do not create `FilterTransform`. Filtering belongs to record/view/index construction.

### 22.1 Transform roles

Although the public base classes should remain small, transform implementations should be organized by role. This makes the package easier to navigate and clarifies lifecycle semantics.

Recommended roles:

```text
DETERMINISTIC
  Non-random processing of existing fields.
  Examples: resize video, normalize video, resample signal, align timestamps.

AUGMENTATION
  Stochastic training-time modification of fields.
  Examples: random temporal crop, color jitter, noise injection, synchronized crop.

EXTRACTION
  Derives new fields from existing fields.
  Examples: video -> landmarks, video + landmarks -> ROI, video -> CHROM trace.

CHECK
  Validates consistency or quality.
  Examples: check no NaNs, check coordinate frame, check temporal lengths match.

EXPORT
  Offline formatting/materialization operation.
  Examples: write video to zarr, write signal to parquet, create symlink FieldRef.
```

A role is not always a separate base class. For example, landmark extraction can be implemented as a deterministic SampleTransform with role `EXTRACTION`. Random crop is a SampleAugmentation with role `AUGMENTATION`. A zarr writer is a SampleExporter with role `EXPORT`.

Possible role enum:

```python
class TransformRole(str, Enum):
    DETERMINISTIC = "deterministic"
    AUGMENTATION = "augmentation"
    EXTRACTION = "extraction"
    CHECK = "check"
    EXPORT = "export"
```

### 22.2 Role-first package organization

Use role-first organization where it improves navigation:

```text
rphys/transforms/
  deterministic/
    video/
    signal/
    multimodal/

  augmentation/
    video/
    signal/
    multimodal/

  extraction/
    video/
    signal/
    multimodal/
    rppg/

  checks/
    video/
    signal/
    multimodal/

  export/
    video/
    signal/
    timestamps/
    symlink.py
```

The modality is still important, but role should be the first distinction for transform implementation modules because it communicates when and why the operation is used.

### 22.3 BaseSampleTransform

```python
class BaseSampleTransform:
    name: str | None = None
    role: TransformRole = TransformRole.DETERMINISTIC
    input_contract: SampleContract = SampleContract()
    output_contract: SampleContract = SampleContract()
    deterministic: bool = True
    mutates: bool = True

    def prepare(self, context: PipelineContext) -> None:
        pass

    def validate_input(self, sample: Sample, context: SampleContext) -> None:
        self.input_contract.validate(sample)

    def validate_output(self, sample: Sample, context: SampleContext) -> None:
        self.output_contract.validate(sample)

    def apply(self, sample: Sample, context: SampleContext) -> Sample:
        raise NotImplementedError

    def __call__(self, sample: Sample, context: SampleContext) -> Sample:
        self.validate_input(sample, context)
        output = self.apply(sample, context)
        self.validate_output(output, context)
        return output
```

### 22.4 SampleContext

```python
@dataclass(slots=True)
class SampleContext:
    run_seed: int
    sample_id: str | None = None
    record_id: str | None = None
    item_id: str | None = None
    split: str | None = None
    epoch: int | None = None
    worker_id: int | None = None
    global_step: int | None = None
    mode: str = "train"
    deterministic: bool = False
    rng: Any | None = None
    provenance: MutableMapping[str, Any] | None = None
```

### 22.5 PipelineContext

```python
@dataclass(slots=True)
class PipelineContext:
    run_seed: int
    mode: str
    split: str | None = None
    device: str | None = None
    config_fingerprint: str | None = None
    provenance_enabled: bool = False
```

### 22.6 SamplePipeline

`SamplePipeline` is the main mechanism for chaining transforms.

Because every runtime transform uses the same signature, composition is direct:

```text
Sample -> Transform A -> Sample -> Transform B -> Sample -> Transform C -> Sample
```

Example:

```python
pipeline = SamplePipeline([
    ResizeVideo(video_key="video.rgb", size=(128, 128)),
    NormalizeVideo(video_key="video.rgb"),
    AlignVideoSignal(video_key="video.rgb", signal_key="signal.bvp"),
    RandomTemporalCrop(keys=["video.rgb", "signal.bvp"], length=300),
    CheckNoNaNs(keys=["video.rgb", "signal.bvp"]),
])
```

Interface:

```python
class SamplePipeline:
    def __init__(self, steps: Sequence[SampleTransform | SampleCheck]):
        self.steps = list(steps)

    def prepare(self, context: PipelineContext) -> None:
        for step in self.steps:
            step.prepare(context)

    def __call__(self, sample: Sample, context: SampleContext) -> Sample:
        for index, step in enumerate(self.steps):
            context = self.with_step_rng(context, index, step)
            sample = step(sample, context)
        return sample
```

Pipeline responsibilities:

```text
Maintain transform order.
Provide per-step reproducibility context.
Optionally record provenance.
Respect train/eval mode.
Apply checks consistently.
Support mutable Sample flow without unnecessary copies.
Support explicit shallow copies for branching pipelines.
```

Branching or multi-view construction should be explicit. For example, a contrastive augmentation may read one wider loaded window and write `view.a.video.rgb` and `view.b.video.rgb` fields into the same Sample, rather than requiring the index to produce separate contrastive members.

### 22.7 SampleExporter and export-style transforms

A `SampleExporter` is used by offline materialization pipelines. It does not run in the hot training path unless explicitly requested.

Conceptual interface:

```python
class SampleExporter(Protocol):
    name: str
    role: TransformRole = TransformRole.EXPORT
    input_contract: SampleContract

    def export(
        self,
        sample: Sample,
        context: ExportContext,
    ) -> Mapping[DataKey, FieldRef]:
        ...
```

Examples:

```text
VideoZarrExporter
  writes video.rgb to a zarr store and emits a new video.rgb FieldRef

SignalParquetExporter
  writes signal.bvp to parquet and emits a new signal.bvp FieldRef

SymlinkExporter
  creates a symlink or pass-through FieldRef to avoid copying data

MetadataSidecarExporter
  writes selected metadata or annotations to a sidecar resource
```

This is the preferred place to put dataset formatting logic. The dataset package should not contain a `formatting/` component.

## 23. SampleAugmentation and reproducibility

Stochastic operations should use `SampleAugmentation`.

```python
class SampleAugmentation(BaseSampleTransform):
    deterministic = False

    def sample_params(
        self,
        sample: Sample,
        context: SampleContext,
    ) -> AugmentationParams:
        ...

    def apply_params(
        self,
        sample: Sample,
        params: AugmentationParams,
        context: SampleContext,
    ) -> Sample:
        ...

    def apply(self, sample: Sample, context: SampleContext) -> Sample:
        params = self.sample_params(sample, context)
        if context.provenance is not None:
            context.provenance.setdefault("augmentations", []).append(
                {"name": self.name, "params": params}
            )
        return self.apply_params(sample, params, context)
```

The pipeline should derive deterministic per-transform RNG streams from:

```text
run seed
epoch
worker ID
item ID or sample ID
transform index
transform name
view name, if relevant
```

Example seed derivation:

```text
seed = hash(run_seed, epoch, worker_id, item_id, transform_index, transform_name)
```

This supports:

```text
multi-worker dataloaders
distributed training
paired contrastive views
synchronized video/landmark/mask crops
debug reproducibility
evaluation-time deterministic behavior
```

Synchronized augmentation examples:

```text
SynchronizedTemporalCrop
  reads video.rgb, signal.bvp, timestamps.video, face.landmarks.mediapipe_468
  samples one temporal crop
  applies it consistently to all fields

SynchronizedSpatialCrop
  reads video.rgb, face.landmarks.mediapipe_468, face.mask.face
  samples one crop box
  applies it consistently to video, landmarks, and mask
```

---

## 24. Sample checks

A `SampleCheck` validates a sample. It is not a filter by default.

Examples:

```text
CheckRequiredFields
CheckVideoShape
CheckSignalFinite
CheckTemporalLengthsMatch
CheckLandmarksCoordinateFrame
CheckVideoSignalAlignment
CheckNoNaNs
```

Recommended behavior modes:

```text
raise
  default for training-critical checks

annotate
  write check results to metadata or quality fields

warn
  useful during dataset exploration
```

Do not use SampleCheck as the normal mechanism for filtering training data. If a sample should not exist, exclude it during index construction.

---

## 25. Lifecycle rules: runtime versus offline/materialized

Some operations can run in two modes.

Example: landmark extraction.

Runtime mode:

```text
Sample(video.rgb)
  -> LandmarkExtractionTransform
  -> Sample(video.rgb, face.landmarks.mediapipe_468)
```

Offline/materialized mode:

```text
DatasetRef(video.rgb FieldRefs)
  -> IndexItems with FieldViews
  -> SampleBuilder loads video Samples
  -> LandmarkExtractionTransform adds landmarks
  -> LandmarkParquetExporter writes landmarks
  -> new RecordRefs include face.landmarks.mediapipe_468 FieldRefs
  -> new DatasetRef/manifest is emitted
```

Dataset formatting follows the same materialization pattern.

Examples:

```text
raw MP4 FieldRefs
  -> VideoZarrExporter
  -> zarr video FieldRefs

raw signal text FieldRefs
  -> SignalParquetExporter
  -> parquet signal FieldRefs

already acceptable local files
  -> SymlinkExporter or pass-through FieldRef writer
  -> formatted DatasetRef without copying bytes unnecessarily
```

Rules:

```text
DatasetAdapter:
  discovers raw DatasetRefs, RecordRefs, and FieldRefs.

IndexBuilder:
  creates FieldViews with optional TemporalIndexSlice.

SampleBuilder:
  resolves FieldViews through codecs and creates Sample.

SamplePipeline:
  applies runtime SampleTransforms, SampleAugmentations, and SampleChecks.

MaterializationPipeline:
  loads Samples, optionally applies deterministic transforms/extractions/checks,
  then uses SampleExporters to write or symlink fields and emit new FieldRefs.

Formatting:
  is a materialization/export use case, not a datasets/ component.

Augmentation:
  runtime-only by default, not persisted.

Extraction:
  may be runtime or materialized.

Validation/checking:
  may raise, annotate, or produce reports.

Filtering:
  should generally happen before index finalization.
```

A materialized output should be explicit about whether it replaces existing field keys or adds new keys. For example, formatting may replace `video.rgb.raw` with `video.rgb`, while extraction may add `face.landmarks.mediapipe_468`.

## 26. Coordinate frames and temporal alignment

Multimodal transforms require explicit coordinate and temporal semantics.

Fields such as video, landmarks, masks, meshes, ROIs, and camera calibration should specify coordinate frames where needed.

Examples:

```text
video.rgb.pixel
video.rgb.normalized_0_1
video.rgb.face_crop.pixel
camera.rgb.camera_frame
camera.rgb.world_frame
```

Landmarks should declare whether coordinates are:

```text
pixel coordinates in original video
pixel coordinates in cropped video
normalized [0, 1]
normalized [-1, 1]
camera coordinates
world coordinates
```

Temporal semantics should also be explicit:

```text
temporal index space
sample rate
fps
timestamps
clock/source
start offset
```

A transform should fail if it requires alignment metadata that is absent or inconsistent.

---

## 27. Methods, models, learners, and trainers

Separate these concepts.

```text
Model
  Usually a torch.nn.Module. Maps tensors to tensors.

Method
  Prediction algorithm. Consumes Sample/Batch fields and emits prediction fields.
  May wrap a model, a signal-processing algorithm, or both.

Learner
  Defines training_step and validation_step for a learning style.

Trainer
  Runs loops, device placement, distributed execution, logging hooks, and checkpoints.
  Should not know whether the learner is supervised, self-supervised, contrastive,
  or masked modeling.
```

### 27.1 Method

```python
class Method(Protocol):
    input_contract: SampleContract
    output_contract: SampleContract

    def predict(
        self,
        batch: Batch,
        context: PredictionContext,
    ) -> Batch:
        ...
```

Methods may include:

```text
Neural rPPG method
CHROM method
POS method
Green-channel baseline
Classical regression method
Self-supervised encoder method
Hybrid signal-processing plus neural method
```

### 27.2 Model

Models should usually be normal PyTorch modules:

```python
class PhysNet(torch.nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        ...
```

Models should not contain dataset IO, augmentation, training loops, evaluation protocols, or artifact logic.

### 27.3 Learner

```python
class Learner(Protocol):
    def training_step(
        self,
        batch: Batch,
        context: TrainingContext,
    ) -> StepOutput:
        ...

    def validation_step(
        self,
        batch: Batch,
        context: TrainingContext,
    ) -> StepOutput:
        ...
```

Learner types:

```text
SupervisedLearner
SelfSupervisedLearner
ContrastiveLearner
MaskedModelingLearner
MultiTaskLearner
FineTuningLearner
```

### 27.4 Trainer

Trainer loop shape:

```python
for batch in train_loader:
    output = learner.training_step(batch, context)
    output.loss.backward()
    optimizer.step()
```

The trainer should not know how the learner computes the loss. It should only understand the returned `StepOutput`.

---

## 28. Training adapters and objectives

Input and target adapters prevent model assumptions from leaking into dataset or batch definitions.

Example input adapter:

```python
class VideoOnlyInputAdapter:
    def __init__(self, video_key: DataKey = DataKey("video.rgb")):
        self.video_key = video_key

    def __call__(self, batch: Batch) -> dict[str, Any]:
        video = batch.require(self.video_key, VideoData)
        return {"x": video.frames}
```

Example target adapter:

```python
class SignalTargetAdapter:
    def __init__(self, signal_key: DataKey = DataKey("signal.bvp")):
        self.signal_key = signal_key

    def __call__(self, batch: Batch) -> Any:
        return batch.require(self.signal_key, SignalData)
```

This allows the same dataset and batch structure to support different models and methods.

---

## 29. Losses

Losses should be grouped at top level, not under models.

Recommended structure:

```text
rphys/losses/
  core/
    base.py
    reduction.py
    composite.py
    adapters.py

  waveform/
    mse.py
    l1.py
    pearson.py
    cosine.py
    phase.py

  spectral/
    fft.py
    snr.py
    bandpower.py
    peak_frequency.py
    spectral_convergence.py

  temporal/
    smoothness.py
    derivative.py
    periodicity.py
    consistency.py

  physiological/
    heart_rate.py
    pulse_band.py
    bvp_constraints.py
    pulse_consistency.py

  contrastive/
    temporal_contrastive.py
    view_contrastive.py
    subject_contrastive.py

  multitask/
    weighted_sum.py
    uncertainty_weighted.py
    scheduled.py

  regularization/
    spatial.py
    temporal.py
    entropy.py
```

Recommended loss styles:

```text
TensorLoss
  forward(pred_tensor, target_tensor)

FieldLoss
  reads prediction and target fields from Sample/Batch

BatchLoss
  has full access to prediction batch and reference batch

CompositeLoss
  combines named loss terms
```

Example:

```python
class FieldLoss(torch.nn.Module):
    prediction_key: DataKey
    target_key: DataKey

    def forward(self, prediction: Batch, batch: Batch) -> torch.Tensor:
        pred = prediction.require(self.prediction_key)
        target = batch.require(self.target_key)
        return self.compute(pred, target)
```

This supports supervised, self-supervised, contrastive, and multi-task objectives.

---

## 30. Predictions as Samples

Predictions should not use a rigid waveform/heart-rate object.

A prediction is a Sample or Batch containing prediction fields.

Examples:

```text
prediction.signal.bvp
prediction.hr
prediction.embedding.video
prediction.quality.signal_snr
prediction.face.landmarks
prediction.mask.face
```

Evaluation can merge prediction fields with reference fields:

```text
Batch fields:
  signal.bvp.reference
  prediction.signal.bvp
  label.hr
  prediction.hr
  timestamps.video

Batch metadata:
  record_id
  subject_id
  dataset
  item_id
  split
```

This supports:

```text
waveform prediction
heart-rate regression
representation learning
quality prediction
mask prediction
landmark prediction
multi-task methods
signal-processing baselines
self-supervised evaluation
```

without changing the prediction container.

---

## 31. Metrics and evaluation aggregation

Metric design should support both orders:

```text
A. Compute metric per sample/window, then aggregate metric values.
B. Aggregate prediction samples first, then compute metric.
```

Examples:

```text
A:
  per-window waveform correlation
  -> aggregate mean/std by subject/dataset

B:
  window predictions
  -> aggregate into record-level waveform
  -> compute record-level heart-rate error
```

Recommended components:

```text
SampleAggregator
  Converts many Samples into fewer Samples before metric computation.

Metric
  Computes metric values from fields.

MetricAggregator
  Aggregates metric values after computation.

EvaluationProtocol
  Defines the order, grouping, metrics, and reports.
```

Metric interface:

```python
class Metric(Protocol):
    required_fields: SampleContract

    def update(self, prediction: Batch, reference: Batch) -> None:
        ...

    def compute(self) -> MetricResult:
        ...
```

Field-based metric example:

```yaml
metrics:
  - _target_: rphys.evaluation.metrics.PearsonMetric
    prediction_key: prediction.signal.bvp
    target_key: signal.bvp.reference

  - _target_: rphys.evaluation.metrics.HeartRateMAE
    prediction_key: prediction.hr
    target_key: label.hr
```

Evaluation protocol example:

```yaml
evaluation:
  prediction_aggregators:
    - _target_: rphys.evaluation.aggregation.OverlapAverageByRecord
      prediction_key: prediction.signal.bvp
      timestamp_key: timestamps.video

  metrics:
    - _target_: rphys.evaluation.metrics.HeartRateMAE
      prediction_key: prediction.signal.bvp
      target_key: signal.bvp.reference

  metric_aggregators:
    - _target_: rphys.evaluation.aggregation.MeanByDataset
    - _target_: rphys.evaluation.aggregation.MeanBySubject
```

---

## 32. Analysis

`rphys.analysis` should consume artifacts and reports. It should not rerun training or evaluation.

Useful analysis functionality:

```text
metric table generation
subject-level summaries
dataset-level summaries
confidence intervals
bootstrap utilities
statistical tests
failure-case mining
quality-stratified metrics
prediction-target waveform overlays
Bland-Altman plots
error distribution plots
frequency-spectrum visualizations
HTML/Markdown report generation
LaTeX table generation
```

Analysis may depend on heavier plotting/statistics packages.

---

## 33. Recipes and configuration

Recipe mechanism belongs to `loom`. Recipe definitions can live in `rphys`.

Use recipes for stable reusable domain patterns. Use full `_target_` object graphs for experiment-specific code.

Example supervised learner config:

```yaml
learner:
  _target_: rphys.training.learners.SupervisedLearner
  method:
    _target_: rphys.methods.neural.TorchMethod
    model:
      _target_: rphys.models.architectures.physnet.PhysNet
  input_adapter:
    _target_: rphys.training.input_adapters.VideoOnlyInputAdapter
    video_key: video.rgb
  target_adapter:
    _target_: rphys.training.target_adapters.SignalTargetAdapter
    signal_key: signal.bvp
  loss:
    _target_: rphys.losses.waveform.pearson.NegativePearsonLoss
```

Example contrastive learner config:

```yaml
learner:
  _target_: rphys.training.learners.ContrastiveLearner
  view_builder:
    _target_: rphys.transforms.augmentation.video.TwoViewTemporalCrop
    input_key: video.rgb
    output_keys: [view.a.video.rgb, view.b.video.rgb]
  encoder:
    _target_: my_project.models.VideoEncoder
  objective:
    _target_: rphys.losses.contrastive.TemporalContrastiveLoss
```

Example signal-processing baseline:

```yaml
method:
  _target_: rphys.methods.signal_processing.CHROMMethod
  video_key: video.rgb
  prediction_key: prediction.signal.bvp
```

Example materialization/formatting config:

```yaml
materialization:
  _target_: rphys.transforms.core.MaterializationPipeline
  sample_pipeline:
    _target_: rphys.transforms.core.SamplePipeline
    steps:
      - _target_: rphys.transforms.checks.video.CheckVideoDecodable
        video_key: video.rgb
  exporters:
    - _target_: rphys.transforms.export.video.VideoZarrExporter
      input_key: video.rgb
      output_key: video.rgb
      codec_key: video.zarr.v1
      output_root: /scratch/rphys/formatted/ubfc/videos
    - _target_: rphys.transforms.export.signal.SignalParquetExporter
      input_key: signal.bvp
      output_key: signal.bvp
      codec_key: signal.parquet.v1
      output_root: /scratch/rphys/formatted/ubfc/signals
```

Rules:

```text
Users should be able to use _target_ import paths for custom extensions.
Registries should not be required for every user extension.
Registries are useful for symbolic names such as dataset names, codec keys,
standard field schemas, standard metrics, and recipes.
Resolved configs should always be saved for reproducibility.
```

## 34. Stages

Concrete rphys stages implement loom's stage protocol.

Stages should be thin orchestration around rphys APIs.

Recommended stage groups:

```text
rphys.stages.datasets
  ScanDatasetStage
  BuildDatasetManifestStage
  BuildDatasetViewStage
  BuildIndexStage

rphys.stages.materialization
  MaterializeDatasetStage
  FormatDatasetStage
  ExportFieldsStage
  SymlinkDatasetStage
  ComputeMaterializedFieldsStage

rphys.stages.preprocessing
  RunRuntimePreprocessingStage, if needed for non-formatting preprocessing artifacts
  ComputeLandmarksStage, if treated as a named domain stage
  ComputeMasksStage
  ComputeQualityAnnotationsStage

rphys.stages.training
  TrainMethodStage
  FineTuneMethodStage
  PretrainMethodStage

rphys.stages.evaluation
  PredictStage
  AggregatePredictionsStage
  ComputeMetricsStage
  EvaluateProtocolStage

rphys.stages.analysis
  MakeReportStage
  MakePaperTablesStage
  MakeFiguresStage
```

Formatting stages live under `stages.materialization`, not under `stages.datasets`. They may be called `FormatDatasetStage` for user clarity, but conceptually they are materialization/export stages.

Stage design rules:

```text
Stages consume ArtifactRefs and produce ArtifactRefs.
Stages should not depend on in-memory outputs from previous stages.
Stages should be runnable independently through loom.
Stages should delegate domain work to rphys APIs.
Stages should return all declared outputs.
Stages should be safe to rerun when loom decides they are stale.
Dataset stages should not perform formatting side effects.
Materialization stages should emit new DatasetRefs/manifests rather than mutating inputs.
```

## 35. Failure behavior and error classes

Default behavior should be explicit and loud.

Important errors:

```text
RPhysError
RPhysDataError
RPhysDatasetError
RPhysIOError
RPhysTransformError
RPhysTrainingError
RPhysEvaluationError

MissingFieldError
MissingRequiredMetadataError
FieldTypeError
FieldSchemaError
FieldValidationError
CodecResolutionError
SliceUnsupportedError
SliceOutOfBoundsError
CollateError
TransformContractError
CoordinateFrameError
TemporalAlignmentError
```

Rules:

```text
No silent full-load fallback when a slice is requested.
No silent padding/truncation during collation.
No silent time-to-index conversion inside codecs.
No silent coordinate-frame conversion.
No silent consumption of a wrong field role.
```

Fallback behavior can exist, but must be explicit configuration.

---

## 36. Extension guide: add a dataset adapter

User goal:

```text
Add a new dataset that contains RGB video, BVP, timestamps, MediaPipe landmarks,
and optional FLAME meshes.
```

Steps:

```text
1. Choose field keys:
   video.rgb
   signal.bvp
   timestamps.video
   face.landmarks.mediapipe_468
   face.mesh.flame

2. Define FieldSpecs in DatasetSchema.

3. Implement DatasetAdapter.schema().

4. Implement DatasetAdapter.scan(source) to emit records with FieldRefs.

5. Add validation that checks expected files and required metadata.

6. Reuse existing codecs where possible.

7. Implement new codecs only for new storage formats.

8. Add synthetic or tiny fixture data for tests.
```

Minimal interface:

```python
class MyDatasetAdapter:
    dataset_name = "my_dataset"

    def schema(self) -> DatasetSchema:
        return DatasetSchema(...)

    def scan(self, source: DatasetSource) -> Iterable[Record]:
        for native_record in discover_records(source):
            yield Record(
                record_id=...,
                fields={
                    "video.rgb": FieldRef(...),
                    "signal.bvp": FieldRef(...),
                },
                metadata={...},
            )
```

Do not decode video or load full signals inside `scan()` unless probing is explicitly requested.

---

## 37. Extension guide: add a field type or modality

User goal:

```text
Add optical flow or a 3D face mesh field.
```

Steps:

```text
1. Choose a DataKey, preferably under a standard namespace or custom namespace.
2. Define a FieldSpec.
3. Define a DataObjectBase subclass if validation/collation/device movement matter.
4. Define one or more codecs if the field is stored externally.
5. Add ops if there are reusable tensor/data operations.
6. Add transforms if Samples should be modified using the field.
7. Add metrics/losses only if needed.
```

Example keys:

```text
face.mesh.flame
video.flow.raft
custom.my_project.face_embedding
```

---

## 38. Extension guide: add a codec

Implement `FieldCodec`.

Rules:

```text
Codec loads FieldView.
Codec reads FieldRef.ref, codec_key, selector, schema, and metadata.
Codec respects TemporalIndexSlice if supported.
Codec declares capabilities.
Codec fails loudly if unsupported operations are requested.
```

Skeleton:

```python
class MyMeshCodec:
    codec_key = "mesh.flame_npz.v1"
    capabilities = CodecCapabilities(
        supports_probe=True,
        supports_save=False,
        supports_temporal_index_slice=True,
        random_access=True,
    )

    def probe(self, field_ref: FieldRef) -> FieldMetadata:
        ...

    def load(self, view: FieldView) -> MeshData:
        ...
```

---

## 39. Extension guide: add a SampleTransform

Rules:

```text
Operate on Sample -> Sample.
Use configurable input and output keys.
Use sample.require() for required fields.
Declare input and output contracts.
Return the Sample, usually mutated.
Put reusable math in rphys.ops or local functional code.
Do not load files directly.
Do not filter samples.
Do not assume hard-coded field names unless the transform is explicitly standard-specific.
```

Skeleton:

```python
class NormalizeVideo(BaseSampleTransform):
    deterministic = True
    mutates = True

    def __init__(self, video_key="video.rgb", mean=None, std=None):
        self.video_key = DataKey(video_key)
        self.mean = mean
        self.std = std
        self.input_contract = SampleContract(required={self.video_key: VideoData})
        self.output_contract = SampleContract(required={self.video_key: VideoData})

    def apply(self, sample: Sample, context: SampleContext) -> Sample:
        video = sample.require(self.video_key, VideoData)
        video.frames = rphys.ops.video.normalize.normalize_video(
            video.frames,
            mean=self.mean,
            std=self.std,
        )
        return sample
```

---

## 40. Extension guide: add a SampleAugmentation

Rules:

```text
Subclass SampleAugmentation.
Implement sample_params() and apply_params().
Do not sample randomness inside apply_params().
Use context-provided RNG.
Record parameters in provenance when enabled.
For synchronized augmentations, sample one parameter object and apply it to all affected fields.
```

Skeleton:

```python
class RandomTemporalCrop(SampleAugmentation):
    def __init__(self, keys, length):
        self.keys = [DataKey(k) for k in keys]
        self.length = length

    def sample_params(self, sample: Sample, context: SampleContext):
        max_len = min(sample.require(k).temporal_length for k in self.keys)
        start = context.rng.integers(0, max_len - self.length + 1)
        return {"start": int(start), "length": self.length}

    def apply_params(self, sample: Sample, params, context: SampleContext) -> Sample:
        for key in self.keys:
            value = sample.require(key)
            sliced = rphys.ops.temporal.slicing.temporal_slice(
                value,
                start=params["start"],
                length=params["length"],
            )
            sample.set_field(key, sliced)
        return sample
```

---


## 41. Extension guide: add a SampleExporter or materialization step

Use a SampleExporter when the operation writes fields to a target format, creates symlinks, or emits new FieldRefs as part of an offline materialization or formatting process.

Rules:

```text
Do not put dataset formatting logic in rphys.datasets.
Use DatasetRef/RecordRef/FieldRef for input structure.
Use IndexItems and FieldViews to lazily load input fields.
Use a SamplePipeline for deterministic processing or extraction before export.
Use SampleExporter to write or symlink selected fields.
Emit new FieldRefs and a new DatasetRef/manifest.
Do not mutate the input DatasetRef in place.
Fail loudly if the requested output codec, schema, or target path is invalid.
```

Skeleton:

```python
class VideoZarrExporter:
    name = "video_zarr_exporter"
    role = TransformRole.EXPORT
    input_contract = SampleContract(required={"video.rgb": VideoData})

    def __init__(self, input_key="video.rgb", output_key="video.rgb", output_root=None):
        self.input_key = DataKey(input_key)
        self.output_key = DataKey(output_key)
        self.output_root = output_root

    def export(self, sample: Sample, context: ExportContext) -> Mapping[DataKey, FieldRef]:
        video = sample.require(self.input_key, VideoData)
        output_ref = context.make_resource_ref(
            output_root=self.output_root,
            record_id=sample.metadata["record_id"],
            field_key=self.output_key,
            extension=".zarr",
        )
        context.codec_registry.save(
            value=video,
            field_ref=FieldRef(
                key=self.output_key,
                data_type="video",
                ref=output_ref,
                codec_key="video.zarr.v1",
                schema="rgb_video_tchw.v1",
            ),
        )
        return {
            self.output_key: FieldRef(
                key=self.output_key,
                data_type="video",
                ref=output_ref,
                codec_key="video.zarr.v1",
                schema="rgb_video_tchw.v1",
            )
        }
```

Symlink exporters should make the no-copy behavior explicit and should still emit normal FieldRefs that downstream code can load through codecs.

## 42. Extension guide: add a method

A method predicts fields from a Batch.

Signal-processing baseline example:

```python
class CHROMMethod:
    input_contract = SampleContract(required={"video.rgb": VideoData})
    output_contract = SampleContract(required={"prediction.signal.bvp": SignalData})

    def __init__(self, video_key="video.rgb", prediction_key="prediction.signal.bvp"):
        self.video_key = DataKey(video_key)
        self.prediction_key = DataKey(prediction_key)

    def predict(self, batch: Batch, context: PredictionContext) -> Batch:
        video = batch.require(self.video_key, VideoData)
        pred = rphys.ops.rppg.chrom.estimate_bvp(video.frames, fps=video.fps)
        output = Batch(fields={}, metadata=dict(batch.metadata), batch_size=batch.batch_size)
        output.set_field(self.prediction_key, SignalData(values=pred, sample_rate=video.fps))
        return output
```

Neural method example:

```text
TorchMethod wraps:
  model
  input_adapter
  output_adapter
```

A method can be evaluated without being trainable.

---

## 43. Extension guide: add a model

For ordinary neural models, implement a normal PyTorch module.

```python
class MyRPPGModel(torch.nn.Module):
    def __init__(self, ...):
        super().__init__()
        ...

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        ...
```

Do not put dataset IO, training loops, augmentation, evaluation, or artifact logic inside the model.

Wire the model through a method or learner:

```yaml
method:
  _target_: rphys.methods.neural.TorchMethod
  model:
    _target_: my_project.models.MyRPPGModel
  input_adapter:
    _target_: rphys.training.input_adapters.VideoOnlyInputAdapter
    video_key: video.rgb
  output_adapter:
    _target_: rphys.models.adapters.SignalOutputAdapter
    prediction_key: prediction.signal.bvp
```

---

## 44. Extension guide: add a learner

A learner defines training logic for a learning style.

Examples:

```text
SupervisedLearner
ContrastiveLearner
MaskedModelingLearner
SelfDistillationLearner
MultiTaskLearner
```

Skeleton:

```python
class MyLearner:
    def __init__(self, method, objective, optimizer_builder=None):
        self.method = method
        self.objective = objective
        self.optimizer_builder = optimizer_builder

    def training_step(self, batch: Batch, context: TrainingContext) -> StepOutput:
        prediction = self.method.predict(batch, context.prediction_context)
        loss = self.objective(prediction, batch)
        return StepOutput(loss=loss, outputs={"prediction": prediction})

    def validation_step(self, batch: Batch, context: TrainingContext) -> StepOutput:
        prediction = self.method.predict(batch, context.prediction_context)
        loss = self.objective(prediction, batch)
        return StepOutput(loss=loss, outputs={"prediction": prediction})
```

Trainer remains generic over learner type.

---

## 45. Extension guide: add a loss

Choose the simplest appropriate base:

```text
TensorLoss
  if it only needs tensors

FieldLoss
  if it reads fields by key

BatchLoss
  if it needs full batch/prediction context

CompositeLoss
  if combining terms
```

Example:

```python
class NegativePearsonFieldLoss(FieldLoss):
    def compute(self, pred: SignalData, target: SignalData) -> torch.Tensor:
        return -rphys.ops.signal.statistics.pearson_corr(pred.values, target.values).mean()
```

---

## 46. Extension guide: add a metric

Metrics should consume fields by key.

Skeleton:

```python
class MyMetric:
    def __init__(self, prediction_key, target_key):
        self.prediction_key = DataKey(prediction_key)
        self.target_key = DataKey(target_key)
        self.values = []

    def update(self, prediction: Batch, reference: Batch) -> None:
        pred = prediction.require(self.prediction_key)
        target = reference.require(self.target_key)
        value = self.compute_one(pred, target)
        self.values.append(value)

    def compute(self) -> MetricResult:
        return MetricResult(name="my_metric", value=aggregate(self.values))
```

For metrics that require record-level signals, use a `SampleAggregator` before metric computation.

---

## 47. Core design decisions to specify now

These choices are fundamental and should be locked down before implementation hardens.

```text
1. loom/rphys boundary.

2. DatasetRef / RecordRef / FieldRef structure:
   DatasetRef defines a dataset or view.
   RecordRef defines an item/entry.
   FieldRef defines a complete logical field.

3. FieldSpec / FieldRef / FieldView / FieldValue separation.

4. DataKey naming grammar and reserved namespaces.

5. TemporalIndexSlice semantics:
   index-based only, half-open, field-native temporal indices.

6. IndexItem semantics:
   lazy IO view only, not transforms, augmentation, formatting, or learning logic.

7. Dataset adapters expose arbitrary logical fields.

8. Dataset formatting is materialization/export, not a datasets/ component.

9. Sample is the central runtime container.

10. Sample and Batch use the same field access API.

11. Sample is mutable by default.

12. Field metadata/schema/layout/collate attributes are explicit.

13. Missing fields, unsupported slices, schema mismatches, and collate ambiguity fail loudly.

14. Filtering happens during record/view/index construction, not through SampleTransform.

15. SampleTransform is the core Sample -> Sample runtime operation.

16. Transform implementations are organized by role where useful:
    deterministic, augmentation, extraction, checks, and export.

17. SampleAugmentation is the stochastic SampleTransform subtype.

18. Reproducibility context is supplied by SamplePipeline.

19. SamplePipeline is the standard composition mechanism for Sample -> Sample operations.

20. SampleExporter and MaterializationPipeline handle formatting/export/symlinking.

21. Ops are pure functional machinery with no IO and no Sample plumbing.

22. Offline stages can materialize fields, but runtime transforms operate on Samples.

23. Model, Method, Learner, and Trainer are distinct.

24. Predictions are Samples/Batches with prediction fields.

25. Metrics support both pre-metric sample aggregation and post-metric metric aggregation.

26. Collate policy is field-level and explicit.

27. Public extension contracts are stable and documented.

28. Registries are used for symbolic names such as codecs and dataset names,
    not required for every user extension.

29. User extensions should work via _target_ import paths without editing rphys internals.
```

## 48. Decisions that can be deferred

These do not need to be fully solved now.

```text
Exact list of collate policies.
Exact list of codecs.
Exact list of export formats.
Exact list of datasets.
Exact list of model architectures.
Whether to implement mesh support immediately.
Whether to implement nested multi-view Samples.
Whether to add spatial slices.
Whether to add time-based slices.
Whether to add multi-member IndexItems.
Whether to support plugin discovery through package entry points.
Full library of self-supervised learners.
Full library of signal-processing methods.
Full library of materialization exporters.
Full publication/reporting analysis stack.
```

The architecture should leave room for these without forcing implementation immediately.

## 49. Registry and plugin policy

Use `_target_` for most user-defined objects.

Use registries only where symbolic names are useful:

```text
codec_key
dataset_name
field schema names
standard metric names
standard recipe names
```

Do not force users to register every transform, method, loss, metric, or model. Experiment-local code should be usable through import paths:

```yaml
transform:
  _target_: my_project.transforms.CustomTransform

method:
  _target_: my_project.methods.CustomMethod
```

Optional future plugin discovery via Python entry points can be added later.

---

## 50. Testing strategy

Testing should include:

```text
unit tests
contract tests
synthetic data tests
codec round-trip tests
index/slice tests
collation tests
transform reproducibility tests
method/learner tests
evaluation aggregation tests
stage integration tests with loom
smoke pipelines
```

Important contract tests:

```text
Dataset adapters emit valid FieldRefs matching DatasetSchema.
IndexItems contain only FieldViews and metadata, not loaded data.
SampleBuilder fails on missing fields or unsupported slices.
SampleTransform input/output contracts catch errors.
SampleAugmentation is reproducible under fixed context.
Collation fails loudly without explicit padding/list/missing policy.
Prediction Samples can be consumed by metrics through field keys.
Stages satisfy loom's stage protocol.
Recipes expand to valid loom-compatible configs.
```

Synthetic data should include:

```text
small video tensors
synthetic BVP signals
synthetic timestamps
synthetic landmarks
metadata with subject/session/trial IDs
known split behavior
known metric outputs
```

---

## 51. Dependency policy

Use optional dependency groups.

Potential extras:

```text
rphys[video]
  av
  opencv-python
  imageio

rphys[signal]
  scipy

rphys[torch]
  torch

rphys[training]
  torch
  lightning or fabric, optional

rphys[analysis]
  pandas
  matplotlib
  scipy
  statsmodels

rphys[dev]
  pytest
  ruff
  mypy
```

Import boundary:

```text
rphys.data.core:
  lightweight where possible

rphys.datasets:
  should avoid torch unless necessary

rphys.io:
  optional backend dependencies

rphys.data.modalities:
  may depend on torch

rphys.training/models/losses:
  torch-dependent

rphys.analysis:
  pandas/matplotlib/scipy-dependent
```

Do not split packages prematurely, but keep dependency boundaries clean enough that splitting is possible later.

---

## 52. Documentation requirements

The architecture should include user-facing extension guides for:

```text
adding a dataset adapter
adding a DatasetRef/RecordRef-backed manifest
adding a field type
adding a codec
adding a DataObject modality
adding a deterministic SampleTransform
adding a SampleAugmentation
adding an extraction transform
adding a SampleCheck
adding a SampleExporter or materialization/export step
adding a signal-processing method
adding a neural model
adding a learner
adding a loss
adding a metric
adding an evaluation protocol
adding an offline materialization stage
```

Each guide should state:

```text
which protocol/base class to implement
which methods are required
what must be serializable
what field keys to use
how to declare contracts
how to test the extension
what not to do
```

Most important user-facing rule:

```text
Users should extend rphys by adding new fields, codecs, transforms, exporters,
methods, learners, losses, and metrics through public contracts and config targets,
not by modifying core internals.
```

## 53. Final architecture recommendation

`rphys` should be a field-centric, sample-centric, domain-specific package layered on top of `loom`.

The central abstractions are:

```text
FieldSpec
FieldRef
TemporalIndexSlice
FieldView
IndexItem
Sample
Batch
SampleTransform
SampleAugmentation
Method
Learner
Metric
EvaluationProtocol
```

The most important separation is:

```text
FieldView and IndexItem:
  lazy IO definition

SampleTransform and SampleAugmentation:
  runtime data modification

RecordFilter, FieldFilter, IndexItemFilter:
  dataset/index construction

Method, Learner, Trainer:
  prediction and learning behavior

Prediction Samples and Metrics:
  evaluation behavior
```

This design should support:

```text
many data types
many dataset layouts
lazy loading
standard supervised learning
pretraining
self-supervised learning
contrastive learning
masked modeling
signal-processing baselines
neural models
multi-task predictions
custom experiment packages
artifact-based pipelines through loom
```

The practical rule remains:

```text
If the code would still make sense for genomics, robotics, remote sensing,
or generic ML pipelines, it probably belongs in loom.

If the code knows about video, BVP/PPG, timestamps, face ROI, physiological
signals, rPPG models, or heart-rate evaluation, it belongs in rphys.
```
