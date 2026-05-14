from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.test_harness import cli as harness_cli
from tools.test_harness.cli import (
    Counts,
    CoverageMetric,
    SuiteSummary,
    ValidationCheck,
    format_coverage,
    parse_coverage_json,
    parse_deselected,
    parse_junit,
    parse_validation_checks,
    write_pr_summary,
    write_summary,
)


def test_parse_junit_groups_testcase_counts_by_suite_section(tmp_path: Path) -> None:
    junit_path = tmp_path / "junit.xml"
    junit_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
  <testsuite name="pytest" tests="4" failures="1" errors="1" skipped="1">
    <testcase classname="tests.unit.rphys.data.test_sample" name="test_passes" time="0.10" />
    <testcase classname="tests.unit.rphys.io.test_fields" name="test_fails" time="0.20">
      <failure message="failed" />
    </testcase>
    <testcase classname="tests.unit.rphys.metrics.test_metric" name="test_errors" time="0.30">
      <error message="errored" />
    </testcase>
    <testcase classname="tests.unit.tools.test_test_harness" name="test_skips" time="0.40">
      <skipped message="skipped" />
    </testcase>
  </testsuite>
</testsuites>
""",
        encoding="utf-8",
    )

    counts, groups = parse_junit(junit_path, "unit")

    assert counts.passed == 1
    assert counts.failed == 1
    assert counts.errors == 1
    assert counts.skipped == 1
    assert counts.total == 4
    assert groups["data"].passed == 1
    assert groups["io"].failed == 1
    assert groups["metrics"].errors == 1
    assert groups["test-harness"].skipped == 1


def test_parse_deselected_uses_last_pytest_summary_count() -> None:
    assert parse_deselected("14 passed, 5 deselected in 0.25s") == 5
    assert parse_deselected("first: 1 deselected\nsecond: 411 deselected") == 411
    assert parse_deselected("14 passed in 0.25s") == 0


def test_parse_coverage_json_reports_suite_and_group_percentages(
    tmp_path: Path,
) -> None:
    coverage_path = tmp_path / "coverage.json"
    coverage_path.write_text(
        json.dumps(
            {
                "totals": {"covered_lines": 8, "num_statements": 10},
                "files": {
                    "src/rphys/data/sample.py": {
                        "summary": {"covered_lines": 6, "num_statements": 8}
                    },
                    "src/rphys/io/fields.py": {
                        "summary": {"covered_lines": 2, "num_statements": 2}
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    coverage = parse_coverage_json(coverage_path, "unit")

    assert format_coverage(coverage["__suite__"]) == "80%"
    assert format_coverage(coverage["data"]) == "75%"
    assert format_coverage(coverage["io"]) == "100%"


def test_write_summary_renders_overall_and_suite_breakdowns(tmp_path: Path) -> None:
    summary_path = tmp_path / "summary.md"
    write_summary(
        summary_path,
        [
            SuiteSummary(
                suite="unit",
                command="UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit",
                status="passed",
                duration=1.23,
                returncode=0,
                output="unit output",
                counts=Counts(passed=2, skipped=1, deselected=4, duration=1.23),
                groups={"data": Counts(passed=2, duration=0.50)},
                coverage={
                    "__suite__": CoverageMetric(covered_lines=9, statements=10),
                    "data": CoverageMetric(covered_lines=3, statements=4),
                },
            )
        ],
    )

    rendered = summary_path.read_text(encoding="utf-8")

    assert "# Test Suite Summary" in rendered
    assert "| unit | passed | 2 | 0 | 0 | 1 | 4 | 3 | 1.23s | 90% |" in rendered
    assert "| Overall | passed | 2 | 0 | 0 | 1 | 4 | 3 | 1.23s | - |" in rendered
    assert "## unit" in rendered
    assert "| data | passed | 2 | 0 | 0 | 0 | 2 | 0.50s | 75% |" in rendered
    assert "unit output" in rendered


def test_parse_validation_checks_accepts_structured_rows() -> None:
    checks = parse_validation_checks(
        [
            {
                "check": "Targeted Ruff",
                "result": "Passed",
                "evidence": "ruff check touched files",
            }
        ]
    )

    assert checks == [
        ValidationCheck(
            check="Targeted Ruff",
            result="Passed",
            evidence="ruff check touched files",
        )
    ]


def test_parse_validation_checks_rejects_malformed_rows() -> None:
    with pytest.raises(ValueError, match="evidence"):
        parse_validation_checks(
            [{"check": "Targeted Ruff", "result": "Passed"}],
            label="checks.json",
        )


def test_write_pr_summary_renders_validation_section_and_compact_suite_table(
    tmp_path: Path,
) -> None:
    summary_path = tmp_path / "pr-summary.md"
    write_pr_summary(
        summary_path,
        [
            SuiteSummary(
                suite="unit",
                command="UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit",
                status="passed",
                duration=1.23,
                returncode=0,
                output="unit output",
                counts=Counts(passed=2, skipped=1, deselected=4, duration=1.23),
                groups={"data": Counts(passed=2, duration=0.50)},
                coverage={"__suite__": CoverageMetric(covered_lines=9, statements=10)},
            )
        ],
        [
            ValidationCheck(
                check="Focused pytest",
                result="Passed",
                evidence="2 passed | deterministic",
            )
        ],
    )

    rendered = summary_path.read_text(encoding="utf-8")

    assert "## Tests And Validation" in rendered
    assert "| Focused pytest | Passed | 2 passed \\| deterministic |" in rendered
    assert "| Automated suite summary | Passed | Suite summary below |" in rendered
    assert "### Test Suite Summary" in rendered
    assert "| Suite | Status | Passed | Failed | Errors | Skipped | Deselected |" in rendered
    assert "| unit | passed | 2 | 0 | 0 | 1 | 4 |" in rendered
    assert "Command:" not in rendered
    assert "unit output" not in rendered


def test_main_summary_pr_uses_explicit_artifact_dir_and_checks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report_path = tmp_path / "report.md"
    artifact_dir = tmp_path / "artifacts"
    checks_path = tmp_path / "checks.json"
    checks_path.write_text(
        json.dumps(
            [
                {
                    "check": "Targeted Pytest",
                    "result": "Passed",
                    "evidence": "focused subset passed",
                }
            ]
        ),
        encoding="utf-8",
    )
    calls: list[tuple[str, Path]] = []

    def fake_run_summary_suite(name: str, artifact_root: Path) -> SuiteSummary:
        calls.append((name, artifact_root))
        return SuiteSummary(
            suite=name,
            command=f"pytest tests/{name}",
            status="passed",
            duration=0.01,
            returncode=0,
            output="",
            counts=Counts(passed=1),
            groups={},
            coverage={},
        )

    monkeypatch.setattr(harness_cli, "run_summary_suite", fake_run_summary_suite)

    status = harness_cli.main(
        [
            "summary",
            "unit",
            "--format",
            "pr",
            "--output",
            str(report_path),
            "--artifact-dir",
            str(artifact_dir),
            "--checks",
            str(checks_path),
        ]
    )

    assert status == 0
    assert calls == [("unit", artifact_dir)]
    rendered = report_path.read_text(encoding="utf-8")
    assert "| Targeted Pytest | Passed | focused subset passed |" in rendered
