# Roadmap Stage 6 Implementation Plan

Status: implemented
Roadmap version: `v6`
Planning document: `docs/roadmap/stage-6/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: all phases merged
Blockers: none

## Summary

- Goal: implement the Stage 6 generic operation foundation in `rphys.ops`: code-backed public operation exports, pure functional-kernel boundaries, generic operation contracts, runtime-only context/result records, wrapper-first operation execution, ordered sequence pipelines, exercised typed failures, and dependency-light validation/docs.
- Source functionality-agreement gate: passed; FQ-1 through FQ-8 are repo-resolved and accepted.
- Approved behavior: generic operations are explicit, inspectable, dependency-light, and provisional; `.run()` and `__call__` return `OperationResult`; pipelines pass `result.output`; contract/context/result failures are typed and fail loud.
- Source behavior confirmation: passed; no open functionality-level question remains.
- Key design constraints: package-level `rphys.ops` re-exports; focused implementation-home submodules; wrapper-first `Operation`; minimal `OperationContract`; runtime-only `OperationContext` and `OperationResult`; sequence-only `OperationPipeline`; exercised concrete errors only; private helper leakage forbidden.
- Source design-agreement gate: passed; DQ-1, DQ-3, DQ-4, DQ-5, and DQ-6 are locked; DQ-2 and DQ-7 are recorded recommendations; DQ-8/DD-10 is auto-approved with traceability to FR-8 and adversarial helper-leakage review.
- Source functionality-agreement queue: FQ-1 through FQ-8 resolved with no blocker, pending approval, or maintainer-discussion item.
- Source design-agreement queue: no unresolved blocked, needs-maintainer-discussion, pending-approval, or ready-for-approval item remains.
- Source future-roadmap/reuse safety review: passed; Stage 7 SampleOp/BatchOp, Stage 8 export/save, Stage 9 cache/materialization, Stage 5 identity/manifest, and downstream workflow pressures are deferred with revisit triggers.
- Examples covered: plain kernel direct/wrapped use; two-step primitive pipeline; generic `Sample` or `Batch` payload handling; mutation/side-effect declarations; concrete error behavior.
- Source phase shaping: passed; five accepted phases are converted below.
- Source plan quality gate: passed.
- Out of scope: deterministic/randomness declaration fields, public `OperationLike`/Protocol/base class, raw-output operation API, ordered mapping or named-entry pipeline construction, SampleOp/BatchOp locator permissions, export/save/datasource/cache/workflow behavior, concrete rPPG kernels, heavy optional dependencies, root `rphys` re-exports, placeholder future packages, registries, DAGs, routing, retries, resume, and broad batch-program behavior.

## Implementation Workflow State

- Implementation-plan quality gate: passed
- Review pass: manager review passed 2026-05-14
- Refinement pass: not needed
- Confirmation review: not needed; no implementation-plan blocker found
- Automatic merge mode: enabled
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `public-schemas-imports-errors` | merged | `agent/stage-6-p1-public-schemas-imports-errors` | [#38](https://github.com/samcantrill/rphys/pull/38) | `src/rphys/ops` schema/context/kernel vocabulary, `src/rphys/errors.py`, package/import tests | Establish code-backed provisional public surface and minimal declaration records | package/import, unit contract/context, error inheritance if exercised, `git diff --check` | contract/context/result construction |
| 2 | `operation-wrapper-kernel-execution` | merged | `agent/stage-6-p2-operation-wrapper-kernel-execution` | [#40](https://github.com/samcantrill/rphys/pull/40) | `Operation` wrapper/core execution and kernel examples/tests | Implement single-operation wrapper execution and kernel boundary | unit core/kernel, execution contract, package/import regression | plain kernel direct/wrapped use |
| 3 | `ordered-pipeline-composition` | merged | `agent/stage-6-p3-ordered-pipeline-composition` | [#42](https://github.com/samcantrill/rphys/pull/42) | `OperationPipeline` and pipeline tests | Implement ordered sequence pipeline composition | unit pipeline, pipeline contract, package/import regression | two-step primitive pipeline |
| 4 | `runtime-boundary-docs` | merged | `agent/stage-6-p4-runtime-boundary-docs` | [#44](https://github.com/samcantrill/rphys/pull/44) | runtime-boundary test, operation docs/docstrings/examples | Prove runtime/lazy compatibility and document Stage 6 boundaries | integration or contract runtime-boundary test, docs review, `git diff --check` | generic `Sample`/`Batch` payload, mutation/side-effect declarations |
| 5 | `final-validation-readiness` | merged | `agent/stage-6-p5-final-validation-readiness` | [#46](https://github.com/samcantrill/rphys/pull/46) | validation evidence, plan/status updates only if required | Consolidate stage evidence and ready implementation for review/merge | `make test-package`, `make test-unit`, `make test-contract`, `make test-integration`, `make test-summary`, `uv lock --check`, `git diff --check` | full Stage 6 example/guardrail review |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None. Functionality agreement, behavior confirmation, design agreement, validation and phase shaping, plan quality gate, future-roadmap/reuse safety review, and auto-approval traceability checks are resolved. | `docs/roadmap/stage-6/planning.md` plan quality gate and implementation-plan handoff | Continue with five accepted phases after implementation-plan approval. | resolved |

## Cross-Phase Ownership Boundaries

- `src/rphys/ops/`: owns Stage 6 generic operation contracts, context/result records, kernel vocabulary, wrapper execution, private validation helpers, and ordered pipeline implementation. It must not import datasource, IO, codec, workflow, test-support, or heavy optional stacks.
- `src/rphys/ops/__init__.py`: owns package-level re-exports for implemented Stage 6 names only. Do not add root `rphys` exports or placeholder Stage 7/8 names.
- `src/rphys/errors.py`: owns broad existing error bases and only concrete operation/pipeline errors exercised by public behavior and tests.
- `tests/package/`: owns exact package export and lightweight import-boundary coverage.
- `tests/unit/rphys/ops/`: owns source-mirrored unit coverage for contracts, context/result, kernels, core wrapper execution, and pipelines.
- `tests/contracts/`: owns public behavior contracts for operation declaration, execution, pipeline semantics, and runtime-boundary expectations when better treated as a public contract.
- `tests/integration/`: may own one tiny runtime-container/lazy-field boundary test if contract placement is too broad for the fixture shape.
- Public docs/docstrings/examples: document package-level imports and user-visible behavior; do not document private helpers or implementation submodules as stable public API.
- Do not edit `docs/roadmap.md`, `docs/roadmap/stage-5`, source runtime data modules, IO/datasource modules, codec behavior, or unrelated local work unless a phase uncovers a concrete approved blocker.

## Phase 1: Public Schemas, Imports, And Errors

Status: merged
Slug: `public-schemas-imports-errors`
Branch: `agent/stage-6-p1-public-schemas-imports-errors`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p1-public-schemas-imports-errors`
PR: [#38](https://github.com/samcantrill/rphys/pull/38)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: establish the code-backed provisional `rphys.ops` public surface and minimal declaration records before execution behavior depends on them.
- Files/modules owned: likely `src/rphys/ops/__init__.py`, `src/rphys/ops/contracts.py`, `src/rphys/ops/context.py`, `src/rphys/ops/kernels.py`, optional private `src/rphys/ops/_validation.py`, `src/rphys/errors.py`, `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`, `tests/unit/rphys/ops/test_contracts.py`, `tests/unit/rphys/ops/test_context.py`, `tests/unit/rphys/test_errors.py`, `tests/contracts/test_operation_contract.py`.
- Behavior implemented: `OperationRole`, `OperationContract`, `OperationContext`, `OperationResult`, broad `FunctionalKernel` vocabulary, immutable or shallow-immutable declaration/context/result normalization, code-backed package exports, and exercised concrete error classes only if needed by public failures in this phase.
- Decisions applied: DD-1, DD-3, DD-4, DD-5, DD-7, DD-9, DD-10.
- Future-roadmap/reuse constraints: no deterministic/randomness fields, no locator permissions, no export/cache/workflow/identity fields, no public Protocol/base, no placeholder SampleOp/BatchOp/export names, no IO/datasource/heavy imports, no private helper exports or direct private-helper tests.
- Examples or demos covered: contract/context/result construction and invalid declaration examples with synthetic stdlib values.
- Out of scope: operation execution, pipeline execution, concrete kernels, runtime-container examples, registry APIs, durable serialization, root re-exports, Stage 7/8 schemas.
- Dependencies: implementation-plan approval and current `develop` checkout with unrelated work preserved.

### Tasks

- Create focused `rphys.ops` implementation-home modules only for schema/context/kernel vocabulary required by Stage 6.
- Update `rphys.ops.__all__` with implemented provisional names and no placeholder future names.
- Implement minimal contract fields: role, optional input/output type expectations, mutation policy, side-effect labels, required context keys, and failure-mode labels.
- Implement runtime-only context/result records with metadata/provenance mappings, output, operation identity/role, and side-effect evidence as needed; exclude identity-like and durable serialization fields.
- Add private validators only where they remove duplication and keep them local to `rphys.ops`.
- Add only concrete error classes that this phase exercises; otherwise keep broad bases until later phases exercise concrete failures.
- Add package/import-boundary and unit/contract tests for public names, schema validation, context/result construction, error inheritance if applicable, and absence of deferred fields.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Confirm exact exports and lightweight import boundaries for `rphys.ops` and implemented submodules. | yes |
| `make test-unit` | Exercise contract/context/result construction and any concrete error inheritance. | yes |
| `make test-contract` | Validate public operation contract semantics and absence of deferred fields. | yes |
| `git diff --check` | Check Markdown/Python whitespace hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: public names are code-backed; contract/context/result records validate inputs and normalize inspectable metadata/provenance without hidden globals.
- Design-decision evidence: `rphys.ops` package exports are exact; implementation submodules are not promoted as stable public imports; no public Protocol/base or registry exists.
- Future-roadmap/reuse evidence: deterministic/randomness, locator, export/cache/workflow, identity, and serialization fields are absent and tested where practical.
- Example/demo evidence: synthetic construction examples cover valid and invalid declarations.
- Documentation evidence: docstrings describe provisional Stage 6 behavior and deferrals without private helper names.
- Scientific contract evidence: declarations make input/output, mutation, side effects, context requirements, and failure modes inspectable without algorithm-specific schemas.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-6/phases/public-schemas-imports-errors.md`
- Planning/refinement budget: one reviewable phase plan plus at most one refinement pass unless schema naming reveals a blocker.
- Implementation/refinement budget: one implementation pass plus focused fixes.
- PR review budget: one review pass focused on public API, import cost, and schema fields.
- Blocker-resolution budget: stop for maintainer/design review if a required public field conflicts with locked deferrals.
- Pre-submit blocker gate: no extra public names, no deferred fields, no heavy/IO/datasource imports.
- Merge record: PR [#38](https://github.com/samcantrill/rphys/pull/38) squash-merged to `develop` at `159734a0f4c79722afa14abb0484b76cff3ef4d3`; phase worktree and local/remote phase branches cleaned up.

### Risks And Stop Conditions

- Risks: public schema field names are hard to remove; over-eager concrete errors or helpers could become unsupported API; helper validation can accidentally couple to IO primitives.
- Stop conditions: implementation requires deterministic/randomness fields, locator permissions, durable identity/serialization fields, public Protocol/base, or unexercised public error taxonomy; import-boundary tests show `rphys.ops` pulls IO/datasource/heavy stacks.
- Assumptions: exact mutation-policy spelling may be chosen during implementation if it expresses pure/new-output/may-mutate/side-effecting behavior and remains generic.

### Completion Summary

- Implementation: added dependency-light `rphys.ops` schema/context/kernel modules, exact package re-exports, and the three exercised Phase 1 operation construction errors.
- Validation: `make test-package`, `make test-unit`, `make test-contract`, `make validate-pr`, `uv lock --check`, `uv build`, and `git diff --check` passed before merge; latest summary recorded 476 passing tests across package, unit, contract, and integration suites.
- PR: [#38](https://github.com/samcantrill/rphys/pull/38) opened against `develop`
- Merge: squash-merged 2026-05-14 at `159734a0f4c79722afa14abb0484b76cff3ef4d3`
- Follow-up: Phase 2 owns wrapper execution, `.run()`/`__call__`, callable errors, and result validation during execution.

## Phase 2: Operation Wrapper And Kernel Execution

Status: merged
Slug: `operation-wrapper-kernel-execution`
Branch: `agent/stage-6-p2-operation-wrapper-kernel-execution`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p2-operation-wrapper-kernel-execution`
PR: [#40](https://github.com/samcantrill/rphys/pull/40)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement single-operation execution semantics over wrapped callables and prove the plain functional-kernel boundary.
- Files/modules owned: likely `src/rphys/ops/core.py`, `src/rphys/ops/kernels.py`, private validators needed by execution, relevant `src/rphys/ops/__init__.py` export updates, `src/rphys/errors.py` for exercised operation execution failures, `tests/unit/rphys/ops/test_core.py`, `tests/unit/rphys/ops/test_kernels.py`, `tests/contracts/test_operation_execution_contract.py`, package/import regression tests.
- Behavior implemented: wrapper-first `Operation`, callable and callable-object wrapping, input/context validation, callable invocation, result creation or acceptance, output/result validation, `.run()` and `__call__` parity, `OperationResult` returns, explicit `.output` access, and cause-preserving typed operation errors.
- Decisions applied: DD-2, DD-3, DD-5, DD-6, DD-7, DD-9, DD-10.
- Future-roadmap/reuse constraints: no raw-output convenience API, no public Protocol/base, no registry lookup, no hidden RNG/device/schema conversion, no field-level mutation policing, no runtime-container dependency for kernels, no concrete rPPG kernels.
- Examples or demos covered: plain stdlib signal-like kernel direct call and wrapped call with explicit metadata/context/provenance.
- Out of scope: pipeline composition, SampleOp/BatchOp APIs, runtime-container integration, export/save behavior, named steps, workflow context.
- Dependencies: Phase 1 merged or available as base.

### Tasks

- Implement `Operation` as a concrete lightweight wrapper around importable callables or callable objects.
- Validate declared input type and required context before invocation.
- Invoke the callable with explicit input/context behavior chosen from the locked design without hidden globals.
- Return `OperationResult` from both `.run()` and `__call__`; pass bare callable outputs into validated results when allowed by the approved wrapper behavior.
- Preserve operation name, role, metadata/provenance, side-effect evidence, and causes in operation errors.
- Add tests proving direct kernels stay callable without `Sample`, `Batch`, IO, RNG, device movement, schema conversion, or registry lookup.
- Assert no public raw-output execution method exists in Stage 6.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Exercise wrapper execution, kernel boundary, result validation, and operation errors. | yes |
| `make test-contract` | Confirm public execution semantics: result return, context requirements, input/output mismatch, and cause preservation. | yes |
| `make test-package` | Ensure added execution code does not break exports or import boundaries. | yes |
| `git diff --check` | Check whitespace hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: `.run()` and `__call__` both return `OperationResult`; users unwrap `.output`; invalid inputs, missing context, invalid results, and callable exceptions fail loudly.
- Design-decision evidence: wrapper-first composition works for functions and callable objects without public inheritance requirements.
- Future-roadmap/reuse evidence: no raw-output API, no public Protocol/base, no registry, no hidden RNG/device/schema conversion, and no concrete rPPG kernels.
- Example/demo evidence: synthetic plain kernel direct/wrapped example passes.
- Documentation evidence: docstrings/examples explain wrapper requirement for contract/context/provenance and the explicit `.output` unwrapping behavior.
- Scientific contract evidence: functional kernel placement remains payload/parameter/explicit-metadata oriented and dependency-light.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-6/phases/operation-wrapper-kernel-execution.md`
- Planning/refinement budget: one focused execution plan.
- Implementation/refinement budget: one implementation pass plus focused fixes.
- PR review budget: one review pass focused on public call behavior and failure context.
- Blocker-resolution budget: stop for design review if execution requires raw-output API or a public operation protocol.
- Pre-submit blocker gate: result-return semantics and no raw-output API verified by tests.
- Merge record: PR [#40](https://github.com/samcantrill/rphys/pull/40) squash-merged to `develop` at `860baf12fdb1fc36a484adc88f0674ac55dfa03d`; phase worktree and local/remote phase branches cleaned up.

### Risks And Stop Conditions

- Risks: direct-call ergonomics may feel noisy; callable purity cannot be statically proven; error names may need refinement once failures are exercised.
- Stop conditions: implementation cannot support callable objects through wrapper composition, requires hidden globals, or cannot preserve causes in typed errors without broadening public error taxonomy beyond exercised failures.
- Assumptions: any exact callable signature adaptation remains narrow, explicit, and documented through examples rather than a hidden registry.

### Completion Summary

- Implementation: added concrete `Operation` wrapper execution, fixed keyword-context callable invocation, result wrapping/validation, and the two exercised execution errors `InvalidOperationInputError` and `OperationExecutionError`.
- Validation: `make test-package`, `make test-unit`, `make test-contract`, `make validate-pr`, `uv lock --check`, `uv build`, and `git diff --check` passed before merge; latest summary recorded 500 passing tests across package, unit, contract, and integration suites.
- PR: [#40](https://github.com/samcantrill/rphys/pull/40) opened against `develop`
- Merge: squash-merged 2026-05-14 at `860baf12fdb1fc36a484adc88f0674ac55dfa03d`
- Follow-up: Phase 3 owns ordered pipeline composition, step-aware pipeline errors, and explicit `result.output` forwarding.

## Phase 3: Ordered Pipeline Composition

Status: merged
Slug: `ordered-pipeline-composition`
Branch: `agent/stage-6-p3-ordered-pipeline-composition`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p3-ordered-pipeline-composition`
PR: [#42](https://github.com/samcantrill/rphys/pull/42)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: add generic ordered `OperationPipeline` composition over approved operation/result behavior.
- Files/modules owned: likely `src/rphys/ops/pipelines.py`, private compatibility/step-context validators, `src/rphys/ops/__init__.py`, `src/rphys/errors.py` for exercised pipeline failures, `tests/unit/rphys/ops/test_pipelines.py`, `tests/contracts/test_operation_pipeline_contract.py`, package/import regression tests.
- Behavior implemented: sequence-only construction, ordered tuple storage, adjacent declared type compatibility validation, unchanged explicit context propagation, `result.output` forwarding, final `OperationResult` return, and step-aware pipeline errors with step index plus operation name and cause.
- Decisions applied: DD-6, DD-8, DD-9, DD-10.
- Future-roadmap/reuse constraints: no ordered mapping or named-entry construction, no DAG/routing/retry/resume/workflow runtime, no per-step workflow context policy, no SampleOpPipeline, no BatchProgram, no export pipeline, no private helper dependency in public API.
- Examples or demos covered: two-step synthetic primitive payload pipeline.
- Out of scope: runtime-container boundary tests, docs expansion beyond pipeline docstrings/examples, specialized pipeline classes, export/save side effects.
- Dependencies: Phases 1 and 2 merged or available as base.

### Tasks

- Implement `OperationPipeline` construction from ordered sequences only and store operations in order.
- Reject unsupported construction forms, including unordered mappings and named entries, for Stage 6.
- Validate adjacent declared output/input compatibility at construction or explicit validation time and at execution when runtime values are available.
- Propagate one explicit context unchanged to each operation.
- Forward each step's `OperationResult.output` into the next step and return the final step's `OperationResult`.
- Wrap validation and execution failures with pipeline errors that include step index, operation name, and original cause where applicable.
- Add unit and contract tests for ordering, context propagation, result forwarding, mismatch failures, step-aware diagnostics, and no workflow semantics.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Exercise sequence construction, compatibility validation, result forwarding, and step errors. | yes |
| `make test-contract` | Confirm public pipeline behavior and failure contracts. | yes |
| `make test-package` | Ensure pipeline exports/import boundaries remain lightweight. | yes |
| `git diff --check` | Check whitespace hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: ordered pipelines preserve sequence order, propagate context, forward outputs, return final `OperationResult`, and fail with step-aware context.
- Design-decision evidence: sequence-only construction and diagnostics based on step index plus operation name are implemented.
- Future-roadmap/reuse evidence: ordered mappings/named entries, DAGs, routing, retries, resume, workflow runtime, SampleOpPipeline, BatchProgram, and export pipelines remain absent.
- Example/demo evidence: two-step primitive pipeline demonstrates the full generic composition path.
- Documentation evidence: pipeline docstrings/examples state sequence-only behavior and `.output` forwarding.
- Scientific contract evidence: pipeline validation surfaces declared compatibility without adding hidden scheduling or conversion behavior.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-6/phases/ordered-pipeline-composition.md`
- Planning/refinement budget: one focused pipeline plan.
- Implementation/refinement budget: one implementation pass plus focused fixes.
- PR review budget: one review pass focused on ordering, validation timing, and diagnostics.
- Blocker-resolution budget: stop for design review if sequence-only construction cannot express required Stage 6 behavior.
- Pre-submit blocker gate: tests reject mapping/named-entry construction and workflow/DAG semantics.
- Merge record: PR [#42](https://github.com/samcantrill/rphys/pull/42) squash-merged to `develop` at `9c9bfacc5286cf88ae7964e4811e5c80d2d70147`; phase worktree and local/remote phase branches cleaned up.

### Risks And Stop Conditions

- Risks: Stage 7 may soon need explicit step names; declared adjacent type validation may be underpowered for richer future schemas.
- Stop conditions: implementation requires named entries, per-step context policy, routing, graph semantics, or workflow/artifact state to satisfy current tests.
- Assumptions: richer step naming remains additive and is deferred until Stage 7 pressure proves the need.

### Completion Summary

- Implementation: added sequence-only `OperationPipeline`, static adjacent type compatibility validation, final-result return with `OperationResult.output` forwarding, unchanged context propagation, and the exercised pipeline errors `InvalidOperationPipelineError` and `OperationPipelineExecutionError`.
- Validation: `make test-package`, `make test-unit`, `make test-contract`, `make validate-pr`, `uv lock --check`, `uv build`, `git diff --check`, and automated phase review passed before merge; latest summary recorded 518 passing package/unit/contract/integration tests, with e2e and acceptance suites not present.
- PR: [#42](https://github.com/samcantrill/rphys/pull/42) opened against `develop`
- Merge: squash-merged 2026-05-14 at `9c9bfacc5286cf88ae7964e4811e5c80d2d70147`
- Follow-up: Phase 4 owns runtime-container-as-payload examples, public docs expansion, and mutation/side-effect declaration examples.

## Phase 4: Runtime-Boundary Examples And Public Docs

Status: merged
Slug: `runtime-boundary-docs`
Branch: `agent/stage-6-p4-runtime-boundary-docs`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p4-runtime-boundary-docs`
PR: [#44](https://github.com/samcantrill/rphys/pull/44)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: prove Stage 6 coexists with existing runtime/lazy objects and document exact Stage 6 user and future-agent boundaries.
- Files/modules owned: operation docstrings and any Stage 6 operation docs/examples added during implementation, `tests/integration/test_operation_runtime_container_boundary.py` or `tests/contracts/test_operation_runtime_boundary_contract.py`, possibly small additions to operation contract/execution tests for mutation/side-effect examples.
- Behavior implemented: synthetic examples for plain kernel versus wrapper, sequence pipeline, mutation/side-effect declarations, and generic `Operation[Sample, Sample]` or `Operation[Batch, Batch]` as ordinary payload handling without changing runtime data modules.
- Decisions applied: FR-5, FR-7, FR-8, DD-3, DD-5, DD-7, DD-8.
- Future-roadmap/reuse constraints: no edits to Stage 5 files, no `Sample`, `Batch`, `SampleField`, or `SampleBuilder` semantic changes, no SampleOp/BatchOp locator permissions, no routing, no augmentation replay, no BatchOp equivalence, no export/save behavior, no concrete kernels, no raw datasets, no durable provenance/cache identity.
- Examples or demos covered: generic runtime-container payload handling; lazy `SampleField` materialization remains payload-demand driven; declared mutation/side-effect limitations.
- Out of scope: broad tutorials, data module refactors, real datasource fixtures, CHROM/POS/model kernels, export flows, workflow artifacts.
- Dependencies: Phases 1 through 3 merged or available as base; existing Stage 2/4 runtime contracts remain passing.

### Tasks

- Add one small runtime-boundary test showing a generic operation handles `Sample` or `Batch` as an ordinary payload.
- Verify lazy materialization remains controlled by existing runtime APIs and occurs only if the wrapped callable accesses payload-demanding behavior.
- Document the plain-kernel versus wrapper boundary, result-return execution, explicit `.output` access, sequence-only pipeline construction, and mutation/side-effect declaration limits.
- Document locked Stage 7/8/9 deferrals without implying locator permissions, cache keys, export results, datasource identity, or workflow behavior.
- Ensure examples use synthetic, license-safe, stdlib or existing tiny runtime fixtures only.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-integration` or focused runtime-boundary contract target | Prove generic operations coexist with runtime/lazy objects without changing data modules. | yes |
| `make test-contract` | Keep public operation and runtime-boundary contracts passing. | yes |
| `make test-unit` | Keep mutation/side-effect and docs-backed examples aligned with operation behavior. | yes |
| `git diff --check` | Check docs and code whitespace hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: generic operations can consume `Sample` or `Batch` as ordinary payloads; existing lazy-field behavior remains owned by runtime APIs.
- Design-decision evidence: docs/examples align with package-level imports, result-return execution, sequence-only pipelines, and declared-only mutation/side-effect semantics.
- Future-roadmap/reuse evidence: no locator permissions, export/save, datasource/cache/workflow identity, concrete kernels, or Stage 5 edits appear.
- Example/demo evidence: runtime-container-as-payload and mutation/side-effect declaration examples are present and synthetic.
- Documentation evidence: public docs/docstrings state Stage 6 boundaries and deferrals without private helper references.
- Scientific contract evidence: provenance mappings are described as inspectable runtime records, not durable cache keys or manifests.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-6/phases/runtime-boundary-docs.md`
- Planning/refinement budget: one focused docs/test boundary plan.
- Implementation/refinement budget: one implementation pass plus wording/test fixes.
- PR review budget: one review pass focused on boundary wording and runtime non-interference.
- Blocker-resolution budget: stop if examples require runtime data module changes or imply Stage 7/8 behavior.
- Pre-submit blocker gate: docs/examples do not document private helpers or stable implementation submodules.
- Merge record: PR [#44](https://github.com/samcantrill/rphys/pull/44) squash-merged to `develop` at `15232cf2ea209ee81c5fd420168ad02ccff35bc1`; phase worktree and local/remote phase branches cleaned up.

### Risks And Stop Conditions

- Risks: examples could accidentally imply locator permissions, durable provenance keys, export/cache identity, or stable submodule imports.
- Stop conditions: runtime-boundary proof requires changing `Sample`, `Batch`, `SampleField`, `SampleBuilder`, Stage 5 files, datasource/index behavior, or codec behavior.
- Assumptions: one small synthetic integration or contract test is enough to prove the generic boundary without broad runtime regression rewrites.

### Completion Summary

- Implementation: added runtime-boundary contract coverage proving generic `Operation` accepts loaded `Sample`/`Batch` payloads, preserves explicit `OperationResult.output` unwrapping, and leaves lazy `SampleField` materialization payload-demand driven by existing runtime APIs; updated operation docs/docstrings for package-level imports, plain kernel versus wrapper boundaries, sequence-only pipelines, mutation/side-effect declarations, and Stage 7/8/9 deferrals.
- Validation: `make test-package`, `make test-unit`, `make test-contract`, `make validate-pr`, `uv lock --check`, `uv build`, `git diff --check`, and automated phase review passed before merge; latest summary recorded 521 passing package/unit/contract/integration tests, with e2e and acceptance suites not present.
- PR: [#44](https://github.com/samcantrill/rphys/pull/44) opened against `develop`
- Merge: squash-merged 2026-05-14 at `15232cf2ea209ee81c5fd420168ad02ccff35bc1`
- Follow-up: Phase 5 owns final Stage 6 validation evidence, guardrail review, and readiness accounting.

## Phase 5: Final Validation And Readiness

Status: merged
Slug: `final-validation-readiness`
Branch: `agent/stage-6-p5-final-validation-readiness`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p5-final-validation-readiness`
PR: [#46](https://github.com/samcantrill/rphys/pull/46)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: consolidate Stage 6 evidence, broaden validation, and prepare the stage for review/merge.
- Files/modules owned: implementation evidence in this plan or active phase records if the workflow requires status updates; no new feature modules unless final validation exposes a blocker that is separately approved.
- Behavior implemented: no new feature behavior; validation evidence, guardrail review, and residual risk accounting only.
- Decisions applied: all Stage 6 FR-1 through FR-8 and DD-1 through DD-10 as implemented in phases 1 through 4.
- Future-roadmap/reuse constraints: preserve every locked deferral and revisit trigger; no scope expansion during cleanup.
- Examples or demos covered: full Stage 6 example set reviewed against tests/docs.
- Out of scope: new feature work, queue reopening without a concrete blocker, unrelated dirty-file cleanup, Stage 5/source-roadmap edits, implementation-plan rewrite beyond required status/evidence updates.
- Dependencies: Phases 1 through 4 merged.

### Tasks

- Run final required validation commands and record exact results in the active implementation artifact.
- Confirm public imports, import boundaries, private-helper leakage guardrails, docs/examples, and future-roadmap deferrals.
- Review changed files for public/private boundary, scientific contract clarity, and absence of heavy optional dependencies.
- Update `docs/roadmap/stage-6/planning.md` only if the implementation workflow explicitly requires a small handoff/status update; otherwise leave planning untouched.
- Prepare final PR/merge handoff with behavior, scientific contract implications, tests, assumptions, residual risks, and accepted deferrals.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Final public export and import-boundary validation. | yes |
| `make test-unit` | Final source-mirrored unit validation. | yes |
| `make test-contract` | Final public behavior contract validation. | yes |
| `make test-integration` | Final runtime-boundary validation if Phase 4 used integration coverage. | yes |
| `make test-summary` | Generate/confirm repository test summary. | yes |
| `uv lock --check` | Confirm lockfile consistency. | yes |
| `git diff --check` | Final whitespace hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: all Stage 6 package, unit, contract, and runtime-boundary behavior is tested or documented with skipped-command risk explicitly recorded.
- Design-decision evidence: implemented public surface matches locked design and no queue item needs reopening.
- Future-roadmap/reuse evidence: locked deferrals remain absent and revisit triggers are preserved.
- Example/demo evidence: five recommended example categories are covered by docs/tests or explicitly accounted for.
- Documentation evidence: public docs/docstrings match implemented behavior and do not expose private helpers.
- Scientific contract evidence: kernel purity limits, declared mutation limits, explicit context/result provenance, and fail-loud behavior are reviewable.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-6/phases/final-validation-readiness.md`
- Planning/refinement budget: one validation plan.
- Implementation/refinement budget: validation-only fixes unless a concrete blocker is approved.
- PR review budget: final review focused on evidence and scope control.
- Blocker-resolution budget: stop if final validation reveals a design contradiction or missing maintainer decision.
- Pre-submit blocker gate: no unresolved agreement queue, no failed required validation without recorded risk and approval.
- Merge record: PR [#46](https://github.com/samcantrill/rphys/pull/46) squash-merged to `develop` at `7bd231728ac1639b2c8758ea7d6fb772a4421bef`; phase worktree and local/remote phase branches cleaned up.

### Risks And Stop Conditions

- Risks: dirty unrelated files may complicate validation reporting; final tests may reveal exact error-name or mutation-policy spelling issues; Stage 5 adjacency may have changed in another worktree.
- Stop conditions: final validation requires source behavior outside Stage 6, discovers unresolved design contradiction, or finds helper/public API leakage that cannot be fixed without reopening design.
- Assumptions: final validation runs from a clean phase worktree targeting `develop`; unrelated local work in the main checkout remains untouched.

### Completion Summary

- Implementation: validation/evidence-only phase completed without source, test, or public API behavior changes; reviewed Stage 6 public exports, scoped operation submodule exports, Stage 6 error exports, root-export absence, private-helper boundaries, lightweight import guardrails, docs/docstring wording, explicit `.output`, sequence-only pipeline semantics, declaration-only mutation/side-effect wording, runtime payload boundary evidence, and Stage 7/8/9 deferrals.
- Validation: `make test-package` (29 passed), `make test-unit` (416 passed), `make test-contract` (73 passed), `make test-integration` (3 passed), `make test-summary` (package 29 passed, unit 416 passed, contract 73 passed, integration 3 passed, e2e/acceptance not present), `UV_CACHE_DIR=/tmp/uv-cache uv lock --check` (passed after uncached `uv lock --check` hit read-only home cache), `git diff --check` (passed), and `make validate-pr` (package 29 passed, unit 416 passed, contract 73 passed, integration 3 passed, e2e/acceptance not present; `uv lock --check`, `uv build`, and `git diff --check` passed).
- PR: [#46](https://github.com/samcantrill/rphys/pull/46) opened against `develop`
- Merge: squash-merged 2026-05-14 at `7bd231728ac1639b2c8758ea7d6fb772a4421bef`
- Follow-up: Stage 6 complete; Stage 7 owns SampleOp/BatchOp, locator permissions, named entries, and deferred operation-family behavior.

## Cross-Phase Validation

- Full relevant test command: `make test-package`; `make test-unit`; `make test-contract`; `make test-integration`; `make test-summary`; `uv lock --check`; `git diff --check`.
- Focused per-phase tests: package/import tests for Phase 1; unit/contract execution tests for Phase 2; unit/contract pipeline tests for Phase 3; integration or contract runtime-boundary test for Phase 4.
- Docs/template checks: review operation docstrings and any Stage 6 docs/examples for package-level imports, provisional labels, explicit `.output` unwrapping, sequence-only pipelines, mutation/side-effect declaration limits, and deferrals.
- Scientific/workflow contract checks: no hidden IO/RNG/device/schema conversion; no datasource/index/export/cache/workflow behavior; no raw datasets; no concrete rPPG kernels; no heavy optional imports; no private helper leakage.
- Example/demo checks: plain kernel direct/wrapped call, two-step generic pipeline, runtime-container-as-payload behavior, mutation/side-effect declarations, and concrete errors.
- Manual review focus: exact public `__all__`, public schema fields, error export names, import graph, private helper boundaries, docs wording that could imply Stage 7/8/9 behavior, and preservation of unrelated work.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| No implementation readiness blocker found during plan drafting. | note | Manager review found the five-phase plan traceable to the approved planning artifact and ready for phase execution. | resolved |

Gate result:

- Status: passed
- Review evidence: manager readback confirmed passed planning gates, resolved queues, locked deferrals, five reviewable phases, bounded ownership, validation coverage, stop conditions, and no implementation readiness blockers.
- Accepted risks: callable purity cannot be statically proven; arbitrary hidden mutation cannot be fully detected; direct `.output` unwrapping is intentionally explicit; sequence-only pipelines may need additive Stage 7 naming; exact exercised error names may refine during implementation.
- Revisit triggers: helper leakage into public docs/tests/imports; operation contract needs deterministic/randomness or locator fields; context/result records become identity/cache/export/workflow schemas; raw-output API pressure appears; Stage 7 requires named pipeline entries; Stage 5 identity/manifest changes affect generic operation contracts.

## Final Approval

- Approval status: approved 2026-05-14
- Approved scope: Phase 1 through Phase 5 as listed above, targeting `develop` through isolated worktrees under `/home/samcantrill/work/rphys-worktrees`.
- Accepted risks: callable-purity limits, hidden-mutation limits, explicit `OperationResult.output` ergonomics, sequence-only pipeline naming pressure, exact exercised error-name refinement, Stage 5 adjacency, and private-helper leakage guardrails.
- Deferred items: deterministic/randomness declaration fields; public Protocol/base; raw-output operation API; ordered mapping/named-entry pipeline construction; SampleOp/BatchOp locator permissions; export/save/datasource/cache/workflow behavior; concrete rPPG kernels; heavy optional dependencies; root exports; placeholder future packages.
