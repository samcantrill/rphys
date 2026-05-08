"""Static checks for dependency and package-boundary contracts."""

from __future__ import annotations

import ast
import importlib.util
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "rphys"
PYPROJECT = ROOT / "pyproject.toml"

OPTIONAL_STACK_IMPORT_ROOTS = {
    "cv2",
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "sklearn",
    "tensorflow",
    "torch",
}

GENERIC_INFRASTRUCTURE_TERMS = (
    "ArtifactStore",
    "ConfigComposer",
    "DagExecutor",
    "PipelineExecutor",
    "RecipeExpander",
    "RunStore",
    "StageRunner",
    "SweepRunner",
)

DEFERRED_MODULES = (
    "analysis",
    "evaluation",
    "losses",
    "methods",
    "models",
    "ops",
    "recipes",
    "stages",
    "testing",
    "training",
)


def _python_files() -> list[Path]:
    return sorted(SRC.rglob("*.py"))


def _import_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", maxsplit=1)[0])

    return roots


def test_base_project_has_no_runtime_dependencies_or_license_metadata() -> None:
    metadata = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    project = metadata["project"]

    assert project["requires-python"] == ">=3.12"
    assert project["dependencies"] == []
    assert "Private :: Do Not Upload" in project["classifiers"]
    assert "license" not in project
    assert "license-files" not in project
    assert metadata["build-system"] == {
        "requires": ["uv_build>=0.11.6,<0.12"],
        "build-backend": "uv_build",
    }


def test_source_imports_do_not_pull_heavy_optional_stacks() -> None:
    imported_roots = set().union(*(_import_roots(path) for path in _python_files()))

    assert imported_roots.isdisjoint(OPTIONAL_STACK_IMPORT_ROOTS)


def test_deferred_module_directories_do_not_exist() -> None:
    for module in DEFERRED_MODULES:
        assert not (SRC / module).exists()
        assert importlib.util.find_spec(f"rphys.{module}") is None


def test_generic_loom_owned_infrastructure_is_not_implemented() -> None:
    source_text = "\n".join(path.read_text(encoding="utf-8") for path in _python_files())

    for term in GENERIC_INFRASTRUCTURE_TERMS:
        assert term not in source_text
