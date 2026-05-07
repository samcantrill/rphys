# Stage 1 Planning Notes: Public Architecture Contracts

## Metadata

- Roadmap slug: `public-architecture-contracts`
- Source context:
  - `docs/rphys_architecture_plan_v3.md`
  - `docs/implementation/field-centric-architecture-scaffold/planning-notes.md`
  - `AGENTS.md`
  - `.codex/workflows/stage-1-roadmap.md`
  - `.codex/templates/stage-1-planning-notes.md`
  - `docs/roadmap/index.md`
- Planning notes status: accepted
- Current discussion stage: handoff complete
- Related roadmap row: `Public architecture contracts`
- Blockers:
  - Split boundaries are confirmed as the working Stage 1 roadmap map; individual package-size risk remains under review.
  - Functionality and behavior are confirmed.
  - Context compaction/reset checkpoint is recorded; design-decision review must resume after reset.
  - Design-decision review is complete.
  - Maintainer explicitly accepted this Stage 1 work package.

## Stage Gates

| Stage | Status | Locked decisions | Defaults | Open questions | Next focus |
| --- | --- | --- | --- | --- | --- |
| Roadmap framing | completed | Six-package split confirmed as the working Stage 1 roadmap map; this is the first package to drive through Stage 1 | Revisit package subdivision only if a package's decision queue is too broad | None for this gate | Intent discovery |
| Intent discovery | completed | Stable public API is the highest project priority; design should avoid lock-in, restrictive behavior, and future refactor pain; lock modules before signatures; use stable/provisional/private API labels | Serve maintainers, downstream extension authors, and future agents | None for this gate | Capability brainstorming |
| Capability brainstorming | completed | Stable module surface starts with `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`; `methods`/`training`/`losses` follow later; `evaluation` follows after that; `analysis`/`recipes`/`stages` are future/provisional; central `rphys.errors` hierarchy | Thin supporting skeleton may follow API design as documentation/validation, but should not drive the API | How much package skeleton should be implemented after API design? | Functionality and behavior confirmation |
| Functionality and behavior confirmation | completed | Public architecture contracts is API-design/docs-first; first stable module wave is `data`/`io`/`datasets`/`transforms` plus `errors`; later modules stay future/provisional; signatures deferred; thin skeleton only after API design; generic infrastructure belongs to `loom` | API-design-first; fail loudly; do not duplicate loom; keep optional dependencies out of core | None for this gate | Context compaction/reset checkpoint |
| Context compaction/reset checkpoint | completed | Functionality and behavior checkpoint recorded; reset/resume required before design-decision review | Resume from this notes file with `.codex/prompts/stage-1-planning-notes-resume.md` | None | Design-decision review after reset |
| Design-decision review | completed | Decision queue validated; strict one-way `loom`/`rphys` boundary confirmed; first-wave stable inventory confirmed; future/provisional module map confirmed; code-backed contract documentation confirmed; thin skeleton depth confirmed; `RemotePhysError` naming confirmed; registry, `_target_`, optional dependency, and API-label obligations confirmed | Keep confirmed design decisions as Stage 2 inputs | None | Phase shaping |
| Phase shaping | completed | One small Stage 2 phase confirmed: Boundary And Contract Skeleton | Keep implementation narrow and structural | None | Handoff |
| Handoff | completed | Maintainer accepted `Public architecture contracts` as a Stage 1 work package | Use these notes as the Stage 2 master-plan input | None | Stage 2 master-plan drafting |

## Context Extraction

Baseline outcome:

- Establish `rphys` as a domain-specific remote physiological measurement library layered on `loom`.
- Document the package ownership rules, public extension contracts, stable import surface, error families, registry policy, dependency boundaries, and scaffold layout.

Constraints:

- `loom` owns generic experiment execution, config composition, recipe expansion, run stores, artifact stores, executors, resume logic, and generic artifact/resource mechanics.
- `rphys` owns remote physiological measurement semantics and concrete domain components.
- Public contracts must be documented before downstream use.
- Optional dependencies must not leak into the lightweight core.

Deferred or out-of-scope ideas:

- Concrete dataset adapters, codecs, transforms, models, learners, metrics, and exporters.
- Full plugin discovery through Python entry points.
- Deep scientific algorithm implementations.

Scientific workflow obligations:

- Cross-cutting docs must require units, shapes, dtypes, coordinate frames, sampling rates, alignment assumptions, leakage risks, failure behavior, and validation tests for scientific components.

## User Intent

Target audience:

- Maintainers and Stage 2/3 implementation agents defining the initial scaffold boundaries.
- Downstream researchers deciding how to extend `rphys`.

User-visible outcome:

- A documented architecture boundary and package skeleton that makes extension points clear without promising deep implementation coverage.

Success criteria:

- The `loom`/`rphys` boundary is explicit.
- Public contract names and modules are listed.
- Registry and `_target_` extension rules are clear.
- Dependency boundaries and optional extras are documented.
- Generic infrastructure is not reimplemented in `rphys`.

Non-goals:

- Implementing runtime field containers.
- Implementing dataset scanning or IO.
- Implementing learning/evaluation behavior.

Operational constraints:

- Keep this package small enough to unblock later packages without deciding their internal implementations.
- Treat stable public API design as the main maintainability and extensibility risk.
- Use this package to reason across the rest of the project before implementation hardens API names, module boundaries, or extension paths.
- Keep any supporting code skeleton very thin and downstream of the API design. The skeleton may act as executable documentation and import-boundary validation, but it should not force premature API lock-in.
- Avoid exposing unimplemented placeholders as stable behavior. If a name exists before implementation, it should be documented as provisional or should raise an explicit `NotImplementedError`/equivalent when called.

## Stage Readbacks

### Roadmap Framing Split Review

Maintainer feedback:

- The broad v3 architecture should be split before acceptance.
- There is concern that some split work packages are still quite large.
- `Public architecture contracts` should be the first package reviewed because stable public API is the most important part of the project.
- API design should be done with the rest of the project in mind to avoid major refactoring and long-term maintenance problems.
- The six-package split is acceptable and should be followed.
- This package should focus heavily on API design and structure to avoid lock-in, limitation, restrictive behavior, and refactor pain later.
- A very thin supporting skeleton can come after API design and can function partly as documentation.
- API stability tiers may help development, but unimplemented behavior can also be represented with explicit `NotImplementedError` placeholders or refactored as needed.

Current interpretation:

- The six-package split is confirmed as the working Stage 1 map, not final proof that each package is the right Stage 2 size.
- The first package should be treated as a design-governance package: it must define stable public API principles, ownership boundaries, extension rules, and compatibility expectations before lower-level packages harden contracts.
- The main size-risk candidates are `Runtime transforms and materialization` and `Learning evaluation core`; these may need to split later into runtime/export and method/evaluation packages respectively.
- `Field runtime core` and `Dataset IO and index core` are also broad, but their concepts are tightly coupled enough that splitting them too early could make the API less coherent.
- API tiers and `NotImplementedError` solve different problems: tiers communicate compatibility promises, while `NotImplementedError` communicates runtime absence. The recommended default is to use explicit public-surface labels in documentation and reserve `NotImplementedError` for intentionally importable skeleton members that should not be used yet.

### Public API Scope Review

Maintainer feedback:

- Public API design should lock module ownership before method signatures.
- Method signatures should be reviewed later, package by package.
- `analysis`, `recipes`, and `stages` should remain future/provisional until the core data, IO, transform, and evaluation APIs are ready.
- Maintainer requested a recommendation on API stability tiers.
- Maintainer accepted the three-label API policy: stable, provisional, and private/internal.
- Initial stable top-level module areas should be cut down to `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`.
- `rphys.methods`, `rphys.training`, and `rphys.losses` should come after the first stable core.
- `rphys.evaluation` should come after the learning-related modules.
- A central `rphys.errors` module with broad base errors is preferred; package-specific errors can be introduced later under that hierarchy.

Current interpretation:

- The first contract inventory should name top-level modules, ownership boundaries, and key public contract names, but should avoid freezing full call signatures.
- `analysis`, `recipes`, and `stages` should be documented as expected future public areas, not stable first-pass APIs.
- Accepted API policy: stable documented contracts only; provisional surfaces allowed when clearly labeled; private/internal surfaces carry no compatibility promise; intentionally importable skeleton members may raise `NotImplementedError` but should not be labeled stable until behavior exists.
- Initial stable API design should focus on the data/IO/dataset/transform spine. This reduces public surface area while preserving the architecture needed by most later packages.
- Methods/training/losses and evaluation should be designed with the full architecture in mind, but not treated as initial stable module surfaces in this work package.
- `rphys.errors` should exist as a stable central module early because consistent diagnostics affect all later packages.

### Functionality And Behavior Confirmation

Maintainer feedback:

- Confirmed the proposed behavior for `Public architecture contracts`.

Confirmed behavior:

- This package produces API design docs and module ownership, not full implementations.
- Stable first-wave modules are `rphys.data`, `rphys.io`, `rphys.datasets`, `rphys.transforms`, plus central `rphys.errors`.
- Learning, evaluation, analysis, recipes, and stages are documented as future/provisional until their dependencies are ready.
- Method signatures are deferred to the owning packages.
- A thin skeleton may be added after API design, only to validate imports and act as executable documentation.
- Unimplemented skeleton symbols must be provisional and raise explicit `NotImplementedError` if called.
- Generic experiment infrastructure remains out of scope and belongs to `loom`.

### Design-Decision Queue Validation

Maintainer feedback:

- The proposed design-decision review queue looks good.

Current interpretation:

- The review queue is complete enough to proceed decision-by-decision.
- The queue should include a separate documentation-as-contract decision because API design and structure are the main deliverables for this package.
- The error decision should distinguish taxonomy placement from implementation depth, so the package can define cross-cutting names without over-implementing behavior that belongs to later packages.

### Design-Decision Review Round 1

Maintainer feedback:

- Confirmed the strict `loom`/`rphys` ownership boundary.
- Confirmed the first-wave public contract inventory.
- Confirmed that `FieldRef`, `TemporalIndexSlice`, and `FieldView` should live under `rphys.io`, not `rphys.data`.
- Confirmed the future/provisional module map.
- Confirmed that `rphys.ops`, `rphys.models`, and `rphys.testing` should not be part of the initial stable public contract.

Current interpretation:

- `rphys` depends on `loom`; `loom` must not depend on `rphys`.
- `loom` owns generic workflow, config, `_target_`, recipe, DAG, stage execution, store, executor, resume, fingerprint, locking, and generic resource/artifact/record/manifest mechanics.
- `rphys` owns remote-phys domain semantics, domain object contracts, field-aware IO, dataset/index concepts, transforms, materialization/export semantics, and later method/training/loss/evaluation contracts.
- Concrete `rphys` stages and recipes may exist later, but they are thin domain wrappers/config definitions executed by `loom`, not generic infrastructure.
- First-wave stable contracts are limited to `rphys.data`, `rphys.io`, `rphys.datasets`, `rphys.transforms`, and `rphys.errors`.
- Later learning and evaluation surfaces remain documented but provisional until their prerequisite contracts are mature.

### Design-Decision Review Round 2

Maintainer feedback:

- Contract documentation should not become a duplicate source of truth for API details once implementation exists.
- Code should be the contract after implementation; docs should support planning, implementation, deeper insight, discussion of functionality, behavior, policy, and artifact expectations.
- Development-facing contract docs are acceptable if they reference the actual code once implementation exists.
- Confirmed thin skeleton depth.
- Asked whether the root error name should avoid `RPhysError` or whether that is standard convention.

Current interpretation:

- Public contract documentation should define policy, ownership, stability labels, extension rules, and behavioral intent, while API reference detail should be generated from or point to implemented code once code exists.
- Stage 2 should avoid creating parallel hand-written API reference pages that duplicate class/function signatures.
- Thin skeleton means package/module homes, broad real error base classes, module docstrings, optional `__all__` inventories, import smoke tests, and dependency-boundary checks only.
- Broad placeholder classes for runtime, dataset, IO, or transform concepts should not be created in this package unless the owning package has accepted their behavior.
- The central root error should be named `RemotePhysError`, not `RPhysError`.
- Broad package-family errors should use the same readable prefix pattern, such as `RemotePhysDataError`.

### Design-Decision Review Round 3

Maintainer feedback:

- Confirmed the remaining registry, `_target_`, optional dependency, and API labeling recommendations as written.

Current interpretation:

- Registries should be used only where symbolic names are valuable, such as codec keys, built-in dataset names, standard field schemas, and later standard metric or recipe names.
- Custom transforms, methods, models, losses, metrics, dataset adapters, and similar extension objects should not require global registration by default.
- `_target_` import paths are the default user-extension mechanism, while the generic `_target_` instantiation engine belongs to `loom`.
- The lightweight core should avoid heavy optional dependencies on import. Optional stacks such as video, signal, torch, training, analysis, and dev dependencies should be documented as extras, but exact package selections can be finalized during implementation planning.
- API labels require practical obligations: stable means documented, tested, importable, and compatibility-preserving; provisional may change before stabilization; private/internal has no compatibility promise.
- Skeleton names that raise `NotImplementedError` must be provisional, never stable.

### Phase Shaping

Maintainer feedback:

- Confirmed the recommended one-phase shape.

Current interpretation:

- Stage 2 should plan a single small implementation phase: Boundary And Contract Skeleton.
- The phase should cover code-backed public contract docs/policy, top-level module homes for `data`, `io`, `datasets`, `transforms`, and `errors`, broad `RemotePhys*Error` classes, a thin import skeleton, import smoke tests, and dependency-boundary checks.
- The phase must not implement real `DataKey`, `Sample`, `DatasetRef`, `FieldRef`, transform behavior, codecs, adapters, method signatures, or broad placeholder classes.
- The package is now ready for handoff review and explicit maintainer acceptance.

### Handoff Acceptance

Maintainer feedback:

- Accepted.

Current interpretation:

- `Public architecture contracts` is accepted as a Stage 1 work package.
- The next workflow step is Stage 2 master-plan drafting with `.codex/workflows/stage-2-master-plan.md`, using these planning notes as the accepted source of scope, decisions, deferrals, and validation expectations.

## Brainstormed Capabilities

| Capability | Decision | Rationale | Notes |
| --- | --- | --- | --- |
| `loom`/`rphys` boundary | include, pending confirmation | Prevents duplicate generic infrastructure | Boundary must be documented before stages/recipes are planned |
| Package skeleton | include, pending confirmation | Gives later packages stable homes and executable documentation after API design | Should be thin and should avoid misleading empty public APIs |
| Initial stable module inventory | include | Sets first stable extension surface and reduces later refactor risk | Stable first wave: `rphys.data`, `rphys.io`, `rphys.datasets`, `rphys.transforms` |
| Later learning module inventory | defer | Learning APIs depend on stable field/data contracts | `rphys.methods`, `rphys.training`, and `rphys.losses` come after the first stable core |
| Later evaluation module inventory | defer | Evaluation depends on prediction/loss/method conventions | `rphys.evaluation` comes after learning-related modules |
| Error taxonomy | include | Cross-cutting diagnostics are useful early | Central `rphys.errors` with broad base errors; package-specific errors can be introduced later under that hierarchy |
| Registry policy | include, pending confirmation | Avoids forcing every extension through registration | Use registries for symbolic names only |
| `_target_` extension rule | include, pending confirmation | Supports experiment-local extension code | Must align with `loom` config behavior |
| Optional dependency policy | include, pending confirmation | Keeps core package lightweight | Extras can be refined later |
| Public API stability policy | include | Stable API is the highest project priority | Use stable/provisional/private labels; `NotImplementedError` is an implementation placeholder, not an API tier |
| `analysis`, `recipes`, and `stages` public areas | defer | These depend on core APIs being stable enough to avoid churn | Document as future/provisional until core data, IO, transform, and evaluation APIs are ready |
| Generic workflow infrastructure | out of scope | Belongs in `loom` | Only thin domain stages should live in `rphys` |

## Confirmed Functionality And Behavior

Included functionality:

- Confirmed. Scope includes API design and structure, boundary docs, module ownership, initial stable module inventory for `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`, future/provisional module inventory for later learning/evaluation/workflow areas, registry policy, dependency policy, central error-family inventory, extension-rule docs, and a very thin supporting skeleton only after API design is documented.

User-visible behavior:

- Confirmed. Users should see that the first stable API spine is data/IO/datasets/transforms plus central errors. Learning, evaluation, analysis, recipes, and stages are future/provisional until core contracts are ready. Private/internal surfaces carry no compatibility promise. Extension code should use documented contracts and `_target_` paths.

Agent-visible behavior:

- Confirmed. Future agents should use this package as the source for ownership boundaries and public API expectations. They must not start design-decision review without reloading these notes after reset/resume.

Default behavior:

- Confirmed. Default is API-design-first, lightweight core, explicit failures, symbolic registries only where useful, `_target_` import paths for user extensions, and skeleton code only where it validates the design.

Failure behavior and diagnostics:

- Confirmed. Cross-cutting errors should be named here through a central `rphys.errors` hierarchy, but detailed failure tests can live with the package that raises them. Unimplemented skeleton symbols must be provisional and raise explicit `NotImplementedError` if called.

Explicit deferrals:

- Confirmed. Concrete adapters, codecs, transform implementations, exporters, stable methods/training/losses APIs, stable evaluation APIs, broad implementation skeletons, stable `analysis`, stable `recipes`, and stable `stages` APIs are deferred to later work packages.

Out-of-scope behavior:

- Confirmed. Generic config, recipe expansion, DAG execution, run/artifact stores, executors, resume logic, and locking are out of scope and belong to `loom`.

## Context Compaction Or Reset Checkpoint

- Checkpoint status: recorded; direct context compaction is unavailable in this chat, so design-decision review must begin only after reset/resume.
- Notes path: `docs/implementation/public-architecture-contracts/planning-notes.md`
- Resume instruction: Reset or compact context, then resume with `.codex/prompts/stage-1-planning-notes-resume.md` and reload `docs/implementation/public-architecture-contracts/planning-notes.md` before beginning design-decision review. Treat confirmed functionality and behavior as stable unless the maintainer explicitly reopens them.
- Functionality or behavior reopened after checkpoint: none

## Design-Decision Review Queue

| Decision | Why it matters | User feedback needed | Status |
| --- | --- | --- | --- |
| Exact `loom`/`rphys` ownership boundary | Prevents infrastructure duplication and circular dependencies | Confirm exceptions and integration assumptions | confirmed in design review |
| Stable public contract inventory | Determines what downstream code may depend on | First stable wave confirmed as data/IO/datasets/transforms; method signatures deferred | confirmed in design review |
| Future/provisional public module map | Prevents premature lock-in while preserving architecture direction | Confirm later learning/evaluation/workflow modules as documented but not stable | confirmed in design review |
| Package skeleton depth | Affects churn and discoverability | Confirm thin post-design skeleton only where useful as executable documentation | confirmed in design review |
| Error taxonomy placement | Affects diagnostics consistency | Central `rphys.errors` preferred; package-specific errors may extend it later | confirmed in design review |
| Error taxonomy implementation depth | Controls how much behavior this package implements versus reserves for later packages | Confirm broad base classes here, detailed package errors later | confirmed in design review |
| Registry policy | Controls extension ergonomics | Confirm symbolic registries only | confirmed in design review |
| `_target_` extension policy | Controls downstream custom code path | Confirm import paths as default extension mechanism | confirmed in design review |
| Optional dependency boundaries | Keeps core lightweight | Confirm initial extras and import restrictions | confirmed in design review |
| API surface labeling strategy | Prevents accidental lock-in while allowing refactor of unimplemented names | Three-label strategy accepted; capture obligations during design review | confirmed in design review |
| Documentation-as-contract shape | Makes API promises findable and enforceable without freezing signatures too early | Confirm code-backed docs rather than duplicate API reference | confirmed in design review |

## Design Decisions

| Decision | Selected approach | User feedback | Alternatives rejected | Rationale | Maintainability impact | Extensibility and expansion impact | Validation/documentation obligation | Debt and revisit trigger |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| API surface labeling strategy | Use `stable`, `provisional`, and `private/internal` as API-surface labels; reserve `NotImplementedError` for intentionally importable skeleton members that are not usable yet | Maintainer accepted the three-label policy | Relying only on `NotImplementedError`; simple public/internal split | Labels communicate compatibility promises; `NotImplementedError` only communicates runtime absence | Reduces accidental lock-in while making public guarantees visible | Allows future design surfaces to be documented without freezing them as stable | Documentation must label public surfaces; skeleton members with `NotImplementedError` must not be marked stable until behavior is implemented and tested | Revisit if labels become too burdensome or users cannot tell which surfaces are safe to depend on |
| Exact `loom`/`rphys` ownership boundary | Keep a strict one-way dependency: `rphys` depends on `loom`; `loom` must not depend on `rphys`. `loom` owns generic workflow/config/execution infrastructure; `rphys` owns remote-phys domain semantics and thin domain stages/recipes | Maintainer agreed | Duplicating generic infrastructure in `rphys`; allowing `loom` to know about `rphys`; making `rphys` stages own execution mechanics | One-way ownership prevents circular dependencies and keeps the base library domain-focused | Reduces duplicate infrastructure and unclear ownership | Allows domain extensions to compose with `loom` without changing either project's internals | Boundary docs must list owned concepts and forbidden infrastructure; stale generic-infrastructure checks should guard against drift | Revisit if `loom` lacks a required generic primitive and the missing primitive cannot be added there |
| Stable public contract inventory | First-wave stable public contracts are limited to `rphys.data`, `rphys.io`, `rphys.datasets`, `rphys.transforms`, and `rphys.errors`; contract names are documented now, signatures are deferred to owning packages | Maintainer agreed | Freezing all v3 public modules now; freezing method signatures now; making `ops`, `models`, or `testing` stable in the first wave | Small stable spine protects downstream users while avoiding premature lock-in | Limits future compatibility burden to the modules needed by core data/IO/dataset/transform work | Provides stable homes for future adapters, codecs, datasets, and transforms | Docs must list contract names and explicitly defer signatures; import inventory checks can verify skeleton exports if implemented | Revisit when the owning package's Stage 1/2 plan is ready to lock signatures or add stable names |
| `FieldRef`/`FieldView` ownership | Put `FieldRef`, `TemporalIndexSlice`, and `FieldView` under `rphys.io` rather than `rphys.data` | Maintainer agreed | Treating lazy field references/views as `rphys.data` runtime containers | These concepts describe lazy access to external payloads, not in-memory field values | Keeps `rphys.data` focused on runtime containers and contracts | Keeps IO and dataset adapters extensible around lazy loading and codecs | Public docs must explain the conceptual distinction between runtime field values and lazy field views | Revisit if later implementation shows these objects need to be dependency-free data primitives |
| Future/provisional public module map | Document `rphys.methods`, `rphys.training`, `rphys.losses`, then `rphys.evaluation` as later public surfaces; keep `rphys.analysis`, `rphys.recipes`, and `rphys.stages` future/provisional; keep `rphys.ops`, `rphys.models`, and `rphys.testing` out of the initial stable public contract | Maintainer agreed | Making all v3 packages stable immediately; hiding later areas entirely | The project needs architectural direction without early compatibility promises | Avoids over-promising late-bound APIs before core contracts settle | Leaves room for learning/evaluation/workflow modules to grow coherently from the core | Docs must label later modules as future/provisional and point users to stable extension surfaces first | Revisit after methods/training/losses and evaluation packages complete their own Stage 1 design reviews |
| Code-backed public contract documentation | Use docs for policy, ownership, behavior, implementation guidance, artifact expectations, and deeper design discussion; once implementation exists, docs should reference the actual code/API reference rather than duplicating signatures | Maintainer clarified and accepted this direction | Treating planning docs as permanent API reference; duplicating signatures in docs and code | Code should become the authoritative contract after implementation, while docs explain why the contract exists and how to extend it | Reduces drift between docs and code | Lets user-facing docs remain useful without becoming stale parallel API definitions | Stage 2 should plan a public contract doc that links to code/API reference once available and keeps planning notes internal | Revisit if users cannot discover stable surfaces from generated/reference docs |
| Package skeleton depth | Create only a thin post-design skeleton: package/module homes, broad central errors, module docstrings, optional `__all__`, import smoke tests, and dependency-boundary checks; avoid broad placeholder classes for core contracts until owning packages design behavior | Maintainer agreed | Creating broad placeholder classes for `DataKey`, `Sample`, `DatasetRef`, transforms, and related contracts now; waiting for all packages before creating any module homes | Thin skeleton validates architecture without freezing half-designed runtime behavior | Avoids refactor churn from premature placeholders | Gives later packages stable homes and import boundaries | Skeleton tests must validate imports and lightweight dependency boundaries; unimplemented symbols, if any, must be provisional and fail loudly | Revisit if later packages need an importable symbol before its behavior is accepted |
| Error taxonomy placement and depth | Use central `rphys.errors`; implement broad base classes now using readable `RemotePhys*Error` names, and defer detailed package-specific errors until the owning packages implement behavior | Maintainer accepted `RemotePhysError` naming | Using acronym root `RPhysError`; defining every specific error from v3 now; scattering root errors across subpackages | A central hierarchy gives consistent diagnostics without pretending detailed failure behavior is already designed | Broad base classes are stable and low-churn; detailed errors stay close to tested behavior | Later packages can extend the central hierarchy while keeping user catch patterns stable | Stage 2 should define broad classes such as `RemotePhysError`, `RemotePhysDataError`, `RemotePhysIOError`, `RemotePhysDatasetError`, `RemotePhysTransformError`, `RemotePhysTrainingError`, and `RemotePhysEvaluationError`; docs should list detailed future examples as non-final | Revisit when package-specific implementation needs a shared specific error promoted to stable API |
| Registry policy | Use registries only where symbolic names are useful: codec keys, built-in dataset names, standard field schema names, and later standard metric or recipe names. Do not force registration for every transform, method, model, loss, metric, or adapter | Maintainer agreed | Registry-everything; no registries at all | Symbolic names are useful for standard resources, but global registration is too restrictive for experiment-local research code | Avoids global-state coupling and naming collisions | Lets downstream users extend through normal Python imports while preserving convenient built-ins | Docs must define when registry use is appropriate; tests can cover built-in registry smoke behavior when implemented | Revisit if users cannot discover standard components or if import paths become too verbose in common recipes |
| `_target_` extension policy | Use `_target_` import paths as the default user-extension mechanism; `loom` owns generic `_target_` instantiation, while `rphys` defines domain contracts those objects must satisfy | Maintainer agreed | Requiring all custom objects to be registered; implementing a separate `_target_` engine inside `rphys` | Import paths keep extension local and composable without duplicating `loom` mechanics | Prevents duplicate config/instantiation infrastructure | Enables downstream custom datasets, transforms, methods, losses, and metrics without editing `rphys` internals | Docs must show `_target_` examples and make clear that contract validation belongs to the receiving `rphys` API | Revisit if `loom` lacks necessary validation hooks for domain contracts |
| Optional dependency boundaries | Keep core imports lightweight; document likely extras such as `rphys[video]`, `rphys[signal]`, `rphys[torch]`, `rphys[training]`, `rphys[analysis]`, and `rphys[dev]`, but finalize exact package lists during implementation planning | Maintainer agreed | Requiring torch/video/plotting/training stacks for base imports; freezing exact dependency packages in Stage 1 | Optional extras keep the base library usable across lightweight and specialized environments | Reduces dependency churn and install failures | Allows modality, training, and analysis capabilities to grow independently | Stage 2 should include import-boundary checks and document which modules may import optional stacks | Revisit when exact backend choices are implemented or when a core contract truly requires a heavy dependency |
| API label enforcement obligations | Keep `stable`, `provisional`, and `private/internal`; stable requires docs, tests, importability, and compatibility preservation; provisional may change; private/internal carries no compatibility promise. `NotImplementedError` skeleton names must be provisional | Maintainer agreed | Treating every importable name as stable; relying on `NotImplementedError` as the only signal; using only public/private labels | Compatibility promises must be explicit, especially while the architecture is still filling in | Gives maintainers a clear threshold before promoting APIs | Lets future modules be discussed and scaffolded without premature lock-in | Docs and skeleton metadata should make labels visible; promotion to stable requires behavior and tests | Revisit if labeling overhead outweighs user clarity or if users frequently depend on provisional names accidentally |

## Practical Design Notes

Public API or documentation surface:

- Initial stable public groups: `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`.
- Initial stable diagnostics group: `rphys.errors`.
- `rphys.io` owns lazy field-access concepts: `FieldRef`, `TemporalIndexSlice`, and `FieldView`.
- Later public groups after the first stable core: `rphys.methods`, `rphys.training`, and `rphys.losses`.
- Later public group after learning-related contracts: `rphys.evaluation`.
- Future/provisional public groups until core APIs are ready: `rphys.analysis`, `rphys.recipes`, and `rphys.stages`.
- `rphys.ops`, `rphys.models`, and `rphys.testing` are not part of the initial stable public contract.

Workflow and artifact surface:

- Concrete `rphys` stages should be thin wrappers around domain APIs and `loom` stage protocols.

Failure modes and diagnostics:

- Cross-cutting failure families should be documented centrally and tested where raised.
- The central root exception should be `RemotePhysError`.

Extension points and flexibility boundaries:

- Users should extend through public protocols and `_target_` paths, with registries reserved for symbolic names.
- `rphys` should not own generic `_target_` instantiation.

Maintainability assessment:

- This package reduces future churn by fixing ownership and import boundaries before deeper implementation.

Extensibility assessment:

- Clear public contracts allow downstream projects to add domain components without editing internals.

Accepted debt:

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| None accepted yet | Design review has not started | Confirm during design-decision review |

## Phase Sketch

### Phase 1 - Boundary And Contract Skeleton

Goal:

- Create the minimal architecture skeleton and docs needed to unblock later packages.
- Preserve code as the implementation contract once code exists, with docs focused on policy, ownership, extension rules, behavior, and artifact expectations.

Scope:

- Boundary documentation, top-level module ownership, public contract-name inventory for the first stable API wave, future/provisional module map, API stability/compatibility policy, registry policy, dependency policy, central error-family inventory, and a very thin post-design package skeleton with import smoke tests.
- Broad `RemotePhys*Error` base classes in `rphys.errors`.
- Top-level module homes for `rphys.data`, `rphys.io`, `rphys.datasets`, `rphys.transforms`, and `rphys.errors`.

Out of scope:

- Deep implementation of runtime, dataset, transform, or learning contracts.
- Real `DataKey`, `Sample`, `DatasetRef`, `FieldRef`, transform behavior, codecs, adapters, method signatures, or broad placeholder classes.

Acceptance criteria:

- The scaffold makes ownership boundaries visible and importable without pulling optional heavy dependencies into core.

Test expectations:

- Package: import smoke tests.
- Unit: error-family and public API inventory checks if implemented.
- Contract: stale generic-infrastructure search.
- Integration: none.
- E2E: none.
- Opt-in: none.

Design impact:

- Sets cross-package boundaries for future Stage 2 plans.

Future compatibility:

- Leaves room to deepen each public package in later work packages.

Reviewability:

- Small structural diff.

## Open Questions

| Question | Affects | Current default | Status |
| --- | --- | --- | --- |
| Should any split package be subdivided before acceptance? | Roadmap granularity and Stage 2 scope | Keep six-package dependency map; split large packages only when their decision queues prove too broad | answered for current split; revisit per package |
| Should errors be fully implemented here or introduced package-by-package? | Scope and tests | Define broad `RemotePhys*Error` base classes here; implement detailed package-specific errors with owning packages | answered |
| Should broad empty modules be created up front? | Churn and discoverability | Create only thin module homes and import-boundary skeleton; avoid broad placeholder classes | answered |
| Which optional extras should exist initially? | Packaging and CI | Document likely extras and enforce lightweight core; finalize exact packages during implementation planning | answered |

## Handoff Notes

Master-plan draft inputs:

- `docs/rphys_architecture_plan_v3.md` sections 1-4, 7-8, 35, 49, 51, and 53.
- This planning note after behavior/design confirmation.

Quality-gate risks:

- Over-promising stable APIs before deeper packages are accepted.
- Accidentally duplicating `loom` mechanics.
- Pulling optional dependencies into core imports.

Assumptions to carry forward:

- This is the first package to plan if the maintainer wants boundaries before implementation.
- The work package is accepted and ready for Stage 2 master-plan drafting.
