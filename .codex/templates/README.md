# Codex Handoff Templates

These templates define durable Markdown artifacts for the artifact-centered `rphys` workflow.

Workflow entrypoints in `.codex/workflows/` tell users how to start common workflows. Prompts in `.codex/prompts/` tell agents what to do. Templates in `.codex/templates/` define the document shape that one or more agents draft, refine, review, and pass to the next stage.

## Template Map

| Workflow stage or handoff | Template | Typical destination |
| --- | --- | --- |
| Stage 1 planning notes | `stage-1-planning-notes.md` | `docs/implementation/<roadmap-slug>/planning-notes.md` |
| Stage 2 master plan | `master-implementation-plan.md` | `docs/implementation/<roadmap-slug>/master-plan.md` |
| Master-plan quality review | `master-plan-review-report.md` | manager thread or `docs/implementation/<roadmap-slug>/master-plan-review.md` |
| Master-plan quality refinement | `master-plan-refinement-summary.md` | manager thread or `docs/implementation/<roadmap-slug>/master-plan-refinement.md` |
| Phase execution playbook | `execution-playbook.md` | `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/execution-playbook.md` |
| Internal phase notes | `phase-notes.md` | `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/phase-notes.md` |
| Code or scientific review | `review-report.md` | `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/<review-kind>-review.md` |
| Public PR body | `phase-pr-body.md` | `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/pr-body.md` |

Keep public PR bodies concise and reviewer-facing. Keep workflow internals such as budget accounting, commit lists, GitHub JSON, blocker history, and cleanup state in phase notes.
