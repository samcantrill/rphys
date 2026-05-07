# rphys Codex Instructions

## Project Purpose

`rphys` is a Python package for remote physiological measurement research. It should provide reusable, scientifically careful components for domain-specific datasets, preprocessing, models, training, evaluation, and analysis. Full research projects and heavy experiment workflows should live in downstream repositories; this repository should remain the base library.

## Core Engineering Rules

- Prefer clean modern APIs over direct preservation of earlier project structure.
- Treat previous code, notes, and uploaded project context as evidence, not as the API contract.
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

- Use `git` for version control and `gh` for GitHub PRs when authenticated.
- Use `/home/samcantrill/work/rphys` as the main foreground checkout.
- Use `/home/samcantrill/work/rphys-worktrees` for isolated implementation worktrees.
- Use one branch and one worktree per implementation phase.
- Branch pattern: `agent/<roadmap-slug>-p<n>-<phase-slug>`.
- Worktree pattern: `../rphys-worktrees/<roadmap-slug>-p<n>-<phase-slug>`.
- Do not let multiple workers edit overlapping file sets.
- Keep implementation PRs small enough for the selected standard or fast implementation pathway.
- Default merge strategy is automatic squash merge after pathway gates pass. Human review is not a default merge gate.
- Remove the phase worktree after the PR is merged and the branch is deleted.

## Multi-Agent Workflow Rules

- The main agent owns synthesis, user discussion, approvals, integration, and final judgment.
- Use subagents explicitly for bounded tasks only.
- Use roadmap and master-plan agents for planning support, but keep user acceptance as the gate between stages.
- Keep workflows artifact-centered: `.codex/workflows/` are short entrypoints, `.codex/prompts/` are canonical role/action prompts, `.codex/templates/` are durable artifact schemas, and `.codex/agents/` define authority/model/sandbox.
- Use implementation agents only after a roadmap work package is accepted, Stage 1 planning notes are complete, the master implementation plan is accepted, and the master-plan quality gate has passed.
- Keep planning direct: provide the maintainer with a concise context readout, then ask the concrete design questions needed to continue. Do not make the maintainer manage workflow mechanics or document proliferation.
- Each implementation phase may use a planning worker followed by a coding worker. Record planning output, pathway decisions, fast-path checklists, validation evidence, review summaries, and PR facts in the live implementation plan instead of creating separate phase-planning documents by default.
- Implementation agents must work inside their assigned worktree and branch.
- Each subagent must return concise evidence: paths, decisions, commands run, risks, and open questions.
- Durable handoffs must be written under `docs/implementation/<roadmap-slug>/` so later agents can resume from repository state. Keep the default durable artifact set lean: `planning-notes.md`, the live `master-plan.md`, and the live `implementation-plan.md`. If a single implementation plan becomes unreviewably large, place phase-specific plans under `docs/implementation/<roadmap-slug>/implementation-plans/` and keep `implementation-plan.md` as the index and status ledger. Create other planning/review documents only when the maintainer asks for them or when a blocker cannot be understood from the lean artifacts.
- The main agent must reconcile conflicting agent findings before implementation or merge.

## Required Gates

Before Stage 2 planning:

- Scaffold roadmap work package is accepted.
- Scope, success criteria, out-of-scope behavior, and validation goals are recorded.
- Stage 1 planning notes exist under `docs/implementation/<roadmap-slug>/planning-notes.md`.
- Functionality, behavior, major design decisions, accepted assumptions, and validation goals are recorded in the planning notes.
- The maintainer has answered the concrete design questions needed to start Stage 2, or explicit assumptions are recorded.

Before Stage 3 implementation:

- Master implementation plan is accepted.
- Master plan has passed the quality gate: one review, one refinement pass if needed, and one confirmation review, with the result recorded in the master plan rather than separate review/refinement files by default.
- Phase sections in the accepted master plan are implementation-ready, and any Phase 0 preflight has confirmed them or recorded blockers in the master plan or implementation plan.
- Phase branch/worktree ownership is clear and disjoint.
- GitHub authentication and worktree write access are verified or blockers are documented.

Before merge:

- Tests requested by the master plan and implementation plan have run or failures are documented.
- The full repository test/check suite has run when available.
- The pre-submit blocker gate has checked the implementation plan, diff, public PR body or PR summary, validation evidence, scope boundaries, assumptions, and risks.
- Standard pathway phases have completed automated code review and automated scientific/workflow review with no unresolved blocker.
- Fast pathway phases have a manager checklist in the implementation plan confirming narrow scope, low risk, no public-interface impact, and no scientific/workflow contract impact.
- Public PR body summarizes implementation, tests, validation, assumptions, and risks. The implementation plan records workflow details, budgets, commits, GitHub facts, blockers, review summaries, and cleanup. A repository copy of the PR body is optional and should be created only when useful for offline review or blocked PR creation.
- PRs are automatically squash-merged when validation and pathway gates pass. The manager may approve, admin-merge, or otherwise force merge only for human-review-requirement branch protection after automated gates pass, not for failing validation, wrong target branches, unresolved conflicts, changes outside the accepted plan, or known implementation/review blockers.
