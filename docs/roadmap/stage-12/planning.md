# Roadmap Stage 12 Planning

Status: implementation plan approved; Phase 1 implementation may begin through
the implementation workflow. Post-prediction batch pipeline implementation
remains deferred and documented as a future compatibility goal.
Roadmap version: `v12`
Stage directory: `docs/roadmap/stage-12/`

## Source Evidence

| Source | Relevant content | Used for | Notes |
| --- | --- | --- | --- |
| `AGENTS.md` | `rphys` is a reusable research library; core imports stay lightweight; public imports are intentional and tested; workflow assets record approvals, assumptions, validation evidence, and open questions. | Repository constraints and write scope. | This pass updates only `docs/roadmap/stage-12/planning.md` and writes no code or implementation plan. |
| `.codex/prompts/roadmap-stage-context-planner.md` | Requires source evidence, exploration coverage, roadmap extraction, capability triage, module behavior, functional requirements, and a functionality-agreement queue. | Current specialist pass instructions. | This pass reconstructs the missing full-template context/functionality sections around the existing focused design artifact. |
| `.codex/prompts/roadmap-stage-design-proposer.md` | Requires implementation-shape proposal, public/private interfaces, adapter boundaries, dependency direction, design decisions, design-agreement queue entries, classification, future-roadmap pressure, adversarial assumptions, and traceability to approved behavior. | Current design proposal pass instructions. | This pass adds independent design proposal evidence and does not implement code or create `implementation-plan.md`. |
| `.codex/templates/roadmap-stage-planning.md` | Defines the required planning sections, stage gates, readbacks, queues, requirements, behavior confirmation, checkpoints, validation, quality gate, and change log. | Section shape. | Existing Stage 12 content is preserved rather than replaced from the template. |
| `docs/roadmap.md` sections 1-7 | Purpose, canonical naming, API governance, scientific contract rules, field-centric design, thin semantic objects, training performance objective, package ownership, and import-boundary policy. | Architecture constraints. | Stage 12 must stay a reusable library layer, not a workflow runtime or framework-specific runner. |
| `docs/roadmap.md` Milestone 12 | Learner owns mode-specific step semantics; Trainer owns execution mechanics in roadmap shorthand; key interfaces include `Learner`, `SupervisedLearner`, `StepOutput`, `LoopMode`, `LoopContext`, `Trainer`, `TrainingPlan`, `TrainingResult`, events, callbacks, profilers, and experimental `run_train`; Lightning is optional. | Direct Stage 12 extraction. | Current approved design refines "Trainer owns loop mechanics" into `Trainer` facade plus selected `TrainingEngine` loop owner. |
| `docs/roadmap.md` Milestones 10, 11, 13, and 15 | Stage 10 provides `Method` and `MethodOutput`; Stage 11 provides objective/metric scalar and detached result contracts; Stage 13 consumes predictions and metric observations; Stage 15 deepens training profiling/data-path optimization. | Adjacent-stage compatibility. | Stage 12 must compose adjacent contracts without taking over prediction export, evaluation, reports, or Stage 15 profiler depth. |
| `docs/GLOSSARY.md` | Defines `Method`, `Loss`, `Objective`, `Metric`, `Learner`, and `Trainer` as distinct semantic objects. | Vocabulary. | Confirms `Learner` and `Trainer` should not collapse into method/model/loss/metric abstractions. |
| `docs/findings.md` | Prior comparison warns against copying downstream coupling of payloads, IO, tensor movement, caching, Lightning data modules, metrics, persistence, and workflows into `rphys` core. | Design pressure. | Supports explicit engine/adaptor boundaries and no project workflow ownership. |
| `docs/roadmap/stage-10/planning.md`; `src/rphys/methods/**`; `tests/contracts/test_method_contract.py`; `tests/contracts/test_trainable_method_contract.py` | Stage 10 implemented structural `Method`, patch-like `MethodOutput`, `PredictionContext`, explicit `apply_method_output`, backend-neutral `StateView`, and `ParameterView`; tests prove no training/export/metric behavior and no framework lifecycle hooks. | Upstream method and trainable evidence. | `StepOutput.predictions` should include `MethodOutput`; trainable parameter owner registration for external engines should stay adapter-local. |
| `docs/roadmap/stage-11/planning.md`; `src/rphys/losses/**`; `src/rphys/objectives/**`; `src/rphys/metrics/**`; `tests/integration/test_stage11_synthetic_contract_flow.py` | Stage 11 code now exists for loss/objective/metric contracts, raw backend-native scalar handles, `ObjectiveResult.total`, detached `MetricValue`, row-like observations, and dependency-light imports. | Objective and metric integration evidence. | This supersedes the older "Stage 11 absent" blocker; Stage 12 should integrate against these contracts where practical, with fakes only for engine-specific behavior. |
| `src/rphys/ops/pipelines.py`; `src/rphys/ops/batch.py`; `src/rphys/ops/sample.py`; Stage 7 operation tests | Existing `BatchOperationPipeline` and `SampleOperationPipeline` run operation sequences over concrete `Batch` or `Sample` containers and validate declared field effects. | Future post-prediction pipeline feasibility evidence. | These contracts make future batch processing over model outputs plausible, but Stage 12 only documents the desired capability and does not add learner pipeline execution. |
| `src/rphys/learning/__init__.py`; `src/rphys/training/__init__.py` | Learning and training package homes exist but export no public names. | Current Stage 12 implementation state. | Stage 12 will introduce the first code-backed learning/training contracts. |
| `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`; `pyproject.toml`; `tests/README.md` | Planned package homes include `rphys.learning` and `rphys.training`; dependencies are empty; import-boundary tests forbid heavy optional stacks such as torch, torchmetrics, numpy, pandas, scipy, video, and plotting libraries from core imports; suite layout defines package/unit/contract/integration placement. | Validation and dependency constraints. | Stage 12 must add focused package, unit, contract, and integration checks while keeping core imports lightweight. |
| Current `docs/roadmap/stage-12/planning.md` | Focused design narrative plus maintainer-approved decisions for `Trainer` facade, `TrainingEngine`, `NativeTrainingEngine`, simple `TrainingPlan`, simple `TrainingResult`, fake external-engine validation, provisional `StepOutput.predictions`, minimal `BackwardableScalar`, and real Lightning deferral. | Product/design input to preserve. | This pass adds missing scaffold and does not delete approved design-review findings or change-log entries. |

## Exploration Coverage

| Area | Files or patterns checked | Findings | Gaps |
| --- | --- | --- | --- |
| Roadmap and architecture docs | `AGENTS.md`, `docs/roadmap.md`, `docs/GLOSSARY.md`, `docs/findings.md` | Stage 12 is a reusable library training layer; no workflow runtime, artifact store, datasource scanning, prediction export, or heavy framework import belongs in core. | No separate feature docs exist under `docs/features`. |
| Workflow template and prompt | `.codex/prompts/roadmap-stage-context-planner.md`, `.codex/templates/roadmap-stage-planning.md` | The existing Stage 12 artifact lacked required context/functionality sections from the template. | Those sections have been reconstructed, manager-reviewed, and carried through validation/quality review. |
| Existing Stage 12 artifact | `docs/roadmap/stage-12/planning.md` | Strong design narrative and maintainer-approved design packets already exist. | Earlier evidence/status text still referenced missing functionality sections and stale Stage 11 absence; those are updated by this pass. |
| Stage 10 methods/trainable evidence | `src/rphys/methods/**`, `tests/contracts/test_method_contract.py`, `tests/contracts/test_trainable_method_contract.py`, `docs/roadmap/stage-10/planning.md` | `Method.predict` returns patch-like `MethodOutput`; methods do not train/export/log; trainable state/parameters are descriptive and backend-neutral. | No Stage 12 learner currently composes these contracts. |
| Stage 11 objective/metric evidence | `src/rphys/losses/**`, `src/rphys/objectives/**`, `src/rphys/metrics/**`, `tests/integration/test_stage11_synthetic_contract_flow.py`, `docs/roadmap/stage-11/planning.md` | Objective and metric records now exist with raw backend handles, detached metric values, and field patch semantics. | Stage 12 still needs actual learner/trainer integration tests against these code-backed contracts. |
| Operation pipelines | `src/rphys/ops/pipelines.py`, `src/rphys/ops/batch.py`, `src/rphys/ops/sample.py`, `tests/unit/rphys/ops/**`, `tests/contracts/test_operation_pipeline_contract.py` | Existing operation pipelines already compose field-transforming steps over concrete containers. `BatchOperationPipeline` is the plausible future primitive for post-model batch processing; `SampleOperationPipeline` should remain explicit caller adapter behavior if that path is ever approved. | Source evidence proves feasibility. Maintainer clarified Stage 12 should document the desired future capability rather than implement learner-local pipeline composition now. |
| Learning/training code | `src/rphys/learning/__init__.py`, `src/rphys/training/__init__.py` | Package homes are empty and dependency-light. | No Stage 12 code, tests, import exports, examples, or validation evidence yet. |
| Package/config/tests | `pyproject.toml`, `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`, `tests/README.md`, `tests/contracts/**`, `tests/integration/**` | Dependencies are empty; tests protect package imports and heavy optional dependency boundaries; suite placement is defined. | No Stage 12-specific package/contract/integration tests exist. |
| Archive/discussions | Existing Stage 10/11 planning and current Stage 12 narrative/change log only. | Archived planning content clarifies adjacent-stage decisions and maintainer approvals. | No additional external archive was needed for this context pass. |

## Roadmap Extraction

- Baseline roadmap outcome: define reusable `Learner` and `Trainer` contracts that keep learning semantics separate from loop mechanics and compose `Method`, optional `Objective`, and metrics into training, validation, test, and prediction steps. Post-prediction batch pipelines over model outputs are documented as a future compatibility goal, not Stage 12 implementation scope.
- Prerequisites: Stage 10 method contracts and patch-like `MethodOutput`; Stage 11 loss/objective/metric records including `ObjectiveResult.total` and detached metric values; existing `Sample`/`Batch` containers and lightweight import policy.
- Prior or adjacent roadmap links: Stage 10 supplies predictions and trainable descriptive records; Stage 11 supplies optimizer scalar and metric records; Stage 13 will consume predictions, metrics, diagnostics, and reports; Stage 15 will harden profiling, training events, and data-path performance.
- Primary feature docs: none found under `docs/features`; `docs/roadmap.md` is the canonical source.
- Deferred or out-of-scope roadmap work: real Lightning implementation, Fabric/JAX/torch integrations, dataset scanning, dataloader construction, prediction export/materialization, evaluation/report generation, checkpoint/artifact stores, distributed strategy, logger integrations, early stopping, full profiler integrations, concrete learner families beyond `SupervisedLearner`, and workflow/project configuration schemas.
- Compatibility obligations: base imports stay framework-free; `Learner` owns step semantics only; `Trainer` is the RemotePhys facade; selected `TrainingEngine` owns loop control; `TrainingPlan` stays assembled-object oriented; `TrainingResult` remains primitive summary evidence; no method/loss/objective/metric object owns optimizer, scheduler, checkpoint, logger, datasource, or export behavior. Future post-prediction transforms should be able to reuse existing operation pipelines without requiring trainer-owned routing or Stage 12 prediction materialization.
- Public surfaces or durable artifacts likely affected: provisional code-backed names under `rphys.learning` for `LoopMode`, `LoopContext`, `StepOutput`, `BackwardableScalar`, `Learner`, and `SupervisedLearner`; under `rphys.training` for `TrainingPlan`, `TrainingResult`, summaries, backend descriptors, events, profiling records, `Trainer`, `TrainingEngine`, `NativeTrainingEngine`, and experimental `run_train`; no durable file artifacts are expected.

## Overview

Stage 12 introduces the first reusable learning and training layer for
`rphys`. The design separates scientific step semantics from loop mechanics:

- A `Learner` defines what one train, validation, test, or prediction step
  means for the scientific method, objective, metrics, diagnostics, and
  provenance.
- A `Trainer` is the RemotePhys facade that selects a training engine,
  delegates loop control, and normalizes the returned training result. The
  selected engine defines how batches are iterated, how step contexts are
  created, how backward and optimizer mechanics happen, and how events and
  profiles are emitted.

This keeps `rphys` useful as a reusable research library without making it a
project workflow runtime. Datasource discovery, dataloader construction, config
parsing, artifact stores, experiment sweeps, export/materialization, and
framework-specific runners remain outside Stage 12 core.

- What this stage covers: learning modes and contexts, learner step output,
  `Learner` and `SupervisedLearner`, `Trainer` facade, provisional
  `TrainingEngine`, default `NativeTrainingEngine`, assembled-object
  `TrainingPlan`, primitive `TrainingResult`, backend descriptors for native
  mechanics, dependency-light events/profiles/observers, fake external-engine
  pressure tests, examples, docs, and import-boundary tests.
- Primary outcomes: a supervised learner can compose a Stage 10 method with
  Stage 11 objective and metrics; a trainer can run or delegate
  fit/validate/test/predict over already-built batches; native training can
  use only `StepOutput.objective` for backward; external engines can delegate
  control and normalize summary evidence without becoming core dependencies.
  Future batch-pipeline processing over model outputs is documented but not
  implemented in Stage 12.
- Non-goals: raw dataset access, dataloader building, project config, artifact
  directories, checkpoint writers, Lightning/JAX/torch imports in core, export,
  evaluation/reporting, and advanced Stage 15 profiler/data-path behavior.
- Impacted repo areas: `src/rphys/learning`, `src/rphys/training`,
  `src/rphys/errors.py` only if code-backed learning/training errors are
  needed, package import tests, unit tests for records and validation, contract
  tests for learner/trainer behavior, integration tests for synthetic
  method/objective/metric/native loop flow, and docs/docstrings.
- Current state: Stage 10 and Stage 11 upstream contracts exist; learning and
  training package homes are empty; no Stage 12 behavior or validation exists.
- Key uncertainty: no product-scope blocker remains after the maintainer
  clarified that post-prediction batch pipeline support should be documented
  as a desired future capability, not implemented in Stage 12.
- User clarification questions and resolved answers: current maintainer input
  locks the Trainer facade/TrainingEngine boundary, simple plan/result shapes,
  adapter-local trainable owner registration, provisional prediction union,
  minimal native backward surface, fake external-engine validation, and real
  Lightning deferral, and deferring learner-level post-prediction
  `BatchOperationPipeline` composition while documenting that future
  RemotePhys should be able to run batch pipelines over model outputs.
- Planning priority or optimization target: maximize valid experiment decisions
  per unit cost while keeping the Stage 12 core inspectable, dependency-light,
  and compatible with future optional engines.

## Stage Gates

| Gate | Required inputs | Current blockers or queue items | Status | Date/round | Notes |
| --- | --- | --- | --- | --- | --- |
| Roadmap briefing, capability triage, and candidate requirements | Roadmap extraction, source evidence, exploration coverage, overview, capability triage, module behavior map, functional requirements, initial functionality queue | None. | passed | 2026-05-16 / manager functionality review | Reconstructed context/functionality scaffold reviewed; no missing product-scope question found. |
| Functionality-agreement review | Functionality Agreement Queue FQ-12-1 through FQ-12-9 and FR-12-1 through FR-12-9 | None. | passed | 2026-05-16 / manager functionality review after pipeline deferral | FQ-12-1 through FQ-12-8 remain locked. FQ-12-9 is resolved as deferred/documentation-only future compatibility, so FR-12-9 is not a Stage 12 implementation requirement. |
| Behavior confirmation | Resolved functionality queue and behavior confirmation section | None. | passed | 2026-05-16 / manager behavior confirmation after pipeline deferral | Included/default/failure behavior is locked for FR-12-1 through FR-12-8. Post-prediction batch pipeline execution is documented as a future extension, not Stage 12 behavior. |
| Context checkpoint if applicable | Resume checkpoint and refreshed context if needed | Not needed unless the managing agent finds stale evidence or conflicting requirements. | not needed | 2026-05-16 / context planner reconstruction | Existing artifact was updated in place. |
| Design-agreement review | Proposed implementation shape, design decisions, design agreement queue, implication review, future-roadmap/reuse safety review | None. | passed | 2026-05-16 / manager design agreement after pipeline deferral | DQ-12-1 through DQ-12-6 remain locked. DQ-12-7 is resolved by deferring implementation and documenting future batch-pipeline compatibility. |
| Validation, phase shaping, and plan quality gate | Validation strategy, phase shaping, traceability review, specialist evidence check | None. | passed | 2026-05-16 / validation planner | Required validation, optional checks, phase boundaries, future-compatibility notes, and plan-quality evidence are recorded. Pipeline execution remains documentation/future-compatibility coverage only. |
| Implementation plan approved | Draft `docs/roadmap/stage-12/implementation-plan.md` plus implementation-plan design review and maintainer approval | None. | passed | 2026-05-16 / maintainer approval | Implementation plan has been reviewed, refined, and approved. Phase 1 implementation may begin through `.codex/workflows/roadmap-version-implementation.md`. |

## Stage Readbacks

| Stage | Gate result | Locked decisions | Defaults and recommendations | Open questions or blockers | Next focus |
| --- | --- | --- | --- | --- | --- |
| Roadmap briefing, capability triage, and candidate requirements | passed | Stage 12 scope is `Learner`/`Trainer` contracts with the approved facade/engine refinement. | Include the engine boundary, native reference engine, supervised learner, plan/result/event/profile vocabulary, fake external-engine validation, docs/examples, and import-boundary tests. Document future post-prediction batch-pipeline compatibility. | None. | Validation planning. |
| Functionality-agreement review | passed | FR-12-1 through FR-12-8 are locked; FR-12-9 is deferred/documentation-only. | FQ-12-1 through FQ-12-8 are preserved. Existing ops contracts make future batch-pipeline composition plausible, but Stage 12 does not implement it. | None. | Behavior confirmation. |
| Behavior confirmation | passed | Included/default/failure/unsupported/downstream/deferral behavior is locked. | Real Lightning/JAX remain deferred; post-prediction batch pipeline execution is also deferred while documented as future-compatible. | None. | Design agreement status. |
| Context checkpoint if applicable | not needed | Current artifact is updated in place. | Reopen only if evidence changes or Stage 11/Stage 10 code changes incompatibly. | None. | Continue workflow gates. |
| Design-agreement review | passed | DQ-12-1 through DQ-12-6 were approved or locked by maintainer on 2026-05-16 and are preserved. DQ-12-7 is resolved as deferral/documentation-only. | Proposer implementation-shape evidence is accepted after scoping DD-12-16 out of implementation. | None. | Validation planning. |
| Validation, phase shaping, and plan quality gate | passed | Required validation and reviewable phase boundaries are locked; FR-12-9/DQ-12-7 remains documentation-only. | Implementation phases must cover learning primitives, supervised learner composition, plan/result/facade contracts, native mechanics, observability/fake external pressure, docs/examples/final validation. | None. | Implementation-plan drafting may proceed. |
| Implementation-plan handoff | passed | Draft implementation plan exists, passed manager design review after refinement, and is maintainer-approved. | Six phases are defined with ownership, validation, acceptance evidence, risks, assumptions, and stop conditions. Phase 3 now avoids placeholder native-default behavior; Phase 5 now constrains fake external result mapping to primitive optional evidence. | None. | Begin Phase 1 implementation through the implementation workflow. |

## Capability Triage

| Capability | Decision | Rationale | Requirements produced | Notes |
| --- | --- | --- | --- | --- |
| Learning modes and loop contexts | include | Direct Stage 12 key interfaces; keeps mode distinct from split/workflow stage. | FR-12-1 | `LoopMode` covers train/validate/test/predict; `LoopContext` carries primitive metadata/provenance and loop indexes. |
| `Learner` structural contract | include | Roadmap says learner owns mode-specific step semantics and composes method/objective/metrics. | FR-12-1, FR-12-3 | Structural protocol, no registry or required base class. |
| `StepOutput` and backward scalar boundary | include | It is the handoff between learner semantics and engine mechanics. | FR-12-2, FR-12-4 | Predictions union and minimal native `BackwardableScalar` are maintainer-approved. |
| `SupervisedLearner` | include | Only initial concrete learner in roadmap; composes Stage 10 and Stage 11 contracts. | FR-12-3 | Other learner families remain deferred. |
| Differentiable post-prediction operation pipeline composition | defer / document future compatibility | Existing operation contracts make this plausible, but adding it to `SupervisedLearner` now would change public learner behavior and prediction semantics. The maintainer clarified that Stage 12 does not need to implement it now. | FR-12-9 deferred | Document that RemotePhys should remain able to perform batch pipelines over model outputs later; keep Stage 12 prediction handling field-aware enough that a future extension can apply `BatchOperationPipeline` without trainer-owned routing. |
| `Trainer` facade and `TrainingEngine` boundary | include | Maintainer-approved refinement that supports native and future external engines. | FR-12-5 | `Trainer` delegates to selected engine; engine protocol is provisional. |
| `NativeTrainingEngine` reference loop | include | Provides dependency-light executable semantics for tests/examples/simple runs. | FR-12-5, FR-12-6 | Reference-grade only, not Lightning-sized. |
| `TrainingPlan` assembled-object record | include | Keeps Stage 12 independent from project config/workflow/runtime schemas. | FR-12-6 | No `engine_config`, dataset paths, artifact dirs, Hydra schema, or dataloader construction. |
| `TrainingResult` and summaries | include | Required normalized evidence for native and external engines. | FR-12-7 | Primitive status/mode/count/failure/metric/event/profile summaries only. |
| Events, observer sinks, and profiling records | include | Direct roadmap key interfaces and Stage 15 compatibility foundation. | FR-12-8 | Dependency-light and cheap by default; deep profiler integrations deferred. |
| Native backend descriptors for device/backward/optimizer/scheduler mechanics | include | Roadmap assigns loop mechanics to trainer/training; native loop needs narrow hooks without importing frameworks. | FR-12-4, FR-12-6 | Descriptors stay optional and caller-owned; no backend catalog/registry. |
| Fake external-engine delegation and trainable-owner validation | include | Maintainer approved fake external-engine validation while deferring real Lightning. | FR-12-5, FR-12-7, FR-12-8 | No real Lightning/JAX/torch imports in Stage 12 core. |
| Experimental `run_train` | include | Roadmap allows stage-friendly function-style entrypoint that delegates and returns a typed result. | FR-12-5, FR-12-7 | Experimental only, no workflow runtime/config schema. |
| Concrete Lightning engine implementation | defer | Optional dependency and adapter behavior are approved as future work, not Stage 12 core. | None | Keep docs/examples/fake pressure tests only. |
| JAX engine or functional learner extension | defer | Future backend pressure; current engine boundary should not hard-code JAX or torch assumptions. | None | Revisit when a JAX prototype exists. |
| Mode-specific prediction pipeline specs | defer | Useful later if repeated training/eval/inference routing patterns emerge, but premature now. | None | Stage 12 defines no learner pipeline hook, no `TrainingPlan` mode routers, and no stable `PredictionPipelineSpec`; it only records the future compatibility goal. |
| Rich checkpointing, early stopping, logging, distributed, precision, profiler integrations | defer | Mature external engines and Stage 15 own advanced behavior. | None | Native engine may expose only narrow descriptors and summaries. |
| Prediction export/evaluation/report helpers | defer | Stage 13 owns durable prediction/evaluation/report behavior. | None | Trainer keeps predictions opaque. |
| Datasource scanning, dataloader construction, SampleBuilder, prepared data materialization | out of scope | Owned by earlier data/datasource stages or downstream workflows. | None | `TrainingPlan` consumes assembled iterables/loaders only. |
| Project config, workflow stages, artifact stores, run directories, sweeps | out of scope | Roadmap assigns generic workflow/runtime concerns to downstream projects or `loom`. | None | Do not add `Stage`, `ArtifactRef`, or project config schemas. |
| Concrete numerical losses, objectives, metrics, or learner families beyond supervised | out of scope | Stage 11 owns metric/objective contracts; concrete algorithms and extra learners need later pressure. | None | Stage 12 composes, it does not catalog algorithms. |

## Module Behavior Map

| Module or area | Intended behavior | Why it matters | Codebase capability enabled | Requirements produced | Status |
| --- | --- | --- | --- | --- | --- |
| `rphys.learning.modes` | Define execution modes `train`, `validate`, `test`, and `predict` independent from split names. | Prevents data partition labels and workflow stages from controlling optimization semantics. | Mode-aware learner and engine contracts. | FR-12-1 | draft |
| `rphys.learning.context` | Define primitive, immutable loop context records with mode, epoch/step/batch indexes, split label, metadata, and provenance. | Makes step provenance inspectable without adding global runtime state. | Reproducible learner calls and engine event context. | FR-12-1 | draft |
| `rphys.learning.output` | Define `StepOutput`, minimal `BackwardableScalar`, detached summaries, diagnostics, metadata, and provenance. | Separates scientific step outputs from loop mechanics. | Engine-neutral learner-to-trainer boundary. | FR-12-2, FR-12-4 | draft |
| `rphys.learning.core` | Define structural `Learner.step(batch, context) -> StepOutput`. | Supports extension by importable objects and avoids registries/base-class coupling. | Custom learner implementations without editing `rphys`. | FR-12-1 | draft |
| `rphys.learning.supervised` | Compose `Method`, optional `Objective`, and optional metrics into a `StepOutput`; default predictions to `MethodOutput`. | Gives Stage 12 one concrete learner while preserving Method/Object/Loss/Metric boundaries. | Synthetic supervised training/evaluation smoke paths. | FR-12-3 | draft |
| `rphys.ops` pipelines consumed by learning | Existing `BatchOperationPipeline` is the likely future primitive for batch-side processing over model outputs, but Stage 12 does not add a learner hook for it. | Records a future extension path without complicating the initial learner/trainer contracts. | Future training/eval/inference wrappers can compose batch pipelines over model outputs without trainer-owned routing if later approved. | FR-12-9 deferred | documented future compatibility |
| `rphys.training.plan` | Carry assembled batch iterables/loaders, primitive limits, observers, optional native backend descriptors, metadata, and provenance. | Prevents project config/framework schema leakage into the library core. | Stage-friendly but not workflow-owning training entrypoint. | FR-12-6 | draft |
| `rphys.training.results` | Record primitive status/mode/count/failure/metric/last-step/event/profile summaries and metadata/provenance. | Gives native/external engines a common result handoff. | Downstream persistence/report wrappers can consume summaries. | FR-12-7 | draft |
| `rphys.training.backend` | Define optional native device/backward/optimizer/scheduler descriptors or call hooks. | Keeps native loop useful without importing torch/JAX/Lightning. | Backend mechanics can be caller-supplied and tested with fakes. | FR-12-4, FR-12-6 | draft |
| `rphys.training.events` | Define dependency-light events, observer sinks/callbacks, phase/status vocabulary. | Native and external engines can expose comparable execution evidence. | Structured training observability foundation. | FR-12-8 | draft |
| `rphys.training.profiling` | Define cheap profile/span summaries and unavailable/overhead metadata. | Aligns with Stage 15 without implementing deep profiling now. | Basic timing/profiling evidence for native/fake engine runs. | FR-12-8 | draft |
| `rphys.training.core` | Define `Trainer` facade, provisional `TrainingEngine`, and `NativeTrainingEngine`. | Locks the approved facade/engine boundary. | Native and delegated training through one RemotePhys facade. | FR-12-5 | draft |
| `rphys.training.experimental` | Define experimental `run_train` that delegates to assembled trainer/plan/learner and returns `TrainingResult`. | Gives downstream wrappers a function-style hook without a workflow runtime. | Stage-friendly call surface. | FR-12-5, FR-12-7 | draft |
| `rphys.methods`, `rphys.objectives`, `rphys.metrics`, `rphys.data` | Provide existing method output, objective scalar, metric value, sample/batch contracts consumed by Stage 12. | Keeps Stage 12 composition grounded in code-backed contracts. | Cross-stage learner/trainer integration. | FR-12-2, FR-12-3 | existing upstream |
| `tests/package`, `tests/unit`, `tests/contracts`, `tests/integration`, `tests/support` | Protect imports, records, public contracts, synthetic composition, fake external engines, and no heavy dependencies; document future post-prediction pipeline compatibility without implementation tests in Stage 12. | Public learning/training behavior needs executable evidence before downstream use. | Reviewable validation and regression safety. | FR-12-1 through FR-12-8; FR-12-9 deferred documentation | draft |

## Functionality Agreement Queue

| Queue ID | Related requirement IDs | Depends on | Impact | What is being locked | Why it matters | Recommended answer | Trade-offs or rejected branches | Repo evidence or direct resolution | Exact feedback needed | State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FQ-12-1 | FR-12-1, FR-12-2, FR-12-3 | Stage 10/11 contracts | high | Learner step boundary and mode/context semantics. | This is the scientific contract that methods/objectives/metrics compose through. | Use a structural `Learner.step(batch, context) -> StepOutput`; keep `LoopMode` separate from split/workflow identity; keep context primitive/provenance-oriented. | Rejected: trainer-specific step hooks on methods; registry-only learners; split name as mode; context carrying dataloader/device/checkpoint/project config. | Roadmap Milestone 12, glossary, AGENTS modularity rules, and existing Method/Objective/Metric boundaries resolve this default; managing-agent review found no missing maintainer clarification. | None. | locked |
| FQ-12-2 | FR-12-2, FR-12-3, FR-12-4 | FQ-12-1; Stage 10/11 code | high | `StepOutput.predictions` and objective scalar/backward behavior. | It bridges learner outputs to native and delegated engine mechanics. | Keep `predictions: MethodOutput | Sample | Batch | None` provisionally; `SupervisedLearner` defaults to `MethodOutput`; trainer/engine treat predictions as opaque; native train mode uses minimal `.backward()` surface unless backend override is supplied. | Rejected: force all predictions into `Batch`; materialize/export predictions in trainer; make objective a metric name; require torch tensors or JAX functional state in core. | Maintainer approved DQ-12-5 on 2026-05-16; Stage 10/11 code supports the selected shape. | None. Carry validation obligations. | locked |
| FQ-12-3 | FR-12-3 | FQ-12-1; FQ-12-2 | medium | First concrete learner scope. | Stage 12 needs one executable learner without overcommitting to every learning style. | Implement only `SupervisedLearner` now; compose Stage 10 `Method`, optional Stage 11 `Objective`, and optional Stage 11 metrics; defer contrastive/self-supervised/masked/multitask classes. | Rejected: concrete learner catalog; learner-owned optimizer; learner-owned dataloader/export/checkpoint; objective/metric stand-ins in learning. | Roadmap explicitly names `SupervisedLearner` as only initial concrete learner and defers other styles; managing-agent review accepted this repo-resolved default. | None. | locked |
| FQ-12-4 | FR-12-4, FR-12-6 | FQ-12-2 | high | Native backend mechanics ownership. | Native engine must train simple cases without turning core into torch/JAX/Lightning. | Provide optional native descriptors/call hooks for device movement, backward, optimizer, scheduler, and related mechanics; no backend catalog, hard framework import, or project config. | Rejected: backend mechanics in `Method`/`Learner`; hard torch scalar requirement; distributed/precision/checkpoint/logging frameworks in core. | Roadmap assigns mechanics to trainer/training; import-boundary tests and maintainer DQ-12-5 approval constrain dependency posture; exact descriptor details are implementation-planning work under this locked boundary. | None. | locked |
| FQ-12-5 | FR-12-5 | FQ-12-1 | high | `Trainer` facade and provisional `TrainingEngine` boundary. | It controls public training entrypoints and future external-engine reuse. | Keep `Trainer` as the RemotePhys facade; selected `TrainingEngine` owns loop control through `fit/validate/test/predict(plan, learner)`; default engine is `NativeTrainingEngine`. | Rejected: `Trainer` as only loop implementation; Lightning as canonical runtime; engine registry now; `learner` embedded in `TrainingPlan`; single opaque `run(mode=...)` only. | Maintainer approved DQ-12-1 on 2026-05-16. | None. Carry validation obligations. | locked |
| FQ-12-6 | FR-12-6, FR-12-7 | FQ-12-5 | high | `TrainingPlan` and `TrainingResult` public behavior. | These records can accidentally become workflow config or framework-private state. | Keep plan simple and assembled-object oriented; keep result primitive and summary-oriented; include only minimal optional monitored metric/checkpoint identifiers when already available. | Rejected: `engine_config`, Hydra/project config, dataset paths, artifact dirs, framework loggers/callback objects, full checkpoint parsing, raw framework-private state, report generation. | Maintainer approved DQ-12-2 and DQ-12-3 on 2026-05-16. | None. Carry validation obligations. | locked |
| FQ-12-7 | FR-12-5, FR-12-7, FR-12-8 | FQ-12-5; FQ-12-6 | medium | External-engine scope and trainable owner registration. | Fake external tests need to prove the engine boundary without importing Lightning or duplicating parameters. | Validate delegated control with fake external engines; require exactly one explicit adapter-local trainable parameter owner shared with the method; do not add a public trainable-module helper/protocol; defer real Lightning. | Rejected: real Lightning core implementation; duplicate method+nested-module registration; core torch introspection; adapter wrapping native loop. | Maintainer approved DQ-12-4 and DQ-12-6 on 2026-05-16; Stage 10 `ParameterView` is descriptive, not framework policy. | None. | locked |
| FQ-12-8 | FR-12-8 | FQ-12-5; Stage 15 roadmap | medium | Event/profile/observer vocabulary scope. | Observability must be common enough for native/external engines but not become Stage 15 deep profiling. | Define cheap dependency-light `TrainingEvent`, observer sinks/callbacks, and profile/span summaries with explicit phase/status/unavailable/overhead metadata; defer logger integrations and deep profiler timelines. | Rejected: logger-specific APIs, callback loop control, hidden synchronization, GPU/system profiler requirements, checkpoint/logging features in native loop. | Roadmap Milestone 12 and 15 resolve scope; existing design review records native reference-grade guardrail; managing-agent review found no missing maintainer clarification. | None. | locked |
| FQ-12-9 | FR-12-3, FR-12-9 | FQ-12-2; Stage 7/10/11 code | high | Differentiable post-prediction operation pipelines. | Training, eval, and inference often need reusable processing after model outputs but before objectives, metrics, or export. | Do not implement optional learner-level `BatchOperationPipeline` composition in Stage 12. Document the desired future ability to perform batch pipelines over model outputs, and keep Stage 12 prediction handling field-aware and trainer-opaque so a later extension can add this without redesigning `Trainer`. | Rejected for Stage 12: trainer applies predictions implicitly; mode-specific pipeline specs now; automatic sample uncollation/collation; pipeline objects in `TrainingPlan`; detaching or materializing predictions by default; adding a `SupervisedLearner` pipeline argument now. | Existing `BatchOperationPipeline`, `MethodOutput`, and Stage 11 objective/metric contracts support the future composition technically. Maintainer clarified that implementation is not necessary for Stage 12 and should be documented for future work. | None. Carry only documentation and future-compatibility notes. | deferred / documented |

## Functional Requirements

| ID | Requirement | Depends on | Agreement queue | What | Why | Scope | User-visible behavior | Agent/system behavior | Codebase capability enabled | Impact | Out of scope | Validation | Recommendation | Decision/status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FR-12-1 | Define learning modes, loop context, and structural learner contract. | Stage 10/11 imports | FQ-12-1 | Add `LoopMode`, `LoopContext`, and `Learner.step(batch, context) -> StepOutput`. | Establish the scientific step boundary independent from loop mechanics. | Primitive mode/index/split/metadata/provenance context; structural protocol only. | Users can implement custom learners without subclassing or registering symbolic names. | Learner receives `Batch` plus context and returns `StepOutput`; it does not step optimizers, build loaders, export, or write checkpoints. | Mode-aware learner extension surface. | high | Datasource scans, dataloader builders, device/checkpoint/logging policy, workflow state. | Unit and contract tests for mode values, context validation, structural protocol, mode/split distinction, and forbidden responsibilities. | Repo-resolved default accepted by managing agent. | locked |
| FR-12-2 | Define `StepOutput` with opaque predictions, objective, terms, metrics, diagnostics, metadata, and provenance. | FR-12-1; Stage 10/11 code | FQ-12-2 | Add a dependency-light record that carries learner outputs to engines. | Engines need one boundary for backward, summaries, events, and later prediction/evaluation handoff. | `predictions: MethodOutput | Sample | Batch | None`; `objective: BackwardableScalar | None`; primitive summaries and mappings. | Users see predictions and metric/objective summaries preserved without trainer materialization. | Trainer/engine only interprets objective for backward and otherwise records/summarizes outputs opaquely. | Engine-neutral step result. | high | Prediction export, report tables, logger objects, framework-private state. | Unit/contract tests for accepted prediction types, immutable/primitive mappings, objective handling, and no prediction application/export in trainer. | Maintainer-locked default. | locked |
| FR-12-3 | Implement `SupervisedLearner` as the only concrete learner in Stage 12. | FR-12-1; FR-12-2; Stage 10/11 code | FQ-12-3 | Compose `Method.predict`, optional `Objective`, and optional metrics into `StepOutput`. | Provides executable supervised semantics without collapsing methods/losses/metrics/trainers. | Stage 10 `MethodOutput` default; local working batch/sample composition when objective/metrics need predictions; objective optional outside train; metrics detached. | Users can train/validate/test/predict simple supervised flows over existing `Batch` containers. | Fails clearly for train mode when objective/backward is required but unavailable; validate/test/predict avoid optimizer/backward behavior. | First concrete learner and synthetic vertical slice. | high | Contrastive, self-supervised, multitask, concrete algorithms, learner-owned optimizer/export/checkpoint. | Contract/integration tests with synthetic method/objective/metrics, prediction-only mode, missing objective failure, and no input batch mutation unless explicit local copy behavior is used. | Repo-resolved default accepted by managing agent. | locked |
| FR-12-4 | Define native backward and backend descriptor behavior without hard framework imports. | FR-12-2; FR-12-5 | FQ-12-2, FQ-12-4 | Provide minimal `BackwardableScalar` and optional backend/native descriptors for device movement, backward, optimizer, scheduler, and related train mechanics. | Native engine needs loop mechanics while core stays torch/JAX/Lightning-free. | Dependency-light protocols/callable descriptors, backend override path, train-only default backward. | Users can pass simple fake or backend-owned mechanics to native training. | Native train mode calls configured mechanics in order; validate/test/predict do not backward or optimizer-step. | Lightweight reference training loop. | high | Distributed strategy, precision/compile policy, checkpointing, logger/profiler frameworks, backend registry. | Tests for `.backward()` scalar, unsupported scalar error, backend override, device mover order, optimizer/scheduler train-only behavior, no heavy imports. | Repo-resolved default accepted by managing agent. | locked |
| FR-12-5 | Implement `Trainer` facade, provisional `TrainingEngine`, `NativeTrainingEngine`, and experimental `run_train`. | FR-12-1 through FR-12-4 | FQ-12-5, FQ-12-7 | `Trainer` dispatches mode-specific calls to selected engine; native engine runs reference loops; fake external engines prove delegation. | Supports a stable RemotePhys entrypoint while allowing delegated-control engines. | `fit`, `validate`, `test`, `predict`, thin `run(plan, learner)`, default native engine, fake external tests. | Users call the same facade for native or delegated engines. | Selected engine owns loop control; external engine path never runs native loop accidentally. | Native and delegated execution boundary. | high | Engine registry, real Lightning/JAX implementation, workflow runtime, project config parsing. | Contract/integration tests for facade dispatch, selected-engine delegation, native mode loops, fake external results, and experimental `run_train`. | Maintainer-locked default. | locked |
| FR-12-6 | Define neutral `TrainingPlan` for assembled objects and primitive loop limits. | FR-12-5 | FQ-12-4, FQ-12-6 | Carry caller-built batch iterables/loaders, loop limits, observers, optional native backend descriptors, metadata, and provenance. | Prevents rphys from owning project configuration or datasource/dataloader construction. | Fit/validate/test/predict batch sources, max epochs/steps, validation cadence if needed, event sinks/callbacks/profilers, backend descriptors, primitive metadata/provenance. | Users provide already assembled training inputs. | Plan validation rejects or omits framework/project config responsibilities. | Stage-friendly training input record. | high | `engine_config`, dataset paths, artifact dirs, Hydra/project configs, dataloader construction, Lightning trainer/logger/callback fields. | Unit tests for accepted fields, primitive metadata/provenance, loop limit validation, no config/path/artifact behavior, and engine config absence. | Maintainer-locked default. | locked |
| FR-12-7 | Define primitive `TrainingResult` and result-summary records. | FR-12-5; FR-12-6 | FQ-12-6, FQ-12-7 | Summarize status, mode, counts, failures, metrics, optional last-step/event/profile summaries, metadata, provenance, and minimal optional monitored metric/checkpoint identifiers. | Downstream workflow/reporting tools need reusable evidence without framework-private coupling. | Native and fake external result normalization; primitive/serializable where practical. | Users receive a consistent result object from native or delegated execution. | Engines normalize summaries and failure evidence; no raw logger/callback/checkpoint/framework objects are exposed. | Common result handoff for later Stage 13/downstream tools. | high | Durable artifact stores, full checkpoint parsing, report generation, callback-private state, logger-specific schemas. | Unit/integration tests for completed/failed/stopped/partial runs, metric summaries, missing optional engine evidence, primitive metadata, and no framework-private objects. | Maintainer-locked default. | locked |
| FR-12-8 | Define training event, observer, callback, and profiling vocabulary with fake external mapping tests. | FR-12-5; FR-12-7 | FQ-12-7, FQ-12-8 | Add dependency-light records and observer surfaces for loop phases, statuses, profile spans, unavailable probes, and overhead notes. | Native and delegated engines need comparable observability while Stage 15 remains future work. | Events/profiles for dataloader wait, device transfer, forward, objective/loss, backward, optimizer, callbacks/logging, checkpointing, validation/test/predict, whole-step timing, unavailable probes. | Users can inspect coarse execution evidence from training results or sinks. | Callbacks/sinks observe only; they do not control learner semantics or choose splits/loaders. | Shared native/external training observability. | medium | Logger integrations, deep profiler timelines, hidden synchronization, callback loop control, Stage 15 data-path benchmarking. | Tests for native event order, fake external event mapping, observer-only callbacks, profile summaries, unavailable probe metadata, and import boundaries. | Repo-resolved default accepted by managing agent. | locked |
| FR-12-9 | Deferred note: document future post-prediction `BatchOperationPipeline` capability. | FR-12-2; FR-12-3; Stage 7/10/11 code | FQ-12-9 | Document that RemotePhys should be able to perform batch pipelines over model outputs in a later stage or downstream wrapper. Do not add Stage 12 `SupervisedLearner` pipeline execution. | Preserves a useful future extension path while keeping the initial learner/trainer contracts simple. | Documentation and future-compatibility notes only; no learner constructor field, no mode-specific pipeline spec, no trainer-owned routing, and no automatic sample pipeline uncollation. | Users see no Stage 12 pipeline hook. They see docs explaining that `MethodOutput` remains field-aware and trainer-opaque so future post-model batch processing can be added. | Stage 12 implementation agents must not implement pipeline execution. They should avoid designs that materialize, detach, or export predictions in the trainer because that would make later batch-pipeline composition harder. | Future post-model processing without new Stage 12 implementation scope. | high | Concrete pipeline execution, mode-specific pipeline specs, trainer routing, export/materialization, automatic sample uncollation/collation, concrete signal-processing algorithms, no-grad/detach policy, backend autograd verification. | Docs/review checks only: examples and design notes must state this as a future capability, and validation planning must ensure no implementation phase assumes pipeline execution. | Maintainer clarified implementation is not needed now; document the future ability. | deferred / documented |

## Behavior Confirmation

- Included behavior: Stage 12 defines dependency-light learner/trainer contracts, `SupervisedLearner`, `StepOutput`, native reference execution, facade-to-engine delegation, neutral plans, primitive results, event/profile vocabulary, fake external-engine pressure tests, documentation/examples, and import-boundary validation. Post-prediction `BatchOperationPipeline` execution is not included; only the future compatibility goal is documented.
- Default behavior: `Trainer` defaults to `NativeTrainingEngine`; `TrainingEngine` remains provisional; `SupervisedLearner` returns Stage 10 `MethodOutput` by default; train mode expects an objective/backward path; validate/test/predict do not backward or optimizer-step; predictions remain opaque to trainers and engines.
- Failure behavior: invalid modes/contexts/plans/results fail loudly; train mode fails when a required objective or backward path is unavailable; unsupported scalar/backward behavior raises a learning/training error unless a backend override owns it; duplicate external trainable-owner registration fails in fake adapter tests; invalid metadata/provenance or non-primitive summaries fail where records require primitive values.
- Unsupported behavior: Stage 12 core does not scan datasources, construct dataloaders, parse project config, own artifact directories, write checkpoints, implement real Lightning/JAX/torch/logger adapters, export predictions, generate reports, run sweeps, add broad registries, add mode-specific prediction pipeline specs or trainer-owned prediction routing, implicitly uncollate/collate `SampleOperationPipeline`s, or implement concrete learner families beyond supervised.
- Resume/interruption behavior: this is a planning artifact only; no runtime resume behavior is locked. Training run resume/restart state is deferred to downstream workflow systems or later roadmap work unless a narrow Stage 12 native summary field is explicitly approved.
- Downstream implications: downstream projects or `loom` can construct `TrainingPlan`s from their own config and persist `TrainingResult`s; external engines can adapt their lifecycle into RemotePhys events/results without making framework imports core dependencies; Stage 13 can consume predictions/metrics later without trainer export behavior. Future post-model batch-pipeline composition should remain possible because trainers do not materialize or own predictions.
- Explicit deferrals: real Lightning implementation, JAX functional training, distributed synchronization, precision/compile policy, checkpoint writers, logger integrations, early stopping, full profiling/data-path optimization, prediction export/evaluation/reporting, workflow config/runtime, learner-level post-prediction batch pipeline execution, mode-specific prediction pipeline specs, automatic sample-pipeline adapters, backend autograd proof, and additional learner families.
- Why this behavior is locked: FR-12-1 through FR-12-8 follow roadmap boundaries, existing Stage 10/11 contracts, import-boundary tests, AGENTS reusable-library policy, and maintainer-approved or maintainer-locked design packets DQ-12-1 through DQ-12-6. FR-12-9 is deferred/documented by maintainer clarification.


## Why This Stage Exists

The adjacent contracts are already split by responsibility:

- Stage 10 `Method` objects predict from `Sample` or `Batch` containers and
  return patch-like `MethodOutput` records.
- Stage 11 defines objective, loss, and metric contracts.
- Stage 12 composes those contracts into learning steps and training loops.
- Stage 13 can later consume predictions, metric observations, diagnostics,
  and training summaries for prediction and evaluation.
- Stage 15 can later expand training events and profiling.

The main pressure is to avoid mixing these concerns too early. A method should
not own optimizer stepping. A learner should not build dataloaders or write
checkpoints. A trainer should not parse physiological selectors or compute
losses and metrics. Optional framework adapters should map into the same
library-level contracts without pulling framework imports into core.

## Proposed Public Structure

Stage 12 should open only scoped, code-backed module surfaces:

```text
rphys.learning.modes          # LoopMode
rphys.learning.context        # LoopContext and related context records
rphys.learning.output         # StepOutput, BackwardableScalar
rphys.learning.core           # Learner protocol
rphys.learning.supervised     # SupervisedLearner

rphys.training.plan           # TrainingPlan
rphys.training.results        # TrainingResult and summaries
rphys.training.backend        # backend/device/optimizer descriptors
rphys.training.events         # TrainingEvent, sinks, callbacks
rphys.training.profiling      # profile/span records
rphys.training.core           # Trainer facade, TrainingEngine, NativeTrainingEngine
rphys.training.experimental   # run_train
```

Package exports should expose only implemented names. Stage 12 should not add
root-level exports such as `rphys.Trainer`, placeholder modules, registries, or
stable package-level convenience helpers.

## Responsibility Map

| Object or module | Owns | Does not own |
| --- | --- | --- |
| `LoopMode` | The execution mode: train, validate, test, predict. | Dataset split, workflow stage, artifact state. |
| `LoopContext` | Primitive loop metadata such as mode, epoch, step, batch index, split name, metadata, and provenance. | Datasource construction or global runtime state. |
| `Learner` | Structural protocol for one step over a `Batch` plus context, returning `StepOutput`. | Optimizer stepping, scheduler stepping, checkpoint writing, dataloader construction, export. |
| `SupervisedLearner` | Composition of Stage 10 method output with Stage 11 objective and metrics; no Stage 12 post-prediction pipeline hook. | Framework lifecycle, device movement, optimizer policy, artifact persistence, mode-specific pipeline routing, future batch-pipeline execution. |
| Future post-prediction operation pipeline | Documented future ability to run caller-assembled batch transforms over model outputs after explicit `MethodOutput` application to a `Batch`. | Stage 12 implementation, model execution, trainer loop control, export/report behavior, mode routing, implicit sample uncollation/collation. |
| `StepOutput` | Predictions, objective scalar, detached terms/metrics, diagnostics, metadata, and provenance. | Loop control, device movement, persistence, export materialization. |
| `Trainer` | User-facing RemotePhys facade that dispatches to a selected training engine and normalizes `TrainingResult`. | Scientific loss/metric computation, datasource scanning, config parsing, workflow runtime, hard framework imports. |
| `TrainingEngine` | Actual loop-control boundary for native or delegated execution. | Scientific step semantics or public workflow configuration. |
| `NativeTrainingEngine` | Dependency-light reference loop over already-built `Batch` iterables, step contexts, backward, optimizer mechanics, events, profiles, and results. | Lightning-sized logging, checkpoint, profiler, callback, distributed, or dataloader features. |
| `TrainingPlan` | Assembled objects and primitive loop settings for a trainer run. | Serializable project config, Hydra schema, dataset path schema, artifact manifest. |
| `TrainingResult` | Summary of statuses, counts, failures, metrics, events, profiles, and step summaries. | Durable run storage or report generation. |
| Backend descriptors | Caller-owned hooks for device movement, backward, optimizers, schedulers, and related mechanics. | Backend catalogs, hard torch/JAX/Lightning imports, distributed runtime implementation. |
| Events/profiles/callbacks | Dependency-light observability records and observe-only callbacks. | Logger integrations, callback loop control, hidden synchronization side effects. |
| `run_train` | Experimental delegation to an assembled plan, trainer, and learner. | Config parsing, dataloader construction, artifact writing, stable workflow API. |

## Proposed Implementation Shape

Design proposer evidence date: 2026-05-16

The likely Stage 12 implementation should be small, module-local, and
assembled-object oriented. It should introduce code-backed learning and
training contracts without broad registries, root-package re-exports,
workflow/runtime configuration, dataset paths, artifact directories, or heavy
framework imports.

| Area | Likely public classes/functions/protocols | Internal helpers | Data flow and dependency direction | Related FRs | Extension and validation pressure |
| --- | --- | --- | --- | --- | --- |
| Learning modes and context | `LoopMode`, `LoopContext`, structural `Learner.step(batch, context) -> StepOutput` | Private coercion for mode, indexes, metadata, provenance, and primitive mappings. | `rphys.learning` may import `Batch`, `Sample`, `MethodOutput`, and Stage 11 result types; it must not import `rphys.training`, datasource, IO, export, or framework modules. | FR-12-1, FR-12-2 | Validate mode/split distinction, context failure behavior, structural protocol use, primitive metadata/provenance, and lightweight imports. |
| Step output and backward boundary | `StepOutput`, provisional `BackwardableScalar` protocol or helper check. | Private summary coercion and objective/backward validation helpers. | Learner returns predictions/objective/metrics/diagnostics; engines inspect only objective for train-mode backward and summarize other values opaquely. | FR-12-2, FR-12-4 | Validate `MethodOutput | Sample | Batch | None`, no trainer materialization/export, train objective-required failure, no backward outside train, unsupported scalar error, and backend override path. |
| Supervised learner | `SupervisedLearner`. | Private method-output local-application helper, Stage 11 objective/metric context assembly, result flattening into `StepOutput`. | `Method.predict` produces Stage 10 `MethodOutput`; learner applies it only to a local working batch when objective/metrics need predicted fields; objective/metrics remain Stage 11-owned. | FR-12-2, FR-12-3 | Validate Stage 10/11 composition, objective optional outside train, prediction-only mode, no input mutation unless explicit local copy behavior is used, and no learner-owned optimizer/export/checkpoint behavior. |
| Future post-prediction operation pipeline note | No public Stage 12 class/function. | None in Stage 12. | Planning/docs should record that future RemotePhys can run `BatchOperationPipeline` over model outputs without trainer-owned prediction materialization. | FR-12-9 deferred | Validate documentation only: implementation phases must not add a learner pipeline argument, mode-specific prediction spec, or trainer-owned pipeline routing in Stage 12. |
| Plan/result records | `TrainingPlan`, `TrainingResult`, minimal summary records for step, metric, event, profile, failure, and optional engine evidence. | Private validation for loop limits, primitive summaries, non-empty names, and failure/status records. | Callers assemble batch iterables/loaders, native backend descriptors, observers, metadata, and provenance into a plan; engines normalize primitive result evidence. | FR-12-5, FR-12-6, FR-12-7 | Validate absence of `engine_config`, project config, dataset paths, artifact dirs, raw framework objects, and durable persistence promises. |
| Trainer and engines | `Trainer`, provisional `TrainingEngine`, `NativeTrainingEngine`, experimental `run_train`. | Private mode dispatch, plan construction from convenience arguments, native loop iterators, context builders, and result accumulators. | User calls `Trainer`; `Trainer` delegates to selected engine; selected engine owns loop control; native engine runs already-built batch iterables; external fake engine returns normalized result without native-loop execution. | FR-12-5, FR-12-6, FR-12-7 | Validate facade dispatch, mode-specific engine calls, default native engine, fake external delegation, no accidental native loop execution, and provisional engine docs. |
| Native backend descriptors | Dependency-light callable descriptors for device movement, backward override, optimizer step/zeroing, scheduler step, and related native mechanics. | Private call ordering and train-only enforcement helpers. | Native engine invokes descriptors around learner steps; framework-specific policy stays in caller-owned hooks or external engines. | FR-12-4, FR-12-5, FR-12-6 | Validate call order, train-only optimizer/scheduler behavior, no hard torch/JAX assumptions, and clear errors for unavailable mechanics. |
| Events, observers, profiling | `TrainingEvent`, `TrainingEventSink`, `TrainingCallback`, `TrainingProfiler`, profile/span summary records. | Private phase vocabulary validation, observer fanout, span timing aggregation, unavailable-probe records. | Native and fake external engines emit comparable RemotePhys records; observers receive evidence but do not control learner semantics or choose data. | FR-12-7, FR-12-8 | Validate event order, observer-only callbacks, profile summaries, unavailable probes, overhead metadata, fake external mapping, and Stage 15 deferrals. |
| External-engine adapter pressure | No real public Lightning adapter in Stage 12 core; fake external engine/test adapter only. | Test-local fake trainable owner registration checks; no public helper/protocol. | Adapter-local code registers exactly one parameter-bearing object shared with the method and maps engine evidence to `TrainingResult`. | FR-12-5, FR-12-7, FR-12-8 | Validate one-registration guardrail, duplicate rejection, shared object identity, no core framework introspection, and no Lightning/torch/JAX imports. |

Proposed dependency direction:

```text
rphys.methods + rphys.objectives + rphys.metrics
  -> rphys.learning
  -> rphys.training
  -> downstream engines/adapters/workflows
```

`rphys.training` may depend on `rphys.learning`, but `rphys.learning` should not
depend on `rphys.training`. Optional external adapters may depend on framework
packages and `rphys.training`, but Stage 12 core must not depend on those
adapters. Downstream projects or `loom` translate their own config/workflow
objects into `TrainingPlan` and persist `TrainingResult`; Stage 12 does not
own that translation.

The proposed implementation should keep public protocol reuse narrow:
`Learner`, `TrainingEngine`, and observer/event protocols are reusable only for
learning/training semantics. Backend-, framework-, storage-, codec-,
dataset-, and project-specific policy belongs behind descriptors, adapters, or
downstream wrappers rather than inside the core records.

## Core Step Contract

The structural learner shape is intentionally small:

```python
class Learner(Protocol):
    def step(self, batch: Batch, context: LoopContext) -> StepOutput:
        ...
```

Custom learners can satisfy this protocol without subclassing a shared base
class or registering symbolic names. This matches the repository preference for
importable Python objects and avoids premature registries.

`LoopMode` is distinct from split identity:

```python
context = LoopContext(
    mode=LoopMode.TRAIN,
    epoch_index=0,
    step_index=12,
    batch_index=12,
    split_name="train",
    metadata={"smoke_test": True},
    provenance={"source": "synthetic"},
)
```

`mode=LoopMode.TRAIN` controls learning mechanics such as backward and
optimizer stepping. `split_name="train"` is provenance about the data. They are
often aligned, but they are not the same contract.

## StepOutput

`StepOutput` is the boundary between learner semantics and trainer mechanics:

```python
step = StepOutput(
    predictions=method_output,
    objective=objective_result.total,
    loss_terms={"waveform_mse": detached_loss_value},
    objective_terms={"total": detached_objective_value},
    metric_values={"heart_rate_mae": detached_metric_value},
    diagnostics={"num_valid_targets": 31},
    metadata={"window_seconds": 10.0},
    provenance={"objective": "SupervisedPulseObjective"},
)
```

The trainer interprets only `StepOutput.objective` for backward. Predictions,
loss terms, objective terms, metrics, diagnostics, metadata, and provenance stay
opaque to the trainer except for summaries and event/result recording.

The approved provisional prediction shape is:

```python
MethodOutput | Sample | Batch | None
```

`SupervisedLearner` should default to returning Stage 10 `MethodOutput`, because
that preserves patch semantics. The broader union keeps room for Stage 13 to
decide whether prediction/evaluation should consume patch-like outputs,
materialized `Sample` objects, materialized `Batch` objects, or no predictions.

Backward compatibility is intentionally minimal. If no backend adapter overrides
backward behavior, train mode expects an objective scalar with a small
`.backward()`-compatible surface:

```python
step.objective.backward()
```

Non-`.backward()` frameworks can be supported later through backend adapters
without changing learner or objective contracts.

## Supervised Learner

`SupervisedLearner` is the only concrete learner in Stage 12. It composes:

- a Stage 10 `Method`;
- an optional Stage 11 `Objective`;
- optional Stage 11 metrics.

Stage 12 does not add a post-prediction pipeline hook to
`SupervisedLearner`. It should still avoid trainer-side prediction
materialization so future work can run batch pipelines over model outputs.

Conceptual Stage 12 flow:

```python
prediction = method.predict(batch, context=context)

working_batch = apply_prediction_patch_for_local_use(batch, prediction)

objective_result = objective(working_batch, context=context)
metric_results = [metric(working_batch, context=context) for metric in metrics]

return StepOutput(
    predictions=prediction,
    objective=objective_result.total,
    metric_values=detach_metric_results(metric_results),
)
```

The local working batch is only for objective and metric computation. It
should not become an export path, a persistent materialization contract, or a
trainer-owned prediction processing mechanism.

Prediction mode works without objective or targets:

```python
learner = SupervisedLearner(method=method)

step = learner.step(
    batch,
    LoopContext(mode=LoopMode.PREDICT, batch_index=0),
)

assert step.objective is None
assert step.predictions is not None
```

Train mode should fail clearly when backward is required but no objective is
available. Validation, test, and prediction must not accidentally step
optimizers.

## Future Post-Prediction Pipelines

Stage 12 documents, but does not implement, the desired future ability to run
batch pipelines over model outputs. Existing operation contracts make the shape
plausible, and the Stage 12 design should avoid choices that would make this
future work hard.

A likely later flow would reuse the existing operation pipeline contracts
instead of adding a trainer-owned prediction router:

```text
Batch
  -> Method.predict
  -> MethodOutput
  -> apply_method_output(local Batch copy)
  -> optional BatchOperationPipeline
  -> Objective and Metrics
  -> StepOutput
```

`MethodOutput` remains patch-like. A configured pipeline sees a concrete
working `Batch`, so existing field-declaration and provenance behavior from
`BatchOperationPipeline` could be reused. Stage 12 should not detach,
materialize, export, or otherwise consume predictions inside the trainer,
because doing so would make this later composition harder.

No mode-specific `PredictionPipelineSpec`, `train_pipeline`, `eval_pipeline`,
or inference router is part of Stage 12. A later stage or downstream wrapper
can decide whether this belongs as a learner-level hook, an evaluation/export
adapter, or explicit caller composition.

`SampleOperationPipeline` is not hidden inside `SupervisedLearner`. If a
project needs sample-level post-prediction processing, it should provide an
explicit caller adapter that controls uncollation/collation and its scientific
meaning.

## Native Engine Flow

The native engine consumes already-built `Batch` iterables behind the
RemotePhys `Trainer` facade:

```python
trainer = Trainer(engine=NativeTrainingEngine())

result = trainer.fit(
    learner=learner,
    train_batches=train_batches,
    validate_batches=validate_batches,
)
```

The native engine loop is mechanical:

```text
for epoch in epochs:
  for batch_index, batch in enumerate(train_batches):
    context = LoopContext(mode=TRAIN, epoch_index=epoch, batch_index=batch_index)
    batch = device_mover(batch)                         # if configured
    step = learner.step(batch, context)
    backward(step.objective)                            # train mode only
    optimizer.step()                                    # train mode only
    scheduler.step()                                    # if configured
    emit events and profile spans

return TrainingResult(...)
```

Mode-specific entrypoints should be explicit:

```python
trainer.fit(...)
trainer.validate(...)
trainer.test(...)
trainer.predict(...)
```

For the native engine, `Trainer.run(plan)` should be a thin dispatch helper over
the same methods, not a separate workflow runtime. For delegated engines,
`Trainer.run(plan)` dispatches to the selected engine instead of running the
native loop.

## Training Plan And Result

`TrainingPlan` is assembled-object oriented:

```python
plan = TrainingPlan(
    train_batches=train_batches,
    validate_batches=validate_batches,
    max_epochs=5,
    device_mover=device_mover,
    optimizer=optimizer_spec,
    event_sinks=[recording_sink],
    profilers=[profiler],
    metadata={"run_label": "synthetic-smoke"},
)
```

It should not accept raw project configuration, dataset paths, artifact
directories, or serialization promises.

`TrainingResult` summarizes what happened:

```python
result = TrainingResult(
    status="completed",
    epochs_completed=5,
    steps_completed=1200,
    failures=[],
    metric_summaries={"val_heart_rate_mae": 1.8},
    event_summary=event_summary,
    profile_summary=profile_summary,
)
```

Downstream workflow tools can persist or report this result, but Stage 12 core
does not write durable run artifacts.

## Events And Profiling

Stage 12 defines dependency-light event and profile records so native and
future framework-backed execution can produce comparable evidence:

```python
event = TrainingEvent(
    source="native",
    mode=LoopMode.TRAIN,
    phase="optimizer_step",
    position="end",
    epoch_index=0,
    step_index=12,
    batch_index=12,
    status="ok",
    metadata={"optimizer": "fake"},
)
```

The controlled phase/span vocabulary should cover dataloader wait, device
transfer, forward, objective/loss, backward, optimizer step, callbacks/logging,
checkpointing, validation/test/predict, whole-step timing, unavailable probes,
and synchronization overhead.

Callbacks are observe-only in Stage 12. They can receive events and contexts,
but they cannot change learner semantics, request loop control, or become
logger-specific integration points.

## Trainer Engine Architecture And Delegated Control

RemotePhys should keep `Trainer` and `Learner` as the stable library-facing
paradigm, but it should not require the native trainer loop to implement every
feature that mature external engines already provide. The design should treat
loop execution as an engine boundary:

```text
RemotePhys Trainer facade
  -> NativeTrainingEngine for dependency-light reference execution
  -> LightningTrainingEngine adapter for Lightning-controlled execution
  -> Future JaxTrainingEngine or other engines for different backend paradigms
```

This avoids two bad outcomes:

- coupling RemotePhys core to Lightning's object model, callback system,
  checkpoint format, and logging stack;
- rebuilding Lightning-sized functionality in the native trainer before the
  library actually needs it.

The stable contract remains:

```text
Batch-like input + LoopContext -> Learner.step -> StepOutput -> TrainingResult
```

The engine decides how control reaches that learner step and who owns the
mechanics around it.

| Layer | Stable responsibility | Example native owner | Example delegated owner |
| --- | --- | --- | --- |
| `Learner` | Scientific step semantics. | `SupervisedLearner`. | Same `SupervisedLearner` called by adapter hooks. |
| `StepOutput` | Objective, predictions, metrics, diagnostics, metadata, provenance. | Returned to native trainer. | Returned to Lightning/JAX adapter, then logged or summarized. |
| `Trainer` | User-facing RemotePhys training facade and result normalization. | Delegates to native engine by default. | Delegates to an external engine adapter. |
| `TrainingEngine` | Actual loop control. | Native loop over `Iterable[Batch]`. | Lightning `Trainer`, future JAX loop, or downstream runtime. |
| Backend mechanics | Device, backward, optimizer, scheduler, precision, distributed behavior. | Native descriptors/adapters. | External engine configuration. |
| Observability | RemotePhys event/profile vocabulary and `TrainingResult` summaries. | Native event/profile emission. | Adapter maps external hooks/logs/profiles back to RemotePhys records. |

A provisional engine protocol can be kept narrow:

```python
class TrainingEngine(Protocol):
    def fit(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        ...

    def validate(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        ...

    def test(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        ...

    def predict(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        ...
```

The public `Trainer` can stay as the RemotePhys entrypoint:

```python
trainer = Trainer(engine=NativeTrainingEngine())
result = trainer.fit(
    learner=learner,
    train_batches=train_batches,
    validate_batches=validate_batches,
)
```

The same facade can delegate control to an external engine:

```python
lightning_engine = LightningTrainingEngine(
    lightning_trainer=lightning_trainer,
    module_factory=RemotePhysLightningModule,
    trainable_module=network,
)

trainer = Trainer(engine=lightning_engine)

result = trainer.run(
    TrainingPlan(
        train_batches=train_loader,
        validate_batches=validate_loader,
        metadata={"engine": "lightning"},
    ),
    learner=learner,
)
```

In that delegated path, `Trainer.run(...)` is not looping over batches itself.
It asks the selected engine to run. The Lightning engine creates the
`RemotePhysLightningModule`, calls Lightning's `Trainer.fit(...)`,
collects logged values, checkpoint metadata, callback state summaries, profiler
summaries, and adapter-emitted RemotePhys events, then normalizes that into a
`TrainingResult`.

`TrainingPlan` should not become the place where Lightning or JAX configuration
lives. Engine-specific objects such as a Lightning trainer, logger list,
callback list, accelerator policy, precision policy, or future JAX compile
policy belong on the engine or adapter object. The plan may carry assembled
batch iterables or loader objects supplied by the caller, loop limits,
callbacks/sinks that are part of RemotePhys, and primitive metadata/provenance.
It should not construct dataloaders or parse framework configuration.

The design can support three execution modes without changing `Learner`:

| Execution mode | Who owns loop control? | Why use it? | What RemotePhys should provide |
| --- | --- | --- | --- |
| Native engine | RemotePhys native trainer loop. | Lightweight tests, examples, simple dependency-free runs, reference semantics. | `NativeTrainingEngine`, backend descriptors, events/profiles, result summaries. |
| External delegated engine | Lightning, future JAX engine, or downstream runtime. | Mature logging, checkpointing, accelerators, distributed training, precision, callbacks, profiling. | Adapter protocol, context/step/output mapping, result normalization. |
| Hybrid native engine with backend adapters | RemotePhys loop plus caller-supplied backend mechanics. | Users want RemotePhys loop semantics but custom backward/optimizer/device behavior. | Narrow backend descriptors without external framework imports. |

For a future JAX path, the same engine boundary helps avoid baking torch or
Lightning assumptions into the learner/trainer contract. A `JaxTrainingEngine`
may need a functional learner implementation, explicit train state, PRNG keys,
and `value_and_grad`-style mechanics. That should be an engine/adapter concern
or a later functional learner extension, not a reason for Stage 12 to make the
native trainer a universal backend framework.

Stage 12 should therefore define the engine boundary and native reference
engine, plus fake external-engine pressure tests. A real Lightning engine can
live behind an optional adapter module or later implementation phase; core
imports must remain Lightning-free.

The main Stage 12 design rule is:

```text
RemotePhys defines the learning contract and result vocabulary.
The selected engine owns loop control and backend mechanics.
Adapters translate engine-specific behavior back into RemotePhys records.
```

## Alignment With Torch Lightning

Lightning has its own `Trainer` and loop machinery. In Lightning, users define
step hooks such as `training_step`, `validation_step`, `test_step`, and
`predict_step` on a `LightningModule`, while Lightning's `Trainer` owns device
placement, gradient mode, backward, optimizer stepping, scheduler stepping,
callbacks, logging, checkpointing, precision, and distributed mechanics.

Under the engine architecture, Lightning integration is not an adapter around
the native RemotePhys trainer loop. It is a delegated-control engine that calls
the same learner contract while Lightning owns the loop:

```text
RemotePhys owns: Method -> Learner.step -> StepOutput
Lightning owns:  loop, device, backward, optimizer, scheduler, callbacks, logs
Adapter owns:    translating Lightning hooks into RemotePhys LoopContext calls
```

This means there are two compatible execution paths over the same learner:

```text
Native path:
Batch iterable -> Trainer with NativeTrainingEngine -> Learner.step
               -> StepOutput -> TrainingResult

Lightning path:
DataLoader -> Lightning Trainer -> LightningModule adapter -> Learner.step
           -> StepOutput -> Lightning mechanics -> RemotePhys-compatible summary/events
```

The native `NativeTrainingEngine` is a dependency-light reference loop and
library baseline. Lightning is an optional stronger loop engine for users who
want Lightning's device, distributed, precision, callback, logging, checkpoint,
and dataloader integration behavior.

| RemotePhys concept | Native rphys execution | Lightning-backed execution |
| --- | --- | --- |
| `SupervisedLearner.step` | Called by `NativeTrainingEngine` through the `Trainer` facade. | Called by an optional `LightningModule` adapter from `training_step`, `validation_step`, `test_step`, or `predict_step`. |
| `StepOutput.objective` | Native trainer uses it for backward unless a backend adapter overrides backward. | Adapter returns it as the Lightning loss for automatic optimization, or passes it to Lightning manual optimization. |
| `StepOutput.predictions` | Native trainer keeps it opaque and records summaries only. | Adapter may return/log selected values, but Lightning should not force a new rphys prediction schema. |
| `TrainingEvent` and profile spans | Emitted directly by native trainer. | Optional adapter maps Lightning hooks into the same event/profile records. |
| Backend descriptors | Caller-owned native loop mechanics. | Usually replaced by Lightning `configure_optimizers`, strategy, precision, callbacks, and trainer settings. |
| `TrainingPlan` / `TrainingResult` | Native assembled-object plan and summary result. | Downstream wrapper can translate assembled objects into Lightning module/trainer calls and then summarize back into `TrainingResult`. |

The important design choice is that `SupervisedLearner` should not subclass
`LightningModule`, and `rphys.training.Trainer` should not import or wrap
Lightning's `Trainer` in core. A future optional adapter can sit at the edge.

### Learner Versus Trainable Module

The `Learner` and the Lightning-visible trainable module are different
concepts:

| Concept | Role | Typical owner |
| --- | --- | --- |
| `SupervisedLearner` | Scientific step orchestration: call the method, apply prediction patches locally when needed, evaluate objective/metrics, and return `StepOutput`. | RemotePhys core. |
| `Method` | Prediction semantics over `Sample` or `Batch`; may hold or reference a backend model. | RemotePhys core or downstream method implementation. |
| trainable module / parameter owner | The torch `nn.Module` or parameter-bearing object Lightning must register for device movement, checkpointing, and optimizer construction. | Optional Lightning adapter or downstream integration. |
| `RemotePhysLightningModule` | Bridge from Lightning hooks to `Learner.step`; registers the trainable module for Lightning. | Optional adapter. |

There should not be two learnable models. In a torch-backed method, the same
module object can be referenced by both the method and the Lightning adapter:

```python
network = PulseNet()
method = TorchPulseMethod(model=network)
learner = SupervisedLearner(method=method, objective=objective, metrics=[metric])

lightning_module = RemotePhysLightningModule(
    learner=learner,
    trainable_module=network,  # same object used by method, not a copy
    optimizer_factory=lambda parameters: torch.optim.Adam(parameters, lr=1e-3),
)
```

The learner stores step semantics and may indirectly hold the trainable state
through `method`. The Lightning adapter stores a direct reference to the same
trainable module so Lightning can discover parameters and apply framework
mechanics. This is a registration/reference concern, not a second model or a
second learning abstraction.

The adapter must avoid registering the same parameter-bearing module twice under
different Lightning attributes. For torch-backed methods, prefer one explicit
Lightning registration point such as `self.trainable_module = network`, while
the learner remains a plain RemotePhys object. If a method object is itself a
torch module, register that method object directly instead of separately
registering both the method and a nested module.

If the method itself is a torch module, the adapter can register the method:

```python
method = TorchPulseMethod(...)
learner = SupervisedLearner(method=method, objective=objective)

lightning_module = RemotePhysLightningModule(
    learner=learner,
    trainable_module=method,
    optimizer_factory=make_optimizer,
)
```

If the method is a pure Python object that owns a nested torch module, the
adapter should register that nested module. If a future backend does not expose
a torch module, Lightning integration is adapter-specific and should not force
new fields onto `SupervisedLearner`.

### Lightning Adapter With Automatic Optimization

With Lightning automatic optimization, `training_step` returns the objective
scalar and Lightning owns backward, optimizer stepping, scheduler stepping,
precision, and distributed mechanics. The adapter records or logs selected
values, but it does not reinterpret the scientific result.

```python
class RemotePhysLightningModule(LightningModule):
    def __init__(self, learner, trainable_module, optimizer_factory, event_sink=None):
        super().__init__()
        self.learner = learner
        # Same parameter-bearing object used by the learner's method.
        # Registering it here lets Lightning own framework mechanics.
        self.trainable_module = trainable_module
        self.optimizer_factory = optimizer_factory
        self.event_sink = event_sink

    def training_step(self, batch, batch_idx):
        context = LoopContext(
            mode=LoopMode.TRAIN,
            batch_index=batch_idx,
            metadata={"engine": "lightning"},
        )
        step = self.learner.step(batch, context)
        self._record_step_output(step, prefix="train")
        return step.objective

    def validation_step(self, batch, batch_idx):
        context = LoopContext(
            mode=LoopMode.VALIDATE,
            batch_index=batch_idx,
            metadata={"engine": "lightning"},
        )
        step = self.learner.step(batch, context)
        self._record_step_output(step, prefix="val")
        return step.metric_values

    def test_step(self, batch, batch_idx):
        context = LoopContext(
            mode=LoopMode.TEST,
            batch_index=batch_idx,
            metadata={"engine": "lightning"},
        )
        step = self.learner.step(batch, context)
        self._record_step_output(step, prefix="test")
        return step.metric_values

    def predict_step(self, batch, batch_idx):
        context = LoopContext(
            mode=LoopMode.PREDICT,
            batch_index=batch_idx,
            metadata={"engine": "lightning"},
        )
        step = self.learner.step(batch, context)
        self._record_step_output(step, prefix="predict")
        return step.predictions

    def configure_optimizers(self):
        return self.optimizer_factory(self.trainable_module.parameters())
```

The `trainable_module` exists so Lightning can discover parameters, move state
to devices, checkpoint state, and own optimizer construction. It should be the
same parameter-bearing object used by the learner's method, not an independent
copy. This is adapter surface, not a Stage 12 core import requirement.

### Lightning Adapter With Manual Optimization

If a downstream integration needs Lightning manual optimization, the adapter
can disable automatic optimization and call Lightning's manual optimization
helpers. The learner still does not step optimizers.

```python
class RemotePhysManualLightningModule(LightningModule):
    def __init__(self, learner, trainable_module, optimizer_factory):
        super().__init__()
        self.automatic_optimization = False
        self.learner = learner
        # Same parameter-bearing object used by the learner's method.
        self.trainable_module = trainable_module
        self.optimizer_factory = optimizer_factory

    def training_step(self, batch, batch_idx):
        optimizer = self.optimizers()

        context = LoopContext(
            mode=LoopMode.TRAIN,
            batch_index=batch_idx,
            metadata={"engine": "lightning", "optimization": "manual"},
        )
        step = self.learner.step(batch, context)

        optimizer.zero_grad()
        self.manual_backward(step.objective)
        optimizer.step()

        self._record_step_output(step, prefix="train")
        return step.objective

    def configure_optimizers(self):
        return self.optimizer_factory(self.trainable_module.parameters())
```

Manual optimization is an optional adapter concern. It must not move optimizer
logic into `SupervisedLearner`.

### Batch And Device Transfer

Lightning may receive `rphys.data.Batch` objects from a `DataLoader` or
`LightningDataModule`. If the batch container is not automatically transferable
by Lightning, the adapter can define transfer behavior:

```python
class RemotePhysLightningModule(LightningModule):
    def transfer_batch_to_device(self, batch, device, dataloader_idx):
        if isinstance(batch, Batch):
            return move_remotephys_batch_to_device(batch, device)
        return super().transfer_batch_to_device(batch, device, dataloader_idx)
```

This keeps device transfer outside `SupervisedLearner`. The learner receives a
batch and context; it does not know whether the native trainer, Lightning, or
another engine moved that batch.

### Event And Profile Mapping

A Lightning adapter can map hook boundaries into the same Stage 12 event and
profile vocabulary used by the native trainer:

```python
def training_step(self, batch, batch_idx):
    context = LoopContext(
        mode=LoopMode.TRAIN,
        batch_index=batch_idx,
        metadata={"engine": "lightning"},
    )

    self.event_sink.emit(TrainingEvent(
        source="lightning",
        mode=LoopMode.TRAIN,
        phase="forward",
        position="start",
        batch_index=batch_idx,
    ))

    step = self.learner.step(batch, context)

    self.event_sink.emit(TrainingEvent(
        source="lightning",
        mode=LoopMode.TRAIN,
        phase="objective_loss",
        position="end",
        batch_index=batch_idx,
        metadata={"has_objective": step.objective is not None},
    ))

    return step.objective
```

The adapter can also translate Lightning callback, validation, test, prediction,
logging, checkpoint, and profiler hooks into `TrainingEvent` or profile span
records. Stage 12 core should only define the shared records and vocabulary; it
should not import Lightning to implement concrete hook mapping.

### Delegating Lightning Features Without Duplicating Them

When Lightning is the selected engine, RemotePhys should not reimplement
Lightning's logging, checkpoint, early stopping, profiler, precision, or
distributed behavior. The adapter should expose RemotePhys values to the
Lightning surfaces that already drive those features.

| Feature | Lightning owner | RemotePhys adapter responsibility |
| --- | --- | --- |
| Logging | Lightning `self.log`, `self.log_dict`, and configured loggers. | Convert selected `StepOutput` objective, metrics, and diagnostics into stable log names. |
| Multiple checkpoints | Lightning `ModelCheckpoint` callbacks. | Ensure monitored metrics such as `val/objective` or `val/heart_rate_mae` are logged. |
| Early stopping | Lightning `EarlyStopping` callback. | Log the monitored validation metric with the expected name and cadence. |
| Profiling | Lightning trainer profiler. | Optionally emit RemotePhys event/profile records at scientific boundaries such as method forward and objective computation. |
| Precision/distribution/device | Lightning `Trainer` configuration, strategies, accelerators, and batch transfer hooks. | Keep learner code device-agnostic and register the same trainable module used by the method. |
| Callback lifecycle | Lightning callbacks. | Avoid duplicating loop-control callbacks in RemotePhys core; map important callback lifecycle evidence into RemotePhys events if needed. |

Example adapter logging:

```python
def _record_step_output(self, step, prefix):
    if step.objective is not None:
        self.log(
            f"{prefix}/objective",
            step.objective,
            on_step=prefix == "train",
            on_epoch=True,
            prog_bar=prefix in {"train", "val"},
            logger=True,
        )

    for name, value in step.metric_values.items():
        self.log(
            f"{prefix}/{name}",
            value,
            on_step=prefix == "train",
            on_epoch=True,
            prog_bar=prefix == "val",
            logger=True,
        )
```

Example Lightning-controlled execution:

```python
checkpoint_best_metric = ModelCheckpoint(
    monitor="val/heart_rate_mae",
    mode="min",
    save_top_k=3,
    filename="best-mae-{epoch}",
)

checkpoint_best_objective = ModelCheckpoint(
    monitor="val/objective",
    mode="min",
    save_top_k=2,
    filename="best-objective-{epoch}",
)

early_stopping = EarlyStopping(
    monitor="val/heart_rate_mae",
    mode="min",
    patience=10,
)

lightning_trainer = LightningTrainer(
    accelerator="gpu",
    devices=1,
    precision="16-mixed",
    logger=[tensorboard_logger, csv_logger],
    callbacks=[checkpoint_best_metric, checkpoint_best_objective, early_stopping],
    profiler="simple",
    max_epochs=100,
)

engine = LightningTrainingEngine(
    lightning_trainer=lightning_trainer,
    module_factory=RemotePhysLightningModule,
    trainable_module=network,
)

result = Trainer(engine=engine).run(plan, learner=learner)
```

In this example, RemotePhys does not decide which checkpoints to save, when to
early stop, how to reduce distributed metrics, how to flush logs, or how to run
the profiler. It supplies the scientific values and maps the resulting
Lightning execution evidence back into `TrainingResult`.

### Design Consequences

The Lightning integration confirms the Stage 12 boundary:

- `SupervisedLearner` remains the reusable scientific unit.
- The trainable module remains the backend parameter owner; when Lightning is
  used, the adapter registers the same object that the method uses.
- `Trainer` remains the RemotePhys user-facing facade and result-normalization
  point.
- `NativeTrainingEngine` remains a lightweight reference loop.
- Lightning integration is an optional delegated engine that calls the same
  learner from Lightning hooks.
- Lightning-specific data modules, dataloaders, strategies, precision,
  checkpointing, logging, and distributed behavior stay outside core.
- `StepOutput.objective` is the one value a loop engine may use for backward.
- `StepOutput.predictions`, metrics, diagnostics, metadata, and provenance
  remain learner outputs that the adapter may summarize or log without changing
  their meaning.

## Design Review: Trainer Engine Boundary

Review date: 2026-05-16

Review result: pass with guardrails. The delegated-engine architecture is a
better fit than treating Lightning as a wrapper around the native trainer loop,
because it lets RemotePhys keep its learner/trainer vocabulary while avoiding a
partial reimplementation of mature framework features.

| Finding | Severity | Impact | Resolution |
| --- | --- | --- | --- |
| Older wording made `Trainer` sound like the native loop owner. | high | Conflicts with the new facade/engine design and would make Lightning delegation look bolted on. | Updated the responsibility map and phase shape so `Trainer` is the facade, `TrainingEngine` owns loop control, and `NativeTrainingEngine` is the reference loop. |
| `TrainingPlan` could become an engine-specific config container. | high | Lightning callbacks, loggers, precision, accelerator, and future JAX compile policy could leak into stable RemotePhys records. | Engine-specific configuration belongs on the engine/adapter object; `TrainingPlan` carries assembled inputs, loop limits, RemotePhys callbacks/sinks, and primitive metadata only. |
| A Lightning adapter can accidentally register duplicate trainable modules. | high | Duplicate parameter registration or checkpoint keys would make optimization/checkpoint behavior confusing. | The adapter must register one parameter-bearing object for Lightning, shared with the method; do not separately register both a method and its nested model. |
| `TrainingResult` normalization from Lightning can overreach. | medium | Parsing full checkpoint files, logger internals, or callback-private state would couple RemotePhys to Lightning implementation details. | Record primitive summaries only: status, counts, monitored metric names/values, checkpoint metadata paths or identifiers when available, profiler summaries, callback names/statuses, and RemotePhys events. |
| JAX-style training may not fit object-mutating learner semantics. | medium | A future JAX engine may need explicit state input/output, PRNG keys, and functional gradient transforms. | Keep `TrainingEngine` provisional and avoid hard-coding torch scalar or module assumptions into the learner protocol; record JAX as a revisit trigger for functional learner extensions. |
| Real Lightning support would add optional dependency pressure. | medium | Core import tests and lightweight package policy could regress. | Stage 12 core should define the engine boundary and fake external-engine pressure tests; real Lightning support should live behind an optional adapter module or later optional phase. |
| Native engine feature scope can creep toward Lightning. | medium | RemotePhys could duplicate logging, checkpointing, early stopping, profiler, and distributed features. | Native engine remains reference-grade; advanced loop features are delegated to external engines or narrow backend descriptors only when required. |

Accepted design guardrails:

- `Trainer` is the public RemotePhys facade; it delegates to a selected
  `TrainingEngine`.
- `NativeTrainingEngine` is dependency-light and reference-grade.
- `LightningTrainingEngine` is a delegated-control adapter, not a wrapper around
  the native engine loop.
- `TrainingPlan` is not a framework config schema.
- `TrainingResult` records normalized summaries, not framework-private state.
- `Learner.step` remains the scientific contract used by all engines.
- External engines may own backward, optimizer, scheduler, logging,
  checkpointing, early stopping, profiling, precision, distributed strategy,
  and framework callback lifecycles.
- Core Stage 12 imports remain Lightning-, torch-, JAX-, logger-, and
  dataset-SDK-free unless a later optional adapter phase explicitly changes
  that boundary.

Validation implications:

- Add package/import tests proving core `rphys.training` does not import
  Lightning, torch, JAX, or logger packages.
- Add fake external-engine tests proving `Trainer(engine=fake_engine)` delegates
  control and does not run the native loop.
- Add native-engine tests proving `NativeTrainingEngine` still executes
  fit/validate/test/predict over already-built `Batch` iterables.
- Add result-normalization tests using fake logged metrics, checkpoint metadata,
  callback summaries, profiler summaries, and RemotePhys events.
- Add adapter-contract tests proving a trainable module is registered once and
  shared with the learner's method in Lightning-like examples.
- Add a future-roadmap test or documentation check that JAX/functional training
  pressure remains an explicit revisit trigger, not an implicit Stage 12
  promise.

## Source Evidence Refresh

Review date: 2026-05-16

| Source | Relevant evidence | Review use | Gap or blocker |
| --- | --- | --- | --- |
| `AGENTS.md` | `rphys` is a reusable library; core imports stay lightweight; public imports are intentional and tested; workflow artifacts record approvals and blockers; detailed workflow mechanics live under `.codex/`. | Baseline architecture and write-scope constraints. | None. |
| `.codex/prompts/roadmap-stage-design-proposer.md` | Requires proposed implementation shape, design decisions, agreement queue entries, classifications, future-roadmap interactions, adversarial assumptions, and approved-behavior traceability. | Current design proposal evidence pass. | None after this refresh; reviewer acceptance is still required. |
| `.codex/prompts/roadmap-stage-design-implication-reviewer.md` | Requires adversarial design review, reclassification of decisions, future-roadmap/reuse safety review, examples, audit traceability, and blockers for missing specialist evidence. | Current pass instructions. | None. |
| `.codex/templates/roadmap-stage-planning.md` | Names required planning sections, including design queue, decision triage, implication review, future-roadmap/reuse review, audit, examples, and gate evidence. | Section shape for this focused artifact. | The current Stage 12 artifact was not generated from the full template. |
| `docs/roadmap.md` Milestone 12 | Learner owns step semantics; Trainer owns loop mechanics; Lightning is optional; native and Lightning-backed execution share event/profiling records; no heavy framework dependencies in core. | Direct Stage 12 target. | Roadmap wording still says `Trainer` owns loop mechanics; the approved facade/engine design refines that to "selected engine owns loop control through Trainer." |
| `docs/roadmap.md` Milestone 15 | Training profiling must make overhead explicit; native and Lightning-backed execution share event schema; advanced profiling and data-path optimization are later work. | Future-roadmap pressure on events/profiles and result summaries. | Stage 12 should not overbuild Stage 15 profiling policy. |
| `docs/roadmap/stage-10/planning.md`; `src/rphys/methods/*` | Stage 10 records and current code define `Method`, patch-like `MethodOutput`, `apply_method_output`, backend-neutral `StateView`, and `ParameterView`. | Upstream method/trainable evidence for `SupervisedLearner`, `StepOutput.predictions`, and trainable-module registration pressure. | Stage 10 code exists in this worktree, but Stage 12 should still treat trainable state as descriptive and backend-neutral. |
| `docs/roadmap/stage-11/planning.md`; `src/rphys/losses/**`; `src/rphys/objectives/**`; `src/rphys/metrics/**` | Stage 11 plans and current code implement objective/metric contracts, raw backend-native objective values, detached metric values, and metric observation records. | Sequencing evidence for `SupervisedLearner`, objective scalar handling, and metric summaries. | Stage 12 should integrate against code-backed Stage 11 contracts where practical; fake scalar/backend objects remain useful for engine-specific tests. |
| `src/rphys/learning/__init__.py`; `src/rphys/training/__init__.py` | Package homes exist but expose no learning/training implementation. | Current implementation state. | No Stage 12 code-backed behavior or tests exist yet. |
| `tests/package/test_import_boundaries.py` | Core imports are checked against heavy optional modules including `torch`, `numpy`, `pandas`, `scipy`, and plotting/video stacks. | Validation obligation for import boundaries. | No Stage 12-specific training engine import tests exist yet. |
| Current `docs/roadmap/stage-12/planning.md` | Focused design narrative for `Learner`, `Trainer`, `TrainingEngine`, native execution, Lightning delegation, trainable-module sharing, result/event summaries, non-goals, and phase shape. | Primary design material reviewed. | Missing full source evidence, functionality agreement, design proposer handoff, design agreement queue, and validation/quality gates from the original template. |

## Specialist Evidence Status

| Evidence item | Status | Impact | Required action |
| --- | --- | --- | --- |
| Full Stage 12 context/functionality planning artifact | reconstructed and manager-reviewed, with FQ-12-9 resolved by deferral | Functional requirements and capability coverage are locked for FR-12-1 through FR-12-8. FR-12-9 is documentation/future-compatibility only. | Preserve FR-12-1 through FR-12-8; carry FR-12-9 only as a docs and future-roadmap note. |
| Functionality-agreement queue and behavior confirmation | passed | FQ-12-9 is resolved by maintainer clarification: document future batch-pipeline capability, do not implement it in Stage 12. | Carry locked behavior into validation planning with pipeline execution explicitly out of implementation scope. |
| Design proposer specialist evidence | complete in this pass | Public API, adapter, result-schema, event/profile, and helper-placement decisions now have independent implementation-shape evidence and FR traceability. | Run design implication/traceability review; no proposer-evidence blocker remains. |
| Stage 11 objective/metric implementation | present in this worktree | `SupervisedLearner` can use code-backed Stage 11 contracts for normal composition tests while retaining fake backend scalars for native/external engine pressure tests. | Validate against Stage 11 public contracts where practical and do not publish objective/loss/metric stand-ins from learning/training. |
| Stage 12 implementation evidence | absent by design | No code-backed names, import boundaries, or behavior tests exist yet. | Do not implement code in this pass; do not create implementation plan until prior gates are accepted. |

## Design Decisions

Design proposer note: public decisions below keep their maintainer-approved or
manager-accepted state where already locked, but the proposer classification
uses the required categories. `needs maintainer discussion` means the decision
has public API, adapter, dependency, schema, future-roadmap, or meaningful
refactor impact and requires maintainer judgment. DQ-12-1 through DQ-12-6
resolved those discussions; DQ-12-7 is resolved by maintainer clarification to
defer implementation and document future batch-pipeline compatibility.

| Decision ID | Classification | Related FRs | What and proposed shape | Why it matters | Options considered and recommendation | Trade-off or limitation | Validation/documentation obligation | Future-roadmap interaction and adversarial assumptions | Residual risk and escalation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DD-12-1 `Trainer` facade over `TrainingEngine` | needs maintainer discussion; resolved by DQ-12-1 | FR-12-5, FR-12-7 | `Trainer` is the RemotePhys user-facing facade and result-normalization point; selected engine owns loop control. | This public boundary controls native, fake external, future Lightning, future JAX, and downstream runtime reuse. | Recommended facade/engine split; rejected trainer-only loop, Lightning-as-canonical, and engine registry now. | Users may expect `Trainer` itself to run loops; docs and code must keep facade wording precise. | Contract tests for facade dispatch, external delegation, and no accidental native loop execution. | Future JAX may need functional state; downstream workflows need dispatch without `rphys` owning config; interface must allow extension without editing trainer internals. | Low after DQ approval; revisit if a second engine cannot fit mode-specific calls. |
| DD-12-2 mode-specific `TrainingEngine` protocol | needs maintainer discussion; resolved by DQ-12-1 | FR-12-5 | Provisional engine protocol exposes `fit/validate/test/predict(plan, learner) -> TrainingResult`. | Locks public adapter shape and keeps `learner` outside `TrainingPlan`. | Recommended mode-specific methods; rejected single opaque `run(mode=...)`, plan-containing-learner, and adapter-specific public methods. | External engines may later need a lower-level context/hook object. | Fake engine tests verify each mode method receives plan and learner; docs label protocol provisional. | Future Lightning/JAX/downstream engines can implement the protocol; revisit if second engine needs stateful streaming or compile-specific hooks. | Residual additive hook risk; no new maintainer question because DQ-12-1 locked the signature. |
| DD-12-3 `NativeTrainingEngine` as default reference loop | needs maintainer discussion; resolved by DQ-12-1 | FR-12-4, FR-12-5, FR-12-6 | Default engine iterates already-built batch sources, creates contexts, calls learner steps, invokes native descriptors, emits events/profiles, and returns results. | Provides executable semantics without framework dependencies. | Recommended reference-grade native engine; rejected Lightning clone, no native engine, and torch-specific native loop. | Native will remain intentionally less capable than Lightning or later external engines. | Native fit/validate/test/predict integration tests, train-only backward/optimizer checks, no datasource/dataloader construction. | Stage 15 may add profiling depth; future engines should reuse result/event vocabulary without inheriting native internals. | Feature creep risk; controlled by docs and validation. |
| DD-12-4 real Lightning deferred; delegated-control shape documented | needs maintainer discussion; resolved by DQ-12-6 | FR-12-5, FR-12-7, FR-12-8 | Stage 12 core validates fake external delegation only; real Lightning adapter is future optional work. | Avoids adding dependency/test/support burden before core contracts are proven. | Recommended fake external engine now; rejected real core Lightning adapter, native-loop wrapper, and no delegated-engine pressure test. | Users may expect runnable Lightning from examples; docs must label it future/optional. | Import-boundary tests and fake external mapping tests. | Future optional Lightning adapter maps hooks/events/results without forcing torch concepts into learners. | Real adapter may expose missing helper needs; revisit in optional adapter phase. |
| DD-12-5 neutral assembled-object `TrainingPlan` | needs maintainer discussion; resolved by DQ-12-2 | FR-12-6 | Plan carries caller-built batch sources, primitive loop limits, RemotePhys observers/profilers, optional native backend descriptors, metadata, and provenance. | Prevents training API from becoming workflow config or framework schema. | Recommended simple assembled objects; rejected `engine_config`, Hydra/project config, dataset paths, artifact dirs, and framework-specific fields. | Downstream wrappers must translate their own config into plans. | Unit tests for allowed fields, loop-limit validation, primitive metadata, and absent config/path/artifact behavior. | Loom/downstream projects persist and construct plans externally; future engines add fields only when proven. | Additive-field pressure remains; no generic escape hatch unless maintainer reopens. |
| DD-12-6 primitive `TrainingResult` summary | needs maintainer discussion; resolved by DQ-12-3 | FR-12-7, FR-12-8 | Result records status, mode, counts, failures, metric summaries, optional last-step/event/profile summaries, metadata/provenance, and minimal optional monitored metric/checkpoint identifiers. | Result is the handoff to evaluation, reports, downstream workflows, and external engines. | Recommended primitive summaries; rejected raw framework state, full checkpoint parsing, logger objects, durable artifact store, and report generation. | Some external-engine evidence will be unavailable or summary-only in Stage 12. | Unit/integration tests for completed/failed/stopped/partial runs, primitive summaries, missing external evidence, and no raw objects. | Stage 13 may consume result metrics; downstream persistence may add identifiers later. | Too-little-schema risk for real Lightning; revisit when real adapter exists. |
| DD-12-7 adapter-local single trainable owner registration | needs maintainer discussion; resolved by DQ-12-4 | FR-12-5, FR-12-7 | External adapters register exactly one parameter-bearing object shared with the method; no public core helper/protocol in Stage 12. | Prevents duplicate parameters, optimizer groups, and checkpoint keys. | Recommended explicit adapter argument; rejected core torch introspection, learner-owned module field, duplicate method+nested-module registration, and public provider protocol. | Fake tests cannot reveal all real framework registration edge cases. | Fake external adapter tests for shared identity, method-as-module, nested-module, duplicate rejection, unsupported pure-Python cases, and no torch imports. | Real Lightning may need adapter-local helpers later; Stage 10 `ParameterView` remains descriptive, not optimizer policy. | Revisit when real framework adapter proves a reusable helper is needed. |
| DD-12-8 framework-free Stage 12 core imports | recorded recommendation | FR-12-5, FR-12-8 | `rphys.learning` and `rphys.training` remain importable without Lightning, torch, JAX, logger, video, array, plotting, or dataset-SDK stacks. | Keeps base library lightweight and optional engines optional. | Recommended import boundary tests; rejected package-import-time optional framework imports. | Optional adapter modules must live outside core or import lazily later. | Package import-boundary tests covering learning/training submodules. | Future backend adapters can depend on frameworks at adapter edge; core protocols stay reusable. | Low risk; strong repo evidence, but dependency additions require review. |
| DD-12-9 `StepOutput.predictions` includes `MethodOutput` | needs maintainer discussion; resolved by DQ-12-5 | FR-12-2, FR-12-3 | Provisional union is `MethodOutput | Sample | Batch | None`; `SupervisedLearner` defaults to `MethodOutput`; trainers/engines treat predictions as opaque. | Preserves Stage 10 patch semantics and avoids premature materialization/export. | Recommended union with `MethodOutput`; rejected `Batch` only, arbitrary object, trainer materialization, and export in trainer. | Stage 13 may need a narrower prediction/evaluation handoff. | Tests for accepted prediction types, pass-through, no application/export by trainer, and Stage 13 revisit docs. | Stage 13 prediction/evaluation/reporting may pressure this shape; field-aware patch semantics remain available. | Revisit trigger: Stage 13 needs durable prediction rows or materialized samples. |
| DD-12-10 minimal `BackwardableScalar` plus backend override | needs maintainer discussion; resolved by DQ-12-5 | FR-12-2, FR-12-4, FR-12-5 | Native train mode uses a minimal `.backward()`-compatible scalar unless backend descriptor/engine owns backward; validate/test/predict never backward. | Gives native training executable semantics without requiring torch or excluding future JAX. | Recommended minimal scalar and override; rejected torch tensor protocol, no scalar contract, objective-as-metric, and JAX state in Stage 12 learner. | `.backward()` is object-oriented and not natural for all backends. | Tests for objective-required train failure, unsupported scalar, override path, no backward outside train, and Stage 11 raw handle integration. | Future JAX/functional engines own `value_and_grad`, PRNG, train state, and updates behind engine boundary. | Revisit if native functional backend is accepted. |
| DD-12-11 private validation/helper placement | auto-approved candidate | FR-12-1 through FR-12-8 | Use private helpers inside learning/training modules for coercion, summary validation, context construction, and native loop accumulation. Do not add pipeline output checks in Stage 12. | Reduces duplication without making public contracts. | Recommended private module-local helpers; rejected public utility package or broad base classes. | Helpers must remain private and tested through public behavior. | Public failure tests cover helper behavior; no public import docs. | Later stages can move/refactor helpers without downstream impact. | No maintainer escalation unless helpers become public. |
| DD-12-12 `LoopMode`, `LoopContext`, and structural `Learner` | recorded recommendation | FR-12-1 | Define mode values, primitive loop context, and structural `Learner.step(batch, context)`. | Establishes learning semantics independent of splits, workflows, and engines. | Recommended structural protocol and primitive context; rejected base-class requirement, registry, split-as-mode, and context carrying dataloaders/devices/checkpoints. | Context may need additive fields after real external engines. | Tests for mode values, mode/split distinction, primitive metadata/provenance, and forbidden responsibilities. | Future second dataset/model/modality can implement learner structurally; downstream extension works through importable objects. | Low after behavior agreement; revisit if engine adapters need non-primitive context state. |
| DD-12-13 `SupervisedLearner` only concrete learner | recorded recommendation | FR-12-3 | Implement one concrete learner that composes Stage 10 `Method`, optional Stage 11 `Objective`, and optional Stage 11 metrics into `StepOutput`. | Provides executable supervised flow without a premature learner catalog. | Recommended supervised only; rejected contrastive/self-supervised/masked/multitask classes, learner-owned optimizer, and training logic in methods. | Other learning styles remain patterns/tests until implementation pressure exists. | Synthetic integration tests for method/objective/metric composition, prediction-only mode, missing objective failure, and no input mutation. | Future modalities and learner families can add separate classes without editing trainer internals. | Revisit when a second concrete learner family is planned. |
| DD-12-14 event/profile observer vocabulary | recorded recommendation | FR-12-7, FR-12-8 | Define dependency-light events, observer sinks/callbacks, profiler/span summaries, unavailable probes, and overhead metadata. | Gives native and fake external engines comparable observability while deferring Stage 15 depth. | Recommended observe-only records; rejected logger-specific callbacks, callback loop control, hidden synchronization, and GPU/system profiler requirements. | Coarse Stage 12 spans may be insufficient for performance tuning. | Tests for event order, observer-only semantics, profile summaries, unavailable probes, overhead metadata, and fake external mapping. | Stage 15 can deepen profiling using the same vocabulary; real engines can map hooks later. | Revisit if Stage 15 needs incompatible timing semantics. |
| DD-12-15 experimental `run_train` as thin entrypoint | recorded recommendation | FR-12-5, FR-12-6, FR-12-7 | Provide experimental function-style delegation to assembled plan/trainer/learner; no workflow config or stable project schema. | Helps downstream wrappers call Stage 12 without making `rphys` a workflow runtime. | Recommended thin helper; rejected stable workflow API, config parser, artifact writer, and duplicate runner class. | Experimental status means downstream wrappers should not treat it as durable workflow schema. | Tests/docs prove it delegates to `Trainer` and returns `TrainingResult` without constructing dataloaders or artifacts. | Loom/downstream systems may wrap it later; `rphys` should not own orchestration. | Revisit if repeated downstream wrappers need a stable callable contract. |
| DD-12-16 optional post-prediction `BatchOperationPipeline` | needs maintainer discussion; resolved by DQ-12-7 deferral | FR-12-9 deferred | Do not implement learner-level `BatchOperationPipeline` execution in Stage 12. Document that future RemotePhys should be able to run batch pipelines over model outputs. | Keeps Stage 12 simple while preserving a useful extension path. | Recommended deferral; rejected Stage 12 `SupervisedLearner` pipeline argument, `PredictionPipelineSpec`, `train_pipeline`/`eval_pipeline`/`inference_pipeline`, trainer-owned routing, pipeline fields on `TrainingPlan`, and implicit sample uncollation. | Future callers needing different behavior per run can use downstream wrappers until a later public hook is approved. | Documentation and validation-planning obligation only: implementation phases must not add this hook now. | Stage 13 may later define prediction export/materialization adapters; Stage 15 may add profiling around pipeline time. | Revisit if repeated downstream use needs a stable post-model batch-pipeline hook. |

## Design Agreement Queue

| Queue ID | Related decision IDs | Depends on | Impact | What is being locked | Why it matters | Recommended answer | Trade-offs or rejected branches | Repo evidence or direct resolution | Exact feedback needed | State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DQ-12-1 | DD-12-1, DD-12-2, DD-12-3 | FR-12-5; FR-12-6 | high | `Trainer` as stable facade and `TrainingEngine` as provisional loop-control boundary. | This is public training API shape and affects native, Lightning, future JAX, and downstream engines. | Keep `Trainer` stable as facade; keep `TrainingEngine` provisional with mode-specific `fit/validate/test/predict(plan, learner)` methods; default engine is `NativeTrainingEngine`. | Rejected: make `Trainer` the only loop implementation; make Lightning canonical; expose a registry before symbolic engine names are a contract; put `learner` inside `TrainingPlan`; collapse all execution into `run(plan, mode)`. | Maintainer approved this shape on 2026-05-16. Design proposer confirms it is the implementation shape required by FR-12-5 and does not conflict with source evidence. | Resolved. Implement validation for facade dispatch, selected-engine delegation, native mode dispatch, and no accidental native loop execution when an external engine is selected. | locked |
| DQ-12-2 | DD-12-5 | DQ-12-1; FR-12-6 | high | `TrainingPlan` neutrality and initial field set. | If plan accepts framework config, it becomes a project/runtime schema and blocks future JAX/downstream reuse. | Keep plan simple and assembled-object oriented for Stage 12: caller-supplied batch iterables/loaders, primitive loop limits, RemotePhys sinks/callbacks/profilers, optional native backend descriptors, primitive metadata/provenance; engine-specific config belongs on engine objects and future fields are additive only when needed. | Rejected: raw project config, Hydra schema, dataset paths, artifact directories, Lightning trainer/callback/logger fields, JAX compile policy fields, generic `engine_config` escape hatch. | Maintainer approved this shape on 2026-05-16 and explicitly preferred simple now, expand as needed. Design proposer maps it to FR-12-6 and downstream workflow separation. | Resolved. Validate accepted fields, absence of `engine_config`, no datasource/artifact/config parsing, and engine-specific config kept on engine/adapter objects. | locked |
| DQ-12-3 | DD-12-6 | DQ-12-1; FR-12-7; FR-12-8 | high | `TrainingResult` normalized summary shape. | Result schema is the durable handoff to evaluation, reports, downstream workflow tools, and optional engines. | Keep result simple, summary-oriented, and primitive for Stage 12: status, mode, counts, failures, metric summaries, optional last-step summary, event/profile summaries, metadata/provenance. External-engine evidence remains optional and minimal, limited to primitive monitored metric names/values and checkpoint identifiers when already available; callback/profiler details are additive later if needed. Do not parse framework-private state. | Rejected: logger-specific objects, raw callback objects, full checkpoint parsing, report generation, durable artifact store, required external-engine summaries, broad callback/profiler schemas now. | Maintainer approved this primitive summary-oriented shape on 2026-05-16 and reiterated to keep it simple for now. Design proposer maps it to FR-12-7 and FR-12-8 result/observability handoff. | Resolved. Validate primitive fields, minimal optional engine evidence, missing/partial summaries, failed/stopped runs, no raw framework objects, and no artifact-store behavior. | locked |
| DQ-12-4 | DD-12-7 | DQ-12-1; FR-12-5; FR-12-7 | high | External-engine trainable-module registration contract. | Duplicate parameter registration can corrupt optimization/checkpoint behavior; overusing Stage 10 `ParameterView` could leak backend policy into core. | For external-engine adapters, require one explicit adapter-local parameter owner shared with the method; register exactly one object; keep detection/failure behavior in the adapter; do not add a public trainable-module provider protocol in Stage 12. | Rejected: duplicate registration of method plus nested module; core introspection of torch modules; forcing `SupervisedLearner` to expose framework-specific module fields; adapter recreating learner semantics; auto-introspection in core. | Maintainer approved explicit adapter-local registration on 2026-05-16. Design proposer confirms adapter-local ownership is consistent with Stage 10 descriptive `ParameterView`. | Resolved. Validate one-registration guardrail with fake external-engine tests, shared object identity, duplicate rejection, method-as-module/nested-module cases, and no core torch/Lightning imports. | locked |
| DQ-12-5 | DD-12-9, DD-12-10 | FR-12-2; FR-12-3; FR-12-4; Stage 10 and Stage 11 contracts | high | `StepOutput.predictions` and objective scalar/backward boundary. | These fields bridge methods/objectives with every engine; mistakes here are expensive public API churn. | Allow `MethodOutput | Sample | Batch | None` provisionally for predictions; `SupervisedLearner` returns `MethodOutput` by default; predictions remain trainer/engine-opaque; define `BackwardableScalar` as the minimal train-mode objective surface for native execution while allowing backend engines/adapters to override backward. | Rejected: forcing predictions to `Batch` only; treating objective as a named metric; requiring torch tensor protocol in core; requiring JAX functional state in Stage 12 learner; engines materializing/exporting predictions. | Maintainer approved this union and scalar/backward boundary on 2026-05-16. Design proposer confirms current Stage 10/11 code supports pass-through predictions and raw objective handles. | Resolved. Validate `MethodOutput` pass-through, accepted `Sample`/`Batch`/`None`, no trainer materialization/export, train objective-required failure, validate/test/predict no backward, unsupported scalar error, backend override path, and Stage 11 contract integration with fake backend scalars where useful. | locked |
| DQ-12-6 | DD-12-4, DD-12-8 | DQ-12-1; FR-12-5; FR-12-7; FR-12-8 | medium | Optional external engine import boundary and Stage 12 scope. | Real Lightning support would add dependency, package, test, and public API pressure. | Stage 12 core defines engine boundary, native engine, result/event vocabulary, and fake external-engine pressure tests. Real Lightning implementation is deferred to a later optional adapter phase or stage. | Rejected: importing Lightning in core; wrapping native loop with Lightning; implementing Lightning-sized logging/checkpoint/early-stop features in native engine; adding real optional Lightning adapter code before core contracts are proven. | Maintainer approved deferring real Lightning implementation on 2026-05-16. Design proposer confirms fake external-engine validation satisfies Stage 12 without weakening import boundaries. | Resolved. Validate core import boundaries, fake external-engine delegation, docs/examples that mark Lightning as optional/future, and no Lightning/torch/JAX/logger imports in Stage 12 core. | locked |
| DQ-12-7 | DD-12-16 | FQ-12-9; FR-12-9 | high | Optional differentiable post-prediction operation pipeline shape. | Prediction/output processing can affect losses, metrics, and inference semantics; adding a premature mode-specific spec would be expensive public API churn. | Defer implementation in Stage 12. Document the desired future ability to run `BatchOperationPipeline` over model outputs, and keep predictions trainer-opaque so later composition remains possible. | Rejected for Stage 12: `SupervisedLearner` pipeline argument, `PredictionPipelineSpec`, `train_pipeline`/`eval_pipeline`/`inference_pipeline`, trainer-applied prediction patches, pipeline objects in `TrainingPlan`, hidden detach/no-grad, and automatic sample-to-batch adapters. | Existing Stage 7 operation pipelines and Stage 10/11 contracts support future feasibility. Maintainer clarified implementation is not needed now. | Resolved. Validation planner should include docs/future-compatibility coverage and exclude implementation tests for pipeline execution. | deferred / documented |

## Design Decision Triage

| Decision ID | Proposer classification | Current approval state | Why this classification | Traceability | Future/adversarial pressure | Required follow-up | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DD-12-1 `Trainer` facade over `TrainingEngine` | needs maintainer discussion | DQ-12-1 locked | Public facade/engine API with future-engine impact. | FR-12-5, FR-12-7; DQ-12-1 | Lightning/JAX/downstream engines must compose without trainer internals. | Validate facade dispatch and keep wording facade-oriented. | locked |
| DD-12-2 mode-specific `TrainingEngine` protocol | needs maintainer discussion | DQ-12-1 locked | Public protocol signature and adapter reuse shape. | FR-12-5; DQ-12-1 | Second engine may need additive hooks or context. | Validate `fit/validate/test/predict(plan, learner)` delegation. | locked |
| DD-12-3 `NativeTrainingEngine` default reference loop | needs maintainer discussion | DQ-12-1 locked | Public default engine and native mechanics boundary. | FR-12-4, FR-12-5, FR-12-6; DQ-12-1 | Stage 15 profiling and external engines must not inherit native internals. | Validate reference-grade scope and no Lightning-sized features. | locked |
| DD-12-4 real Lightning deferred, delegated-control shape | needs maintainer discussion | DQ-12-6 locked | Dependency, package, test, and user-expectation impact. | FR-12-5, FR-12-7, FR-12-8; DQ-12-6 | Future Lightning adapter must map hooks/results without core imports. | Validate fake external delegation and docs deferral. | locked |
| DD-12-5 neutral assembled-object `TrainingPlan` | needs maintainer discussion | DQ-12-2 locked | Public schema can become workflow config if too broad. | FR-12-6; DQ-12-2 | Downstream wrappers translate their own config; future fields are additive. | Validate no `engine_config`, paths, artifact dirs, or project config. | locked |
| DD-12-6 primitive `TrainingResult` summary | needs maintainer discussion | DQ-12-3 locked | Public result handoff to evaluation/reporting/downstream systems. | FR-12-7, FR-12-8; DQ-12-3 | Stage 13 and real adapters may need additive evidence fields. | Validate primitive summaries and no framework-private objects. | locked |
| DD-12-7 adapter-local single trainable owner registration | needs maintainer discussion | DQ-12-4 locked | External-engine adapter correctness and backend-policy boundary. | FR-12-5, FR-12-7; DQ-12-4 | Real frameworks may need adapter-local helpers later. | Validate shared object identity and duplicate rejection with fakes. | locked |
| DD-12-8 framework-free Stage 12 imports | recorded recommendation | DQ-12-6 locked as scope guardrail | Strong repo policy and package tests make the default clear; not auto-approved because dependency posture is material. | FR-12-5, FR-12-8; DQ-12-6 | Optional adapters stay outside core or lazy-imported in future. | Add Stage 12 import-boundary tests. | locked guardrail |
| DD-12-9 `StepOutput.predictions` includes `MethodOutput` | needs maintainer discussion | DQ-12-5 locked | Public step-output schema and Stage 13 prediction compatibility. | FR-12-2, FR-12-3; DQ-12-5 | Stage 13 may narrow or adapt prediction handoff. | Validate pass-through, accepted union, and no materialization/export. | locked |
| DD-12-10 minimal `BackwardableScalar` plus backend override | needs maintainer discussion | DQ-12-5 locked | Public/native train semantics and future backend compatibility. | FR-12-2, FR-12-4, FR-12-5; DQ-12-5 | Future JAX/functional engines pressure `.backward()` assumptions. | Validate train objective failure, unsupported scalar, and override path. | locked |
| DD-12-11 private validation/helper placement | auto-approved candidate | upheld by design proposer | Private, local, refactorable, and no public import/schema/scientific/dependency impact. | FR-12-1 through FR-12-8 implementation support | Helpers may be refactored later without downstream impact. | Test only through public behavior; escalate if made public. | auto-approved candidate |
| DD-12-12 `LoopMode`, `LoopContext`, structural `Learner` | recorded recommendation | behavior locked by FR-12-1 | Direct roadmap behavior with low ambiguity after functionality agreement; public but evidence-backed. | FR-12-1 | Second datasets/models/modalities should implement structurally without registries. | Validate mode/split distinction and forbidden responsibilities. | recorded |
| DD-12-13 `SupervisedLearner` only concrete learner | recorded recommendation | behavior locked by FR-12-3 | Direct roadmap behavior; avoids premature learner catalog. | FR-12-3 | Future learner families should be additive and trainer-independent. | Validate Stage 10/11 composition and prediction-only mode. | recorded |
| DD-12-14 event/profile observer vocabulary | recorded recommendation | behavior locked by FR-12-8 | Direct roadmap behavior; Stage 15 depth remains deferred. | FR-12-7, FR-12-8 | Stage 15 and external engines may extend vocabulary. | Validate observer-only callbacks, events, profiles, unavailable probes. | recorded |
| DD-12-15 experimental `run_train` thin entrypoint | recorded recommendation | behavior locked by FR-12-5 | Direct roadmap behavior; experimental label avoids workflow API lock-in. | FR-12-5, FR-12-6, FR-12-7 | Downstream wrappers may later request a stable callable. | Validate delegation-only behavior and no config/artifact ownership. | recorded |
| DD-12-16 optional post-prediction `BatchOperationPipeline` | needs maintainer discussion | DQ-12-7 deferred/documented | Public learner constructor/behavior, prediction semantics, and objective/metric input semantics; maintainer chose documentation-only future compatibility for Stage 12. | FR-12-9 deferred; DQ-12-7 | Stage 13 export/eval and repeated downstream routing patterns may later require adapters or specs. | Validation planner should ensure implementation phases do not include pipeline execution and docs mention the future ability. | deferred / documented |

Auto-approval review result: DD-12-11 is the only auto-approved candidate
because it is private/internal, local, refactorable, traceable to approved
behavior, straightforward to validate through public failures, and has no public
API, import-path, schema, config, scientific-workflow, dependency,
serialization, persistence, future-roadmap, interface-reuse, compatibility, or
meaningful future-refactor impact. Every public API, adapter, protocol, schema,
dependency, or future-backend decision is classified as a recorded
recommendation or a decision that needed maintainer discussion. DQ-12-1 through
DQ-12-6 are already resolved by locked DQ packets; DQ-12-7 is resolved as a
deferral/documentation-only decision.

### Design Packets Requiring Maintainer Discussion

| Packet | Ambiguity | Options | Recommendation | Impact | Validation obligation | Residual risk | Exact feedback needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DQ-12-1 engine protocol shape | The approved architecture needs a public `TrainingEngine` boundary, but the exact method signatures and whether `learner` is passed separately from `plan` were not locked by specialist evidence. | Mode-specific methods; single `run(plan, mode)`; plan contains learner; adapter-specific public methods. | Use mode-specific `fit/validate/test/predict(plan, learner)` provisionally and keep `Trainer.run(...)` as thin dispatch. | Freezes extension shape for native, fake external, Lightning, and future JAX engines. | Contract tests for fake engine delegation, native mode dispatch, no accidental native loop execution when external engine is selected. | External engines may later need an additive lower-level hook or context object. | Resolved 2026-05-16: maintainer approved mode-specific protocol and learner/plan argument split. |
| DQ-12-2 `TrainingPlan` public fields | The current narrative rejected engine config but did not lock initial plan fields. | Minimal loop inputs and limits; richer native backend descriptors; generic metadata plus `engine_config`; framework-specific fields. | Keep assembled batch iterables/loaders, primitive loop limits, RemotePhys sinks/callbacks/profilers, optional native backend descriptors, and primitive metadata/provenance. No `engine_config`; expand additively only when needed. | Prevents `TrainingPlan` from becoming workflow config or framework schema. | Unit tests for accepted fields, primitive metadata, no dataset path/artifact/config parsing, and engine-specific config rejection or absence. | Downstream wrappers may need their own config translation layer. | Resolved 2026-05-16: maintainer approved simple assembled-object plan now, additive expansion later, and no generic engine config escape hatch. |
| DQ-12-3 `TrainingResult` normalization | The narrative listed candidate result content but not a precise public schema. | Primitive summary only; include structured checkpoint/log/profile summaries; expose raw framework state; defer external summaries. | Use primitive RemotePhys summaries plus minimal optional engine evidence records for monitored metric names/values and checkpoint identifiers when already available; never expose framework-private objects. | Affects Stage 13 evaluation/reporting and downstream workflow persistence. | Tests with fake native and fake external summaries, missing values, failed runs, partial epochs, minimal checkpoint metadata, and serialization-safe primitive metadata. | A real Lightning adapter may need extra optional callback/profiler fields later. | Resolved 2026-05-16: maintainer approved summary-oriented primitive fields, minimal optional external-engine evidence, and simple-now/additive-later posture. |
| DQ-12-4 trainable-module registration | The design said register one parameter-bearing object, but not whether core provides a helper/protocol. | Explicit adapter argument; derive from Stage 10 `TrainableMethod.parameters`; method-owned module provider protocol; leave adapter-local. | Require explicit adapter-local parameter owner for external engines; fake tests prove one registration and shared object identity; defer public helper until real adapter implementation proves the need. | Avoids duplicate parameters and checkpoint confusion without making core torch-aware. | Fake Lightning-like adapter tests for same object, duplicate rejection, method-as-module, nested-module, and pure-Python method failure/unsupported cases. | Real frameworks may need more introspection than fake tests reveal. | Resolved 2026-05-16: maintainer approved explicit adapter-local registration and no public helper/protocol in Stage 12. |
| DQ-12-5 `StepOutput` prediction and scalar contract | Stage 10 code supports patch-like `MethodOutput`, while roadmap text lists `Sample | Batch | None`; Stage 11 scalar/value records are backend-native and intentionally loose. | Prediction union includes `MethodOutput`; force application to `Batch`; prediction remains opaque object; define `.backward` protocol; delegate all backward to backend adapter. | Use `MethodOutput | Sample | Batch | None` provisionally and a minimal `BackwardableScalar` for native `.backward()` only, with backend adapters allowed to override. | Affects learners, native backward, Lightning automatic optimization, prediction/evaluation handoff, and future JAX. | Tests for train objective required, validate/test/predict no backward, `MethodOutput` pass-through, unsupported scalar error, backend override, and no prediction materialization by trainer. | Stage 13 may require adapters from `MethodOutput` into evaluation/export fields. | Resolved 2026-05-16: maintainer approved provisional prediction union and minimal native backward contract with backend override path. |
| DQ-12-6 real Lightning implementation timing | The narrative names `LightningTrainingEngine`, but also says real support can live in a later optional adapter phase. | Stage 12 fake external only; Stage 12 import-gated optional Lightning adapter; later dedicated Lightning stage. | Stage 12 should implement only fake external pressure tests and keep real Lightning deferred. | Controls dependency, test, public API, and support burden. | Import-boundary tests and fake external tests now; real Lightning acceptance tests only when a later optional adapter phase is approved. | Users may expect Lightning code from the design examples. | Resolved 2026-05-16: maintainer approved deferring real Lightning implementation; Stage 12 core validates the boundary with fake external engine tests and docs/examples. |
| DQ-12-7 post-prediction pipeline shape | The design proposer introduced reusable post-model processing during training/eval/inference; maintainer clarified Stage 12 should document the desired ability but not implement the hook now. | Learner-level `BatchOperationPipeline`; mode-specific `PredictionPipelineSpec`; trainer-owned pipeline routing; pipeline objects in `TrainingPlan`; hidden sample uncollation; defer to Stage 13/downstream wrappers. | Defer implementation and document future compatibility. Do not add a Stage 12 `SupervisedLearner` pipeline argument. | Affects learner semantics, objective/metric inputs, prediction opacity, Stage 13 export/evaluation pressure, and future mode-routing API. | Docs/review checks only: validation planner must ensure no implementation phase assumes pipeline execution. | A future repeated train/eval/inference routing pattern may justify an additive public spec. | Resolved 2026-05-16: maintainer chose documentation-only future compatibility for Stage 12. |

## Design Implication Review

| Finding | Affected decision or requirement | Maintainability/extensibility impact | Recommended revision | Queue action | Status |
| --- | --- | --- | --- | --- | --- |
| The facade/engine split is the right long-term shape, but `Trainer` wording must stay consistently facade-oriented. | DD-12-1, DD-12-2 | If docs or code say `Trainer` owns loop mechanics directly, Lightning and JAX adapters become exceptions instead of first-class engines. | Revise future implementation docs so `Trainer` owns user-facing dispatch/result normalization while the selected `TrainingEngine` owns loop control. | DQ-12-1 discussion | recorded concern |
| `TrainingPlan` is the most likely accidental coupling point. | DD-12-5 | Framework config, dataset paths, artifact directories, or Hydra-like schemas would turn Stage 12 into workflow runtime infrastructure. | Locked simple neutral assembled-object fields and keep engine-specific config on engine/adapter objects; expand additively only when needed. | DQ-12-2 locked | resolved |
| `TrainingResult` normalization needs a public-schema decision before implementation. | DD-12-6 | Too much schema couples to framework internals; too little schema prevents downstream evaluation/reporting from consuming training evidence. | Locked simple primitive result records for status, mode, counts, failures, metrics, optional last-step summary, event/profile summaries, metadata/provenance, and minimal optional engine evidence. | DQ-12-3 locked | resolved |
| Duplicate trainable-module registration is a real delegated-engine failure mode. | DD-12-7 | Registering both a method and nested model can duplicate parameters, optimizer groups, or checkpoint keys. | Keep learner plain; require one explicit adapter-local registration point; validate with fake external adapter examples before real Lightning. | DQ-12-4 locked | resolved |
| Native engine should remain reference-grade. | DD-12-3 | Adding logging, checkpointing, early stopping, profiler, precision, and distributed replicas to native duplicates Lightning and Stage 15 work. | Native owns only dependency-light iteration, context creation, backward/optimizer hooks, events/profiles, and result summaries. | no queue reopen | recorded recommendation |
| The prediction union is compatible with Stage 10 code but conflicts with the roadmap shorthand. | DD-12-9 | If Stage 12 omits `MethodOutput`, `SupervisedLearner` must materialize predictions too early; if it accepts arbitrary prediction objects, Stage 13 loses traceability. | Locked `MethodOutput | Sample | Batch | None` as provisional; `MethodOutput` is the `SupervisedLearner` default; revisit in Stage 13 if needed. | DQ-12-5 locked | resolved |
| Backward semantics cannot assume torch while still supporting native `.backward()`. | DD-12-10 | A torch-shaped scalar contract makes JAX awkward; no scalar contract makes native training under-specified. | Locked minimal native `BackwardableScalar` plus backend override path and train-mode failure behavior. | DQ-12-5 locked | resolved |
| Post-prediction pipelines are plausible but deferred from Stage 12. | DD-12-16, FR-12-9 | If trainers or plans own prediction pipeline routing now, Stage 12 becomes a prediction/evaluation workflow layer and future mode-specific specs are prematurely locked. Even learner-local composition changes public `SupervisedLearner` behavior and objective/metric inputs. | Resolve by deferral: document the future ability to run `BatchOperationPipeline` over model outputs, but do not add a learner hook, trainer routing, or mode-specific prediction spec in Stage 12. | DQ-12-7 deferred/documented | resolved |
| Import boundaries have strong repo evidence. | DD-12-8 | Heavy imports in core would violate existing package tests and make optional engines mandatory. | Add Stage 12 import-boundary tests for `rphys.learning`, `rphys.training`, and submodules. | no queue reopen | recorded recommendation |
| Design proposer specialist evidence is present, with FR-12-9/DD-12-16 now scoped to deferral. | all public decisions; DD-12-16 | The implementation-shape proposal and FR-to-DD mapping exist; the added pipeline behavior is accepted only as future documentation, not implementation. | Preserve DQ-12-1 through DQ-12-6 and record DQ-12-7 as deferred/documented. | DQ-12-7 deferred/documented | resolved |

## Future Roadmap And Reuse Safety Review

| Finding | Affected decision or requirement | Future roadmap item or dependency | Interface/adapter/protocol implication | Recommended revision or deferral | Revisit trigger | Queue action | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Future JAX training pressures object-mutating and `.backward()` assumptions. | DD-12-1, DD-12-2, DD-12-10 | Future `JaxTrainingEngine`; Stage 15 compile/precision policy. | Keep engine provisional and allow adapters to own functional train state, PRNG keys, `value_and_grad`, and update mechanics. | Do not widen `Learner.step` in Stage 12 solely for JAX; record functional learner extension as future work. | A JAX prototype cannot call `Learner.step` without hidden state mutation or scalar adaptation. | DQ-12-1, DQ-12-5 | recorded concern |
| Stage 13 needs prediction outputs that remain field-aware. | DD-12-9 | Stage 13 prediction/evaluation/analysis/report helpers. | `MethodOutput` pass-through preserves patch semantics; trainers should not materialize or export predictions. | Prediction union locked as provisional; revisit in Stage 13 if first-class prediction export/materialization or report rows need a narrower contract. | Stage 13 requires first-class prediction export/materialization or report rows. | DQ-12-5 locked | resolved with revisit trigger |
| Stage 13 and downstream inference may pressure post-prediction pipeline routing. | DD-12-16, FR-12-9 | Stage 13 prediction/export/evaluation; downstream train/eval/inference wrappers. | Existing `BatchOperationPipeline` could preserve field-aware composition without adding a stable routing spec, but putting it into `SupervisedLearner` now is a public learner decision. | Defer learner-local pipeline composition, mode-specific `PredictionPipelineSpec`, and sample-pipeline adapters from Stage 12. Document the future ability to run batch pipelines over model outputs. | Multiple downstream projects need separate train/eval/inference pipeline routing, or a later stage accepts a stable post-model batch-pipeline hook. | DQ-12-7 deferred/documented | resolved with revisit trigger |
| Stage 15 profiling should build on Stage 12 event/profile vocabulary, not be implemented early. | DD-12-3, DD-12-4, DD-12-6 | Milestone 15 profiling and data-path optimization. | Stage 12 event/profile records should be generic and cheap; deep profiler integrations remain optional later adapters. | Keep Stage 12 spans to native/fake boundaries and explicit unavailable probes. | Profiling tests need GPU/system/operator timelines or synchronized timing policy. | DQ-12-3, DQ-12-6 | recorded recommendation |
| Downstream workflow systems need result summaries, not rphys-owned artifact stores. | DD-12-5, DD-12-6 | Loom/downstream project orchestration; Stage 13 reports. | `TrainingPlan` stays simple and assembled-object oriented; `TrainingResult` can be persisted by downstream tools, but rphys should not own storage, run directories, or config schemas. | Keep plans/results primitive and serializable where practical; no artifact-store API. | Downstream persistence may later need additive identifiers beyond primitive metadata. | DQ-12-2 and DQ-12-3 locked | resolved |
| Lightning delegation must not force torch concepts into core methods or learners. | DD-12-4, DD-12-7, DD-12-8 | Optional Lightning adapter; future backend adapters. | Trainable parameter ownership stays adapter-local; core uses backend-neutral Stage 10 trainable records only for description. | Real Lightning implementation deferred; Stage 12 core stays framework-free and validates fake external-engine delegation. | Real adapter needs torch-specific lifecycle code, module registration helpers, or checkpoint mapping. | DQ-12-6 locked | resolved |
| Stage 11 contracts should be used without moving objective/metric behavior into Stage 12. | DD-12-10 | Stage 11 losses/objectives/metrics; Stage 12 `SupervisedLearner`; Stage 13 metric analysis. | Integrate against public Stage 11 contracts where practical; keep fake backend scalars/test helpers local; do not publish objective/metric stand-ins from learning/training. | Keep Stage 11 integration guardrail in phase plan. | Stage 11 public contracts change incompatibly or native scalar/backward validation needs stricter typing. | DQ-12-5 locked with sequencing guardrail | recorded implementation dependency |

## Functionality And Decision Audit

| Audit item | Impact | Resolution | Status |
| --- | --- | --- | --- |
| Capability-to-requirement traceability | The focused artifact previously lacked functional requirement IDs and a functionality-agreement queue. | Reconstructed Capability Triage, Module Behavior Map, Functionality Agreement Queue, Functional Requirements, and Behavior Confirmation; FQ-12-1 through FQ-12-8 are implementation scope and FQ-12-9 is deferred/documented. | passed |
| Requirement-to-design traceability | Design decisions needed to be checked against reconstructed FR IDs. | Design proposer refresh added Proposed Implementation Shape, DD-12-1 through DD-12-16, FR mappings, DQ mappings, future-roadmap assumptions, adversarial assumptions, and validation obligations. DD-12-16 now traces to deferred FR-12-9/DQ-12-7. | passed |
| Auto-approved decision traceability | No prior auto-approved candidates were recorded; public decisions cannot be auto-approved. | Only private helper placement is auto-approved after adversarial review. | reviewed |
| TrainingPlan neutrality | Narrative and roadmap agree on no workflow runtime; maintainer approved simple assembled-object fields with no `engine_config`. | DQ-12-2 locked; implementation plan must carry field and non-config validation. | resolved |
| TrainingResult normalization | Maintainer approved simple primitive summary-oriented result records with minimal optional external-engine evidence and no framework-private state. | DQ-12-3 locked; implementation plan must carry result-schema and non-artifact validation. | resolved |
| Duplicate trainable registration | Maintainer approved explicit adapter-local parameter owner registration with no Stage 12 public helper/protocol. | DQ-12-4 locked; implementation plan must carry fake external-engine validation. | resolved |
| Post-prediction pipeline reuse | Existing operation contracts make learner-level composition feasible, but adding it to `SupervisedLearner` is high-impact public behavior. | Maintainer chose to defer implementation and document future ability to run batch pipelines over model outputs. Implementation plan must not include learner-level pipeline execution. | resolved |
| Import boundaries | Roadmap and package tests provide strong evidence. | Record import-boundary tests as mandatory Stage 12 validation. | recorded recommendation |
| Stage 11 dependency | Current code has objective/metric contracts. | Stage 12 should use public Stage 11 contracts where practical and keep fakes test-local for engine/backward pressure; it must not publish stand-ins. | recorded implementation dependency |
| Public API surface | `Trainer`, `TrainingEngine`, `TrainingPlan`, `TrainingResult`, `StepOutput`, and scalar/prediction shapes are all public-contract decisions. | Reclassified as recorded recommendation or needs maintainer discussion, not auto-approved. | reviewed |
| Examples and validation coverage | Current examples demonstrate intent and key risk cases and now map to validation needs. | Required examples are mapped to tests/docs in `Examples And Demonstrations` and `Validation Strategy`; implementation planning must carry them into phase acceptance criteria. | passed |

Capability traceability finding: every included Stage 12 capability now has at
least one locked requirement and related design/example coverage. The
post-prediction pipeline item is traceable as a deferred future-compatibility
note, not as implementation scope.

## Examples And Demonstrations

| Example | Behavior demonstrated | Project context | Required docs/tests | Status |
| --- | --- | --- | --- | --- |
| Native supervised smoke run | `Trainer(engine=NativeTrainingEngine()).fit(...)` delegates to native loop, creates `LoopContext`, calls `SupervisedLearner.step`, uses only `StepOutput.objective` for backward, and returns `TrainingResult`. | Synthetic `Batch` iterable, Stage 10 method output, Stage 11 objective/metric contracts, and fake backend scalar/optimizer mechanics as needed. | Learning/training docs; contract and integration tests for fit/validate/test/predict, objective-required train failure, no optimizer step outside train. | required |
| Fake external engine delegation | `Trainer(engine=fake_engine).run(...)` calls the selected engine and never enters native loop. | Fake Lightning-like engine with no external dependencies. | Contract tests proving delegation, result normalization, events, and no native-loop side effects. | required |
| Lightning-like automatic optimization sketch | Adapter hook calls `Learner.step`, returns objective to framework, logs selected metrics, and leaves backward/optimizer/checkpointing to external engine. | Documentation-only or fake adapter; real Lightning deferred unless approved. | Docs and fake tests for hook-to-context mapping and log-name normalization; import-boundary test forbids Lightning in core. | required if real adapter deferred |
| Duplicate trainable-module guardrail | Adapter registers one trainable object shared with method; duplicate method+nested-module registration fails or is unsupported. | Torch-like fake module and method object; no torch import required. | Contract tests for same object identity, method-as-module, nested-module, duplicate rejection, unsupported pure Python method. | required |
| `TrainingPlan` neutrality | Plan accepts assembled batch iterables/loaders and loop limits but not project config, dataset paths, artifact directories, or engine config. | Downstream workflow wrapper constructs plan from its own config. | Unit tests for field validation and docs showing workflow config outside rphys. | required |
| `TrainingResult` external summary | Fake external engine returns primitive metric, checkpoint, callback, profiler, event, and failure summaries normalized into RemotePhys result records. | Lightning-like execution evidence without framework-private objects. | Unit tests for missing/partial summaries, failed run, primitive metadata, and no raw logger/checkpoint object exposure. | required |
| Prediction pass-through | `SupervisedLearner` returns Stage 10 `MethodOutput` in `StepOutput.predictions`; trainer records/summarizes without applying/exporting it. | Stage 10 synthetic method output; Stage 13 later consumes predictions. | Contract tests for `MethodOutput | Sample | Batch | None`; docs explaining no trainer materialization and Stage 13 revisit trigger. | required |
| Future post-prediction batch pipeline | Documentation explains that future RemotePhys should be able to run `BatchOperationPipeline` over model outputs, while Stage 12 keeps predictions trainer-opaque and does not implement the hook. | Existing operation pipeline components, Stage 10 method output, Stage 11 objective/metric contracts. | Docs/review checks only; no Stage 12 implementation tests for pipeline execution. | deferred/documented |
| JAX pressure example | Fake functional engine shows why train state, PRNG, and `value_and_grad` stay engine/adapter concerns. | Future-backend design note, not implementation. | Docs-only revisit trigger or fake protocol test that no torch scalar/module assumption is required in core. | required |

## Design Gate Status

Design approval passed after DQ-12-7 was resolved by deferring implementation
and documenting future post-prediction batch-pipeline compatibility.

Gate findings:

- The full Stage 12 context/functionality scaffold has been reconstructed and
  functionality agreement plus behavior confirmation have passed.
- Design proposer evidence is present and accepted after scoping
  FQ-12-9/DQ-12-7/DD-12-16 to documentation-only future compatibility.
- Public-contract packets DQ-12-1 through DQ-12-6 are resolved and locked.
  DQ-12-7 is resolved as deferred/documented.
- Stage 12 implementation evidence is absent by design; no code, tests, or
  implementation plan have been created.
- Existing operation pipeline contracts prove future feasibility, not Stage 12
  implementation scope.

Accepted direction:

- `Trainer` remains the stable RemotePhys facade.
- `TrainingEngine` owns loop control behind that facade.
- `NativeTrainingEngine` is the lightweight reference loop.
- Lightning-style execution is delegated-control and optional.
- Future JAX or other engines remain possible because backend mechanics and
  framework policy stay behind engine/adapter boundaries.
- Future post-model batch-pipeline composition remains documented, but Stage
  12 does not implement learner-level pipeline execution.

## End-To-End Example

```python
method = PulseMethod(...)
objective = PulseObjective(...)
metric = HeartRateMAE(...)

learner = SupervisedLearner(
    method=method,
    objective=objective,
    metrics=[metric],
)

trainer = Trainer(engine=NativeTrainingEngine())

result = trainer.fit(
    learner=learner,
    train_batches=train_batches,
    validate_batches=validate_batches,
)
```

Execution connects as:

```text
Batch iterable
  -> Trainer dispatches to NativeTrainingEngine
  -> NativeTrainingEngine creates LoopContext
  -> SupervisedLearner calls Method.predict
  -> SupervisedLearner applies MethodOutput only as needed for objectives/metrics
  -> SupervisedLearner evaluates Objective and Metrics when available
  -> SupervisedLearner returns StepOutput
  -> NativeTrainingEngine uses only StepOutput.objective for backward
  -> NativeTrainingEngine emits TrainingEvent/ProfileSpan records
  -> Trainer returns TrainingResult
```

## Explicit Non-Goals

Stage 12 should not implement:

- datasource scanning;
- dataloader construction;
- `SampleBuilder`;
- config parsing or workflow runtime behavior;
- raw artifact stores or checkpoint file writers;
- prediction export/materialization;
- learner-level post-prediction `BatchOperationPipeline` execution;
- mode-specific prediction pipeline specs or trainer-owned prediction routers;
- implicit `SampleOperationPipeline` uncollation/collation adapters;
- backend autograd proof or no-grad/detach policy beyond preserving handles;
- evaluation/report generation;
- concrete Lightning, Fabric, torch, JAX, or logger dependencies in core;
- public Stage 11 objective or metric stand-ins from learning/training;
- additional concrete learner families beyond `SupervisedLearner`.

## Stage 11 Sequencing

Stage 11 objective and metric code is a sequencing dependency that now exists
in this worktree. Stage 12 should integrate against those public contracts
where practical, while still using test-local fake backend scalars, optimizers,
external engines, or trainable owners when engine mechanics need dependency-free
pressure tests. It must not publish objective, loss, metric, observation, or
metric table stand-ins from `rphys.learning` or `rphys.training`.

Post-prediction batch pipelines over model outputs are deferred from Stage 12.
The Stage 12 design should still keep predictions field-aware and
trainer-opaque so a later stage or downstream wrapper can compose
`BatchOperationPipeline` over model outputs without trainer-side
materialization or export.

## Validation Strategy

Validation planner date: 2026-05-16

Required validation must prove the accepted Stage 12 contract without adding
real Lightning, learner-level post-prediction pipeline execution, mode-specific
prediction pipeline specs, trainer-owned prediction routing, `TrainingPlan`
pipeline fields, or sample uncollation adapters.

| Coverage area | Required checks | Likely locations | Likely commands | Related FRs / decisions | Status |
| --- | --- | --- | --- | --- | --- |
| Package and import boundaries | Import `rphys.learning`, `rphys.training`, and implemented submodules without importing Lightning, torch, JAX, logger, video, plotting, dataset-SDK, or heavy array stacks; expose only code-backed names. | `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`, `src/rphys/learning/__init__.py`, `src/rphys/training/__init__.py` | `make test-package`, `uv lock --check` | FR-12-1 through FR-12-8; DD-12-8; DQ-12-6 | required |
| Learning primitives | Validate `LoopMode`, `LoopContext`, structural `Learner`, primitive metadata/provenance, mode/split distinction, invalid modes/indexes, and forbidden learner responsibilities. | `tests/unit/rphys/learning/*`, `tests/contracts/test_stage12_learner_contract.py`, `src/rphys/learning/*` | `make test-unit`, `make test-contract` | FR-12-1; DD-12-12 | required |
| `StepOutput` and scalar boundary | Validate accepted prediction union `MethodOutput | Sample | Batch | None`, immutable or primitive summary mappings, opaque prediction handling, train objective/backward requirements, unsupported scalar failures, backend override path, and no backward outside train. | `tests/unit/rphys/learning/test_output*.py`, `tests/contracts/test_stage12_step_output_contract.py`, `tests/unit/rphys/training/test_backend*.py` | `make test-unit`, `make test-contract` | FR-12-2, FR-12-4; DQ-12-5; DD-12-9, DD-12-10 | required |
| `SupervisedLearner` composition | Validate Stage 10 `MethodOutput` pass-through, local prediction application only for objective/metric calculation, Stage 11 objective/metric integration, prediction-only mode, missing train objective failure, detached metrics, and no input batch mutation unless explicitly documented. | `tests/contracts/test_stage12_supervised_learner_contract.py`, `tests/integration/test_stage12_synthetic_training_flow.py`, `tests/support/*` | `make test-contract`, `make test-integration` | FR-12-3; DD-12-13 | required |
| Deferred post-prediction pipeline compatibility | Review docs/examples to ensure future `BatchOperationPipeline` over model outputs is documented, while Stage 12 code and phases do not add learner pipeline hooks, mode-specific specs, trainer routing, plan fields, or sample uncollation adapters. | `docs/roadmap/stage-12/planning.md`, future Stage 12 public docs/docstrings, implementation-plan acceptance criteria | `git diff --check`; review during implementation-plan and PR review | FR-12-9; DQ-12-7; DD-12-16 | required docs/review check |
| `TrainingPlan` neutrality | Validate assembled batch sources/loaders, primitive limits, observers/profilers, optional native backend descriptors, metadata/provenance, invalid loop limits, and absence of `engine_config`, dataset paths, artifact dirs, project config parsing, and framework trainer/logger/callback fields. | `tests/unit/rphys/training/test_plan*.py`, `src/rphys/training/plan.py` | `make test-unit` | FR-12-6; DQ-12-2; DD-12-5 | required |
| `TrainingResult` summaries | Validate completed/failed/stopped/partial statuses, mode/count/failure summaries, metric summaries, optional last-step/event/profile summaries, minimal monitored metric/checkpoint identifiers, primitive metadata/provenance, missing external evidence, and no raw framework-private objects. | `tests/unit/rphys/training/test_results*.py`, `tests/contracts/test_stage12_training_result_contract.py` | `make test-unit`, `make test-contract` | FR-12-7; DQ-12-3; DD-12-6 | required |
| Trainer facade and engine delegation | Validate `Trainer` defaults to `NativeTrainingEngine`, delegates each mode to the selected engine with separate `plan` and `learner`, `run_train` is thin/experimental, fake external engine never enters native loop, and no engine registry or workflow runtime appears. | `tests/contracts/test_stage12_trainer_engine_contract.py`, `tests/integration/test_stage12_fake_external_engine.py`, `src/rphys/training/core.py`, `src/rphys/training/experimental.py` | `make test-contract`, `make test-integration` | FR-12-5; DQ-12-1; DD-12-1, DD-12-2, DD-12-15 | required |
| Native engine mechanics | Validate fit/validate/test/predict over already-built `Batch` iterables, context creation, device mover order, train-only backward/optimizer/scheduler behavior, max epoch/step limits, objective-required failures, error result normalization, and no datasource/dataloader construction. | `tests/unit/rphys/training/test_native_engine*.py`, `tests/integration/test_stage12_synthetic_training_flow.py` | `make test-unit`, `make test-integration` | FR-12-4, FR-12-5, FR-12-6; DD-12-3 | required |
| Events, observers, and profiling | Validate dependency-light event/profile records, phase/status vocabulary, observer-only callbacks, event ordering, profile span summaries, unavailable probes, overhead metadata, fake external mapping, and Stage 15 deferral wording. | `tests/unit/rphys/training/test_events*.py`, `tests/unit/rphys/training/test_profiling*.py`, `tests/contracts/test_stage12_observability_contract.py` | `make test-unit`, `make test-contract` | FR-12-8; DD-12-14 | required |
| Fake external trainable-owner pressure | Validate explicit adapter-local single trainable owner, shared identity with method, method-as-module and nested-module cases, duplicate rejection, unsupported pure-Python owner behavior, fake logged metrics/checkpoint/profile/callback summaries, and no torch/Lightning import. | `tests/support/stage12_fake_external.py`, `tests/contracts/test_stage12_external_engine_contract.py` | `make test-contract`, `make test-package` | FR-12-5, FR-12-7, FR-12-8; DQ-12-4, DQ-12-6; DD-12-4, DD-12-7 | required |
| Scientific/workflow contracts | Validate no leakage of datasource scanning, dataloader construction, config/runtime/artifact ownership, checkpoint writing, prediction export/materialization, report generation, learner-owned optimizer behavior, or Stage 11 stand-ins from learning/training. | Cross-cutting contract tests, docs/docstrings, package exports, implementation-plan review | `make test-contract`, `make validate-pr` | Behavior Confirmation; Explicit Non-Goals; Stage 11 Sequencing | required |

Optional checks that would materially reduce risk:

| Optional check | Risk reduced | Likely location or command | Trigger |
| --- | --- | --- | --- |
| Serialization smoke checks for plans/results/events/profiles with primitive metadata. | Confirms downstream workflow persistence can consume summaries without raw framework objects. | Unit tests near `tests/unit/rphys/training/test_results*.py`; `make test-unit` | Add if result records claim serializable/primitive behavior beyond type validation. |
| Type-checking or protocol conformance smoke tests for structural learner and engine fakes. | Catches accidental nominal-base-class or protocol signature drift. | Contract tests or any existing type-check command if later adopted. | Add if implementation uses runtime-checkable protocols or overload-heavy signatures. |
| Property-style table tests over invalid loop limits, modes, statuses, and event phases. | Reduces edge-case gaps in record validation. | Unit tests using parametrization; `make test-unit` | Add if validation helpers grow beyond simple dataclass/Pydantic-style checks. |
| Micro smoke timing checks for profile span aggregation using fake clocks. | Avoids flaky wall-clock tests while proving profiling summaries. | Unit tests with fake clock; `make test-unit` | Add if profiling summaries compute durations rather than storing caller-provided spans. |

Recommended final validation for the implementation plan or PR:

```bash
make test-package
make test-unit
make test-contract
make test-integration
make test-summary
git diff --check
uv lock --check
make validate-pr
```

## Implementation Phase Shape

Phase shaping result: passed. The implementation should be split into
reviewable phases with non-overlapping acceptance criteria. No phase may
implement learner-level post-prediction `BatchOperationPipeline` execution,
mode-specific prediction pipeline specs, `TrainingPlan` pipeline fields,
trainer-owned routing, or sample uncollation adapters.

| Phase | Scope and review boundary | Depends on | Acceptance criteria | Required tests/checks | Design impact and future compatibility | Main risks |
| --- | --- | --- | --- | --- | --- | --- |
| P1 learning contract foundation | Add `LoopMode`, `LoopContext`, `StepOutput`, `BackwardableScalar` boundary, structural `Learner`, private validation helpers, and package exports. | Stage 10/11 public imports only. | Learning primitives are code-backed, dependency-light, mode/split distinction is explicit, predictions stay opaque, and exports expose only implemented names. | Package/import tests; unit/contract tests for modes/context/output/scalar errors. | Establishes the public learner-to-engine boundary used by all later phases; keeps JAX/Lightning pressure behind engines/adapters. | Over-widening context or scalar contracts; importing training from learning; accidentally requiring torch-like scalar behavior everywhere. |
| P2 supervised learner composition | Add `SupervisedLearner` over Stage 10 `Method` and Stage 11 objective/metric contracts, with test-local fakes only for dependency-free mechanics. | P1; existing Stage 10/11 contracts. | `MethodOutput` is the default prediction; objective/metrics use local working composition only; prediction mode works without objective; train mode fails clearly when objective/backward is required; no optimizer/export/checkpoint behavior appears. | Contract and integration tests for synthetic method/objective/metric flow, prediction-only mode, missing objective failure, detached metrics, and no unintended input mutation. | Provides the first concrete learner while preserving future learner-family extensibility and Stage 13 prediction handoff. | Accidentally materializing/exporting predictions; publishing objective/metric stand-ins; sneaking in pipeline execution. |
| P3 plan, result, facade, and delegated engine boundary | Add `TrainingPlan`, `TrainingResult` summaries, provisional `TrainingEngine`, `Trainer` facade, and mode-specific delegation without native loop complexity beyond minimal stubs/fakes. | P1; P2 for learner fixtures. | Plan remains assembled-object oriented with no `engine_config`; result summaries are primitive; `Trainer` delegates through an explicitly selected engine in this phase; fake engine receives separate `plan` and `learner`; `run_train` behavior is specified if included here or deferred to P6. The public `NativeTrainingEngine` default is completed in P4. | Unit tests for plan/result records; contract tests for facade dispatch, fake engine calls, no accidental native execution, and no workflow/config/artifact ownership. | Locks the RemotePhys facade/engine protocol before adding native mechanics; supports future Lightning/JAX/downstream engines. | Plan/result schema creep; treating `Trainer` as loop owner in public wording; adding registry, config escape hatch, or placeholder native default. |
| P4 native engine mechanics | Implement `NativeTrainingEngine` loops over already-built `Batch` iterables plus backend/device/backward/optimizer/scheduler descriptors and result accumulation. | P1-P3. | Fit/validate/test/predict run through native mode methods; train-only backward/optimizer/scheduler order is explicit; validate/test/predict do not backward; failures normalize into results; no datasource/dataloader construction occurs. | Unit tests for backend descriptor order and failure behavior; integration tests for native synthetic fit/validate/test/predict; import-boundary checks. | Provides reference execution while keeping mature framework features delegated. | Reimplementing Lightning-sized features; ambiguous objective-required policy; flaky loop-limit behavior. |
| P5 observability and fake external pressure | Add `TrainingEvent`, observers/callbacks, profile/span summaries, unavailable/overhead metadata, fake external-engine mapping, and fake trainable-owner guardrails. | P3; P4 where native event/profile emission is tested. | Native and fake external engines emit comparable dependency-light records; callbacks are observe-only; fake external adapter proves single trainable owner/shared identity and primitive external summaries; real Lightning remains absent. | Unit/contract tests for events/profiles/observer-only behavior, fake external mapping, duplicate trainable-owner rejection, missing partial summaries, and no torch/Lightning imports. | Preserves Stage 15 profiling path and future optional Lightning adapter path without importing frameworks. | Event vocabulary too broad; callbacks gaining loop control; fake adapter overfitting or implying real Lightning support. |
| P6 docs, examples, experimental entrypoint, and final validation | Add or refresh public docs/docstrings/examples, `run_train` if not already included, end-to-end synthetic example, future-compatibility note for post-model batch pipelines, final import and validation sweep. | P1-P5. | Docs match accepted responsibilities; examples show native and fake external patterns without real Lightning implementation; future batch-pipeline ability is documented only; no pipeline execution phase or code exists; final validation evidence is recorded. | Docs/review checks; package/unit/contract/integration suites; `make test-summary`; `git diff --check`; `uv lock --check`; `make validate-pr`. | Makes the accepted public contract usable and preserves revisit triggers for Stage 13, Stage 15, optional Lightning, JAX, and post-prediction pipelines. | Docs promising future features as current behavior; adding docs-only changes outside approved phase flow; incomplete final validation. |

Phase dependencies are linear enough for review clarity, but P5 observability can
start after P3 if it avoids touching native loop internals that P4 owns. The
implementation plan should keep file ownership explicit if phases run in
worktrees. P2 and P4 are the main scientific/workflow contract phases; P3 and
P5 are the main interface/adapter/reuse phases.

Implementation-plan acceptance criteria should explicitly include:

- no unresolved functionality or design queue items;
- no real Lightning/JAX/torch/logger dependency in Stage 12 core;
- no learner-level post-prediction pipeline execution or plan/router fields;
- no datasource, dataloader, config, artifact, checkpoint-writer, export, or
  report-generation ownership;
- public behavior backed by tests and docs before downstream use.

## Plan Quality Gate

Gate result: passed. Implementation-plan drafting may proceed.

| Check | Evidence reviewed | Result | Notes |
| --- | --- | --- | --- |
| Required specialist evidence | Context/functionality scaffold, functionality agreement, behavior confirmation, design proposer evidence, design implication/reuse safety review, examples, audit, design agreement, validation/phase shaping. | passed | Evidence is recorded in this artifact. No required specialist pass is missing or stale relative to the accepted DQ-12-7 deferral. |
| Agreement queues | FQ-12-1 through FQ-12-8 locked; FQ-12-9 deferred/documented. DQ-12-1 through DQ-12-6 locked; DQ-12-7 deferred/documented. | passed | No item remains `needs maintainer discussion`, `blocked`, `pending approval`, or `ready for approval`. No queue reopen is required. |
| Traceability | Roadmap extraction, capability triage, module behavior map, FR-12-1 through FR-12-9, DQ/DD records, behavior confirmation, examples, validation, and phases. | passed | FR-12-1 through FR-12-8 map to implementation validation and phases. FR-12-9 maps only to docs/review checks and future-compatibility notes. |
| Future-roadmap compatibility | Stage 13 prediction/evaluation pressure, Stage 15 profiling, optional Lightning, future JAX, downstream workflow/persistence, and post-prediction batch pipelines. | passed | Revisit triggers are recorded. Current phases avoid decisions that would force trainer-owned prediction materialization, framework imports, or workflow ownership. |
| Interface/adapter/protocol reuse | `Learner`, `TrainingEngine`, `TrainingPlan`, `TrainingResult`, events/profiles, backend descriptors, fake external adapter pressure. | passed | Protocols are narrow and provisional where needed. Adapter-specific trainable-owner behavior stays out of core public helpers. |
| Scientific/workflow contracts | Mode/split distinction, objective/backward semantics, prediction opacity, Stage 11 integration, metadata/provenance, leakage and ownership non-goals. | passed | Required tests cover failure behavior, edge cases, and no hidden optimizer/export/config responsibilities. |
| Phase granularity and reviewability | Six phases with dependencies, acceptance criteria, validation expectations, design impact, and risks. | passed | No phase combines unrelated public API, native mechanics, fake external pressure, docs, and final validation into a single broad review. |
| Ambiguity and blocked decisions | Current accepted design state from maintainer is reflected, including DQ-12-7 deferral. | passed | No implementation agent must invent product or design decisions before drafting `implementation-plan.md`. |
| Stale or reopened evidence | Stage 11 code-backed contracts are recorded as present; pipeline deferral supersedes earlier reopened state. | passed | Evidence should be rechecked only if Stage 10/11 contracts change before implementation planning starts. |
| Documentation/workflow readiness | This pass updated only `planning.md`; no code or `implementation-plan.md` was created. | passed | Next gate is implementation-plan drafting, not code implementation. |

Blocking findings: none.

Unresolved/open questions: none.

Queue reopen required: no.

No implementation code should be written until an implementation plan is
created and approved.

## Resume Checkpoints

### After Context And Functionality Reconstruction

- Queue state: FQ-12-1 through FQ-12-8 preserved and locked; FQ-12-9 resolved
  as deferred/documented. FQ-12-2, FQ-12-5, FQ-12-6, and FQ-12-7 remain
  maintainer-locked through existing DQ approvals; FQ-12-1, FQ-12-3,
  FQ-12-4, and FQ-12-8 remain repo-resolved defaults accepted by
  managing-agent review.
- Behavior confirmation status: passed.
- Open questions: none for functionality.
- Next step: validation, phase shaping, and plan quality.

### After Functionality Agreement And Behavior Confirmation

- Queue state: FQ-12-1 through FQ-12-8 locked; FQ-12-9 deferred/documented.
  FR-12-1 through FR-12-8 locked; FR-12-9 documentation-only.
- Behavior confirmation status: passed.
- Open questions: none.
- Next step: validation planning.

### After Functionality Agreement

- Queue state: FQ-12-1 through FQ-12-8 locked; FQ-12-9 deferred/documented.
  FR-12-1 through FR-12-8 locked; FR-12-9 documentation-only.
- Behavior confirmation status: passed.
- Open questions: none.
- Next step: design agreement.

### After Design Agreement

- Queue state: DQ-12-1 through DQ-12-6 are already maintainer-approved or
  maintainer-locked and preserved; DQ-12-7 is resolved as
  deferred/documented. DD-12-1 through DD-12-15 map the proposed
  implementation shape to locked FR-12-1 through FR-12-8; DD-12-16 maps to
  deferred FR-12-9.
- Implementation shape locked: DQ-12-1 through DQ-12-6 and FR-12-1 through
  FR-12-8; DQ-12-7 is a future-compatibility documentation constraint.
- Open questions: none.
- Next step: validation planner and phase shaping.

### After Validation, Phase Shaping, And Plan Quality Gate

- Validation baseline locked: required package/import, unit, contract,
  integration, fake external-engine, docs/review, and final validation checks
  are recorded. Optional checks are identified only where they materially
  reduce risk.
- Phase sketch locked: six reviewable phases cover learning primitives,
  supervised learner composition, plan/result/facade contracts, native engine
  mechanics, observability/fake external pressure, and docs/examples/final
  validation.
- Gate result: passed. Implementation planning may proceed.
- Open questions: none.
- Next step: create `implementation-plan.md` through the implementation
  planner. No code implementation should begin until that plan is approved.

### After Implementation Planning

- Implementation plan status: drafted at
  `docs/roadmap/stage-12/implementation-plan.md` and reviewed/refined.
- Phase sketch: six phases are recorded with ownership, validation,
  acceptance evidence, risks, assumptions, and stop conditions.
- Review result: passed with two resolved clarity concerns. Phase 3 now keeps
  explicit selected-engine delegation until `NativeTrainingEngine` exists in
  Phase 4; Phase 5 now limits fake external-engine summaries to primitive
  optional evidence and forbids framework-private parsing.
- Gate result: passed; maintainer approved the implementation plan on
  2026-05-16.
- Open questions: none.
- Next step: begin Phase 1 implementation through
  `.codex/workflows/roadmap-version-implementation.md`.

## Change Log

| Round | Update |
| --- | --- |
| 2026-05-16 / design narrative | Documented Stage 12 purpose, proposed interfaces, responsibility map, native trainer flow, Torch Lightning alignment, examples, non-goals, Stage 11 sequencing, and phase shape. No implementation plan or code created. |
| 2026-05-16 / Lightning trainable module clarification | Clarified that `SupervisedLearner` owns step semantics while the Lightning adapter registers the same trainable module or parameter owner used by the method; this avoids duplicating learnable models or moving optimizer mechanics into the learner. |
| 2026-05-16 / delegated engine architecture | Added the `Trainer` facade and `TrainingEngine` boundary so RemotePhys can keep its learner/trainer paradigm while delegating loop control to native, Lightning, or future backend engines without duplicating mature framework features. |
| 2026-05-16 / delegated engine design review | Reviewed the facade/engine architecture, resolved responsibility-map and plan/config risks, added duplicate-registration and result-normalization guardrails, and recorded validation implications. |
| 2026-05-16 / design implication and safety audit | Added source evidence refresh, specialist-evidence blockers, design agreement queue, decision triage, maintainer decision packets, future-roadmap/reuse review, functionality/decision audit, examples, and blocked design gate status. No code or implementation plan created. |
| 2026-05-16 / DQ-12-1 approval | Maintainer approved `Trainer` as the RemotePhys facade, `TrainingEngine` as a provisional loop-control boundary with mode-specific `fit/validate/test/predict(plan, learner)` methods, separate `learner` and `TrainingPlan` arguments, and `NativeTrainingEngine` as the default reference engine. |
| 2026-05-16 / DQ-12-2 approval | Maintainer approved keeping `TrainingPlan` simple for Stage 12: assembled batch iterables/loaders, primitive loop limits, RemotePhys observers, optional native backend descriptors, metadata/provenance, no generic `engine_config`, and additive expansion only when needed. |
| 2026-05-16 / DQ-12-3 approval | Maintainer approved keeping `TrainingResult` simple for Stage 12: primitive status/mode/counts/failures/metrics, optional last-step and event/profile summaries, metadata/provenance, minimal optional monitored metric/checkpoint identifiers when already available, no framework-private state, and additive expansion only when needed. |
| 2026-05-16 / DQ-12-4 approval | Maintainer approved explicit adapter-local trainable parameter owner registration for external engines, exactly one registered object shared with the method, fake external-engine validation in Stage 12, and no public trainable-module helper/protocol or core framework introspection yet. |
| 2026-05-16 / DQ-12-5 approval | Maintainer approved provisional `StepOutput.predictions: MethodOutput | Sample | Batch | None`, `SupervisedLearner` defaulting to `MethodOutput`, trainer/engine-opaque predictions, minimal native `BackwardableScalar` with backend override path, no backward outside train, and Stage 11 integration with test-local fakes only where engine mechanics need them. |
| 2026-05-16 / DQ-12-6 approval | Maintainer approved deferring real Lightning implementation from Stage 12 core; Stage 12 will implement the engine boundary, native engine, result/event vocabulary, fake external-engine pressure tests, docs/examples, and strict import-boundary checks, with real Lightning left to a later optional adapter phase or stage. |
| 2026-05-16 / functionality agreement and behavior confirmation | Managing agent accepted repo-resolved functionality defaults FQ-12-1, FQ-12-3, FQ-12-4, and FQ-12-8, and confirmed maintainer-locked FQ-12-2, FQ-12-5, FQ-12-6, and FQ-12-7. Later review reopened FQ-12-9 because explicit maintainer approval was not visible. Current locked range is FR-12-1 through FR-12-8. |
| 2026-05-16 / context and functionality reconstruction | Added missing full-template workflow evidence sections: source evidence, exploration coverage, roadmap extraction, stage gates, stage readbacks, capability triage, module behavior map, functionality agreement queue, functional requirements, behavior confirmation, and resume checkpoints. Updated stale Stage 11 absence blockers to reflect current code-backed Stage 11 contracts. No implementation plan or code created. |
| 2026-05-16 / post-prediction pipeline clarification | Added FQ-12-9 and FR-12-9 for optional differentiable post-prediction `BatchOperationPipeline` composition after explicit `MethodOutput` application. Additional review reclassified this as a candidate needing explicit maintainer discussion, not locked behavior. |
| 2026-05-16 / design proposer refresh | Added independent Proposed Implementation Shape, DD-12-1 through DD-12-16, DQ-to-FR traceability including DQ-12-7 for post-prediction pipeline behavior, required proposer classifications, future-roadmap/adversarial assumptions, validation obligations, and updated gate/resume status to mark design proposer evidence complete. No implementation plan or code created. |
| 2026-05-16 / additional design implication review | Reopened FQ-12-9, DQ-12-7, FR-12-9, and DD-12-16 because optional post-prediction `BatchOperationPipeline` composition is high-impact public learner behavior and explicit maintainer approval was not visible. Preserved DQ-12-1 through DQ-12-6. Marked design approval blocked pending maintainer decision. |
| 2026-05-16 / DQ-12-7 deferral | Maintainer clarified that Stage 12 does not need to implement learner-level post-prediction `BatchOperationPipeline` execution now. The plan records the desired future ability to run batch pipelines over model outputs and keeps Stage 12 implementation scope limited to simpler learner/trainer contracts. |
| 2026-05-16 / validation phase shaping quality gate | Added required and optional validation coverage, shaped six implementation phases, checked specialist evidence and traceability, passed the plan quality gate, and recorded that implementation planning may proceed. No code or implementation plan created. |
| 2026-05-16 / implementation-plan draft | Created `docs/roadmap/stage-12/implementation-plan.md` with six phases, ownership boundaries, validation expectations, acceptance evidence, risks, assumptions, and stop conditions. No code implemented. |
| 2026-05-16 / implementation-plan design review | Reviewed the implementation plan against locked Stage 12 decisions, implementation workflow expectations, import-boundary policy, Stage 10/11 contracts, phase granularity, and deferrals. Refined Phase 3 native-default timing and Phase 5 fake external summary scope; no queue reopening or code implementation. |
| 2026-05-16 / implementation-plan approval | Maintainer approved the Stage 12 implementation plan. Phase 1 implementation may begin through the roadmap-version implementation workflow. |
