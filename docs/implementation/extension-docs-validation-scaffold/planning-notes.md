# Stage 1 Planning Notes: Extension Docs And Validation Scaffold

## Metadata

- Roadmap slug: `extension-docs-validation-scaffold`
- Source context:
  - `docs/rphys_architecture_plan_v3.md`
  - `docs/implementation/field-centric-architecture-scaffold/planning-notes.md`
  - `docs/roadmap/index.md`
- Planning notes status: draft
- Current discussion stage: roadmap framing
- Related roadmap row: `Extension docs and validation scaffold`
- Blockers:
  - Split boundaries have not been confirmed by the maintainer.
  - Requires accepted public contract set from other packages.
  - Design-decision review has not started.

## Stage Gates

| Stage | Status | Locked decisions | Defaults | Open questions | Next focus |
| --- | --- | --- | --- | --- | --- |
| Roadmap framing | draft | Broad architecture is split; this package owns extension guides, validation strategy, docs, recipes, and workflow-facing tests | This package follows or tracks contract packages | Should recipes/stages live here or with the package they exercise? | Confirm scope |
| Intent discovery | draft | None yet | Serve downstream extension authors and future automation agents | Which guides must exist before first release? | Clarify doc priorities |
| Capability brainstorming | draft | None yet | Include guides, synthetic fixtures, checks, dependency docs, recipe examples | Full analysis/reporting docs deferred | Mark include/defer |
| Functionality and behavior confirmation | not started | None yet | Examples must be runnable or explicitly illustrative | None yet | Confirm behavior |
| Context compaction/reset checkpoint | not started | None yet | Stop with resume instruction if direct compaction is unavailable | None | Record checkpoint |
| Design-decision review | not started | None yet | Review queue below | None yet | Review decisions |
| Phase shaping | not started | None yet | Docs and validation gates around accepted contracts | None yet | Sketch phases |
| Handoff | not started | None yet | Carry accepted docs/checks into Stage 2 | None yet | Prepare Stage 2 inputs |

## Context Extraction

Baseline outcome:

- Provide extension-oriented documentation, synthetic fixtures, testing strategy, recipe/stage examples, and validation gates that keep the scaffold usable and maintainable.

Constraints:

- Users should extend `rphys` through public contracts and `_target_` paths, not by editing internals.
- Docs must state what to implement, what must be serializable, what field keys to use, how to declare contracts, how to test the extension, and what not to do.
- No raw datasets should enter the repository.
- Examples should use synthetic or tiny license-safe fixtures.

Deferred or out-of-scope ideas:

- Full plugin discovery.
- Full publication/reporting guide set.
- Full real dataset tutorial suite.
- Full production recipes for every learning style.

Scientific workflow obligations:

- Extension docs must require units, shapes, dtypes, coordinate frames, sampling rates, temporal alignment, leakage assumptions, validation behavior, and citations where relevant.

## User Intent

Target audience:

- Extension authors adding datasets, fields, codecs, transforms, exporters, methods, models, learners, losses, metrics, and protocols.
- Future agents using docs and tests as behavioral contracts.

User-visible outcome:

- Clear guides and validation checks that make extension behavior repeatable and scientifically explicit.

Success criteria:

- Guides exist for all accepted public extension contracts.
- Synthetic fixtures exercise core workflows without raw datasets.
- Docs and tests catch broken links, stale examples, optional dependency leaks, and extension anti-patterns.
- Recipes/stage docs show how `rphys` plugs into `loom` without owning generic infrastructure.

Non-goals:

- Implementing the underlying runtime/dataset/transform/learning contracts.
- Full real-world tutorials.
- Heavy analysis reports.

Operational constraints:

- This package should follow accepted contracts and not invent APIs not approved by package owners.

## Brainstormed Capabilities

| Capability | Decision | Rationale | Notes |
| --- | --- | --- | --- |
| Dataset adapter guide | include, pending confirmation | High-value extension path | Depends on dataset IO contracts |
| Field/modality guide | include, pending confirmation | Enables arbitrary fields | Depends on runtime core |
| Codec guide | include, pending confirmation | Storage extension path | Depends on codec contract |
| Transform/augmentation/check guide | include, pending confirmation | Runtime extension path | Depends on transform package |
| Export/materialization guide | include, pending confirmation | Formatting/precompute path | Depends on materialization package |
| Method/model/learner/loss/metric guides | include, pending confirmation | Learning/evaluation extension path | Depends on learning package |
| Synthetic fixtures | include, pending confirmation | Validation without raw datasets | Should be reusable across packages |
| Recipe and stage examples | maybe | Useful for loom integration | May live with package-specific work |
| Link/import/config checks | include, pending confirmation | Keeps docs executable | Avoid stale docs |
| Plugin discovery guide | defer | Not required initially | `_target_` is default |

## Confirmed Functionality And Behavior

Included functionality:

- Pending maintainer confirmation. Proposed scope includes extension guides, synthetic fixtures, documentation checks, optional dependency docs, recipe examples, stage examples, and validation strategy.

User-visible behavior:

- Pending maintainer confirmation. Users should be able to follow guides to add components without editing `rphys` internals.

Agent-visible behavior:

- Pending maintainer confirmation. Future agents should use docs/tests as behavioral contracts and avoid inventing undocumented extension paths.

Default behavior:

- Pending maintainer confirmation. Examples use `_target_` paths, synthetic fixtures, explicit field keys, and strict scientific contracts.

Failure behavior and diagnostics:

- Pending maintainer confirmation. Broken links, stale examples, invalid configs, optional dependency leaks, and missing scientific contract docs should fail checks where possible.

Explicit deferrals:

- Pending maintainer confirmation. Plugin entry points, broad real-world tutorials, and full analysis/reporting docs are deferred.

Out-of-scope behavior:

- Pending maintainer confirmation. Implementing core APIs owned by other work packages.

## Context Compaction Or Reset Checkpoint

- Checkpoint status: not reached
- Notes path: `docs/implementation/extension-docs-validation-scaffold/planning-notes.md`
- Resume instruction: After functionality and behavior are confirmed, compact or reset context, then resume with `.codex/prompts/stage-1-planning-notes-resume.md` and reload this planning notes file before design-decision review.
- Functionality or behavior reopened after checkpoint: none

## Design-Decision Review Queue

| Decision | Why it matters | User feedback needed | Status |
| --- | --- | --- | --- |
| Guide ownership | Avoids docs drifting from package APIs | Confirm docs package versus package-local guides | draft |
| Runnable versus illustrative examples | Affects maintenance burden | Confirm which examples must execute in CI | draft |
| Synthetic fixture scope | Affects validation coverage | Confirm shared fixture shape and modalities | draft |
| Recipe/stage doc placement | Affects loom integration clarity | Confirm central docs versus package-local examples | draft |
| Optional dependency checks | Prevents import leaks | Confirm check strategy | draft |
| Extension anti-pattern checks | Prevents undocumented internal coupling | Confirm enforceable rules | draft |
| Plugin discovery deferral | Controls extension story | Confirm `_target_` default until entry points are needed | draft |

## Design Decisions

| Decision | Selected approach | User feedback | Alternatives rejected | Rationale | Maintainability impact | Extensibility and expansion impact | Validation/documentation obligation | Debt and revisit trigger |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| None confirmed yet | Pending review | Pending maintainer feedback | Pending review | Stage 1 has not reached design-decision review | Avoids docs promising unaccepted APIs | Keeps extension docs aligned with contracts | Review required | Revisit after behavior confirmation |

## Practical Design Notes

Public API or documentation surface:

- Guides should cover datasets, fields, codecs, data objects, transforms, augmentations, checks, exporters, methods, models, learners, losses, metrics, evaluation protocols, recipes, and stages as corresponding APIs are accepted.

Workflow and artifact surface:

- Docs should explain how `rphys` stages and recipes plug into `loom` while keeping generic machinery in `loom`.

Failure modes and diagnostics:

- Broken docs links, stale import paths, invalid example configs, missing fixture coverage, optional dependency leaks, and undocumented extension behavior.

Extension points and flexibility boundaries:

- The docs should teach public extension contracts and explicitly warn against editing core internals for project-specific behavior.

Maintainability assessment:

- Docs/tests reduce rediscovery and keep implementation agents aligned with accepted contracts.

Extensibility assessment:

- Strong guides make downstream extension practical without expanding the base library prematurely.

Accepted debt:

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| None accepted yet | Design review has not started | Confirm during design-decision review |

## Phase Sketch

### Phase 1 - Extension Guides And Validation Harness

Goal:

- Build docs and checks around the accepted public contracts.

Scope:

- Extension guide skeletons, synthetic fixtures, docs link checks, example import/config checks, optional dependency notes, testing strategy.

Out of scope:

- Implementing core APIs owned by other packages.

Acceptance criteria:

- Accepted extension paths are documented and backed by synthetic examples or clear validation expectations.

Test expectations:

- Package: docs/example import checks.
- Unit: synthetic fixture tests if fixture helpers are implemented.
- Contract: docs link and API reference checks.
- Integration: recipe/config validation when available.
- E2E: minimal synthetic workflow docs only when dependencies exist.
- Opt-in: optional dependency examples gated by extras.

Design impact:

- Turns accepted APIs into maintainable user-facing contracts.

Future compatibility:

- New packages add guide sections without changing core extension strategy.

Reviewability:

- Docs-heavy, check-focused.

## Open Questions

| Question | Affects | Current default | Status |
| --- | --- | --- | --- |
| Should this package wait until one or more implementation packages are complete? | Scheduling | Draft docs with accepted contracts, validate as APIs land | open |
| Which examples should execute in CI? | Maintenance burden | Execute synthetic examples only | open |
| Should recipes/stages be centralized here? | Docs structure | Document centrally, implement with owning packages | open |

## Handoff Notes

Master-plan draft inputs:

- `docs/rphys_architecture_plan_v3.md` sections 36-41 and 49-52.
- Accepted public contracts from other split packages.

Quality-gate risks:

- Docs drifting ahead of implementation.
- Examples that are too heavy for CI.
- Extension docs promising plugin discovery before it exists.

Assumptions to carry forward:

- This package should trail the contract packages or be planned as a docs-first companion with explicit placeholders.
