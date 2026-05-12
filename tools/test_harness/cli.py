from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence
from xml.etree import ElementTree


DEFAULT_MARKER_EXPR = (
    "not slow and not network and not optional_dependency and not acceptance"
)
LOCAL_ALL_MARKER_EXPR = "not network and not optional_dependency and not acceptance"
SUMMARY_OUTPUT = Path("build/test-summary.md")
SUMMARY_ARTIFACT_DIR = Path("build/test-summary")
SOURCE_COVERAGE_ROOT = "src/rphys"
UV_CACHE_DIR = "/tmp/uv-cache"


@dataclass(frozen=True)
class Suite:
    name: str
    path: Path
    marker_expr: str = DEFAULT_MARKER_EXPR


@dataclass(frozen=True)
class Result:
    suite: str
    command: str
    status: str
    duration: float
    returncode: int
    output: str


@dataclass(frozen=True)
class GroupRule:
    name: str
    class_prefixes: tuple[str, ...]
    coverage_paths: tuple[str, ...] = ()


@dataclass
class Counts:
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    deselected: int = 0
    duration: float = 0.0

    @property
    def total(self) -> int:
        return self.passed + self.failed + self.errors + self.skipped

    @property
    def status(self) -> str:
        if self.failed or self.errors:
            return "failed"
        if self.total:
            return "passed"
        return "not present"

    def add(self, other: Counts) -> None:
        self.passed += other.passed
        self.failed += other.failed
        self.errors += other.errors
        self.skipped += other.skipped
        self.deselected += other.deselected
        self.duration += other.duration


@dataclass(frozen=True)
class CoverageMetric:
    covered_lines: int
    statements: int

    @property
    def percent(self) -> float | None:
        if self.statements == 0:
            return None
        return (self.covered_lines / self.statements) * 100


@dataclass(frozen=True)
class SuiteSummary:
    suite: str
    command: str
    status: str
    duration: float
    returncode: int
    output: str
    counts: Counts
    groups: Mapping[str, Counts]
    coverage: Mapping[str, CoverageMetric]


SUITES: dict[str, Suite] = {
    "package": Suite("package", Path("tests/package")),
    "unit": Suite("unit", Path("tests/unit")),
    "contract": Suite("contract", Path("tests/contracts")),
    "integration": Suite("integration", Path("tests/integration")),
    "e2e": Suite("e2e", Path("tests/e2e")),
    "acceptance": Suite("acceptance", Path("tests/acceptance"), "not network"),
}

GROUP_RULES: dict[str, tuple[GroupRule, ...]] = {
    "package": (
        GroupRule(
            "imports-boundaries",
            (
                "tests.package.test_import",
                "tests.package.test_import_boundaries",
            ),
        ),
        GroupRule("public-api", ("tests.package.test_public_api",), ("src/rphys/",)),
    ),
    "unit": (
        GroupRule("data", ("tests.unit.rphys.data",), ("src/rphys/data/",)),
        GroupRule("io", ("tests.unit.rphys.io",), ("src/rphys/io/",)),
        GroupRule(
            "datasources",
            ("tests.unit.rphys.datasources",),
            ("src/rphys/datasources/",),
        ),
        GroupRule("ops", ("tests.unit.rphys.ops",), ("src/rphys/ops/",)),
        GroupRule("methods", ("tests.unit.rphys.methods",), ("src/rphys/methods/",)),
        GroupRule("models", ("tests.unit.rphys.models",), ("src/rphys/models/",)),
        GroupRule("nn", ("tests.unit.rphys.nn",), ("src/rphys/nn/",)),
        GroupRule("losses", ("tests.unit.rphys.losses",), ("src/rphys/losses/",)),
        GroupRule(
            "objectives",
            ("tests.unit.rphys.objectives",),
            ("src/rphys/objectives/",),
        ),
        GroupRule("metrics", ("tests.unit.rphys.metrics",), ("src/rphys/metrics/",)),
        GroupRule(
            "learning",
            ("tests.unit.rphys.learning",),
            ("src/rphys/learning/",),
        ),
        GroupRule(
            "training",
            ("tests.unit.rphys.training",),
            ("src/rphys/training/",),
        ),
        GroupRule(
            "prediction",
            ("tests.unit.rphys.prediction",),
            ("src/rphys/prediction/",),
        ),
        GroupRule(
            "evaluation",
            ("tests.unit.rphys.evaluation",),
            ("src/rphys/evaluation/",),
        ),
        GroupRule(
            "analysis",
            ("tests.unit.rphys.analysis",),
            ("src/rphys/analysis/",),
        ),
        GroupRule("test-harness", ("tests.unit.tools",)),
        GroupRule(
            "core",
            ("tests.unit.rphys.test_",),
            (
                "src/rphys/__init__.py",
                "src/rphys/errors.py",
            ),
        ),
    ),
    "contract": (
        GroupRule(
            "datasources",
            ("tests.contracts.test_datasource",),
            ("src/rphys/datasources/",),
        ),
        GroupRule(
            "codecs",
            ("tests.contracts.test_codec",),
            ("src/rphys/io/",),
        ),
        GroupRule(
            "operations",
            ("tests.contracts.test_operation", "tests.contracts.test_transform"),
            ("src/rphys/ops/",),
        ),
        GroupRule(
            "methods",
            ("tests.contracts.test_method",),
            ("src/rphys/methods/",),
        ),
        GroupRule(
            "metrics",
            ("tests.contracts.test_metric",),
            ("src/rphys/metrics/",),
        ),
    ),
    "integration": (
        GroupRule("data-io", ("tests.integration.data", "tests.integration.io")),
        GroupRule("datasources", ("tests.integration.datasources",)),
        GroupRule("docs", ("tests.integration.docs",)),
        GroupRule(
            "methods-models",
            ("tests.integration.methods", "tests.integration.models"),
        ),
    ),
    "e2e": (
        GroupRule("public-api", ("tests.e2e",), ("src/rphys/",)),
    ),
    "acceptance": (
        GroupRule("real-data", ("tests.acceptance",)),
    ),
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run rphys test suites.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run one test suite.")
    run_parser.add_argument(
        "suite",
        choices=[*SUITES.keys(), "default", "all"],
        help="Suite to run.",
    )

    summary_parser = subparsers.add_parser(
        "summary", help="Run suites and write a Markdown summary."
    )
    summary_parser.add_argument(
        "suites",
        nargs="*",
        choices=SUITES.keys(),
        help="Suites to summarize. Defaults to all suites.",
    )
    summary_parser.add_argument(
        "--output",
        type=Path,
        default=SUMMARY_OUTPUT,
        help=f"Summary path. Defaults to {SUMMARY_OUTPUT}.",
    )

    args = parser.parse_args(argv)

    if args.command == "run":
        result = run_suite(args.suite)
        print_result(result)
        return result.returncode

    if args.command == "summary":
        suite_names = list(args.suites) or list(SUITES)
        results = [run_summary_suite(name) for name in suite_names]
        write_summary(args.output, results)
        print(f"Wrote test summary to {args.output}")
        for result in results:
            print(
                f"{result.suite}: {result.status} "
                f"({result.counts.passed} passed, {result.counts.failed} failed, "
                f"{result.counts.errors} errors, {result.counts.skipped} skipped, "
                f"{result.counts.deselected} deselected; {result.duration:.2f}s)"
            )
        return 1 if any(result.returncode != 0 for result in results) else 0

    raise AssertionError(f"unhandled command: {args.command}")


def run_summary_suite(name: str) -> SuiteSummary:
    suite = SUITES[name]
    if not has_tests(suite.path):
        counts = Counts()
        return SuiteSummary(
            suite=suite.name,
            command=f'uv run pytest {suite.path} -m "{suite.marker_expr}"',
            status="not present",
            duration=0.0,
            returncode=0,
            output="No test files are present for this suite yet.",
            counts=counts,
            groups={},
            coverage={},
        )

    artifact_dir = SUMMARY_ARTIFACT_DIR / name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    junit_path = artifact_dir / "junit.xml"
    coverage_data_path = artifact_dir / ".coverage"
    coverage_json_path = artifact_dir / "coverage.json"
    unlink_existing(junit_path, coverage_data_path, coverage_json_path)

    pytest_args = [*pytest_args_for_suite(suite), "--junitxml", str(junit_path)]
    command = uv_command()
    if should_collect_coverage(name):
        command.extend(
            [
                "python",
                "-m",
                "coverage",
                "run",
                "--data-file",
                str(coverage_data_path),
                "--source",
                SOURCE_COVERAGE_ROOT,
                "-m",
                "pytest",
                *pytest_args,
            ]
        )
    else:
        command.extend(["python", "-m", "pytest", *pytest_args])

    env = os.environ.copy()
    env.setdefault("UV_CACHE_DIR", UV_CACHE_DIR)
    display_command = f"UV_CACHE_DIR={env['UV_CACHE_DIR']} {format_command(command)}"

    start = time.monotonic()
    completed = subprocess.run(
        command,
        check=False,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    duration = time.monotonic() - start
    output = completed.stdout

    coverage_output = write_coverage_json(coverage_data_path, coverage_json_path, env)
    if coverage_output:
        output = (
            output
            + ("\n" if output and not output.endswith("\n") else "")
            + coverage_output
        )

    counts, groups = parse_junit(junit_path, name)
    counts.deselected = parse_deselected(output)
    counts.duration = duration
    coverage = parse_coverage_json(coverage_json_path, name)
    status = "passed" if completed.returncode == 0 else "failed"
    if counts.total == 0 and completed.returncode == 0:
        status = "not present"

    return SuiteSummary(
        suite=name,
        command=display_command,
        status=status,
        duration=duration,
        returncode=completed.returncode,
        output=output,
        counts=counts,
        groups=groups,
        coverage=coverage,
    )


def uv_command() -> list[str]:
    return ["uv", "run", "--isolated", "--locked", "--group", "dev"]


def write_coverage_json(
    coverage_data_path: Path,
    coverage_json_path: Path,
    env: Mapping[str, str],
) -> str:
    if not coverage_data_path.exists():
        return ""
    command = [
        *uv_command(),
        "python",
        "-m",
        "coverage",
        "json",
        "--data-file",
        str(coverage_data_path),
        "-o",
        str(coverage_json_path),
        "--quiet",
    ]
    completed = subprocess.run(
        command,
        check=False,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if completed.returncode == 0:
        return ""
    return completed.stdout or "coverage json failed without output\n"


def pytest_args_for_suite(suite: Suite) -> list[str]:
    return [str(suite.path), "-m", suite.marker_expr]


def unlink_existing(*paths: Path) -> None:
    for path in paths:
        if path.exists():
            path.unlink()


def run_suite(name: str) -> Result:
    if name == "default":
        return run_named_pytest(
            "default",
            Path("tests"),
            ["tests", "-m", DEFAULT_MARKER_EXPR],
            f'uv run pytest tests -m "{DEFAULT_MARKER_EXPR}"',
        )
    if name == "all":
        return run_named_pytest(
            "all",
            Path("tests"),
            ["tests", "-m", LOCAL_ALL_MARKER_EXPR],
            f'uv run pytest tests -m "{LOCAL_ALL_MARKER_EXPR}"',
        )

    suite = SUITES[name]
    return run_named_pytest(
        suite.name,
        suite.path,
        pytest_args_for_suite(suite),
        f'uv run pytest {suite.path} -m "{suite.marker_expr}"',
    )


def run_named_pytest(
    suite: str,
    path: Path,
    args: Sequence[str],
    command: str,
) -> Result:
    if not has_tests(path):
        return Result(
            suite=suite,
            command=command,
            status="not present",
            duration=0.0,
            returncode=0,
            output="No test files are present for this suite yet.\n",
        )
    return run_pytest(suite, args, command)


def has_tests(path: Path) -> bool:
    if not path.exists():
        return False
    return any(candidate.is_file() for candidate in path.rglob("test*.py"))


def has_source_files() -> bool:
    source_root = Path(SOURCE_COVERAGE_ROOT)
    if not source_root.exists():
        return False
    return any(candidate.is_file() for candidate in source_root.rglob("*.py"))


def should_collect_coverage(suite: str) -> bool:
    if not has_source_files():
        return False
    if suite == "unit":
        return has_tests(Path("tests/unit/rphys"))
    return True


def run_pytest(suite: str, args: Sequence[str], command: str) -> Result:
    start = time.monotonic()
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    duration = time.monotonic() - start
    status = "passed" if completed.returncode == 0 else "failed"
    return Result(
        suite=suite,
        command=command,
        status=status,
        duration=duration,
        returncode=completed.returncode,
        output=completed.stdout,
    )


def print_result(result: Result) -> None:
    if result.output:
        print(result.output, end="" if result.output.endswith("\n") else "\n")
    print(f"{result.suite}: {result.status} ({result.duration:.2f}s)")


def parse_junit(path: Path, suite: str) -> tuple[Counts, dict[str, Counts]]:
    counts = Counts()
    groups: dict[str, Counts] = {}
    if not path.exists():
        return counts, groups

    root = ElementTree.parse(path).getroot()
    for case in root.iter():
        if local_name(case.tag) != "testcase":
            continue
        classname = case.attrib.get("classname", "") or case.attrib.get("name", "")
        group_name = group_for_classname(suite, classname)
        group_counts = groups.setdefault(group_name, Counts())
        case_counts = testcase_counts(case)
        counts.add(case_counts)
        group_counts.add(case_counts)

    return counts, groups


def testcase_counts(case: ElementTree.Element) -> Counts:
    counts = Counts(duration=parse_float(case.attrib.get("time")))
    child_tags = {local_name(child.tag) for child in case}
    if "error" in child_tags:
        counts.errors = 1
    elif "failure" in child_tags:
        counts.failed = 1
    elif "skipped" in child_tags:
        counts.skipped = 1
    else:
        counts.passed = 1
    return counts


def local_name(tag: str) -> str:
    return tag.rsplit("}", maxsplit=1)[-1]


def group_for_classname(suite: str, classname: str) -> str:
    for rule in GROUP_RULES.get(suite, ()):
        if classname.startswith(rule.class_prefixes):
            return rule.name
    return "other"


def parse_float(raw: str | None) -> float:
    if raw is None:
        return 0.0
    try:
        return float(raw)
    except ValueError:
        return 0.0


def parse_deselected(output: str) -> int:
    matches = re.findall(r"(\d+)\s+deselected", output)
    if not matches:
        return 0
    return int(matches[-1])


def parse_coverage_json(path: Path, suite: str) -> dict[str, CoverageMetric]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}
    files = raw.get("files")
    if not isinstance(files, dict):
        return {}

    coverage: dict[str, CoverageMetric] = {}
    totals = raw.get("totals")
    if isinstance(totals, dict):
        coverage["__suite__"] = CoverageMetric(
            covered_lines=int(totals.get("covered_lines", 0)),
            statements=int(totals.get("num_statements", 0)),
        )

    for rule in GROUP_RULES.get(suite, ()):
        metric = aggregate_coverage(files, rule.coverage_paths)
        if metric is not None:
            coverage[rule.name] = metric
    return coverage


def aggregate_coverage(
    files: Mapping[str, object],
    coverage_paths: Sequence[str],
) -> CoverageMetric | None:
    if not coverage_paths:
        return None
    covered_lines = 0
    statements = 0
    for raw_path, raw_file in files.items():
        path = normalize_coverage_path(raw_path)
        if not coverage_path_matches(path, coverage_paths):
            continue
        if not isinstance(raw_file, dict):
            continue
        summary = raw_file.get("summary")
        if not isinstance(summary, dict):
            continue
        covered_lines += int(summary.get("covered_lines", 0))
        statements += int(summary.get("num_statements", 0))
    if statements == 0:
        return None
    return CoverageMetric(covered_lines=covered_lines, statements=statements)


def normalize_coverage_path(path: str) -> str:
    normalized = Path(path).as_posix()
    marker = f"/{SOURCE_COVERAGE_ROOT}/"
    if marker in normalized:
        return f"{SOURCE_COVERAGE_ROOT}/{normalized.split(marker, maxsplit=1)[1]}"
    return normalized


def coverage_path_matches(path: str, selectors: Sequence[str]) -> bool:
    for selector in selectors:
        if selector.endswith("/"):
            if path.startswith(selector):
                return True
        elif path == selector:
            return True
    return False


def write_summary(path: Path, results: Sequence[SuiteSummary]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    overall = aggregate_counts([result.counts for result in results])
    overall_status = (
        "failed" if any(result.returncode != 0 for result in results) else "passed"
    )
    lines = [
        "# Test Suite Summary",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"Overall Status: {overall_status}",
        "",
        "| Suite | Status | Passed | Failed | Errors | Skipped | Deselected | Total | Duration | Coverage |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for result in results:
        lines.append(
            "| "
            + " | ".join(
                [
                    result.suite,
                    result.status,
                    str(result.counts.passed),
                    str(result.counts.failed),
                    str(result.counts.errors),
                    str(result.counts.skipped),
                    str(result.counts.deselected),
                    str(result.counts.total),
                    f"{result.duration:.2f}s",
                    format_coverage(result.coverage.get("__suite__")),
                ]
            )
            + " |"
        )
    lines.append(
        "| "
        + " | ".join(
            [
                "Overall",
                overall_status,
                str(overall.passed),
                str(overall.failed),
                str(overall.errors),
                str(overall.skipped),
                str(overall.deselected),
                str(overall.total),
                f"{sum(result.duration for result in results):.2f}s",
                "-",
            ]
        )
        + " |"
    )

    for result in results:
        lines.extend(["", f"## {result.suite}", "", f"Command: `{result.command}`", ""])
        if result.groups:
            lines.extend(
                [
                    "| Group | Status | Passed | Failed | Errors | Skipped | Total | Duration | Coverage |",
                    "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
                ]
            )
            for group_name, counts in sorted(result.groups.items()):
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            group_name,
                            counts.status,
                            str(counts.passed),
                            str(counts.failed),
                            str(counts.errors),
                            str(counts.skipped),
                            str(counts.total),
                            f"{counts.duration:.2f}s",
                            format_coverage(result.coverage.get(group_name)),
                        ]
                    )
                    + " |"
                )
        else:
            lines.append("_No tests were present for this suite._")

    lines.extend(["", "## Output Tails", ""])
    for result in results:
        lines.extend(
            [
                f"### {result.suite}",
                "",
                "```text",
                tail(result.output),
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def aggregate_counts(counts: Sequence[Counts]) -> Counts:
    aggregate = Counts()
    for count in counts:
        aggregate.add(count)
    return aggregate


def format_coverage(metric: CoverageMetric | None) -> str:
    if metric is None:
        return "N/A"
    percent = metric.percent
    if percent is None:
        return "N/A"
    return f"{percent:.0f}%"


def format_command(command: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def tail(output: str, line_count: int = 20) -> str:
    stripped = output.strip()
    if not stripped:
        return "(no output)"
    lines = stripped.splitlines()
    return "\n".join(lines[-line_count:])
