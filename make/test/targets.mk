.PHONY: test-help test test-no-extra test-package test-unit test-contract
.PHONY: test-integration test-e2e test-acceptance test-all
.PHONY: test-package-summary test-unit-summary test-contract-summary
.PHONY: test-integration-summary test-e2e-summary test-acceptance-summary
.PHONY: test-summary test-pr-summary

TEST_HARNESS := python -m tools.test_harness
TEST_UV_RUN := uv run
TEST_UV_DEV := UV_CACHE_DIR=$(UV_CACHE_DIR) uv run --isolated --locked --group dev
TEST_UV_LOCKED_DEV := UV_CACHE_DIR=$(UV_CACHE_DIR) uv run --locked --group dev

test-help:
	@printf 'rphys test targets\n'
	@printf '\n'
	@printf 'Suite runs:\n'
	@printf '  make test                 Run the default local test suite\n'
	@printf '  make test-no-extra        Run baseline tests without optional dependencies\n'
	@printf '  make test-package         Run package/API tests\n'
	@printf '  make test-unit            Run unit tests\n'
	@printf '  make test-contract        Run contract tests\n'
	@printf '  make test-integration     Run integration tests\n'
	@printf '  make test-e2e             Run end-to-end tests\n'
	@printf '  make test-acceptance      Run optional acceptance tests\n'
	@printf '  make test-all             Run all local non-network tests\n'
	@printf '\n'
	@printf 'Summary reports:\n'
	@printf '  make test-summary                 Write all suite summaries to build/test-summary.md\n'
	@printf '  make test-pr-summary              Write PR-ready validation summary to build/test-pr-summary.md\n'
	@printf '  make test-package-summary         Write package suite summary\n'
	@printf '  make test-unit-summary            Write unit suite summary\n'
	@printf '  make test-contract-summary        Write contract suite summary\n'
	@printf '  make test-integration-summary     Write integration suite summary\n'
	@printf '  make test-e2e-summary             Write end-to-end suite summary\n'
	@printf '  make test-acceptance-summary      Write acceptance suite summary\n'

test:
	@$(MAKE) test-no-extra

test-no-extra:
	$(TEST_UV_DEV) $(TEST_HARNESS) run default

test-package:
	$(TEST_UV_RUN) $(TEST_HARNESS) run package

test-unit:
	$(TEST_UV_RUN) $(TEST_HARNESS) run unit

test-contract:
	$(TEST_UV_RUN) $(TEST_HARNESS) run contract

test-integration:
	$(TEST_UV_RUN) $(TEST_HARNESS) run integration

test-e2e:
	$(TEST_UV_RUN) $(TEST_HARNESS) run e2e

test-acceptance:
	$(TEST_UV_RUN) $(TEST_HARNESS) run acceptance

test-all:
	$(TEST_UV_RUN) $(TEST_HARNESS) run all

test-package-summary:
	$(TEST_UV_LOCKED_DEV) $(TEST_HARNESS) summary package --output build/test-package-summary.md

test-unit-summary:
	$(TEST_UV_LOCKED_DEV) $(TEST_HARNESS) summary unit --output build/test-unit-summary.md

test-contract-summary:
	$(TEST_UV_LOCKED_DEV) $(TEST_HARNESS) summary contract --output build/test-contract-summary.md

test-integration-summary:
	$(TEST_UV_LOCKED_DEV) $(TEST_HARNESS) summary integration --output build/test-integration-summary.md

test-e2e-summary:
	$(TEST_UV_LOCKED_DEV) $(TEST_HARNESS) summary e2e --output build/test-e2e-summary.md

test-acceptance-summary:
	$(TEST_UV_LOCKED_DEV) $(TEST_HARNESS) summary acceptance --output build/test-acceptance-summary.md

test-summary:
	$(TEST_UV_LOCKED_DEV) $(TEST_HARNESS) summary

test-pr-summary:
	$(TEST_UV_LOCKED_DEV) $(TEST_HARNESS) summary --format pr --output build/test-pr-summary.md --artifact-dir build/test-pr-summary $(if $(TEST_REPORT_CHECKS),--checks $(TEST_REPORT_CHECKS),)
