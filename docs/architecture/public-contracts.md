# rphys Public Architecture Contracts

This document defines the first public architecture contract for `rphys`.
It is intentionally narrower than the long-range architecture plan: it names
the stable package homes, policy obligations, and validation expectations that
may be relied on while concrete scientific behavior is still deferred.

`rphys` is a domain package for remote physiological measurement research.
It owns domain semantics for fields, datasets, transforms, methods, training,
evaluation, and analysis when those components are implemented. It does not own
generic experiment infrastructure.

## API Stability Labels

Every public component should be documented with one of these labels before
downstream code relies on it.

- Stable: compatibility is expected across normal minor releases. Breaking
  changes require explicit migration notes and tests.
- Provisional: the component is public enough for experimentation, but names,
  signatures, and semantics may change before promotion to stable.
- Private or internal: implementation detail. Names beginning with `_` are
  private unless a contract document states otherwise.

Undocumented imports are not stable by default. A public import becomes a
contract only when the code, docs, and tests agree on its behavior.

## First Stable Module Wave

The first stable import homes are:

- `rphys`: lightweight package marker.
- `rphys.errors`: broad package error bases.
- `rphys.data`: future home for in-memory field-centric sample and batch data.
- `rphys.io`: future home for external field access, lazy field references, and
  codecs.
- `rphys.datasets`: future home for dataset discovery, filtering, indexing, and
  sample-building semantics.
- `rphys.transforms`: future home for sample transforms, augmentations, checks,
  export, and materialization contracts.

These modules may exist before their concrete behavior exists. Placeholder
domain classes, empty registries, or broad re-exports should not be added only
to reserve names.

## Deferred And Provisional Areas

The following areas are intentionally deferred until their own implementation
plans define code-backed contracts:

- `rphys.methods`
- `rphys.models`
- `rphys.training`
- `rphys.losses`
- `rphys.evaluation`
- `rphys.analysis`
- `rphys.recipes`
- `rphys.stages`
- `rphys.ops`
- `rphys.testing`

Downstream projects should not treat these module paths as available until they
are created by a later accepted plan.

`FieldRef`, `TemporalIndexSlice`, and `FieldView` are future `rphys.io`
concepts. They are IO contracts because they describe lazy requests for
external field payloads, optional temporal slicing, and load-time views. They
are not part of the first implementation wave.

## Error Contract

Public errors use readable `RemotePhys*Error` names:

- `RemotePhysError`
- `RemotePhysDataError`
- `RemotePhysIOError`
- `RemotePhysDatasetError`
- `RemotePhysTransformError`
- `RemotePhysTrainingError`
- `RemotePhysEvaluationError`

Detailed future errors should inherit from the closest broad base. Domain code
should raise these errors when a failure belongs to the `rphys` contract rather
than to a lower-level dependency.

## Code-Backed Documentation

Public API documentation should be backed by importable code and tests. Handwritten
architecture docs may explain policy, ownership, terminology, and scientific
contracts, but they should not publish signatures or behavior that are absent
from code.

When a future API reference exists, public docs should link to it rather than
copying function signatures manually. If docs and code disagree, the mismatch is
a validation bug.

## Scientific Contract Obligations

Scientific components must document the contract that makes their outputs
interpretable and reproducible. For each public dataset, preprocessing step,
signal-processing operation, model, loss, metric, evaluation routine, or
analysis component, docs and tests should cover the relevant items below.

- Inputs and outputs, including shapes, units, dtypes, and device expectations.
- Coordinate frames, channel order, field keys, and modality conventions.
- Sampling rates, timestamp conventions, temporal alignment, windowing,
  resampling, filtering, masking, interpolation, and padding behavior.
- Normalization order and whether statistics are per-sample, per-subject,
  per-record, per-video, per-dataset, or global.
- Leakage risks, train/test boundary assumptions, subject identity handling,
  split behavior, and label availability.
- Failure behavior for NaNs, flat signals, short inputs, missing frames, empty
  masks, invalid sampling rates, dtype mismatches, device mismatches, and
  unsupported temporal slices.
- Validation tests, including synthetic fixtures or tiny license-safe fixtures
  where data examples are needed.

Raw datasets must not be committed to this repository.

## loom Boundary

The dependency direction is one-way: `rphys` may depend on `loom`; `loom` must
not depend on `rphys`.

`loom` owns generic reproducible experiment infrastructure, including config
composition, `_target_` instantiation mechanics, artifact stores, execution
engines, generic stage execution, run state, resume logic, sweeps, and generic
resource or manifest mechanics when provided there.

`rphys` owns remote-physiology domain semantics layered on top of those generic
mechanisms. A stage class may eventually live in `rphys` if it expresses a
domain operation, but stage execution remains a `loom` concern.

## Extension Policy

The default extension mechanism is an importable Python object referenced by a
`_target_` path in config. Users should be able to define project-local
datasets, transforms, methods, losses, metrics, exporters, or analysis objects
without editing `rphys` internals.

Registries should be limited to cases where a compact symbolic name is the
scientific contract, such as a codec name, modality-specific backend name, or
well-defined recipe catalog entry. Registries should not become the required
path for ordinary user extension.

## Dependency Policy

Base imports must stay lightweight. Importing `rphys` or the first-wave modules
must not import heavy optional stacks such as video backends, array analysis
libraries, plotting stacks, deep learning frameworks, or dataset-specific SDKs.

Optional dependencies should be grouped by capability, such as video IO, signal
processing, torch-based learning, analysis, plotting, documentation, and local
development. Concrete extras remain deferred until code needs them.

## Repository Tooling Policy

The repository uses `uv` for package, lockfile, and local development workflow.
The Python baseline is Python 3.12 with `requires-python = ">=3.12"` in package
metadata and `3.12` in `.python-version`.

`uv.lock` is committed. Makefile targets are thin wrappers around `uv` and git
checks; they do not define a separate build system.

## Rights Status

No public-use license has been selected. Until that changes, this repository is
all rights reserved and grants no permission to copy, modify, distribute, or
reuse the code beyond rights that already exist by law or separate written
agreement.

Package metadata must not advertise a public open-source license while this
placeholder is in effect. The rights status must be replaced before publication,
distribution, or external reuse.
