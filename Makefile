UV_CACHE_DIR ?= /tmp/uv-cache
export UV_CACHE_DIR

.DEFAULT_GOAL := help

.PHONY: help

help:
	@printf 'rphys make targets\n'
	@printf '\n'
	@printf 'Target groups:\n'
	@printf '  make setup-help    List setup and dependency targets\n'
	@printf '  make dev-help      List development, validation, and build targets\n'
	@printf '  make test-help     List test run and summary targets\n'

include make/setup/*.mk
include make/dev/*.mk
include make/test/*.mk
