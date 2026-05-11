# rphys Agent Guide

`rphys` is a Python package for remote physiological measurement research. Keep
this repository as the reusable base library for domain data structures,
datasets, preprocessing, models, training, evaluation, and analysis. Full
research projects, raw datasets, and heavy experiment workflows belong in
downstream repositories.

## Defaults

- Prefer clean modern APIs over preserving old project structure.
- Treat prior notes, archived workflows, and old code as evidence, not contract.
- Preserve scientific meaning over superficial parity with earlier code.
- Back public behavior with code, tests, and docs before downstream use.
- Keep base imports lightweight; do not pull heavy video, array, plotting,
  deep-learning, or dataset-SDK stacks into core imports.
- Do not commit raw datasets; use synthetic or tiny license-safe fixtures.
- Protect user work. Inspect `git status` before editing and do not revert
  unrelated local changes.

## Repository Shape

- Package code lives under `src/rphys`.
- Tests live under `tests`.
- Public architecture policy: `docs/architecture/public-contracts.md`.
- Focused domain docs: `docs/data/` and similar topic directories.
- Current Codex workflow assets: `.codex/`.
- Historical workflow reference only: `.codex-archive/`.

Use Python 3.12 and `uv`.

```bash
uv sync
uv run pytest
uv lock --check
git diff --check
```

For narrow changes, run the smallest relevant tests first, then broaden to the
full suite when the touched surface is shared or public.

## Scientific And API Contracts

For public datasets, preprocessing, signal processing, models, losses, metrics,
evaluation, or analysis code, document enough for results to be interpretable:

- shapes, units, dtypes, devices, coordinate conventions, and sampling rates;
- timestamps, alignment, windowing, resampling, filtering, masking,
  interpolation, padding, and normalization order;
- whether statistics are per-sample, per-subject, per-record, per-video,
  per-dataset, or global;
- leakage risks, split boundaries, subject identity handling, and label
  availability;
- failure behavior for NaNs, flat signals, short inputs, missing data, empty
  masks, invalid sampling rates, dtype/device mismatches, and unsupported
  temporal slices.

- Follow the stability labels in `docs/architecture/public-contracts.md`:
  stable, provisional, and private/internal.
- Do not add placeholder modules, registries, re-exports, or classes just to
  reserve names.
- Keep public imports intentional and tested.
- Prefer extension through importable Python objects referenced by `_target_`
  paths. Add registries only when symbolic names are part of the domain
  contract.
- `rphys` may depend on `loom`; `loom` must not depend on `rphys`. Generic
  experiment execution, artifacts, sweeps, and config infrastructure belong in
  `loom`.

Use concise docstrings with the relevant scientific details. Add comments only
where processing order or research logic would otherwise be easy to misread.

## Workflow Guidance

Keep this file stable and lean. Put detailed, evolving agent process in
`.codex/` workflows, prompts, templates, and agent definitions.

- Use `.codex/workflow/roadmap-version-plan.md` when the maintainer asks for a
  roadmap-stage planning workflow.
- Treat `.codex/templates/`, `.codex/prompts/`, and `.codex/agents/` as the
  current workflow schema and specialist-agent definitions.
- Record approvals, assumptions, validation evidence, and review notes in the
  active planning or implementation artifact.
- Ask the maintainer about product and scientific decisions; do not make them
  manage workflow mechanics.
- Rebuild and simplify the workflow iteratively as actual use reveals what is
  worth keeping.

For ordinary small edits, work in `/home/samcantrill/work/rphys`. For larger
implementation phases, use one isolated worktree per phase under
`/home/samcantrill/work/rphys-worktrees`.

Suggested phase naming:

- Branch: `agent/<roadmap-slug>-p<n>-<phase-slug>`
- Worktree: `../rphys-worktrees/<roadmap-slug>-p<n>-<phase-slug>`

If an active workflow explicitly uses subagents, keep write ownership bounded
and non-overlapping. Require concise handoffs with paths changed, commands run,
decisions, risks, and open questions.

## Pull Requests And Reviews

- Use `git` for version control and `gh` for GitHub when authenticated.
- Keep PRs scoped to the accepted change.
- In PR bodies, summarize behavior, scientific contract implications, tests,
  validation evidence, assumptions, and residual risks.
- Before merge, run the relevant tests and checks or record why they could not
  run and what risk remains.
