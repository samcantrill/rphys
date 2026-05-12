from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HEAVY_OPTIONAL_MODULES = [
    "av",
    "cv2",
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "torch",
]
LIGHTWEIGHT_IMPORTS = [
    "rphys",
    "rphys.analysis",
    "rphys.data",
    "rphys.data.keys",
    "rphys.data.metadata",
    "rphys.data.schemas",
    "rphys.data.splits",
    "rphys.data.types",
    "rphys.datasources",
    "rphys.errors",
    "rphys.evaluation",
    "rphys.io",
    "rphys.learning",
    "rphys.losses",
    "rphys.methods",
    "rphys.metrics",
    "rphys.models",
    "rphys.nn",
    "rphys.objectives",
    "rphys.ops",
    "rphys.prediction",
    "rphys.training",
]


def test_core_imports_do_not_load_heavy_optional_modules() -> None:
    imports = ", ".join(repr(module_name) for module_name in LIGHTWEIGHT_IMPORTS)
    heavy_modules = ", ".join(repr(module_name) for module_name in HEAVY_OPTIONAL_MODULES)
    script = textwrap.dedent(
        f"""
        import importlib
        import sys

        for module_name in [{imports}]:
            importlib.import_module(module_name)

        loaded = sorted(
            module_name
            for module_name in [{heavy_modules}]
            if module_name in sys.modules
        )
        if loaded:
            raise SystemExit("heavy optional modules loaded: " + ", ".join(loaded))
        """
    )
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    pythonpath_parts = [str(REPO_ROOT / "src"), str(REPO_ROOT)]
    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)

    completed = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    assert completed.returncode == 0, completed.stdout


def test_rphys_does_not_define_generic_workflow_or_artifact_runtime_packages() -> None:
    forbidden_packages = [
        "rphys.artifacts",
        "rphys.stages",
        "rphys.workflow",
        "rphys.workflows",
    ]

    for package_name in forbidden_packages:
        assert importlib.util.find_spec(package_name) is None
