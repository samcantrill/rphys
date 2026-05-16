# PURE DataSource And Prepared Training Data Findings

Date: 2026-05-16
Status: findings for a possible standalone roadmap item
Scope: PURE raw ingestion, rphys-native formatting, filtering, splitting,
indexing, prepared/materialized data, and LitData-backed training access.

## Summary

PURE can fit the current `rphys` architecture, but it should be treated as a
real `DataSource` integration rather than a new `Dataset` package or a training
shortcut. The clean path is:

1. scan the license-restricted raw PURE copy into descriptor-only
   `DataSourceRef` and `RecordRef` objects;
2. validate raw structure, field availability, sampling rates, subject/task
   metadata, and reference-signal shape;
3. build non-mutating views, filters, subject-disjoint splits, and
   `DataSourceIndex` manifests;
4. export or materialize deterministic formatted fields into an immutable
   rphys-native prepared product;
5. expose that prepared product through `PreparedSampleSource` and an
   import-gated LitData reader/writer adapter for training.

The main architectural constraint is that raw scanning, deterministic
formatting, LitData optimization, and training iteration are separate layers.
The PURE adapter should not decode every frame during scan, choose hidden
splits, run face detection inside `__getitem__`, write LitData chunks directly
from datasource discovery, or convert samples into model-specific tuples.

## External Dataset Facts

The official PURE page describes 10 people, six controlled head-motion setups,
and one-minute face recordings with parallel pulse measurements. It records the
camera setup as 30 Hz, 640x480 RGB video and the reference pulse oximeter as
60 Hz pulse wave plus SpO2 readings. The page also states that access requires
contacting TU Ilmenau and cites Stricker, Mueller, and Gross, RO-MAN 2014.

The observed raw layout used by rPPG-Toolbox expects directories like
`RawData/01-01/`, nested frame folders such as `RawData/01-01/01-01/*.png`,
and a sidecar JSON file such as `RawData/01-01/01-01.json`. That loader reads
frames by sorted PNG path and reads BVP labels from JSON entries under
`/FullPackage`, specifically `Value.waveform`.

Treat these as implementation evidence, not an immutable contract. The first
PURE phase should verify the actual licensed archive locally, including whether
all 60 subject-task sequences are present, whether any task is missing, whether
filenames are consistently nested, and whether JSON keys include pulse rate,
SpO2, timestamps, or only waveform values in the available copy.

## Current Repository Fit

The relevant existing contracts are already mostly in place:

- `src/rphys/datasources/adapters.py` provides descriptor-only
  `DataSourceSpec`, `DataSourceAdapter`, and `DataSourceScanResult`.
- `src/rphys/datasources/filters.py` provides non-mutating views and
  `FilterChain` behavior over descriptor or candidate targets.
- `src/rphys/datasources/splits.py` provides candidate-level group extraction
  and explicit group-disjoint split assignment.
- `src/rphys/datasources/indexes.py` provides `IndexCandidate`,
  `DataSourceIndex`, sidecar entries, manifests, and composite indexes.
- `src/rphys/data/sample_builders.py` bridges one `IndexItem` to a
  FieldLocator-keyed runtime `Sample`.
- `src/rphys/datasources/sources.py`, `cache.py`, `prepared.py`, and `torch.py`
  provide `SampleSource`, deterministic cache records, prepared manifests and
  readers, and optional torch loading boundaries.
- `src/rphys/ops/export.py` and `src/rphys/datasources/derived.py` support the
  right place for deterministic formatted outputs and derived datasource refs.

The missing work is a real PURE-specific adapter, dataset-specific validation
and field mapping, formatted output/materialization policy, and an optional
LitData prepared-storage backend. None of those should be added to
`rphys.__init__`, `rphys.datasets`, or package-level `rphys.datasources`
re-exports unless a later roadmap approval explicitly broadens public imports.

## Proposed Roadmap Item

Name:

```text
PURE DataSource And Prepared Training Data
```

Goal:

```text
Make a local licensed PURE copy discoverable, validated, filtered, split,
indexed, deterministically formatted, and optionally materialized into
LitData-backed prepared training data while preserving rphys field,
provenance, split, and optional-dependency contracts.
```

Primary package areas:

```text
src/rphys/datasources/pure/
src/rphys/datasources/prepared.py
src/rphys/datasources/prepared_litdata.py      # proposed optional backend
src/rphys/ops/export.py                        # use existing export boundary
src/rphys/io/
tests/unit/rphys/datasources/pure/
tests/contracts/
tests/integration/
tests/acceptance/
docs/roadmap/stage-<new>/
```

`prepared_litdata.py` is recommended as a reusable optional backend adapter,
not a PURE-only adapter. PURE-specific planning should decide whether that file
lands in this roadmap item or is split into a prerequisite generic prepared
backend item.

## Proposed Package Shape

Use a subpackage only when code-backed behavior exists. Avoid placeholder files.

```text
src/rphys/datasources/pure/
  __init__.py          # narrow, code-backed exports only
  constants.py         # subject/task naming and PURE field keys, if needed
  raw.py               # raw layout scanner and JSON/frame descriptor parsing
  validation.py        # PURE-specific descriptor validation helpers/reports
  fields.py            # PURE raw-to-rphys field mapping helpers
  codecs.py            # optional raw frame/json codecs, import-gated
  materialization.py   # PURE materialization plans over existing ops/prepared APIs
```

Candidate generic backend path:

```text
src/rphys/datasources/prepared_litdata.py
```

This module should import `litdata` only inside backend construction or
execution methods. Importing `rphys`, `rphys.datasources`, or
`rphys.datasources.prepared` must not import LitData, torch, OpenCV, NumPy,
Pillow, imageio, or any dataset SDK.

## Data Model

Recommended rphys fields for the first implementation:

```text
inputs/video.rgb
targets/signal.bvp.reference
targets/label.pulse_rate.reference       # only if JSON exposes pulse-rate labels
targets/signal.spo2.reference            # only if JSON exposes SpO2 readings
source/timestamps.video.seconds
source/timestamps.signal.bvp.seconds
diagnostics/quality.pure.raw_structure   # optional, if represented as a field
```

Recommended metadata:

```text
subject_id
record_id
source_id
pure_task
pure_task_index
pure_subject_index
camera_fps
reference_sample_rate_hz
raw_record_path
raw_json_path
raw_frame_path
```

Subject, task, split, and group values should stay as metadata unless a method,
loss, metric, operation, or analysis component needs to load them as structured
fields. Activity labels such as steady, talking, translation, and rotation are
analysis/split metadata initially, not model inputs by default.

## Stage 0: Access, Policy, And Raw Audit

Deliverables:

- Record that PURE raw data is not committed and is obtained externally from
  TU Ilmenau.
- Add a small local-only audit command or acceptance helper that scans a user
  supplied PURE root and reports observed subject-task folders, JSON keys,
  frame counts, label counts, sampling rates, and missing records.
- Document that official material says 60 one-minute sequences, but the code
  must validate the actual local archive rather than assuming all 60 exist.
- Decide whether the roadmap item includes only raw descriptors plus prepared
  materialization, or also includes deterministic face cropping/resizing.

Repository work:

```text
docs/roadmap/stage-<new>/planning.md
tests/acceptance/test_pure_raw_audit.py       # marked acceptance, local path only
```

Acceptance tests must be opt-in and require an environment variable such as
`RPHYS_PURE_ROOT`. They must not run in default CI.

## Stage 1: PURE Raw Scanner

Implement a `DataSourceAdapter` that turns the raw PURE directory into
descriptor-only records.

Behavior:

- Accept a `DataSourceSpec` with a `DataSourceRef.source` pointing at the raw
  PURE root.
- Discover record IDs such as `01-01`, extracting subject and task metadata.
- Detect the expected nested frame folder and sidecar JSON file for each
  record.
- Emit one `RecordRef` per valid raw record, with `FieldRef`s for video frames
  and reference signal JSON resources.
- Preserve raw resource paths exactly in `ResourceRef`; do not normalize in a
  way that changes manifest fingerprints.
- Record warnings or rejections for missing nested frame folders, missing JSON,
  empty frame lists, malformed IDs, duplicate records, and unknown tasks.

Non-goals:

- No frame decoding during scan.
- No BVP resampling during scan.
- No face detection, cropping, resizing, normalization, split assignment,
  LitData writing, torch dataset construction, or training tuple formatting.

Tests:

```text
tests/unit/rphys/datasources/pure/test_raw.py
tests/contracts/test_pure_datasource_contract.py
```

Use tiny license-safe synthetic PURE-like folders with a few PNG placeholders
or text-backed fake resources. Do not include raw PURE data.

## Stage 2: PURE Validation

Validation should convert scan evidence into explicit diagnostics before any
formatting or indexing happens.

Checks:

- record ID grammar and subject/task extraction;
- expected task vocabulary and task-to-description mapping;
- frame folder presence and non-empty frame listing;
- JSON parseability and required `/FullPackage` shape;
- waveform availability and finite numeric values where lightweight JSON
  parsing is allowed;
- expected or observed camera frame rate and reference sample rate metadata;
- approximate duration consistency between video frames and reference samples;
- duplicate, missing, or extra subject-task records;
- optional presence of pulse-rate and SpO2 values if the local JSON exposes
  them.

Important scientific contract:

The raw reference signal is sampled at 60 Hz while video is recorded at 30 Hz.
The implementation must preserve native reference timestamps or native sample
indices. If a training product resamples BVP to video frame count, that
resampling is a deterministic materialization operation with an operation
fingerprint, not a property of the raw datasource.

Repository work:

```text
src/rphys/datasources/pure/validation.py
tests/unit/rphys/datasources/pure/test_validation.py
tests/integration/test_pure_synthetic_scan_validation_flow.py
```

## Stage 3: Field Codecs And Loading

Add only the minimum code needed to load PURE fields through existing codec and
sample-builder contracts.

Likely codecs:

- a raw frame-sequence codec for `video.rgb` resources backed by sorted PNGs;
- a JSON reference-signal codec for BVP waveform, pulse rate, SpO2, and
  optional timestamp arrays;
- possibly a lightweight metadata codec only if metadata must become a field.

Dependency posture:

- Keep heavy decode libraries optional and import-gated.
- Prefer standard-library JSON parsing for descriptor validation.
- If image loading needs Pillow, imageio, or OpenCV, put that behind codec
  construction/load calls, not module import.
- Do not make NumPy a base dependency unless the roadmap accepts an optional
  data extra or a broader scientific runtime dependency.

Tests:

```text
tests/unit/rphys/datasources/pure/test_codecs.py
tests/integration/test_pure_synthetic_index_sample_builder_flow.py
tests/package/test_import_boundaries.py
```

## Stage 4: Views, Filters, Groups, And Splits

Use existing datasource primitives rather than custom split code.

Recommended filters:

- include/exclude subject IDs;
- include/exclude task names or task indexes;
- require fields such as video and BVP reference;
- reject malformed or missing raw resources;
- reject records shorter than a configured duration;
- reject records with invalid or missing labels;
- candidate-level filters for window length, finite labels, valid face/quality
  evidence, and deterministic materialization availability.

Recommended grouping:

```text
GroupPlan({
  "subject": "subject_id",
  "task": "pure_task",
})
```

Recommended splitting:

- use subject-disjoint splits by default;
- use explicit subject-to-split assignments for the first roadmap item because
  PURE has only 10 subjects and no official train/valid/test split in the
  current rphys contract;
- preserve task as an analysis group so metrics can report motion-condition
  behavior;
- do not split windows or clips randomly across train and validation, because
  that leaks subject identity and near-duplicate temporal content.

Repository work:

```text
tests/unit/rphys/datasources/pure/test_filters.py
tests/unit/rphys/datasources/pure/test_splits.py
tests/contracts/test_datasource_group_split_contract.py
```

If ratio-plus-seed split helpers are desired for PURE, that should be a
separate design decision because current split code is explicit
group-to-split assignment.

## Stage 5: Index And Window Construction

Build `IndexCandidate`s and `DataSourceIndex` entries over whole records and
field-native temporal windows.

Initial index modes:

- whole-record index for inspection and baseline methods;
- fixed-frame clip windows over `inputs/video.rgb`;
- corresponding reference-signal windows in native BVP sample space;
- optional overlap/stride settings recorded in index metadata.

Scientific details to preserve:

- video and BVP have different native sample rates;
- matching numeric slices across fields must not imply alignment;
- any frame-to-signal mapping must be explicit in window metadata or
  materialization provenance;
- invalid short windows fail or are rejected with reasons rather than silently
  padded;
- windows inherit subject, task, split, group, record ID, and raw source
  provenance through sidecar `DataSourceIndexEntry` metadata.

Repository work:

```text
src/rphys/datasources/pure/fields.py
tests/unit/rphys/datasources/pure/test_indexing.py
tests/integration/test_pure_synthetic_scan_split_index_flow.py
```

## Stage 6: Rphys-Native Formatted Data

The "cohesive/formatted structure" should be an exported or materialized
derived datasource, not an alternate scanner that bypasses descriptors.

Recommended formatted output:

```text
<output_root>/pure-rphys-v1/
  manifest.json
  datasource.json
  indexes/
    pure_records.index.json
    pure_windows.index.json
  records/
    <subject_id>/<task>/<record_id>/
      fields/
        video.rgb.<codec-owned-extension>
        signal.bvp.reference.<codec-owned-extension>
        timestamps.video.seconds.<codec-owned-extension>
        timestamps.signal.bvp.seconds.<codec-owned-extension>
      metadata.json
```

The exact field file extensions should be selected by codecs and materialization
requirements. The roadmap should avoid freezing NumPy, Zarr, image folders, or
LitData as the only formatted representation unless implementation evidence
proves that is the right public contract.

Materialization responsibilities:

- create deterministic output paths;
- record source raw resources and checksums where available;
- record operation fingerprints for resampling, cropping, resizing,
  normalization, mask generation, or fixed feature extraction;
- make idempotency explicit: conflict, skip, replace, or write;
- emit derived `DataSourceRef` and `RecordRef` descriptors;
- emit `DataSourceIndexManifest` files for records and windows;
- never mutate the raw datasource descriptors in place.

Repository work:

```text
src/rphys/datasources/pure/materialization.py
tests/integration/test_pure_synthetic_formatting_flow.py
```

This stage should reuse `rphys.ops.export` and `rphys.datasources.derived`
where possible. If those APIs are insufficient, record the gap rather than
putting export behavior inside the scanner.

## Stage 7: Prepared Manifest And LitData Optimization

LitData should be treated as one optimized prepared-storage backend behind the
existing prepared-data contract.

Required behavior:

- build a `PreparedDataManifest` for the PURE prepared product;
- include source datasource/index identity, request fingerprint, fields,
  shapes, dtypes, splits, groups, checksums, layout, cost metadata, software
  versions, and invalidation inputs;
- write LitData chunks only for deterministic materialized fields requested by
  a `SampleRequest`;
- expose a `PreparedSampleReader` implementation that reads LitData samples and
  returns FieldLocator-keyed `Sample` objects through `PreparedSampleSource`;
- preserve the same logical sample shape as `IndexSampleSource`;
- fail loudly when a request asks for fields or operation fingerprints not
  proven by the manifest.

Non-goals:

- no LitData dependency in core imports;
- no generic `OptimizedStorageBackend` registry unless separately approved;
- no stochastic augmentation or device movement in LitData writing;
- no model tuple formatting in the LitData reader;
- no mutation of a prepared product after creation.

Repository work:

```text
src/rphys/datasources/prepared_litdata.py
tests/unit/rphys/datasources/test_prepared_litdata.py
tests/integration/test_pure_synthetic_litdata_prepared_flow.py
tests/package/test_import_boundaries.py
```

Because LitData APIs can change, implementation planning should verify the
current `litdata.optimize`, `StreamingDataset`, and `StreamingDataLoader`
surface and pin any optional dependency range deliberately.

## Stage 8: Training Access

Training should consume prepared or index-backed samples through existing source
and torch boundaries.

Paths:

- raw/debug path:
  `DataSourceIndex -> IndexSampleSource -> TorchSampleSourceDataset`;
- formatted path:
  `DerivedDataSourceRef -> DataSourceIndex -> IndexSampleSource`;
- prepared path:
  `PreparedDataManifest -> LitDataPreparedSampleReader -> PreparedSampleSource
  -> TorchSampleSourceDataset`.

Expected behavior:

- `BatchCollater` preserves FieldLocator keys;
- data loading returns `Sample` or `Batch`, not model-specific positional
  tuples;
- learners/method adapters decide which fields are inputs and targets;
- train/validate/test/predict loop modes remain distinct from datasource split
  metadata;
- loader/profile evidence records whether data came from raw index, formatted
  datasource, cache, or LitData prepared source.

Repository work:

```text
tests/integration/test_pure_synthetic_training_source_flow.py
tests/contracts/test_prepared_sample_reader_contract.py
tests/contracts/test_torch_adapter_contract.py
```

Real model training over PURE should remain outside default tests. A later
acceptance or downstream experiment can use the prepared source.

## Stage 9: Documentation And Validation

Documentation should cover the scientific and operational assumptions needed to
interpret results:

- PURE citation and access instructions;
- raw layout expectations and local audit command;
- field mapping, schemas, units, shapes, dtypes, and sampling rates;
- subject/task metadata and split policy;
- filter definitions and rejection reasons;
- windowing, resampling, and alignment behavior;
- formatted datasource layout and manifest semantics;
- LitData prepared product invalidation and equivalence rules;
- acceptance-test setup with `RPHYS_PURE_ROOT`;
- limitations: small subject count, controlled lighting, limited demographics,
  motion-condition bias, no official universal split.

Minimum validation for implementation PRs:

```bash
make test-package
make test-unit
make test-contract
make test-integration
uv lock --check
git diff --check
```

Real PURE acceptance validation should be explicit and opt-in:

```bash
RPHYS_PURE_ROOT=/path/to/PURE make test-acceptance
```

Broaden to `make test`, `make test-summary`, and `make validate-pr` when the
roadmap phase touches public imports, prepared manifests, optional dependency
configuration, or shared datasource behavior.

## Open Decisions Before Implementation

- Should real public datasource adapters live in base `rphys`, or should PURE
  begin downstream and only promote reusable contracts back into `rphys`?
- What is the accepted optional dependency policy for image decoding, NumPy
  arrays, and LitData?
- Should the first formatted output preserve raw frame sequences, encode video,
  store arrays, or defer the physical layout to prepared-data materialization?
- Which deterministic preprocessing belongs in the base roadmap item:
  decode-only, crop/resize, face-mask creation, normalization, BVP resampling,
  or fixed rPPG features?
- What canonical subject-disjoint split, if any, should be documented for PURE?
- Should `prepared_litdata.py` be a generic prerequisite roadmap item before
  PURE, or included as a phase of the PURE item?
- How should local raw archive variations be handled if some copies expose AVI
  files, PNG folders, missing subject-task records, or different JSON keys?

## Recommended Implementation Sequence

1. Create roadmap planning artifact for the PURE item and lock boundaries.
2. Add synthetic PURE-like fixtures and raw audit acceptance scaffold.
3. Implement descriptor-only PURE raw scan.
4. Add PURE validation and field mapping.
5. Add optional raw field codecs and sample-builder integration.
6. Add filters, explicit subject-disjoint split examples, and index/window
   construction.
7. Add rphys-native formatted datasource materialization through export/derived
   contracts.
8. Add generic import-gated LitData prepared reader/writer if approved.
9. Add PURE prepared manifest generation and LitData optimized product flow.
10. Add docs, acceptance instructions, and validation evidence.

## References

- TU Ilmenau, "Pulse Rate Detection Dataset - PURE":
  https://www.tu-ilmenau.de/en/university/departments/department-of-computer-science-and-automation/profile/institutes-and-groups/institute-of-computer-and-systems-engineering/group-for-neuroinformatics-and-cognitive-robotics/data-sets-code/pulse-rate-detection-dataset-pure
- rPPG-Toolbox PURE loader raw-layout and JSON parsing evidence:
  https://github.com/ubicomplab/rPPG-Toolbox/blob/main/dataset/data_loader/PURELoader.py
- Lightning-AI LitData repository and current optimized streaming examples:
  https://github.com/Lightning-AI/litdata
