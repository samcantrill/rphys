# Field Runtime Core

This document describes the code-backed Phase 1 runtime contracts in
`rphys.data`. The runtime core owns loaded in-memory field identity and loaded
field values. Lazy field references, codecs, dataset indexes, transforms,
training loops, evaluation, concrete modality objects, `Sample`, `Batch`,
`SampleContract`, `CollateContext`, and `collate_samples` are intentionally
deferred to later accepted plans.

## Runtime And IO Boundary

`rphys.data` describes data that is already in memory. Phase 1 provides:

- Stable: `DataKey`
- Stable: namespace constants such as `VIDEO_NAMESPACE`, `SIGNAL_NAMESPACE`,
  `CUSTOM_NAMESPACE`, and `STANDARD_NAMESPACES`
- Stable: `FieldSpec`
- Stable: `FieldValue`
- Stable for the exposed member: `CollatePolicy.LIST`

`FieldRef`, `TemporalIndexSlice`, and `FieldView` remain future `rphys.io`
contracts because they describe lazy requests for external payloads. They are
not exported from `rphys.data` in Phase 1.

## DataKey

`DataKey` is a validated `str` subclass for logical field identity. Keys are
lowercase ASCII dot-separated tokens.

Standard keys use a reserved namespace and at least one semantic token:

```python
DataKey("video.rgb")
DataKey("signal.bvp.reference")
DataKey("prediction.quality.signal_snr")
```

Project-local fields use `custom.<project>.<field...>`:

```python
DataKey("custom.my_project.some_field")
```

Equality and hashing follow `str`. The stable serialization token is the key
string. Copying may return the same immutable object or an equal object; callers
must not rely on `DataKey` object identity.

## FieldSpec

`FieldSpec` is intentionally minimal:

- `key`: a `DataKey`
- `data_type`: a lowercase ASCII dot-separated data category
- `schema`: an optional schema identifier

The base spec does not include `description`, `runtime_type`, coordinate frames,
temporal axes, units, layouts, shapes, sample rates, or field-specific
integration metadata. Those details should be added by future specialized
specs, data objects, sample contracts, dataset contracts, or transform docs when
concrete code actually needs them.

`FieldSpec` uses value equality across `key`, `data_type`, and `schema`. It is
not hashable by public contract. Copying and deep copying are value-preserving
over those primitive fields. No dict, JSON, or registry serialization round trip
is public in Phase 1.

## FieldValue

`FieldValue` wraps a loaded payload with narrow field-level metadata:

- `value`: arbitrary loaded runtime payload
- `schema`: optional schema identifier
- `metadata`: shallow-copied mapping with string keys
- `collate_policy`: optional explicit `CollatePolicy`

`FieldValue` does not store `data_type`; broad field identity belongs to the
field key/spec. Metadata describes the field value, not the whole sample. Shape,
dtype, units, coordinate-frame, temporal-axis, and sample-rate validation are
deferred until specialized contracts need them.

Equality is object identity so tensor-like payload equality is never invoked
accidentally. `FieldValue` is not hashable. Shallow copying shares the payload
and nested metadata values while copying the metadata mapping. Deep copying uses
normal Python deep-copy behavior and may fail for non-copyable payloads with the
payload's underlying error. No payload serialization contract exists in Phase 1.

## CollatePolicy

Phase 1 exposes only `CollatePolicy.LIST`.

`LIST` means a later collation step may preserve per-sample payloads as a
Python list. It does not imply stacking, padding, truncation, missing-field
handling, metadata promotion, or backend-specific tensor behavior. There is no
default collation policy: absent policy must fail when executable collation lands
in a later phase.

## Failure Behavior

`rphys.data` raises `RemotePhysDataError` for invalid keys, unknown non-custom
namespaces, invalid data type tokens, non-string, blank, or padded schema
values, invalid metadata, and unsupported collation-policy values. Phase 1
stores schema identifiers as caller-provided strings after those narrow checks;
it does not enforce a global schema-token grammar or registry.

Phase 1 imports stay lightweight and must not import torch, numpy, pandas,
OpenCV, scipy, sklearn, tensorflow, plotting libraries, dataset SDKs, future
`rphys.io` modules, future dataset modules, or transform modules.
