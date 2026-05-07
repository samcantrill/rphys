# Execution Playbook: Public Architecture Contracts Phase 2 Repository Tooling Scaffold

Status: ready for phase implementation planning
Master plan: `docs/implementation/public-architecture-contracts/master-plan.md`
Roadmap item: `docs/roadmap/index.md`
Branch: `agent/public-architecture-contracts-p2-repository-tooling-scaffold`
Worktree: `../rphys-worktrees/public-architecture-contracts-p2-repository-tooling-scaffold`
Phase notes: `docs/implementation/public-architecture-contracts/phase-2-repository-tooling-scaffold/phase-notes.md`
Public PR body: `docs/implementation/public-architecture-contracts/phase-2-repository-tooling-scaffold/pr-body.md`
Quality gate: Stage 1 accepted; Stage 2 accepted; master-plan quality gate passed
Blockers: GitHub auth is invalid for `samcantrill`, blocking PR creation and merge until re-authenticated

## Compact Context Capsule

Goal: establish uv-managed package metadata, Python 3.12 baseline, command wrappers, contributor guidance, and temporary all-rights-reserved status before package code and tests depend on repository tooling.

Accepted decisions: use uv, `pyproject.toml`, `.python-version`, committed `uv.lock`, thin Makefile wrappers, Python 3.12, exact `uv_build` backend metadata, no real license metadata, and exact classifier `Private :: Do Not Upload`.

Constraints: do not add package module code, persistent tests, CI workflows, heavy optional stacks, real public license terms, or future module homes.

## Ownership

- Files/modules owned by this phase:
  - `pyproject.toml`
  - `.python-version`
  - `uv.lock`
  - `Makefile`
  - `CONTRIBUTING.md`
  - `LICENSE` temporary all-rights-reserved placeholder
- Files/modules explicitly out of scope:
  - `src/rphys/**`
  - `tests/**`
  - `docs/architecture/public-contracts.md` except for narrow link fixes requested by the manager
  - CI workflows, release automation, docs site config, pre-commit config
- Public interfaces allowed to change:
  - Repository command surface through Makefile wrappers.
  - Project metadata and dependency management.
  - No Python runtime API.
- Other active branches/worktrees to avoid:
  - Phase 1 docs branch/worktree.
  - Phase 3 package skeleton branch/worktree.
  - Phase 4 validation branch/worktree.

## Current Source And Harness Findings

- Existing files that constrain this phase: master plan locks Python 3.12, uv, `uv_build`, no license metadata, and no-upload classifier.
- Existing tests or harness behavior: no durable test harness exists yet. This phase creates the project environment that Phase 3 and Phase 4 use.
- Import-boundary or dependency constraints: `[project.dependencies]` stays empty or minimal; base install must not pull torch, video, signal, training, or analysis stacks.
- Scientific contract constraints: `CONTRIBUTING.md` must carry AGENTS.md expectations for scientific contracts and the no-raw-datasets rule.
- GitHub status: `gh auth status` reports an invalid token for `samcantrill`; local validation can run, but PR creation and merge are blocked.

## Scope Contract

This phase creates repository tooling only. It must:

- Use `requires-python = ">=3.12"` and `.python-version` value `3.12`.
- Use build system:
  - `requires = ["uv_build>=0.11.6,<0.12"]`
  - `build-backend = "uv_build"`
- Keep `[project.dependencies]` empty or minimal.
- Use uv dependency groups for local-only tools.
- Avoid publishing empty user extras unless the implementation has a concrete reason accepted by the manager; planned extras remain categories.
- Omit `license` and `license-files` metadata.
- Include classifier `Private :: Do Not Upload`.
- Add a temporary all-rights-reserved `LICENSE` placeholder that grants no public permission.
- Keep Makefile targets thin wrappers around uv/git commands.

No package code, runtime behavior, public errors, tests, CI, or future module homes are in scope.

## Tasks

- Add `pyproject.toml` with project metadata, Python 3.12 floor, `uv_build`, private classifier, minimal base dependencies, and local dependency groups needed for later tests.
- Add `.python-version` with `3.12`.
- Run `uv lock` to create committed `uv.lock`.
- Run `uv sync` and `uv lock --check`.
- Add a Makefile with thin targets such as `sync`, `lock`, `lock-check`, `test`, `check`, and `diff-check`.
- Add `CONTRIBUTING.md` for uv setup, Makefile commands, dependency policy, API labels, scientific-contract expectations, no raw datasets, and temporary rights status.
- Add `LICENSE` as the temporary all-rights-reserved placeholder.
- Record validation evidence and any network/auth/tooling blockers in phase notes.

## Pathway Eligibility

- Recommended pathway: standard.
- Fast-path rationale, if applicable: not recommended. This phase changes package metadata, lockfile behavior, dependency workflow, command surface, and rights metadata.
- Criteria that would force standard pathway:
  - Already met by package/tooling changes.
  - Any dependency, release, rights, or command behavior change.

## Implementation Plan Output

- Detailed implementation plan path: `docs/implementation/public-architecture-contracts/phase-2-repository-tooling-scaffold/implementation-plan.md`
- Fast-path checklist path, if used: `docs/implementation/public-architecture-contracts/phase-2-repository-tooling-scaffold/fast-path-checklist.md`

## Expected Commits

- Planning/handoff documents.
- Tooling metadata and lockfile.
- Contributor guidance and temporary rights placeholder.
- Validation evidence and phase notes.
- Review fixes and cleanup.

## Design Impact

- Maintainability: makes uv and pyproject the single dependency and environment source of truth.
- Extensibility: leaves exact optional backend packages to future behavior packages while reserving user-facing categories.
- Scientific workflow safety: contributor docs preserve scientific contract and no-raw-datasets rules.
- Source-tree boundaries: root tooling only; no package runtime surface.

## Future Compatibility

Later package work can add concrete optional extras, dependency markers, CI, docs tooling, or packaging refinements without changing the baseline uv workflow. The placeholder license must be replaced only after an explicit maintainer license decision.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Raw pip/requirements as primary workflow | Maintainer accepted uv as the project workflow. |
| setup.py or setup.cfg | `pyproject.toml` with uv is the accepted source of truth. |
| Heavy base scientific dependencies | Base imports must remain lightweight. |
| Real open-source license metadata now | Maintainer has not selected a license. |
| Broad Makefile logic | Makefile must be a thin wrapper, not a second source of truth. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Exact optional dependency packages remain deferred | No concrete backend behavior exists yet | Implementing video, signal, torch, training, or analysis behavior |
| Temporary `LICENSE` placeholder | Maintainer deferred real license selection | Before publication, distribution, external reuse, or maintainer license decision |
| Initial local dependency groups may be minimal | Phase 4 determines exact validation needs | Adding lint/docs/CI commands |

## Reviewability

- Expected PR size and shape: root tooling and governance files plus lockfile.
- Files and areas to inspect: build backend strings, Python version, dependency groups, absence of license metadata, private classifier, Makefile wrapper behavior, and rights placeholder wording.
- Scope-control checks: reject package code, tests, CI workflows, heavy base dependencies, real license terms, or future module homes.

## Verification

- Phase-specific commands:
  - `uv sync`
  - `uv lock --check`
  - `make lock-check`
  - `git diff --check`
- Full-suite command:
  - Not required before package tests exist; if `make test` or `uv run pytest` is wired and no tests exist, record the observed behavior.
- Expected evidence to record:
  - `uv sync` output.
  - `uv lock --check` output.
  - `make lock-check` output.
  - Manual review that `pyproject.toml` has no `license` or `license-files` metadata and contains `Private :: Do Not Upload`.
  - Manual review that base dependencies are empty or minimal.

### Suite Obligations

- Package: not required because package code has not landed.
- Unit: not required.
- Contract: manual metadata and rights-policy checks.
- Integration: uv environment sync and lock consistency.
- E2E: not required.
- Opt-in: not required.

## Review Focus

- Standard pathway code review: package metadata correctness, lockfile consistency, Makefile thinness, and no heavy base dependencies.
- Standard pathway scientific/workflow review: contributor docs preserve scientific-contract obligations and keep generic workflow infrastructure in `loom`.
- Fast-path manager checklist: not applicable unless the manager deliberately narrows the phase, which is not recommended.

## Stop Conditions

- GitHub auth remains invalid when PR creation or merge is required.
- `uv sync` or `uv lock --check` cannot succeed without choosing unaccepted dependencies or changing accepted Python/build backend policy.
- Implementing tooling requires package code, CI, pre-commit, generated docs tooling, or future module homes.
- Any real license metadata or public license terms would be needed.
- Network restrictions block required uv operations after an escalated retry or manager-approved workaround is unavailable.

## Budget Status

- Implementation blocker cycles used: 0 of 2.
- Code review: pending standard pathway.
- Scientific/workflow review: pending standard pathway.
- Fast-path checklist: not applicable by default.
- Pre-submit blocker gate: pending.

## Completion Notes

- Implementation summary: pending.
- Validation summary: pending.
- Review summary: pending.
- PR preparation: blocked until `gh auth status` succeeds.
- Merge and cleanup: pending.
- Remaining blockers: GitHub auth invalid for `samcantrill`.
