# Phase 0 Preflight: Public Architecture Contracts

Status: complete
Roadmap slug: `public-architecture-contracts`
Checked from: `/home/samcantrill/work/rphys`
Workflow step: Stage 3 Phase 0 playbook creation

## Source Artifacts

- `AGENTS.md`
- `.codex/workflows/README.md`
- `.codex/workflows/stage-3-managed-implementation.md`
- `.codex/templates/execution-playbook.md`
- `docs/roadmap/index.md`
- `docs/implementation/public-architecture-contracts/planning-notes.md`
- `docs/implementation/public-architecture-contracts/master-plan.md`
- `docs/implementation/public-architecture-contracts/architecture-refactor-risk-review.md`
- `docs/implementation/public-architecture-contracts/master-plan-review-initial.md`
- `docs/implementation/public-architecture-contracts/master-plan-quality-refinement-summary.md`
- `docs/implementation/public-architecture-contracts/master-plan-review-confirmation.md`

## Gate Status

- Stage 1 planning notes: accepted.
- Stage 2 master plan: accepted.
- Master-plan quality gate: passed.
- Architecture refactor-risk review: passed with accepted risks and no blocking findings.
- Current Stage 3 step: Phase 0 playbook creation.

## Repository Status

- Foreground checkout: `/home/samcantrill/work/rphys`.
- Branch: `main`.
- Upstream: `origin/main`.
- Branch status: ahead by 1 commit.
- Dirty status observed:
  - `M docs/roadmap/index.md`
  - `D docs/rphys_revised_package_architecture.md`
  - `?? docs/implementation/`
  - `?? docs/rphys_architecture_plan_v3.md`
- Worktree root: `/home/samcantrill/work/rphys-worktrees`.
- Worktree root write access: available.

## GitHub Auth

`gh auth status` reports an invalid token for account `samcantrill`:

- Active account exists.
- Token in `/home/samcantrill/.config/gh/hosts.yml` is invalid.
- Re-authentication command is `gh auth login -h github.com`.

Impact: implementation branches and local worktrees can be prepared, but PR creation, PR monitoring, auto-merge, branch cleanup through GitHub, and any `gh`-dependent Stage 3 merge flow are blocked until authentication is repaired.

## Phase Ownership Summary

| Phase | Slug | Primary files |
| --- | --- | --- |
| 1 | `contract-docs-and-policy` | `docs/architecture/public-contracts.md`, optional `README.md` link, optional roadmap implementation note |
| 2 | `repository-tooling-scaffold` | `pyproject.toml`, `.python-version`, `uv.lock`, `Makefile`, `CONTRIBUTING.md`, temporary `LICENSE` placeholder |
| 3 | `package-and-error-skeleton` | `src/rphys/__init__.py`, `src/rphys/errors.py`, `src/rphys/data/__init__.py`, `src/rphys/io/__init__.py`, `src/rphys/datasets/__init__.py`, `src/rphys/transforms/__init__.py` |
| 4 | `contract-validation` | `tests/test_public_imports.py`, `tests/test_error_hierarchy.py`, `tests/test_public_contract_docs.py`, `tests/test_dependency_boundaries.py` |

## Current Findings

- No implementation code or tooling should be created during Phase 0.
- The target Phase 0 outputs are docs-only under `docs/implementation/public-architecture-contracts/`.
- Phase 0 must not change unrelated dirty files.
- The quality gate artifacts are sufficient for playbook creation.
- The GitHub auth blocker must be carried into relevant phase stop conditions because Stage 3 requires PR creation and merge.

## Stop Conditions

- Stop before opening PRs or attempting merge while `gh auth status` reports the invalid token.
- Stop if `main` changes in a way that invalidates the accepted master plan or quality gate.
- Stop if another active worker owns overlapping files for the same phase.
- Stop if a phase needs to change accepted decisions instead of implementing the accepted plan.
- Stop if the dirty worktree includes unrelated changes in a file a phase must edit and those changes cannot be preserved safely.

## Completion Notes

- Phase 0 produced four execution playbooks for the accepted implementation phases.
- No missing Stage 3 design decision blocks phase implementation planning.
- Re-authentication remains the only known preflight blocker for autonomous PR creation and merge.
