# Roadmap Stage 2 Implementation Plan

Status: implemented
Roadmap version: `v2`
Planning document: `docs/roadmap/stage-2/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: complete
Blockers: none

## Summary

- Goal: implement Milestone 2 loaded runtime core for in-memory field specs, field values, simple and compositional data-object hooks, samples, batches, sample contracts, and LIST-only collation.
- Approved behavior: the full Stage 2 design baseline is recorded in `docs/roadmap/stage-2/planning.md`; this implementation plan is approved for execution.
- Key design constraints: stdlib-only, dependency-free core imports, field-centric containers keyed by `FieldLocator`, no IO/datasource/operation/model/training behavior, no serialization, and fail-loud typed diagnostics.
- Examples covered: loaded video field, target BVP sample access, sample contract validation, LIST collation into `Batch`, rejection of implicit stack/pad behavior, synthetic `DataObjectBase` tensor traversal, and synthetic `CompositeDataObjectBase` child traversal.
- Source phase shaping: proposed five-phase sketch in `docs/roadmap/stage-2/planning.md`.
- Source plan quality gate: pass; planning artifacts support execution of this approved implementation plan.
- Out of scope: lazy IO refs, codecs, datasource scanning, sample builders, transforms, operations, methods, models, losses, objectives, metrics, training, prediction, evaluation, analysis, workflow runtime, artifact references, serialization, stack/pad collation, and optional backend imports.

## Implementation Workflow State

- Implementation-plan quality gate: approved
- Review pass: completed during planning; no blocking finding remains.
- Refinement pass: not required.
- Confirmation review: completed by accepted implementation-plan baseline.
- Automatic merge mode: enabled
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `runtime-fields-errors` | merged | `agent/stage-2-p1-runtime-fields-errors` | [#10](https://github.com/samcantrill/rphys/pull/10) | `rphys.errors`, `rphys.data.fields`, `rphys.data.__init__`, unit/package/contract seeds | Add Stage 2 runtime errors, `FieldSpec`, and `FieldValue` | Unit, package, contract seed, `git diff --check` | Loaded video field and identity-safe payload wrapper |
| 2 | `data-object-base` | merged | `agent/stage-2-p2-data-object-base` | [#11](https://github.com/samcantrill/rphys/pull/11) | `rphys.data.objects`, focused unit tests | Add backend-free `DataObjectBase` and `CompositeDataObjectBase` hooks | Unit, package import boundary | Synthetic tensor-like leaf and child-object traversal |
| 3 | `sample-batch-contracts` | merged | `agent/stage-2-p3-sample-batch-contracts` | [#12](https://github.com/samcantrill/rphys/pull/12) | `rphys.data.containers`, `rphys.data.contracts`, unit/contract tests | Add `Sample`, `Batch`, `FieldRequirement`, and `SampleContract` | Unit, contract, package | BVP target access and sample validation |
| 4 | `list-collation` | merged | `agent/stage-2-p4-list-collation` | [#13](https://github.com/samcantrill/rphys/pull/13) | `rphys.data.collation`, collation unit/contract/integration tests | Add `CollatePolicy.LIST`, `CollateContext`, and `collate_samples` | Unit, contract, integration if useful | Homogeneous sample collation and unsupported policy rejection |
| 5 | `runtime-core-hardening` | merged | `agent/stage-2-p5-runtime-core-hardening` | [#14](https://github.com/samcantrill/rphys/pull/14) | package tests, contract tests, docs/docstrings, cross-phase fixes | Finalize public runtime surface and validation evidence | `make test-unit`, `make test-package`, `make test-contract`, optional integration, `uv lock --check`, `git diff --check` | Full Stage 2 public contract |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| Stage 2 design baseline is approved. | `docs/roadmap/stage-2/planning.md` approvals through DD-12 | No further design-decision discussion is required before execution. | resolved |
| Implementation plan is approved for execution. | Planning workflow explicit approval gate | Maintainer approved the implementation plan after reviewing scope, risks, validation plan, and a final specialist design-analysis pass. | resolved |

## Phase 1: Runtime Fields And Errors

Status: merged
Slug: `runtime-fields-errors`
Branch: `agent/stage-2-p1-runtime-fields-errors`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-2-p1-runtime-fields-errors`
PR: [#10](https://github.com/samcantrill/rphys/pull/10)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: establish the Stage 2 runtime field/value surface and typed diagnostics.
- Files/modules owned: `src/rphys/errors.py`; `src/rphys/data/fields.py`; `src/rphys/data/__init__.py`; `tests/unit/rphys/test_errors.py`; `tests/unit/rphys/data/test_fields.py`; targeted `tests/package/`; contract seed if approved.
- Behavior implemented: `MissingFieldError`, `FieldTypeError`, `FieldSchemaError`, `CollatePolicyError`; `FieldSpec`; `FieldValue`; initial `rphys.data` code-backed exports.
- Decisions applied: DD-1, DD-2, DD-3, DD-4, DD-8, DD-11.
- Examples or demos covered: `FieldSpec("video.rgb", "video", "video.rgb.v1")`; `FieldValue(payload, schema="video.rgb.v1", metadata={"source_id": "fixture"}, collate_policy=None)`.
- Out of scope: containers, sample contracts, collation implementation, data-object hooks, IO, serialization, rich schema validation, and backend imports.
- Dependencies: completed Stage 1 vocabulary modules.

### Tasks

- Add Stage 2 error subclasses without changing `RemotePhysError` mechanics.
- Implement `FieldSpec` with Stage 1 vocabulary coercion, value equality, copy/deepcopy-preserving primitive fields, and no rich schema fields.
- Implement `FieldValue` with identity equality, shallow-copied/coerced metadata, optional schema, optional collation policy placeholder/coercion as available, and copy/deepcopy behavior aligned with roadmap.
- Update `rphys.data.__all__` only for implemented runtime contracts if the design baseline is approved.
- Add focused unit, package, and contract seed coverage.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Verify errors, `FieldSpec`, and `FieldValue`. | yes |
| `make test-package` | Verify public imports and lightweight import boundaries. | yes |
| `make test-contract` if contract seed is added | Verify initial public examples. | yes |
| `git diff --check` | Patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: field spec/value tests pass for valid and invalid examples.
- Design-decision evidence: no shape/dtype/unit/runtime-type fields; no payload value equality.
- Example/demo evidence: loaded video field example is executable in tests.
- Documentation evidence: docstrings explain excluded scientific/schema/serialization behavior.
- Scientific contract evidence: no processing, IO, padding, stacking, or shape semantics introduced.

### Phase Workflow State

- Phase execution plan: covered by approved implementation plan and Phase 1 PR body.
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: standard
- Blocker-resolution budget: return to planning if `rphys.data` export policy or field wrapper semantics change.
- Pre-submit blocker gate: no optional dependencies, no serialization contract, no rich schema fields.
- Merge record: PR [#10](https://github.com/samcantrill/rphys/pull/10), squash merge `8a9c040`.

### Risks And Stop Conditions

- Risks: accidental public hashability assertions; over-exporting names from `rphys.data`; `FieldValue` metadata behavior becoming too broad.
- Stop conditions: implementation needs serialization, payload inspection, or optional backend imports.
- Assumptions: Stage 1 vocabulary constructors are available and stable.

### Completion Summary

- Implementation: complete; added Stage 2 typed runtime errors, `FieldSpec`, `FieldValue`, and initial code-backed `rphys.data` exports.
- Validation: `make test-unit`, `make test-package`, `make validate-pr`, and `git diff --check` passed in the phase worktree.
- PR: [#10](https://github.com/samcantrill/rphys/pull/10).
- Merge: squash merged to `develop` as `8a9c040`.
- Follow-up: none for Phase 1 scope.

## Phase 2: Data Object Bases

Status: merged
Slug: `data-object-base`
Branch: `agent/stage-2-p2-data-object-base`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-2-p2-data-object-base`
PR: [#11](https://github.com/samcantrill/rphys/pull/11)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: add backend-free loaded-payload bases with explicit validation, declared tensor traversal hooks, and declared child data-object traversal.
- Files/modules owned: `src/rphys/data/objects.py`; `src/rphys/data/__init__.py`; `tests/unit/rphys/data/test_objects.py`; targeted package tests.
- Behavior implemented: `DataObjectBase.validate`, tensor mapping/device/detach/pin helper methods, default no-op behavior, typed failure for unsupported operations on declared leaves, and `CompositeDataObjectBase` structural recursion over declared child data-object fields.
- Decisions applied: DD-1, DD-5, DD-11.
- Examples or demos covered: synthetic tensor-like leaf object with `.to()`, `.detach()`, and `.pin_memory()`; synthetic composite object with video-like and landmark-like child data objects.
- Out of scope: torch/numpy helpers, concrete video/signal/landmark wrappers, arbitrary attribute inspection, generic copy/deepcopy guarantees, parent `Sample` or sibling-field references, and video/landmark/timestamp alignment validation.
- Dependencies: Phase 1 errors if an unsupported declared leaf needs a typed data error path.

### Tasks

- Implement `DataObjectBase` with minimal override hooks and no backend imports.
- Implement `CompositeDataObjectBase` as a concrete subclass for explicit local child-data-object composition.
- Ensure helper methods return the object callers must use.
- Add tests with synthetic declared tensor leaves, declared child data objects, recursive traversal, child-type failures, and unsupported leaf failures.
- Verify imports remain lightweight.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Verify `DataObjectBase` and `CompositeDataObjectBase` behavior. | yes |
| `make test-package` | Verify lightweight imports and public exports. | yes |
| `git diff --check` | Patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: no-op defaults, synthetic leaf traversal, child-object recursion, and structural failure cases pass.
- Design-decision evidence: no backend imports, arbitrary attribute walking, parent-sample references, or sibling-field references.
- Example/demo evidence: fake tensor-like object and synthetic composite object demonstrate helper semantics.
- Documentation evidence: docstrings state no in-place guarantee, explicit validation, structural recursion, and deferred scientific alignment checks.
- Scientific contract evidence: no payload-specific scientific assumptions or video/landmark/timestamp alignment validation.

### Phase Workflow State

- Phase execution plan: covered by approved implementation plan and Phase 2 PR body.
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: standard
- Blocker-resolution budget: return to planning if concrete payload behavior or base-level scientific alignment validation is needed.
- Pre-submit blocker gate: no optional backend imports, registry hooks, arbitrary attribute walking, sibling-field links, parent-sample links, or alignment validation.
- Merge record: PR [#11](https://github.com/samcantrill/rphys/pull/11), squash merge `13c3cae`.

### Risks And Stop Conditions

- Risks: base-class API may be too narrow for future structured payloads; `CompositeDataObjectBase` may need richer specialized validation hooks later.
- Stop conditions: implementation requires torch/numpy imports, concrete scientific payload classes, sibling/parent-sample references, or base-level alignment checks.
- Assumptions: later protocols, optional backend helpers, and specialized scientific validators can be additive.

### Completion Summary

- Implementation: complete; added backend-free `DataObjectBase` and `CompositeDataObjectBase` with declared tensor and child traversal.
- Validation: `make test-unit`, `make test-package`, `make validate-pr`, and `git diff --check` passed in the phase worktree.
- PR: [#11](https://github.com/samcantrill/rphys/pull/11).
- Merge: squash merged to `develop` as `13c3cae`.
- Follow-up: none for Phase 2 scope.

## Phase 3: Sample, Batch, And SampleContract

Status: merged
Slug: `sample-batch-contracts`
Branch: `agent/stage-2-p3-sample-batch-contracts`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-2-p3-sample-batch-contracts`
PR: [#12](https://github.com/samcantrill/rphys/pull/12)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement mutable runtime containers and explicit runtime validation contracts.
- Files/modules owned: `src/rphys/data/containers.py`; `src/rphys/data/contracts.py`; `src/rphys/data/__init__.py`; `tests/unit/rphys/data/test_containers.py`; `tests/unit/rphys/data/test_contracts.py`; contract tests.
- Behavior implemented: distinct public `Sample` and `Batch` classes with API parity and private shared implementation, field access/mutation/copy APIs, read-only role filtering, tensor mapping, public `FieldRequirement` records, and `SampleContract`.
- Decisions applied: DD-1, DD-6, DD-7, DD-8, DD-9, DD-11.
- Examples or demos covered: BVP target access, missing field failure, wrong type failure, schema mismatch failure, and sample contract pass/fail cases.
- Out of scope: collation, lazy loading, persistence, sample building from IO refs, transform pipelines, rich scientific validation.
- Dependencies: Phases 1 and 2.

### Tasks

- Implement distinct public `Sample` and `Batch` classes over `FieldLocator -> FieldValue` storage with private shared implementation; `Batch` is not a `Sample` by public contract.
- Implement `has`, `field`, `get`, `require`, `set_field`, `delete_field`, `rename_field`, `role`, `shallow_copy`, `deep_copy`, and `map_tensors_`, with `field()` returning `FieldValue`, `get()`/`require()` returning payloads, and `role()` returning a read-only shallow `FieldLocator -> FieldValue` mapping.
- Implement public `FieldRequirement` records and `SampleContract` for required/optional locators, expected payload types, and schema constraints.
- Add unit and contract coverage for container parity, mutation, copying, validation, and typed failures.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Verify containers and sample contracts. | yes |
| `make test-contract` | Verify public runtime examples. | yes |
| `make test-package` | Verify imports and lightweight boundaries. | yes |
| `git diff --check` | Patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: all expected APIs work on `Sample` and `Batch`; failures are typed.
- Design-decision evidence: `Batch` is distinct public class with API parity; role filtering, copy semantics, and public `FieldRequirement` declaration shape match planning.
- Example/demo evidence: BVP target and sample contract examples are executable.
- Documentation evidence: docstrings explain mutable default and explicit copy behavior.
- Scientific contract evidence: `SampleContract` only checks presence, expected payload type, and schema; no hidden shape/unit/sample-rate validation or IO behavior.

### Phase Workflow State

- Phase execution plan: covered by approved implementation plan and Phase 3 PR body.
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: standard
- Blocker-resolution budget: return to planning if approved accessor return shapes or contract declaration shapes need redesign.
- Pre-submit blocker gate: no collation behavior, no IO refs, no rich scientific schema checks.
- Merge record: PR [#12](https://github.com/samcantrill/rphys/pull/12), squash merge `456d150`.

### Risks And Stop Conditions

- Risks: container API breadth may create edge cases around wrapping and copying; public `FieldRequirement` records become a compatibility surface; later method typing may need an additive common protocol.
- Stop conditions: implementation requires persistence, lazy loading, or shape/unit validation.
- Assumptions: `role()` returning a read-only shallow mapping, `require()` returning payloads, and public `FieldRequirement` records are approved.

### Completion Summary

- Implementation: complete; added `Sample`, `Batch`, private field-entry storage, read-only role views, `FieldRequirement`, and `SampleContract`.
- Validation: `make test-unit`, `make test-contract`, `make test-package`, `make validate-pr`, and `git diff --check` passed in the phase worktree.
- PR: [#12](https://github.com/samcantrill/rphys/pull/12).
- Merge: squash merged to `develop` as `456d150`.
- Follow-up: none for Phase 3 scope.

## Phase 4: LIST Collation

Status: merged
Slug: `list-collation`
Branch: `agent/stage-2-p4-list-collation`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-2-p4-list-collation`
PR: [#13](https://github.com/samcantrill/rphys/pull/13)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement deterministic, fail-loud LIST-only collation into `Batch`.
- Files/modules owned: `src/rphys/data/collation.py`; `src/rphys/data/__init__.py`; `tests/unit/rphys/data/test_collation.py`; contract tests; optional narrow integration test.
- Behavior implemented: `CollatePolicy.LIST`, `CollateContext`, and `collate_samples`.
- Decisions applied: DD-1, DD-4, DD-10, DD-11, DD-12.
- Examples or demos covered: homogeneous samples with explicit LIST policy collate to lists; absent/unsupported policy, inconsistent fields, missing fields, and schema mismatches fail.
- Out of scope: stack, padding, allow-missing, drop-if-missing, custom callable policies, object-delegated collation.
- Dependencies: Phases 1 and 3.

### Tasks

- Implement `CollatePolicy` with public LIST enum identity/name/value behavior.
- Implement minimal `CollateContext` without policy overrides.
- Implement `collate_samples` requiring non-empty homogeneous samples, explicit LIST policy, matching schemas, and deterministic metadata-key union with sample-order-aligned `None` for missing values.
- Add unit, contract, and optional integration tests.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Verify collation behavior and errors. | yes |
| `make test-contract` | Verify public collation examples. | yes |
| `make test-integration` if integration test is added | Verify sample-to-batch integration. | yes |
| `make test-package` | Verify imports and lightweight boundaries. | yes |
| `git diff --check` | Patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: LIST collates payloads and metadata deterministically under the approved DD-12 semantics; invalid cases fail loudly.
- Design-decision evidence: no stack/pad/custom behavior appears.
- Example/demo evidence: homogeneous sample collation and unsupported policy rejection are covered.
- Documentation evidence: docstrings state LIST-only scope and deferred policies.
- Scientific contract evidence: no hidden padding, truncation, or shape interpretation.

### Phase Workflow State

- Phase execution plan: covered by approved implementation plan and Phase 4 PR body.
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: standard
- Blocker-resolution budget: return to planning if metadata collation semantics are rejected.
- Pre-submit blocker gate: no stack/pad/missing/custom policy implementation.
- Merge record: PR [#13](https://github.com/samcantrill/rphys/pull/13), squash merge `f9fd766`.

### Risks And Stop Conditions

- Risks: metadata union ordering and missing metadata behavior need careful tests.
- Stop conditions: implementation requires shape inspection, padding, stacking, or callable policy dispatch.
- Assumptions: minimal `CollateContext` without policy overrides is approved; LIST metadata uses deterministic key union with sample-order-aligned `None` for missing values.

### Completion Summary

- Implementation: complete; added `CollatePolicy.LIST`, minimal `CollateContext`, LIST-only `collate_samples`, missing-aware metadata rendering, contract coverage, and a narrow integration test.
- Validation: `make test-unit`, `make test-contract`, `make test-integration`, `make test-package`, `make validate-pr`, and `git diff --check` passed in the phase worktree.
- PR: [#13](https://github.com/samcantrill/rphys/pull/13).
- Merge: squash merged to `develop` as `f9fd766`.
- Follow-up: none for Phase 4 scope.

## Phase 5: Runtime Core Hardening

Status: merged
Slug: `runtime-core-hardening`
Branch: `agent/stage-2-p5-runtime-core-hardening`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-2-p5-runtime-core-hardening`
PR: [#14](https://github.com/samcantrill/rphys/pull/14)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: align public exports, docs, contracts, and validation evidence after behavior phases.
- Files/modules owned: `src/rphys/data/__init__.py`; `tests/package/`; `tests/contracts/`; docstrings; docs updates if needed; cross-phase fixes only.
- Behavior implemented: no new runtime behavior except approved cross-phase consistency fixes.
- Decisions applied: DD-1 through DD-12.
- Examples or demos covered: all Stage 2 examples from planning.
- Out of scope: new features, additional collation policies, IO/datasource/ops/model behavior.
- Dependencies: Phases 1-4.

### Tasks

- Finalize `rphys.data.__all__` and package import tests.
- Add or refine contract tests for documented public runtime examples.
- Review docstrings for scientific contract clarity and explicit deferrals.
- Run full relevant validation and record evidence in the PR/merge record.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Full unit coverage for Stage 2 modules. | yes |
| `make test-package` | Public imports and lightweight dependency boundary. | yes |
| `make test-contract` | Public runtime contract examples. | yes |
| `make test-integration` if integration tests exist | Cross-module runtime behavior. | yes when present |
| `uv lock --check` | Lockfile unchanged/valid. | yes |
| `git diff --check` | Patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: all Stage 2 tests pass.
- Design-decision evidence: public imports and deferrals match planning.
- Example/demo evidence: all planning examples are covered by tests or docstrings.
- Documentation evidence: public docstrings explain units/schemas only where Stage 2 owns semantics and explicitly defer richer scientific validation.
- Scientific contract evidence: no hidden padding, stacking, serialization, IO, or backend dependency appears.

### Phase Workflow State

- Phase execution plan: covered by approved implementation plan and this hardening PR.
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: standard
- Blocker-resolution budget: return to planning for public-surface changes outside approved baseline.
- Pre-submit blocker gate: no unapproved new behavior.
- Merge record: PR [#14](https://github.com/samcantrill/rphys/pull/14), squash merge `b86a94f8ddebaf95ca39d43bf42818dd6226e6a2`.

### Risks And Stop Conditions

- Risks: hardening may reveal earlier phase inconsistency around exports or contract tests.
- Stop conditions: final validation exposes a design conflict requiring maintainer decision.
- Assumptions: earlier phases preserve approved boundaries.

### Completion Summary

- Implementation: complete; records phase PR sequence, validates final public runtime surface, and preserves scope deferrals.
- Validation: `make test-unit`, `make test-package`, `make test-contract`, `make test-integration`, `make validate-pr`, and `git diff --check` passed in the phase worktree.
- PR: [#14](https://github.com/samcantrill/rphys/pull/14).
- Merge: squash merged to `develop` on 2026-05-12 as `b86a94f8ddebaf95ca39d43bf42818dd6226e6a2`.
- Follow-up: collate-policy normalization test hardening was merged through PR [#15](https://github.com/samcantrill/rphys/pull/15) as `8e0c847a0eafe45663b68729e9e3cef25aaf5cf4`.

## Cross-Phase Validation

- Full relevant test command: `make test-unit && make test-package && make test-contract`
- Docs/template checks: docstring review, `git diff --check`
- Scientific/workflow contract checks: verify no IO refs, datasource scanning, operation/model/training behavior, workflow/artifact runtime, stack/pad collation, or optional backend import enters `rphys.data`.
- Example/demo checks: loaded field example, sample target access, sample contract validation, LIST collation, rejected implicit collation, synthetic data-object traversal, and synthetic composite data-object traversal.
- Manual review focus: public import surface, copy/equality semantics, typed diagnostics context, metadata collation behavior, and deferral boundaries.

## Implementation Completion Evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Phase 1 PR | merged | [#10](https://github.com/samcantrill/rphys/pull/10), squash merge `8a9c040` |
| Phase 2 PR | merged | [#11](https://github.com/samcantrill/rphys/pull/11), squash merge `13c3cae` |
| Phase 3 PR | merged | [#12](https://github.com/samcantrill/rphys/pull/12), squash merge `456d150` |
| Phase 4 PR | merged | [#13](https://github.com/samcantrill/rphys/pull/13), squash merge `f9fd766` |
| Phase 5 PR | merged | [#14](https://github.com/samcantrill/rphys/pull/14), squash merge `b86a94f8ddebaf95ca39d43bf42818dd6226e6a2` |
| Collate-policy test hardening PR | merged | [#15](https://github.com/samcantrill/rphys/pull/15), squash merge `8e0c847a0eafe45663b68729e9e3cef25aaf5cf4` |
| `make test-unit` | passed | 186 passed |
| `make test-package` | passed | 13 passed |
| `make test-contract` | passed | 12 passed |
| `make test-integration` | passed | 1 passed |
| `uv lock --check` | passed | included in `make validate-pr` |
| `make validate-pr` | passed | summary generation, build, and diff check completed |
| `git diff --check` | passed | no whitespace errors |

Notes:

- Phases 1 through 5 were implemented in dedicated worktrees and merged through separate PRs to `develop`.
- PR [#15](https://github.com/samcantrill/rphys/pull/15) preserved the relevant follow-up test-hardening evidence for collate-policy normalization.
- Phase 5 records the final phase evidence and reran the full Stage 2 validation gate.
- No optional backend, IO, datasource, operation, model, training, serialization, stack, or pad behavior was added.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| Implementation plan is approved for execution. | resolved | Maintainer approved phase execution after the final specialist design-analysis pass found no new blocker. | resolved |
| Stage 1 current worktree is dirty and may be incomplete locally. | concern | Treat Stage 1 as completed per maintainer instruction; implementation should verify required imports before Phase 1. | recorded |
| Collation metadata semantics carry scientific/provenance risk. | concern | Keep LIST-only, explicit policy, deterministic metadata-key union, sample-order alignment, explicit `None` sentinels for missing keys, and no shape/pad behavior. | recorded |

Gate result:

- Status: approved for execution.
- Review evidence: plan traces to the approved Stage 2 baseline in `docs/roadmap/stage-2/planning.md`.
- Accepted risks: `DataObjectBase`, `CompositeDataObjectBase`, public `FieldRequirement`, `CollateContext`, and LIST metadata semantics may need additive refinement in later stages.
- Revisit triggers: maintainer changes public export policy, container API return shapes, data-object hook shape, or later milestones require stricter provenance semantics than LIST provides.

## Final Approval

- Approval status: complete; implementation merged through PRs [#10](https://github.com/samcantrill/rphys/pull/10)-[#15](https://github.com/samcantrill/rphys/pull/15).
- Approved scope: Milestone 2 runtime core as defined by Phases 1-5 in this plan.
- Accepted risks: `DataObjectBase`, `CompositeDataObjectBase`, public `FieldRequirement`, `CollateContext`, and LIST metadata semantics may need additive refinement in later stages; LIST provenance strictness should expand via a new policy rather than reinterpretation of existing LIST behavior.
- Deferred items: serialization, IO/lazy refs, datasource scans, operations/transforms, method/model/loss/metric behavior, training/evaluation/analysis, stack/pad/custom collation, optional backend helpers, rich scientific schema validation, and workflow/artifact runtime.
