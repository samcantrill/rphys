# Codex Workflow Entrypoints

This directory is the user-facing "start here" layer for rphys Codex
workflows.

Files here are intentionally short. They route user requests to canonical
prompts in `.codex/prompts/` and durable artifacts in `.codex/templates/`.

Do not put role authority, model, or sandbox policy here; that belongs in
`.codex/agents/`. Do not put full artifact schemas here; that belongs in
`.codex/templates/`. Do not duplicate long prompt bodies here.

## Entrypoints

| Entrypoint | Use when | Canonical prompts |
| --- | --- | --- |
| `roadmap-version-planning.md` | The user wants to convert one roadmap stage into approved planning and an implementation plan | `roadmap-stage-*.md` planning prompts |
| `roadmap-version-implementation.md` | An approved roadmap-stage implementation plan exists and Codex should execute phases through PRs and automated merges | `phase-loop-management.md` plus phase/PR prompts |

## Typical Path

```text
roadmap-version planning
approved stage implementation plan
automatic implementation-plan quality gate
phase execution plan
implementation and phase-scoped validation
PR body and suite evidence
automated review
CI-gated merge to develop
merge metadata update and cleanup
```

## Internal Capabilities

These are workflow internals, not separate user-facing entrypoints:

- Implementation-plan quality gate before phase selection.
- Expanded-path phase execution plan refinement for public API, scientific
  contract, import-boundary, dependency, serialization, provenance, or
  cross-module risk.
- Pre-submit blocker gate before PR creation.
- Automated phase review and merge after validation and CI pass.
