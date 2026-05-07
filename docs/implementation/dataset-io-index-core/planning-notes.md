# Stage 1 Planning Notes: Dataset IO And Index Core

## Metadata

- Roadmap slug: `dataset-io-index-core`
- Source context:
  - `docs/rphys_architecture_plan_v3.md`
  - `docs/implementation/field-centric-architecture-scaffold/planning-notes.md`
  - `docs/roadmap/index.md`
- Planning notes status: draft
- Current discussion stage: roadmap framing
- Related roadmap row: `Dataset IO and index core`
- Blockers:
  - Split boundaries have not been confirmed by the maintainer.
  - Dependency on accepted runtime field contracts is unresolved.
  - Design-decision review has not started.

## Stage Gates

| Stage | Status | Locked decisions | Defaults | Open questions | Next focus |
| --- | --- | --- | --- | --- | --- |
| Roadmap framing | draft | Broad architecture is split; this package owns dataset refs, lazy IO, indexing, and codec contracts | Runtime core precedes this package | Should concrete reference codecs be included? | Confirm scope |
| Intent discovery | draft | None yet | Serve dataset adapter authors and SampleBuilder users | Which first dataset workflow matters most? | Clarify workflows |
| Capability brainstorming | draft | None yet | Include refs, views, slices, indexes, specs, builders, filters, codec protocol | Real adapters deferred unless selected | Mark include/defer |
| Functionality and behavior confirmation | not started | None yet | Lazy IO only; no loaded data in refs/indexes; strict slice behavior | None yet | Confirm behavior |
| Context compaction/reset checkpoint | not started | None yet | Stop with resume instruction if direct compaction is unavailable | None | Record checkpoint |
| Design-decision review | not started | None yet | Review queue below | None yet | Review decisions |
| Phase shaping | not started | None yet | Synthetic fixtures first | None yet | Sketch phases |
| Handoff | not started | None yet | Carry accepted IO contracts into transforms/materialization | None yet | Prepare Stage 2 inputs |

## Context Extraction

Baseline outcome:

- Implement the reference-oriented dataset layer and lazy IO contracts that turn dataset records into runtime Samples.

Constraints:

- Dataset adapters emit serializable refs, not loaded payloads.
- `DatasetRef -> RecordRef -> FieldRef` describes dataset structure.
- `FieldRef + TemporalIndexSlice -> FieldView -> IndexItem` describes lazy IO.
- IndexItems do not encode transforms, augmentation, formatting, or learning logic.
- Codecs must not silently ignore requested slices or load full fields when slicing is unsupported.

Deferred or out-of-scope ideas:

- Spatial slices.
- Time-based slices.
- Multi-member IndexItems.
- Full real dataset adapter and codec catalog.
- Runtime transform and materialization implementation.

Scientific workflow obligations:

- Dataset refs and schemas must preserve metadata needed for units, sampling rates, fps, temporal axes, coordinate frames, selectors, codecs, and provenance.
- Invalid records/windows should be filtered during record/view/index construction, not by runtime transforms.

## User Intent

Target audience:

- Dataset adapter authors, codec authors, and training/evaluation users who need reproducible lazy loading.

User-visible outcome:

- A clear path from dataset scan to IndexItems to Samples without eager IO or hidden transformations.

Success criteria:

- Dataset adapters expose arbitrary logical fields.
- SampleBuilder loads requested FieldViews through codecs.
- Missing fields, unsupported slices, out-of-bounds slices, codec errors, and schema mismatches fail loudly.
- Synthetic fixtures prove the flow end to end.

Non-goals:

- Dataset formatting/export.
- Runtime augmentation.
- Training/evaluation.

Operational constraints:

- Keep real backend dependencies optional and avoid raw datasets in the repo.

## Brainstormed Capabilities

| Capability | Decision | Rationale | Notes |
| --- | --- | --- | --- |
| `DatasetRef` | include, pending confirmation | Describes dataset/view/manifest structure | May wrap loom manifest mechanics |
| `RecordRef` | include, pending confirmation | Describes logical dataset item | Contains FieldRefs and metadata |
| `FieldRef` | include, pending confirmation | Serializable complete field reference | Uses codec, selector, schema, metadata |
| `TemporalIndexSlice` | include, pending confirmation | Initial bounded slice type | Index-based only |
| `FieldView` | include, pending confirmation | Lazy IO request | FieldRef plus optional slice |
| `IndexItem` | include, pending confirmation | SampleBuilder input | Lazy IO only |
| `SampleSpec` and `SampleBuilder` | include, pending confirmation | Validates and loads requested fields | Depends on runtime core |
| Dataset filters/index builders | include, pending confirmation | Exclude invalid records/windows before runtime | Filtering is not SampleTransform |
| Codec protocol and registry | include, pending confirmation | Decouples storage formats from dataset refs | Real codec catalog deferred |
| Real dataset adapters | defer | Scope control and fixture constraints | Use synthetic adapters first |

## Confirmed Functionality And Behavior

Included functionality:

- Pending maintainer confirmation. Proposed scope includes dataset refs, record refs, field refs, temporal index slices, field views, index items, sample specs/builders, filters, codec contracts, registry, and synthetic fixtures.

User-visible behavior:

- Pending maintainer confirmation. Users can scan or construct references, build indexes of lazy field views, and load Samples only through SampleBuilder and codecs.

Agent-visible behavior:

- Pending maintainer confirmation. Future agents should not place formatting, augmentation, or learning logic in IndexItems.

Default behavior:

- Pending maintainer confirmation. Lazy by default; strict slice support; no silent full-load fallback; no loaded data in refs.

Failure behavior and diagnostics:

- Pending maintainer confirmation. Missing fields, unsupported slices, slice bounds, codec resolution, schema mismatch, and unexpected layout fail loudly.

Explicit deferrals:

- Pending maintainer confirmation. Real codec catalog, real datasets, spatial/time slices, and multi-member IndexItems are deferred.

Out-of-scope behavior:

- Pending maintainer confirmation. Runtime transforms, materialization exporters, learners, metrics, and analysis.

## Context Compaction Or Reset Checkpoint

- Checkpoint status: not reached
- Notes path: `docs/implementation/dataset-io-index-core/planning-notes.md`
- Resume instruction: After functionality and behavior are confirmed, compact or reset context, then resume with `.codex/prompts/stage-1-planning-notes-resume.md` and reload this planning notes file before design-decision review.
- Functionality or behavior reopened after checkpoint: none

## Design-Decision Review Queue

| Decision | Why it matters | User feedback needed | Status |
| --- | --- | --- | --- |
| DatasetRef relationship to loom manifests | Avoids duplicate generic manifest mechanics | Confirm wrap/reuse strategy | draft |
| FieldRef contents and serialization | Controls portability and reproducibility | Confirm `ref`, codec, selector, schema, metadata fields | draft |
| TemporalIndexSlice semantics | Affects all codec slicing behavior | Confirm index-based half-open field-native semantics | draft |
| IndexItem scope | Prevents learning/formatting leakage into indexes | Confirm lazy IO-only scope | draft |
| Filtering locations | Affects IO cost and data exclusion traceability | Confirm record/field/index filters | draft |
| SampleBuilder validation order | Affects diagnostics and safety | Confirm strict validation before/while loading | draft |
| Codec capabilities and fallbacks | Prevents hidden scientific errors | Confirm no silent fallback behavior | draft |
| Synthetic versus real reference implementations | Affects validation realism and scope | Confirm fixture-first approach | draft |

## Design Decisions

| Decision | Selected approach | User feedback | Alternatives rejected | Rationale | Maintainability impact | Extensibility and expansion impact | Validation/documentation obligation | Debt and revisit trigger |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| None confirmed yet | Pending review | Pending maintainer feedback | Pending review | Stage 1 has not reached design-decision review | Avoids premature IO API lock-in | Keeps dataset extension flexible | Review required | Revisit after behavior confirmation |

## Practical Design Notes

Public API or documentation surface:

- Proposed contracts: `DatasetRef`, `RecordRef`, `FieldRef`, `TemporalIndexSlice`, `FieldView`, `IndexItem`, `SampleSpec`, `SampleBuilder`, `DatasetAdapter`, `FieldCodec`, `CodecRegistry`, and filters.

Workflow and artifact surface:

- Dataset stages can later scan, validate, build manifests/views, and build indexes through these APIs.

Failure modes and diagnostics:

- Missing fields, unsupported slices, out-of-bounds slices, missing codecs, schema mismatch, invalid selector, and loaded-data-in-ref violations.

Extension points and flexibility boundaries:

- New datasets add FieldSpecs and FieldRefs; new storage formats add codecs.

Maintainability assessment:

- Separating refs/views/indexes from transforms keeps dataset IO predictable and testable.

Extensibility assessment:

- Arbitrary logical fields allow future modalities without changing the dataset core.

Accepted debt:

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| None accepted yet | Design review has not started | Confirm during design-decision review |

## Phase Sketch

### Phase 1 - Reference And Lazy IO Contracts

Goal:

- Implement serializable dataset references and lazy loading through synthetic codecs.

Scope:

- Refs, slices, views, index items, sample spec/builder, filters, codec protocol/registry, synthetic fixtures.

Out of scope:

- Production codecs, real datasets, transforms, and materialization.

Acceptance criteria:

- Synthetic DatasetRef to IndexItem to SampleBuilder flow works and fails loudly on contract violations.

Test expectations:

- Package: import checks.
- Unit: refs, slices, fields, codecs, builder validation.
- Contract: no loaded data in refs/indexes; no silent slice fallback.
- Integration: synthetic scan/index/load.
- E2E: tiny synthetic lazy-loading flow.
- Opt-in: none initially.

Design impact:

- Locks dataset and IO contracts for later packages.

Future compatibility:

- Leaves room for real codecs, datasets, and new slice types.

Reviewability:

- API-heavy; should be scoped tightly.

## Open Questions

| Question | Affects | Current default | Status |
| --- | --- | --- | --- |
| Should a minimal filesystem resource ref be defined in `rphys` if `loom` is not ready? | Loom boundary and implementation | Prefer reuse/wrap loom resource refs | open |
| Should any real lightweight codec be included as a reference? | Validation realism | Use synthetic codec first | open |
| Should probing happen during scan by default? | IO cost and metadata quality | No eager probing unless explicit | open |

## Handoff Notes

Master-plan draft inputs:

- `docs/rphys_architecture_plan_v3.md` sections 16-20 and 36-38.
- Accepted runtime core contracts if already available.

Quality-gate risks:

- Coupling to incomplete `loom` manifest/resource contracts.
- Scope creep into real datasets/codecs.
- Hidden IO or fallback behavior.

Assumptions to carry forward:

- Runtime field core exists or is planned before this package.
