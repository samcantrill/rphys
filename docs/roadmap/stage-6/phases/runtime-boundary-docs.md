# Phase 4 Execution Plan: Runtime-Boundary Examples And Public Docs

## Metadata

- Status: draft phase execution plan; expanded-path rigor included; ready for implementation
- Roadmap stage: `v6`
- Feature focus: Runtime-container payload boundary and public operation docs
- Stage descriptor: Operation Foundations And Functional Kernels
- Phase descriptor: Runtime-Boundary Examples And Public Docs
- PR title: `Stage 6 Operation Foundations And Functional Kernels - Phase 4: Runtime-Boundary Examples And Public Docs`
- Branch: `agent/stage-6-p4-runtime-boundary-docs`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p4-runtime-boundary-docs`
- Phase execution plan path: `docs/roadmap/stage-6/phases/runtime-boundary-docs.md`
- Full plan: `docs/roadmap/stage-6/implementation-plan.md`
- Planning document: `docs/roadmap/stage-6/planning.md`
- Source phase: Phase 4, `runtime-boundary-docs`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: existing dedicated branch and worktree verified; preserve this branch/worktree/base/target
- Plan quality gate: Stage 6 implementation plan approved; expanded-path rigor used because this phase adds public runtime-boundary wording and examples that must not imply Stage 7/8/9 behavior. Separate refine pass is not needed unless a stop condition below is hit.
- Draft pass: completed 2026-05-14
- Refine pass: not needed before implementation
- Setup limitations: no product code, tests, PR body, PR, or broad validation run during this planning pass. The assigned worktree already existed on `agent/stage-6-p4-runtime-boundary-docs`; local `HEAD`, `develop`, `origin/develop`, and merge-base all resolved to `52b99571bf86df76237fb007aa3a056d88cadfc7`.
- Blockers: none before implementation

## Objective

Prove that Stage 6 generic operations treat existing runtime containers and lazy fields as ordinary Python payloads, then document the public Stage 6 boundary: package-level `rphys.ops` imports, plain kernels versus `Operation`, explicit `OperationResult.output`, sequence-only `OperationPipeline`, declaration-only mutation and side-effect semantics, and Stage 7/8/9 deferrals.

## Full-Plan Context

Phase 1 established the provisional `rphys.ops` public schemas, context/result records, kernel vocabulary, and exercised construction errors. Phase 2 added the wrapper-first `Operation` execution path and explicit `OperationResult.output` behavior. Phase 3 added sequence-only `OperationPipeline` composition and `result.output` forwarding. Phase 4 is a narrow documentation and boundary-proof phase: it must show compatibility with `Sample`, `Batch`, `SampleField`, and lazy materialization without changing any runtime modules. Phase 5 owns final stage-wide validation and evidence consolidation.

Future work that must remain out of scope includes Stage 7 `SampleOp`/`BatchOp` locator permissions and runtime operation families, Stage 8 export/save behavior, Stage 9 cache/materialization identity, concrete rPPG kernels, real datasource fixtures, broad tutorials, and workflow/export/cache provenance semantics.

## Source Phase Summary

- Goal: prove Stage 6 coexists with existing runtime/lazy objects and document exact Stage 6 user and future-agent boundaries.
- Required scope: one focused runtime-boundary test; docs/docstrings/examples for package-level imports, plain kernels versus wrapped operations, explicit `.output`, sequence-only pipelines, mutation/side-effect declarations, runtime containers as ordinary payloads, and locked deferrals.
- Required checkpoints: focused runtime-boundary contract test by default; `make test-contract`; `make test-unit`; `make test-integration` only if the runtime proof moves to integration; docs review; `git diff --check`.
- Acceptance criteria: `Operation` can consume `Sample` or `Batch` as ordinary payloads, lazy `SampleField` materialization remains payload-demand driven by runtime APIs, docs/examples do not imply private helpers or Stage 7/8/9 behavior, and no runtime/data/datasource/IO modules are edited.

## Current Source And Harness Findings

- Existing operation modules: `src/rphys/ops/__init__.py` exports only code-backed Stage 6 names. `Operation.run()` and `__call__()` in `src/rphys/ops/core.py` validate declared input/context, invoke `function(input_value, context=context)`, and always return `OperationResult`. `OperationResult.output` is the payload field in `src/rphys/ops/context.py`. `OperationPipeline` in `src/rphys/ops/pipelines.py` accepts only a non-empty sequence of `Operation` objects and forwards each step's `result.output`.
- Existing declaration APIs: `OperationContract` in `src/rphys/ops/contracts.py` exposes `input_type`, `output_type`, `mutation_policy`, `side_effects`, `required_context`, and `failure_modes`. `OperationMutationPolicy.MAY_MUTATE` and `SIDE_EFFECTING` are declaration/evidence vocabulary only; there is no field-level mutation policing.
- Existing runtime APIs: `Sample` and `Batch` in `src/rphys/data/containers.py` share the `FieldContainer` access shape. `field()` and `field_items()` return stored `FieldValue`-compatible objects; `get()` and `require()` return payloads and may materialize lazy fields. `set_field()` stores `FieldValue` inputs unchanged and wraps raw payloads.
- Existing lazy APIs: `SampleField` in `src/rphys/data/sample_fields.py` subclasses `FieldValue`, starts `UNLOADED`, exposes `state`, `loaded`, `failed`, `load_result`, `load_error`, and `field_value`, and materializes once through `payload`, `load()`, `eager_load()`, `get()`, `require()`, contracts, collation, or `map_tensors_()`.
- Existing tiny lazy fixture pattern: `tests/unit/rphys/data/test_sample_fields.py` defines a local `CountingLoader`, `_load_context()`, `_load_result()`, and `_sample_field()` using `CodecLoadResult`, `LoadContext`, `FieldRef`, `FieldView`, `TemporalIndexSlice`, `ResourceRef`, `FieldValue`, and `SampleField`; these helpers prove a tiny license-safe lazy field can be built without datasource scans or real files.
- Existing runtime evidence: `tests/unit/rphys/data/test_sample_fields.py` proves `Sample.field()`, `field_items()`, and `role()` do not load a lazy handle, while `expected_type`, `get()`, `require()`, `SampleContract`, collation, and `map_tensors_()` are payload-demanding. `tests/unit/rphys/data/test_containers.py` proves `Sample`/`Batch` API parity, `FieldContainer` conformance, field snapshots, copy semantics, and typed missing/type/schema failures. `tests/contracts/test_runtime_core_contract.py` provides loaded runtime contract examples.
- Existing Stage 6 evidence: `tests/contracts/test_operation_execution_contract.py` proves fixed constructor/call signatures, explicit context metadata checks, `OperationResult` return shape, no raw-output API, and side-effect evidence validation. `tests/contracts/test_operation_pipeline_contract.py` proves sequence-only pipeline shape and absence of stable step/pipeline-name APIs. Unit ops tests mirror those behaviors.
- Existing package/import boundary: `tests/package/test_import.py` asserts exact `rphys.ops` exports and no root `rphys` operation exports. `tests/package/test_import_boundaries.py` imports `rphys.ops`, `contracts`, `context`, `core`, `kernels`, and `pipelines` in a subprocess and fails if those imports load `rphys.data`, `rphys.datasources`, `rphys.io`, codec modules, `tests.support`, or heavy optional stacks.

## Phase Isolation State

- Control checkout dirty-state review: main checkout on `develop` had unrelated untracked `docs/roadmap/stage-7/`; this phase must not touch or depend on it.
- Dedicated branch/worktree status: assigned branch and worktree already exist at `/home/samcantrill/work/rphys-worktrees/stage-6-p4-runtime-boundary-docs`.
- Current `develop` base: local `HEAD`, `develop`, `origin/develop`, and merge-base all resolved to `52b99571bf86df76237fb007aa3a056d88cadfc7` before this plan edit.
- Earlier phase dependency status: Phases 1 through 3 are merged into the current base, including operation schemas, wrapper execution, pipeline composition, and merge records.
- Push/PR infrastructure status: not exercised in this planning pass.
- Stop condition if isolation cannot be maintained: stop before implementation if the worktree leaves `agent/stage-6-p4-runtime-boundary-docs`, if unrelated dirty files appear in touched paths, if `develop` advances and invalidates the Phase 1-3 operation surface, or if implementation pressure requires runtime module edits.

## In-Scope Work

- Add a focused runtime-boundary contract test at `tests/contracts/test_operation_runtime_boundary_contract.py` by default. Use `tests/integration/test_operation_runtime_container_boundary.py` only if the proof unexpectedly needs integration-only fixture shape. The current evidence supports contract placement because this is public `Operation` behavior and can use tiny public runtime objects safely.
- In the contract test, construct loaded `Sample` and `Batch` payloads with public `FieldValue`/`FieldLocator` APIs and wrap identity-style kernels with `OperationContract(input_type=Sample, output_type=Sample)` or `OperationContract(input_type=Batch, output_type=Batch)`. Assert `Operation` returns `OperationResult`, `result.output is container`, and no runtime container adaptation occurs in `rphys.ops`.
- Add a tiny lazy `SampleField` boundary test using a local `CountingLoader`, `LoadContext`, `FieldView`, `FieldRef`, `TemporalIndexSlice`, `ResourceRef`, `CodecLoadResult`, and `FieldValue`, following the existing `tests/unit/rphys/data/test_sample_fields.py` fixture pattern. Assert a kernel that passes through or inspects `sample.field(locator)` does not load the field, while a payload-demanding kernel that calls `sample.require(locator, expected_type=tuple)` loads exactly once through existing runtime APIs.
- If useful for docs-backed coverage, add small assertions to existing operation contract/unit tests that `MAY_MUTATE` declarations do not allow side-effect evidence and `SIDE_EFFECTING` declarations validate evidence labels. Do not add mutation enforcement, locator permissions, or new errors.
- Update public docs/docstrings/examples narrowly. Primary candidates are `src/rphys/ops/__init__.py`, `src/rphys/ops/contracts.py`, `src/rphys/ops/core.py`, `src/rphys/ops/pipelines.py`, `src/rphys/ops/kernels.py`, `docs/GLOSSARY.md`, and a narrow `README.md` Current Status wording update if needed to avoid contradicting the implemented `rphys.ops` surface.
- Document package-level imports from `rphys.ops`, the plain-kernel direct-call boundary versus `Operation` wrapping, explicit `.output` unwrapping, sequence-only `OperationPipeline`, mutation/side-effect declarations as inspectable declarations rather than enforcement, runtime containers as ordinary payloads, and Stage 7/8/9 deferrals.
- Keep examples synthetic, license-safe, stdlib-only, and tiny. Use public imports only; do not document private helpers or implementation submodules as stable public API.

## Out-of-Scope Work

- Edits to `src/rphys/data`, `src/rphys/datasources`, `src/rphys/io`, or any `docs/roadmap/stage-5` files.
- Changes to `Sample`, `Batch`, `SampleField`, `SampleBuilder`, `FieldContainer`, locators, codec contexts, datasource indexes, Stage 5 identity/manifest behavior, or lazy materialization semantics.
- `SampleOp`, `BatchOp`, specialized operation families, locator read/write/delete permissions, augmentation replay, BatchOp equivalence, export/save/cache/workflow identity, derived datasources, concrete kernels, real datasets, broad tutorials, or private helper docs.
- New public operation APIs, raw-output helpers, registries, root `rphys` re-exports, placeholder Stage 7/8/9 modules, stable submodule import promises, new errors, or broad docs unrelated to this boundary.
- Importing runtime/data/datasource/IO modules from `src/rphys/ops` to make examples more convenient.

## Assumptions

- The existing `SampleField` fixture pattern is acceptable in a contract test because it uses public records and local in-test fakes without scanning datasources or touching files.
- Contract-suite placement is preferred: the public behavior under test is that `Operation` treats any object, including `Sample` and `Batch`, as a typed payload and does not force materialization. Integration placement is a fallback only if contract fixtures become integration-heavy.
- `Operation` and `OperationPipeline` already have the required public behavior. Phase 4 should not redesign wrappers or pipelines to make docs easier.
- Docs may state that `OperationContract(input_type=Sample, output_type=Sample)` is possible, but must not introduce generic type parameters, `SampleOp`, `BatchOp`, field permission policy, cache keys, export targets, or workflow state.
- Lazy materialization behavior remains owned entirely by runtime APIs: `Sample.field()`/`field_items()`/`role()` are non-payload-demanding; `require()`, `get()`, expected-type validation, contracts, collation, and `map_tensors_()` may demand payloads.

## Scope Contract

Phase 4 does not change public runtime semantics. It adds evidence and wording around existing behavior: Stage 6 generic operations accept runtime containers as ordinary Python inputs/outputs when the wrapped callable and `OperationContract` declare those types. The `Operation` wrapper must not inspect fields, materialize `SampleField`, enforce locators, apply schema conversion, move devices, choose splits, scan datasources, or know about codec builders. Any materialization in tests must be caused by the wrapped callable invoking existing payload-demanding runtime APIs.

Public docs must keep the import contract clear: users import Stage 6 names from `rphys.ops`, not root `rphys`, and not private helpers. `Operation` returns `OperationResult`; users read the payload through `.output`. Plain functional kernels remain normal callables and may be used directly when no contract/context/provenance wrapper is needed. `OperationPipeline` remains sequence-only and forwards `OperationResult.output` between steps.

Mutation and side effects remain declaration and evidence fields. `OperationMutationPolicy.MAY_MUTATE` documents that a callable may mutate its input, while `SIDE_EFFECTING` documents declared side-effect labels and accepts matching evidence. Stage 6 must not add field-level write permissions, side-effect completion proof, export layout, cache identity, or workflow artifact semantics.

## Scientific Contract Notes

- Sampling and temporal alignment: tests may use synthetic tuple/list payloads and `TemporalIndexSlice` descriptor objects only as lazy fixture inputs. No resampling, alignment, padding, windowing, seconds conversion, invalid-rate behavior, or temporal cross-field claim is introduced.
- Field roles, locators, schemas, and provenance: locators and schemas may appear only to construct tiny runtime fields. The operation boundary must not add locator permissions, schema conversion, datasource identity, manifest fingerprints, or cache keys. `OperationContext` and `OperationResult` provenance remain runtime inspectable mappings, not durable manifests.
- Masking, filtering, normalization, and aggregation order: no signal processing algorithm, CHROM/POS kernel, normalization, filter, or aggregation behavior is introduced. Example kernels should be pass-through, identity, or trivial payload access.
- Subject identity, splits, leakage, and grouping: no subject, split, record, or leakage policy changes. Any metadata key in examples is descriptive runtime context only.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: this phase does not add numerical edge-case policy. Missing fields or failed lazy loads should continue to use existing runtime/codec errors when the callable demands payloads; wrapper errors should remain existing operation errors.

## Design Impact

- Maintainability: the phase adds a narrow executable boundary proof and docs, avoiding new adapters or runtime coupling inside `rphys.ops`.
- Extensibility: showing `Sample` and `Batch` as ordinary payloads leaves Stage 7 free to add specialized `SampleOp`/`BatchOp` policies explicitly instead of inheriting hidden Stage 6 behavior.
- Lightweight import policy: `rphys.ops` source imports must stay stdlib plus `rphys.errors`/local ops modules. Any runtime imports belong only in tests or docs examples and must not alter package import-boundary tests.
- Source-tree boundaries: implementation should primarily touch `tests/contracts/test_operation_runtime_boundary_contract.py`, narrow operation docstrings/docs, and any focused operation contract/unit tests required by docs-backed examples.

## Future Compatibility

- Stage 7 can add `SampleOp`, `BatchOp`, locator permissions, augmentation replay, and specialized pipelines without changing the Stage 6 generic `Operation` contract.
- Stage 8 can define export/save operations and side-effect policy without treating Stage 6 `side_effect_evidence` as export results.
- Stage 9 can define cache/materialization identity without treating `OperationContext.provenance` or `OperationResult.provenance` as cache keys or manifests.
- Future docs can grow tutorials after the operation families exist; this phase should only establish the minimal public wording needed to prevent misuse.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Put the runtime-boundary proof in integration by default | The behavior is public operation contract behavior and a tiny public `Sample`/`SampleField` fixture is safe; integration is only a fallback if fixture shape becomes too broad. |
| Import `Sample`, `Batch`, or `SampleField` from `src/rphys/ops` | That would violate the lightweight operation import boundary and couple generic operations to runtime containers before Stage 7. |
| Add `SampleOp`/`BatchOp` examples now | The implementation plan explicitly defers specialized operation families and locator permissions to Stage 7. |
| Use real datasource or builder fixtures for realism | Phase 4 only needs payload compatibility. Datasource scans, builders, records, and real files would expand scope and risk Stage 5/8/9 implications. |
| Add broad operation tutorials | The phase asks for exact boundary docs, not user education across future operation families. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Runtime-boundary tests duplicate a tiny local lazy-field fixture | Reusing test-local public records keeps this phase independent of test-support and datasource fixtures. | Multiple phases need the same fixture and a public/test-support helper becomes justified. |
| `Sample`/`Batch` examples use runtime type expectations, not generic typing syntax | Stage 6 contracts use runtime `type`/`tuple[type, ...]` checks and do not define public generic operation types. | A later accepted API adds generic typing or specialized `SampleOp`/`BatchOp` wrappers. |
| Mutation declarations remain unpoliced | Arbitrary Python mutation cannot be enforced generically without Stage 7 locator policy. | Stage 7 introduces field permission declarations or mutation auditing. |

## Reviewability

- Expected PR size and shape: small docs/test PR, likely one new contract test file plus narrow docstring/docs wording edits and any focused mutation/side-effect assertion updates needed to back examples.
- Files and areas to inspect: `tests/contracts/test_operation_runtime_boundary_contract.py`; `tests/contracts/test_operation_execution_contract.py` only if mutation/side-effect examples need assertions; `tests/unit/rphys/ops/test_contracts.py`, `test_core.py`, or `test_pipelines.py` only for docs-backed unit coverage; `src/rphys/ops/__init__.py`; `src/rphys/ops/contracts.py`; `src/rphys/ops/core.py`; `src/rphys/ops/pipelines.py`; `src/rphys/ops/kernels.py`; `docs/GLOSSARY.md`; `README.md` only if narrowly updated; package/import tests only if public docs wording requires export assertions.
- Scope-control checks: no changes under `src/rphys/data`, `src/rphys/datasources`, `src/rphys/io`, or `docs/roadmap/stage-5`; no private helper docs; no root exports; no new operation APIs; no new errors; no real datasets; no datasource scans; `rphys.ops` import-boundary test remains green.

## Implementation Steps

1. Add the focused runtime-boundary proof in `tests/contracts/test_operation_runtime_boundary_contract.py`: create loaded `Sample` and `Batch` payloads with public runtime APIs, wrap identity kernels with `Operation`, assert `OperationResult` return and explicit `.output`, and verify containers are ordinary payloads.
2. Extend that contract file with one tiny lazy `SampleField` scenario following the existing unit fixture pattern. Assert no load for pass-through or `sample.field(locator)` access, and exactly one load when the wrapped callable calls a payload-demanding runtime API such as `sample.require(locator, expected_type=tuple)`.
3. Update operation docs/docstrings/examples to show package-level imports, direct plain-kernel calls versus `Operation` wrapping, explicit `.output`, sequence-only `OperationPipeline`, runtime containers as ordinary payloads, and mutation/side-effect declaration limits.
4. Review wording for Stage 7/8/9 deferrals: no locator permissions, export/save/cache/workflow identity, concrete kernels, private helpers, root exports, stable implementation submodule imports, or broad tutorials.
5. Add or adjust focused unit/contract assertions only where they enforce new docs wording. Keep runtime/data module tests as evidence, not edit targets.
6. Run focused tests first, then required suite targets; stop if tests or docs require changing runtime modules, adding specialized operation APIs, or weakening import boundaries.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: confirm `rphys.ops` exports remain exact, root `rphys` does not re-export operation names, operation submodule `__all__` values remain scoped, and importing `rphys.ops` plus submodules does not load `rphys.data`, `rphys.datasources`, `rphys.io`, codec modules, `tests.support`, or heavy optional stacks. Update only if docs wording changes public import assertions.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/ops/test_contracts.py`; `tests/unit/rphys/ops/test_core.py`; `tests/unit/rphys/ops/test_pipelines.py`; evidence paths `tests/unit/rphys/data/test_sample_fields.py` and `tests/unit/rphys/data/test_containers.py`
- Required assertions or deferral reason: operation unit tests should remain aligned with docs on mutation/side-effect declarations, `OperationResult` return, no raw-output API, and sequence-only pipelines. Runtime unit tests serve as evidence that `field()`/`field_items()`/`role()` do not load, payload-demanding APIs do load, and `Sample`/`Batch` have API parity; edit them only if a docs-backed assertion belongs there.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_operation_runtime_boundary_contract.py`; existing `tests/contracts/test_operation_execution_contract.py`; `tests/contracts/test_operation_pipeline_contract.py`; `tests/contracts/test_runtime_core_contract.py`
- Required assertions or deferral reason: new contract coverage must prove generic operations accept `Sample`/`Batch` as payloads, return `OperationResult`, require explicit `.output`, do not materialize lazy fields unless the callable invokes payload-demanding runtime APIs, preserve existing runtime lazy semantics, and do not expose raw-output, stable step names, locator permissions, export/cache/workflow identity, or private helper behavior.

### Integration Suite

- Status: conditionally required
- Expected paths: `tests/integration/test_operation_runtime_container_boundary.py` only if contract-suite placement proves too broad
- Required assertions or deferral reason: default is deferred because contract coverage is more precise and the tiny fixture uses public records safely. If the executor chooses integration placement, the same runtime-boundary assertions are required there and `make test-integration` becomes mandatory for the phase.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no end-to-end operation workflow, real dataset, datasource scan, export/save flow, cache/materialization path, or downstream project behavior is involved in this phase.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no hardware, GPU, external dependency, real data, network, or long-running acceptance behavior is involved. Acceptance remains stage-level documentation and validation review in Phase 5.

## Risks

- Docs examples could accidentally imply `SampleOp`, `BatchOp`, locator permission, export/save, cache, workflow, or durable provenance behavior.
- A lazy boundary test can become an integration test by stealth if it starts using builders, datasource records, registries, files, or support fixtures.
- Updating README or glossary wording can drift into broad tutorial work or future-stage promises.
- Runtime imports in docs are acceptable, but runtime imports in `src/rphys/ops` would break the Stage 6 lightweight boundary.
- Mutation wording is easy to overstate; Stage 6 declares possible mutation and side effects but does not police field-level writes or prove external side effects completed.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/contracts/test_operation_runtime_boundary_contract.py
uv run pytest tests/contracts/test_operation_execution_contract.py tests/contracts/test_operation_pipeline_contract.py
uv run pytest tests/unit/rphys/ops/test_contracts.py tests/unit/rphys/ops/test_core.py tests/unit/rphys/ops/test_pipelines.py
uv run pytest tests/unit/rphys/data/test_sample_fields.py tests/unit/rphys/data/test_containers.py
make test-contract
make test-unit
make test-package
# Only if runtime-boundary coverage lands in integration:
make test-integration
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: runtime-boundary contract test first; docs/docstrings second; focused docs-backed assertion updates third; validation last.
- Tests to run with each slice: run the new contract test after the runtime proof; run operation unit/contract tests after docs-backed behavior assertions; run package/import tests after any import or public-doc wording change; run integration only if the boundary test is placed there.
- Decisions the executor must not revisit: contract-suite placement is preferred; `Sample`/`Batch` are ordinary payloads; lazy materialization is runtime-owned; users unwrap `.output`; pipelines are sequence-only; mutation/side effects are declarations/evidence, not permissions or enforcement.
- Conditions that require stopping for the manager: any need to edit `src/rphys/data`, `src/rphys/datasources`, `src/rphys/io`, Stage 5 docs/files, operation execution semantics, package exports, locator permissions, export/cache/workflow identity, concrete kernels, real dataset fixtures, or new public APIs/errors.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in this artifact
- Final phase execution plan: this artifact unless a refinement trigger is hit
- Implementation summary: added `tests/contracts/test_operation_runtime_boundary_contract.py` coverage for generic runtime payload acceptance and lazy boundary behavior, plus narrowed docs/docstrings across `rphys.ops` entrypoints and operation modules.
- Implementation validation: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/contracts/test_operation_runtime_boundary_contract.py` (3 passed), `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/contracts/test_operation_execution_contract.py tests/contracts/test_operation_pipeline_contract.py`, `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/ops/test_contracts.py tests/unit/rphys/ops/test_core.py tests/unit/rphys/ops/test_pipelines.py`, `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_sample_fields.py tests/unit/rphys/data/test_containers.py`, `make test-contract`, `make test-unit`, `make test-package` (29 passed), `make validate-pr` (package 29 passed, unit 416 passed, contract 73 passed, integration 3 passed, e2e/acceptance not present; `uv lock --check`, `uv build`, and `git diff --check` passed)
- Refinement summary: none
- Pre-submit blocker gate: passed
- PR preparation: not required by this phase scope
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none known
