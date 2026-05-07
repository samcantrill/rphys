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
| Workflow automation scaffold | draft | Initial maintainer workflow discussion | Three-stage roadmap, master-plan, and managed-implementation workflow with durable agent handoffs | Link/reference checks, TOML validation, stale-workflow search | Pending |

## Next Actions

1. Upload or paste project context for Stage 1.
2. Use `.codex/workflows/stage-1-roadmap.md` to start the roadmap discussion.
3. Keep this roadmap updated during discussion.
4. Select one accepted work package and use `.codex/workflows/stage-2-master-plan.md` to draft the master implementation plan.
