# rphys Scaffold Roadmap

This roadmap is the canonical planning document for scaffold work in `rphys`. Roadmap items are work packages: coherent capabilities such as package layout, validation infrastructure, documentation structure, CI, extension points, and reusable project conventions.

Stage 1 keeps this file current while uploaded project context and maintainer discussion are converted into accepted work packages. Stage 2 turns one accepted work package into a master implementation plan. Stage 3 implements the accepted plan through managed worktree phases.

## Status Values

- `draft`: under discussion during Stage 1.
- `accepted`: accepted as a scaffold work package and ready for Stage 2.
- `planning`: master implementation plan is being drafted or reviewed.
- `implementing`: phase PRs are active.
- `reviewing`: implementation is in automated review, fast-path checklist, or merge checks.
- `merged`: accepted into `main`.
- `deferred`: valid but intentionally postponed.
- `dropped`: not planned for the modern library.

## Work Packages

| Work Package | Status | Context Evidence | Target Direction | Validation Needs | Implementation |
| --- | --- | --- | --- | --- | --- |
| Workflow automation scaffold | draft | Initial maintainer workflow discussion | Three-stage roadmap, master-plan, and implementation workflow with durable agent handoffs | Link/reference checks, TOML validation, stale-workflow search | Pending |
| Public architecture contracts | merged | `docs/rphys_architecture_plan_v3.md`; split from `docs/implementation/00-field-centric-architecture-scaffold/planning-notes.md`; maintainer accepted Stage 1 and Stage 2 scope | Establish the `loom`/`rphys` boundary, API stability labels, first stable module wave (`data`, `io`, `datasets`, `transforms`), central `RemotePhys*Error` hierarchy, uv/Python 3.12 project tooling, temporary all-rights-reserved placeholder, registry policy, dependency boundaries, and future/provisional module map | Import smoke tests, public API inventory checks, uv lock checks, dependency-boundary checks, docs link checks, stale generic-infrastructure search, architecture/refactor-risk criteria in the master plan | Implemented on `main`/`origin/main` in commits `ac1ed54`, `fba9ecb`, `95e57f7`, and `83b9e4c`; closeout validation passed on 2026-05-08 and is recorded in `docs/implementation/01-public-architecture-contracts/implementation-plan.md` |
| Field runtime core | reviewing | `docs/rphys_architecture_plan_v3.md` sections 8-15; split planning notes | Implement the field-centric runtime model: `DataKey`, `FieldSpec`, `FieldValue`, typed data object base, `Sample`, `Batch`, field metadata, mutability rules, and explicit collation behavior | Unit tests for key parsing, field wrappers, Sample/Batch access and mutation, data object tensor traversal, strict collation, padding/missing-field failures, and metadata collation | Planning notes: `docs/implementation/02-field-runtime-core/planning-notes.md`; accepted master plan: `docs/implementation/02-field-runtime-core/master-plan.md`; implementation ledger: `docs/implementation/02-field-runtime-core/implementation-plan.md`; Phase 1 PR open; merge pending |
| Dataset IO and index core | planning | `docs/rphys_architecture_plan_v3.md` sections 16-20; split planning notes; F1 intent/functionality approved on 2026-05-08 | Implement `DatasetRef`, `RecordRef`, `FieldRef`, `TemporalIndexSlice`, `FieldView`, `IndexItem`, `SampleSpec`, `SampleBuilder`, dataset filters, adapter protocol, codec protocol, and synthetic lazy-loading fixtures | Contract tests for unloaded refs/indexes, slice semantics, missing fields, unsupported slices, codec resolution, synthetic DatasetRef-to-SampleBuilder flow, and adapter schema validation | Planning notes: `docs/implementation/03-dataset-io-index-core/planning-notes.md`; master plan draft: `docs/implementation/03-dataset-io-index-core/master-plan.md`; pending design-decision classification review, design discussion, deep design review, and quality gate |
| Runtime transforms and materialization | draft | `docs/rphys_architecture_plan_v3.md` sections 21-26 and 33-35; split planning notes | Implement pure ops boundaries, `SampleTransform`, `SampleAugmentation`, `SampleCheck`, `SamplePipeline`, context/RNG behavior, `SampleExporter`, `MaterializationPipeline`, and thin materialization stage contracts | Transform contract tests, deterministic/stochastic reproducibility tests, no-hidden-IO checks, sample check behavior tests, synthetic export/materialization smoke tests, and field replacement/addition tests | Planning notes: `docs/implementation/04-runtime-transforms-materialization/planning-notes.md`; master plan pending acceptance |
| Learning evaluation core | draft | `docs/rphys_architecture_plan_v3.md` sections 27-32 and 42-46; split planning notes | Implement method/model/learner/trainer boundaries, input/target adapters, loss contracts, predictions as Samples/Batches, metrics, sample aggregation, metric aggregation, evaluation protocols, and minimal analysis report interfaces | Synthetic method prediction tests, learner/loss adapter tests, prediction-field contract tests, per-window and aggregate metric tests, evaluation protocol smoke tests, and optional torch-gated tests | Planning notes: `docs/implementation/05-learning-evaluation-core/planning-notes.md`; master plan pending acceptance |
| Extension docs and validation scaffold | draft | `docs/rphys_architecture_plan_v3.md` sections 36-41 and 49-52; split planning notes | Provide extension guides, recipe/stage documentation, synthetic fixtures, testing strategy, optional dependency documentation, and validation gates that teach users how to extend `rphys` without editing internals | Documentation link checks, guide example import checks, synthetic fixture coverage, recipe/config validation, optional dependency import-boundary checks, and extension anti-pattern checks | Planning notes: `docs/implementation/06-extension-docs-validation-scaffold/planning-notes.md`; master plan pending acceptance |

## Next Actions

1. Refresh GitHub CLI authentication with `gh auth login -h github.com` before future PR-based implementation phases.
2. Keep temporary rights status as all rights reserved until a real license is selected later.
3. Keep the remaining draft work packages in Stage 1 until their own behavior/design reviews are accepted.
