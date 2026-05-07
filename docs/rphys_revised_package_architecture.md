# rphys Revised Package Architecture and Design Plan

Draft version: 0.2  
Date: 2026-05-06

## 1. Purpose

`rphys` is the domain-specific package for remote physiological measurement research. It should provide the scientific and engineering components needed to work with remote physiological datasets, video and signal data, preprocessing and augmentation pipelines, reusable models, losses, metrics, evaluation protocols, and analysis tooling.

`rphys` is intended to sit on top of `loom`, which owns the domain-agnostic experiment infrastructure. The boundary remains:

```text
loom knows how to run a reproducible artifact-based experiment.
rphys knows what a remote physiological measurement experiment is.
```

The revised design treats `rphys` as a domain package with a single unified data interface. The central runtime object is a generic `Sample`, which contains typed fields such as video, BVP, landmarks, masks, meshes, timestamps, labels, and arbitrary future data types. Transforms, collators, model input adapters, losses, and metrics should all interact with this sample interface rather than with hard-coded attributes such as `sample.video` or `sample.target`.

## 2. Core Goals

The package should be:

```text
Extensible
  New data modalities, fields, codecs, datasets, transforms, models, losses,
  metrics, and stages can be added without changing core package internals.

Lazy by default
  Dataset discovery, filtering, indexing, and sample loading are separate.
  Expensive I/O is deferred until a sample is loaded by a torch Dataset.

Composable
  Data processing is represented as chains of Sample -> Sample transforms.
  Functional operations are separated from transform wrappers.

Modality-aware but not hard-coded
  Video, signal, landmarks, masks, meshes, timestamps, and metadata are strongly
  represented, but no single modality is privileged.

Artifact-compatible
  Expensive deterministic work can be run offline through stages and persisted as
  manifest, index, processed-resource, prediction, metric, or report artifacts.

Experiment-friendly
  Experiment packages can define custom fields, codecs, transforms, models,
  losses, metrics, recipes, and stages through importable _target_ config.
```

## 3. Non-Goals

`rphys` should not own generic experiment infrastructure. These belong in `loom`:

```text
configuration composition
recursive _target_ instantiation
recipe expansion mechanics
pipeline DAG execution
run stores
artifact stores
artifact references
resource references, if already generic in loom
stage status machines
resume planning
executors
SLURM or subprocess orchestration
sweep execution
generic record and manifest primitives, if provided by loom
```

`rphys` may define domain-specific stage classes and artifact payload schemas, but the generic stage execution machinery should remain in `loom`.

## 4. Main Architectural Decision

The main architectural decision is:

```text
Do not model every combination of data modalities as a separate class.

Model individual data types strongly.
Model combinations through Sample fields, FieldRef objects, SampleSpec objects,
BundleSpec objects, and transform contracts.
```

This avoids class explosion. The package should not need permanent classes such as:

```text
VideoSignalSample
VideoLandmarkSample
VideoSignalLandmarkSample
VideoSignalLandmarkMaskSample
VideoSignalLandmarkMeshMaskSample
```

Instead, all runtime data flows through:

```text
Sample(fields={...}, metadata={...})
```

A sample may contain:

```text
video.rgb
signal.bvp
timestamps.video
face.landmarks.468
face.mask.face
face.mesh.flame
face.roi.left_cheek
quality.video_motion
label.hr
annotation.skin_tone
```

All runtime transforms should accept a `Sample` and return a `Sample`.

## 5. End-to-End Data Flow

The intended data flow is:

```text
native dataset source
  -> dataset adapter
  -> records with logical FieldRefs
  -> dataset manifest
  -> filtered dataset view
  -> training/evaluation index
  -> lazy sample builder
  -> Sample
  -> Sample transform pipeline
  -> Batch with same field interface
  -> model input adapter
  -> model
  -> loss / prediction / metric / report
```

This separates discovery from loading, records from samples, and runtime samples from persisted artifacts.

## 6. Recommended Top-Level Package Structure

The package should be organized for growth. Flat modules such as `data/video.py`, `io/video_codecs.py`, or `preprocessing/video.py` are not sufficient once there are many video operations, many codecs, multiple signal types, landmarks, meshes, masks, and multimodal transforms.

Recommended structure:

```text
src/rphys/
  __init__.py

  conventions/
    __init__.py
    keys.py
    fields.py
    metadata.py
    resources.py

  errors/
    __init__.py
    data.py
    datasets.py
    io.py
    transforms.py
    training.py
    evaluation.py

  registry/
    __init__.py
    base.py
    codecs.py
    datasets.py
    transforms.py
    metrics.py

  data/
    core/
      __init__.py
      keys.py
      field.py
      sample.py
      batch.py
      collate.py
      policies.py
      schema.py
      contracts.py
      bundles.py
      tensor_tree.py
      validation.py

    modalities/
      video/
        __init__.py
        data.py
        batch.py
        schema.py
        metadata.py
        validation.py

      signal/
        __init__.py
        data.py
        batch.py
        schema.py
        metadata.py
        validation.py

      timestamps/
        __init__.py
        data.py
        schema.py
        validation.py

      landmarks/
        __init__.py
        data.py
        batch.py
        schema.py
        geometry.py
        validation.py

      meshes/
        __init__.py
        data.py
        batch.py
        schema.py
        validation.py

      masks/
        __init__.py
        data.py
        batch.py
        schema.py
        validation.py

      roi/
        __init__.py
        data.py
        schema.py
        validation.py

      events/
        __init__.py
        data.py
        schema.py

      labels/
        __init__.py
        data.py
        schema.py

      arrays/
        __init__.py
        data.py
        schema.py

      metadata/
        __init__.py
        data.py
        schema.py

    bundles/
      __init__.py
      video_signal.py
      face_tracking.py
      video_landmarks.py
      video_mask.py
      physiological.py
      generic.py

  io/
    core/
      __init__.py
      resources.py
      field_refs.py
      regions.py
      codecs.py
      registry.py
      probing.py
      cache.py
      validation.py

    codecs/
      video/
        __init__.py
        opencv.py
        pyav.py
        frame_directory.py
        zarr.py
        torch_tensor.py

      signal/
        __init__.py
        csv.py
        txt.py
        parquet.py
        zarr.py
        ubfc.py

      timestamps/
        __init__.py
        synthetic.py
        csv.py
        json.py

      landmarks/
        __init__.py
        parquet.py
        json.py
        mediapipe.py

      meshes/
        __init__.py
        flame.py
        npz.py
        parquet.py

      masks/
        __init__.py
        image_directory.py
        zarr.py

      arrays/
        __init__.py
        numpy.py
        torch.py
        zarr.py

      metadata/
        __init__.py
        json.py
        yaml.py
        csv.py

  datasets/
    core/
      __init__.py
      adapters.py
      records.py
      fields.py
      manifests.py
      views.py
      indexing.py
      sample_specs.py
      validation.py
      statistics.py

    discovery/
      __init__.py
      glob.py
      regex.py
      filesystem.py

    filters/
      __init__.py
      base.py
      metadata.py
      resources.py
      fields.py
      quality.py
      subject.py
      duration.py

    splits/
      __init__.py
      subject.py
      session.py
      dataset.py
      explicit.py
      cross_dataset.py

    formatting/
      __init__.py
      base.py
      video.py
      signal.py
      timestamps.py
      landmarks.py
      manifests.py

    adapters/
      __init__.py
      synthetic/
      ubfc/
      pure/
      mahnob/
      cohface/
      vipln_hr/

  ops/
    video/
      __init__.py
      resize.py
      crop.py
      normalize.py
      color.py
      temporal.py
      layout.py
      quality.py

    signal/
      __init__.py
      filtering.py
      resampling.py
      normalization.py
      detrending.py
      spectral.py
      quality.py
      correlation.py

    landmarks/
      __init__.py
      geometry.py
      smoothing.py
      interpolation.py
      normalization.py

    meshes/
      __init__.py
      geometry.py
      projection.py
      fitting.py

    masks/
      __init__.py
      morphology.py
      resizing.py
      quality.py

    geometry/
      __init__.py
      boxes.py
      affine.py
      coordinate_systems.py

    temporal/
      __init__.py
      windows.py
      alignment.py
      interpolation.py
      synchronization.py

    physiology/
      __init__.py
      heart_rate.py
      bvp.py
      ppg.py
      spectral.py
      snr.py

    multimodal/
      __init__.py
      alignment.py
      roi.py
      synchronization.py
      consistency.py

  transforms/
    core/
      __init__.py
      base.py
      compose.py
      contracts.py
      selectors.py
      rng.py
      params.py
      provenance.py
      validation.py
      field.py
      sample.py
      multifield.py
      stochastic.py
      extraction.py

    video/
      deterministic/
        resize.py
        crop.py
        normalize.py
        color.py
        layout.py
        temporal.py

      stochastic/
        random_crop.py
        random_resize.py
        color_jitter.py
        frame_dropout.py
        temporal_jitter.py
        compression.py
        noise.py

      extraction/
        face_detection.py
        landmarks.py
        masks.py
        roi.py

      validation/
        shape.py
        fps.py
        quality.py

    signal/
      deterministic/
        resample.py
        filter.py
        detrend.py
        normalize.py
        clip.py

      stochastic/
        noise.py
        scale.py
        dropout.py
        time_warp.py

      extraction/
        heart_rate.py
        spectral_features.py

      validation/
        sample_rate.py
        value_range.py
        coverage.py

    landmarks/
      deterministic/
        smooth.py
        normalize.py
        interpolate.py

      stochastic/
        jitter.py
        dropout.py

      validation/
        visibility.py
        geometry.py

    meshes/
      deterministic/
        normalize.py
        project.py
        smooth.py

      stochastic/
        jitter.py
        dropout.py

      validation/
        topology.py
        visibility.py

    masks/
      deterministic/
        resize.py
        erode.py
        dilate.py

      stochastic/
        dropout.py
        perturb.py

      validation/
        coverage.py

    multimodal/
      deterministic/
        synchronize.py
        align_video_signal.py
        crop_video_by_landmarks.py
        roi_from_landmarks.py
        mask_video.py
        extract_roi_signal.py

      stochastic/
        synchronized_spatial_crop.py
        synchronized_temporal_crop.py
        synchronized_temporal_jitter.py
        multimodal_dropout.py

      extraction/
        chrom.py
        pos.py
        face_roi_traces.py
        video_to_landmarks.py
        video_landmarks_to_roi.py

      validation/
        timestamp_alignment.py
        spatial_alignment.py
        field_consistency.py

    batch/
      deterministic/
      stochastic/
      validation/

    dataset/
      deterministic/
      validation/

  models/
    core/
      __init__.py
      base.py
      specs.py
      checkpoints.py
      outputs.py

    architectures/
      physnet/
        __init__.py
        model.py
        blocks.py
        config.py

      efficientphys/
        __init__.py
        model.py
        blocks.py
        config.py

      tscan/
        __init__.py
        model.py
        blocks.py
        config.py

      deepphys/
        __init__.py
        model.py
        blocks.py
        config.py

      simple_baselines/
        __init__.py
        cnn.py
        linear.py

    layers/
      __init__.py
      temporal.py
      spatial.py
      attention.py
      normalization.py

    heads/
      __init__.py
      waveform.py
      heart_rate.py
      multitask.py

    adapters/
      __init__.py
      inputs.py
      outputs.py

  losses/
    core/
      __init__.py
      base.py
      reduction.py
      composite.py
      adapters.py
      registry.py

    waveform/
      __init__.py
      mse.py
      l1.py
      pearson.py
      cosine.py
      phase.py
      dtw.py

    spectral/
      __init__.py
      fft.py
      snr.py
      bandpower.py
      peak_frequency.py
      spectral_convergence.py

    temporal/
      __init__.py
      smoothness.py
      derivative.py
      periodicity.py
      consistency.py

    physiological/
      __init__.py
      heart_rate.py
      pulse_band.py
      bvp_constraints.py
      pulse_consistency.py

    probabilistic/
      __init__.py
      gaussian_nll.py
      laplace_nll.py
      uncertainty.py

    contrastive/
      __init__.py
      temporal_contrastive.py
      subject_contrastive.py
      view_contrastive.py

    regularization/
      __init__.py
      spatial.py
      temporal.py
      entropy.py
      weight.py

    multitask/
      __init__.py
      weighted_sum.py
      uncertainty_weighted.py
      scheduled.py

  training/
    __init__.py
    datasets.py
    sample_builders.py
    input_adapters.py
    target_adapters.py
    dataloaders.py
    trainers.py
    optim.py
    checkpointing.py

  evaluation/
    __init__.py
    predictions.py
    metrics.py
    protocols.py
    aggregation.py
    reports.py

  analysis/
    __init__.py
    tables.py
    plots.py
    statistics.py
    reports.py
    diagnostics.py

  recipes/
    __init__.py
    data.py
    preprocessing.py
    training.py
    evaluation.py
    experiments.py

  stages/
    __init__.py
    datasets.py
    preprocessing.py
    training.py
    evaluation.py
    analysis.py
    inference.py

  testing/
    __init__.py
    synthetic_data.py
    fixtures.py
    smoke.py
```

## 7. Core Data Interface

### 7.1 DataKey

A `DataKey` is a logical name for a field in a sample or record. It should be extensible and string-like, not a closed enum.

Recommended naming pattern:

```text
<domain>.<semantic>[.<variant>]
```

Examples:

```text
video.rgb
video.nir
video.depth
video.thermal
signal.bvp
signal.ppg
signal.ecg
signal.respiration
timestamps.video
timestamps.bvp
face.landmarks.68
face.landmarks.468
face.landmarks.openface
face.mesh.flame
face.mask.skin
face.mask.face
face.roi.left_cheek
face.roi.right_cheek
face.roi.forehead
quality.video_motion
quality.face_visibility
quality.signal_snr
label.hr
label.bvp
camera.intrinsics
camera.extrinsics
annotation.skin_tone
annotation.lighting
```

Standard keys can be constants for convenience, but custom keys must remain allowed.

### 7.2 FieldValue

A `FieldValue` wraps a runtime payload inside a `Sample` or `Batch`.

Recommended structure:

```python
@dataclass(frozen=True, slots=True)
class FieldValue:
    value: Any
    data_type: str | None = None
    schema: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    collate: CollatePolicy | None = None
```

The payload may be a `VideoData`, `SignalData`, `LandmarkData`, `MeshData`, `MaskData`, `TimestampData`, `LabelData`, `ArrayData`, a tensor, or another data object.

### 7.3 Sample

`Sample` is the central runtime abstraction.

```python
@dataclass(frozen=True, slots=True)
class Sample:
    fields: Mapping[DataKey, FieldValue]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def has(self, key: str) -> bool: ...
    def get(self, key: str, default: Any = None) -> Any: ...
    def field(self, key: str) -> FieldValue: ...
    def require(self, key: str, expected_type: type | None = None) -> Any: ...
    def with_field(self, key: str, value: Any, **kwargs) -> "Sample": ...
    def without_field(self, key: str) -> "Sample": ...
    def map_tensors(self, fn) -> "Sample": ...
    def to(self, device, *, non_blocking: bool = True) -> "Sample": ...
```

Example:

```python
sample = Sample(
    fields={
        "video.rgb": FieldValue(VideoData(...), data_type="video"),
        "signal.bvp": FieldValue(SignalData(...), data_type="signal"),
        "timestamps.video": FieldValue(TimestampData(...), data_type="timestamps"),
        "face.landmarks.468": FieldValue(LandmarkData(...), data_type="landmarks"),
        "face.mesh.flame": FieldValue(MeshData(...), data_type="mesh"),
        "face.mask.face": FieldValue(MaskData(...), data_type="mask"),
    },
    metadata={
        "record_id": "ubfc/s01/trial01",
        "dataset": "ubfc",
        "subject_id": "s01",
        "split": "train",
    },
)
```

### 7.4 Batch

Collation should produce a `Batch` with the same field access API as `Sample`.

```python
batch = collate_samples([sample_0, sample_1, sample_2])

video = batch.require("video.rgb", VideoData)
frames = video.frames
# frames shape: [B, T, C, H, W]
```

The downstream model input adapter, target adapter, loss, and metric code should not need a different interface for single samples and batches.

## 8. Data Modalities

Typed modality objects should exist inside `rphys.data.modalities`. They should be strong enough to enforce shape conventions and domain metadata, but not so rigid that every experiment requires a new class.

### 8.1 VideoData

Recommended shape convention:

```text
single video: [T, C, H, W]
batched video: [B, T, C, H, W]
```

Suggested fields:

```python
@dataclass(frozen=True, slots=True)
class VideoData(DataObjectBase):
    frames: torch.Tensor
    timestamps: torch.Tensor | None = None
    fps: float | None = None
    color_space: str | None = None
    layout: str = "TCHW"
    metadata: Mapping[str, Any] = field(default_factory=dict)
```

### 8.2 SignalData

Recommended shape convention:

```text
single signal: [T] or [C, T]
batched signal: [B, T] or [B, C, T]
```

Suggested fields:

```python
@dataclass(frozen=True, slots=True)
class SignalData(DataObjectBase):
    values: torch.Tensor
    timestamps: torch.Tensor | None = None
    sample_rate: float | None = None
    units: str | None = None
    signal_type: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
```

### 8.3 TimestampData

Timestamps should be explicit when available or inferable. Synthetic constant-FPS timestamps should be represented as real fields, not hidden assumptions.

### 8.4 LandmarkData

Recommended shape convention:

```text
single landmarks: [T, N, 2] or [T, N, 3]
batched landmarks: [B, T, N, 2] or [B, T, N, 3]
```

Landmark data should carry schema information, for example:

```text
mediapipe_face_468.v1
openface_68.v1
ibug_68.v1
```

### 8.5 MeshData

Meshes are future-facing but should be planned for early. Meshes may contain vertices, faces, per-frame transforms, visibility masks, and schema metadata.

Example field keys:

```text
face.mesh.flame
body.mesh.smpl
head.mesh.custom
```

### 8.6 MaskData and ROIData

Masks and ROIs should support video-aligned data such as face masks, skin masks, foreground masks, and landmark-derived regions of interest.

Example field keys:

```text
face.mask.face
face.mask.skin
face.roi.left_cheek
face.roi.right_cheek
face.roi.forehead
```

## 9. Dataset Records and Arbitrary Fields

Dataset adapters must expose logical fields, not just raw resources.

A record should not only say:

```python
resources = {
    "video": ResourceRef(...),
    "bvp": ResourceRef(...),
}
```

Instead, it should expose logical field references:

```python
record.fields = {
    "video.rgb": FieldRef(...),
    "signal.bvp": FieldRef(...),
    "timestamps.video": FieldRef(...),
    "face.landmarks.468": FieldRef(...),
    "face.mesh.flame": FieldRef(...),
}
```

This allows video, BVP, landmarks, meshes, masks, labels, and arbitrary experiment-specific fields to be accessed through one interface.

### 9.1 FieldRef

A `FieldRef` describes how to load one logical field.

```python
@dataclass(frozen=True, slots=True)
class FieldRef:
    key: DataKey
    data_type: str
    ref: ResourceRef | None = None
    inline_value: Any | None = None
    codec_key: str | None = None
    selector: Mapping[str, Any] | None = None
    schema: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
```

Example video field:

```python
FieldRef(
    key="video.rgb",
    data_type="video",
    ref=ResourceRef(uri="/data/ubfc/s01/vid.avi"),
    codec_key="video.avi.opencv.v1",
    metadata={
        "fps": 30.0,
        "width": 640,
        "height": 480,
    },
)
```

Example BVP field from a multi-column text file:

```python
FieldRef(
    key="signal.bvp",
    data_type="signal",
    ref=ResourceRef(uri="/data/ubfc/s01/ground_truth.txt"),
    codec_key="signal.ubfc_txt.v1",
    selector={"column": "bvp"},
    metadata={"sample_rate": 64.0, "units": "a.u."},
)
```

Example precomputed landmark field:

```python
FieldRef(
    key="face.landmarks.468",
    data_type="landmarks",
    ref=ResourceRef(uri="/cache/ubfc/s01/landmarks.parquet"),
    codec_key="landmarks.mediapipe_parquet.v1",
    schema="mediapipe_face_468.v1",
)
```

Example inline annotation:

```python
FieldRef(
    key="annotation.skin_tone",
    data_type="annotation",
    inline_value="fitzpatrick_iii",
)
```

### 9.2 Multiple Logical Fields From One Physical Resource

One physical file may provide several logical fields.

```text
physical resource:
  /data/subject01/signals.csv

logical fields:
  signal.bvp
  signal.ecg
  signal.respiration
```

Each logical field can share the same `ResourceRef` but use a different selector.

```python
FieldRef(
    key="signal.ecg",
    data_type="signal",
    ref=ResourceRef(uri="/data/subject01/signals.csv"),
    codec_key="signals.csv.v1",
    selector={"column": "ecg"},
)
```

This is more extensible than assuming one resource equals one field.

### 9.3 RPhysRecordView

If `loom.Record` remains generic, `rphys` should provide a domain view:

```python
class RPhysRecordView:
    def __init__(self, record: loom.Record):
        self.record = record

    def field(self, key: str) -> FieldRef: ...
    def require_field(self, key: str) -> FieldRef: ...
    def has_field(self, key: str) -> bool: ...
    def fields(self, *, data_type: str | None = None, prefix: str | None = None) -> Mapping[DataKey, FieldRef]: ...
```

Internally, this may be backed by `record.resources`, `record.metadata["rphys.fields"]`, or a future generic field mechanism in `loom`.

The public rphys dataset interface should use logical fields rather than resource-name special cases.

## 10. Metadata Versus Fields

Use this rule:

```text
If it is a payload that can be loaded, transformed, validated, collated, saved,
used by a model, used by a loss, or used by a metric, make it a field.

If it only describes the record/sample globally, make it metadata.
```

Usually metadata:

```text
dataset
subject_id
session_id
trial_id
scenario
split
dataset_version
protocol_name
source_path
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
skin segmentation masks
camera calibration if consumed by transforms or models
```

Some concepts may be either. For example, skin tone may be metadata if used only for reporting, but a field if used as a target, conditioning variable, fairness-stratification input, or collated model input.

## 11. I/O and Codecs

The I/O layer should convert `FieldRef` objects into runtime field values. Codecs should be field-aware rather than only file-aware.

Recommended protocol:

```python
class FieldCodec(Protocol):
    codec_key: str

    def probe(self, field: FieldRef) -> FieldMetadata: ...

    def load(
        self,
        field: FieldRef,
        *,
        region: LoadRegion | None = None,
    ) -> Any: ...

    def save(self, value: Any, field: FieldRef) -> None: ...
```

Examples:

```text
video.avi.opencv.v1
  FieldRef(video.rgb) -> VideoData

signal.ubfc_txt.v1
  FieldRef(signal.bvp, selector={column: bvp}) -> SignalData

landmarks.parquet.v1
  FieldRef(face.landmarks.468) -> LandmarkData

mesh.flame_npz.v1
  FieldRef(face.mesh.flame) -> MeshData

array.numpy.v1
  FieldRef(custom.embedding) -> ArrayData
```

Partial loading should be supported through regions:

```python
FrameRegion(start_frame=900, num_frames=300)
TimeRegion(start_time=30.0, duration=10.0)
SampleRegion(start_sample=1920, num_samples=640)
```

Video, signal, timestamp, landmark, mask, and mesh codecs should support windowed loading where practical.

## 12. Dataset Layer

The dataset layer should be record-centric before it is sample-centric.

Dataset adapters are responsible for:

```text
scanning native dataset layouts
regex/glob matching files
inferring subject/session/trial metadata
discovering raw resources
creating FieldRefs
representing missing/synthetic timestamps explicitly
validating record completeness where possible
emitting generic records with rphys field conventions
```

Dataset adapters should not:

```text
train models
apply stochastic augmentation
construct torch batches
move tensors to GPU
run model-specific preprocessing inside discovery
perform expensive sample loading in scan operations
```

Recommended dataset artifacts and views:

```text
DatasetManifest
  What records and fields exist?

DatasetView
  Which records and fields are selected?

TrainingIndex / EvaluationIndex
  Which windows or samples should be loaded?
```

### 12.1 Dataset Discovery

Discovery should support:

```text
filesystem walking
glob matching
regular-expression matching
nested dataset layouts
manual download instructions
automatic download where legal and practical
archive extraction helpers
checksum validation
dataset version metadata
partial-download detection
```

### 12.2 Validation

Validation should exist at multiple levels.

Dataset source validation:

```text
expected files exist
unexpected missing resources
duplicate records
bad filenames
unparseable metadata
wrong dataset version
```

Field/resource validation:

```text
video decodable
frame count known
fps known or inferable
timestamps monotonic
signal length valid
sample rate valid
signal and video durations compatible
landmark schema recognized
mesh topology valid
mask dimensions compatible
```

Sample validation:

```text
video window has expected frame count
target signal covers requested time window
no invalid NaNs or Infs
timestamps aligned
face ROI exists if required
mask dimensions match video
landmarks align with video frames
```

### 12.3 Filtering and Splitting

Filtering should occur at record level and sample/window level.

Record-level filters:

```text
DatasetIn
SubjectIn
SubjectNotIn
HasField
HasResource
HasVideo
HasPhysSignal
MinDuration
ScenarioEquals
QualityAtLeast
```

Window-level filters:

```text
valid signal coverage
valid video coverage
face coverage threshold
motion threshold
heart-rate range
landmark visibility
mask coverage
```

Splits should include:

```text
SubjectDisjointSplit
SessionDisjointSplit
TrainValTestBySubject
LeaveOneSubjectOut
LeaveOneDatasetOut
CrossDatasetSplit
ExplicitSplitFile
HashBasedSplit
```

Subject-disjoint splits should be first-class because random window-level splitting can leak subject/session information.

## 13. Sample Specs and Lazy Sample Building

Training datasets should load fields by `SampleSpec`, not by hard-coded conventions.

```python
sample_spec = SampleSpec(
    required={
        "video.rgb": FieldRequirement(data_type="video", runtime_type=VideoData),
        "signal.bvp": FieldRequirement(data_type="signal", runtime_type=SignalData),
    },
    optional={
        "face.landmarks.468": FieldRequirement(data_type="landmarks", runtime_type=LandmarkData),
        "face.mask.face": FieldRequirement(data_type="mask", runtime_type=MaskData),
    },
)
```

Index rows should contain field bindings and regions:

```python
IndexRow(
    sample_id="ubfc/s01/trial01/window_0007",
    record_id="ubfc/s01/trial01",
    fields={
        "video.rgb": FieldRef(...),
        "signal.bvp": FieldRef(...),
        "timestamps.video": FieldRef(...),
        "face.landmarks.468": FieldRef(...),
    },
    regions={
        "video.rgb": FrameRegion(start_frame=900, num_frames=300),
        "signal.bvp": TimeRegion(start_time=30.0, duration=10.0),
        "timestamps.video": FrameRegion(start_frame=900, num_frames=300),
        "face.landmarks.468": FrameRegion(start_frame=900, num_frames=300),
    },
    metadata={
        "subject_id": "s01",
        "split": "train",
    },
)
```

The sample builder then loads every field through the same mechanism:

```python
for key, field_ref in row.fields.items():
    region = row.regions.get(key)
    value = codec_registry.load(field_ref, region=region)
    sample = sample.with_field(key, value, metadata=field_ref.metadata)
```

The torch dataset should not scan directories or parse native dataset layouts.

```python
class RPhysTrainingDataset(torch.utils.data.Dataset):
    def __init__(self, index, sample_builder, transforms=None):
        self.index = index
        self.sample_builder = sample_builder
        self.transforms = transforms

    def __len__(self):
        return len(self.index)

    def __getitem__(self, idx):
        row = self.index[idx]
        sample = self.sample_builder(row)
        if self.transforms is not None:
            sample = self.transforms(sample)
        return sample
```

## 14. Ops Layer

`rphys.ops` should contain stateless or mostly stateless functional operations. These should not perform sample field plumbing. They should operate on tensors or typed modality objects.

Examples:

```text
rphys.ops.video.normalize.normalize_video
rphys.ops.video.resize.resize_video
rphys.ops.signal.filtering.bandpass_filter
rphys.ops.signal.resampling.resample_signal
rphys.ops.signal.correlation.pearson_corr
rphys.ops.temporal.alignment.align_by_timestamps
rphys.ops.physiology.heart_rate.estimate_hr
rphys.ops.multimodal.roi.crop_video_by_landmarks
```

The same op can be reused by transforms, losses, metrics, and analysis.

Example:

```text
rphys.ops.signal.spectral.compute_fft
  used by:
    rphys.losses.spectral.FrequencyDomainLoss
    rphys.evaluation.metrics.SNRMetric
    rphys.analysis.plots.PowerSpectrumPlot
```

## 15. Transform Layer

All runtime transforms should be:

```text
Sample -> Sample
```

Specialized base classes are convenience wrappers, not separate data-flow types.

Transform categories by scope:

```text
FieldTransform
  Reads one field and writes one field.

MultiFieldTransform
  Reads multiple fields and writes one or more fields.

SampleTransform
  May operate on the whole sample.

BatchTransform
  Operates on a batched Sample-like object after collation.

RecordTransform
  Operates on records before sample loading.

ManifestTransform
  Operates on whole manifests.

ResourceTransform
  Consumes FieldRefs or ResourceRefs and produces new FieldRefs or ResourceRefs.
```

Transform categories by behavior:

```text
DeterministicTransform
  Same input and config produce same output.

StochasticTransform
  Samples random parameters and applies them.

DerivedFieldTransform / Extractor
  Consumes fields and adds derived fields.

AnnotationTransform
  Adds metadata-like or quality fields.

ValidatorTransform
  Checks fields and may raise, annotate, or filter.
```

Recommended protocol:

```python
class SampleTransform(Protocol):
    input_contract: SampleContract
    output_contract: SampleContract
    deterministic: bool

    def __call__(
        self,
        sample: Sample,
        *,
        rng: RandomGenerator | None = None,
    ) -> Sample: ...
```

### 15.1 Field Transform Example

```python
class NormalizeVideo(FieldTransform):
    def __init__(self, mean, std, input_key="video.rgb", output_key=None):
        self.mean = mean
        self.std = std
        self.input_key = input_key
        self.output_key = output_key or input_key

    def __call__(self, sample: Sample, *, rng=None) -> Sample:
        video = sample.require(self.input_key, VideoData)
        frames = rphys.ops.video.normalize.normalize_video(
            video.frames,
            mean=self.mean,
            std=self.std,
        )
        return sample.with_field(
            self.output_key,
            replace(video, frames=frames),
        )
```

### 15.2 Multimodal Transform Example

```python
class CropVideoByLandmarks(MultiFieldTransform):
    def __call__(self, sample: Sample, *, rng=None) -> Sample:
        video = sample.require(self.video_key, VideoData)
        landmarks = sample.require(self.landmarks_key, LandmarkData)

        cropped_video, transformed_landmarks, roi = (
            rphys.ops.multimodal.roi.crop_video_by_landmarks(
                video=video,
                landmarks=landmarks,
                padding=self.padding,
                output_size=self.output_size,
            )
        )

        sample = sample.with_field(self.output_video_key, cropped_video)
        sample = sample.with_field(self.output_landmarks_key, transformed_landmarks)
        sample = sample.with_field(self.output_roi_key, roi)
        return sample
```

### 15.3 Stochastic Transform Design

Stochastic transforms should sample parameters separately from applying them.

```python
params = transform.sample_params(sample, rng)
sample = transform.apply(sample, params)
```

This is essential for synchronized multimodal augmentation.

Example:

```text
SynchronizedSpatialCrop
  reads:
    video.rgb
    face.landmarks.468
    face.mask.face

  samples:
    crop box

  writes:
    cropped video.rgb
    transformed face.landmarks.468
    cropped face.mask.face
```

Example:

```text
SynchronizedTemporalCrop
  reads:
    video.rgb
    signal.bvp
    timestamps.video
    face.landmarks.468

  samples:
    start time and duration

  writes:
    temporally matched video, signal, timestamps, and landmarks
```

### 15.4 Extraction, Annotation, and Validation

Not all preprocessing is the same. The package should distinguish:

```text
processing
  Modifies an existing field.

augmentation
  Stochastic modification of existing fields, usually training-time only.

extraction
  Derives new fields from existing fields.

annotation
  Adds quality scores, metadata-like fields, or derived labels.

validation
  Checks fields and may raise, mark invalid, or filter.

formatting
  Changes storage representation and produces new resources or manifests.
```

Landmark extraction is best treated as deterministic derived-field extraction.

Runtime mode:

```text
Sample(video.rgb)
  -> LandmarkExtractor
  -> Sample(video.rgb, face.landmarks.468)
```

Offline stage mode:

```text
raw manifest
  -> ComputeLandmarksStage
  -> landmark resources
  -> processed manifest with face.landmarks.468 FieldRefs
```

The transform can be the same; the stage decides whether the output stays in memory or is persisted.

## 16. Bundle Specs and Transform Contracts

A bundle spec describes a common group of fields without making a new sample class.

Example:

```python
FaceTrackingBundle = BundleSpec(
    required={
        "video.rgb": VideoData,
        "face.landmarks.468": LandmarkData,
    },
    optional={
        "face.mask.face": MaskData,
        "face.roi": ROIData,
    },
)
```

A transform may declare:

```python
class FaceROIExtractor(MultiFieldTransform):
    input_bundle = FaceTrackingBundle
    outputs = {
        "video.face_roi": VideoData,
        "face.roi": ROIData,
    }
```

This makes dependencies explicit without creating many compound data classes.

## 17. Collation

Collation should preserve the unified interface.

```text
Sequence[Sample] -> Batch
```

The `Batch` should expose the same methods:

```python
batch.has("video.rgb")
batch.require("signal.bvp")
batch.metadata["record_id"]
```

Field-level collation policy is required because different fields require different behavior.

Default policies:

```text
fixed-size tensors:
  stack

variable-length tensors:
  pad or list

strings and metadata:
  list

optional missing fields:
  missing/null policy

ragged landmarks:
  pad or list

video with variable T:
  pad, crop, reject, or list

mesh sequences:
  pad, list, or custom
```

A field can specify its policy:

```python
FieldValue(
    value=video,
    data_type="video",
    collate=CollatePolicy.STACK,
)
```

Typed data objects can also provide custom collation:

```python
class VideoData(DataObjectBase):
    @classmethod
    def collate(cls, values: Sequence["VideoData"], policy: CollatePolicy) -> "VideoData":
        ...
```

The generic collator should understand:

```text
Sample
Batch
FieldValue
DataObjectBase
torch.Tensor
numpy.ndarray
numbers
strings
None
mappings
sequences
dataclasses
```

## 18. Formatting, Preprocessing, and Stages

Formatting, preprocessing, and augmentation should not be collapsed.

```text
Formatting
  Storage/layout normalization. Usually deterministic and reusable across experiments.

Deterministic preprocessing
  Data transformation. May be reusable but often model- or protocol-specific.

Stochastic augmentation
  Training-time random transformation. Usually not persisted as a dataset artifact.
```

Examples of formatting:

```text
AVI/MP4 -> chunked tensor store
frame directory -> canonical video store
text signal -> parquet or zarr signal store
native metadata -> canonical sidecar
synthetic timestamps -> explicit timestamp resource
```

Examples of deterministic preprocessing:

```text
resize
crop
face detection
landmark extraction
ROI extraction
temporal resampling
signal filtering
signal normalization
video-signal synchronization
quality annotation
```

Examples of stochastic augmentation:

```text
random crop
random temporal jitter
color jitter
noise injection
time masking
frame dropping
signal perturbation
multimodal dropout
```

Stages should perform artifact-producing orchestration. The domain work should be delegated to `rphys` APIs.

```text
Transform:
  Sample -> Sample

Stage:
  Manifest/Index/ArtifactRef -> Manifest/Index/ArtifactRef
```

Heavy deterministic work such as landmark extraction, face segmentation, mesh fitting, optical flow, and quality annotation should usually have offline stage support.

## 19. Models

Models should be included in `rphys` when they are canonical, reusable, or used across multiple experiments.

Include:

```text
canonical baseline architectures
widely reused rPPG architectures
small reference implementations
model input/output specs
checkpoint compatibility helpers
preprocessing requirement declarations
```

Do not include:

```text
every paper-specific variant
one-off ablation models
unmaintained model zoo sprawl
training scripts embedded in model classes
generic neural-network utilities with no rphys relevance
```

Promotion rule:

```text
Used by one experiment:
  keep it in the experiment package.

Used across multiple experiments:
  consider promoting to rphys.

Canonical baseline or common reference model:
  belongs in rphys.

Generic and domain-agnostic:
  probably does not belong in rphys.
```

Models should be normal PyTorch modules. They should not scan datasets, build batches, manage artifacts, or own pipeline execution.

## 20. Losses

Losses should be top-level, not hidden under `models`. Losses are training objectives, not model definitions.

Recommended grouping:

```text
rphys.losses.core
  base classes, reductions, composite losses, adapters

rphys.losses.waveform
  MSE, L1, Pearson, cosine, phase, DTW-like losses

rphys.losses.spectral
  FFT, SNR, bandpower, peak-frequency, spectral convergence losses

rphys.losses.temporal
  smoothness, derivative, periodicity, temporal consistency losses

rphys.losses.physiological
  heart-rate, pulse-band, BVP constraints, pulse consistency losses

rphys.losses.probabilistic
  Gaussian NLL, Laplace NLL, uncertainty losses

rphys.losses.contrastive
  temporal, subject, and view contrastive losses

rphys.losses.regularization
  spatial, temporal, entropy, and weight regularizers

rphys.losses.multitask
  weighted sums, uncertainty weighting, scheduled terms
```

Losses should generally be `nn.Module` objects, but the mathematical implementation should use `rphys.ops` where possible.

Support at least three loss styles:

```text
TensorLoss
  forward(pred: Tensor, target: Tensor)

BatchLoss
  forward(prediction, batch)

CompositeLoss
  combines named loss terms
```

Many rPPG losses need more than `(prediction, target)`. They may need:

```text
timestamps
sample rate
validity mask
record metadata
window duration
frequency band
expected heart-rate range
```

Therefore, the base design should allow:

```python
loss_value = loss(
    prediction=prediction,
    target=target,
    batch=batch,
    metadata=batch.metadata,
)
```

Composite loss example:

```yaml
loss:
  _target_: rphys.losses.core.composite.WeightedSumLoss
  terms:
    waveform:
      weight: 1.0
      loss:
        _target_: rphys.losses.waveform.NegativePearsonLoss

    spectral:
      weight: 0.2
      loss:
        _target_: rphys.losses.spectral.SpectralConvergenceLoss
        min_hz: 0.7
        max_hz: 4.0

    smoothness:
      weight: 0.05
      loss:
        _target_: rphys.losses.temporal.TemporalSmoothnessLoss
```

## 21. Training

The training package should provide domain-specific glue, not generic experiment orchestration.

Training components:

```text
lazy torch Dataset over TrainingIndex
sample builders
input adapters
target adapters
batch adapters
domain-aware dataloader builders
trainer wrappers
optimizer/scheduler builders, if useful
checkpoint helpers
```

Input adapters prevent model assumptions from leaking into datasets.

```python
class VideoOnlyInputAdapter:
    def __call__(self, batch: Batch) -> dict[str, torch.Tensor]:
        return {"x": batch.require("video.rgb", VideoData).frames}
```

Target adapters isolate loss targets.

```python
class SignalTargetAdapter:
    def __call__(self, batch: Batch) -> torch.Tensor:
        return batch.require("signal.bvp", SignalData).values
```

Training should support:

```text
windowed training
record-level training
multi-view input
video-only input
video + landmarks
video + masks
video + meshes
signal reconstruction
heart-rate regression
multi-task targets
```

Training checkpoint state belongs in `rphys.training.checkpointing`. Model architecture metadata and compatibility helpers belong in `rphys.models.core.checkpoints`.

## 22. Evaluation

Evaluation should preserve enough structure for scientific reporting.

Prediction artifacts should contain:

```text
record_id
subject_id
dataset
window_id
timestamps
predicted waveform
target waveform, optional
predicted heart rate, optional
target heart rate, optional
model/checkpoint metadata
preprocessing metadata
aggregation metadata
```

Suggested structures:

```text
WindowPrediction
RecordPrediction
PredictionSet
MetricReport
EvaluationReport
```

Metrics:

```text
MAE
RMSE
Pearson correlation
heart-rate MAE
heart-rate RMSE
BVP waveform correlation
SNR
frequency-domain error
coverage rate
missing prediction rate
per-record aggregate metrics
per-subject aggregate metrics
cross-dataset metrics
```

Evaluation protocols:

```text
PerWindowProtocol
PerRecordAggregateProtocol
WithinDatasetProtocol
CrossDatasetProtocol
LeaveOneSubjectOutProtocol
LeaveOneDatasetOutProtocol
OfficialSplitProtocol
```

Remote physiological measurement results are protocol-sensitive, so evaluation protocols should be explicit and reusable.

## 23. Analysis

Analysis should consume outputs, not rerun training or evaluation.

Include:

```text
metric table generation
subject-level summaries
dataset-level summaries
confidence intervals
bootstrap utilities
statistical tests
failure-case mining
quality-stratified metrics
plots
HTML/Markdown report generation
LaTeX table generation
```

Domain-specific analyses:

```text
metric by dataset
metric by subject
metric by skin-tone, lighting, or motion metadata if available
metric by signal quality
metric by face-detection coverage
metric by heart-rate range
prediction-target waveform overlays
Bland-Altman plots
error distribution plots
frequency-spectrum visualizations
```

## 24. Recipes and Stages

Recipes should provide reusable domain defaults. The recipe mechanism itself belongs to `loom`; concrete rphys recipe definitions belong in `rphys`.

Stages should be thin domain orchestration over package APIs.

Examples:

```text
rphys.stages.datasets.IndexRPhysDatasetStage
rphys.stages.datasets.BuildDatasetViewStage
rphys.stages.datasets.BuildTrainingIndexStage
rphys.stages.preprocessing.ComputeFaceLandmarksStage
rphys.stages.preprocessing.PreprocessRPhysDatasetStage
rphys.stages.training.TrainRPhysModelStage
rphys.stages.evaluation.EvaluateRPhysModelStage
rphys.stages.analysis.MakeReportStage
rphys.stages.inference.BatchInferenceStage
```

Stage design rules:

```text
Stages consume ArtifactRefs and produce ArtifactRefs.
Stages should not depend on in-memory outputs from previous stages.
Stages should be independently runnable through loom stage execution.
Stages should keep domain work delegated to rphys APIs.
Stages should return all declared outputs.
Stages should be safe to rerun when loom decides they are stale.
```

## 25. Dependency Policy

Use optional extras to avoid forcing heavy libraries on all users.

Suggested extras:

```text
rphys[io-video]
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

Import boundaries:

```text
rphys.conventions:
  no heavy dependencies

rphys.datasets:
  mostly no torch

rphys.io:
  optional backend dependencies

rphys.data:
  torch-dependent if tensor traversal is implemented here

rphys.training:
  torch-dependent

rphys.models:
  torch-dependent

rphys.analysis:
  pandas/matplotlib/scipy-dependent
```

Start as one package. Split only if dependency conflicts, install profiles, or ownership boundaries justify it.

## 26. Testing Strategy

Testing should include unit tests, contract tests, synthetic data tests, and smoke pipelines.

Unit test areas:

```text
DataKey and field conventions
Sample and Batch APIs
collation policies
DataObjectBase tensor traversal
modality validation
FieldRef loading
codec registry
dataset adapters
filters and splits
index builders
sample builders
transforms
stochastic transform reproducibility
multimodal synchronized transforms
losses
metrics
input/target adapters
stage contracts
recipe expansion
```

Synthetic data should include:

```text
small video tensors
synthetic timestamps
synthetic BVP signals
landmarks
masks
metadata with subject/session/trial IDs
expected manifests
expected training indexes
```

A CI smoke pipeline should run:

```text
index synthetic dataset
build dataset view
build training index
lazy-load samples
apply transform pipeline
collate batch
train for a few steps
evaluate
compute metrics
produce analysis summary
```

## 27. V0 Implementation Scope

The first version should implement the smallest vertical slice that validates the architecture.

### 27.1 Core Data

Implement:

```text
DataKey
FieldValue
FieldRef
Sample
Batch
SampleContract
SampleSpec
BundleSpec
CollatePolicy
generic_collate
DataObjectBase
```

### 27.2 Initial Modalities

Implement:

```text
VideoData
SignalData
TimestampData
LandmarkData
MaskData
```

Defer full mesh support unless there is an immediate dataset need, but keep the field system able to represent meshes.

### 27.3 Initial I/O

Implement:

```text
one video codec
one signal codec
one timestamp codec
one landmark codec if landmarks are included in the first real pipeline
codec registry
field-aware partial loading
```

### 27.4 Initial Datasets

Implement:

```text
synthetic dataset adapter
one real adapter, probably UBFC
manifest generation
record validation
subject-disjoint split
training index builder
```

### 27.5 Initial Ops and Transforms

Implement:

```text
video normalization
video resize
signal filtering
signal resampling
temporal windowing
video-signal alignment
synchronized temporal crop
optional landmark extraction wrapper
```

### 27.6 Initial Training

Implement:

```text
lazy TrainingDataset
SampleBuilder over TrainingIndex
VideoOnlyInputAdapter
SignalTargetAdapter
basic Trainer wrapper
checkpoint helpers
```

### 27.7 Initial Models and Losses

Implement:

```text
one baseline model
NegativePearsonLoss
SignalMSELoss
WeightedSumLoss
```

### 27.8 Initial Evaluation and Analysis

Implement:

```text
PredictionSet
MAE
RMSE
Pearson
heart-rate error
simple evaluation protocol
metric report
basic tables or Markdown report
```

## 28. Development Phases

### Phase 1: Data and Field System

Goal:

```text
A record with arbitrary logical fields can be lazily loaded into a Sample.
```

Implement:

```text
DataKey
FieldRef
FieldValue
Sample
Batch
collation
codec registry
synthetic data
```

### Phase 2: Dataset Indexing

Goal:

```text
A native dataset can be scanned, validated, filtered, split, and indexed without loading full samples.
```

Implement:

```text
dataset adapter protocol integration
synthetic adapter
UBFC adapter
manifest helpers
views
subject splits
window index builder
```

### Phase 3: Runtime Transform Pipeline

Goal:

```text
Sample -> Sample pipelines work for field, multimodal, deterministic, stochastic, extraction, validation, and annotation transforms.
```

Implement:

```text
transform base classes
Compose
field selectors
sample contracts
stochastic parameter sampling
video/signal transforms
synchronized temporal crop
video-signal alignment
```

### Phase 4: Minimal Training

Goal:

```text
A model can train from a lazy rphys TrainingIndex.
```

Implement:

```text
TrainingDataset
sample builders
input/target adapters
baseline model
losses
trainer
checkpointing
```

### Phase 5: Evaluation and Metrics

Goal:

```text
A checkpoint can produce predictions, metrics, and reports.
```

Implement:

```text
PredictionSet
evaluation dataloader
evaluation protocol
metric implementations
report payloads
```

### Phase 6: Offline Processing Stages

Goal:

```text
Expensive deterministic operations can be persisted as artifacts.
```

Implement:

```text
formatting stage
landmark extraction stage
quality annotation stage
processed manifest output
```

### Phase 7: Broader Domain Coverage

Goal:

```text
Add datasets, models, losses, protocols, and analysis tools without changing the core architecture.
```

Add:

```text
PURE
MAHNOB
COHFACE
VIPL-HR
EfficientPhys
TS-CAN
cross-dataset evaluation
advanced losses
quality-stratified reports
```

## 29. Key Design Rules

The design should preserve these rules:

```text
1. Do not special-case video.
   Video is the most common field, not a privileged field.

2. All runtime transforms should be Sample -> Sample.

3. Functional math and tensor operations belong in rphys.ops.
   Transform classes wrap ops and handle field plumbing.

4. Dataset discovery, filtering, indexing, and loading are separate.

5. Dataset adapters expose logical fields through FieldRefs.

6. Multiple logical fields may come from one physical resource.

7. Batches should preserve the same field access interface as samples.

8. Stochastic multimodal transforms must sample shared parameters before applying them.

9. Formatting, deterministic preprocessing, stochastic augmentation, extraction,
   annotation, and validation are different concepts.

10. Losses are top-level and grouped by training signal type.

11. Metrics are evaluation objects, not losses.

12. Heavy deterministic extraction should usually be available as an offline stage.

13. rphys owns domain concepts. loom owns generic execution infrastructure.
```

## 30. Example Minimal Pipeline

Example resolved flow:

```text
IndexRPhysDatasetStage
  native UBFC root
  -> records with FieldRefs:
       video.rgb
       signal.bvp
       timestamps.video
  -> DatasetManifest

BuildDatasetViewStage
  DatasetManifest
  -> subject-disjoint filtered view

BuildTrainingIndexStage
  DatasetView
  -> windowed TrainingIndex

TrainRPhysModelStage
  TrainingIndex
  -> lazy RPhysTrainingDataset
  -> SampleBuilder loads requested fields
  -> Sample transforms:
       AlignVideoSignal
       ResizeVideo
       NormalizeVideo
       SynchronizedTemporalCrop
  -> collate_samples produces Batch
  -> input adapter selects video.rgb
  -> target adapter selects signal.bvp
  -> model and losses
  -> checkpoint artifacts

EvaluateRPhysModelStage
  checkpoint + EvaluationIndex
  -> predictions
  -> metrics
  -> EvaluationReport
```

## 31. Example Config Sketch

```yaml
schema_version: 1
name: physnet_ubfc_baseline

run:
  seed: 42
  output_dir: runs/${name}/${run.seed}/${timestamp}

data:
  source:
    _target_: rphys.datasets.sources.LocalDatasetSource
    root: /data/ubfc

  adapter:
    _target_: rphys.datasets.adapters.ubfc.UBFCAdapter

  sample_spec:
    required:
      video.rgb:
        data_type: video
        runtime_type: rphys.data.modalities.video.VideoData
      signal.bvp:
        data_type: signal
        runtime_type: rphys.data.modalities.signal.SignalData
    optional:
      timestamps.video:
        data_type: timestamps
        runtime_type: rphys.data.modalities.timestamps.TimestampData

transforms:
  train:
    _target_: rphys.transforms.core.compose.Compose
    transforms:
      - _target_: rphys.transforms.multimodal.deterministic.AlignVideoSignal
        video_key: video.rgb
        signal_key: signal.bvp
        timestamp_key: timestamps.video

      - _target_: rphys.transforms.video.deterministic.ResizeVideo
        input_key: video.rgb
        output_key: video.rgb
        size: [128, 128]

      - _target_: rphys.transforms.video.deterministic.NormalizeVideo
        input_key: video.rgb
        output_key: video.rgb
        mean: [0.5, 0.5, 0.5]
        std: [0.5, 0.5, 0.5]

      - _target_: rphys.transforms.multimodal.stochastic.SynchronizedTemporalCrop
        duration_seconds: 10.0
        fields:
          - video.rgb
          - signal.bvp
          - timestamps.video

model:
  _target_: rphys.models.architectures.physnet.model.PhysNet
  hidden_channels: 64

loss:
  _target_: rphys.losses.core.composite.WeightedSumLoss
  terms:
    waveform:
      weight: 1.0
      loss:
        _target_: rphys.losses.waveform.pearson.NegativePearsonLoss

training:
  dataset:
    _target_: rphys.training.datasets.RPhysTrainingDataset

  sample_builder:
    _target_: rphys.training.sample_builders.FieldSampleBuilder

  input_adapter:
    _target_: rphys.training.input_adapters.VideoOnlyInputAdapter
    video_key: video.rgb

  target_adapter:
    _target_: rphys.training.target_adapters.SignalTargetAdapter
    signal_key: signal.bvp

pipeline:
  stages:
    - name: index
      target:
        _target_: rphys.stages.datasets.IndexRPhysDatasetStage

    - name: build_training_index
      target:
        _target_: rphys.stages.datasets.BuildTrainingIndexStage
      inputs:
        manifest: index.manifest

    - name: train
      target:
        _target_: rphys.stages.training.TrainRPhysModelStage
      inputs:
        training_index: build_training_index.training_index

    - name: evaluate
      target:
        _target_: rphys.stages.evaluation.EvaluateRPhysModelStage
      inputs:
        checkpoint: train.best_checkpoint
        evaluation_index: build_training_index.evaluation_index
```

## 32. Final Recommendation

The revised `rphys` package should be built around a small number of core abstractions:

```text
DataKey
FieldRef
FieldValue
Sample
Batch
SampleSpec
BundleSpec
FieldCodec
SampleTransform
CollatePolicy
TrainingIndex
PredictionSet
MetricReport
```

Everything else should extend these abstractions.

The most important practical rule is:

```text
Make the data interface generic, but make the payloads typed.
```

That gives `rphys` enough structure for maintainable remote physiological measurement research while keeping it open to future datasets and modalities such as landmarks, meshes, masks, optical flow, calibration fields, quality traces, metadata annotations, and arbitrary experiment-specific payloads.
