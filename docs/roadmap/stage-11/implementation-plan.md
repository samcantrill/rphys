# Roadmap Stage 11 Implementation Plan

Status: approved for implementation after current revised design audit
Roadmap version: `v11`
Planning document: `docs/roadmap/stage-11/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: Phase 3 pending
Blockers: none

## Summary

- Goal: implement dependency-light base contracts for reusable collections/views/collectors, sample collections/views, losses, objectives, metrics, metric observation collections, grouping, observation views, broad error bases, and scoped public exports without concrete numerical algorithms.
- Source functionality-agreement gate: passed in `docs/roadmap/stage-11/planning.md`; FQ-1 through FQ-9 are resolved.
- Approved behavior: collectors materialize iterables into inspectable collection snapshots; collection views transform collections into collections without a separate view-result shape; sample collection views can group/sort/stitch samples before metrics; losses produce structured differentiable terms; objectives aggregate optimizer-relevant terms and expose `ObjectiveResult.total`; metrics produce detached values, row-like observations, and observation collections; observation view behavior emits the same metric observation/collection shape at a coarser or projected scope; result field updates are patch-only through public `fields`.
- Source behavior confirmation: passed; no unsupported trainer/evaluator/export/backend behavior enters Stage 11.
- Key design constraints: structural protocols plus frozen records; raw backend-native scalar/value handles plus metadata; central broad error bases; shared collection interfaces stay dependency-light; package-local private helpers only; no cross-package private helper imports; no root re-exports; no public `MetricResultRow`, `MetricResultTable`, `MetricAggregationResult`, or view-result class.
- Source design-agreement gate: passed; DQ-3, DQ-4, DQ-5, and DQ-8 are maintainer-approved/refined, and DQ-1, DQ-2, DQ-6, and DQ-7 are reviewed recommendations.
- Source functionality-agreement queue: FQ-1 through FQ-9 resolved with no reopened item.
- Source design-agreement queue: DQ-1 through DQ-8 resolved with no unresolved `needs maintainer discussion`, `blocked`, `pending approval`, or `ready for approval` item.
- Source future-roadmap/reuse safety review: Stage 10 remains evidence only; Stage 12 owns backward/distributed/scalar adapter policy; TorchMetrics/torchmetrics are optional future adapter pressure; Stage 13 owns evaluation/report/dataframe schemas, sample collection runner policy, observation view lifecycle, and report/dataframe adapters; shared helper extraction needs a revisit trigger.
- Current revised design audit: passed in `docs/roadmap/stage-11/planning.md`; DQ-1 through DQ-8 remain resolved, DQ-3/DQ-4/DQ-5/DQ-8 remain locked, no queue item was reopened, and the approved eight-phase implementation-plan draft was found coherent with DQ-8/DD-13/DD-14 guardrails.
- Examples covered: examples 1-8: synthetic loss, objective aggregation, detached metric observations/collections, metric observation grouped views, result patch handoff without mutation, common identity/grouping metadata, pre-metric sample collection reconstruction, and implementation-plan coherence smoke.
- Source phase shaping: eight phases accepted in planning: errors/import scaffold, shared collection/view/collector contracts, loss contracts, objective contracts, sample collection views, metric observation collections/grouping, observation views/composition, final validation closeout.
- Source plan quality gate: passed; no implementation readiness blockers.
- Out of scope: concrete loss/metric catalogs, optimizer/scheduler/checkpoint/trainer loops, learners, evaluator/report runners, datasource scans, export/persistence, plotting, dataframe/report schemas, hard backend imports, distributed synchronization, and workflow/project configuration.

## Implementation Workflow State

- Implementation-plan quality gate: approved by maintainer; design-pass refinement completed.
- Review pass: formal revised-scope design safety refresh completed after DQ-8 refinement, followed by the current revised design implication/future-roadmap safety/coherence audit recorded in `planning.md`; no queue item reopened.
- Refinement pass: completed; added collection/view/collector and sample collection phases, clarified value iteration plus entry metadata access, fail-loud collector defaults, fake/injected-only sample stitching, narrowed observation-view lifecycle, import-boundary checks, and synthetic integration expectations without reopening agreement queues.
- Confirmation review: maintainer approved scope, risks, and deferrals on 2026-05-16; refinement did not add scope or require a new maintainer decision.
- Automatic merge mode: enabled
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `error-import-scaffold` | merged | `agent/stage-11-loss-objective-metric-contracts-p1-error-import-scaffold` | [#71](https://github.com/samcantrill/rphys/pull/71) | `src/rphys/errors.py`, package `__init__.py` import surfaces, package/import tests | Established broad error bases and import-boundary scaffold. | `make test-package`; focused error/import unit tests; `git diff --check` | Import/API posture |
| 2 | `collection-view-collector-contracts` | merged | `agent/stage-11-loss-objective-metric-contracts-p2-collection-view-collector-contracts` | [#72](https://github.com/samcantrill/rphys/pull/72) | `src/rphys/collections.py`, central collection errors, collection tests/docs | Implemented reusable collection, view-plan, view, collector, and collector-result contracts. | focused collection unit/contract tests; `make test-unit`; `make test-contract`; `make test-package`; `git diff --check` | Collection/view/collector posture |
| 3 | `loss-contracts` | pending | `agent/stage-11-loss-objective-metric-contracts-p3-loss-contracts` | pending | `src/rphys/losses/**`, loss tests/docs only | Implement loss specs, protocols, contexts, terms, results, and patch records. | focused loss unit/contract tests; `make test-unit`; `make test-contract`; `make test-package` | Examples 1 and 5 |
| 4 | `objective-contracts` | pending | `agent/stage-11-loss-objective-metric-contracts-p4-objective-contracts` | pending | `src/rphys/objectives/**`, objective tests/docs only | Implement objective specs, protocols, contexts, terms, and `ObjectiveResult.total`. | focused objective unit/contract tests; `make test-unit`; `make test-contract`; `make test-package` | Example 2 and patch handoff |
| 5 | `sample-collection-views` | pending | `agent/stage-11-loss-objective-metric-contracts-p5-sample-collection-views` | pending | `src/rphys/data/collections.py`, data exports, sample collection/view tests/docs | Implement `SampleCollection`, `SampleCollectionViewPlan`, `SampleCollectionView`, and sample collector behavior for pre-metric reconstruction. | focused data collection unit/contract tests; `make test-unit`; `make test-contract`; `make test-package` | Example 7 |
| 6 | `metric-observation-collections` | pending | `agent/stage-11-loss-objective-metric-contracts-p6-metric-observation-collections` | pending | `src/rphys/metrics/**` value/observation/collection/grouping records, metric tests/docs | Implement metric values, observations, observation collections, grouping specs, and metric protocol records. | focused metric unit/contract tests; `make test-unit`; `make test-contract`; `make test-package` | Examples 3, 5, and 6 |
| 7 | `metric-observation-views-composition` | pending | `agent/stage-11-loss-objective-metric-contracts-p7-metric-observation-views-composition` | pending | observation view descriptors/behavior over metric records plus cross-contract synthetic tests/docs | Implement metric observation view behavior and synthetic composition across sample/loss/objective/metric records. | metric observation view unit/contract tests; synthetic integration if feasible; `make test-unit`; `make test-contract`; relevant `make test-integration` | Examples 1-8 |
| 8 | `api-validation-closeout` | pending | `agent/stage-11-loss-objective-metric-contracts-p8-api-validation-closeout` | pending | package exports, docs/docstrings, import-boundary and final validation evidence | Close public API, docs, import boundaries, and full-stage validation. | `make test-package`; `make test-unit`; `make test-contract`; relevant `make test-integration`; `make test-summary`; `uv lock --check`; `git diff --check`; `make validate-pr` when practical | Examples 1-8 |

## Implementation Readiness Blockers

No readiness blockers are present. Planning records show the validation and phase-shaping gate passed, the plan quality gate passed, all required specialist evidence is current through the revised design implication/future-roadmap safety/coherence audit, both agreement queues are resolved, future-roadmap/reuse findings are resolved or deferred with revisit triggers, every auto-approved decision has traceability plus adversarial review evidence, and no design decision is blocked or awaiting maintainer discussion.

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None | Plan quality gate passed | No action required before implementation-plan approval. | resolved |

## Global Ownership Boundaries

- `rphys.collections` may depend only on central `rphys.errors` and standard-library typing/collections.
- `rphys.data.collections` may depend on public `rphys.collections`, `rphys.data` containers, field locators, field values, and central errors.
- `losses`, `objectives`, and `metrics` may depend on public `rphys.data`, public `rphys.collections`, and central `rphys.errors`.
- `objectives` may import public loss result records only when code-backed by tests; losses must not import objectives; metrics must not depend on losses or objectives for core behavior.
- No Stage 11 core module may import `methods`, `models`, `learning`, `training`, `evaluation`, `analysis`, `datasources`, `io`, `ops.export`, torch, torchmetrics, numpy, pandas, scipy, matplotlib, video stacks, or unlanded Stage 10 modules.
- Private validation/coercion helpers stay package-local. Do not import another package's private helper module.
- Public exports must be code-backed, tested, documented, and scoped to package homes. Root `rphys` re-exports remain out of scope.
- Result patch fields use immutable `fields` mappings from `FieldLocator` to `FieldValue`; execution must not mutate input containers by default.
- Collectors materialize iterables into collection snapshots. Views transform collections and return collections; no separate view-result class is introduced. If collection/view behavior is wrapped as an operation, `OperationResult.output` carries the collection.

## Phase 1: Error And Import Scaffold

Status: merged
Slug: `error-import-scaffold`
Branch: `agent/stage-11-loss-objective-metric-contracts-p1-error-import-scaffold`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p1-error-import-scaffold`
PR: [#71](https://github.com/samcantrill/rphys/pull/71)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: establish the central broad error bases and package import boundary before behavior records rely on them.
- Files/modules owned: `src/rphys/errors.py`; `src/rphys/losses/__init__.py`; `src/rphys/objectives/__init__.py`; `src/rphys/metrics/__init__.py`; `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`; focused error tests if needed.
- Behavior implemented: importable `RemotePhysLossError`, `RemotePhysObjectiveError`, and `RemotePhysMetricError` from `rphys.errors`; package homes remain lightweight and expose only implemented names.
- Decisions applied: FQ-6, FQ-9, DD-1, DD-8, DQ-1, DQ-6.
- Future-roadmap/reuse constraints: broad catch points are stable for Stage 12/13; no package-local duplicate error bases; no placeholder specific-error taxonomy.
- Examples or demos covered: import/API readiness only.
- Out of scope: loss/objective/metric records, concrete algorithms, backend adapters, root exports, package-local error base duplication, public `MetricResultRow`.
- Dependencies: approved planning artifact only.

### Tasks

- Add the three broad central error bases to `rphys.errors` and `__all__`.
- Keep package `__init__.py` files lightweight and code-backed; avoid exporting future names before implementation exists.
- Update package/import-boundary tests for the new broad errors and forbidden dependency imports, including adding `torchmetrics` to the forbidden optional dependency sentinel set and checking `rphys.losses`, `rphys.objectives`, and `rphys.metrics` module imports directly.
- Add focused error tests only where the broad bases need direct coverage beyond package imports.
- Record any discovered import-boundary risk in the phase PR body; do not broaden API to solve later-phase convenience.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Verify import surfaces and dependency-light package homes, including no `torch` or `torchmetrics` import on Stage 11 package import. | yes |
| focused error unit tests | Verify broad bases and central import paths if package tests do not cover them. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: broad errors import from `rphys.errors`; package homes import without heavy optional stacks.
- Design-decision evidence: no package-local duplicate broad errors and no placeholder specific taxonomy.
- Future-roadmap/reuse evidence: Stage 12/13 can catch package-specific broad failures without trainer/evaluator coupling.
- Example/demo evidence: package import examples remain dependency-light.
- Documentation evidence: public error docstrings or module docs explain broad catch-point purpose.
- Scientific contract evidence: errors are ready to carry primitive context in later phases.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-11/phases/error-import-scaffold.md`
- Planning/refinement budget: small
- Implementation/refinement budget: small
- PR review budget: small
- Blocker-resolution budget: stop on public API expansion or import-boundary conflict.
- Pre-submit blocker gate: no placeholder exports, no root re-exports, no heavy imports.
- Merge record: completed in `docs/roadmap/stage-11/phases/error-import-scaffold-merge-record.md`

### Risks And Stop Conditions

- Risks: exporting too many names early; accidentally making broad errors package-local; import tests missing optional dependency leakage.
- Stop conditions: a change requires package-level error re-exports, specific public error subclasses, or root exports without new design approval.
- Assumptions: current empty package homes can remain lightweight while later phases add code-backed names.

### Completion Summary

- Implementation: added central `RemotePhysLossError`, `RemotePhysObjectiveError`, and `RemotePhysMetricError`; package homes stayed lightweight with no placeholder exports.
- Validation: `uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/test_errors.py tests/package/test_import.py tests/package/test_import_boundaries.py`; `UV_CACHE_DIR=/tmp/uv-cache make test-package`; `git diff --check`.
- PR: [#71](https://github.com/samcantrill/rphys/pull/71)
- Merge: squash merged to `develop` as `5980cb6` on 2026-05-16.
- Follow-up: later phases must add code-backed package exports only when their contracts land.

## Phase 2: Shared Collection, View, And Collector Contracts

Status: merged
Slug: `collection-view-collector-contracts`
Branch: `agent/stage-11-loss-objective-metric-contracts-p2-collection-view-collector-contracts`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p2-collection-view-collector-contracts`
PR: [#72](https://github.com/samcantrill/rphys/pull/72)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement the reusable collection/view/collector vocabulary before sample and metric collection phases depend on it.
- Files/modules owned: `src/rphys/collections.py`; central collection error additions in `src/rphys/errors.py` if required; scoped package exports only if code-backed; `tests/unit/rphys/test_collections.py` or equivalent; collection contract tests; collection docstrings/docs.
- Behavior implemented: dependency-light `Collection` protocol or minimal record shape, reusable `CollectionItem` for values that need item metadata, `CollectionContext`, `CollectionViewPlan`, `CollectionView` protocol, `Collector` protocol, and `CollectorResult` record.
- Decisions applied: collection/view refinement; DD-1, DD-2, DD-11, DD-12, DD-13; FR-6A and FR-8.
- Future-roadmap/reuse constraints: base collection contracts must be domain-neutral and must not import `data`, `metrics`, `losses`, `objectives`, `ops`, datasource, evaluator, pandas, numpy, torch, or torchmetrics.
- Examples or demos covered: shared collection/view/collector posture only.
- Out of scope: `SampleCollection`, `MetricObservationCollection`, concrete grouping/stitching/reduction algorithms, dataframe/report adapters, operation pipelines, streaming runners, and persistent state containers.
- Dependencies: Phase 1 broad errors/import scaffold.

### Tasks

- Define `Collection` as a structural, sequence-like interface over immutable membership plus collection-level metadata/provenance. Iteration yields member values, while an explicit entry access surface such as an `entries` property returns `CollectionItem[T]` records for item metadata/provenance. Do not require subclassing for concrete collections.
- Define `CollectionItem` as the reusable item wrapper for domains whose item value does not already carry metadata/provenance. Use it for Stage 11 sample collection entries rather than inventing a sample-specific row class, and test that value iteration does not lose entry metadata access.
- Define `CollectionViewPlan` as an inspectable descriptor base or protocol with name, metadata, and provenance; domain plans add group/sort/stitch/view specifics.
- Define `CollectionView` as structural behavior that accepts a collection and returns a collection. Do not define a separate `CollectionViewResult`.
- Define `Collector` as structural behavior that consumes `Iterable[T]` and materializes a collection snapshot through `CollectorResult[C]`.
- Define `CollectorResult` for materialization diagnostics: the collection, accepted count, rejected/skipped items or reasons when an explicit skip/reject policy is configured, metadata, and provenance. The default collector posture is fail-loud for invalid items or missing required metadata; silent dropping is not allowed. It is not an operation result and not the normal output of a view.
- Document how an operation wrapper can put a collection on `OperationResult.output` while preserving collector diagnostics in operation metadata/provenance.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| focused collection unit tests | Validate collection protocols/records, immutable membership, value iteration, entry metadata access, collector result diagnostics, fail-loud defaults, explicit skip/reject diagnostics, and invalid descriptor errors. | yes |
| focused collection contract tests | Prove fake collectors and fake views compose without requiring inheritance or operation wrappers and without duplicating `OperationResult`. | yes |
| `make test-unit` | Ensure unit suite remains coherent. | yes |
| `make test-contract` | Ensure public extension semantics hold. | yes |
| `make test-package` | Ensure base collection imports stay lightweight and do not pull domain packages. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: fake collection, collector, and view objects can be inspected and composed; collection iteration yields values while entry access preserves `CollectionItem` metadata/provenance; views return collections; collectors return `CollectorResult`.
- Design-decision evidence: no view-result class, no inheritance requirement, no operation-pipeline dependency, and no domain imports in the shared module.
- Future-roadmap/reuse evidence: sample collections and metric observation collections can both reuse the vocabulary without depending on each other.
- Example/demo evidence: direct fake collector/view examples demonstrate `Iterable[T] -> CollectorResult[Collection[T]] -> CollectionView -> Collection`.
- Documentation evidence: docstrings explain when to use `CollectorResult` versus `OperationResult`.
- Scientific contract evidence: collection membership, item metadata/provenance, accepted/rejected counts, ordering assumptions, and fail-loud versus explicit skip/reject behavior are inspectable.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-11/phases/collection-view-collector-contracts.md`
- Planning/refinement budget: medium
- Implementation/refinement budget: medium
- PR review budget: medium
- Blocker-resolution budget: stop on generic framework overreach or domain import leakage.
- Pre-submit blocker gate: no public view-result class, no root exports, no data/metric/loss/objective imports in `rphys.collections`.
- Merge record: completed in `docs/roadmap/stage-11/phases/collection-view-collector-contracts-merge-record.md`

### Risks And Stop Conditions

- Risks: generic collection contracts may become too broad; `CollectorResult` may duplicate `OperationResult`; base classes may be overused instead of structural protocols; entry metadata access may be lost if value iteration is the only public surface.
- Stop conditions: implementation needs a registry, datasource/evaluator runner, streaming lifecycle protocol, pandas/dataframe behavior, required inheritance hierarchy, silent filtering policy, or a separate collection/view result family.
- Assumptions: a tiny shared protocol/record layer is enough for Stage 11 sample and metric collection phases.

### Completion Summary

- Implementation: added `rphys.collections` protocols and frozen records plus central collection validation errors.
- Validation: focused collection/error/package tests; `UV_CACHE_DIR=/tmp/uv-cache make test-unit`; `UV_CACHE_DIR=/tmp/uv-cache make test-contract`; `UV_CACHE_DIR=/tmp/uv-cache make test-package`; `git diff --check`.
- PR: [#72](https://github.com/samcantrill/rphys/pull/72)
- Merge: squash merged to `develop` as `8652c96` on 2026-05-16.
- Follow-up: Phase 5 and Phase 6 should reuse `CollectionItem` and `CollectorResult` rather than adding one-off row/result families.

## Phase 3: Loss Contracts And Patch Results

Status: pending
Slug: `loss-contracts`
Branch: `agent/stage-11-loss-objective-metric-contracts-p3-loss-contracts`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p3-loss-contracts`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement the first executable semantic contract for losses over declared fields.
- Files/modules owned: `src/rphys/losses/core.py`; `src/rphys/losses/specs.py`; `src/rphys/losses/context.py`; `src/rphys/losses/results.py`; package-local private validation helpers; `src/rphys/losses/__init__.py`; `tests/unit/rphys/losses/**`; loss contract tests; loss docstrings/docs.
- Behavior implemented: `Loss` protocol, loss input/contract/context records, `LossTerm`, `LossResult`, backend-native term values plus metadata, declared immutable `fields` patches, fail-loud validation, no default mutation.
- Decisions applied: FR-1, FR-2, FR-7, FR-9; DD-2, DD-3, DD-4, DD-5, DD-8, DD-10, DD-11.
- Future-roadmap/reuse constraints: use current field containers and `FieldLocator`; do not import Stage 10 method output; preserve structured terms for future objectives; keep helper code package-local.
- Examples or demos covered: Example 1 synthetic loss over prediction/target fields; Example 5 result patch handoff.
- Out of scope: concrete numerical loss algorithms, objectives, metrics, aggregators, optimizer/trainer behavior, backend tensor helpers, Stage 10 imports.
- Dependencies: Phase 1 broad errors/import scaffold; Phase 2 shared collection contracts only if implementation reuses public metadata/provenance helpers.

### Tasks

- Define package-local frozen records for loss input specs, contracts, contexts, terms, and results.
- Normalize `FieldLocator | str` inputs at construction and validate duplicates, roles, masks, reductions, missing-field policy, and expected metadata descriptors.
- Preserve raw backend-native term handles while recording descriptive metadata such as backend, differentiability, gradient path, reduction, unit, diagnostics, and provenance.
- Implement immutable `LossResult.fields` patch behavior with `FieldLocator -> FieldValue` values; validate declared writes and no input mutation.
- Add structural protocol/contract tests with fake scalar handles and synthetic `Batch` or field-container inputs.
- Document backend-neutral limits and that Stage 11 cannot prove autograd behavior without backend adapters.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| focused loss unit tests | Validate specs, contexts, terms, results, patches, and error context. | yes |
| focused loss contract tests | Exercise fake loss objects against synthetic field containers. | yes |
| `make test-unit` | Ensure unit suite remains coherent. | yes |
| `make test-contract` | Ensure public extension semantics hold. | yes |
| `make test-package` | Ensure imports stay lightweight and exports are code-backed. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: loss specs normalize locators and loss results preserve structured terms and immutable patches.
- Design-decision evidence: raw handles plus metadata, public `fields`, no hidden mutation, package-local helpers, central errors.
- Future-roadmap/reuse evidence: future objectives can consume loss terms without Stage 10 or trainer imports.
- Example/demo evidence: synthetic loss over prediction/target fields and patch handoff are tested or documented.
- Documentation evidence: docstrings specify field roles, masks, reductions, missing-field behavior, units, backend metadata limits, and failure behavior.
- Scientific contract evidence: tests cover missing fields, invalid descriptors, empty masks where contract-level validation applies, incompatible metadata, and typed failures with context.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: medium
- Implementation/refinement budget: medium
- PR review budget: medium
- Blocker-resolution budget: stop on scalar protocol/backend import pressure.
- Pre-submit blocker gate: no concrete algorithms, no trainer/objective/metric coupling, no cross-package private helper imports.
- Merge record: pending

### Risks And Stop Conditions

- Risks: scalar metadata becomes too loose; helper duplication diverges from later packages; loss result patches tempt apply-helper scope creep.
- Stop conditions: implementation appears to need a public `DifferentiableScalar`, backend import, concrete loss math, or shared public selector helper.
- Assumptions: fake scalar handles and synthetic field containers are sufficient to validate the base contract before concrete algorithms exist.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 4: Objective Contracts And Optimizer Scalar Results

Status: pending
Slug: `objective-contracts`
Branch: `agent/stage-11-loss-objective-metric-contracts-p4-objective-contracts`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p4-objective-contracts`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement optimizer-facing objective contracts and the required `.total` result shape.
- Files/modules owned: `src/rphys/objectives/core.py`; `src/rphys/objectives/specs.py`; `src/rphys/objectives/context.py`; `src/rphys/objectives/results.py`; package-local private validation helpers; `src/rphys/objectives/__init__.py`; `tests/unit/rphys/objectives/**`; objective contract tests; objective docstrings/docs.
- Behavior implemented: `Objective` protocol, objective input/contract/context records, aggregation descriptors, `ObjectiveTerm`, `ObjectiveResult.total`, structured term breakdown, optional immutable `fields`, typed validation failures.
- Decisions applied: FR-3, FR-4, FR-7, FR-8, FR-9; DQ-3, DQ-4, DQ-7; DD-2, DD-3, DD-4, DD-5, DD-8, DD-10, DD-11.
- Future-roadmap/reuse constraints: Stage 12 consumes `.total` but owns backward calls, optimizer stepping, schedules as runtime objects, checkpointing, device movement, and distributed policy.
- Examples or demos covered: Example 2 objective aggregation; Example 5 patch handoff.
- Out of scope: learners/trainers, backward calls, optimizer/scheduler/checkpoint objects, metric logging/reporting, concrete executable schedules.
- Dependencies: Phases 1-3. Objectives may import public loss result records only when tests prove the dependency and must not import loss private helpers.

### Tasks

- Define objective specs, contracts, contexts, term descriptors, aggregation descriptors, and result records.
- Require `ObjectiveResult.total` and preserve the raw backend-native scalar handle with metadata/provenance.
- Validate duplicate/invalid terms, invalid weights/reductions, missing or malformed totals, schedule descriptors as data, and undeclared patch fields.
- Support loss-term passthrough or references using public loss records only when code-backed by tests.
- Add contract tests with fake loss results and fake scalar handles.
- Document that Stage 11 objectives expose the optimizer target but do not call backward or own trainer mechanics.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| focused objective unit tests | Validate specs, aggregation descriptors, terms, results, `.total`, patches, and errors. | yes |
| focused objective contract tests | Exercise fake objectives and fake loss results. | yes |
| `make test-unit` | Ensure unit suite remains coherent. | yes |
| `make test-contract` | Ensure objective public semantics hold. | yes |
| `make test-package` | Ensure imports stay lightweight and public exports are code-backed. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: `.total` is required, structured objective/loss terms are inspectable, and optional `fields` are explicit patches.
- Design-decision evidence: raw backend scalar handle plus metadata; no trainer, optimizer, scheduler, checkpoint, or backend dependency.
- Future-roadmap/reuse evidence: Stage 12 can build learner/trainer adapters around `.total` without string-key lookup.
- Example/demo evidence: synthetic objective aggregation from fake loss terms is tested or documented.
- Documentation evidence: docstrings explain aggregation descriptors, term weights, provenance, backend-neutral limits, and non-ownership of trainer mechanics.
- Scientific contract evidence: invalid totals, duplicate terms, invalid reductions/weights, missing metadata, and dtype/device/backend mismatch descriptors fail loudly where contract-level validation can detect them.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: medium
- Implementation/refinement budget: medium
- PR review budget: medium
- Blocker-resolution budget: stop on trainer/backend adapter creep.
- Pre-submit blocker gate: no backward calls, no optimizer/scheduler objects, no cross-package private helper imports.
- Merge record: pending

### Risks And Stop Conditions

- Risks: objective records accidentally become trainer configuration; `.total` metadata claims more backend guarantees than Stage 11 can prove; objective-to-loss dependency direction becomes too broad.
- Stop conditions: implementation needs a public scalar/backward protocol, direct trainer behavior, runtime scheduler execution, or unlanded Stage 10 imports.
- Assumptions: loss public records from Phase 2 are sufficient for objective composition examples.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 5: Sample Collections And Pre-Metric Views

Status: pending
Slug: `sample-collection-views`
Branch: `agent/stage-11-loss-objective-metric-contracts-p5-sample-collection-views`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p5-sample-collection-views`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement sample collection snapshots and pre-metric collection views for grouping, sorting, and descriptor-level reconstruction/stitching without concrete signal-processing algorithms.
- Files/modules owned: `src/rphys/data/collections.py`; `src/rphys/data/__init__.py`; public imports from `src/rphys/collections.py`; package-local private validation helpers if needed; `tests/unit/rphys/data/**`; sample collection contract tests; sample collection docstrings/docs.
- Behavior implemented: `SampleCollection`, `SampleCollectionViewPlan`, structural `SampleCollectionView` behavior, sample collector behavior over `Iterable[Sample]`, per-sample metadata/provenance through reusable `CollectionItem`, value iteration plus entry metadata access, grouping/sorting descriptors, fake or injected field-stitch/reconstruction descriptors, and explicit missing/overlap/order policies.
- Decisions applied: collection/view refinement; FR-6A, FR-6B, FR-8, FR-9; DD-12, DD-13, DD-14 plus shared collection decisions.
- Future-roadmap/reuse constraints: Stage 13 can wrap this in evaluation runners later; Stage 11 does not scan datasources, load samples, write files, report tables, or implement concrete physiological reconstruction algorithms.
- Examples or demos covered: Example 7 pre-metric sample collection reconstruction boundary, now as an included Stage 11 contract.
- Out of scope: datasource scans/builders, lazy `IndexItem` materialization, evaluator runners, report/dataframe outputs, out-of-core streaming policy, concrete interpolation/resampling/filtering algorithms, and metric observation computation.
- Dependencies: Phase 2 shared collection/view/collector contracts. May run after Phase 1 and before metric phases; independent from loss/objective implementation except final composition examples.

### Tasks

- Define `SampleCollection` as an immutable-membership, sequence-like collection of samples with collection metadata/provenance. The collection iterates over `Sample` values while exposing entry access, such as `entries`, for `CollectionItem[Sample]` metadata/provenance used by grouping and sorting.
- Use reusable `CollectionItem[Sample]` or an equivalent shared item wrapper for per-sample metadata such as `subject_id`, `record_id`, `sample_id`, `window_start`, `window_stop`, `split`, and source provenance. Do not add a one-off sample row class unless implementation proves the generic item wrapper is insufficient.
- Define sample collector behavior that consumes `Iterable[Sample]` or an existing `SampleCollection` and returns `CollectorResult[SampleCollection]` with accepted counts, rejected/skipped samples only when an explicit skip/reject policy is configured, metadata, and provenance. Default materialization fails loudly for invalid samples or missing required collection metadata.
- Define `SampleCollectionViewPlan` descriptors for group keys, sort keys, selected fields, reconstruction/stitch policy labels, optional synthetic or injected fake stitch behavior, missing-window policy, overlap policy, and provenance requirements.
- Define `SampleCollectionView` behavior that consumes a `SampleCollection` and emits a `SampleCollection` of reconstructed or selected samples. Because `SampleCollection` is iterable, this still satisfies call sites that need `Iterable[Sample]` while preserving metadata/provenance.
- Validate that view execution does not mutate source samples by default and that reconstructed samples carry source grouping/window provenance.
- Add tiny synthetic tests for grouping by `record_id`/`subject_id`, sorting by `window_start`, rejecting missing sort metadata, value iteration plus entry access, explicit skip/reject diagnostics, and stitching declared field payloads with fake tuple/list values or injected fake stitch behavior only.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| focused sample collection unit tests | Validate collection construction, value iteration, entry metadata, collector results, fail-loud defaults, explicit skip/reject diagnostics, grouping, sorting, view plans, reconstruction provenance, and invalid policies. | yes |
| focused sample collection contract tests | Exercise fake sample collection views and prove outputs are iterable `SampleCollection` snapshots. | yes |
| `make test-unit` | Ensure unit suite remains coherent. | yes |
| `make test-contract` | Ensure public extension semantics hold. | yes |
| `make test-package` | Ensure imports stay lightweight and avoid datasource/evaluator/backend/report dependencies. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: `Iterable[Sample] -> CollectorResult[SampleCollection] -> SampleCollectionView -> SampleCollection` works with synthetic samples; `SampleCollection` iteration yields `Sample` and `entries` preserve `CollectionItem[Sample]` metadata/provenance.
- Design-decision evidence: sample reconstruction belongs to sample collection views, not metrics; collectors materialize iterables; views return collections; no builder or view-result class is introduced.
- Future-roadmap/reuse evidence: Stage 13 can add evaluation runners around the same contracts without changing metric records.
- Example/demo evidence: BVP-window-style grouping/sorting/stitching is represented with fake or injected test payload behavior and explicit provenance, without a public physiological reconstruction algorithm.
- Documentation evidence: docstrings explain sample metadata keys, grouping/sort semantics, mutation policy, missing/overlap policies, and algorithm deferrals.
- Scientific contract evidence: tests cover out-of-order windows, missing group/sort metadata, source provenance, declared fields, non-mutation, and leakage-sensitive grouping notes.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: medium
- Implementation/refinement budget: medium
- PR review budget: medium
- Blocker-resolution budget: stop on datasource/evaluator runner scope or concrete signal-processing algorithm creep.
- Pre-submit blocker gate: no datasource scans, no sample loading, no evaluator/report/export imports, no hidden source mutation.
- Merge record: pending

### Risks And Stop Conditions

- Risks: sample collection views may drift into evaluator runner behavior; stitch descriptors may overfit before concrete signal processing stages; sample metadata may be too flexible; entry metadata may be hard to preserve if the API only exposes values.
- Stop conditions: implementation needs datasource indexes, lazy IO, report writing, out-of-core streaming orchestration, concrete resampling/interpolation/filtering algorithms, real physiological reconstruction behavior, silent item filtering, or hidden mutation of source samples.
- Assumptions: Stage 11 can validate collection/view contracts with synthetic sample fields and fake stitch behavior only.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 6: Metric Values, Observations, Collections, And Grouping

Status: pending
Slug: `metric-observation-collections`
Branch: `agent/stage-11-loss-objective-metric-contracts-p6-metric-observation-collections`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p6-metric-observation-collections`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement detached metric value, observation collection, grouping, and metric protocol records.
- Files/modules owned: `src/rphys/metrics/core.py`; `src/rphys/metrics/specs.py`; `src/rphys/metrics/context.py`; `src/rphys/metrics/results.py`; package-local private validation helpers; `src/rphys/metrics/__init__.py`; `tests/unit/rphys/metrics/**`; metric contract tests; metric docstrings/docs.
- Behavior implemented: `Metric` protocol, metric input/contract/context records, detached `MetricValue`, row-like `MetricObservation`, immutable `MetricObservationCollection`, `GroupBySpec`, grouping metadata, optional immutable `fields`, typed validation failures.
- Decisions applied: FR-5, FR-6, FR-7, FR-8, FR-9; DQ-3, DQ-4, DQ-5; DD-2, DD-3, DD-4, DD-5, DD-6, DD-8, DD-9, DD-10, DD-11, shared collection decisions.
- Future-roadmap/reuse constraints: Stage 13 owns evaluator/report/dataframe schemas and any first-class identity columns; Stage 12 may log detached observations without report dependencies. Metric observation collections reuse the shared collection vocabulary but remain metric-owned records.
- Examples or demos covered: Example 3 detached observations/collections, Example 5 patch handoff, Example 6 identity/grouping metadata.
- Out of scope: metric observation views beyond collection/group specs, concrete metric algorithms, dataframe/report schemas, evaluator runners, datasource group builders, sample collection reconstruction implementation beyond consuming `SampleCollection` outputs, first-class identity fields unless tests prove an immediate need, public `MetricResultRow` or `MetricResultTable`.
- Dependencies: Phases 1-2 and Phase 5 for the shared/sample collection contracts; may proceed after Phases 3-4 in the sequential workflow. Metrics remain independent of losses/objectives for core behavior.

### Tasks

- Define metric specs, contexts, values, observations, observation collections, grouping specs, and the metric protocol.
- Represent collection entries as `MetricObservation`; do not introduce a separate public `MetricResultRow` or `MetricResultTable`.
- Validate detachment metadata, invalid differentiability claims, levels/scopes, group keys, duplicate/invalid observations, collection immutability/combination, and optional patch fields.
- Keep identity in `groups`/metadata using glossary-style keys such as `subject_id`, `record_id`, `sample_id`, `split`, and custom keys.
- Add tests proving no pandas/report/datasource/evaluator imports and no heavy backend imports.
- Document leakage-sensitive grouping semantics as caller-supplied metadata, not datasource-owned logic.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| focused metric unit tests | Validate metric values, observations, collections, grouping specs, patches, and errors. | yes |
| focused metric contract tests | Exercise fake metric objects and observation collection construction. | yes |
| `make test-unit` | Ensure unit suite remains coherent. | yes |
| `make test-contract` | Ensure metric public semantics hold. | yes |
| `make test-package` | Ensure imports stay lightweight and no public `MetricResultRow` or `MetricResultTable` appears. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: detached metric values, row-like observations, immutable collections, grouping specs, and optional patches work as public records.
- Design-decision evidence: approved observation collection shape, `groups`/metadata identity, no pandas/report dependency, no public row/table class.
- Future-roadmap/reuse evidence: Stage 13 can map observations to evaluation protocols/reports later without changing Stage 11 internals.
- Example/demo evidence: sample/window and grouped observations with grouping metadata are tested or documented.
- Documentation evidence: docstrings explain levels/scopes, grouping metadata, detachment metadata, provenance, missing-group policy, and Stage 13 deferrals.
- Scientific contract evidence: tests cover invalid levels/groups, missing metadata policy, per-sample/per-window/record/group/dataset clarity, view metadata placeholders, and leakage-sensitive grouping notes.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: medium
- Implementation/refinement budget: medium
- PR review budget: medium
- Blocker-resolution budget: stop on report/dataframe/schema creep.
- Pre-submit blocker gate: no public `MetricResultRow` or `MetricResultTable`, no datasource/evaluator/report imports, no hidden metric state.
- Merge record: pending

### Risks And Stop Conditions

- Risks: flexible `groups`/metadata may obscure identity semantics; collection helpers may drift toward dataframe/report behavior; metric value detachment metadata can overclaim backend behavior.
- Stop conditions: implementation needs first-class identity fields, dataframe conversion, evaluator runner hooks, datasource grouping builders, or concrete metric algorithms.
- Assumptions: dependency-light observation records are enough for Stage 13 to adapt later.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 7: Metric Observation Views And Synthetic Composition

Status: pending
Slug: `metric-observation-views-composition`
Branch: `agent/stage-11-loss-objective-metric-contracts-p7-metric-observation-views-composition`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p7-metric-observation-views-composition`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement explicit metric observation view behavior and prove the approved records compose through synthetic examples.
- Files/modules owned: observation view descriptors/behavior over metric records in `src/rphys/metrics/core.py`, `src/rphys/metrics/specs.py`, and `src/rphys/metrics/results.py`; view tests under `tests/unit/rphys/metrics/**`; cross-contract contract/integration tests; docs/docstrings for examples 1-8.
- Behavior implemented: small `MetricObservationViewPlan` descriptor, minimal `MetricObservationView` structural behavior if needed, grouped/projected `MetricObservation` records or `MetricObservationCollection` outputs, empty/missing/mixed-level policies, provenance, synthetic loss/objective/metric composition.
- Decisions applied: FR-6, FR-7, FR-8; DD-7, DD-9, DD-12; future-roadmap safety findings for Stage 10/12/13.
- Future-roadmap/reuse constraints: Stage 13 can wrap observation view behavior and sample collection views in evaluator ops later; optional torchmetrics/distributed behavior remains future adapter pressure; Stage 11 keeps view descriptors dependency-light.
- Examples or demos covered: Examples 1-8, especially explicit observation views, metric-then-view behavior, the pre-metric sample collection boundary, and implementation-plan coherence smoke.
- Out of scope: concrete view/reduction algorithms beyond descriptor/fake behavior, separate public `MetricAggregationResult`, public `MetricResultTable`, evaluator/report runners, additional sample collection stitching/reconstruction beyond Phase 5 contracts, streaming evaluator lifecycle, required public `reset`/`update` lifecycle, distributed synchronization, torchmetrics adapters, durable export.
- Dependencies: Phases 2-6.

### Tasks

- Define the smallest observation view descriptor/behavior surface required by the roadmap. Treat `MetricObservationViewPlan` as configuration and `MetricObservationView` as structural callable/object behavior over observations/collections, not a result family, required base class, or persistent state container.
- View output is just metric output at a coarser or different `level`/window/grouping scope: grouped/projected `MetricObservation` records or a `MetricObservationCollection` whose entries carry view metadata/provenance.
- Do not add a separate public `MetricAggregationResult`, `MetricResultTable`, or view-result class; provenance, diagnostics, source view plan metadata, source observation counts, and grouping/window details belong on view observations or collection metadata.
- Do not add evaluator-style lifecycle methods to the public protocol. A richer `reset`/`update`/streaming lifecycle, persistent state object, distributed synchronization contract, or report/evaluator ownership must stop for Stage 13 or a new design review.
- Validate group keys, grouping order, metadata selectors, empty groups, missing metadata, view provenance, mixed-level policy, observation/collection output shape, and level/window semantics.
- Add fake observation view behavior or contract examples for metric-then-view order, and compose with Phase 5 sample-collection-then-metric reconstruction contracts without concrete scientific algorithms.
- Cover the implementation-plan coherence smoke from example 8: `Iterable[Sample] -> CollectorResult[SampleCollection] -> SampleCollectionView -> Metric -> MetricObservationCollection -> MetricObservationView` with fake payloads, plus independent `LossResult -> ObjectiveResult.total`.
- Add synthetic composition tests using direct field containers and fake scalar/metric handles; do not import Stage 10 `MethodOutput`, Stage 12 trainers, or Stage 13 evaluators.
- Document that core `Metric` does not hide accumulation and that distributed/torchmetrics synchronization belongs to future adapters or trainer/evaluator policy.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| focused metric observation view unit tests | Validate view plans, view behavior, observation/collection outputs, grouping, empty/missing policies, and provenance. | yes |
| cross-contract contract tests | Prove fake loss/objective/metric records and observation view behavior compose. | yes |
| direct field-container/sample-collection synthetic integration test or recorded infeasibility | Validate Stage 11 base records compose after Phases 2-6 land; if a direct integration test is infeasible, the phase PR must record why and provide equivalent contract coverage. | yes |
| `make test-unit` | Ensure unit suite remains coherent. | yes |
| `make test-contract` | Ensure public extension semantics hold. | yes |
| relevant `make test-integration` or documented equivalent contract coverage | Run synthetic integration when added; otherwise record the infeasibility reason and equivalent contract coverage. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: observation view plans and behavior emit grouped/projected observations or collections with explicit level/window/grouping metadata and provenance without a public streaming lifecycle or view result class.
- Design-decision evidence: no hidden metric mutation, no evaluator-owned ad hoc view state, no distributed/backend adapter in core.
- Future-roadmap/reuse evidence: Stage 13 can adapt sample collection views, view descriptors, and observation collections to evaluator/report workflows; Stage 12 can ignore or log detached observations.
- Example/demo evidence: sample-collection-then-metric and metric-then-view examples plus cross-contract composition are represented with fakes or documented tests.
- Documentation evidence: docstrings explain empty/missing group policy, mixed-level handling, grouped/projected level/window semantics, view provenance, absence of a public aggregation/view result class, absence of a public streaming lifecycle, and future distributed adapter deferral.
- Scientific contract evidence: tests cover grouping order, missing metadata, empty groups, leakage-sensitive grouping documentation, mixed observation levels, and provenance.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: medium
- Implementation/refinement budget: medium
- PR review budget: medium
- Blocker-resolution budget: stop on lifecycle overfit, sample reconstruction scope creep, or evaluator/report coupling.
- Pre-submit blocker gate: no concrete algorithms, no torchmetrics/distributed sync, no durable export/report behavior.
- Merge record: pending

### Risks And Stop Conditions

- Risks: observation view behavior may overfit before Stage 13; synthetic integration may become too broad; descriptor records may under-specify empty/mixed-level behavior.
- Stop conditions: implementation needs concrete statistical view/reduction algorithms, additional sample collection reconstruction beyond Phase 5 contracts, distributed synchronization, evaluator runner lifecycle, public `reset`/`update` streaming protocol, persistent view state object, separate aggregation/view result class, or dataframe/report output.
- Assumptions: descriptor/fake view behavior is enough to validate the public contract without numerical catalogs.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 8: API, Docs, Import Review, And Validation Closeout

Status: pending
Slug: `api-validation-closeout`
Branch: `agent/stage-11-loss-objective-metric-contracts-p8-api-validation-closeout`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p8-api-validation-closeout`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: consolidate Stage 11 public API, docs, examples, import boundaries, validation evidence, and residual risks before completion.
- Files/modules owned: package `__init__.py` exports for collections/data/losses/objectives/metrics; public module docstrings/docs touched by phases 1-7; package/import tests; contract/integration test organization; validation summaries.
- Behavior implemented: no new product behavior beyond corrections needed to make prior phases coherent.
- Decisions applied: all FR-1 through FR-9 plus collection/sample collection refinements and DD-1 through DD-14, with emphasis on public API footprint, documentation, import boundaries, and future-roadmap guardrails.
- Future-roadmap/reuse constraints: preserve additive hooks for Stage 12 scalar/trainer/distributed adapters and Stage 13 evaluation/report/dataframe adapters without implementing them.
- Examples or demos covered: all examples 1-8.
- Out of scope: new product behavior, concrete algorithms, docs-only PRs between phase PRs, implementation-plan scope expansion.
- Dependencies: Phases 1-7.

### Tasks

- Review all package exports for code-backed names only and remove accidental placeholders.
- Confirm root `rphys` has no Stage 11 re-export creep.
- Review docs/docstrings for shapes, units, field roles, masks/reductions, metadata/provenance, grouping levels, backend-neutral limits, failure behavior, and explicit deferrals.
- Confirm import-boundary tests forbid optional backend/dataframe/report/trainer/evaluator/export/datasource imports, including direct checks that Stage 11 package imports do not import `torch` or `torchmetrics`.
- Run final relevant validation commands and record evidence in the PR body.
- Record residual risks and revisit triggers for Stage 10 drift, Stage 12 scalar/backward/distributed policy, Stage 13 table/report schema, and private helper duplication.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Validate public imports and optional dependency boundaries. | yes |
| `make test-unit` | Validate unit coverage across collection, sample collection, loss, objective, and metric records. | yes |
| `make test-contract` | Validate public extension semantics. | yes |
| relevant `make test-integration` or documented equivalent contract coverage | Validate direct field-container/sample-collection synthetic composition after base records exist, or document why contract coverage is equivalent. | yes |
| `make test-summary` | Produce repository test summary where practical. | yes |
| `uv lock --check` | Confirm dependency lock remains stable. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |
| `make validate-pr` | Run full PR validation when practical before final merge. | yes when practical |

### Acceptance Evidence

- Behavior evidence: all Stage 11 public names behave as code-backed, tested contracts.
- Design-decision evidence: no agreement queue is reopened; approved raw handles, `fields`, collection/view/collector contracts, sample collection views, and `MetricObservation` collection shape are preserved.
- Future-roadmap/reuse evidence: Stage 12/13 hooks are additive; no core torch/torchmetrics/pandas/report/trainer/evaluator/export imports.
- Example/demo evidence: examples 1-8 are covered by tests or documented snippets, including direct field-container/sample-collection synthetic composition, the implementation-plan coherence smoke, or a recorded infeasibility reason with equivalent contract coverage.
- Documentation evidence: public docs/docstrings align with scientific/workflow contracts and deferrals.
- Scientific contract evidence: final review covers NaNs/flat/short/missing data where contract-level checks apply, empty masks/groups, invalid sampling-rate metadata, dtype/device/backend mismatch metadata, leakage-sensitive grouping docs, and per-sample/per-window/record/group/dataset scope clarity.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: medium
- Implementation/refinement budget: small to medium
- PR review budget: medium
- Blocker-resolution budget: stop on public API inconsistency or missing validation evidence.
- Pre-submit blocker gate: no scope expansion, no unresolved import-boundary failure, no undocumented public contract.
- Merge record: pending

### Risks And Stop Conditions

- Risks: earlier phases pass in isolation but expose inconsistent naming, helper behavior, or import surfaces; full validation may reveal Stage 10 assumption drift.
- Stop conditions: final review discovers a reopened functionality/design decision, need for concrete algorithms, need for backend imports, or an unapproved public API expansion.
- Assumptions: phase PRs will record validation evidence and residual risk before the closeout pass.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Cross-Phase Validation

- Full relevant test command: run focused phase tests first, then broaden through `make test-package`, `make test-unit`, `make test-contract`, relevant `make test-integration`, `make test-summary`, `uv lock --check`, `git diff --check`, and `make validate-pr` when practical.
- Docs/template checks: public docstrings and any docs additions must state roles, shapes, metadata/provenance, units where known, masking/reduction descriptors, detachment/differentiability limits, grouping semantics, failure behavior, and deferrals.
- Scientific/workflow contract checks: fail loudly for invalid locators/specs, missing fields, invalid reductions/masks/totals/collections/observations/groups, undeclared or duplicate patch fields, ambiguous collection or observation views, unsupported backend metadata, and leakage-sensitive grouping ambiguity.
- Example/demo checks: maintain synthetic examples only; cover examples 1-8 with direct field containers, sample collections, and fake scalar/value handles; skip direct `MethodOutput` integration until Stage 10 lands.
- Manual review focus: API footprint, dependency direction, code-backed exports, no hidden mutation, no public `MetricResultRow`, `MetricResultTable`, or `MetricAggregationResult`, no root exports, no hard backend/dataframe/trainer/evaluator/export imports, no cross-package private helper imports, and no concrete algorithm creep.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| No readiness blocker found during drafting. | note | Planning quality gate passed and the accepted scope was converted into eight reviewable phases after the collection/sample-collection refinement. | resolved |
| Metrics phase is sequential here even though planning allowed isolated parallel work. | note | Kept sequential order for simple phase dependency and review flow; metric implementation still has isolated ownership. | resolved |
| Collection/view/collector scope was promoted into Stage 11. | medium | Added Phase 2 for reusable collection, view-plan, view, collector, and collector-result contracts before sample and metric collection phases. Views return collections; collectors may return `CollectorResult`; operation wrappers can still use `OperationResult`. | resolved |
| Sample collection reconstruction was promoted into Stage 11. | medium | Added Phase 5 for `SampleCollection`, `SampleCollectionViewPlan`, `SampleCollectionView`, and sample collector behavior before metric phases. Concrete datasource runners and signal-processing algorithms remain out of scope. | resolved |
| Revised DQ-8 traceability was stale in summary and readiness text. | medium | Updated the implementation-plan summary to DQ-1 through DQ-8 and aligned the phase tasks with DD-13/DD-14 guardrails from the formal design safety refresh. | resolved |
| Collection metadata access was under-specified. | medium | Refined Phase 2 and Phase 5 so collection iteration yields member values while explicit entry access preserves `CollectionItem[T]` metadata/provenance. `SampleCollection` therefore remains iterable over `Sample` without losing grouping/sorting metadata. | resolved |
| Collector skip/fail behavior could silently drop scientifically relevant samples. | medium | Refined Phase 2 and Phase 5 so default collector materialization is fail-loud; skipped/rejected entries require explicit policy and diagnostics in `CollectorResult`. | resolved |
| Sample collection stitching could drift into real signal-processing behavior. | medium | Refined Phase 5 to limit Stage 11 behavior to descriptors plus synthetic or injected fake stitch behavior; concrete resampling, interpolation, filtering, and physiological reconstruction remain deferred. | resolved |
| Phase 7 observation view result/state shape was under-specified. | medium | Refined Phase 7 to remove the separate aggregation/result class and reframe grouped metric behavior as reusable observation view behavior over `MetricObservation`/`MetricObservationCollection`: outputs are observations/collections with coarser or projected level/window/grouping metadata and provenance. No public streaming lifecycle, persistent state object, evaluator lifecycle, distributed sync, extra sample reconstruction, or report/dataframe output is allowed without later design review. | resolved |
| `torchmetrics` import-boundary validation was not explicit enough. | medium | Refined Phase 1 and Phase 8 to require `torchmetrics` in forbidden optional dependency checks and direct import-boundary checks for `rphys.collections`, `rphys.data`, `rphys.losses`, `rphys.objectives`, and `rphys.metrics`. | resolved |
| Synthetic integration validation was too conditional after base records exist. | low | Refined Phase 7 and Phase 8 to require direct field-container/sample-collection synthetic integration after Phases 2-6 land, or a PR-recorded infeasibility reason with equivalent contract coverage. | resolved |
| Current revised design implication/future-roadmap safety/coherence audit passed. | note | Read back `planning.md` after the current revised audit: DQ-1 through DQ-8 remain resolved, no queue item was reopened, examples 1-8 are locked, and the eight-phase implementation plan remains coherent. | resolved |

Gate result:

- Status: passed and approved for implementation after design-pass refinement.
- Review evidence: gates, queues, design triage, future-roadmap safety, examples 1-8, validation strategy, phase shaping, plan quality gate, implementation-plan approval, and the current revised design implication/future-roadmap safety/coherence audit were read from `docs/roadmap/stage-11/planning.md`; post-approval design review findings were incorporated above.
- Accepted risks: backend-neutral scalar/value metadata is looser until Stage 12; TorchMetrics/torchmetrics remains optional future adapter pressure; patch-only results may need later apply adapters; identity-as-groups/metadata may need Stage 13 refinement; sample entry metadata remains metadata-based rather than first-class fields; package-local helper duplication is accepted to avoid hidden API.
- Revisit triggers: Stage 10 implementation lands or changes field/result patch shape; Stage 12 needs stricter scalar/backward/distributed contracts; Stage 13 needs first-class metric or sample identity fields, report/dataframe adapters, evaluator-owned sample collection runner policy, concrete reconstruction algorithms, or evaluator observation view lifecycle; repeated helper duplication causes inconsistent errors; any Stage 11 core import crosses forbidden boundaries.

## Final Approval

- Approval status: approved by maintainer on 2026-05-16; formal revised-scope design safety refresh and the current revised design implication/future-roadmap safety/coherence audit upheld DQ-8/DD-13/DD-14 with guardrails and did not reopen approval.
- Approved scope: eight phases in this plan: error/import scaffold, shared collection/view/collector contracts, loss contracts, objective contracts, sample collection views, metric observation collection contracts, metric observation views/composition, and API/docs/import/validation closeout.
- Accepted risks: backend-neutral scalar/value metadata remains loose until Stage 12; TorchMetrics/torchmetrics remains optional future adapter pressure; patch-only results may need later apply adapters; identity-as-groups/metadata and sample entry metadata may need Stage 13 refinement; package-local helper duplication is accepted to avoid hidden API.
- Deferred items: concrete loss/metric catalogs, backend adapters, torchmetrics integration, learner/trainer behavior, evaluator/report/export behavior, dataframe/report schemas, concrete signal-processing stitching/resampling/interpolation algorithms, first-class metric identity fields, public scalar/backward protocol, public/shared selector helper, and broad `Measure` base.
