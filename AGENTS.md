# rphys Codex Instructions

## Project Purpose

`rphys` is a Python package for remote physiological measurement research. It should provide reusable, scientifically careful components for domain-specific datasets, preprocessing, models, training, evaluation, and analysis. Full research projects and heavy experiment workflows should live in downstream repositories; this repository should remain the base library.

## Core Engineering Rules

- Prefer clean modern APIs over direct preservation of legacy structure.
- Treat the legacy repository as evidence, not as the API contract.
- Preserve scientific meaning over superficial code parity.
- Keep code self-descriptive through names, types, docstrings, and tests.
- Add comments for complex research logic, especially where processing order affects interpretation.
- Do not introduce raw datasets into the repository. Use synthetic fixtures or tiny license-safe fixtures only.
- Keep public behavior documented in docs, tests, or docstrings before relying on it from downstream projects.

## Scientific Correctness

For preprocessing, signal processing, models, metrics, datasets, and analysis code, document the scientific contract:

- Inputs, outputs, units, shapes, dtypes, coordinate conventions, and sampling rates.
- Temporal alignment assumptions, windowing, resampling, filtering, masking, and interpolation behavior.
- Normalization order and whether statistics are per-sample, per-subject, per-video, per-dataset, or global.
- Leakage risks, train/test boundary assumptions, subject identity handling, and label availability.
- Failure behavior for NaNs, flat signals, short inputs, missing frames, empty masks, invalid sampling rates, and dtype/device mismatches.
- Mathematical operations in LaTeX notation where that improves clarity.
- Citations for domain algorithms, metrics, datasets, and non-obvious assumptions when relevant.

## Docstrings And Comments

Use a custom scientific docstring style. Borrow structure from NumPy or reST where useful, but do not treat either as mandatory.

Every public class/function should explain:

- What the object does and where it fits in the pipeline.
- Parameters, returns, shapes, units, dtype/device expectations, and optional behavior.
- Important equations, assumptions, side effects, and failure modes.
- Downstream implications of the operation when order matters.

Comments should explain why a complex research step is implemented the way it is. Avoid comments that restate obvious code.

## Testing Expectations

Tests are part of the behavioral contract. For each meaningful component, prefer layered tests:

- Unit tests for core operations and edge cases.
- Behavioral tests for NaNs, constant signals, missing values, short windows, invalid inputs, dtype/device handling, and shape preservation.
- Legacy parity fixtures where the old implementation provides trustworthy expected behavior.
- Integration tests for pipeline order, preprocessing/model interaction, and metric aggregation.
- Gradient/backward checks for differentiable model or loss components.

Run the narrowest relevant tests first, then broaden when touching shared behavior. If tests cannot be run, report the reason and the residual risk.

## Git, GitHub, And Worktrees

- Use `git` for version control and `gh` for GitHub issues/PRs when authenticated.
- Use `/home/samcantrill/work/rphys` as the main foreground checkout.
- Use `/home/samcantrill/work/rphys-worktrees` for isolated implementation worktrees.
- Use one branch and one worktree per implementation phase.
- Branch pattern: `agent/<issue>-<component>-p<n>-<slug>`.
- Worktree pattern: `../rphys-worktrees/<issue>-<component>-p<n>-<slug>`.
- Do not let multiple workers edit overlapping file sets.
- Keep implementation PRs small enough for scientific and code review.
- Default merge strategy is squash merge after review.
- Remove the phase worktree after the PR is merged and the branch is deleted.

## Multi-Agent Workflow Rules

- The main agent owns synthesis, user discussion, approvals, integration, and final judgment.
- Use subagents explicitly for bounded tasks only.
- Use read-only agents for legacy audit, RFC planning, phase planning, and scientific review.
- Use implementation agents only after an RFC and phase plan are accepted.
- Implementation agents must work inside their assigned worktree and branch.
- Each subagent must return concise evidence: paths, symbols, decisions, commands run, risks, and open questions.
- The main agent must reconcile conflicting agent findings before implementation or merge.

## Required Gates

Before implementation:

- Roadmap item exists.
- Full component RFC is accepted.
- Phase implementation plan is accepted.
- Phase branch/worktree ownership is clear.

Before merge:

- Tests requested by the phase plan have run or failures are documented.
- Code review has checked correctness, maintainability, API quality, and test coverage.
- Scientific review has checked the RFC, legacy evidence, pipeline implications, and relevant references.
- PR description links the RFC, phase plan, issue, and verification evidence.
