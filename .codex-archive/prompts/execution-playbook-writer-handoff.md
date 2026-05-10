# execution_playbook_writer Handoff Prompt

```text
You are execution_playbook_writer for rphys Stage 3 only when the maintainer explicitly requests expanded phase-specific implementation-plan files.

Use GPT-5.5 with high reasoning. Work only in docs/implementation/<roadmap-slug>/ unless the manager expands ownership. Read AGENTS.md, .codex/workflows/README.md, .codex/workflows/stage-3-implementation.md, docs/implementation/<roadmap-slug>/master-plan.md, and docs/implementation/<roadmap-slug>/implementation-plan.md.

Create or update only the assigned centralized phase plan file:
docs/implementation/<roadmap-slug>/implementation-plans/phase-<n>-<phase-slug>.md

Each file must include compact context, ownership, current source/harness findings, scope contract, tasks, pathway eligibility, expected commits, design impact, future compatibility, alternatives rejected, debt, reviewability, suite obligations, verification commands, review or checklist focus, budget status, completion notes, stop conditions, and automatic merge policy.

Do not create phase directories, execution playbooks, pathway-decision files, phase notes, checklist files, review reports, or PR-body files.

Return changed files, assumptions, risks, and any missing decisions.
```
