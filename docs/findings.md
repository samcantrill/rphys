# Findings: rphys Stages 0-4 Compared With WoundView

Date: 2026-05-14
Reference implementation: `/home/samcantrill/work/mrffcoviu-woundview-sam`

## Purpose

This document reviews the code implemented in roadmap stages 0 through 4
against the design and implementation patterns in the WoundView project. The
comparison focuses on modularity, robustness, extensibility, public interface
design, base structure, adapters, provenance, and scientific-contract pressure.

The main conclusion is that `rphys` should not copy WoundView's concrete
architecture directly. WoundView is a useful downstream research project with
pragmatic data adapters, pipelines, dynamic config, and domain models, but it
also couples payloads, IO, device movement, HDF5 persistence, mutable metadata,
PyTorch/Lightning data loading, caching, transforms, and project workflows in
ways that would weaken `rphys` as a reusable base library. The transferable
value is the set of real domain contracts WoundView exposes: dataset-specific
adapters, field availability, valid native indexes, timestamps, sampling rates,
subject/source/group/split provenance, sidecar resources, and configurable
operation composition.

## Cross-Stage Findings

### What WoundView Does Well

- It uses a practical adapter stack: path scanners, dataset samples, element
  accessors, data models, loading operations, pipelines, datasets, and data
  modules. See WoundView `src/data/sources/base.py`,
  `src/data/sources/elements/base.py`, `src/data/sources/formatted.py`,
  `src/pipelines/samples/load.py`, and `src/data/datasets/dataset.py`.
- It exposes real domain accessors such as `video`, `blood_volume_pulse`,
  `pulse_rate`, `metadata`, `landmarks`, graph features, and graph adjacency.
  These are useful evidence for future `rphys` datasource adapter examples.
- It keeps enough practical provenance to make experiments possible:
  `path`, `start`, `stop`, dataset name, sample index, sample key, source IDs,
  groups, splits, timestamps, frame/sample rates, and valid frame indexes.
- It supports config-composable workflows through importable `_target_`
  objects. The useful pattern is "extension by importable object", not Hydra
  itself as a core `rphys` dependency.
- It demonstrates why window/probe behavior matters. WoundView can construct
  windows from cheap length and valid-index metadata before loading full
  payloads.

### What rphys Should Avoid Copying

- Do not collapse payload, metadata, HDF5 persistence, tensor movement, slicing,
  and loading into one base object. WoundView's `DataModel` is productive in a
  project, but it is too coupled for `rphys` core.
- Do not rely on raw string paths such as `inputs/node_colours` or
  `source/metadata` as the public contract. `FieldLocator`, `DataKey`,
  `MetadataKey`, `RecordRef`, and `IndexItem` are stronger reusable boundaries.
- Do not introduce implicit collation, stacking, padding, sample-rate defaults,
  or hidden full-load fallbacks. WoundView's convenience behavior is useful
  downstream, but the base library should require explicit policy and preserve
  provenance.
- Do not put project orchestration, generic pipelines, caches, Lightning data
  modules, artifact stores, or Hydra mechanics into `rphys` core.

### Overall Recommendations

- Keep the stage 0-4 public architecture. The current `rphys` direction is more
  modular and robust than WoundView's base structure for a reusable library.
- Add a WoundView-to-rphys contract map before implementing adapters. Map
  `path`, `start`, `stop`, `timestamps`, `fps/sps`, `indexes`, `subject_id`,
  `source_id`, `group`, and `split` onto `rphys` metadata, field specs, field
  views, index items, and builder provenance.
- Treat WoundView-style dataset support as adapters/codecs that emit
  descriptors and provenance. Do not model it as loaded `DataModel`
  dictionaries in core APIs.
- Make temporal alignment, resampling, padding, masking, and sample-rate
  assumptions explicit future contracts before porting WoundView transform
  behavior.
- When real codecs are introduced, require structured codec-owned diagnostics
  and provenance through typed result objects. Do not promote codec-specific
  details such as shape, dtype, units, timing basis, or warnings into core
  contracts until repeated adapters prove stable names are needed.

## Stage 0: Repository Skeleton And Governance

### Stage Scope

Stage 0 established package homes, a broad error hierarchy, lightweight imports,
public API guardrails, private rights metadata, README handoff, and explicit
exclusion of domain behavior. It intentionally did not implement scientific
operations, datasource behavior, runtime containers, codecs, transforms, models,
or workflow/artifact runtimes.

### rphys Design Summary

The Stage 0 foundation is sound:

- `src/rphys/__init__.py` keeps the root package lightweight and empty.
- `src/rphys/errors.py` provides `RemotePhysError(message, **context)` plus
  broad domain error categories with inspectable context.
- Package tests enforce import boundaries, metadata policy, empty root surface,
  and absence of generic workflow/artifact runtime packages.
- The README and roadmap put orchestration and project workflow concerns outside
  `rphys`.

This is a strong base-library posture. It prevents accidental public API growth
and keeps optional heavy stacks out of core imports.

### WoundView Comparison

WoundView demonstrates the downstream contracts `rphys` will eventually need to
serve: data models with payload plus attributes, timing properties for video and
timeseries payloads, dataset samples with `start`/`stop` windows, metadata-driven
grouping/splitting, valid-index-aware windowing, and config-composable runs.

The key contrast is coupling. WoundView imports heavy stacks in base data-model
modules and mixes tensor movement, HDF5 persistence, payload state, metadata,
and slicing in `DataModel`. That is useful in a research project but too broad
for `rphys` core.

### Transferable Benefits

- Use WoundView as evidence for the domain metadata and provenance that adapters
  must preserve.
- Preserve the "importable object" extension style from WoundView's configs,
  while keeping config mechanics downstream.
- Keep dataset-specific path parsing and heavy IO behind future descriptors,
  codecs, and adapters.

### Recommendations

- Keep Stage 0's public API posture: empty root, code-backed exports only, and
  no workflow/runtime imports.
- Add an explicit WoundView-to-rphys contract map before implementing adapters.
- Preserve subject/split/group/source provenance as immutable descriptors or
  builder provenance rather than mutating sample objects in-place.
- Keep temporal alignment out of descriptors until a real alignment/resampling
  contract exists.

## Stage 1: Naming, Locators, Schemas, Metadata, And Errors

### Stage Scope

Stage 1 implemented the canonical vocabulary layer: `DataKey`, `FieldRole`,
`FieldLocator`, `SchemaName`, `DataType`, `MetadataKey`, `SplitName`, and typed
diagnostics. Runtime containers, IO, datasets, transforms, registries, config
integration, and payload validation are explicitly out of scope.

### rphys Design Summary

The implementation is modular and defensible:

- `DataKey` is intrinsic field identity only. It is not a path, locator, codec
  key, config route, or runtime lookup.
- `FieldLocator` preserves role, intrinsic data key, and optional metadata
  selector as separate components.
- `SchemaName` and `DataType` remain distinct: schema identity versus broad
  data category.
- `MetadataKey` and `SplitName` are descriptive labels, not storage, trainer,
  grouping, leakage, or split-building policy.
- Typed validator errors preserve context instead of using generic
  `ValueError`/`assert` style.

This is stronger than WoundView's ad hoc string conventions because it makes the
public vocabulary parseable, testable, and stable.

### WoundView Comparison

WoundView uses practical but fragile string conventions such as
`inputs/node_colours`, `targets/blood_volume_pulse`, `source/metadata`, and
metric/attribute suffixes such as `.sps`. Those conventions are productive in
configs and metrics but are parsed indirectly and can mix roles, field identity,
attributes, and runtime routing.

WoundView also exposes useful semantic names through dataset-specific adapter
methods such as `video`, `blood_volume_pulse`, `pulse_rate`, `metadata`, and
`landmarks`. These are good sources for future `DataKey` examples and adapter
mapping tables.

### Transferable Benefits

- Add adapter examples that map WoundView names onto canonical locators, for
  example `targets/blood_volume_pulse` to `targets/signal.bvp.reference`.
- Map attribute suffixes such as `.sps` to metadata keys or structured field
  metadata, not locator string hacks.
- Promote useful provenance names from WoundView into documented metadata/schema
  conventions: source path, start/stop, dataset/sample identifiers, group,
  split, subject ID, device name, timestamps, sampling rate, and notes.

### Recommendations

- Keep Stage 1 unchanged as the canonical vocabulary boundary.
- Do not loosen grammar to accept WoundView's project strings directly.
  Translate them through adapters.
- Avoid silent assumptions such as defaulting to `30.0 Hz` unless the value is
  explicitly recorded as assumed or provisional.

## Stage 2: Loaded Runtime Core

### Stage Scope

Stage 2 implemented the loaded runtime core: `FieldSpec`, `FieldValue`,
`DataObjectBase`, `CompositeDataObjectBase`, `Sample`, `Batch`,
`FieldRequirement`, `SampleContract`, `CollatePolicy.LIST`, `CollateContext`,
and `collate_samples`. IO, payload loading, codecs, datasource scanning,
transforms, persistence, stack/pad collation, models, and optional backend
imports are out of scope.

### rphys Design Summary

The loaded runtime shape is intentionally narrow:

- `FieldSpec` is a minimal immutable value descriptor for key, data type, and
  optional schema. It does not carry shape, dtype, units, sample rate, axes,
  coordinate frames, or runtime payload type.
- `FieldValue` wraps one loaded payload with schema, metadata, and collation
  policy while avoiding payload value equality.
- `DataObjectBase` and `CompositeDataObjectBase` provide backend-free declared
  tensor traversal and explicit child traversal.
- `Sample` and `Batch` are distinct public classes over shared private storage.
  They expose wrapper access via `field()` and payload access via `get()` and
  `require()`.
- `SampleContract` checks only field presence, payload type, and schema.
- LIST collation is explicit and fail-loud: identical field sets, matching
  schemas, explicit `LIST` policy, and no implicit stack/pad/truncate.

This structure is more robust than WoundView's implicit collation and broad
data model base.

### WoundView Comparison

WoundView's `DataModel(data, attrs)` is convenient and expressive. Concrete
models expose domain affordances such as video length/height/width/channels/FPS
and timeseries SPS derived from timestamps or metadata. WoundView also has a
custom `Batch` that reshapes slash-separated keys into nested dictionaries and
stacks tensors where possible.

The benefits are ergonomics and immediate downstream usability. The risks are
hidden assumptions: tensor stacking is implicit, attributes are mutable and
loosely typed, device movement is mixed into data objects, and HDF5 persistence
is part of the base model.

### Transferable Benefits

- Future specialized data objects should expose video/signal/landmark domain
  affordances such as FPS/SPS, dimensions, coordinate frames, timestamp basis,
  and validity masks.
- Future collation policies can learn from WoundView's batching needs, but they
  must be explicit and provenance-aware.
- A migration adapter can map `DataModel(data, attrs)` into `FieldValue` plus
  `FieldLocator` and `MetadataKey` values.

### Recommendations

- Keep Stage 2 public interfaces stable.
- When adding `STACK` or `PAD`, require explicit field policies and carry
  lengths, masks, sample rates, padding values, and provenance.
- Prefer operation APIs over raw dict pipelines: accept `FieldContainer`,
  `SampleContract`, and `FieldLocator` rather than nested string-keyed dicts.
- Keep heavy tensor/array/video dependencies out of core imports.

## Stage 3: Lazy References And Index Items

### Stage Scope

Stage 3 implemented dependency-free lazy descriptors:
`ResourceRef`, `FieldRef`, `FieldIndex`, `TemporalIndexSlice`, `FieldView`,
`DataSourceRef`, `RecordRef`, `DataSourceSchema`, and `IndexItem`. Payload
loading, codecs, sample builders, datasource adapters, manifests, transforms,
training, fingerprints, stable item IDs, seconds/spatial slices, and
multi-member items are out of scope.

### rphys Design Summary

The Stage 3 implementation matches the descriptor-only contract:

- `ResourceRef` stores uninterpreted URI, protocol, and primitive storage
  options without parsing, opening, probing, or canonicalizing.
- `FieldRef` names a logical field with ordered resources, optional schema, and
  metadata. Resource ordering is descriptor data, not priority or binding policy.
- `TemporalIndexSlice` stores half-open field-native integer index bounds. Equal
  numeric slices on different fields do not imply alignment.
- `FieldView` adds an optional field-native index to a `FieldRef` without
  loading or role semantics.
- `DataSourceRef`, `RecordRef`, and `DataSourceSchema` preserve datasource
  identity, record identity, declared field membership, and metadata without
  scanning or validation reports.
- `IndexItem` maps role-qualified `FieldLocator` values to `FieldView`
  descriptors while requiring record provenance and key consistency.

This is the right abstraction layer for a reusable base library.

### WoundView Comparison

WoundView's adapter stack provides practical evidence for what Stage 3
descriptors must support later. `DatasetSample` carries a path and `start`/`stop`
window. Dataset-specific sample classes expose semantic element methods.
Elements separate data and attributes, then materialize models. Window
construction uses cheap length plus valid indexes to avoid invalid contiguous
regions. Formatted samples often combine primary resources and sidecars, such as
video frames plus HDF5 metadata.

WoundView does this in executable project code rather than pure descriptors. In
`rphys`, the correct transfer is to use WoundView-style accessors to emit
`RecordRef`, `FieldRef`, `FieldView`, and `IndexItem` values.

### Transferable Benefits

- Future datasource adapters should report field extent, valid native indexes,
  timestamps/sample-rate evidence, missing-field diagnostics, sidecar resources,
  and subject/source/group/split provenance.
- Future manifest/index envelopes can wrap Stage 3 `to_dict()` payloads instead
  of adding schema versions, fingerprints, or stable item IDs to the descriptors.
- Primary-plus-sidecar resource binding should be designed in codecs/adapters,
  not retrofitted into `FieldRef.resources` semantics.

### Recommendations

- Keep Stage 3 descriptors unchanged.
- In Stage 5 datasource/index planning, add explicit adapter outputs for field
  extent, valid native indexes, timestamps/sample-rate evidence, and missing
  fields.
- Treat subject/split/group/source as normalized metadata/provenance concerns,
  not new Stage 3 constructor fields.
- Add later codec/resource-binding design for primary resources plus sidecars.

## Stage 4: Codecs And Lazy Sample Construction

### Stage Scope

Stage 4 bridged Stage 3 descriptors to Stage 2 runtime samples. It added
codec contracts, explicit local `CodecRegistry` instances, probe/load/save
contexts, metadata save policy, lazy `SampleField` handles, `SampleBuilder`,
and builder-side provenance. Datasource scanning, manifests, caches, transforms,
export orchestration, real codec catalogs, model formatting, and training
loaders are out of scope.

### rphys Design Summary

The Stage 4 design is modular and conservative:

- `rphys.io.codecs` owns structural codec contracts, `CodecCapabilities`,
  datasource-neutral `LoadContext` and `SaveContext`, operation result records,
  `MetadataSavePolicy`, and explicit ordered `CodecRegistry`.
- The registry is local and deterministic. It does not discover codecs, use
  process-global state, or import optional dependencies.
- `SampleField` is `FieldValue`-compatible and stored directly as a field
  object. It loads only on payload/eager access and retains loaded or failed
  state for inspection.
- `SampleBuilder` consumes exactly one `IndexItem`, builds all/subset/one lazy
  fields, probes without payload loading, and keeps record/item provenance
  outside codec contexts.
- Public imports remain focused on owning submodules rather than root or broad
  package-level convenience exports.

This is a good separation between descriptors, codec operation, lazy runtime
state, and datasource provenance.

### WoundView Comparison

WoundView's useful pattern is adapter layering. Dataset-specific methods hide
file layout; `DataElement` separates `data`, `attributes`, and `model`; dynamic
loaders map output keys to element names and constructor kwargs; configured
pipelines compose named importable operations; and window construction uses
cheap length/valid-index metadata before loading payloads.

The risks to avoid are also visible: mutable string-key attrs, heavy imports,
cache/split/process behavior inside dataset loading, broad pipeline side
effects, and implicit sample-rate or tensor assumptions.

### Transferable Benefits

- Real codecs should expose structured codec-owned probe/load evidence before
  broad adapters land, but those details should remain result metadata rather
  than core field contracts until repeated adapters prove the need.
- Future WoundView-style adapters should emit descriptors and provenance, not
  loaded dictionaries.
- Future tests should prove "window/probe without payload load" and valid-index
  slicing behavior.

### Recommendations

- Keep the Stage 4 public surface focused: explicit registries, no global codec
  discovery, no real codec catalog in core.
- Lazy `SampleField` behavior for `Sample.map_tensors_()` is now clarified:
  the method is payload-demanding and may materialize a lazy field, but it must
  preserve the stored `SampleField` handle, retained result metadata, and
  builder provenance instead of replacing the field with a plain `FieldValue`.
- `SampleField.load()` was hardened after this review to catch `Exception`
  rather than `BaseException`, so termination-style `BaseException` subclasses
  propagate without being retained as lazy-load failures.
- Defer real-codec metadata conventions. Require structured result diagnostics
  through existing codec result objects first, then promote only proven repeated
  fields into public contracts later.
- Clean up a stale documentation footer:
  `docs/roadmap/stage-4/implementation-plan.md` says implementation is complete
  at the top, but its `Final Approval` section still says approval is pending
  and not yet approved.

## Prioritized Action Items

1. Keep Stages 0-4 architecture intact. No WoundView-derived redesign is
   warranted for the existing public contracts.
2. Create a WoundView migration/adapter mapping document before implementing
   WoundView adapters.
3. In upcoming datasource/index planning, include field extent, valid indexes,
   timestamps, sample-rate evidence, sidecar resources, and missing-field
   diagnostics as first-class adapter outputs.
4. Keep real-codec probe/load diagnostics structured but codec-owned before
   adding real codec catalogs.
5. Keep lazy `SampleField` tensor mapping handle-preserving as later
   tensor/device integrations expand.
6. Make temporal alignment/resampling an explicit future contract before
   porting WoundView window and transform semantics.
7. Fix the stale Stage 4 implementation-plan approval footer.

## Review Inputs

This document synthesizes five stage-specific read-only subagent reviews plus a
direct local code review of the `rphys` and WoundView repositories. No
WoundView files were edited.
