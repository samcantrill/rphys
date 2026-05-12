from __future__ import annotations

import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_project_has_no_runtime_dependencies() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["dependencies"] == []


def test_project_metadata_keeps_private_rights_status() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    project = pyproject["project"]
    classifiers = project["classifiers"]

    assert "license" not in project
    assert "Private :: Do Not Upload" in classifiers
    assert not any(
        classifier.startswith("License ::") for classifier in classifiers
    )


def test_license_remains_all_rights_reserved_placeholder() -> None:
    license_text = (REPO_ROOT / "LICENSE").read_text()

    assert "All rights reserved." in license_text
    assert "No public-use license has been selected" in license_text
