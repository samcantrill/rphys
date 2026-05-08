.PHONY: sync lock lock-check test check diff-check

sync:
	uv sync

lock:
	uv lock

lock-check:
	uv lock --check

test:
	uv run pytest

check: lock-check test diff-check

diff-check:
	git diff --check
