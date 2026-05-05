# Bootstrap Workflow

## Purpose

Prepare `rphys` for multi-agent porting work before any legacy audit or implementation phase begins.

## Preconditions

- Main checkout exists at `/home/samcantrill/work/rphys`.
- Git remote is configured for `git@github.com:samcantrill/rphys.git`.
- The user can provide `LEGACY_REPO_PATH` before the first audit.

## Process

1. Confirm `git status --short --branch`.
2. Confirm `gh auth status`. If the token is invalid, run `gh auth login -h github.com` interactively before issue or PR automation.
3. Confirm `/home/samcantrill/work/rphys-worktrees` exists.
4. Confirm Codex can write to `/home/samcantrill/work/rphys-worktrees`, either through `~/.codex/config.toml` writable roots or a launch-time `--add-dir`.
5. Confirm `.codex/config.toml` defines conservative subagent limits.
6. Confirm `.codex/agents/*.toml` validates as TOML.
7. Confirm workflow docs and GitHub templates are committed before any branch/worktree implementation starts.

## Verification Commands

```bash
git status --short --branch
gh auth status
git worktree list
python3 -c 'import pathlib, tomllib; [tomllib.loads(p.read_text()) for p in pathlib.Path(".codex").rglob("*.toml")]; print("toml ok")'
git diff --check
```

## Exit Criteria

- Bootstrap files are committed.
- Worktree root exists and is writable to Codex.
- GitHub authentication is either working or explicitly listed as a blocker.
- The next workflow is `legacy-audit-roadmap.md`.
