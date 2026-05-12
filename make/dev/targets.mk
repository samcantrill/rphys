.PHONY: dev-help check validate-pr diff-check build

dev-help:
	@printf 'rphys development targets\n'
	@printf '\n'
	@printf 'Checks:\n'
	@printf '  make check         Run lock, default tests, and whitespace checks\n'
	@printf '  make diff-check    Check staged and unstaged diffs for whitespace errors\n'
	@printf '\n'
	@printf 'Validation and packaging:\n'
	@printf '  make validate-pr   Run the local PR validation gate, summary, and build\n'
	@printf '  make build         Build source and wheel distributions\n'

check: lock-check test diff-check

validate-pr: lock-check test-summary build diff-check

diff-check:
	git diff --check

build:
	uv build
