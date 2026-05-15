# Phase 7 Execution Plan: Docs, Examples, And Final Validation Evidence

## Metadata

- Status: draft phase execution plan; ready for implementation
- Roadmap stage: `v7`
- Feature focus: Stage-wide documentation alignment and validation evidence for sample and batch operations
- Stage descriptor: SampleOps, BatchOps, Transforms, Augmentations, Checks, And Pipelines
- Phase descriptor: Docs, Examples, And Final Validation Evidence
- PR title: `Stage 7 SampleOps, BatchOps, Transforms, Augmentations, Checks, And Pipelines - Phase 7: Docs, Examples, And Final Validation Evidence`
- Branch: `agent/stage-7-p7-docs-validation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p7-docs-validation`
- Phase execution plan path: `docs/roadmap/stage-7/phases/docs-validation.md`
- Full plan: `docs/roadmap/stage-7/implementation-plan.md`
- Planning document: `docs/roadmap/stage-7/planning.md`
- Source phase: Phase 7, `docs-validation`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after local validation, automated review, and PR checks or explicit no-checks evidence
- Workflow path: fast path unless broad validation exposes behavior gaps
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`
- Plan quality gate: Stage 7 implementation plan is approved and Phases 1 through 6 are merged into the current base
- Draft pass: completed 2026-05-15
- Refine pass: not needed before implementation
- Setup limitations: no broad validation, PR body, PR, or GitHub operation was run during this planning pass
- Blockers: none before implementation

## Objective

Close Stage 7 by aligning public prose, glossary wording, and operation docstrings with the code-backed sample and batch operation surface, then run the broad validation commands and record exact evidence without adding new operation behavior.

## Full-Plan Context

Phases 1 through 6 implemented the operation-step foundation, sample operation contracts, field-effect enforcement, deterministic checks, augmentation replay, sample pipelines, and the provisional batch operation surface. Phase 7 must document those merged contracts and accepted deferrals, not add a new API layer.

Future work that must remain out of scope includes export/save/materialization, cache identity, datasource scanning changes, DataLoader adapters, trainer/device movement, model formatting, broad batch planning, concrete rPPG kernels, root `rphys` exports, shorthand public aliases, registries, and workflow/artifact runtime behavior.

## Source Phase Summary

- Goal: align public documentation, examples, and validation evidence with implemented Stage 7 behavior and accepted deferrals.
- Required scope: public docstrings, README/roadmap/glossary wording where stale, phase evidence notes, PR body, and validation evidence.
- Required checkpoints: `make test`, `make test-summary`, `make test-package`, `make test-unit`, `make test-contract`, `make test-integration`, `uv lock --check`, `git diff --check`, and `make validate-pr` when practical.
- Acceptance criteria: docs and examples use public APIs only, preserve full public names, label batch behavior as provisional, document replay/mutation/lazy boundaries, and avoid private helper or future-stage ownership.

## Current Source And Harness Findings

- `README.md` still describes datasource discovery and operations as future work even though Stages 5 through 7 have landed.
- `docs/roadmap.md` Milestone 7 still lists shorthand names such as `SampleOp`, `BatchOp`, `SampleContext`, and `AugmentationParams`; Stage 7 planning approved full public names.
- `docs/GLOSSARY.md` contains a shorthand `SampleOp` row but not the code-backed `SampleOperation`, `BatchOperation`, operation-step, pipeline, replay, and equivalence terms.
- `src/rphys/ops/pipelines.py` still has a Stage 6-only module docstring despite now owning `SampleOperationPipeline` and `BatchOperationPipeline`.
- `src/rphys/ops/sample.py` and `src/rphys/ops/batch.py` have mostly accurate public docstrings; targeted additions can make replay, field-effect, provisional batch, and dtype/device limits more explicit.
- Existing package, unit, contract, and integration tests cover the public operation names, no root exports, lazy field behavior, augmentation replay metadata, pipeline ordering, and batch equivalence metadata.

## Phase Isolation State

- Control checkout dirty-state review: the control checkout has unrelated untracked `docs/roadmap/stage-8/`; Phase 7 must not touch it.
- Dedicated branch/worktree status: `agent/stage-7-p7-docs-validation` is checked out at `/home/samcantrill/work/rphys-worktrees/stage-7-p7-docs-validation`.
- Current `develop` base: `1f84e37` (`docs: record stage 7 phase 6 merge`).
- Earlier phase dependency status: Phases 1 through 6 are merged and recorded in `develop`.
- Push/PR infrastructure status: not exercised yet for Phase 7.
- Stop condition if isolation cannot be maintained: stop before implementation if the branch leaves the dedicated worktree, if `develop` advances with conflicting Stage 7 changes, or if validation exposes a behavior gap requiring an owning-phase fix.

## In-Scope Work

- Update README status to mention the code-backed Stage 5 through Stage 7 surfaces without turning it into a tutorial.
- Update Milestone 7 roadmap key interfaces to full public names and explicitly treat `SampleOp`/`BatchOp` as roadmap shorthand.
- Update glossary entries for full Stage 7 operation vocabulary and boundaries.
- Tighten public operation module docstrings where they are stale or under-specific.
- Record Phase 7 validation evidence and residual risks in this phase artifact and the implementation plan.
- Prepare a Phase 7 PR body artifact.

## Out-of-Scope Work

- New public classes, errors, aliases, re-exports, registries, convenience factories, or root `rphys` exports.
- Source behavior changes to operations, pipelines, containers, collators, codecs, datasources, loaders, exporters, trainers, or models.
- New examples that depend on private helpers, raw datasets, heavy optional stacks, real devices, or downstream workflows.
- Rewriting approved planning decisions or changing workflow templates.

## Assumptions

- Stage 7 behavior is already code-backed by Phases 1 through 6.
- Documentation-only changes do not require new tests unless they reveal a public-surface or import-boundary gap.
- `make validate-pr` is practical because earlier phases have already built locally in this environment.

## Scope Contract

Phase 7 has no public behavior changes. It documents the current contract: users import Stage 7 names from `rphys.ops` or scoped `rphys.ops.sample`/`rphys.ops.batch` modules; `OperationStep` is the shared execution protocol; ordinary user functions are wrapped by callable-first `Operation`, `SampleOperation`, `SampleTransform`, `SampleAugmentation`, `SampleCheck`, `BatchOperation`, `BatchTransform`, or `BatchAugmentation`; specialized pipelines preserve sequence or insertion-ordered mapping order and use mapping keys for diagnostics only.

Sample operations enforce declared field additions, replacements, and deletions through field inventory snapshots, but they do not transparently track reads or payload-internal mutation. Lazy fields load only when operation code accesses payload data. Replay records and augmentation params are runtime evidence, not cache/export schemas. Batch operations are provisional optimization contracts; dtype/device are descriptive strings, equivalence reports are metadata evidence, and batch code does not allocate arrays, move devices, build loaders, export fields, or define model layouts.

## Scientific Contract Notes

- Sampling and temporal alignment: no new sampling, resampling, padding, masking, or temporal slicing policy is added; augmentation replay records only runtime seed/context evidence.
- Field roles, locators, schemas, and provenance: docs must describe parsed `FieldLocator` permissions, runtime provenance mappings, and field-effect metadata without making locators own mutation or routing policy.
- Masking, filtering, normalization, and aggregation order: no concrete signal-processing algorithm, normalization policy, or aggregate metric is introduced.
- Subject identity, splits, leakage, and grouping: docs must keep datasource filters, split construction, loader drop policy, and trainer routing separate from `SampleCheck`/`SampleRoute` records.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: numeric edge-case behavior remains the responsibility of concrete future operations; Stage 7 documents typed failures for the implemented operation contracts.

## Design Impact

- Maintainability: clarifies the implemented Stage 7 surface and reduces future shorthand/full-name drift.
- Extensibility: preserves Stage 8/9/10 boundaries while leaving `OperationStep`, wrappers, and specialized pipelines reusable.
- Lightweight import policy: documentation must not suggest heavy backend imports or hidden device movement in core operation imports.
- Source-tree boundaries: expected edits are README, roadmap/glossary prose, operation docstrings, and Stage 7 evidence artifacts only.

## Future Compatibility

- Stage 8 can add export/save operations without treating replay metadata or field-effect metadata as export schemas.
- Stage 9 can add loader/cache/materialization adapters without changing operation context records into durable cache identities.
- Later batch planning and model/method stages can consume `BatchOperation` equivalence metadata without making Stage 7 a backend or device policy layer.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add shorthand public aliases such as `SampleOp` or `BatchOp` | Maintainer guidance chose full code-facing public names; shorthand stays roadmap prose only. |
| Turn Phase 7 into a tutorial/examples expansion | The phase owns contract alignment and validation evidence, not broad user education. |
| Add extra automated docs tests for this wording pass | Existing package/contract tests already guard the public names; docs changes do not introduce executable behavior. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Stage 7 docs remain concise rather than full user-guide material | The repository roadmap remains the canonical architecture policy and detailed tutorials are premature before export/loading stages. | Downstream users begin consuming the API and need task-oriented examples. |
| Batch equivalence documentation remains descriptive | Stage 7 intentionally avoids heavy numeric backends and fused kernels. | A future batch planner or concrete batch kernel needs stricter numeric proof records. |

## Reviewability

- Expected PR size and shape: small documentation/docstring/evidence PR with no behavior changes.
- Files and areas to inspect: `README.md`, `docs/GLOSSARY.md`, `docs/roadmap.md`, `src/rphys/ops/__init__.py`, `src/rphys/ops/sample.py`, `src/rphys/ops/batch.py`, `src/rphys/ops/pipelines.py`, Stage 7 implementation and phase artifacts.
- Scope-control checks: no new public exports, no source behavior changes, no private helper docs, no root exports, no heavy imports, and no future-stage ownership.

## Implementation Steps

1. Patch stale public prose and operation docstrings to match code-backed Stage 7 behavior.
2. Review changed docs for private helper leakage and future-stage overreach.
3. Run required validation commands and record exact results.
4. Prepare the Phase 7 PR body and update implementation-plan completion notes.
5. Open, review, merge, and record the Phase 7 PR.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package`
- Required assertions or deferral reason: public exports/import boundaries remain exact and lightweight.

### Unit Suite

- Status: required
- Expected paths: `tests/unit`
- Required assertions or deferral reason: Stage 7 operation behavior remains unchanged.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts`
- Required assertions or deferral reason: public operation, sample, pipeline, and batch contracts remain intact.

### Integration Suite

- Status: required
- Expected paths: `tests/integration`
- Required assertions or deferral reason: lazy sample, augmentation, and batch examples remain code-backed.

### E2E Suite

- Status: deferred/not present
- Expected paths: `tests/e2e`
- Required assertions or deferral reason: no e2e suite exists for Stage 7.

### Acceptance Suite

- Status: deferred/not present
- Markers affected: none
- Required assertions or deferral reason: no acceptance suite exists for Stage 7.

## Risks

- Broad validation may reveal a real earlier-phase behavior gap.
- Documentation can accidentally imply export/cache/loader/trainer ownership.
- Shorthand roadmap terms can drift back into public API wording.

## Completion Notes

- Implementation summary: pending
- Validation: pending
- PR: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none before implementation
