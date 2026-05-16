# Roadmap Stage 10 Implementation Plan

Status: implemented; all phases merged and recorded
Roadmap version: `v10`
Planning document: `docs/roadmap/stage-10/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: all phases merged
Blockers: none

## Summary

- Goal: implement dependency-light base contracts for `rphys.methods`, `rphys.models`, and optional protocol-only `rphys.nn` helpers so methods consume `Batch` fields, models stay below `Batch`, and later losses, learners, trainers, prediction runners, and export/evaluation stages can compose the result without Stage 10 owning those later behaviors.
- Source functionality-agreement gate: passed on 2026-05-15; FQ-0 through FQ-8 are repo-resolved after the maintainer-directed LIST uncollation design pass.
- Approved behavior: `Method.predict(batch, *, context=None) -> MethodOutput`; `MethodOutput` is patch-like; explicit merge/apply conversion owns any patch-to-`Batch` behavior; `PredictionContext` carries only generic primitive metadata/provenance and does not define first-class domain identifiers such as sample IDs; adapters parse selectors at construction; models do not import or consume `Batch`; state/trainable records are backend-neutral; no hard torch dependency or core torch import.
- Source behavior confirmation: passed on 2026-05-15 with included/default/failure/unsupported behavior locked.
- Key design constraints: scoped public imports only; no root exports; no registries or placeholder public names; no Stage 10 torch helper; no concrete algorithms; no trainer/export/loss/metric/device/checkpoint behavior; no Stage 9 loader/cache/prepared-data dependency.
- Source design-agreement gate: passed on 2026-05-15 after maintainer approval for DQ-2 and DQ-6.
- Source functionality-agreement queue: FQ-0 through FQ-8 resolved with no blocked or maintainer-discussion items.
- Source design-agreement queue: DQ-0 is locked by maintainer direction; DQ-1, DQ-3, DQ-4, DQ-5, and DQ-7 are recorded recommendations or auto-approved private detail; DQ-2 and DQ-6 are locked by maintainer approval; no decision is blocked, pending approval, or ready for approval.
- Source future-roadmap/reuse safety review: Stage 11-13 compatibility is carried through patch-like outputs, explicit conversion, model-below-`Batch`, descriptive state/parameter records, private helper revisit triggers, and deferred backend helpers.
- Lightning fit review: no additional Stage 10 phase or public Lightning API is needed. Lightning remains a Stage 12/15 optional adapter target that should wrap rphys `Learner`/`Trainer` semantics, use Stage 12 optimizer/device/checkpoint policies, and map Lightning loop hooks/callbacks into rphys `TrainingEvent`/profiling records.
- Examples covered: LIST collate/uncollate round trip, synthetic echo method over a `Batch`, synthetic model independent of `Batch`, backend-neutral trainable fake, context-aware prediction, and explicit prediction merge.
- Current data-layer audit note: exact `Batch` to `Sample` uncollation is expected by maintainer direction but is not currently implemented as a validated public guarantee; Stage 10 must not assume lossless sample reconstruction until the Stage 2/9 collation path is repaired and tested.
- Design review refresh: Stage 10 may refactor landed shared collation/collater code in `rphys.data` to satisfy DD-0, but it must not change Stage 9 planning artifacts or move loader/cache/prepared responsibilities into Stage 10. Stage 10 should preserve generic metadata/provenance only; domain-specific identifiers such as sample IDs remain caller-owned metadata outside the Stage 10 public context shape.
- Source phase shaping: Phase 0 plus four accepted Stage 10 phases: LIST collation round-trip repair; core public contracts/import boundaries; adapter specs and explicit output application; stateful/trainable capability records; synthetic contract integration, docs, and full validation.
- Source plan quality gate: passed on 2026-05-15 with no missing/stale specialist evidence, unresolved agreement packet, or queue-reopen need.
- Out of scope: concrete CHROM/POS/neural baselines, model zoo, losses/objectives/metrics, learners/trainers, optimizers/schedulers/checkpoints, device/distributed behavior, dataloaders, prediction export, evaluation/reporting, workflow runtime, Lightning/Fabric adapters, optional torch helpers, and edits to `docs/roadmap.md`.

## Implementation Workflow State

- Implementation-plan quality gate: passed
- Review pass: completed 2026-05-15 / manager review
- Refinement pass: completed 2026-05-16 / generic metadata phase pass
- Confirmation review: completed 2026-05-16 / maintainer implementation approval
- Automatic merge mode: enabled
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | `list-uncollation-roundtrip` | merged | `agent/stage-10-method-model-contracts-p0-list-uncollation-roundtrip` | [#66](https://github.com/samcantrill/rphys/pull/66) | `src/rphys/data/collation.py`, `src/rphys/data/__init__.py`, focused data/package/contract/integration tests, docs/docstrings | Make default LIST batches unlist back to `tuple[Sample, ...]` before method/model contracts rely on sample reconstruction. | data collation round-trip unit tests; batch collater contract tests; landed Stage 9 torch-collater integration; `make test-package`; `git diff --check` | LIST collate/uncollate round trip with explicit `None` vs missing metadata and generic metadata preservation |
| 1 | `core-contracts-imports` | merged | `agent/stage-10-method-model-contracts-p1-core-contracts-imports` | [#67](https://github.com/samcantrill/rphys/pull/67) | `src/rphys/methods/core.py`, `src/rphys/methods/context.py`, `src/rphys/methods/output.py`, `src/rphys/models/core.py`, scoped package exports, package/unit/contract tests for these names | Establish code-backed public `Method`, `Model`, `PredictionContext`, and patch-like `MethodOutput` with lightweight imports. | `make test-package`; focused context/output unit tests; method/model contract probes; `git diff --check` | context-aware prediction; synthetic model-independent contract probes |
| 2 | `adapters-output-apply` | merged | `agent/stage-10-method-model-contracts-p2-adapters-output-apply` | [#68](https://github.com/samcantrill/rphys/pull/68) | `src/rphys/methods/adapters.py`, private methods validation helpers, explicit `MethodOutput` merge/apply conversion, adapter/output tests | Implement the `Batch`/`FieldLocator` bridge and explicit patch-to-`Batch` application. | adapter unit matrix; output/apply tests; method contract tests using adapters; focused synthetic integration if apply is present | synthetic echo method; explicit prediction merge |
| 3 | `state-trainable-records` | merged | `agent/stage-10-method-model-contracts-p3-state-trainable-records` | [#69](https://github.com/samcantrill/rphys/pull/69) | `src/rphys/methods/state.py`, optional protocol-only `src/rphys/nn/protocols.py` only if code-backed by capability records, package exports, state/trainable tests | Add richer backend-neutral state and parameter capability records without torch, optimizer, checkpoint, or device semantics. | `tests/contracts/test_trainable_method_contract.py`; `tests/unit/rphys/methods/test_state.py`; `make test-package`; `git diff --check` | non-torch trainable fake |
| 4 | `synthetic-integration-docs-validation` | merged | `agent/stage-10-method-model-contracts-p4-synthetic-integration-docs-validation` | [#70](https://github.com/samcantrill/rphys/pull/70) | test-only fake methods/models/stateful objects, synthetic `Batch` fixtures, docs/docstrings or glossary updates if public vocabulary changes, full validation evidence | Prove Stage 10 contracts compose without concrete algorithms, Stage 9 loaders, or heavy optional dependencies. | focused integration; `make test-package`; `make test-unit`; `make test-contract`; `make test-integration`; final `make test`; `make test-summary`; `uv lock --check`; `git diff --check` | all recorded examples, including arbitrary backend-native state/parameter handles |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| Core Stage 10 phases depend on a repaired data-layer uncollation contract. | `docs/roadmap/stage-10/planning.md` DD-0 / Phase 0 design pass | Execute Phase 0 first. Reopen the design queue only if LIST uncollation cannot return `tuple[Sample, ...]`, preserve explicit `None` versus missing metadata, preserve generic metadata/provenance without defining domain-specific keys, or fail loudly for non-reversible fields. | resolved by Phase 0 sequencing |

## Phase 0: LIST Collation Round-Trip Repair

Status: merged
Slug: `list-uncollation-roundtrip`
Branch: `agent/stage-10-method-model-contracts-p0-list-uncollation-roundtrip`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p0-list-uncollation-roundtrip`
PR: [#66](https://github.com/samcantrill/rphys/pull/66)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: make default LIST-collated `Batch` containers unlist back to `tuple[Sample, ...]` before method/model contracts rely on sample reconstruction.
- Files/modules owned: `src/rphys/data/collation.py`, `src/rphys/data/__init__.py`, focused tests under `tests/unit/rphys/data/test_collation.py`, `tests/contracts/test_batch_collater_contract.py`, required focused integration for the existing Stage 9 torch collater flow, and only necessary docstrings.
- Behavior implemented: public `uncollate_batch(batch, ...) -> tuple[Sample, ...]`; default LIST collation remains unchanged as the only supported base policy; collation records enough evidence to distinguish missing metadata from explicit `None`; generic field metadata/provenance round-trips where reversible; non-reversible fields fail loudly. Any required refactor of landed `BatchCollater` behavior stays in Stage 10 Phase 0 and does not alter Stage 9 plans.
- Decisions applied: DD-0, FR-0, FQ-0, and the generic metadata/provenance posture for Stage 10.
- Future-roadmap/reuse constraints: keep uncollation in `rphys.data`, not in methods, learners, trainers, or export helpers; future stack/pad/drop/custom collation policies must define separate inverse semantics before they can participate.
- Examples or demos covered: `tuple[Sample, ...] -> Batch -> tuple[Sample, ...]` with sparse generic metadata and explicit `None`.
- Out of scope: stack/pad/drop/custom policies, device movement, model tuple formatting, trainer batching, durable serialization, and silently skipping batch-level scalar fields.
- Dependencies: existing Stage 2 LIST collation and landed Stage 9 collater behavior for focused integration validation.

### Tasks

- Add public `uncollate_batch` and export it from `rphys.data`.
- Add internal collation evidence or equivalent container metadata so uncollation can reconstruct per-sample metadata presence without treating private evidence as ordinary user metadata.
- Preserve current LIST collation behavior for users while making exact round trip testable.
- Do not add first-class sample or batch identifier fields to Stage 10 contexts; preserve domain-specific identifiers only if they already exist as caller-owned metadata on reversible fields.
- Add fail-loud validation for ambiguous sample count, non-LIST fields, payload length mismatch, metadata alignment mismatch, and unsupported batch-level scalar fields.
- Add focused docs/docstrings explaining that `tuple[Sample, ...]` is the stable return shape; callers may convert to `list` if they need mutable collection operations.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/data/test_collation.py` | Validate LIST round trip, explicit `None` versus missing metadata, mismatched lengths, and non-LIST failures. | yes |
| `uv run pytest tests/contracts/test_batch_collater_contract.py` | Validate the public collater/uncollater contract remains FieldLocator-keyed and non-model-formatted. | yes |
| `uv run pytest tests/integration/test_stage9_torch_collater_flow.py` | Validate the existing framework collater path still produces reversible FieldLocator-keyed batches. | yes |
| `make test-package` | Prove data exports remain code-backed and imports stay lightweight. | yes |
| `git diff --check` | Catch whitespace and Markdown/code formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: reversible LIST batches uncollate to `tuple[Sample, ...]`; explicit `None` metadata and absent metadata remain distinguishable.
- Design-decision evidence: uncollation remains data-layer behavior; methods and trainers do not own sample reconstruction.
- Future-roadmap/reuse evidence: Stage 11-13 can recover LIST-aligned fields and generic metadata through the data-layer inverse without method-owned reconstruction.
- Example/demo evidence: round-trip tests cover payloads, schemas, collate policies, locators, sparse metadata, and explicit `None`.
- Documentation evidence: public docstrings explain tuple return, fail-loud non-LIST behavior, and unsupported batch-level scalar fields.
- Scientific contract evidence: field semantics and generic metadata are preserved without hidden payload inference or metadata loss.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-10/phases/list-uncollation-roundtrip.md`
- Planning/refinement budget: one planning pass focused on exact round-trip semantics and metadata evidence placement.
- Implementation/refinement budget: one implementation pass plus targeted round-trip/failure refinement.
- PR review budget: one review pass focused on no metadata leakage, no model formatting, and no future collation-policy overreach.
- Blocker-resolution budget: stop and reopen design if exact LIST round trip requires public metadata pollution, broad schema changes, or non-LIST policy expansion.
- Pre-submit blocker gate: all Phase 0 validation rows must pass or record explicit risk.
- Merge record: completed below

### Risks And Stop Conditions

- Risks: adding private collation evidence could leak into public metadata; exact object identity is not guaranteed, so tests must focus on field semantics; future non-LIST policies remain unsupported.
- Stop conditions: `uncollate_batch` silently drops fields, returns mutable list by default, cannot distinguish missing metadata from explicit `None`, adds first-class domain identifiers to Stage 10 contexts, requires Stage 9 plan changes, or moves logic into methods/trainers.
- Assumptions: preserving per-sample field semantics is the contract; original `Sample` object identity is not.

### Completion Summary

- Implementation: added public `uncollate_batch`, private LIST collation evidence, scoped `rphys.data` export, and fail-loud validation for ambiguous or edited batches.
- Validation: `uv run pytest tests/unit/rphys/data/test_collation.py`; `uv run pytest tests/contracts/test_batch_collater_contract.py`; `uv run pytest tests/integration/test_stage9_torch_collater_flow.py`; `make test-package`; `make validate-pr`; `make test-summary`; `git diff --check`.
- PR: [#66](https://github.com/samcantrill/rphys/pull/66)
- Merge: merged to `develop` on 2026-05-16 as `739960887b0aab181fb8347ed443f03fcc2887e9`.
- Follow-up: future non-LIST collation policies must define separate inverse semantics before participating in uncollation.

### Merge Record

- Phase: Phase 0 `list-uncollation-roundtrip`
- Branch: `agent/stage-10-method-model-contracts-p0-list-uncollation-roundtrip`
- PR: [#66](https://github.com/samcantrill/rphys/pull/66)
- Base branch: `develop`
- Merge command: `gh pr merge 66 --squash --delete-branch`
- Merge result: merged; GitHub reported no status checks for the branch, so merge relied on the completed local validation gate.
- Merge commit: `739960887b0aab181fb8347ed443f03fcc2887e9`
- Branch cleanup: remote branch deleted by GitHub; local branch cleanup pending worktree removal.
- Worktree cleanup: pending after metadata commit.
- Behavior implemented: default LIST-collated `Batch` containers can uncollate to `tuple[Sample, ...]` while preserving field locators, payload order, schemas, collate policies, and sparse metadata presence.
- Tests and validation: focused unit/contract/integration checks passed; `make validate-pr` passed; `make test-summary` reported package 41 passed, unit 628 passed, contract 118 passed, integration 18 passed, and no e2e/acceptance suites present.
- Documentation: phase plan and PR body artifacts added under `docs/roadmap/stage-10/phases/`; public docstrings describe tuple return and fail-loud LIST-only behavior.
- Scientific contract implications: sample-field semantics and caller-owned generic metadata round-trip without first-class domain identifiers or method/trainer-owned reconstruction.
- Follow-up notes for later phases: Stage 10 methods may rely on data-layer LIST reconstruction, but copied/manual/non-LIST batches still need explicit future inverse semantics.

## Phase 1: Core Public Contracts And Import Boundaries

Status: merged
Slug: `core-contracts-imports`
Branch: `agent/stage-10-method-model-contracts-p1-core-contracts-imports`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p1-core-contracts-imports`
PR: [#67](https://github.com/samcantrill/rphys/pull/67)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: establish the smallest code-backed Stage 10 public surface for method/model prediction contracts while preserving lightweight imports.
- Files/modules owned: `src/rphys/methods/core.py`, `src/rphys/methods/context.py`, `src/rphys/methods/output.py`, `src/rphys/models/core.py`, `src/rphys/methods/__init__.py`, `src/rphys/models/__init__.py`, package/unit/contract tests for these names, and only necessary docstrings.
- Behavior implemented: structural `Method.predict` contract, structural generic `Model` contract below `Batch`, primitive immutable `PredictionContext` with generic metadata/provenance only, patch-like `MethodOutput` with fields/diagnostics/metadata/provenance, scoped package exports, and no root exports.
- Decisions applied: DD-1, DD-2, DD-3/DQ-2, DD-5, DD-6, DD-8, DD-10.
- Future-roadmap/reuse constraints: keep `MethodOutput` usable by Stage 11-13 without returning `Batch`; keep `Model` free of `Batch`, datasource, loader, torch, loss, metric, trainer, and export imports; do not introduce dtype/device context fields or other backend policy in Stage 10. Preserve the later Lightning path by making actual backend-native callables, including `torch.nn.Module` objects, able to satisfy the structural `Model` protocol without Stage 10 declaring Lightning lifecycle hooks.
- Examples or demos covered: context-aware prediction and model contract probes using synthetic fakes, without adapters or Stage 9 loaders.
- Out of scope: adapters, merge/apply helper, state/trainable records, concrete algorithms, losses, metrics, trainers, device movement, checkpoints, torch helpers, and public model input/output records.
- Dependencies: approved planning artifact; Phase 0 LIST uncollation repair merged; existing `Batch` and `FieldLocator` may be imported by `rphys.methods` only as needed for the method contract, not by `rphys.models`.

### Tasks

- Add scoped modules and package exports for only implemented public names.
- Define immutable/copy-protected records for `PredictionContext` and `MethodOutput` with primitive metadata/provenance/diagnostics handling and no first-class domain identifiers.
- Define structural `Method` and `Model` protocols without inheritance or framework requirements.
- Add package/import-boundary assertions proving base imports do not load torch or other heavy optional stacks.
- Add focused unit and contract probes for record immutability, primitive metadata/provenance copying, structural conformance, no default mutation, and no training/export/loss/metric side effects.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Prove scoped public imports are code-backed and lightweight. | yes |
| `uv run pytest tests/unit/rphys/methods/test_context.py tests/unit/rphys/methods/test_output.py` | Validate context/output record behavior. | yes |
| `uv run pytest tests/contracts/test_method_contract.py tests/contracts/test_model_contract.py` | Validate structural method/model contracts and boundaries. | yes |
| `git diff --check` | Catch whitespace and Markdown/code formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: fake `Method` returns `MethodOutput`; fake `Model` works below `Batch`; context is primitive and immutable with generic metadata/provenance only.
- Design-decision evidence: `Method.predict` returns patch-like `MethodOutput`; no `Batch` return from the contract; no public base-class requirement.
- Future-roadmap/reuse evidence: Stage 11-13 can consume fields from a patch; Stage 12 can compose a structural method/model without trainer coupling.
- Example/demo evidence: context-aware fake prediction and model-isolation probe.
- Documentation evidence: docstrings state shapes, roles, provenance, and out-of-scope training/export/loss/device behavior.
- Scientific contract evidence: prediction outputs retain field/provenance semantics and do not choose splits, mutate silently, export files, or update metrics.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-10/phases/core-contracts-imports.md`
- Planning/refinement budget: one planning pass plus one refinement pass if public import names or record fields drift.
- Implementation/refinement budget: one implementation pass plus targeted test-refinement pass.
- PR review budget: one review pass focused on public API/import boundaries and patch-output semantics.
- Blocker-resolution budget: stop and reopen design if the implementation needs a `Batch` return, core torch helper, or model access to runtime containers.
- Pre-submit blocker gate: all required validation rows above must pass or record explicit risk.
- Merge record: completed below

### Risks And Stop Conditions

- Risks: public import paths may need additive fields later; record semantics could accidentally become too broad; model contract may leak `Batch` or backend assumptions.
- Stop conditions: any proposal for hard torch dependency, `rphys.nn.torch`, default `Batch` return, root export, model import of `Batch`/datasources/loaders, loss/metric/export/trainer behavior, Lightning lifecycle hooks, optimizer/device/checkpoint policy, or undocumented mutation.
- Assumptions: exact record field names may be refined if the locked semantics remain intact and tests/docs reflect the behavior.

### Completion Summary

- Implementation: added `PredictionContext`, `MethodOutput`, structural `Method`, structural generic `Model`, scoped methods/models package exports, private primitive mapping validation, and package/unit/contract coverage.
- Validation: `uv run pytest tests/unit/rphys/methods/test_context.py tests/unit/rphys/methods/test_output.py`; `uv run pytest tests/contracts/test_method_contract.py tests/contracts/test_model_contract.py`; `make test-package`; `make validate-pr`; `make test-summary`; `git diff --check`.
- PR: [#67](https://github.com/samcantrill/rphys/pull/67)
- Merge: merged to `develop` on 2026-05-16 as `512e0c6a5dd66954d2f58f38ed8d9a4929e2b219`.
- Follow-up: Phase 2 owns adapters and explicit output application; Phase 3 owns state/trainable records.

### Merge Record

- Phase: Phase 1 `core-contracts-imports`
- Branch: `agent/stage-10-method-model-contracts-p1-core-contracts-imports`
- PR: [#67](https://github.com/samcantrill/rphys/pull/67)
- Base branch: `develop`
- Merge command: `gh pr merge 67 --squash`
- Merge result: merged; GitHub reported no status checks for the branch, so merge relied on the completed local validation gate.
- Merge commit: `512e0c6a5dd66954d2f58f38ed8d9a4929e2b219`
- Branch cleanup: pending after metadata commit.
- Worktree cleanup: pending after metadata commit.
- Behavior implemented: methods expose primitive `PredictionContext`, patch-like `MethodOutput`, and structural `Method`; models expose a structural generic callable `Model` without importing `Batch`.
- Tests and validation: focused unit and contract checks passed; `make validate-pr` passed; `make test-summary` reported package 47 passed, unit 637 passed, contract 123 passed, integration 18 passed, and no e2e/acceptance suites present.
- Documentation: phase plan and PR body artifacts added under `docs/roadmap/stage-10/phases/`; public docstrings describe patch output, primitive context, structural protocols, and out-of-scope trainer/export/loss/device behavior.
- Scientific contract implications: prediction outputs remain explicit field patches with caller-owned primitive provenance and no domain identifier, split, device, checkpoint, training, export, loss, or metric policy.
- Follow-up notes for later phases: Phase 2 should use these records for adapters and explicit patch application without changing `Method.predict` return semantics.

## Phase 2: Adapter Specs And Explicit Output Application

Status: merged
Slug: `adapters-output-apply`
Branch: `agent/stage-10-method-model-contracts-p2-adapters-output-apply`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p2-adapters-output-apply`
PR: [#68](https://github.com/samcantrill/rphys/pull/68)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement the explicit bridge between `Batch`/`FieldLocator` fields and model/method inputs/outputs, including explicit patch-to-`Batch` application.
- Files/modules owned: `src/rphys/methods/adapters.py`, local private validation helpers in `src/rphys/methods/`, any explicit output apply helper colocated with `MethodOutput`, methods package exports, adapter/output unit tests, method contract tests using adapters, and focused synthetic integration tests if the apply helper is exercised.
- Behavior implemented: `MethodInputSpec`, `MethodOutputSpec`, `MethodInputAdapter`, `MethodOutputAdapter`, construction-time locator parsing, duplicate-name/locator checks, optional expected type/schema checks, output role validation, model-output arity/name checks, typed failures, and explicit merge/apply conversion with documented copy/conflict behavior.
- Decisions applied: DD-3/DQ-2, DD-4, DD-9, DD-10.
- Future-roadmap/reuse constraints: adapters remain the only `Batch`/`FieldLocator` bridge; private helpers stay private until Stage 11 repeats identical selector/spec semantics; explicit apply supports Stage 13-style conversion without implementing export; no public registry or schema language.
- Examples or demos covered: synthetic echo method and explicit prediction merge demonstration.
- Out of scope: model input/output public records, datasource/index/sample-builder/dataloader access, device movement, file export, metric/loss computation, shared public validation package, and trainer-owned result schemas.
- Dependencies: Phase 1 public contracts and output/context records.

### Tasks

- Add frozen input/output spec records that normalize string or typed locators at construction.
- Add adapters that extract declared `Batch` fields and map named method/model outputs into `MethodOutput` fields.
- Add explicit apply/merge conversion for `MethodOutput` patches to a caller-selected `Batch` copy/target with conflict policy documented and tested.
- Add private validation for duplicate names, duplicate locators, invalid roles, missing fields, wrong payload/schema/type, undeclared outputs, and invalid model result shape.
- Extend contract/integration tests so no path performs hidden mutation, file export, metric update, or training behavior.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/methods/test_adapters.py` | Validate specs, locator parsing, extraction, output mapping, and failure behavior. | yes |
| `uv run pytest tests/unit/rphys/methods/test_output.py` | Validate explicit apply/merge copy and conflict semantics. | yes |
| `uv run pytest tests/contracts/test_method_contract.py` | Validate adapter-backed method behavior and non-mutation default. | yes |
| `uv run pytest tests/integration/test_synthetic_method_prediction_flow.py` | Validate synthetic batch -> adapter -> model/method -> patch -> explicit apply flow when available. | yes |
| `make test-package` | Recheck imports remain lightweight after adapters. | yes |
| `git diff --check` | Catch formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: adapters extract declared fields and output declared `FieldLocator` patches; explicit apply is the only patch-to-`Batch` route.
- Design-decision evidence: `MethodOutput` remains patch-only; conflict/copy behavior is explicit; private validation helpers are not exported.
- Future-roadmap/reuse evidence: Stage 11 selector/spec reuse remains a revisit trigger, not a public utility now; Stage 13 can convert predictions without Stage 10 export behavior.
- Example/demo evidence: synthetic echo method and explicit merge tests.
- Documentation evidence: docstrings or docs explain selector parsing time, field role validation, output patch semantics, and conflict/copy policy.
- Scientific contract evidence: locator roles, metadata/provenance, and schema/type expectations are preserved or fail loudly.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-10/phases/adapters-output-apply.md`
- Planning/refinement budget: one planning pass with extra attention to merge/apply conflict policy.
- Implementation/refinement budget: one implementation pass plus targeted adapter failure refinement.
- PR review budget: one review pass focused on selector parsing, output role validation, and explicit apply behavior.
- Blocker-resolution budget: stop and reopen design if adapters need datasource/dataloader access, a public schema language, direct export, or default mutation.
- Pre-submit blocker gate: adapter/output/contract/integration tests and package imports must pass or record risk.
- Merge record: completed below

### Risks And Stop Conditions

- Risks: adapter specs may grow into a premature schema language; merge/apply could hide mutation if copy semantics are vague; failure diagnostics may be too broad.
- Stop conditions: default `predict` mutation, `Method.predict` returning `Batch`, file export, metric/loss computation, datasource/loader access, public helper registry, or shared public validation utility.
- Assumptions: existing `Batch`/`FieldLocator`/`FieldValue` APIs are sufficient for extraction and patch application.

### Completion Summary

- Implementation: added `MethodInputSpec`, `MethodOutputSpec`, `MethodInputAdapter`, `MethodOutputAdapter`, explicit `apply_method_output`, scoped methods exports, adapter-backed method contract coverage, and synthetic prediction integration.
- Validation: `uv run pytest tests/unit/rphys/methods/test_adapters.py`; `uv run pytest tests/unit/rphys/methods/test_output.py`; `uv run pytest tests/contracts/test_method_contract.py`; `uv run pytest tests/integration/test_synthetic_method_prediction_flow.py`; `make test-package`; `make test-unit`; `make validate-pr`; `make test-summary`; `git diff --check`.
- PR: [#68](https://github.com/samcantrill/rphys/pull/68)
- Merge: merged to `develop` on 2026-05-16 as `1766df6f68a1cf63f88e0d11e337f8370ad666fa`.
- Follow-up: Stage 11/13 may factor shared selector semantics only after repeated use; future copied/non-LIST uncollation semantics remain separate.

### Merge Record

- Phase: Phase 2 `adapters-output-apply`
- Branch: `agent/stage-10-method-model-contracts-p2-adapters-output-apply`
- PR: [#68](https://github.com/samcantrill/rphys/pull/68)
- Base branch: `develop`
- Merge command: `gh pr merge 68 --squash`
- Merge result: merged; GitHub reported no status checks for the branch, so merge relied on the completed local validation gate.
- Merge commit: `1766df6f68a1cf63f88e0d11e337f8370ad666fa`
- Branch cleanup: pending after metadata commit.
- Worktree cleanup: pending after metadata commit.
- Behavior implemented: adapter specs normalize field locators and validate names/roles/type/schema; input adapters extract named payloads from `Batch`; output adapters map named results to `MethodOutput`; explicit patch application copies by default and has explicit conflict policy.
- Tests and validation: focused adapter/output/contract/integration checks passed; `make validate-pr` passed; `make test-summary` reported package 47 passed, unit 649 passed, contract 124 passed, integration 19 passed, and no e2e/acceptance suites present.
- Documentation: phase plan and PR body artifacts added under `docs/roadmap/stage-10/phases/`; public docstrings describe selector parsing time, output patch semantics, and explicit apply behavior.
- Scientific contract implications: field roles, locators, schema/type checks, and provenance remain explicit without datasource/loader access, hidden mutation, export, loss, metric, or trainer behavior.
- Follow-up notes for later phases: Phase 4 can use the synthetic adapter flow for final composition checks; Phase 3 state/trainable records remain independent.

## Phase 3: Stateful And Trainable Capability Records

Status: merged
Slug: `state-trainable-records`
Branch: `agent/stage-10-method-model-contracts-p3-state-trainable-records`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p3-state-trainable-records`
PR: [#69](https://github.com/samcantrill/rphys/pull/69)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: add DQ-6-approved richer backend-neutral state and parameter records for future learners/trainers without owning optimizer, checkpoint, device, distributed, or torch behavior.
- Files/modules owned: `src/rphys/methods/state.py`, `src/rphys/methods/core.py` only for `StatefulMethod`/`TrainableMethod` protocol links if needed, `src/rphys/methods/__init__.py`, optional code-backed `src/rphys/nn/protocols.py` and `src/rphys/nn/__init__.py` only if the capability records need shared protocol helpers, state/trainable unit and contract tests, and relevant docstrings.
- Behavior implemented: `StatefulMethod`, `TrainableMethod`, `StateView`, `StateEntry`, `StateLoadResult`, `ParameterView`, strict-load success/failure diagnostics, primitive metadata/provenance, named state entries and parameter handles, and trainability/update flags where applicable.
- Decisions applied: DD-7/DQ-6, DD-8, DD-10.
- Future-roadmap/reuse constraints: records stay descriptive and backend-neutral; Stage 12 owns optimizer groups, schedulers, checkpoint metadata/writers, device movement, distributed behavior, and framework adapters; optional torch helpers remain deferred. Do not add torch/Lightning-style lifecycle hooks such as `training_step`, `validation_step`, `configure_optimizers`, `.to()`, precision, compile, logging, callback, or checkpoint behavior to `Model`, `Method`, or capability records.
- Examples or demos covered: non-torch trainable fake with plain Python state and sentinel parameter handles.
- Out of scope: optimizer factories, parameter groups, schedulers, checkpoint schemas/files, device placement/movement, distributed state, `torch.nn.Module` helpers, Lightning/Fabric integration, and hard optional dependency imports.
- Dependencies: Phase 1 import/export conventions; Phase 2 is not required unless tests reuse output helpers.

### Tasks

- Define immutable/copy-protected state and parameter records with inspectable names, handles/values, metadata/provenance, and diagnostic fields.
- Define structural capability protocols using the approved richer records and names equivalent to `state()`, `load_state(..., strict=True)`, and `parameters()`.
- Add non-torch fake capability implementations for contract tests.
- Add package import tests proving no torch or heavy optional module is loaded by methods/models/nn imports.
- Document that records are descriptive and do not encode optimizer, checkpoint, device, distributed, or backend-specific semantics.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/methods/test_state.py` | Validate state/parameter records and strict-load diagnostics. | yes |
| `uv run pytest tests/contracts/test_trainable_method_contract.py` | Validate `StatefulMethod`/`TrainableMethod` structural behavior with non-torch fakes. | yes |
| `make test-package` | Prove capability imports remain lightweight and torch-free. | yes |
| `uv run pytest tests/contracts/test_method_contract.py` | Recheck capability additions do not change base method prediction semantics. | yes |
| `git diff --check` | Catch formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: fake stateful/trainable methods expose named state and parameter records and report strict-load diagnostics.
- Design-decision evidence: richer records are implemented; no bare torch-style-only `state_dict`/`parameters()` contract replaces them.
- Future-roadmap/reuse evidence: Stage 12 can inspect records later while optimizer/checkpoint/device policy remains absent.
- Example/demo evidence: non-torch trainable fake with plain Python values and sentinel handles.
- Documentation evidence: docstrings explain backend-neutral handles, metadata/provenance, trainability flags, and deferred optimizer/checkpoint/device semantics.
- Scientific contract evidence: method state and parameters are inspectable without hidden backend movement, checkpoint writes, or training side effects.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-10/phases/state-trainable-records.md`
- Planning/refinement budget: one planning pass focused on public record fields and naming.
- Implementation/refinement budget: one implementation pass plus targeted diagnostics refinement.
- PR review budget: one review pass focused on no torch/optimizer/checkpoint/device leakage.
- Blocker-resolution budget: stop and reopen design if records must encode optimizer groups, checkpoint schemas, device movement, distributed state, or torch helpers.
- Pre-submit blocker gate: state/unit/contract/package validation rows must pass or record risk.
- Merge record: completed below

### Risks And Stop Conditions

- Risks: richer records may still need additive fields once Stage 12 defines optimizer groups or checkpoint metadata; `rphys.nn` could grow placeholder names if not tied to code-backed behavior.
- Stop conditions: core torch import, Stage 10 torch helper, optimizer/scheduler/checkpoint/device/distributed fields, Lightning/Fabric integration, lifecycle hooks copied from torch/Lightning, or capability records that require trainer objects.
- Assumptions: final method names may be close equivalents to the planning examples if the approved semantics and tests remain intact.

### Completion Summary

- Implementation: added `StateEntry`, `StateView`, `StateLoadResult`, `ParameterView`, structural `StatefulMethod`/`TrainableMethod`, scoped methods exports, and non-torch unit/contract coverage.
- Validation: `uv run pytest tests/unit/rphys/methods/test_state.py`; `uv run pytest tests/contracts/test_trainable_method_contract.py`; `uv run pytest tests/contracts/test_method_contract.py`; `make test-package`; `make validate-pr`; `make test-summary`; `git diff --check`.
- PR: [#69](https://github.com/samcantrill/rphys/pull/69)
- Merge: merged to `develop` on 2026-05-16 as `f5b6451346744f6de18faa54c280fd6b62d3f98a`.
- Follow-up: optimizer groups, checkpoint schemas, device movement, distributed state, and optional torch/Lightning helpers remain deferred.

### Merge Record

- Phase: Phase 3 `state-trainable-records`
- Branch: `agent/stage-10-method-model-contracts-p3-state-trainable-records`
- PR: [#69](https://github.com/samcantrill/rphys/pull/69)
- Base branch: `develop`
- Merge command: `gh pr merge 69 --squash`
- Merge result: merged; GitHub reported no status checks for the branch, so merge relied on the completed local validation gate.
- Merge commit: `f5b6451346744f6de18faa54c280fd6b62d3f98a`
- Branch cleanup: pending after metadata commit.
- Worktree cleanup: pending after metadata commit.
- Behavior implemented: state/load/parameter records expose named backend-neutral values and handles with primitive metadata/provenance and strict-load diagnostics; stateful/trainable protocols remain structural.
- Tests and validation: focused state/trainable/method/package checks passed; `make validate-pr` passed; `make test-summary` reported package 47 passed, unit 654 passed, contract 128 passed, integration 19 passed, and no e2e/acceptance suites present.
- Documentation: phase plan and PR body artifacts added under `docs/roadmap/stage-10/phases/`; public docstrings describe backend-neutral state/parameter semantics and deferred optimizer/checkpoint/device behavior.
- Scientific contract implications: state and parameters are inspectable without hidden backend movement, checkpoint writes, optimizer policy, distributed state, or training side effects.
- Follow-up notes for later phases: Phase 4 should compose the non-torch trainable fake with the existing synthetic method flow for final validation.

## Phase 4: Synthetic Contract Integration, Docs, And Full Validation

Status: merged
Slug: `synthetic-integration-docs-validation`
Branch: `agent/stage-10-method-model-contracts-p4-synthetic-integration-docs-validation`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p4-synthetic-integration-docs-validation`
PR: [#70](https://github.com/samcantrill/rphys/pull/70)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: prove all Stage 10 contracts compose coherently using tiny synthetic/test-only objects and record full validation evidence before implementation closure.
- Files/modules owned: `tests/integration/test_synthetic_method_prediction_flow.py`, test-only support fakes/fixtures under `tests/support/` if needed, any missing contract/unit tests for previously implemented names, public docstrings, and `docs/GLOSSARY.md` only if implementation introduced public vocabulary not already covered.
- Behavior implemented: synthetic batch -> input adapter -> model or direct method -> output adapter -> patch-like `MethodOutput` -> explicit apply flow -> optional LIST uncollate of sample-aligned predictions; model isolation; context propagation; state/trainable fake integration; final documentation and validation evidence.
- Decisions applied: DD-0 through DD-10 as a coherence check, with special enforcement of DD-0 LIST round trip, DQ-2 patch output, DQ-6 richer records, no Stage 10 torch helper, model-below-`Batch`, and no trainer/export/loss/device/checkpoint behavior.
- Future-roadmap/reuse constraints: Stage 11-13 and Stage 12 bridge assumptions are validated without implementing losses, metrics, learners, trainers, prediction runners, export writers, or real backend adapters; remaining Stage 9 loader/cache/prepared work is not required.
- Examples or demos covered: synthetic echo method, synthetic model independent of `Batch`, backend-neutral trainable fake, context-aware prediction, and explicit prediction merge.
- Out of scope: real datasets, raw fixtures, CHROM/POS/neural baselines, model zoo, torch/GPU checks, prediction export runners, learner/trainer loops, workflow runtime, and edits to `docs/roadmap.md`.
- Dependencies: Phases 0, 1, 2, and 3 merged.

### Tasks

- Add or consolidate synthetic test-only fakes that exercise the accepted examples without becoming public algorithms.
- Add integration coverage for the full field-centric prediction flow, explicit patch application, and LIST uncollation where predictions are sample-aligned.
- Audit public docstrings/docs for method/model/state/context/output scientific/workflow boundaries.
- Run focused suites first, then broaden to package, unit, contract, integration, full test, summary, lock, and diff checks.
- Record residual risks and any additive docs/error refinements needed for implementation-plan/PR handoff.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/integration/test_synthetic_method_prediction_flow.py` | Validate the synthetic end-to-end Stage 10 prediction flow and LIST-aligned prediction uncollation where exercised. | yes |
| `make test-package` | Recheck package exports/import boundaries after all phases. | yes |
| `make test-unit` | Validate all unit coverage for records/adapters/state/model helpers. | yes |
| `make test-contract` | Validate method/model/trainable public contract behavior. | yes |
| `make test-integration` | Validate integration boundaries without real data or Stage 9 loaders. | yes |
| `make test` | Run broad repository tests because Stage 10 opens public contracts. | yes |
| `make test-summary` | Produce standard test summary evidence. | yes |
| `uv lock --check` | Prove no dependency lock drift, especially no torch dependency. | yes |
| `git diff --check` | Catch whitespace and formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: all recorded examples execute with synthetic/test-only objects and no hidden mutation/export/training behavior.
- Design-decision evidence: patch-only output, explicit apply, model-below-`Batch`, richer state/parameter records, no Stage 10 torch helper, and scoped exports all remain true after composition.
- Future-roadmap/reuse evidence: Stage 11-13 can select/convert prediction fields later; Stage 12 can inspect state/parameters later; backend helpers remain additive future work.
- Example/demo evidence: integration test names or docs map directly to the five examples in `planning.md`.
- Documentation evidence: docstrings and any glossary updates explain public vocabulary, shapes, provenance, patch-vs-`Batch`, no torch helper, and descriptive state/parameter semantics.
- Scientific contract evidence: provenance, field locators, roles, metadata, failure behavior, and side-effect boundaries are inspectable.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-10/phases/synthetic-integration-docs-validation.md`
- Planning/refinement budget: one planning pass with checklist against all accepted decisions and examples.
- Implementation/refinement budget: one implementation pass plus one validation-refinement pass for any failing broad suite.
- PR review budget: one review pass focused on cross-phase coherence, validation evidence, docs, and residual risk.
- Blocker-resolution budget: stop and reopen relevant design queue if required tests cannot express accepted behavior.
- Pre-submit blocker gate: passed; all required validation rows passed.
- Merge record: completed below

### Risks And Stop Conditions

- Risks: full validation may expose a need for small additive error classes or docs; synthetic tests could accidentally become a public fake algorithm catalog; broad suite runtime may reveal unrelated failures.
- Stop conditions: need for Stage 9 loader/cache/prepared code, concrete algorithm implementation, heavy optional dependency import, learner/trainer/export behavior, or any violation of DQ-2/DQ-6 locked semantics.
- Assumptions: no acceptance tests or real backend/data checks are needed unless a later approved optional backend feature is added.

### Completion Summary

- Implementation: extended the synthetic method integration so adapter extraction, backend-native callable model execution, `MethodOutput`, explicit apply, `PredictionContext`, `StateView`, `StateLoadResult`, and `ParameterView` compose in one test-local flow; clarified public docs/glossary for arbitrary backend compatibility; repaired model import-boundary test isolation so module-cache edits do not leak across the full suite.
- Validation: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/methods/test_state.py`; `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/contracts/test_trainable_method_contract.py tests/contracts/test_model_contract.py`; `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/integration/test_synthetic_method_prediction_flow.py`; `make test-package`; `make test-unit`; `make test-contract`; `make test-integration`; `make test`; `UV_CACHE_DIR=/tmp/uv-cache uv lock --check`; `make test-summary`; `git diff --check`; `make validate-pr`.
- PR: [#70](https://github.com/samcantrill/rphys/pull/70)
- Merge: merged to `develop` on 2026-05-16 as `c591808fef3cdc9d6ceb46c65f2b6ca3f97673a9`.
- Follow-up: concrete backend/framework helpers remain deferred as additive adapters; Stage 12+ owns optimizer/checkpoint/device/distributed behavior.

### Merge Record

- Phase: Phase 4 `synthetic-integration-docs-validation`
- Branch: `agent/stage-10-method-model-contracts-p4-synthetic-integration-docs-validation`
- PR: [#70](https://github.com/samcantrill/rphys/pull/70)
- Base branch: `develop`
- Merge command: `gh pr merge 70 --squash --delete-branch`
- Merge result: merged; GitHub reported no status checks for the branch, so merge relied on the completed local validation gate.
- Merge commit: `c591808fef3cdc9d6ceb46c65f2b6ca3f97673a9`
- Branch cleanup: remote branch deletion requested by merge command; local branch cleanup pending worktree removal.
- Worktree cleanup: pending after metadata commit.
- Behavior implemented: Stage 10 contracts compose through synthetic `Batch` input, adapters, backend-native callable model, patch output, explicit application, prediction context, state load result, and parameter view.
- Tests and validation: targeted unit/contract/integration checks passed; package/unit/contract/integration suites passed; `make test` reported 850 passed; `make validate-pr` passed; `make test-summary` reported package 47 passed, unit 655 passed, contract 128 passed, integration 20 passed, and no e2e/acceptance suites present.
- Documentation: phase plan and PR body artifacts added under `docs/roadmap/stage-10/phases/`; glossary and public docstrings now describe arbitrary backend-native state and parameter handles.
- Scientific contract implications: prediction, state, and parameter contracts remain inspectable without hidden mutation, export, training, optimizer, checkpoint, device, distributed, loss, or metric behavior.
- Follow-up notes for later phases: Stage 11-13 can consume explicit prediction fields; Stage 12 can compose backend-specific adapters around these structural records without adding framework behavior to Stage 10.

## Cross-Phase Validation

- Full relevant test command: focused `uv run pytest ...` for touched phase surfaces first, then `make test-package`, `make test-unit`, `make test-contract`, `make test-integration`, `make test`, `make test-summary`, `uv lock --check`, and `git diff --check` before final Stage 10 merge.
- Docs/template checks: public docstrings must record LIST uncollation tuple return and fail-loud behavior, shape, provenance, immutability/copy behavior, patch-vs-`Batch`, selector parsing time, no torch helper, model-below-`Batch`, and state/parameter descriptive semantics; update `docs/GLOSSARY.md` only if implementation adds public vocabulary that needs glossary coverage.
- Scientific/workflow contract checks: no method-owned split selection, leakage policy, loss/objective/metric update, export/materialization, trainer loop, optimizer, scheduler, checkpoint, device movement, distributed state, datasource scan, dataloader construction, or file write.
- Example/demo checks: LIST collate/uncollate round trip, synthetic echo method, model isolation, context-aware prediction, non-torch trainable fake, and explicit prediction merge must map to required tests/docs.
- Manual review focus: public API names and `__all__`; heavy-import boundaries; no placeholder `nn` names; private helper placement; failure diagnostics; uncollation metadata evidence; explicit apply copy/conflict behavior; DD-0/DQ-2/DQ-6 traceability.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| No implementation readiness blocker found. | note | Manager review checked the plan against the passed planning gates, DQ-2/DQ-6 approvals, accepted phase shaping, and validation obligations. | resolved |
| Phase boundaries are coherent and reviewable. | note | Phase 0 isolates data-layer LIST round-trip repair before four Stage 10 phases separate core contracts/imports, adapters/output application, state/trainable records, and integration/docs/final validation. | resolved |
| Stage 9 plans do not need revision for the collation/uncollation update. | note | Stage 10 Phase 0 owns any required refactor of landed shared `rphys.data` collation/collater code and validates the landed Stage 9 torch-collater path. Stage 10 must not edit Stage 9 planning artifacts or require Stage 9 source-derived identifier propagation. | resolved |
| Stage 10 contexts should remain generic. | concern | `PredictionContext` should carry generic primitive metadata/provenance only. Domain-specific identifiers such as sample IDs belong in caller-owned metadata defined by downstream code, not first-class Stage 10 fields or Phase 0 batch-context changes. | resolved |
| Implementation must not begin without final approval. | concern | Maintainer approval was recorded from the 2026-05-16 implementation request. | resolved |

Gate result:

- Status: passed after design review, quality-gate refresh, generic metadata phase pass, and maintainer implementation approval on 2026-05-16
- Review evidence: manager review completed 2026-05-15 against `docs/roadmap/stage-10/planning.md`, accepted phase shaping, validation strategy, plan-quality gate, unresolved-packet checks, and a refreshed review of landed Stage 9 collation/collater boundaries.
- Accepted risks: Phase 0 adds public data-layer surface and must avoid leaking private collation evidence into user metadata; patch-like `MethodOutput` may require Stage 12/13 adapter code; richer state/parameter records add public surface and validation cost; lifecycle-style model hooks would recreate framework/trainer responsibilities if allowed, so Stage 10 must stay at callable computation plus descriptive state/parameter views; private helper duplication is accepted until repeated selector/spec semantics appear outside methods; Stage 9 Phases 1-4 are landed but Stage 10 integration stays independent from remaining Stage 9 loader/cache/prepared work beyond validating the existing collater path.
- Revisit triggers: LIST uncollation cannot preserve explicit `None` versus missing metadata; hard torch dependency or Stage 10 torch helper; `Method.predict` returns `Batch` or mutates by default; methods own loss/metric/export/training/split/device/checkpoint behavior; models import `Batch`/datasources/loaders or grow torch/Lightning-style lifecycle hooks; state records encode optimizer/checkpoint/device/distributed policy; public helper registries or root exports are added; required tests cannot express accepted behavior.

## Final Approval

- Approval status: approved 2026-05-16 by maintainer implementation request.
- Approved scope: Stage 10 Phases 0-4 as written in this implementation plan, with the recorded phase order, validation obligations, stop conditions, and deferred items.
- Accepted risks: Phase 0 adds public data-layer surface and must avoid leaking private collation evidence into user metadata; patch-like `MethodOutput` may require Stage 12/13 adapter code; richer state/parameter records add public surface and validation cost; lifecycle-style model hooks would recreate framework/trainer responsibilities if allowed, so Stage 10 must stay at callable computation plus descriptive state/parameter views; private helper duplication is accepted until repeated selector/spec semantics appear outside methods; Stage 9 Phases 1-4 are landed but Stage 10 integration stays independent from remaining Stage 9 loader/cache/prepared work beyond validating the existing collater path.
- Deferred items: concrete algorithms, neural baselines/model zoo, losses/objectives/metrics, learners/trainers, optimizers/schedulers/checkpoints, device/distributed behavior, dataloaders, prediction export/evaluation/reporting, workflow runtime, optional torch helpers, and backend/framework adapters.
