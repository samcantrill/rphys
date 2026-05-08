# Master Plan: Field Runtime Core

Status: accepted
Roadmap item: `docs/roadmap/index.md`
Roadmap slug: `field-runtime-core`
Plan number: `02`
Planning notes: `docs/implementation/02-field-runtime-core/planning-notes.md`
Implementation plan: `docs/implementation/02-field-runtime-core/implementation-plan.md`
Quality gate: passed on 2026-05-08
Stage 3 status: Phase 1 committed; pre-submit blocker gate pending
Blockers:

- None. Phase 1 implementation, validation, and standard-path review follow-ups are complete; pre-submit gate remains.

## Summary

This work package turns `rphys.data` from an empty first-wave module home into the stable in-memory runtime contract for field-centric remote physiological measurement workflows.

The package owns loaded runtime data only: logical field keys, field declarations, loaded field values, typed data object hooks, mutable `Sample` containers, `Batch` containers with the same field access API, sample contracts, and explicit field-level collation. It does not own lazy IO references, dataset indexes, codecs, transforms, training, evaluation, or full modality implementations.

The implementation should keep the base package dependency-free. Tensor, array, and device behavior is expressed through duck-typed hooks and synthetic test doubles until an accepted downstream package adds optional backend extras.

## Context Readout

- `rphys.data` currently exists but exports no public domain objects.
- Existing tests enforce that first-wave modules do not expose placeholder APIs; this package must update those checks so `rphys.data` exports real runtime contracts while `rphys.io`, `rphys.datasets`, and `rphys.transforms` remain thin until their own packages land.
- `docs/architecture/public-contracts.md` assigns `FieldRef`, `TemporalIndexSlice`, and `FieldView` to future `rphys.io`; this plan preserves that boundary.
- `docs/rphys_architecture_plan_v3.md` sections 8-15 provide the evidence for `DataKey`, `FieldSpec`, `FieldValue`, `DataObjectBase`, `Sample`, `Batch`, and `CollatePolicy`.
- Runtime API churn here would affect every later dataset, transform, learning, and evaluation package, so the first implementation should be narrow, heavily tested, and explicit about unsupported behavior.

## Behavior Model

- User-visible behavior:
  - Users can import `DataKey`, `FieldSpec`, `FieldValue`, `DataObjectBase`, `Sample`, `Batch`, `CollatePolicy`, `CollateContext`, `collate_samples`, and `SampleContract` from `rphys.data`.
  - Users can create arbitrary fields without editing `rphys` internals, using standard namespaces or `custom.<project>.<field...>` keys.
  - Users can mutate `Sample` objects intentionally with `set_field`, `delete_field`, and `rename_field`.
  - Users can copy Samples explicitly; shallow copy is available when payload sharing is intentional, and deep copy is the expected branching default.
  - Users can access payloads through the same `has`, `field`, `get`, and `require` API on `Sample` and `Batch`.
  - Users may rely on explicit public equality, hashability, copy, and serialization boundaries documented for each new runtime contract; accidental dataclass defaults are not part of the public API.
  - Users get `RemotePhysDataError` diagnostics for invalid keys, missing fields, wrong payload types, schema mismatches, absent collation policies, unsupported collation, and ambiguous missing-field behavior.
- Agent-visible behavior:
  - Later packages treat this plan and the implemented code as the runtime contract source.
  - Later dataset and IO work must not move loaded runtime behavior into `rphys.io` or `rphys.datasets`.
  - Later transform, method, loss, metric, and evaluation work must consume fields by `DataKey`.
- Supported workflows:
  - Construct synthetic samples and batches in tests.
  - Wrap arbitrary payloads in `FieldValue`.
  - Validate required and optional sample fields with `SampleContract`.
  - Collate samples only when each field has explicit `LIST` collation policy.
  - Move or detach tensor-like payloads through backend-agnostic duck-typed hooks.
  - Branch a runtime pipeline only after explicitly deep-copying the Sample to avoid shared mutable field payloads.
- Unsupported workflows:
  - Lazy loading, file references, codecs, dataset scanning, temporal slicing, transforms, model prediction, losses, metrics, and stage execution.
  - Concrete torch/numpy/pandas/OpenCV behavior in base imports.
  - Silent padding, truncation, dropping fields, type coercion, metadata promotion to tensors, or implicit best-effort collation.
  - A full modality class library such as `VideoData` or `SignalData`; those names are reserved for later code-backed contracts unless accepted during this plan.
- Failure and stop behavior:
  - Fail loudly for invalid `DataKey` syntax, unknown non-custom namespaces, wrong sample payload type, missing required fields, field schema mismatches, empty sample sequences, inconsistent field sets, absent collation policies, unsupported collation policies, and unsupported padding/stack behavior.
  - Data object device operations use returned objects as authoritative. Callers must not assume in-place mutation; unsupported declared tensor hooks fail with `RemotePhysDataError` rather than silently dropping a requested operation.
  - Stop Stage 3 if implementation requires heavy dependencies, IO concepts, transform behavior, concrete modality depth, changed public architecture boundaries, or changes outside this package.
- Resume behavior after interruption or context loss:
  - Reload this plan, the planning notes, `docs/roadmap/index.md`, `docs/architecture/public-contracts.md`, and architecture sections 8-15.
  - Continue from the current phase status in `implementation-plan.md` once Stage 3 begins.
- Stage 3 operating model:
  - One live implementation plan, sequential phases, automatic/admin merge after automated gates, no human-review merge gate.

## Goals

- Implement code-backed, documented runtime contracts in `rphys.data`.
- Keep base imports lightweight and dependency-free.
- Define `DataKey` validation, namespace policy, and custom field extension behavior.
- Define `FieldSpec` and `FieldValue` metadata semantics without mixing them with lazy IO references.
- Define `DataObjectBase` tensor traversal and device-operation hooks without importing torch.
- Define mutable `Sample` behavior, explicit shallow/deep copy behavior, and stable field access diagnostics.
- Define `Batch` as Sample-like and preserve the same access API.
- Define strict, explicit collation rules with deterministic metadata collation.
- Add layered tests for normal behavior, edge cases, failure behavior, and dependency boundaries.

## Non-Goals

- `FieldRef`, `TemporalIndexSlice`, `FieldView`, codecs, `DatasetRef`, `RecordRef`, indexes, sample builders, or lazy loading.
- Runtime transforms, augmentations, checks, exporters, or materialization pipelines.
- Methods, models, learners, trainers, losses, metrics, predictions, evaluation, analysis, recipes, or stages.
- Full concrete modality objects such as `VideoData`, `SignalData`, `LandmarkData`, `MaskData`, or `MeshData`.
- Generic `loom` infrastructure.
- Heavy optional dependencies or backend-specific stacking/device semantics in the base package.
- Silent best-effort behavior for missing, ragged, padded, truncated, or unknown fields.

## Intent And Functionality Approval

- Approval status: approved
- Approval date: 2026-05-08
- Current round: complete; design refinement incorporated
- Approval rule: design discussion does not continue until the maintainer explicitly approves the intent/functionality baseline below.

| Packet | Topic | Functionality Baseline | Implementation Consequence | Maintainer Response | Plan Update | Status |
| --- | --- | --- | --- | --- | --- | --- |
| F1 | Runtime-core purpose and included behavior | Implement the loaded in-memory field runtime contract in `rphys.data`: `DataKey`, `FieldSpec`, `FieldValue`, `DataObjectBase`, `Sample`, `Batch`, `SampleContract`, `CollatePolicy`, `CollateContext`, and `collate_samples`. | Stage 3 implements runtime data contracts, not IO, datasets, transforms, training, or evaluation. | Approved on 2026-05-08. | Baseline accepted; design classification may proceed. | accepted |
| F2 | User-visible and agent-visible behavior | Users can create field keys/specs/values, store and mutate arbitrary Sample fields, copy Samples explicitly, access payloads through the same Sample/Batch API, validate required fields, and collate only through explicit field-level policies. Agents treat this package as the runtime contract source for later work. | Later packages build on one field access API and one explicit collation contract. | Approved on 2026-05-08. | Baseline accepted; design classification may proceed. | accepted |
| F3 | Non-goals, failure behavior, and validation goals | Lazy IO, dataset refs/indexes/builders, transforms, concrete modality classes, training/evaluation, and heavy base dependencies stay out of scope. Invalid keys, missing fields, wrong types, schema mismatches, absent collation policies, ambiguous collation, unsupported padding, and backend-specific base behavior fail loudly under `RemotePhysDataError`. | Keeps the package narrow, dependency-light, test-heavy, and safe for downstream public contracts. | Approved on 2026-05-08. | Baseline accepted; design classification may proceed. | accepted |

Approved functionality baseline:

- Implement the loaded in-memory runtime contract in `rphys.data`: keys, specs, loaded values, data object hooks, mutable sample/batch containers, runtime sample contracts, and explicit collation.
- Provide one field access API for `Sample` and `Batch`.
- Preserve dependency-light base imports.
- Make validation and failure behavior explicit enough for downstream dataset IO, transform, training, and evaluation packages to rely on.

Approved non-goals and stop behavior:

- Lazy IO, dataset refs/indexes/builders, transforms, concrete modality classes, training/evaluation, and heavy base dependencies are out of scope.
- Stop Stage 3 if implementation would require changing these scope boundaries or adding unsupported heavy base dependencies.
- Fail loudly under `RemotePhysDataError` for invalid keys, missing fields, wrong types, schema mismatches, absent collation policies, ambiguous collation, unsupported padding, and backend-specific base behavior.

## Design Decision Classification

- Classification status: complete
- Current review round: needs-discussion decisions accepted; recorded recommendations remain documented unless reopened.
- Classification rule: discuss only impactful decisions that lack a strong recommendation, plus any recorded recommendation the maintainer asks to discuss. Record strong recommendations without separate walkthrough.

| Decision | Classification | Why It Matters | Recommendation | User Discussion Needed | Status |
| --- | --- | --- | --- | --- | --- |
| `rphys.data` owns loaded runtime contracts only | recorded recommendation | Preserves the already documented `rphys.io` lazy-reference boundary. | Keep loaded runtime contracts in `rphys.data`; keep `FieldRef`, `TemporalIndexSlice`, `FieldView`, codecs, and builders out. | No, unless maintainer reopens the boundary. | accepted recommendation |
| `DataKey` representation and grammar | accepted | Every later package addresses fields by key. | Use `DataKey(str)`, flexible lowercase dot-separated tokens, reserved namespaces plus `custom.<project>.<field...>`, no aliases, namespace constants only in Phase 1. | Discussed in D1; maintainer answered yes. | accepted |
| `FieldSpec` scientific metadata contract | accepted | This controls how much scientific meaning is enforced in the base runtime versus downstream schemas/transforms. | Use a minimal strict base `FieldSpec` with `key`, `data_type`, and optional `schema`; value equality is public, hashability is not. Useful scientific specificity should come from specialized specs such as future tensor/video/signal specs or modality/data-object contracts, not from stuffing data-specific fields into the base class. | Discussed and accepted as likely best initial approach; equality/hash semantics tightened during quality refinement. | accepted |
| `FieldValue` validation and copy semantics | accepted | This controls payload wrapping, defensive metadata copying, and how transforms preserve field meaning. | Always wrap runtime payloads in `FieldValue`; keep only `value`, optional `schema`, copied `metadata`, and optional `collate_policy`; do not duplicate `data_type`; use identity equality to avoid ambiguous tensor payload equality; leave shape/dtype/unit/coordinate validation to data objects, specialized specs, or contracts. | Discussed and accepted as reasonable for now; equality/hash semantics tightened during quality refinement. | accepted |
| `Sample`/`Batch` API details | accepted | This API will be used by transforms, methods, losses, metrics, and tests. | Use domain-container semantics with mapping-like helpers, not `MutableMapping` inheritance. `get` and `require` return payloads, `field` returns wrappers, mutation is explicit, shallow/deep copy are explicit, and `Batch` subclasses `Sample` initially. | Discussed and accepted. | accepted |
| `DataObjectBase` backend hooks | recorded recommendation | Backend imports can easily leak into base runtime imports. | Keep base duck-typed and dependency-free; validate only when explicitly called by the object/contract path; traverse only subclass-declared tensor-like leaves; return transformed objects instead of promising in-place mutation; raise `RemotePhysDataError` for unsupported declared hook operations; allow optional torch submodule later if import-gated. | No, unless maintainer wants torch-aware design now. Semantics tightened during quality refinement without changing the accepted dependency-free base decision. | accepted recommendation |
| `SampleContract` validation timing | accepted | This affects whether builders/transforms/methods validate wrappers, payloads, metadata, or all three. | Use explicit-call runtime validation only. Validate required/optional fields, payload type, and `FieldValue.schema`; do not validate shapes, axes, units, coordinate frames, sample rates, or `FieldSpec` catalogs in Phase 1. | Discussed and accepted. | accepted |
| Collation policy details | accepted | Batching can silently alter scientific meaning if missing/ragged behavior is wrong. | Initial collation supports only explicit `LIST`; absent policy fails; field sets must match exactly; stack, padding, missing-field, custom, and object-delegated collation are deferred. | Discussed and accepted. | accepted |
| Phase/pathway policy | recorded recommendation | Public contracts need comprehensive review. | Use standard comprehensive pathway for all phases and xhigh for Phase 1 where configurable. | No, already accepted. | accepted recommendation |

Recorded recommendations:

- Runtime ownership boundary, backend-light base imports, optional isolated torch submodule allowance, and standard comprehensive pathway are accepted recommendations unless reopened.

Needs discussion:

- None. Previously queued decisions are accepted.

Deferred or blocking decisions:

- Full modality object library remains deferred.
- Backend-specific stack/padding implementations remain deferred until concrete data objects or optional backend modules exist.

## Design Decisions

| Decision | Status | Alternatives Considered | Rationale | Maintainability/Extensibility Impact | Validation Obligation | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| `rphys.data` owns loaded runtime contracts only | accepted | Put `FieldRef` and views here; split runtime into several packages | The prior public contract assigns lazy IO requests to `rphys.io`; `rphys.data` should stay focused on in-memory samples and batches. | Keeps dataset/IO and runtime mutation independent. | Public contract docs, import tests, and no `FieldRef` exports from `rphys.data`. | Users may expect all field concepts in one module; docs must explain the boundary. |
| `DataKey` is a validated `str` subclass | accepted | Frozen dataclass wrapper; plain strings only | A string subclass remains usable as a mapping key and serializable string while allowing validation and helper properties. | Keeps APIs ergonomic and avoids string/dataclass conversion churn. | Key parsing tests, equality/hash tests with strings, invalid syntax tests. | `str` subclass behavior can surprise static typing; docs should describe accepted key inputs. |
| Standard namespaces are reserved; custom extension keys use `custom.<project>.<field...>` | accepted | Allow any namespace; require registry registration | Reserved namespaces reduce collision risk, and custom keys avoid requiring edits to `rphys` internals. | Future standard fields can be added without breaking project-local extensions. | Tests for standard, custom, invalid, and unknown namespace keys. | Some users may want organization-specific namespaces; custom keys remain the sanctioned path. |
| `FieldSpec` is minimal and strict | accepted | Rich runtime schema with layout/axes/units/temporal axis/coordinate frame; untyped metadata dict; full dataset schema system; premature generic `runtime_type` and `description` fields | `FieldSpec` includes only what is necessary and broadly consistent across field declarations: `key`, `data_type`, and optional `schema`. Data-specific scientific details such as coordinate frames, temporal axes, sample rates, units, and layouts should be expressed by specialized specs or later modality/data-object/dataset/transform contracts when they are actually required. `description` is documentation, not a behavioral contract, and `runtime_type` is only useful when concrete runtime types exist. | Keeps the base runtime contract small, stable, and extensible; avoids freezing integration logic or unused descriptors before data-specific contracts exist. | Tests for required `key` and `data_type`, validation of data type syntax, optional schema behavior, value equality, unhashability, no accidental extra constructor fields, and docs stating which scientific details are intentionally deferred to specialized specs/contracts. | Later packages must add stricter metadata/schema requirements where scientific interpretation depends on them; until then, base `FieldSpec` intentionally remains sparse. |
| `FieldValue` wraps payload plus narrow field-level metadata and collation override | accepted | Store metadata directly on `Sample`; store only raw payloads; duplicate `data_type` inside every loaded value | Separating payload from field metadata preserves scientific meaning during transforms and collation. `data_type` is not duplicated in `FieldValue` because the field key/spec already owns broad field identity and duplicated state would drift. Equality is identity-based so tensor-like payload equality is never invoked accidentally. | Keeps arbitrary fields extensible without changing `Sample`; keeps validation narrow so the wrapper does not pretend to understand data-specific scientific semantics. | Tests for automatic wrapping, existing-wrapper insertion, metadata shallow-copy behavior, schema preservation, collation-policy precedence, absence of duplicated `data_type`, identity equality, unhashability, and explicit shallow/deep copy behavior. | Wrapper remains intentionally generic; specialized data objects/contracts must enforce shape, dtype, units, coordinate frames, and temporal assumptions where needed. |
| `DataObjectBase` is backend-agnostic and duck-typed | accepted | Add torch as a base dependency now; no base class until modality objects exist; allow isolated optional torch submodules later | Base imports must stay lightweight, but later data objects need a common place for explicit validation, tensor traversal, and device movement hooks. The base contract validates only when `validate` or a documented subclass/contract path calls validation; `Sample.set_field` and list collation do not auto-validate objects. Traversal operates only over tensor-like leaves that a subclass exposes through its hook, and device/detach/pin operations call same-named methods on those leaves when present. Callers must use the returned object; base operations do not promise in-place mutation. Base equality is identity-based and base instances are not hashable; subclasses may define value equality or hashability only with docs and tests. A declared tensor-like leaf that lacks the requested operation raises `RemotePhysDataError`; an object with no declared tensor-like leaves is a documented no-op returning an object with the same public value. The maintainer approved optional torch use in an isolated submodule if implementation later needs it. | Avoids base dependency leakage while preserving extension hooks for torch/numpy-backed objects and future optional backend submodules. | Tests with synthetic tensor-like objects, explicit validation timing, traversal path behavior, returned-object behavior, identity equality, unhashability, no-op behavior for no declared leaves, unsupported-hook errors, and no heavy import boundary checks for base imports; any future torch submodule must be optional and separately import-gated. | Backend integrations may later need richer traversal hooks; optional torch support must not change base import behavior. |
| `Sample` is a domain container with mapping-like helpers, explicit mutation, and explicit copy behavior | accepted | Full `MutableMapping` subclass; immutable samples; copy-on-write mutation; shallow copy only | `Sample` needs clear field semantics: `field` returns the wrapper, while `get` and `require` return payloads. Full mapping inheritance would blur wrapper-versus-payload behavior. Mutable operations are explicit, branch isolation uses explicit deep copy, and equality is identity-based to avoid comparing arbitrary payloads. | Gives downstream transforms/methods a stable ergonomic API without pretending `Sample` is a plain dict. | Tests for `has`, `field`, `get`, `require`, `set_field`, `delete_field`, `rename_field`, error diagnostics, automatic wrapping, shallow copy, deep copy, metadata copy, branch isolation, identity equality, unhashability, and no `MutableMapping` inheritance. | Mutable containers require careful transform contracts in later packages. |
| `Batch` subclasses `Sample` initially | accepted | Duplicate the public API without inheritance; separate protocol only | Inheritance gives exact API reuse for the first implementation and matches the architecture sketch. Batch equality remains identity-based and hashability is not public, matching `Sample`. | Reduces code duplication and keeps downstream access uniform. | Tests that `Batch` access mirrors `Sample`, batch size validation, identity equality, unhashability, and type behavior. | If later batch semantics diverge from `Sample`, composition or a shared protocol should be revisited before broad downstream use. |
| Initial collation supports only explicit `LIST` policy | accepted | Default-to-list behavior; early `STACK`; early `PAD_TEMPORAL`; `CUSTOM`; object-delegated collation; missing-field policies | Silent collation can change scientific meaning through padding, truncation, dropping fields, coercion, or accidental lists. Starting with only explicit `LIST` keeps the behavior honest and backend-free. | Forces later data objects and pipelines to state shape/missing behavior before richer batching support is added. | Tests for non-empty inputs, exact field-set matching, absent-policy failure, unsupported-policy failure, explicit `LIST` behavior, deterministic batch metadata, and metadata missing-key handling. | Early users must opt into list collation per field; stack/pad/custom behavior must be added deliberately later. |
| Metadata collation returns deterministic lists | accepted | Promote numeric metadata to tensors; preserve only first value; drop metadata | List collation is backend-free and preserves per-sample provenance. Missing metadata keys produce `None` in sample order. | Keeps metadata reproducible without adding dependencies or implicit aggregation. | Tests for sample metadata key union/order and missing metadata values as `None`. | Numeric metadata may later need opt-in tensor promotion. |
| Full modality objects are deferred | accepted | Implement `VideoData`, `SignalData`, and related classes now | A full modality library would expand scope and require backend decisions before field containers are stable. | Keeps this package reviewable and leaves modality-specific contracts to later packages. | Docs state deferral; tests use local synthetic subclasses instead of public placeholders. | Later packages must add modality contracts deliberately. |
| `SampleContract` belongs in this package as a minimal explicit-call runtime validator | accepted | Defer to transforms/datasets; make it IO-owned; automatically validate on every sample mutation; include shape/unit/axis/coordinate checks now | Required/optional field validation is a runtime concern consumed by many later packages, but automatic validation would make normal sample mutation surprising and a rich scientific schema would duplicate future dataset/transform/modality contracts. Contract objects use value equality over declared requirements and options but are not hashable by contract. | Gives later transforms, builders, and methods one shared contract object without turning the runtime core into a dataset schema system. | Tests for explicit-call validation, required/optional fields, expected payload type, schema checks, missing-field diagnostics, wrong-type diagnostics, value equality, unhashability, and no automatic validation during `set_field`. | The first version is intentionally narrow; later packages must add richer scientific contracts where needed. |

## Maintainer Decision Walkthrough

- Walkthrough status: high-level proposal, deep design review, quality gate, and full-plan acceptance complete
- Current round: all packets approved or revised into accepted decisions
- Approval rule: the high-level packets below established preliminary direction only. This master plan is accepted because the quality gate passed and the maintainer explicitly accepted the full plan on 2026-05-08.

| Packet | Topic | Proposal | Implementation Consequence | Maintainer Response | Plan Update | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Runtime scope and ownership boundary | `rphys.data` owns loaded runtime contracts only; `FieldRef`, `TemporalIndexSlice`, `FieldView`, codecs, dataset indexes, transforms, and full modality classes stay out of scope. | Phase work stays focused on keys, specs, values, data object hooks, samples, batches, contracts, and collation; future IO and modality packages must build on these contracts instead of expanding this package. | Approved all Round 1 packets on 2026-05-08. | Decision rows updated to accepted. | accepted |
| 2 | Field identity and metadata model | `DataKey` is a validated `str` subclass with reserved standard namespaces and `custom.<project>.<field...>` extension keys; base `FieldSpec` requires only `key` and `data_type` with optional `schema`; `FieldValue` wraps payload plus narrow field metadata and an optional explicit `LIST` collation policy. | Users get ergonomic string-like keys and extension safety without registries; downstream datasets/transforms must add specialized specs or contracts when stricter scientific metadata is needed. | Approved all Round 1 packets on 2026-05-08, then narrowed through D2-D3 deep design review. | Decision rows updated to accepted and refined. | accepted |
| 3 | Dependency and data-object posture | The runtime core stays dependency-free; `DataObjectBase` uses duck-typed hooks and tests use synthetic tensor-like objects; concrete `VideoData`, `SignalData`, and related modality objects remain deferred. | Base imports remain lightweight; backend-specific traversal, stack, padding, and modality semantics are added later only when code-backed contracts exist. | Approved on 2026-05-08 with allowance that torch is acceptable in an isolated optional submodule if needed. | Decision row updated to accepted; optional torch submodule allowance recorded as an accepted package-level assumption. | accepted |
| 4 | Sample and Batch semantics | Samples are mutable by default with explicit shallow and deep copy semantics; `Batch` subclasses `Sample` initially to preserve identical field access. | Transforms and methods can share `has`, `field`, `get`, and `require`; branching pipelines should deep copy explicitly; subclassing may be revisited if batch behavior diverges. | Approved on 2026-05-08 with revision that branching should probably use deep copy. | Decision row, behavior model, public conventions, validation, and Phase 2 scope updated for deep copy. | accepted |
| 5 | Runtime contracts and collation | `SampleContract` is a minimal explicit-call runtime validator; collation is field-level and supports only explicit `LIST` initially; metadata collates to deterministic lists. | Missing fields, ragged data, unsupported padding, absent policies, and unsupported policies fail loudly instead of producing silent lists, truncation, padded outputs, or backend-specific behavior. | Approved on 2026-05-08, then narrowed through D6-D7 deep design review. | Decision rows updated to accepted and refined. | accepted |
| 6 | Phase, validation, and merge plan | Implement four sequential phases: keys/fields/docs, sample/batch containers, objects/contracts/collation, and validation closeout. Use the standard comprehensive pathway for every phase; use xhigh reasoning for Phase 1 where agent/model settings are configurable. | Stage 3 gets disjoint file ownership, clear stop conditions, explicit validation commands, comprehensive automated review for every phase, and extra reasoning depth for the initial public-contract phase. | Revised on 2026-05-08: maintainer prefers standard comprehensive pathway for this package and xhigh for the initial phase. | Pathway guidance, Phase 1 reviewability, Phase 4 reviewability, review requirements, and accepted assumptions updated. | accepted |

Accepted package-level assumptions:

- Base imports for `rphys` and `rphys.data` remain dependency-free and must not import torch, numpy, pandas, OpenCV, scipy, sklearn, tensorflow, dataset SDKs, or plotting libraries.
- Torch may be used later in an isolated optional submodule if implementation needs it, provided it is import-gated, documented, tested separately, and does not affect base `rphys.data` imports.
- `FieldRef`, `TemporalIndexSlice`, `FieldView`, dataset indexes, codecs, sample builders, transforms, and concrete modality classes remain out of scope for this package.
- Branching runtime workflows should use explicit deep copy unless a later transform contract deliberately documents payload sharing.
- Every implementation phase uses the standard comprehensive pathway unless the maintainer explicitly revises this plan.
- Phase 1 should use xhigh reasoning for manager decisions and configurable planning/coding/review agents because it establishes important public contracts.

Unresolved decision packets:

- None.

## Deep Design Review

- Review status: complete for required discussions; quality gate passed; full plan accepted
- Review required because: `rphys.data` introduces foundational public runtime contracts that downstream dataset IO, transforms, training, evaluation, and extension packages will build on. The maintainer explicitly flagged that the prior discussion was not deep enough to accept these module contracts.
- Current design packet: none
- Approval rule: the master plan is not accepted until each required deep design packet is accepted, revised into the plan, or explicitly deferred with a reason Stage 3 can proceed.

| Packet | Topic | Design Surface | Key Questions | Maintainer Response | Plan Update | Status |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | `DataKey` and field identity | `DataKey` grammar, namespace policy, validation strictness, equality/hash behavior, constants, aliases, serialization, custom-key extension, and future standard-key growth. | Should `DataKey` be a `str` subclass or value object? How strict should grammar be? Are namespaces and semantic parts enough? Should standard keys be constants now or deferred? Are aliases out of scope? | Maintainer answered yes to `DataKey(str)`, flexible namespace-plus-parts validation, and deferring standard field constants beyond namespace constants. | Accepted: `DataKey(str)`, lowercase ASCII dot-separated lexical validation, reserved namespaces plus `custom.<project>.<field...>`, namespace constants only in Phase 1, aliases out of scope. | accepted |
| D2 | `FieldSpec` and scientific metadata contract | Minimal required fields, optional schema/version identifier, and relation to future specialized specs such as tensor/video/signal specs. Exclude data-specific details such as axes, layout, units, sample rate, temporal axis, coordinate frame, generic `runtime_type`, and `description` from this phase unless a later decision reopens them. | What is the smallest strict `FieldSpec` that remains useful? Should Phase 1 require only `key` and `data_type`, with optional `schema`, while deferring `description`, `runtime_type`, and specialized specs? | Maintainer agreed this is likely the best initial approach after discussion: base `FieldSpec` should include only necessary consistent fields; more specific specs can be created or expanded later as required. | Accepted: base `FieldSpec` has `key`, `data_type`, and optional `schema`; no `description`, `runtime_type`, coordinate frame, temporal axis, units, layout, or axes in Phase 1; specialized specs deferred. | accepted |
| D3 | `FieldValue` and payload wrapping | Payload/wrapper separation, field metadata mutability, schema handling, collate policy overrides, copy behavior, serialization expectations, and arbitrary custom payload support. | Should payloads always be wrapped? How much validation happens at set time? Should metadata be copied defensively? Should `data_type` be duplicated inside `FieldValue`? | Maintainer agreed the proposed narrow wrapper is reasonable for now. | Accepted: `FieldValue` stores `value`, optional `schema`, shallow-copied `metadata`, and optional `collate_policy`; it does not store `data_type`; data-specific validation is deferred to data objects, specialized specs, or contracts. | accepted |
| D4 | `Sample` and `Batch` API semantics | Mapping behavior, `field`/`get`/`require`, mutation API, delete/rename, shallow/deep copy, batch inheritance, batch size invariants, metadata behavior, and error diagnostics. | Should `Sample` behave like a mapping or a domain container only? Should `Batch` subclass `Sample` or share a protocol? What exactly must deep copy guarantee? | Maintainer agreed to domain-container semantics, no `MutableMapping` subclass, payload-returning `get`/`require`, wrapper-returning `field`, explicit shallow/deep copy, and `Batch(Sample)` initially. | Accepted and reflected in design decisions, validation, and Phase 2 scope. | accepted |
| D5 | `DataObjectBase` and optional backend strategy | Base class responsibilities, validation hooks, tensor traversal, device movement, duck typing, optional torch submodules, and no-heavy-base-import checks. | What backend operations belong in the base class? Should torch-aware behavior be a separate module now or later? How should hooks fail when unsupported? | Classified as recorded recommendation, not individually discussed: keep base duck-typed and dependency-free; allow optional torch submodule later if import-gated. | Quality refinement locked the concrete public semantics: explicit validation timing, subclass-declared leaves only, returned-object behavior, identity equality, unhashability, no-op behavior without declared leaves, `RemotePhysDataError` for unsupported declared hook operations, and no Phase 1 torch import. | accepted recommendation |
| D6 | `SampleContract` and validation timing | Required/optional fields, expected payload types, schema checks, diagnostics, and usage by future builders/transforms/methods. | Is `SampleContract` too early or necessary now? Should validation be automatic or explicit-call? Should it validate wrappers, payloads, or both? How strict should optional fields be? | Maintainer agreed to explicit-call runtime validation for required/optional fields, payload type, and schema, avoiding scientific shape/unit/axis checks for now. | Accepted and reflected in design decisions and validation obligations. | accepted |
| D7 | Collation semantics | Policy enum, precedence, missing fields, list-only initial behavior, padding deferral, metadata collation, batch metadata, and failure behavior. | Should strict collation require explicit policy for every field? Is `LIST` the only supported initial policy? What metadata should be produced for missing metadata keys? | Maintainer agreed to start with only explicit `LIST` collation and fail when policy is absent by default. | Accepted: Phase 1/3 exposes only `LIST`; absent policy fails; all samples must have identical field sets; stack/pad/missing/custom/object delegation deferred; batch metadata collates to deterministic lists with `None` for missing sample metadata keys. | accepted |

Design examples or sketches discussed:

- D1 proposed `DataKey(str)`, lowercase ASCII dot-separated tokens, reserved namespace or `custom`, at least two tokens for standard keys, at least three tokens for custom keys, lexical validation rather than semantic catalog enforcement, namespace constants in Phase 1, and aliases out of scope.
- D2 revised direction: `FieldSpec` should be minimal and strict, avoiding data-specific integration logic. Coordinate frames, temporal axes, sample rates, layouts, axes, units, generic `runtime_type`, and `description` are not part of the initial base `FieldSpec` contract unless reopened. Useful scientific specificity should come from future specialized specs or modality/data-object contracts.
- D2 accepted direction: base `FieldSpec` has `key`, `data_type`, and optional `schema`; specialized specs are deferred until a concrete package needs them.
- D3 accepted direction: `FieldValue` always wraps runtime payloads and stores only `value`, optional `schema`, shallow-copied `metadata`, and optional `collate_policy`; it does not duplicate `data_type`.
- D4 accepted direction: `Sample` is a domain container, not a `MutableMapping`; `field` returns wrappers, `get`/`require` return payloads, mutation and copy operations are explicit, and `Batch` subclasses `Sample` initially.
- D6 accepted direction: `SampleContract` validates only when explicitly called and checks required/optional fields, payload type, and schema; richer scientific checks are deferred.
- D7 accepted direction: initial collation supports only explicit `LIST`; absent policy fails; all samples must have identical field sets; stack, padding, missing-field, custom, and object-delegated policies are deferred.

Public contract semantics locked by quality refinement:

- `DataKey`: value equality and hashing follow `str`; copy and deep copy preserve the same string value, and callers must not rely on object identity. The stable serialization token is the key string. No aliasing or registry serialization exists in this package.
- `FieldSpec`: value equality covers `key`, `data_type`, and `schema`; it is not hashable by public contract. Copy and deep copy are value-preserving over those primitive fields; implementations may return the same immutable object or an equivalent object, and callers must rely on equality rather than identity. No public serialization or dict round trip is introduced beyond users reading these primitive attributes.
- `FieldValue`: equality is object identity, not payload value equality; it is not hashable. Construction shallow-copies `metadata`; shallow copy shares payload and metadata values intentionally; deep copy delegates to normal Python deep-copy behavior and may fail for non-copyable payloads with the underlying error. No serialization contract exists for arbitrary payloads.
- `DataObjectBase`: equality is object identity and base instances are not hashable; subclasses may define value equality or hashability only with docs and tests. Generic copy and deep copy are not public base guarantees; subclasses may support copy only when they document and test payload sharing/isolation semantics. Validation is explicit-call only. Subclasses declare tensor-like leaves for traversal; the base must not inspect arbitrary attributes or import backend libraries. Device/detach/pin operations return an object that callers must use, are transformation operations rather than copy operations, do not promise in-place mutation, no-op when no tensor-like leaves are declared, and raise `RemotePhysDataError` when a declared leaf cannot perform the requested operation.
- `Sample` and `Batch`: equality is object identity; they are not hashable. `shallow_copy` shares payload objects and nested metadata values; `deep_copy` is the branch-isolation operation for ordinary copyable payloads. No JSON, pickle, or dict serialization round trip is a public contract in this package.
- `SampleContract`: value equality covers declared required/optional fields, expected payload types, schemas, and validation options; it is not hashable. Copy and deep copy are value-preserving over declared requirements and options; implementations may return the same immutable object or an equivalent object, and callers must rely on equality rather than identity. It validates only when explicitly called and does not serialize as a public schema format.
- `CollatePolicy`: enum member identity, equality, hashing, copy, deep copy, and name/value tokens are public for the exposed `LIST` member only; copying preserves the enum member identity. Reserved or future policy names must fail if used before implementation.
- `CollateContext`: value equality covers documented context fields, but it is not hashable. Copy and deep copy are value-preserving for documented context fields; implementations may share referenced immutable policy/key objects, and callers must not treat a copied context as durable state. It is an execution context for collation, not a durable serialization format.
- Serialization boundary: this package stabilizes only key strings and documented primitive attributes. Payload serialization, sample persistence, contract export, and backend tensor serialization are deferred to later IO/dataset plans.

Unresolved deep design blockers:

- None known after targeted copy-boundary clarification, focused confirmation review, and full-plan acceptance.

## Structure And Extensibility

- Directory/module structure:
  - `src/rphys/data/__init__.py`: public exports for runtime contracts.
  - `src/rphys/data/keys.py`: `DataKey`, namespace constants, standard namespace validation.
  - `src/rphys/data/fields.py`: `FieldSpec` and `FieldValue`.
  - `src/rphys/data/objects.py`: `DataObjectBase` and backend-agnostic tensor traversal helpers.
  - `src/rphys/data/samples.py`: `Sample`, `Batch`, and field access/mutation behavior.
  - `src/rphys/data/collation.py`: `CollatePolicy`, `CollateContext`, and `collate_samples`.
  - `src/rphys/data/contracts.py`: `SampleContract` and field requirement validation.
  - `docs/data/runtime-core.md`: code-backed user-facing contract document.
  - `tests/test_data_keys.py`, `tests/test_field_specs_values.py`, `tests/test_samples_batches.py`, `tests/test_data_objects.py`, `tests/test_collation.py`, `tests/test_sample_contracts.py`: layered runtime tests.
  - Existing public import and dependency-boundary tests updated for real `rphys.data` exports.
- Ownership boundaries:
  - `rphys.data`: loaded runtime values and contracts.
  - `rphys.io`: future lazy references, codecs, and external payload loading.
  - `rphys.datasets`: future dataset discovery, filtering, indexing, and sample building.
  - `rphys.transforms`: future `Sample -> Sample` behavior.
  - `src/rphys/data/collation.py` is an intentional sequential handoff: Phase 1 introduces only `CollatePolicy.LIST`, then Phase 3 reopens the same file after Phase 1 has merged to add `CollateContext` and `collate_samples`. No parallel phase may edit this file.
- Dependency direction:
  - `rphys.data` may import `rphys.errors`.
  - `rphys.data` must not import `torch`, `numpy`, `pandas`, `cv2`, `scipy`, `sklearn`, `tensorflow`, dataset SDKs, or future `rphys.io`/`datasets`/`transforms` modules.
- Extension points:
  - User-defined keys under `custom.<project>.<field...>`.
  - Arbitrary `FieldValue.value` payloads.
  - `DataObjectBase` subclasses with validation, tensor traversal, and device movement.
  - `SampleContract` field requirements.
  - Explicit per-field `LIST` collation policy.
- Coupling intentionally avoided:
  - No lazy IO resources in runtime values.
  - No transform classes in sample mutation methods.
  - No backend-specific array/tensor imports.
  - No registry requirement for ordinary custom fields.
- Expected future changes this structure should absorb:
  - Concrete modality data objects.
  - Optional torch/numpy extras and richer device movement.
  - Dataset sample builders creating `Sample` instances.
  - Transforms validating input/output contracts.
  - Methods emitting prediction fields as `Sample` or `Batch`.

## Public Interfaces And Documents

- Files or docs allowed to change:
  - `src/rphys/data/**`
  - `src/rphys/errors.py` only if narrow data errors are added under `RemotePhysDataError`
  - `docs/data/runtime-core.md`
  - `docs/architecture/public-contracts.md`
  - `README.md` if a docs link is needed
  - `tests/**` for runtime contract tests and existing public-boundary updates
  - `docs/implementation/02-field-runtime-core/implementation-plan.md` during Stage 3
- Public behavior or conventions introduced:
  - `DataKey` grammar and reserved namespace behavior.
  - `custom.<project>.<field...>` extension convention.
  - Field-level metadata and sample-level metadata separation.
  - Mutable `Sample` behavior and explicit shallow/deep copy semantics.
  - Same field access API on `Sample` and `Batch`.
  - Strict, explicit `LIST` collation policy.
  - Deterministic list-based sample metadata collation.
  - Public API stability labels for every new public contract, following `docs/architecture/public-contracts.md`.
- Compatibility constraints:
  - Base imports remain dependency-free.
  - Existing `RemotePhys*Error` hierarchy remains stable.
  - `FieldRef`, `TemporalIndexSlice`, and `FieldView` remain deferred to `rphys.io`.
  - Deferred module homes remain absent until their own plans land.
  - Each new public API must be labeled `Stable`, `Provisional`, or `Private/internal` in docs before downstream code relies on it; undocumented imports are not stable by default.

## Validation Strategy

- Behavior that must be tested:
  - Valid and invalid `DataKey` syntax, namespaces, string equality, hashing, and normalization from `str`.
  - `FieldSpec` construction, required `key`/`data_type` checks, optional schema behavior, value equality, unhashability, value-preserving copy/deep-copy behavior, and lack of accidental public fields.
  - `FieldValue` wrapping, metadata mutability/copy behavior, collation-policy precedence, identity equality, unhashability, and no arbitrary payload serialization contract.
  - `Sample` field access, mutation, deletion, rename, `require`, wrong type diagnostics, identity equality, unhashability, shallow copy behavior, and deep copy branch isolation.
  - `Batch` API parity with `Sample`, batch size validation, identity equality, and unhashability.
  - `DataObjectBase` explicit validation timing, synthetic tensor traversal, returned-object behavior, identity equality, unhashability, documented no-public-copy guarantee for the base class, no declared-leaf no-op behavior, unsupported declared-hook failure, `to`, `cpu`, `detach`, and `pin_memory` without importing torch.
  - Strict collation for empty inputs, inconsistent field sets, absent policy, explicit `LIST`, unsupported stack/padding/custom policies, and deterministic metadata lists.
  - `SampleContract` required/optional fields, expected payload types, schema checks, explicit-call timing, value equality, unhashability, and value-preserving copy/deep-copy behavior.
  - `CollatePolicy` enum copy/deep-copy identity behavior and `CollateContext` value-preserving copy/deep-copy behavior.
- Behavior that must be documented:
  - Runtime inputs and outputs, payload wrapper semantics, metadata locations, dtype/device expectations for backend-agnostic hooks, mutability, per-contract copy/no-copy behavior, explicit `LIST` collation, failure behavior, extension rules, and the explicit deferral of shape/unit/axis/coordinate-frame/sample-rate enforcement to later specialized specs or contracts.
  - The boundary between loaded runtime values and future lazy IO references.
  - Stability labels for every new public API introduced by this package, consistent with `docs/architecture/public-contracts.md`.
- Behavior guarded by templates or workflow checks:
  - Public import tests.
  - Placeholder absence tests for deferred modules.
  - Dependency-boundary static import checks.
  - `git diff --check`.
- Synthetic fixtures or safe test data:
  - Pure Python scalar/list payloads.
  - Local test-only `DataObjectBase` subclasses.
  - Synthetic tensor-like objects with `.to`, `.cpu`, `.detach`, and `.pin_memory` methods.
  - No raw datasets or external media.
- CI/static/check commands:
  - `uv run pytest tests/test_data_keys.py`
  - `uv run pytest tests/test_field_specs_values.py tests/test_samples_batches.py`
  - `uv run pytest tests/test_data_objects.py tests/test_collation.py tests/test_sample_contracts.py`
  - `uv run pytest tests/test_public_imports.py tests/test_dependency_boundaries.py tests/test_public_contract_docs.py tests/test_error_hierarchy.py`
  - `uv lock --check`
  - `uv run pytest`
  - `git diff --check`
- Acceptance evidence required before merge:
  - Phase-specific tests pass.
  - Full test suite passes or failures are documented as unrelated.
  - Dependency-boundary check shows no heavy optional imports.
  - Public docs and code exports agree.
  - Public docs assign stability labels to each new public API and tests or manual evidence confirm there are no undocumented public exports.
  - Implementation plan records validation evidence, review/checklist outcome, PR facts or direct-commit deviation, blockers, and cleanup.

## Implementation Phases

| Phase | Slug | Status | Branch | Worktree | Ownership | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `keys-fields-and-docs` | pending | `agent/field-runtime-core-p1-keys-fields-and-docs` | `../rphys-worktrees/field-runtime-core-p1-keys-fields-and-docs` | `src/rphys/data/keys.py`, `src/rphys/data/fields.py`, `src/rphys/data/collation.py` for `CollatePolicy` only, `src/rphys/data/__init__.py`, runtime docs, key/field tests | `DataKey`, minimal `FieldSpec`, narrow `FieldValue`, `CollatePolicy.LIST`, initial docs, and public exports land. |
| 2 | `sample-batch-containers` | pending | `agent/field-runtime-core-p2-sample-batch-containers` | `../rphys-worktrees/field-runtime-core-p2-sample-batch-containers` | `src/rphys/data/samples.py`, relevant exports, sample/batch tests | Mutable `Sample` and `Batch` field APIs land. |
| 3 | `objects-contracts-and-collation` | pending | `agent/field-runtime-core-p3-objects-contracts-and-collation` | `../rphys-worktrees/field-runtime-core-p3-objects-contracts-and-collation` | `src/rphys/data/objects.py`, `src/rphys/data/contracts.py`, `src/rphys/data/collation.py` after Phase 1 merge, relevant tests | Backend-agnostic data object hooks, sample contracts, and explicit collation land. |
| 4 | `contract-validation-closeout` | pending | `agent/field-runtime-core-p4-contract-validation-closeout` | `../rphys-worktrees/field-runtime-core-p4-contract-validation-closeout` | public import tests, dependency-boundary tests, public-contract docs, implementation ledger | Full validation, docs alignment, and boundary checks are reconciled. |

Phase execution rule: implement one phase at a time. Phase `n + 1` may start only after phase `n` has merged and branch/worktree cleanup is complete.

### Phase 1 - Keys, Fields, And Runtime Docs

- Goal:
  - Establish field identity and loaded field wrappers.
- Scope:
  - `DataKey`, reserved namespaces, custom key rule, minimal `FieldSpec`, narrow `FieldValue`, `CollatePolicy` with only `LIST`, initial runtime docs, and public exports.
- Out of scope:
  - `Sample`, `Batch`, `DataObjectBase`, `CollateContext`, `collate_samples`, IO refs, modality classes, and policies beyond `LIST`.
- Acceptance criteria:
  - Keys validate deterministically.
  - Field specs and values record only the accepted narrow fields without hidden IO behavior or data-specific integration metadata.
  - Public-contract semantics for `DataKey`, `FieldSpec`, `FieldValue`, and `CollatePolicy.LIST` include equality, hashability, copy/deep-copy, and serialization boundaries.
  - Public docs describe runtime/IO boundary and field metadata contract.
  - Public docs assign stability labels to each Phase 1 public API consistent with `docs/architecture/public-contracts.md`.
- Test expectations:
  - Package: import `rphys.data` exports.
  - Unit: key parsing, invalid keys, field spec/value construction, equality/hashability behavior, `FieldSpec` value-preserving copy/deep-copy behavior, `FieldValue` copy behavior, and `CollatePolicy.LIST` copy/deep-copy identity behavior.
  - Contract: no heavy imports, no lazy IO concepts exported from `rphys.data`.
  - Integration: none.
  - E2E: none.
  - Opt-in: none.
- Design impact:
  - Locks the field naming and metadata wrapper baseline.
- Future compatibility:
  - Dataset schemas and transforms can refer to the same key/spec/value types.
- Alternatives rejected:
  - Plain strings only, unvalidated namespace names, field refs in data.
- Debt introduced:
  - Standard key constants may start small; broad catalogs remain deferred.
- Reviewability:
  - Small API-heavy diff with focused tests. Use xhigh reasoning for manager decisions and configurable planning/coding/review agents because this phase establishes initial public runtime contracts.
- Completion summary:
  - Pending.

### Phase 2 - Sample And Batch Containers

- Goal:
  - Implement mutable runtime containers and shared field access behavior.
- Scope:
  - `Sample`, `Batch`, field lookup/mutation, `require`, `shallow_copy`, `deep_copy`, metadata behavior, public exports, tests.
- Out of scope:
  - Transform contracts, collation, data object traversal, dataset sample builders.
- Acceptance criteria:
  - Samples and batches can store, require, mutate, shallow-copy, deep-copy, delete, and rename arbitrary fields with clear diagnostics.
  - Deep copy isolates branch mutations for ordinary copyable payloads; shallow copy is documented as sharing payloads intentionally.
  - Batch exposes the same public field API as Sample.
  - Sample and Batch identity equality, unhashability, copy behavior, and serialization boundary are tested and documented.
- Test expectations:
  - Package: import checks.
  - Unit: sample/batch access, mutation, shallow copy, deep copy, identity equality, and unhashability tests.
  - Contract: missing and wrong-type failure tests.
  - Integration: synthetic multi-field sample.
  - E2E: none.
  - Opt-in: none.
- Design impact:
  - Locks the central runtime access pattern for later transforms and methods.
- Future compatibility:
  - Later transforms can operate on `Sample -> Sample`; methods can consume samples and batches uniformly.
- Alternatives rejected:
  - Immutable sample containers, hidden copy-on-write mutation, batch API divergence.
- Debt introduced:
  - If subclassing proves restrictive, revisit before downstream broad adoption.
- Reviewability:
  - Focused container behavior diff.
- Completion summary:
  - Pending.

### Phase 3 - Data Objects, Contracts, And Collation

- Goal:
  - Add backend-agnostic typed object hooks, runtime sample contracts, and strict explicit collation.
- Scope:
  - `DataObjectBase`, `SampleContract`, `CollateContext`, `collate_samples`, explicit list collation, deterministic metadata collation, and tests.
- Out of scope:
  - Concrete modality classes, backend-specific stack/padding implementations, dataset builders, and additional collation policies beyond `LIST`.
- Acceptance criteria:
  - Data objects can validate and map synthetic tensor-like payloads without heavy imports.
  - Data object validation timing, subclass-declared traversal, returned-object behavior, no-op behavior, and unsupported-hook failure behavior match the public contract.
  - Sample contracts catch missing fields, wrong payload types, and schema mismatches.
  - Collation fails on ambiguity and succeeds only with explicit `LIST`.
  - Missing fields, absent policies, custom/object policies, stack, and padding behavior fail.
  - `SampleContract` and `CollateContext` equality/hashability, copy/deep-copy, and serialization boundaries are tested and documented.
  - The Phase 1 `src/rphys/data/collation.py` handoff is recorded in `implementation-plan.md` before editing the file.
- Test expectations:
  - Package: import checks.
  - Unit: data object hooks, sample contract validation, list-only collation policy behavior, copy/no-copy boundaries, and context copy behavior.
  - Contract: missing field, unsupported padding, absent policy, and metadata collation tests.
  - Integration: synthetic multi-field batch.
  - E2E: none.
  - Opt-in: none.
- Design impact:
  - Locks how downstream training/evaluation code forms batches.
- Future compatibility:
  - Later accepted plans can add stack, padding, custom, or object-delegated collation once concrete modality objects or optional backend modules exist.
- Alternatives rejected:
  - Best-effort list/stack fallback, implicit numeric metadata promotion, early custom/object collation, early stack/padding, mandatory torch dependency.
- Debt introduced:
  - Stack/padding support is intentionally narrow until concrete backend objects exist.
- Reviewability:
  - Medium risk due collation semantics; standard pathway preferred.
- Completion summary:
  - Pending.

### Phase 4 - Contract Validation Closeout

- Goal:
  - Reconcile public docs, import tests, dependency checks, and implementation ledger after runtime behavior lands.
- Scope:
  - Update existing public import and dependency-boundary tests, docs links, implementation plan evidence, and full-suite validation.
- Out of scope:
  - New runtime behavior beyond blocker fixes required by validation.
- Acceptance criteria:
  - Public docs and code exports agree.
  - Every new public API has a documented stability label and no public export relies on an undocumented default.
  - Deferred modules and lazy IO concepts remain deferred.
  - Full repository checks pass or failures are documented.
- Test expectations:
  - Package: full public import suite.
  - Unit: all runtime unit tests.
  - Contract: dependency boundaries, public stability-label docs policy, error hierarchy.
  - Integration: full suite.
  - E2E: none.
  - Opt-in: none.
- Design impact:
  - Locks public validation around the new runtime API.
- Future compatibility:
  - Gives the dataset/IO plan a tested runtime baseline.
- Alternatives rejected:
  - Treat docs/test reconciliation as incidental cleanup.
- Debt introduced:
  - None expected beyond accepted backend-specific deferrals.
- Reviewability:
  - Standard comprehensive pathway required for this package, even if the phase only reconciles tests/docs and records evidence.
- Completion summary:
  - Pending.

## Pathway Guidance

- Standard pathway phases:
  - Phase 1 because it introduces public API and must use xhigh reasoning where agent/model settings are configurable.
  - Phase 2 because it defines mutation and copy semantics.
  - Phase 3 because it defines scientific batching and validation behavior.
  - Phase 4 because the maintainer requested the standard comprehensive pathway for this package.
- Fast-path eligible phases:
  - None under the accepted plan. Any fast-path use requires explicit maintainer approval recorded in `implementation-plan.md`.
- Criteria that force standard pathway:
  - Any public signature change.
  - Any change to `DataKey` grammar, namespace policy, mutability, copy behavior, collation policy precedence, missing-field behavior, or dependency policy.
  - Any concrete modality class or backend-specific behavior added.
  - Any change outside the accepted file set.

## Validation And Tests

- Phase-specific commands:
  - Phase 1: `uv run pytest tests/test_data_keys.py tests/test_field_specs_values.py tests/test_public_imports.py tests/test_dependency_boundaries.py`
  - Phase 2: `uv run pytest tests/test_samples_batches.py tests/test_data_keys.py tests/test_field_specs_values.py`
  - Phase 3: `uv run pytest tests/test_data_objects.py tests/test_sample_contracts.py tests/test_collation.py tests/test_samples_batches.py`
  - Phase 4: `uv run pytest tests/test_public_imports.py tests/test_dependency_boundaries.py tests/test_public_contract_docs.py tests/test_error_hierarchy.py`
- Full-suite command:
  - `uv run pytest`
- Documentation/link checks:
  - Manual review of touched Markdown links.
  - Tests should verify any required README or public-contract link.
- TOML/config checks:
  - `uv lock --check`
- Diff hygiene:
  - `git diff --check`

## Review Requirements

- Standard pathway code review focus:
  - Public API stability, type clarity, error diagnostics, minimal coupling, test coverage, dependency boundaries, and backward compatibility with the first package scaffold.
- Standard pathway scientific/workflow review focus:
  - Explicit shape/unit/axis/coordinate-frame deferrals, sample/field metadata separation, temporal/padding assumptions, mutability risks, collation ambiguity, missing-field behavior, leakage/provenance implications, and downstream transform/dataset compatibility.
- Fast-path manager checklist:
  - Not used for this package under the accepted plan unless the maintainer explicitly approves a later exception.
  - If an exception is approved, the checklist must still confirm no public-interface change, no scientific/workflow contract change, validation commands recorded, and no unresolved blocker.
- Review or checklist recording location:
  - `implementation-plan.md` unless the maintainer explicitly asks for a separate document.

## Merge Policy

- Human review is not a default merge gate.
- Merge automatically when validation and selected pathway gates pass.
- If branch protection blocks solely on human review and available authority permits, approve, admin-merge, or otherwise force merge only after automated validation and pathway gates pass.
- Do not merge known failing validation, wrong-target PRs, unresolved conflicts, unresolved implementation/review blockers, or changes outside this accepted plan.

## Discussion History

- Major question rounds:
  - 2026-05-08: Initial Stage 2 draft created from planning notes, public contract docs, current code surface, and architecture sections 8-15. Maintainer decisions were still needed before acceptance at that draft point.
  - 2026-05-08: Stage 2 workflow revised to require a packet-based maintainer decision walkthrough before full master-plan acceptance. Round 1 will cover runtime boundaries, key/metadata model, and backend dependency posture.
  - 2026-05-08: Maintainer approved all Round 1 packets and noted torch is acceptable in an isolated submodule if needed. The plan preserves dependency-free base imports while allowing a future optional torch submodule if import-gated.
  - 2026-05-08: Maintainer approved Round 2 packets with revisions: branching workflows should probably use deep copy; all implementation phases should use the standard comprehensive pathway; Phase 1 should use xhigh reasoning because it establishes important public contracts.
  - 2026-05-08: Maintainer flagged that the high-level walkthrough was not deep enough for this foundational module. Stage 2 was reopened for deep design review before full master-plan acceptance.
  - 2026-05-08: Maintainer clarified the desired workflow: approve overall intent/functionality first; then classify design decisions; discuss only impactful decisions without strong recommendations or recommendations the maintainer asks to discuss; document as decisions settle; refine plan; run quality gate; resolve final implementation-plan questions if they surface.
  - 2026-05-08: Maintainer explicitly approved F1-F3 intent/functionality baseline under the revised workflow.
- Decisions changed during discussion:
  - Packet 4 changed from shallow-copy-focused semantics to explicit shallow and deep copy semantics, with deep copy as the expected branching default.
  - Packet 6 changed from fast-path closeout eligibility to standard comprehensive pathway for all phases, with xhigh reasoning for Phase 1 where configurable.
- Open questions intentionally deferred:
  - Concrete modality data object library.
  - Backend-specific stack and padding implementations.
  - Standard key constants beyond a minimal namespace/key validation surface.
- Maintainer concerns addressed:
  - Runtime scope and IO boundary.
  - Optional torch use without base import leakage.
  - Branch isolation through deep copy.
  - Comprehensive standard pathway and xhigh reasoning for the initial public-contract phase.
- Maintainer concerns still open:
  - None from the D1-D7 design discussion, quality gate, or full-plan acceptance.

## Master Plan Quality Gate

- Pre-gate design refinement:
  - Completed on 2026-05-08. The plan was reconciled with the accepted D1-D7 decisions: minimal `FieldSpec`, narrow `FieldValue`, no required metadata validation in the base runtime contract, explicit-call `SampleContract`, `CollatePolicy.LIST` only, absent-policy failure, and no object-delegated collation in Phase 1/3.
- Initial review:
  - Completed on 2026-05-08 using `.codex/prompts/master-plan-review.md`.
  - Result: refinement required before confirmation review.
  - Findings summary:
    - Blocking: `DataObjectBase` needed concrete public-contract semantics for validation timing, duck-typed traversal/device operations, returned-object versus in-place behavior, unsupported hook behavior, dependency-free base imports, optional import-gated torch posture, and no object-delegated collation in Phase 1/3.
    - Blocking: public identity, equality, hashability, copy, and serialization boundaries were explicit for `DataKey` but under-specified for `FieldSpec`, `FieldValue`, `Sample`, `Batch`, `SampleContract`, `CollateContext`, `CollatePolicy`, and `DataObjectBase`.
    - Non-blocking: runtime docs needed an explicit requirement for stability labels on every new public API, consistent with `docs/architecture/public-contracts.md`.
    - Non-blocking: Phase 1 and Phase 3 both touched `src/rphys/data/collation.py`; the plan needed either a split file or an explicit sequential handoff.
- Refinement pass:
  - Completed on 2026-05-08.
  - Budget used: one of one allowed master-plan quality refinement passes. Do not run another automated refinement pass.
  - Changes made:
    - Added concrete `DataObjectBase` semantics for explicit validation timing, subclass-declared tensor traversal, no heavy base dependency, returned-object behavior, no-op behavior when no tensor-like leaves are declared, and `RemotePhysDataError` on unsupported declared hook operations.
    - Preserved accepted decisions: dependency-free base imports, optional import-gated torch submodule only in later accepted work, and no object-delegated collation in Phase 1/3.
    - Added public equality, identity, hashability, copy, and serialization boundaries for all new public data contracts, avoiding accidental dataclass defaults as public behavior.
    - Added stability-label requirements to public docs, Phase 1 docs acceptance criteria, Phase 4 closeout criteria, validation strategy, and acceptance evidence.
    - Recorded `src/rphys/data/collation.py` as an intentional sequential handoff: Phase 1 introduces only `CollatePolicy.LIST`; Phase 3 edits the same file only after Phase 1 has merged and cleanup is complete.
    - Confirmed Stage 3 continues to use one live `implementation-plan.md`, sequential phases, standard pathway for all phases, and automatic/admin merge after automated gates without human review as a default gate.
- Confirmation review:
  - Completed on 2026-05-08 using `.codex/prompts/master-plan-review.md`.
  - Result: failed with blocker.
  - Confirmed resolved:
    - `DataObjectBase` semantics are implementation-ready: explicit validation timing, subclass-declared traversal, returned-object behavior, no-op behavior, unsupported-hook errors, dependency-free base imports, optional import-gated torch posture, and no object-delegated collation in Phase 1/3.
    - Public docs and stability-label obligations are required.
    - `src/rphys/data/collation.py` Phase 1/Phase 3 overlap is recorded as an intentional sequential handoff.
  - Remaining blocker:
    - Copy-boundary semantics are still incomplete for `FieldSpec`, `DataObjectBase`, `SampleContract`, `CollatePolicy`, and `CollateContext`; matching test/doc obligations are also incomplete.
- Targeted blocker clarification:
  - Authorized by maintainer on 2026-05-08 after the failed confirmation review. This is not a second broad refinement pass; scope is limited to the copy/no-copy blocker.
  - Changes made:
    - Added copy/deep-copy semantics for `FieldSpec`, `SampleContract`, `CollatePolicy`, and `CollateContext`.
    - Added a no-public-copy guarantee for base `DataObjectBase`, with subclass copy support allowed only when documented and tested.
    - Added matching validation and documentation obligations for copy/deep-copy and no-copy behavior.
  - Focused confirmation review:
    - Completed on 2026-05-08.
    - Result: passed with no blocking findings.
    - Confirmed that copy/no-copy public contracts and matching validation/documentation obligations are complete for `FieldSpec`, `DataObjectBase`, `SampleContract`, `CollatePolicy`, and `CollateContext`.
    - Accepted risk: Phase 3 must make `CollateContext` fields explicit before tests assert value-preserving copy/deep-copy behavior.
- Gate result:
  - Passed on 2026-05-08.
- Full-plan acceptance:
  - Accepted by maintainer on 2026-05-08 after the quality gate passed.
  - Stage 3 startup preflight verified GitHub CLI auth, remote read/write dry-runs through a temporary SSH agent socket, and implementation worktree root write access.
- Blocking findings:
  - None.
- Accepted risks and revisit triggers:
  - Stack, padding, custom, object-delegated, and backend-specific collation remain deferred until concrete modality objects or optional backend extras are accepted.
  - `Batch` subclassing should be revisited before broad downstream use if typing or behavior diverges from `Sample`.
  - Standard modality class names remain deferred to avoid public placeholders.
  - Base `FieldSpec` fields are intentionally minimal; downstream datasets/transforms must require stricter scientific metadata when needed.
  - `FieldValue`, `Sample`, and `Batch` intentionally use identity equality to avoid arbitrary payload comparison; revisit only if downstream code needs structural comparison and can define payload-safe semantics.
  - Serialization is limited to key strings and documented primitive attributes; sample persistence and payload serialization remain deferred to later IO/dataset plans.
  - Phase 3 must define concrete `CollateContext` fields before tests assert value-preserving copy/deep-copy behavior.
  - `src/rphys/data/collation.py` has a planned sequential handoff from Phase 1 to Phase 3; revisit by splitting files only if Phase 1 or Phase 3 grows too large to review cleanly.
- Separate quality-gate documents created:
  - No.

## Blocker Policy

The manager may attempt two automated blocker-fix and re-review cycles for the same blocker. PRs should be auto-merged after pathway gates pass. Human review is not a merge gate. If branch protection blocks solely on human review and available authority permits, approve, admin-merge, or otherwise force merge after automated gates pass. Stop for maintainer intervention only if the blocker remains, GitHub auth is invalid, branch protection blocks merge without available authority, validation is failing, conflicts remain unresolved, or the implementation would require changing accepted design decisions.

## Open Questions Or Accepted Assumptions

- Accepted decision: deep design discussion covered the important, impactful, or unclear items required before quality gate; no unresolved design blocker remains before formal master-plan review.
- Accepted decision: `Batch` should subclass `Sample` for the first implementation.
- Accepted decision: concrete modality objects remain deferred, with tests using local synthetic `DataObjectBase` subclasses.
- Accepted decision: strict collation supports only explicit `LIST` initially; absent policy, custom hooks, object-delegated collation, stack, padding, and missing-field policies fail until added by a later accepted plan.
- Accepted assumption: no torch, numpy, pandas, OpenCV, scipy, sklearn, tensorflow, dataset SDK, or plotting dependency is allowed in base imports for this package.
- Accepted assumption: torch is acceptable in an isolated optional submodule if needed, provided the submodule is import-gated and does not affect base imports.
- Accepted assumption: base `FieldSpec` remains minimal with only `key`, `data_type`, and optional `schema`; specialized specs or later contracts must add stricter data-specific semantics where needed.
- Accepted assumption: `FieldRef`, `TemporalIndexSlice`, `FieldView`, dataset indexes, codecs, and sample builders remain out of scope.
- Accepted assumption: branching runtime workflows should use explicit deep copy unless a later accepted transform contract documents payload sharing.
- Accepted assumption: all implementation phases use the standard comprehensive pathway, and Phase 1 uses xhigh reasoning where configurable.
- Accepted assumption: every new public runtime API must carry an explicit stability label in docs before downstream code treats it as stable.
