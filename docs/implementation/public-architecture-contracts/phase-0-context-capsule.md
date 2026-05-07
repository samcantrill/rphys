# Phase 0 Context Capsule: Public Architecture Contracts

Status: complete
Roadmap item: `Public architecture contracts`
Roadmap slug: `public-architecture-contracts`
Planning notes: `docs/implementation/public-architecture-contracts/planning-notes.md`
Master plan: `docs/implementation/public-architecture-contracts/master-plan.md`
Quality gate: passed; maintainer accepted Stage 1 and Stage 2

## Purpose

Create the Stage 3 handoff context for four implementation phases that establish the first public architecture contract for `rphys`. This package is structural and policy-focused: docs first, uv/tooling second, importable package and broad errors third, persistent validation fourth.

## Accepted Decisions

- Stable public API design is the highest priority.
- Lock module homes before concrete class or function signatures.
- API labels are exactly `stable`, `provisional`, and `private/internal`.
- First stable wave is `rphys.data`, `rphys.io`, `rphys.datasets`, `rphys.transforms`, plus `rphys.errors`.
- Do not create initial homes for `methods`, `training`, `losses`, `evaluation`, `analysis`, `recipes`, `stages`, `ops`, `models`, or `testing`.
- `FieldRef`, `TemporalIndexSlice`, and `FieldView` are future `rphys.io` concepts, not `rphys.data` concepts.
- Root error is `RemotePhysError`.
- Code becomes the contract after implementation; docs should document policy, rationale, and links to code-backed API details, not duplicate signatures.
- `_target_` import paths are the default extension mechanism; generic instantiation belongs to `loom`.
- Registries are limited to symbolic names such as codec keys, built-in dataset names, standard field schemas, and later metric or recipe names.
- Python baseline is 3.12.
- Use uv with `pyproject.toml`, `.python-version`, committed `uv.lock`, and thin Makefile wrappers.
- `uv_build` backend is locked to `requires = ["uv_build>=0.11.6,<0.12"]` and `build-backend = "uv_build"`.
- No real license is selected. Keep all rights reserved, omit `license` and `license-files` metadata, and include classifier `Private :: Do Not Upload`.

## Phase Order

1. `contract-docs-and-policy`
2. `repository-tooling-scaffold`
3. `package-and-error-skeleton`
4. `contract-validation`

## Pathway Defaults

- Phase 1 is fast-path eligible only if it remains docs-only and does not reopen accepted design.
- Phase 2 should use the standard pathway because it changes repository tooling, package metadata, dependency workflow, and rights metadata.
- Phase 3 should use the standard pathway because it creates public import homes and broad public errors.
- Phase 4 is fast-path eligible only if it remains tests/checks-only except for narrowly scoped blocker fixes.

## Hard Stops

- Changing accepted module ownership.
- Adding stable placeholder domain classes.
- Adding future module homes early.
- Adding generic workflow, config, execution, store, resume, locking, resource, registry, plugin-discovery, or `_target_` instantiation machinery to `rphys`.
- Requiring `loom` to depend on `rphys`.
- Adding heavy optional stacks to base imports or base dependencies.
- Adding real license metadata or public license terms.
- Renaming `RemotePhysError`.
- Treating `NotImplementedError` placeholders as stable API.

## Dependency And API Boundaries

- `rphys` may depend on `loom`; `loom` must not depend on `rphys`.
- Base imports must avoid torch, video, signal, training, and analysis stacks.
- Published extras are future user-facing categories: `video`, `signal`, `torch`, `training`, and `analysis`.
- uv dependency groups are local-only groups such as `dev`, `test`, `lint`, and `docs`.
- `[project.dependencies]` stays empty or minimal until concrete runtime code needs a dependency.

## Validation Obligations

- `git diff --check` for every phase.
- `uv sync` once tooling exists.
- `uv lock --check` once `uv.lock` exists.
- Focused import checks for `rphys`, `rphys.errors`, `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`.
- Error hierarchy tests for broad `RemotePhys*Error` classes.
- Docs-policy checks for API labels, boundary policy, extension policy, registry policy, uv/dependency policy, Python 3.12 baseline, code-backed docs policy, and temporary rights status.
- Boundary/search checks showing no generic workflow infrastructure was added to `rphys`.
- Checks proving no stable placeholder runtime/domain exports exist.

## Current Preflight Risks

- `gh auth status` reports an invalid stored token for account `samcantrill`; PR creation and merge are blocked until re-authenticated with `gh auth login -h github.com`.
- Foreground branch is `main`, tracking `origin/main`, and is ahead by 1 commit.
- Dirty worktree includes `M docs/roadmap/index.md`, `D docs/rphys_revised_package_architecture.md`, `?? docs/implementation/`, and `?? docs/rphys_architecture_plan_v3.md`.
- Worktree root `/home/samcantrill/work/rphys-worktrees` exists and is writable.
- Other agents or the manager may own unrelated dirty changes. Stage 3 workers must not revert, overwrite, or normalize unrelated files.

## Playbook Outputs

- `docs/implementation/public-architecture-contracts/phase-1-contract-docs-and-policy/execution-playbook.md`
- `docs/implementation/public-architecture-contracts/phase-2-repository-tooling-scaffold/execution-playbook.md`
- `docs/implementation/public-architecture-contracts/phase-3-package-and-error-skeleton/execution-playbook.md`
- `docs/implementation/public-architecture-contracts/phase-4-contract-validation/execution-playbook.md`

## Missing Decisions

None blocking for Stage 3. Deferred decisions remain exact runtime signatures, exact optional dependency packages, plugin discovery, package-specific detailed errors, generated API docs tooling, and final project license.
