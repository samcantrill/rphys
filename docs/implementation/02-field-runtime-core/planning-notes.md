# Stage 1 Planning Notes: Field Runtime Core

## Metadata

- Roadmap slug: `field-runtime-core`
- Source context:
  - `docs/rphys_architecture_plan_v3.md`
  - `docs/implementation/00-field-centric-architecture-scaffold/planning-notes.md`
  - `docs/roadmap/index.md`
- Planning notes status: accepted for Stage 2
- Current discussion stage: Stage 3 Phase 1 committed; pre-submit blocker gate pending
- Related roadmap row: `Field runtime core`
- Blockers:
  - None. Pre-submit gate remains before PR creation.

## Stage Gates

| Stage | Status | Locked decisions | Defaults | Open questions | Next focus |
| --- | --- | --- | --- | --- | --- |
| Roadmap framing | accepted | This package owns loaded runtime field containers; IO/dataset/transform behavior is deferred | Data layer before dataset IO and transforms | None | Carry boundary into Stage 2 quality gate |
| Intent discovery | accepted | Prioritize stable runtime API for every later package | Keep the initial API narrow and strict | None | Carry accepted intent into implementation plan |
| Capability brainstorming | accepted | Include keys, specs, values, Samples, Batches, contracts, backend-light data hooks, explicit list collation | Defer concrete modality objects and backend-specific stack/pad behavior | None | Preserve deferrals |
| Functionality and behavior confirmation | accepted | Mutable Samples, explicit shallow/deep copy, strict absent-policy collation failure, minimal FieldSpec | Fail loudly for ambiguity | None | Preserve accepted behavior in master plan |
| Context compaction/reset checkpoint | accepted | This file and the master plan are the durable resume context | Reload these artifacts after interruption | None | Continue from master-plan gate status |
| Design-decision review | accepted | D1-D7 decisions documented in the master plan | Discuss only important/impactful/unclear decisions | None | Quality gate review |
| Phase shaping | accepted | Four sequential standard-pathway phases | Phase 1 uses xhigh where configurable | None | Confirm phase readiness |
| Handoff | accepted | Accepted runtime contracts move into Stage 3 after master-plan acceptance | Use one branch/worktree per phase | None | Phase 1 branch/worktree setup |

## Context Extraction

Baseline outcome:

- Implement the field-centric runtime model used by all later dataset, transform, training, and evaluation code.

Constraints:

- Video is a standard field, not a privileged special case.
- Field metadata must capture scientific meaning where needed, but the base `FieldSpec` should stay minimal until specialized specs or contracts need stricter semantics.
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

- Runtime docs must document payload wrapper semantics, dtype/device expectations for backend-agnostic hooks, explicit deferrals for shapes/units/axes/coordinate frames/sample rates, and failure behavior.
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
| `DataKey` | include, accepted | Stable logical field identity | `DataKey(str)`, lowercase ASCII dot-separated tokens, reserved namespaces, and `custom.<project>.<field...>` extension keys |
| `FieldSpec` | include, accepted | Declares broad field identity without pretending to model every modality | Minimal strict base: `key`, `data_type`, optional `schema`; no coordinate frame, temporal axis, units, layout, generic `runtime_type`, or `description` in Phase 1 |
| `FieldValue` | include, accepted | Separates payload from field metadata | Narrow wrapper: `value`, optional `schema`, shallow-copied `metadata`, optional `collate_policy`; no duplicated `data_type` |
| `DataObjectBase` | include, accepted | Standard validation, tensor traversal, and device movement hooks | Base remains dependency-free and duck-typed; optional torch submodule is allowed later only if import-gated |
| Standard modality object skeletons | defer | Avoids public placeholders and unused contracts | Future tensor/video/signal specs or data objects should land when concrete packages need them |
| `Sample` | include, accepted | Central mutable runtime container | Domain container, not `MutableMapping`; `field` returns wrapper, `get`/`require` return payload |
| `Batch` | include, accepted | Same field API for batched data | Subclass `Sample` initially; revisit if semantics diverge |
| Mutability rules | include, accepted | Avoids hidden copy behavior | Mutation is explicit; shallow/deep copy are explicit; branching should deep-copy |
| Field-level collation | include, accepted | Prevents ambiguous shape/missing handling | Only explicit `LIST` initially; absent policy, stack, padding, custom, missing-field, and object-delegated policies fail |

## Confirmed Functionality And Behavior

Included functionality:

- Implement loaded runtime keys/specs/values, backend-agnostic data object hooks, `Sample`/`Batch` API, minimal explicit `SampleContract`, and strict explicit `LIST` collation.

User-visible behavior:

- Users access fields by key, wrap payloads in `FieldValue`, mutate Samples intentionally, use explicit shallow/deep copies, require payloads explicitly, and get deterministic errors when collation policies are absent.

Agent-visible behavior:

- Later agents should treat this package as the runtime contract source for field access, sample mutation, sample contracts, and batching.

Default behavior:

- Samples are mutable; fields are arbitrary under validated keys; `FieldSpec` is minimal; collation is strict; metadata remains explicit and deterministic.

Failure behavior and diagnostics:

- Invalid keys, unknown non-custom namespaces, missing fields, wrong payload type, schema mismatch, absent collation policies, unsupported collation, and padding/stack ambiguity fail loudly.

Explicit deferrals:

- Full modality implementations, specialized tensor/video/signal specs, heavy tensor backend integration, object-delegated collation, stack/padding behavior, and dataset IO are deferred.

Out-of-scope behavior:

- Dataset references, codecs, sample builders, transforms, methods, losses, metrics, evaluation, recipes, and stages.

## Context Compaction Or Reset Checkpoint

- Checkpoint status: not reached
- Notes path: `docs/implementation/02-field-runtime-core/planning-notes.md`
- Resume instruction: After functionality and behavior are confirmed, compact or reset context, then resume with `.codex/prompts/stage-1-planning-notes-resume.md` and reload this planning notes file before design-decision review.
- Functionality or behavior reopened after checkpoint: none

## Design-Decision Review Queue

| Decision | Why it matters | User feedback needed | Status |
| --- | --- | --- | --- |
| `DataKey` grammar ownership | Affects every field and extension | Confirm whether grammar is locked here | accepted |
| Minimum `FieldSpec` fields | Balances scientific clarity against early burden | Confirm required versus optional metadata | accepted: minimal `key`, `data_type`, optional `schema` |
| Data object base dependency model | Controls torch/lightweight core boundary | Confirm whether tensor traversal is backend-agnostic initially | accepted: dependency-free base, optional import-gated torch submodule later |
| Sample mutability default | Affects transform behavior and debugging | Confirm mutable default and copy rules | accepted |
| Batch implementation style | Affects type clarity and code reuse | Choose subclassing or same API without inheritance | accepted: subclass `Sample` initially |
| Initial collation policies | Affects training data behavior | Confirm strict default and first policies | accepted: explicit `LIST` only |
| Metadata collation behavior | Affects reporting and reproducibility | Confirm list-based deterministic default | accepted |

## Design Decisions

| Decision | Selected approach | User feedback | Alternatives rejected | Rationale | Maintainability impact | Extensibility and expansion impact | Validation/documentation obligation | Debt and revisit trigger |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Runtime ownership boundary | `rphys.data` owns loaded runtime contracts only | Approved | Putting lazy `FieldRef`/views here | Preserves `rphys.io` lazy-reference boundary | Keeps IO and runtime mutation independent | Later IO builds on runtime containers | Docs/import tests must show boundary | Revisit only if public architecture boundary changes |
| `DataKey` grammar | `DataKey(str)` with reserved namespaces and `custom.<project>.<field...>` | Approved | Plain strings only; registry-first keys | Ergonomic mapping key with validation | Stable field identity | Custom fields avoid core edits | Key parsing and invalid-key tests | Revisit before broad standard key catalog |
| Base `FieldSpec` | `key`, `data_type`, optional `schema` only | Approved | Rich metadata schema; generic `runtime_type`; `description` | Avoids unused data-specific contract fields | Small stable base API | Specialized specs/contracts can add concrete semantics later | FieldSpec tests and docs for deferrals | Revisit when concrete modality specs land |
| `FieldValue` | `value`, optional `schema`, shallow-copied `metadata`, optional `collate_policy` | Approved | Raw payloads only; duplicate data type | Preserves payload/metadata separation without drift | Generic wrapper remains small | Data-specific validation can be layered later | Wrapping/copy/schema/policy tests | Revisit if serialization contract is added |
| `Sample`/`Batch` API | Domain container, explicit mutation/copy, `Batch(Sample)` initially | Approved | `MutableMapping`, immutable sample, separate batch API | Keeps wrapper/payload access explicit | Downstream code gets one access API | Can revisit batch composition if semantics diverge | Mutation/copy/access/error tests | Revisit before broad downstream use if subclassing hurts |
| `SampleContract` | Explicit-call validation of required/optional fields, payload type, and schema | Approved | Automatic validation; rich scientific schema | Useful shared runtime check without surprising mutation | Narrow contract avoids dataset schema duplication | Later contracts can add shape/unit/axis checks | Explicit-call and diagnostics tests | Revisit when specialized contracts exist |
| Collation | Explicit `LIST` only; absent policy fails; exact field sets required | Approved | Default list; early stack/pad/custom/object policies | Prevents silent scientific changes | Backend-free and strict | Richer collation can be added by accepted plan | Empty/inconsistent/absent/unsupported/list metadata tests | Revisit when concrete backend objects exist |

## Practical Design Notes

Public API or documentation surface:

- Proposed public contracts: `DataKey`, `FieldSpec`, `FieldValue`, `DataObjectBase`, `Sample`, `Batch`, `CollatePolicy`, `CollateContext`, `collate_samples`, and `SampleContract`.

Workflow and artifact surface:

- None directly; these are runtime objects consumed by later stages and pipelines.

Failure modes and diagnostics:

- Invalid keys, missing fields, wrong types, schema mismatch, absent collation policy, unsupported policy, and collation ambiguity.

Extension points and flexibility boundaries:

- Users should add custom fields without editing `Sample`.

Maintainability assessment:

- A small runtime core reduces coupling across datasets, transforms, methods, and metrics.

Extensibility assessment:

- Arbitrary fields and typed data objects allow new modalities and prediction types.

Accepted debt:

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Standard key catalog remains small | Avoids freezing standard field names before concrete packages need them | A downstream package needs stable cross-package field constants |
| Full modality object library is deferred | Avoids public placeholders and backend-specific contracts without implementation pressure | Tensor/video/signal package work needs concrete object behavior |
| Stack, padding, custom, missing-field, and object-delegated collation are deferred | Prevents silent scientific changes and backend leakage in the base runtime | Concrete backend objects or training/evaluation batches require richer collation |
| `Batch` subclasses `Sample` initially | Keeps the first access API small and identical | Batch semantics diverge from sample semantics before broad downstream use |

## Phase Sketch

### Phase 1 - Keys, Fields, And Runtime Docs

Goal:

- Implement and test field identity plus narrow loaded field wrappers.

Scope:

- `DataKey`, minimal `FieldSpec`, narrow `FieldValue`, `CollatePolicy.LIST`, public exports, and runtime docs.

Out of scope:

- `Sample`, `Batch`, `DataObjectBase`, `CollateContext`, `collate_samples`, IO, transforms, learning, and stages.

Acceptance criteria:

- Keys validate deterministically, field wrappers preserve accepted narrow metadata, and docs state the runtime/IO boundary.

Test expectations:

- Package: import checks.
- Unit: key/spec/value tests.
- Contract: no heavy imports and no lazy IO concepts exported from `rphys.data`.
- Integration: none.
- E2E: none.
- Opt-in: none.

Design impact:

- Locks the field naming and wrapper baseline.

Future compatibility:

- Enables dataset schemas and transforms to refer to shared key/spec/value types.

Reviewability:

- Focused API-heavy diff; use xhigh reasoning where configurable.

### Later Phases

- Phase 2: implement mutable `Sample`/`Batch` containers, explicit mutation, explicit shallow/deep copy, and shared access behavior.
- Phase 3: implement backend-agnostic `DataObjectBase`, explicit-call `SampleContract`, `CollateContext`, `collate_samples`, deterministic metadata lists, and explicit `LIST` collation.
- Phase 4: reconcile public docs, import tests, dependency-boundary checks, and implementation-plan evidence.

## Open Questions

| Question | Affects | Current default | Status |
| --- | --- | --- | --- |
| Should torch be optional for `DataObjectBase` from day one? | Dependencies and tests | Keep base runtime dependency-free | resolved: optional import-gated submodule allowed later only if needed |
| Which modality data objects need real implementations first? | Scope | Defer concrete modality objects | deferred to later package plans |
| Should `Batch` inherit from `Sample`? | API and typing | Same API is required | resolved: subclass `Sample` initially |
| Are there blocking design questions before Stage 2 quality gate? | Master-plan acceptance | No unresolved design blocker after D1-D7 | resolved; formal quality gate still pending |

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
