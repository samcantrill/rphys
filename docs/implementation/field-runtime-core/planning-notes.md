# Stage 1 Planning Notes: Field Runtime Core

## Metadata

- Roadmap slug: `field-runtime-core`
- Source context:
  - `docs/rphys_architecture_plan_v3.md`
  - `docs/implementation/field-centric-architecture-scaffold/planning-notes.md`
  - `docs/roadmap/index.md`
- Planning notes status: draft
- Current discussion stage: roadmap framing
- Related roadmap row: `Field runtime core`
- Blockers:
  - Split boundaries have not been confirmed by the maintainer.
  - Runtime behavior has not been confirmed.
  - Design-decision review has not started.

## Stage Gates

| Stage | Status | Locked decisions | Defaults | Open questions | Next focus |
| --- | --- | --- | --- | --- | --- |
| Roadmap framing | draft | Broad architecture is split; this package owns runtime field containers | Data layer before dataset IO and transforms | Should this depend on the public architecture package first? | Confirm package order |
| Intent discovery | draft | None yet | Prioritize stable runtime API for every later package | How rich should initial typed data objects be? | Clarify first user workflows |
| Capability brainstorming | draft | None yet | Include keys, specs, values, Samples, Batches, mutability, collation | Which modality objects are initial versus documented placeholders? | Mark include/defer |
| Functionality and behavior confirmation | not started | None yet | Mutable Samples, strict collation, explicit metadata | None yet | Confirm behavior |
| Context compaction/reset checkpoint | not started | None yet | Stop with resume instruction if direct compaction is unavailable | None | Record checkpoint |
| Design-decision review | not started | None yet | Review queue below | None yet | Review decisions |
| Phase shaping | not started | None yet | Keep core focused and test-heavy | None yet | Sketch phases |
| Handoff | not started | None yet | Carry accepted runtime contracts into dataset/transform packages | None yet | Prepare Stage 2 inputs |

## Context Extraction

Baseline outcome:

- Implement the field-centric runtime model used by all later dataset, transform, training, and evaluation code.

Constraints:

- Video is a standard field, not a privileged special case.
- Field metadata must capture scientific meaning where needed.
- Samples are mutable by default for hot-path efficiency.
- Batch should expose the same field access API as Sample.
- Collation must be field-level and explicit.

Deferred or out-of-scope ideas:

- Dataset refs and lazy IO.
- Concrete codecs.
- Runtime transform pipelines.
- Full modality library depth.
- Learning/evaluation behavior.

Scientific workflow obligations:

- Runtime objects must document shapes, units, dtypes, device behavior, temporal axes, coordinate frames, and failure behavior.
- Collation must not silently pad, truncate, drop fields, or accept missing fields unless policy permits it.

## User Intent

Target audience:

- Developers implementing core `rphys` packages.
- Extension authors adding new fields and data objects.

User-visible outcome:

- Stable field containers and Sample/Batch APIs for downstream code.

Success criteria:

- `DataKey`, `FieldSpec`, `FieldValue`, `Sample`, `Batch`, data object base, and collation policy behavior are documented and tested.
- Samples can hold arbitrary fields.
- Batch access mirrors Sample access.
- Mutability and copy rules are explicit.

Non-goals:

- Loading files.
- Scanning datasets.
- Running transforms or training loops.

Operational constraints:

- Keep core imports lightweight and avoid mandatory torch dependency unless accepted.

## Brainstormed Capabilities

| Capability | Decision | Rationale | Notes |
| --- | --- | --- | --- |
| `DataKey` | include, pending confirmation | Stable logical field identity | Grammar reviewed in public architecture or here |
| `FieldSpec` | include, pending confirmation | Declares meaning and metadata expectations | Used by datasets and contracts |
| `FieldValue` | include, pending confirmation | Separates payload from field metadata | Wraps typed or custom payloads |
| `DataObjectBase` | include, pending confirmation | Standard validation, tensor traversal, device movement, collation hooks | Torch dependency question remains |
| Standard modality object skeletons | maybe | Useful for docs and tests | Full implementations can be deferred |
| `Sample` | include, pending confirmation | Central mutable runtime container | `Sample -> Sample` transforms depend on it |
| `Batch` | include, pending confirmation | Same field API for batched data | Inheritance undecided |
| Mutability rules | include, pending confirmation | Avoids hidden copy behavior | Branching requires explicit copy |
| Field-level collation | include, pending confirmation | Prevents ambiguous shape/missing handling | Exact policy list can start small |

## Confirmed Functionality And Behavior

Included functionality:

- Pending maintainer confirmation. Proposed scope includes runtime keys/specs/values, data object base, Sample/Batch API, metadata rules, mutability semantics, and collation policy hooks.

User-visible behavior:

- Pending maintainer confirmation. Users access fields by key, require typed payloads explicitly, mutate Samples intentionally, and get deterministic collation errors when policies are absent.

Agent-visible behavior:

- Pending maintainer confirmation. Later agents should treat this package as the runtime contract source.

Default behavior:

- Pending maintainer confirmation. Samples are mutable; fields are arbitrary; collation is strict; metadata remains explicit and deterministic.

Failure behavior and diagnostics:

- Pending maintainer confirmation. Missing fields, wrong payload type, schema mismatch, collation ambiguity, and invalid metadata fail loudly.

Explicit deferrals:

- Pending maintainer confirmation. Full modality implementations, heavy tensor backend integration, and dataset IO are deferred.

Out-of-scope behavior:

- Pending maintainer confirmation. Dataset references, codecs, transforms, methods, losses, metrics, and stages.

## Context Compaction Or Reset Checkpoint

- Checkpoint status: not reached
- Notes path: `docs/implementation/field-runtime-core/planning-notes.md`
- Resume instruction: After functionality and behavior are confirmed, compact or reset context, then resume with `.codex/prompts/stage-1-planning-notes-resume.md` and reload this planning notes file before design-decision review.
- Functionality or behavior reopened after checkpoint: none

## Design-Decision Review Queue

| Decision | Why it matters | User feedback needed | Status |
| --- | --- | --- | --- |
| `DataKey` grammar ownership | Affects every field and extension | Confirm whether grammar is locked here | draft |
| Minimum `FieldSpec` fields | Balances scientific clarity against early burden | Confirm required versus optional metadata | draft |
| Data object base dependency model | Controls torch/lightweight core boundary | Confirm whether tensor traversal is backend-agnostic initially | draft |
| Sample mutability default | Affects transform behavior and debugging | Confirm mutable default and copy rules | draft |
| Batch implementation style | Affects type clarity and code reuse | Choose subclassing or same API without inheritance | draft |
| Initial collation policies | Affects training data behavior | Confirm strict default and first policies | draft |
| Metadata collation behavior | Affects reporting and reproducibility | Confirm list-based deterministic default | draft |

## Design Decisions

| Decision | Selected approach | User feedback | Alternatives rejected | Rationale | Maintainability impact | Extensibility and expansion impact | Validation/documentation obligation | Debt and revisit trigger |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| None confirmed yet | Pending review | Pending maintainer feedback | Pending review | Stage 1 has not reached design-decision review | Avoids premature runtime API lock-in | Keeps field model adaptable | Review required | Revisit after behavior confirmation |

## Practical Design Notes

Public API or documentation surface:

- Proposed public contracts: `DataKey`, `FieldSpec`, `FieldValue`, `DataObjectBase`, `Sample`, `Batch`, `CollatePolicy`, `SampleContract`, and modality data object names.

Workflow and artifact surface:

- None directly; these are runtime objects consumed by later stages and pipelines.

Failure modes and diagnostics:

- Missing fields, wrong types, schema mismatch, invalid metadata, and collation errors.

Extension points and flexibility boundaries:

- Users should add custom fields without editing `Sample`.

Maintainability assessment:

- A small runtime core reduces coupling across datasets, transforms, methods, and metrics.

Extensibility assessment:

- Arbitrary fields and typed data objects allow new modalities and prediction types.

Accepted debt:

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| None accepted yet | Design review has not started | Confirm during design-decision review |

## Phase Sketch

### Phase 1 - Runtime Field Containers

Goal:

- Implement and test the runtime data core.

Scope:

- Keys, specs, field values, Sample, Batch, data object base, collation policies, metadata behavior.

Out of scope:

- IO, transforms, learning, and stages.

Acceptance criteria:

- Synthetic Samples and Batches can store, require, mutate, copy, and collate arbitrary fields with strict diagnostics.

Test expectations:

- Package: import checks.
- Unit: key/spec/value/sample/batch/collation tests.
- Contract: missing/wrong field and collation failure tests.
- Integration: synthetic multi-field batch.
- E2E: none.
- Opt-in: tensor backend tests if dependency accepted.

Design impact:

- Locks the runtime object model.

Future compatibility:

- Enables dataset, transform, and evaluation packages.

Reviewability:

- Focused API-heavy diff.

## Open Questions

| Question | Affects | Current default | Status |
| --- | --- | --- | --- |
| Should torch be optional for `DataObjectBase` from day one? | Dependencies and tests | Keep core backend-light | open |
| Which modality data objects need real implementations first? | Scope | Define names and minimal synthetic behavior | open |
| Should `Batch` inherit from `Sample`? | API and typing | Same API is required; inheritance undecided | open |

## Handoff Notes

Master-plan draft inputs:

- `docs/rphys_architecture_plan_v3.md` sections 8-15.
- Accepted decisions from this planning note.

Quality-gate risks:

- Runtime API churn affects all later packages.
- Collation policy scope can expand quickly.
- Optional backend dependencies can leak into core.

Assumptions to carry forward:

- Dataset/IO and transform packages depend on this package.
