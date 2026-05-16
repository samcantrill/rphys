# Roadmap Stage 12 Implementation Plan

Status: approved
Roadmap version: `v12`
Planning document: `docs/roadmap/stage-12/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: complete
Blockers: none

## Summary

- Goal: implement Stage 12 learning/training contracts after this plan is approved, keeping scientific step semantics in learners and loop control in the selected training engine.
- Source functionality-agreement gate: passed on 2026-05-16; FQ-12-1 through FQ-12-8 are locked, and FQ-12-9 is deferred/documented.
- Approved behavior: `Learner` owns mode-specific step semantics; `Trainer` is the RemotePhys facade; `TrainingEngine` owns `fit/validate/test/predict(plan, learner)` loop control; `NativeTrainingEngine` is the reference loop.
- Source behavior confirmation: passed on 2026-05-16 after post-prediction batch pipeline deferral.
- Key design constraints: `TrainingPlan` remains assembled-object oriented; `TrainingResult` remains primitive summary oriented; real Lightning/JAX/torch/logger adapters stay out of Stage 12 core; fake external-engine pressure tests prove delegation.
- Source design-agreement gate: passed on 2026-05-16; DQ-12-1 through DQ-12-6 are locked and DQ-12-7 is deferred/documented.
- Source functionality-agreement queue: FQ-12-1 through FQ-12-8 locked; FQ-12-9 documentation-only future compatibility.
- Source design-agreement queue: DQ-12-1 through DQ-12-6 locked; DQ-12-7 documentation-only future compatibility.
- Source future-roadmap/reuse safety review: passed with revisit triggers for Stage 13 prediction/evaluation, Stage 15 profiling, optional Lightning, future JAX, downstream workflow persistence, and future post-model batch pipelines.
- Examples covered: native supervised smoke run, fake external-engine delegation, Lightning-like documentation sketch, duplicate trainable-owner guardrail, neutral `TrainingPlan`, primitive `TrainingResult`, prediction pass-through, future post-prediction batch-pipeline note, and JAX pressure note.
- Source phase shaping: passed with six reviewable phases.
- Source plan quality gate: passed; no required specialist evidence is missing or stale.
- Out of scope: real Lightning implementation; learner-level post-prediction `BatchOperationPipeline` execution; mode-specific prediction pipeline specs; `TrainingPlan` pipeline fields; trainer-owned prediction routing; sample uncollation adapters; datasource scanning; dataloader construction; project config; artifact/checkpoint writers; prediction export/materialization; evaluation/report generation; logger/framework dependencies in core.

## Implementation Workflow State

- Implementation-plan quality gate: passed after manager design review
- Review pass: completed 2026-05-16
- Refinement pass: completed 2026-05-16
- Confirmation review: completed 2026-05-16
- Automatic merge mode: enabled
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `learning-contract` | merged | `agent/stage-12-learning-training-p1-learning-contract` | [#79](https://github.com/samcantrill/rphys/pull/79) | `src/rphys/learning`, package import tests, learning unit/contract tests | Establish learning modes, context, step output, scalar boundary, and structural learner contract. | `make test-package`, `make test-unit`, `make test-contract`, `git diff --check` | Prediction pass-through contract foundation |
| 2 | `supervised-learner` | merged | `agent/stage-12-learning-training-p2-supervised-learner` | [#80](https://github.com/samcantrill/rphys/pull/80) | `src/rphys/learning/supervised.py`, learning contract/integration tests, test support fakes | Compose Stage 10 methods with Stage 11 objective/metric contracts. | `make test-unit`, `make test-contract`, `make test-integration`, `git diff --check` | Native supervised smoke learner slice; prediction-only mode |
| 3 | `plan-result-facade` | merged | `agent/stage-12-learning-training-p3-plan-result-facade` | [#81](https://github.com/samcantrill/rphys/pull/81) | `src/rphys/training/plan.py`, `results.py`, `core.py`, `experimental.py`, training unit/contract tests | Add neutral plan/result records and facade-to-engine delegation. | `make test-unit`, `make test-contract`, `make test-package`, `git diff --check` | Fake engine delegation; plan neutrality; result summaries |
| 4 | `native-engine` | merged | `agent/stage-12-learning-training-p4-native-engine` | [#82](https://github.com/samcantrill/rphys/pull/82) | `src/rphys/training/backend.py`, native engine internals, native unit/integration tests | Implement dependency-light reference loop and backend mechanics. | `make test-unit`, `make test-integration`, `make test-contract`, `git diff --check` | Native supervised fit/validate/test/predict smoke run |
| 5 | `observability-external-pressure` | merged | `agent/stage-12-learning-training-p5-observability-external-pressure` | [#83](https://github.com/samcantrill/rphys/pull/83) | `src/rphys/training/events.py`, `profiling.py`, fake external test support, observability contracts | Add events/profiles and fake external-engine pressure tests. | `make test-unit`, `make test-contract`, `make test-package`, `git diff --check` | Fake external engine; duplicate trainable-owner guardrail; JAX pressure note |
| 6 | `docs-examples-final-validation` | merged | `agent/stage-12-learning-training-p6-docs-examples-final-validation` | [#84](https://github.com/samcantrill/rphys/pull/84) | Stage 12 docs/docstrings/examples, final validation evidence, package exports | Finish docs/examples, optional `run_train` polish, future-compatibility notes, and full validation. | `make test-package`, `make test-unit`, `make test-contract`, `make test-integration`, `make test-summary`, `uv lock --check`, `git diff --check`, `make validate-pr` | End-to-end native example; fake external example; future batch-pipeline documentation only |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None. Readiness passed: functionality agreement and behavior confirmation passed; design agreement passed; validation and phase-shaping gate passed; plan quality gate passed; required specialist evidence is present; no unresolved or reopened agreement packet remains. | `docs/roadmap/stage-12/planning.md` Stage Gates, Specialist Evidence Status, Design Gate Status, Plan Quality Gate, and this plan's Implementation Plan Review section | No action before maintainer approval. | resolved |

## Phase 1: Learning Contract Foundation

Status: merged
Slug: `learning-contract`
Branch: `agent/stage-12-learning-training-p1-learning-contract`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-12-learning-training-p1-learning-contract`
PR: [#79](https://github.com/samcantrill/rphys/pull/79)
Base branch: `develop`
Target branch: `develop`
Workflow path: `.codex/workflows/roadmap-version-implementation.md`

### Scope

- Goal: add code-backed learning primitives that define the learner-to-engine boundary without importing training or backend frameworks.
- Files/modules owned: `src/rphys/learning/__init__.py`, `src/rphys/learning/modes.py`, `src/rphys/learning/context.py`, `src/rphys/learning/output.py`, `src/rphys/learning/core.py`, private learning validation helpers if needed, `tests/unit/rphys/learning/*`, `tests/contracts/test_stage12_learner_contract.py`, `tests/contracts/test_stage12_step_output_contract.py`, package import tests.
- Behavior implemented: `LoopMode`, `LoopContext`, `StepOutput`, minimal `BackwardableScalar` boundary or helper, structural `Learner.step(batch, context) -> StepOutput`, primitive metadata/provenance validation, mode/split distinction, prediction opacity.
- Decisions applied: DD-12-8, DD-12-9, DD-12-10, DD-12-11, DD-12-12; DQ-12-5 scalar/prediction boundary; framework-free import guardrail from DQ-12-6.
- Future-roadmap/reuse constraints: keep `rphys.learning` independent from `rphys.training`; keep prediction union provisional and field-aware for Stage 13; do not assume torch/JAX scalar behavior beyond native `.backward()` fallback.
- Examples or demos covered: prediction pass-through and learning contract snippets in tests/docstrings only.
- Out of scope: `SupervisedLearner`, `TrainingPlan`, trainer/engine behavior, native backward execution, events/profiles, pipeline execution.
- Dependencies: Stage 10 `MethodOutput`, `Sample`, `Batch`; Stage 11 public result/value types only where needed for type acceptance.

### Tasks

- Define mode/context records with clear validation for invalid modes, invalid indexes, primitive metadata/provenance, and split-name distinction.
- Define `StepOutput` with accepted predictions `MethodOutput | Sample | Batch | None`, objective, terms, metrics, diagnostics, metadata, and provenance.
- Define minimal backward-compatible scalar surface for native execution without requiring torch or any backend import.
- Define structural `Learner` protocol and package exports for implemented names only.
- Add package/import-boundary tests proving learning imports do not load training, Lightning, torch, JAX, logger, video, plotting, dataset-SDK, or heavy array stacks.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Prove package exports and import boundaries for learning modules. | yes |
| `make test-unit` | Prove mode/context/output validation and scalar helper behavior. | yes |
| `make test-contract` | Prove structural learner and `StepOutput` public contracts. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: tests cover valid and invalid modes, contexts, primitive metadata/provenance, accepted prediction union, immutable or primitive summary mappings, objective presence/absence, and unsupported scalar failures.
- Design-decision evidence: tests prove predictions are opaque and include `MethodOutput`; no training import appears in learning.
- Future-roadmap/reuse evidence: docs/tests identify Stage 13 prediction revisit trigger and avoid trainer-side materialization assumptions.
- Example/demo evidence: simple learner fake returns a `StepOutput` with `MethodOutput` unchanged.
- Documentation evidence: public docstrings state shapes, mode/split meaning, prediction opacity, and scalar limitations.
- Scientific contract evidence: context records preserve mode, split, indexes, metadata, and provenance without hiding datasource, label, or workflow state.

### Phase Workflow State

- Phase execution plan: completed inline by manager on 2026-05-16
- Planning/refinement budget: one planning pass plus one refinement pass if review finds API ambiguity.
- Implementation/refinement budget: narrow implementation plus targeted test fixes.
- PR review budget: one reviewer pass focused on public contract and import boundaries.
- Blocker-resolution budget: stop and escalate if Stage 10/11 public contracts do not support the accepted prediction/scalar shape.
- Pre-submit blocker gate: no unresolved learning/training dependency direction violation; no forbidden imports.
- Merge record: PR [#79](https://github.com/samcantrill/rphys/pull/79) merged to `develop` on 2026-05-16 as `9134121` (`feat: add stage 12 learning contract foundation`).

### Risks And Stop Conditions

- Risks: over-widened context schema, implicit split/mode coupling, scalar contract that effectively requires torch, accidental training import from learning.
- Stop conditions: implementation requires a public backend registry, hard framework dependency, root-level exports, or any change to the approved prediction union.
- Assumptions: Stage 10/11 code-backed contracts remain compatible with planning evidence.

### Completion Summary

- Implementation: completed `LoopMode`, `LoopContext`, `StepOutput`, `BackwardableScalar`, structural `Learner`, learning package exports, and package/unit/contract coverage.
- Validation: passed `make test-package`, `make test-unit`, `make test-contract`, and `git diff --check` in `/home/samcantrill/work/rphys-worktrees/stage-12-learning-training-p1-learning-contract`.
- PR: [#79](https://github.com/samcantrill/rphys/pull/79)
- Merge: merged to `develop` on 2026-05-16 as `9134121`.
- Follow-up: Phase 2 should compose the `SupervisedLearner` with Stage 10/11 contracts without adding trainer imports, pipeline hooks, or backend dependencies.

## Phase 2: Supervised Learner Composition

Status: merged
Slug: `supervised-learner`
Branch: `agent/stage-12-learning-training-p2-supervised-learner`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-12-learning-training-p2-supervised-learner`
PR: [#80](https://github.com/samcantrill/rphys/pull/80)
Base branch: `develop`
Target branch: `develop`
Workflow path: `.codex/workflows/roadmap-version-implementation.md`

### Scope

- Goal: implement the only Stage 12 concrete learner, composing Stage 10 method output with Stage 11 objective and metric contracts.
- Files/modules owned: `src/rphys/learning/supervised.py`, learning package exports, `tests/contracts/test_stage12_supervised_learner_contract.py`, `tests/integration/test_stage12_synthetic_training_flow.py` learner portions, `tests/support` synthetic method/objective/metric fakes as needed.
- Behavior implemented: `SupervisedLearner` calls `Method.predict`, returns `MethodOutput` by default, applies prediction patches only to a local working batch when objective/metrics need predicted fields, evaluates optional objective/metrics, detaches or summarizes metrics according to Stage 11 contracts, supports prediction-only mode, and fails clearly for train mode when objective/backward is required but unavailable.
- Decisions applied: DD-12-9, DD-12-10, DD-12-13, Stage 11 sequencing guardrail, DQ-12-5.
- Future-roadmap/reuse constraints: no learner-level post-prediction pipeline hook; no `PredictionPipelineSpec`; no `train_pipeline`/`eval_pipeline`/`inference_pipeline`; no automatic sample uncollation/collation; preserve future field-aware batch-pipeline compatibility by keeping trainer-opaque predictions.
- Examples or demos covered: supervised synthetic learner flow; prediction-only flow; missing train objective failure.
- Out of scope: optimizer/backward execution, trainer loops, external engines, events/profiles, concrete non-supervised learner families, objective/metric stand-ins published from learning/training.
- Dependencies: Phase 1; Stage 10 method contracts; Stage 11 objective/metric contracts.

### Tasks

- Implement `SupervisedLearner` with assembled method, optional objective, and optional metrics.
- Use local working composition for objective/metric calculation without mutating input batches unless the chosen copy/update behavior is explicit and tested.
- Preserve raw `MethodOutput` in `StepOutput.predictions` by default.
- Normalize objective, objective terms, loss terms, metric values, diagnostics, metadata, and provenance into `StepOutput`.
- Add synthetic tests using public Stage 10/11 contracts and test-local fakes only where backend-free mechanics need them.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Prove learner validation, local composition helpers, and failure behavior. | yes |
| `make test-contract` | Prove public supervised learner contract and prediction pass-through. | yes |
| `make test-integration` | Prove synthetic Stage 10/11 composition. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: train/validate/test/predict learner steps behave as accepted; prediction mode works without objective or targets; train mode fails when objective/backward is unavailable.
- Design-decision evidence: tests prove no learner-owned optimizer, scheduler, checkpoint, export, dataloader, or framework lifecycle behavior.
- Future-roadmap/reuse evidence: review confirms no Stage 12 post-prediction pipeline API or behavior exists.
- Example/demo evidence: synthetic method/objective/metric flow demonstrates the native supervised learner slice.
- Documentation evidence: docstrings state local working-batch behavior, default `MethodOutput` prediction, and objective/metric integration boundaries.
- Scientific contract evidence: objective and metrics consume explicitly composed predicted fields with provenance/metadata preserved where records support it; metric values are detached/summarized through Stage 11 contracts.

### Phase Workflow State

- Phase execution plan: completed inline by manager on 2026-05-16
- Planning/refinement budget: one focused design pass for Stage 10/11 call signatures before editing.
- Implementation/refinement budget: one implementation pass plus targeted contract/integration fixes.
- PR review budget: one reviewer pass focused on scientific step semantics and no hidden mutation/export.
- Blocker-resolution budget: stop if Stage 11 public objective/metric contracts cannot be composed without inventing public stand-ins.
- Pre-submit blocker gate: no pipeline hook, no trainer import, no optimizer/checkpoint/export behavior.
- Merge record: PR [#80](https://github.com/samcantrill/rphys/pull/80) merged to `develop` on 2026-05-16 as `745f78a` (`feat: add stage 12 supervised learner`).

### Risks And Stop Conditions

- Risks: accidental prediction materialization/export, unclear input mutation semantics, publishing fake objective/metric types, leaking pipeline execution into learner construction.
- Stop conditions: implementation requires a public prediction pipeline field, Stage 11 stand-in class, or trainer-owned prediction application.
- Assumptions: Stage 10 `apply_method_output` or equivalent public behavior is sufficient for local objective/metric composition.

### Completion Summary

- Implementation: completed `SupervisedLearner` composition over Stage 10 `MethodOutput` and Stage 11 loss/objective/metric contracts with local working-batch prediction application and prediction pass-through.
- Validation: passed `make test-unit`, `make test-contract`, `make test-integration`, `git diff --check`, and extra `make test-package` in `/home/samcantrill/work/rphys-worktrees/stage-12-learning-training-p2-supervised-learner`.
- PR: [#80](https://github.com/samcantrill/rphys/pull/80)
- Merge: merged to `develop` on 2026-05-16 as `745f78a`.
- Follow-up: Phase 3 should establish neutral plan/result/facade records without placeholder default engine behavior or registries.

## Phase 3: Plan, Result, Facade, And Delegated Engine Boundary

Status: merged
Slug: `plan-result-facade`
Branch: `agent/stage-12-learning-training-p3-plan-result-facade`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-12-learning-training-p3-plan-result-facade`
PR: [#81](https://github.com/samcantrill/rphys/pull/81)
Base branch: `develop`
Target branch: `develop`
Workflow path: `.codex/workflows/roadmap-version-implementation.md`

### Scope

- Goal: establish the neutral training records and selected-engine delegation contract before adding native loop mechanics.
- Files/modules owned: `src/rphys/training/__init__.py`, `src/rphys/training/plan.py`, `src/rphys/training/results.py`, `src/rphys/training/core.py`, `src/rphys/training/experimental.py` if included here, `tests/unit/rphys/training/test_plan*.py`, `tests/unit/rphys/training/test_results*.py`, `tests/contracts/test_stage12_trainer_engine_contract.py`, `tests/contracts/test_stage12_training_result_contract.py`.
- Behavior implemented: assembled-object `TrainingPlan`, primitive summary-oriented `TrainingResult` and supporting summary records, provisional `TrainingEngine` protocol with `fit/validate/test/predict(plan, learner)`, `Trainer` facade dispatch with explicit selected-engine support and separate `plan` and `learner`, optional experimental `run_train` if stable enough for this phase. The public default to `NativeTrainingEngine` is completed in Phase 4 after the native engine exists; Phase 3 must not add a placeholder default engine.
- Decisions applied: DD-12-1, DD-12-2, DD-12-5, DD-12-6, DD-12-15; DQ-12-1, DQ-12-2, DQ-12-3.
- Future-roadmap/reuse constraints: no engine registry; no `engine_config`; no learner embedded in `TrainingPlan`; engine-specific config belongs on engine/adapter objects; no raw framework-private objects in results.
- Examples or demos covered: fake engine receives `plan` and `learner` separately; plan neutrality; result primitive summaries.
- Out of scope: full native loop mechanics, events/profiles beyond minimal result placeholders if needed, fake external trainable-owner pressure, real Lightning/JAX implementation, workflow config/runtime.
- Dependencies: Phase 1; Phase 2 for learner fixtures where tests need realistic calls.

### Tasks

- Define `TrainingPlan` with caller-built batch sources/loaders, primitive loop limits, RemotePhys observer/profiler slots if already shaped, optional native backend descriptor slots, metadata, and provenance.
- Define `TrainingResult` status/mode/count/failure/metric/last-step/event/profile summary records with primitive validation and minimal optional monitored metric/checkpoint identifiers.
- Define provisional `TrainingEngine` protocol and `Trainer` facade dispatch methods.
- Add fake engine tests proving selected-engine delegation and no accidental native execution.
- Add `run_train` only as a thin experimental helper if it can be fully tested without workflow/config/artifact ownership; otherwise leave it for Phase 6.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Prove plan/result field validation and primitive summaries. | yes |
| `make test-contract` | Prove facade-to-engine dispatch and result contract. | yes |
| `make test-package` | Prove training exports and import boundaries. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: `Trainer.fit/validate/test/predict` delegate to an explicitly selected engine with separate `plan` and `learner`; fake engine call records prove no native loop execution or placeholder default engine behavior.
- Design-decision evidence: tests prove no `engine_config`, project config, dataset path, artifact dir, framework trainer/logger/callback field, engine registry, or learner-in-plan behavior.
- Future-roadmap/reuse evidence: docs/tests mark `TrainingEngine` provisional and keep extension additive.
- Example/demo evidence: fake engine and primitive result examples cover native/delegated boundary.
- Documentation evidence: docstrings describe `Trainer` as facade and selected engine as loop owner.
- Scientific contract evidence: plan/result metadata and provenance remain primitive/inspectable; failures and partial/stopped runs are represented without hiding loop outcome.

### Phase Workflow State

- Phase execution plan: completed inline by manager on 2026-05-16
- Planning/refinement budget: one pass to settle exact record fields within locked DQ boundaries.
- Implementation/refinement budget: one implementation pass plus contract refinements.
- PR review budget: one reviewer pass focused on schema creep and facade wording.
- Blocker-resolution budget: stop if result/plan shape needs a generic config escape hatch or raw framework object.
- Pre-submit blocker gate: no `engine_config`, no registry, no workflow runtime, no framework imports.
- Merge record: PR [#81](https://github.com/samcantrill/rphys/pull/81) merged to `develop` on 2026-05-16 as `b73a56d` (`feat: add stage 12 training facade contracts`).

### Risks And Stop Conditions

- Risks: plan/result schema creep, facade wording implying `Trainer` owns loop control, premature registry, placeholder default engine behavior, `run_train` becoming workflow API.
- Stop conditions: implementation needs dataset scanning, dataloader construction, artifact paths, framework callback/logger objects, generic engine config, or a fake native default before `NativeTrainingEngine` exists.
- Assumptions: Phase 4 can add `NativeTrainingEngine` mechanics and make it the public default behind the same protocol without changing Phase 3 public signatures.

### Completion Summary

- Implementation: completed neutral `TrainingPlan`, primitive `TrainingResult` and summary records, provisional `TrainingEngine`, explicit-engine `Trainer` facade, and empty experimental module reservation.
- Validation: passed `make test-unit`, `make test-contract`, `make test-package`, and `git diff --check` in `/home/samcantrill/work/rphys-worktrees/stage-12-learning-training-p3-plan-result-facade`.
- PR: [#81](https://github.com/samcantrill/rphys/pull/81)
- Merge: merged to `develop` on 2026-05-16 as `b73a56d`.
- Follow-up: Phase 4 should add `NativeTrainingEngine`, make it the `Trainer` default, and preserve explicit-engine delegation behavior.

## Phase 4: Native Engine Mechanics

Status: merged
Slug: `native-engine`
Branch: `agent/stage-12-learning-training-p4-native-engine`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-12-learning-training-p4-native-engine`
PR: [#82](https://github.com/samcantrill/rphys/pull/82)
Base branch: `develop`
Target branch: `develop`
Workflow path: `.codex/workflows/roadmap-version-implementation.md`

### Scope

- Goal: implement `NativeTrainingEngine` as a dependency-light reference loop over already-built batch iterables.
- Files/modules owned: `src/rphys/training/backend.py`, native portions of `src/rphys/training/core.py`, native result accumulation helpers, `tests/unit/rphys/training/test_backend*.py`, `tests/unit/rphys/training/test_native_engine*.py`, `tests/integration/test_stage12_synthetic_training_flow.py`.
- Behavior implemented: native `fit/validate/test/predict`, public `Trainer` default to `NativeTrainingEngine`, context construction, max epoch/step limits, optional device mover, backward override or minimal `.backward()` fallback, optimizer zero/step, scheduler step, train-only mechanics, failure normalization, result accumulation.
- Decisions applied: DD-12-3, DD-12-10, DQ-12-1, DQ-12-5, Stage 15 native-reference guardrail.
- Future-roadmap/reuse constraints: native engine remains reference-grade; no logging/checkpoint/early-stopping/distributed/precision/profiler framework features; no datasource/dataloader construction; no trainer prediction materialization/export.
- Examples or demos covered: native supervised fit/validate/test/predict smoke flow with synthetic batches and fake backend mechanics.
- Out of scope: events/profile richness beyond hooks needed for Phase 5 integration, fake external engines, real Lightning/JAX, artifact stores, checkpoint writers.
- Dependencies: Phases 1-3.

### Tasks

- Implement native mode loops over caller-provided batch iterables/loaders from `TrainingPlan`.
- Make `NativeTrainingEngine` the public default engine for `Trainer` without changing the selected-engine delegation protocol established in Phase 3.
- Build `LoopContext` values with mode, epoch, step, batch indexes, split names, metadata, and provenance.
- Enforce train-only backward/optimizer/scheduler behavior and validate no backward occurs during validate/test/predict.
- Define backend/device/optimizer/scheduler descriptors or callable hooks with explicit call order and clear unsupported behavior.
- Normalize exceptions, stopped/partial/completed states, counts, metric summaries, and last-step evidence into `TrainingResult`.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Prove backend descriptor ordering, train-only mechanics, limits, and failure handling. | yes |
| `make test-integration` | Prove native synthetic fit/validate/test/predict with Phase 2 learner. | yes |
| `make test-contract` | Prove native engine honors `TrainingEngine` and result contracts. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: native loops create expected contexts, call learner steps, enforce max epochs/steps, make `NativeTrainingEngine` the default `Trainer` engine, and return completed/failed/stopped/partial summaries.
- Design-decision evidence: train mode uses only `StepOutput.objective` for backward; validate/test/predict do not step optimizer/scheduler or call backward.
- Future-roadmap/reuse evidence: no Lightning-sized features appear; future engines can delegate control without inheriting native internals.
- Example/demo evidence: synthetic native smoke tests cover fit with validation, validate, test, and predict.
- Documentation evidence: native engine docstrings describe reference-grade scope and assembled batch input requirement.
- Scientific contract evidence: loop metadata, split/mode distinction, objective/backward failure behavior, and metric summary provenance are inspectable.

### Phase Workflow State

- Phase execution plan: completed inline by manager on 2026-05-16
- Planning/refinement budget: one pass for call-order details and failure normalization.
- Implementation/refinement budget: one implementation pass plus integration fixes.
- PR review budget: one reviewer pass focused on loop mechanics and non-goals.
- Blocker-resolution budget: stop if native mechanics require framework-specific assumptions or broader result schema.
- Pre-submit blocker gate: no datasource/dataloader construction, no checkpoint writer, no logger/distributed/precision implementation.
- Merge record: PR [#82](https://github.com/samcantrill/rphys/pull/82) merged to `develop` on 2026-05-16 as `99ef239` (`feat: add stage 12 native training engine`).

### Risks And Stop Conditions

- Risks: ambiguous objective-required policy, loop-limit off-by-one errors, native feature creep, hidden mutation of batch inputs through device movement or prediction application.
- Stop conditions: implementation requires hard torch/JAX imports, a workflow runtime, checkpoint/logging facilities, or trainer-owned prediction processing.
- Assumptions: caller-supplied fake backend descriptors are enough to prove dependency-free mechanics.

### Completion Summary

- Implementation: completed dependency-light `NativeTrainingEngine`, default `Trainer()` engine selection, native fit/validate/test/predict loops, context construction, train-only backward/optimizer/scheduler behavior, step limits, failure normalization, and primitive result accumulation. Also corrected configured `SupervisedLearner` predict mode to skip objective/loss/metric execution.
- Validation: passed `make test-unit`, `make test-integration`, `make test-contract`, `git diff --check`, and extra `make test-package` in `/home/samcantrill/work/rphys-worktrees/stage-12-learning-training-p4-native-engine`.
- PR: [#82](https://github.com/samcantrill/rphys/pull/82)
- Merge: merged to `develop` on 2026-05-16 as `99ef239`.
- Follow-up: Phase 5 should add event/profile records and fake external pressure while preserving native reference scope and framework deferrals.

## Phase 5: Observability And Fake External Pressure

Status: merged
Slug: `observability-external-pressure`
Branch: `agent/stage-12-learning-training-p5-observability-external-pressure`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-12-learning-training-p5-observability-external-pressure`
PR: [#83](https://github.com/samcantrill/rphys/pull/83)
Base branch: `develop`
Target branch: `develop`
Workflow path: `.codex/workflows/roadmap-version-implementation.md`

### Scope

- Goal: add dependency-light observability records and pressure-test delegated engines without adding real framework adapters.
- Files/modules owned: `src/rphys/training/events.py`, `src/rphys/training/profiling.py`, observer/callback integration points in `src/rphys/training/core.py` if needed, `tests/unit/rphys/training/test_events*.py`, `tests/unit/rphys/training/test_profiling*.py`, `tests/contracts/test_stage12_observability_contract.py`, `tests/support/stage12_fake_external.py`, `tests/contracts/test_stage12_external_engine_contract.py`, `tests/integration/test_stage12_fake_external_engine.py`.
- Behavior implemented: `TrainingEvent`, event sinks, observe-only callbacks, profile/span summaries, unavailable probe records, overhead metadata, native/fake external event mapping, fake external engine result normalization, fake trainable-owner registration guardrails.
- Decisions applied: DD-12-4, DD-12-7, DD-12-8, DD-12-14, DQ-12-4, DQ-12-6.
- Future-roadmap/reuse constraints: Stage 15 deep profiling stays deferred; callbacks cannot control loops or learner semantics; real Lightning remains absent; fake external adapter must not imply a supported real framework integration.
- Examples or demos covered: fake Lightning-like engine delegation; duplicate trainable-owner guardrail; external result summary; JAX/functional pressure through fake protocol or docs note.
- Out of scope: real Lightning/JAX/torch/logger imports, checkpoint parsing, logger integrations, early stopping, deep profiler timelines, hidden synchronization.
- Dependencies: Phase 3; Phase 4 for native event/profile emission integration where touched.

### Tasks

- Define event/status/phase vocabulary and observer sink/callback protocols with observe-only semantics.
- Define profile/span summary records with unavailable probe and overhead metadata.
- Wire native engine to emit dependency-light events/profiles where Phase 4 left integration points.
- Build fake external engine/test adapter that maps external-like primitive evidence into optional `TrainingResult` summaries: logged metric names/values, checkpoint identifiers when already available, callback/profile status summaries, unavailable probes, and RemotePhys events. Do not parse checkpoint files, logger internals, callback-private state, or framework-private objects.
- Add fake trainable-owner checks for shared object identity, method-as-module, nested-module, duplicate rejection, unsupported pure-Python cases, and no core framework introspection.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Prove event/profile records, observer-only behavior, and summaries. | yes |
| `make test-contract` | Prove observability and fake external-engine contracts. | yes |
| `make test-package` | Prove no torch/Lightning/JAX/logger import regression. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: native and fake external engines emit comparable records; fake external delegation never enters native loop; missing/partial external evidence normalizes predictably without requiring broad external-engine result fields.
- Design-decision evidence: tests prove one adapter-local trainable owner, duplicate rejection, and no public trainable-module helper/protocol in core.
- Future-roadmap/reuse evidence: Stage 15 profiling and real Lightning adapter revisit triggers are documented; event vocabulary stays dependency-light.
- Example/demo evidence: fake external tests cover automatic-optimization-like step mapping and primitive summary normalization without real framework imports.
- Documentation evidence: docstrings and test names make fake external scope explicit.
- Scientific contract evidence: observability records preserve mode, phase, indexes, status, unavailable probes, and overhead notes without controlling learner semantics.

### Phase Workflow State

- Phase execution plan: completed inline by manager on 2026-05-16
- Planning/refinement budget: one pass for event/profile vocabulary and fake external boundaries.
- Implementation/refinement budget: one implementation pass plus contract fixes.
- PR review budget: one reviewer pass focused on framework deferral and observer scope.
- Blocker-resolution budget: stop if fake pressure exposes missing public engine/plan/result fields that require DQ reopening.
- Pre-submit blocker gate: no real Lightning/JAX/torch/logger dependency; callbacks remain observe-only.
- Merge record: PR [#83](https://github.com/samcantrill/rphys/pull/83) merged to `develop` on 2026-05-16 as `e22516f` (`feat: add stage 12 training observability`).

### Risks And Stop Conditions

- Risks: event vocabulary overreach, callbacks gaining loop control, fake adapter becoming a de facto real adapter, trainable-owner tests depending on framework behavior not represented by fakes.
- Stop conditions: implementation requires real framework imports, public trainable-owner helper/protocol, raw framework-private result fields, or callback loop-control semantics.
- Assumptions: fake external tests are sufficient Stage 12 pressure because real Lightning is explicitly deferred.

### Completion Summary

- Implementation: completed `TrainingEvent`, observe-only sinks/callbacks, profile span/unavailable probe records, native event/profile emission, fake external result normalization tests, and adapter-local fake trainable-owner guardrails.
- Validation: passed `make test-unit`, `make test-contract`, `make test-package`, `git diff --check`, and extra `make test-integration` in `/home/samcantrill/work/rphys-worktrees/stage-12-learning-training-p5-observability-external-pressure`.
- PR: [#83](https://github.com/samcantrill/rphys/pull/83)
- Merge: merged to `develop` on 2026-05-16 as `e22516f`.
- Follow-up: Phase 6 should finish docs/examples, final export checks, `run_train` polish if appropriate, future-compatibility notes, and full validation.

## Phase 6: Docs, Examples, Experimental Entrypoint, And Final Validation

Status: merged
Slug: `docs-examples-final-validation`
Branch: `agent/stage-12-learning-training-p6-docs-examples-final-validation`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-12-learning-training-p6-docs-examples-final-validation`
PR: [#84](https://github.com/samcantrill/rphys/pull/84)
Base branch: `develop`
Target branch: `develop`
Workflow path: `.codex/workflows/roadmap-version-implementation.md`

### Scope

- Goal: make the accepted public contract usable, document deferrals precisely, add `run_train` if not already completed, and record final validation evidence.
- Files/modules owned: public learning/training docstrings, package exports, docs/examples selected by repo convention, `src/rphys/training/experimental.py` if deferred from Phase 3, Stage 12 final validation notes in this implementation plan after implementation begins, documentation-oriented tests if present.
- Behavior implemented: final public docs/examples for native and fake external usage; `run_train` thin delegation if not already implemented; explicit future-compatibility note for post-model batch pipelines; final import/export cleanup.
- Decisions applied: all locked DQ/DD packets, especially DQ-12-6 Lightning deferral and DQ-12-7 post-prediction pipeline deferral.
- Future-roadmap/reuse constraints: documentation must not promise current real Lightning support, current JAX support, current post-prediction pipeline execution, prediction export/materialization, checkpoint/artifact storage, workflow config parsing, or Stage 15 profiling depth.
- Examples or demos covered: end-to-end native supervised example, fake external-engine example, Lightning-like sketch labeled future/optional, future post-prediction batch-pipeline documentation-only note.
- Out of scope: new behavior beyond docs/final polish; docs-only PRs between phase PRs; implementation of deferred pipeline or real external engines.
- Dependencies: Phases 1-5.

### Tasks

- Add or refresh docs/docstrings/examples so `Trainer` is consistently described as facade and `TrainingEngine` as loop owner.
- Add or finalize `run_train` as an experimental thin helper if not completed in Phase 3.
- Document that future RemotePhys should be able to run `BatchOperationPipeline` over model outputs, while Stage 12 has no learner pipeline argument, mode-specific pipeline spec, trainer routing, plan pipeline field, or sample uncollation adapter.
- Verify package exports expose only implemented names and no root-level placeholder exports are added.
- Run final relevant validation sweep and record results in the implementation workflow artifacts.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Final package/export/import-boundary validation. | yes |
| `make test-unit` | Final unit regression validation. | yes |
| `make test-contract` | Final public contract validation. | yes |
| `make test-integration` | Final synthetic native/fake external integration validation. | yes |
| `make test-summary` | Generate test summary evidence. | yes |
| `uv lock --check` | Prove dependency lock did not drift. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |
| `make validate-pr` | Run repository PR validation gate. | yes |

### Acceptance Evidence

- Behavior evidence: final tests pass for learning primitives, supervised learner, plan/result/facade, native engine, observability, and fake external delegation.
- Design-decision evidence: docs and tests reflect all locked decisions and all explicit rejections.
- Future-roadmap/reuse evidence: docs include revisit triggers for Stage 13 prediction/evaluation, Stage 15 profiling, optional Lightning, future JAX, downstream persistence, and post-model batch pipelines.
- Example/demo evidence: native and fake external examples run or are test-backed; Lightning-like content is clearly documentation-only/future.
- Documentation evidence: public docs/docstrings explain shapes, units or indexes where relevant, metadata/provenance, failure behavior, and non-goals.
- Scientific contract evidence: final review confirms no hidden optimizer/export/config/checkpoint/datasource behavior and no prediction materialization in the trainer.

### Phase Workflow State

- Phase execution plan: completed inline by manager on 2026-05-16
- Planning/refinement budget: one docs/final-validation pass.
- Implementation/refinement budget: one documentation/polish pass plus final validation fixes.
- PR review budget: one final review focused on public docs, deferrals, and validation evidence.
- Blocker-resolution budget: stop if docs expose unimplemented features or tests reveal a cross-phase contract mismatch.
- Pre-submit blocker gate: full relevant validation completed or explicitly recorded with risk.
- Merge record: PR [#84](https://github.com/samcantrill/rphys/pull/84) merged to `develop` on 2026-05-16 as `8e434e6` (`docs: finish stage 12 learning training contracts`).

### Risks And Stop Conditions

- Risks: docs promising future features as current behavior, omitted deferral text for FR-12-9/DQ-12-7, incomplete final validation, docs-only changes drifting outside phase workflow.
- Stop conditions: examples require real Lightning/JAX/torch/logger dependencies, pipeline execution, workflow config parsing, artifact writing, or prediction export.
- Assumptions: earlier phases leave enough docstrings/examples hooks that this phase is mostly documentation and validation evidence, not API redesign.

### Completion Summary

- Implementation: completed Stage 12 examples, README/glossary updates, experimental `run_train` thin helper, public export/package tests, and final validation evidence.
- Validation: passed `make test-package`, `make test-unit`, `make test-contract`, `make test-integration`, `make test-summary`, `uv lock --check`, `git diff --check`, and `make validate-pr` in `/home/samcantrill/work/rphys-worktrees/stage-12-learning-training-p6-docs-examples-final-validation`.
- PR: [#84](https://github.com/samcantrill/rphys/pull/84)
- Merge: merged to `develop` on 2026-05-16 as `8e434e6`.
- Follow-up: real Lightning/JAX/torch/logger adapters, post-prediction batch pipelines, prediction export/materialization, evaluation/report generation, and deep profiling remain deferred to future roadmap stages.

## Cross-Phase Validation

- Full relevant test command: `make test-package && make test-unit && make test-contract && make test-integration && make test-summary && uv lock --check && git diff --check && make validate-pr`
- Final validation evidence: Phase 6 worktree passed `make test-package` (64 passed), `make test-unit` (753 passed), `make test-contract` (153 passed), `make test-integration` (24 passed), `make test-summary`, `uv lock --check`, `git diff --check`, and `make validate-pr` on 2026-05-16. `make test-summary` and `make validate-pr` wrote `build/test-summary.md`; e2e and acceptance suites were not present.
- Docs/template checks: verify docs/docstrings/examples match the approved facade/engine boundary, assembled-object plan, primitive result, fake external-only Stage 12 scope, and FR-12-9 documentation-only future compatibility.
- Scientific/workflow contract checks: no datasource scanning, dataloader construction, workflow runtime, config parsing, artifact/checkpoint writer, prediction export/materialization, learner-owned optimizer, Stage 11 stand-in, root-level placeholder export, broad registry, or heavy framework import appears.
- Example/demo checks: native supervised smoke flow, fake external delegation, duplicate trainable-owner guardrail, prediction pass-through, and future post-prediction batch-pipeline docs-only note.
- Manual review focus: preserve dependency direction `methods/objectives/metrics -> learning -> training -> downstream engines`; keep `rphys.learning` independent of `rphys.training`; confirm `Trainer` remains facade wording in code and docs; confirm `TrainingEngine` owns loop control.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| Phase 3 described a `Trainer` default placeholder before `NativeTrainingEngine` exists. | concern | Clarified that Phase 3 implements explicit selected-engine facade delegation only, and Phase 4 completes the public `NativeTrainingEngine` default. Placeholder default behavior is now a stop condition. | resolved |
| Phase 5 fake external summaries could be read as broad framework-state extraction. | concern | Clarified that fake external mapping covers only primitive optional evidence: logged metric names/values, checkpoint identifiers when already available, callback/profile status summaries, unavailable probes, and RemotePhys events. Parsing checkpoint files, logger internals, callback-private state, and framework-private objects remains out of scope. | resolved |
| Traceability, phase granularity, import boundaries, deferrals, validation coverage, and stop conditions were reviewed against the approved planning artifact. | note | No functionality or design queue needs reopening; no blocker remains before maintainer approval. | passed |

Gate result:

- Status: passed after manager design review; final maintainer approval remains pending
- Review evidence: reviewed `AGENTS.md`, `.codex/workflows/roadmap-version-planning.md`, `.codex/workflows/roadmap-version-implementation.md`, `.codex/prompts/implementation-plan-review.md`, `.codex/prompts/implementation-plan-refinement.md`, `.codex/templates/plan-review-report.md`, `.codex/templates/roadmap-stage-implementation-plan.md`, `docs/roadmap/stage-12/planning.md`, this implementation plan, Stage 10 method contract tests, Stage 11 synthetic integration tests, and package import-boundary tests. Findings were limited to two plan-clarity concerns and were resolved in this plan without changing approved behavior.
- Accepted risks: Stage 12 fake external-engine pressure may miss details a real Lightning adapter later needs; native `.backward()` fallback is intentionally minimal and future functional engines may need adapter-owned state; result schema may need additive fields after real external adapters.
- Revisit triggers: Stage 13 needs durable prediction rows/materialized samples or post-model processing; Stage 15 needs deeper profiling/timing semantics; a real Lightning adapter requires helper/protocol changes; a JAX prototype cannot use current learner/engine boundary without hidden state mutation; downstream workflows need additional primitive persistence identifiers.

## Final Approval

- Approval status: approved by maintainer on 2026-05-16
- Approved scope: Stage 12 implementation plan with six sequential phases: learning contract foundation, supervised learner composition, plan/result/facade boundary, native engine mechanics, observability/fake external pressure, and docs/examples/final validation.
- Accepted risks: Stage 12 fake external-engine pressure may miss details a real Lightning adapter later needs; native `.backward()` fallback is intentionally minimal and future functional engines may need adapter-owned state; result schema may need additive fields after real external adapters.
- Deferred items: real Lightning/JAX/torch/logger adapters; learner-level post-prediction `BatchOperationPipeline` execution; mode-specific prediction pipeline specs; `TrainingPlan` pipeline fields; trainer-owned prediction routing; sample uncollation adapters; datasource/dataloader/config/artifact/checkpoint/export/report ownership; Stage 15 deep profiling.
