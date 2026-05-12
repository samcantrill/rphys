---
name: rphys-roadmap-planning
description: Route roadmap-stage planning work inside the `rphys` repository into the existing `.codex/workflows/roadmap-version-planning.md` flow. Use when Codex needs to turn a `docs/roadmap.md` stage `v<N>` into approved `docs/roadmap/stage-<N>/planning.md` and `implementation-plan.md` artifacts, continue or review an in-progress stage planning pass, or explain the repository's planning workflow without inventing a parallel process.
---

# rphys Roadmap Planning

Use the repository's existing roadmap-planning workflow. Treat this skill as a
router and checklist, not as a replacement for the workflow, prompts, agents,
or templates already stored under `.codex/`.

## Workflow Router

1. Confirm the task is roadmap-stage planning for `rphys`, not phase
   implementation.
2. Resolve `v<N>` to `docs/roadmap/stage-<N>/`.
3. Read the canonical workflow entrypoint:
   `.codex/workflows/roadmap-version-planning.md`.
4. Read the roadmap stage source in `docs/roadmap.md` plus any existing stage
   artifacts under `docs/roadmap/stage-<N>/`.
5. Use the planning and implementation-plan templates named by the workflow.
6. Keep approvals, defaults, assumptions, readbacks, and unresolved decisions
   inside the stage artifacts rather than inventing side documents.

## Canonical Files

Read these files first:

- `AGENTS.md`
- `.codex/workflows/roadmap-version-planning.md`
- `.codex/templates/roadmap-stage-planning.md`
- `.codex/templates/roadmap-stage-implementation-plan.md`
- `docs/roadmap.md`
- Existing files under `docs/roadmap/stage-<N>/`, if present

Use [references/file-map.md](references/file-map.md) for a compact map of the
authoritative files and outputs.

## Operating Rules

- Follow the gates, decision packets, and specialist-pass requirements in the
  workflow entrypoint instead of restating them from memory.
- Keep the workflow artifact-centered: `planning.md` and
  `implementation-plan.md` are the durable outputs.
- Route reusable process feedback to `.codex/` workflow assets, not to product
  requirements.
- Do not implement code inside this planning workflow.
- Switch to `.codex/workflows/roadmap-version-implementation.md` only after an
  implementation plan is approved.

## Example Requests

- `Use $rphys-roadmap-planning for docs/roadmap.md v2.`
- `Continue the Stage 2 planning workflow with $rphys-roadmap-planning.`
- `Explain how Stage 1 roadmap planning works in this repo using $rphys-roadmap-planning.`
