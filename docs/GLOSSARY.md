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
| `Operation` | Generic context-aware callable contract. | Do not use it as a synonym for every semantic role in the library. |
| `SampleOp` | A `Sample -> Sample` operation over runtime fields. | Distinct from datasource discovery, lazy indexing, and training orchestration. |
| `Transform` | An `Operation` whose main purpose is transformed output. | Not every operation is best described as a transform. |
| `Method` | A batch-level prediction or representation algorithm. | Distinct from `Model`, `Loss`, `Objective`, and `Metric`. |
| `Model` | A lower-level computational object, often a tensor or neural module. | Do not use `Model` when the contract really includes prediction semantics, adapters, or batch-level behavior; that is usually a `Method`. |
| `Loss` | A differentiable error or penalty term. | Distinct from `Metric`, which reports rather than optimizes. |
| `Objective` | The optimizer-facing aggregation that produces the scalar used for backward. | Do not collapse `Loss` and `Objective` into one term when aggregation semantics matter. |
| `Metric` | A detached measurement and reporting contract. | Not a differentiable optimization target by default. |
| `Learner` | The object that owns mode-specific step semantics and composes `Method` plus optional `Objective` and `Metric` behavior. | Distinct from `Trainer`, which owns iteration and execution mechanics. |
| `Trainer` | The object that owns iteration, device movement, grad or no-grad mode, backward, and related execution mechanics. | Do not put datasource logic, scientific metrics, or prediction export policy inside the `Trainer`. |
| `Analysis` | Evaluation, summarization, interpretation, or reporting work over predictions, metrics, and provenance-aware outputs. | Distinct from training, checkpoint selection, or datasource crawling. |
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
| `RecordRef` | The lazy reference object for a stable logical record before windowing, including record identity, field presence, and leakage-sensitive metadata. | Not a loaded runtime sample. |
| `Sample` | The per-item runtime container after payloads are loaded or wrapped. | Not a fixed `(inputs, targets)` tuple and not necessarily the same thing as a record. |
| `Batch` | The collated runtime container. It exposes the same field access shape as `Sample`. | Do not treat it as merely a list of samples or as a subtype that erases the sample-vs-batch distinction in documentation. |
| `ResourceRef` | A reference to physical storage through URI, protocol, and storage options. | Not an artifact-store handle or workflow lifecycle object. |
| `FieldRef` | A serializable lazy reference to one complete logical field. | It does not contain runtime role, `FieldLocator`, temporal slice, loaded tensors, or open handles. |
| `FieldView` | A `FieldRef` plus optional imposed access behavior such as a `FieldIndex`. | Distinct from a loaded field payload. |
| `IndexItem` | A mapping from role-qualified `FieldLocator`s to `FieldView`s. This is the unit consumed by `SampleBuilder`. | It must remain pure lazy IO and must not contain transforms, augmentations, method logic, export logic, or training logic. |
| `Codec` | The boundary object that probes, loads, and saves logical fields and field views. | A codec does not choose splits, parse trainer concerns, or own transform logic. |
| `SampleBuilder` | The bridge from `IndexItem` field views to runtime `Sample` objects, including lazy sample-field loading behavior. | It should not scan datasources, choose splits, apply ops, or move devices implicitly. |

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
