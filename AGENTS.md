# rphys Agent Guide

`rphys` is a reusable Python base library for remote physiological measurement
research. Keep it focused on domain data structures, datasets, preprocessing,
signal processing, models, training, evaluation, and analysis. Full research
projects, raw datasets, large experiment runs, and heavy project-specific
workflows belong in downstream repositories.

## Repository

- Package code lives under `src/rphys`.
- Tests live under `tests`.
- Documentation lives under `docs`.
- Canonical roadmap and architecture policy: `docs/roadmap.md`.
- Repository glossary and vocabulary guide: `docs/GLOSSARY.md`.
- Current Codex workflow assets live under `.codex/`, including workflows,
  prompts, templates, and specialist-agent definitions.
- Use Python 3.12 and `uv`.

Repository style:

- Treat this repository as a reusable research library, not as a single
  experiment workspace.
- Prefer clean modern APIs over preserving old project structure.
- Treat prior notes, archived workflows, and old code as evidence, not
  contract.
- Preserve scientific meaning over superficial parity with earlier code.
- Keep base imports lightweight. Do not pull heavy video, array, plotting,
  deep-learning, or dataset-SDK stacks into core imports.
- Do not commit raw datasets. Use synthetic or tiny license-safe fixtures.
- Follow the stability labels in `docs/roadmap.md`: stable, provisional, and
  private/internal.
- `rphys` may depend on `loom`; `loom` must not depend on `rphys`. Generic
  experiment execution, artifacts, sweeps, and config infrastructure belong in
  `loom`.

## Development

Protect user work before editing:

- Inspect `git status` before changing files.
- Do not revert unrelated local changes.
- If a touched file contains unrelated edits, preserve them and work with the
  current file state.

Design principles:

- Design for a research and experimental codebase: implementations should make
  assumptions, transformations, provenance, and failure modes inspectable.
- Prefer small, composable modules with explicit boundaries over coupled
  convenience layers.
- Maximize modularity until coupling is justified by a real domain contract.
  Avoid premature registries, global state, broad base classes, and hidden
  cross-module dependencies.
- Consider whether an implementation will force refactoring later. If likely,
  separate domain logic, IO, configuration, and framework integration now.
- Keep public imports intentional and tested.
- Do not add placeholder modules, registries, re-exports, or classes just to
  reserve names.
- Prefer extension through importable Python objects referenced by `_target_`
  paths. Add registries only when symbolic names are part of the domain
  contract.
- Back public behavior with code, tests, and docs before downstream use.

Scientific and mathematical contracts:

- Preserve the meaning of physiological operations. Do not simplify away
  sampling, alignment, masking, filtering, or normalization details that affect
  interpretation.
- Document the mathematical or scientific rationale for nontrivial operations,
  especially filters, transforms, losses, metrics, normalization, windowing,
  and aggregation.
- Make operation provenance recoverable: important parameters, order of
  operations, reference frames, sample rates, label sources, and split
  boundaries should be clear from code, docs, or returned metadata.
- Be explicit about leakage risks, subject identity handling, label
  availability, and whether statistics are per-sample, per-subject,
  per-record, per-video, per-dataset, or global.
- Define failure behavior for NaNs, flat signals, short inputs, missing data,
  empty masks, invalid sampling rates, dtype/device mismatches, and unsupported
  temporal slices.

Documentation principles:

- Update documentation as you change behavior. Do not leave public APIs,
  scientific assumptions, or workflow instructions to be inferred from code.
- Use concise docstrings with the relevant scientific details: shapes, units,
  dtypes, devices, coordinate conventions, sampling rates, timestamps,
  alignment, windowing, resampling, filtering, masking, interpolation, padding,
  and normalization order.
- Add comments only where processing order or research logic would otherwise be
  easy to misread.
- For public datasets, preprocessing, signal processing, models, losses,
  metrics, evaluation, or analysis code, document enough for results to be
  interpretable and reproducible.

Validation:

```bash
uv sync
make test
make test-summary
make test-package
make test-unit
make test-contract
make test-integration
make validate-pr
uv lock --check
git diff --check
```

- For narrow changes, run the smallest relevant tests first.
- Broaden to the full suite when the touched surface is shared, public, or
  scientifically meaningful.
- Add or update tests when changing public behavior, edge-case handling,
  numerical behavior, or documented contracts.
- Follow `tests/README.md` for suite placement. Keep package/API,
  source-mirrored unit, contract, integration, e2e, acceptance, and support
  tests separated by intent.
- Test execution and Markdown summaries are owned by `tools/test_harness`.
  Make targets are split under `make/setup`, `make/dev`, and `make/test`.

Version control:

- Use `git` for version control and `gh` for GitHub when authenticated.
- Keep commits and PRs scoped to the accepted change.
- In PR bodies, summarize behavior, scientific contract implications, tests,
  validation evidence, assumptions, and residual risks.
- Before merge, run the relevant tests and checks or record why they could not
  run and what risk remains.

## Workflows

Keep this file stable and lean. Put detailed and evolving agent process in
`.codex/` workflows, prompts, templates, and agent definitions.

Workflow assets:

- Use `.codex/workflows/roadmap-version-planning.md` when the maintainer asks
  for a roadmap-stage planning workflow.
- Use `.codex/workflows/roadmap-version-implementation.md` when an approved
  roadmap-stage implementation plan should be implemented through phase
  worktrees, validation, PRs, and automated merge.
- Treat `.codex/templates/`, `.codex/prompts/`, and `.codex/agents/` as the
  current workflow schema and specialist-agent definitions.
- Record approvals, assumptions, validation evidence, review notes, and open
  questions in the active planning or implementation artifact.
- Ask the maintainer about product and scientific decisions. Do not make them
  manage workflow mechanics.
- Rebuild and simplify workflows iteratively as actual use reveals what is
  worth keeping.

Working directory:

- Use `/home/samcantrill/work/rphys` for ordinary small edits.
- Use one isolated worktree per larger implementation phase under
  `/home/samcantrill/work/rphys-worktrees`.
- Keep each worktree scoped to one accepted phase or reviewable unit of work.

Suggested phase naming:

- Branch: `agent/<roadmap-slug>-p<n>-<phase-slug>`
- Worktree: `../rphys-worktrees/<roadmap-slug>-p<n>-<phase-slug>`

Subagents and parallel work:

- Use subagents only when an active workflow explicitly calls for them.
- Keep write ownership bounded and non-overlapping.
- Require concise handoffs with paths changed, commands run, decisions, risks,
  and open questions.
- Integrate subagent work by checking behavior, documentation, tests, and
  scientific contract implications before treating the phase as complete.
