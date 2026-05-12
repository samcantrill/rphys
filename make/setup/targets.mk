.PHONY: setup-help install sync lock lock-check

setup-help:
	@printf 'rphys setup targets\n'
	@printf '\n'
	@printf 'Setup:\n'
	@printf '  make install       Install all dependency groups\n'
	@printf '  make sync          Sync the default environment\n'
	@printf '  make lock          Update uv.lock\n'
	@printf '  make lock-check    Check that uv.lock is current\n'

install:
	uv sync --all-groups

sync:
	uv sync

lock:
	uv lock

lock-check:
	uv lock --check
