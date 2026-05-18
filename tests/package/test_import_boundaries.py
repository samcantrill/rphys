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
    "lightning",
    "matplotlib",
    "numpy",
    "pandas",
    "pytorch_lightning",
    "scipy",
    "torch",
    "torchmetrics",
]
LIGHTWEIGHT_IMPORTS = [
    "rphys",
    "rphys.analysis",
    "rphys.analysis.reports",
    "rphys.analysis.visualization",
    "rphys.collections",
    "rphys.data",
    "rphys.data.collation",
    "rphys.data.collections",
    "rphys.data.containers",
    "rphys.data.contracts",
    "rphys.data.fields",
    "rphys.data.keys",
    "rphys.data.locators",
    "rphys.data.metadata",
    "rphys.data.objects",
    "rphys.data.output",
    "rphys.data.sample_builders",
    "rphys.data.sample_fields",
    "rphys.data.schemas",
    "rphys.data.splits",
    "rphys.data.types",
    "rphys.data.uncollation",
    "rphys.datasources",
    "rphys.datasources.adapters",
    "rphys.datasources.cache",
    "rphys.datasources.datapath",
    "rphys.datasources.derived",
    "rphys.datasources.filters",
    "rphys.datasources.indexes",
    "rphys.datasources.index_items",
    "rphys.datasources.prepared",
    "rphys.datasources.sources",
    "rphys.datasources.torch",
    "rphys.datasources.refs",
    "rphys.datasources.schemas",
    "rphys.datasources.splits",
    "rphys.datasources.validation",
    "rphys.errors",
    "rphys.evaluation",
    "rphys.io",
    "rphys.io.codecs",
    "rphys.io.fields",
    "rphys.io.indexes",
    "rphys.io.resources",
    "rphys.learning",
    "rphys.learning.context",
    "rphys.learning.core",
    "rphys.learning.modes",
    "rphys.learning.output",
    "rphys.learning.supervised",
    "rphys.losses",
    "rphys.methods",
    "rphys.methods.adapters",
    "rphys.methods.context",
    "rphys.methods.core",
    "rphys.methods.output",
    "rphys.methods.state",
    "rphys.metrics",
    "rphys.models",
    "rphys.models.core",
    "rphys.nn",
    "rphys.objectives",
    "rphys.ops",
    "rphys.ops.export",
    "rphys.prediction",
    "rphys.training",
    "rphys.training.backend",
    "rphys.training.core",
    "rphys.training.events",
    "rphys.training.experimental",
    "rphys.training.lightning",
    "rphys.training.plan",
    "rphys.training.profiling",
    "rphys.training.results",
    "rphys.training.tiers",
]

STAGE_12_LEARNING_IMPORTS = [
    "rphys.learning",
    "rphys.learning.context",
    "rphys.learning.core",
    "rphys.learning.modes",
    "rphys.learning.output",
    "rphys.learning.supervised",
]

STAGE_12_TRAINING_IMPORTS = [
    "rphys.training",
    "rphys.training.backend",
    "rphys.training.core",
    "rphys.training.checkpoint",
    "rphys.training.events",
    "rphys.training.experimental",
    "rphys.training.lightning",
    "rphys.training.plan",
    "rphys.training.profiling",
    "rphys.training.policies",
    "rphys.training.probes",
    "rphys.training.results",
    "rphys.training.tiers",
]

STAGE_13_SCAFFOLD_IMPORTS = [
    "rphys.prediction",
    "rphys.evaluation",
    "rphys.analysis",
]

STAGE_11_IMPORTS = [
    "rphys.collections",
    "rphys.data",
    "rphys.data.collections",
    "rphys.losses",
    "rphys.objectives",
    "rphys.metrics",
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


def test_stage_11_package_imports_do_not_load_forbidden_dependencies() -> None:
    imports = ", ".join(repr(module_name) for module_name in STAGE_11_IMPORTS)
    heavy_modules = ", ".join(repr(module_name) for module_name in HEAVY_OPTIONAL_MODULES)
    forbidden = ", ".join(
        repr(module_name)
        for module_name in [
            "rphys.analysis",
            "rphys.datasources",
            "rphys.evaluation",
            "rphys.io",
            "rphys.learning",
            "rphys.methods",
            "rphys.models",
            "rphys.ops",
            "rphys.ops.export",
            "rphys.prediction",
            "rphys.training",
            "tests.support",
        ]
    )
    script = textwrap.dedent(
        f"""
        import importlib
        import sys

        for module_name in [{imports}]:
            importlib.import_module(module_name)

        forbidden = sorted(
            name for name in [{forbidden}]
            if name in sys.modules
        )
        if forbidden:
            raise SystemExit("forbidden modules loaded: " + ", ".join(forbidden))

        heavy = sorted(
            name for name in [{heavy_modules}]
            if name in sys.modules
        )
        if heavy:
            raise SystemExit("heavy optional modules loaded: " + ", ".join(heavy))
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


def test_stage_12_learning_imports_do_not_load_training_or_frameworks() -> None:
    imports = ", ".join(repr(module_name) for module_name in STAGE_12_LEARNING_IMPORTS)
    forbidden_modules = [
        "rphys.training",
        "lightning",
        "pytorch_lightning",
        "jax",
        "torch",
        "torchmetrics",
        "wandb",
        "tensorboard",
        "av",
        "cv2",
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "tests.support",
    ]
    forbidden = ", ".join(repr(module_name) for module_name in forbidden_modules)
    script = textwrap.dedent(
        f"""
        import importlib
        import sys

        for module_name in [{imports}]:
            importlib.import_module(module_name)

        forbidden = sorted(
            name for name in [{forbidden}]
            if name in sys.modules
        )
        if forbidden:
            raise SystemExit("forbidden modules loaded: " + ", ".join(forbidden))
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


def test_stage_12_learning_source_does_not_import_training() -> None:
    violations: list[str] = []

    for source_path in sorted((REPO_ROOT / "src" / "rphys" / "learning").glob("*.py")):
        source_text = source_path.read_text(encoding="utf-8")
        if "rphys.training" in source_text:
            violations.append(f"{source_path.relative_to(REPO_ROOT)} imports rphys.training")

    assert violations == []


def test_stage_12_training_imports_do_not_load_frameworks_or_datasources() -> None:
    imports = ", ".join(repr(module_name) for module_name in STAGE_12_TRAINING_IMPORTS)
    forbidden_modules = [
        "rphys.datasources",
        "lightning",
        "pytorch_lightning",
        "jax",
        "torch",
        "torchmetrics",
        "wandb",
        "tensorboard",
        "av",
        "cv2",
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "tests.support",
    ]
    forbidden = ", ".join(repr(module_name) for module_name in forbidden_modules)
    script = textwrap.dedent(
        f"""
        import importlib
        import sys

        for module_name in [{imports}]:
            importlib.import_module(module_name)

        forbidden = sorted(
            name for name in [{forbidden}]
            if name in sys.modules
        )
        if forbidden:
            raise SystemExit("forbidden modules loaded: " + ", ".join(forbidden))
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


def test_stage_13_scaffold_imports_do_not_load_backend_workflow_or_export_dependencies() -> None:
    imports = ", ".join(repr(module_name) for module_name in STAGE_13_SCAFFOLD_IMPORTS)
    forbidden_modules = [
        "rphys.datasources",
        "rphys.datasources.sources",
        "rphys.io.codecs",
        "rphys.methods",
        "rphys.ops.export",
        "rphys.training",
        "loom",
        "lightning",
        "pytorch_lightning",
        "jax",
        "torch",
        "torchmetrics",
        "wandb",
        "tensorboard",
        "av",
        "cv2",
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "tests.support",
    ]
    forbidden = ", ".join(repr(module_name) for module_name in forbidden_modules)
    script = textwrap.dedent(
        f"""
        import importlib
        import sys

        for module_name in [{imports}]:
            importlib.import_module(module_name)

        forbidden = sorted(
            name for name in [{forbidden}]
            if name in sys.modules
        )
        if forbidden:
            raise SystemExit("forbidden modules loaded: " + ", ".join(forbidden))
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


def test_stage_11_modules_do_not_import_cross_package_private_helpers() -> None:
    source_paths = [
        REPO_ROOT / "src" / "rphys" / "collections.py",
        REPO_ROOT / "src" / "rphys" / "data" / "collections.py",
        *((REPO_ROOT / "src" / "rphys" / "losses").glob("*.py")),
        *((REPO_ROOT / "src" / "rphys" / "objectives").glob("*.py")),
        *((REPO_ROOT / "src" / "rphys" / "metrics").glob("*.py")),
    ]
    private_helper_imports = [
        "from rphys.losses._validation",
        "import rphys.losses._validation",
        "from rphys.objectives._validation",
        "import rphys.objectives._validation",
        "from rphys.metrics._validation",
        "import rphys.metrics._validation",
    ]
    violations: list[str] = []

    for source_path in sorted(source_paths):
        source_text = source_path.read_text(encoding="utf-8")
        for forbidden_import in private_helper_imports:
            if forbidden_import in source_text:
                violations.append(
                    f"{source_path.relative_to(REPO_ROOT)} contains {forbidden_import!r}"
                )

    assert violations == []


def test_package_source_does_not_import_or_call_package_level_random() -> None:
    forbidden_tokens = ("import random", "from random", "random.")
    violations: list[str] = []

    for source_path in sorted((REPO_ROOT / "src" / "rphys").rglob("*.py")):
        source_text = source_path.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            if token in source_text:
                violations.append(f"{source_path.relative_to(REPO_ROOT)} contains {token!r}")

    assert violations == []


def test_rphys_does_not_define_generic_workflow_or_artifact_runtime_packages() -> None:
    forbidden_packages = [
        "rphys.artifacts",
        "rphys.datasets",
        "rphys.fixtures",
        "rphys.stages",
        "rphys.testing",
        "rphys.workflow",
        "rphys.workflows",
    ]

    for package_name in forbidden_packages:
        assert importlib.util.find_spec(package_name) is None


def test_production_source_does_not_import_test_support_modules() -> None:
    violations: list[str] = []

    for source_path in sorted((REPO_ROOT / "src" / "rphys").rglob("*.py")):
        source_text = source_path.read_text(encoding="utf-8")
        if "tests.support" in source_text:
            violations.append(f"{source_path.relative_to(REPO_ROOT)} imports tests.support")

    assert violations == []


def test_codec_contract_import_does_not_load_datasource_or_runtime_builders() -> None:
    script = textwrap.dedent(
        """
        import importlib
        import sys

        importlib.import_module("rphys.io.codecs")

        forbidden = sorted(
            name for name in [
                "rphys.datasources",
                "rphys.datasources.refs",
                "rphys.datasources.schemas",
                "rphys.datasources.index_items",
                "rphys.data.sample_fields",
                "rphys.data.sample_builders",
                "tests.support",
            ]
            if name in sys.modules
        )
        if forbidden:
            raise SystemExit("forbidden modules loaded: " + ", ".join(forbidden))
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


def test_sample_field_import_does_not_load_datasource_builders_or_test_support() -> None:
    script = textwrap.dedent(
        """
        import importlib
        import sys

        importlib.import_module("rphys.data.sample_fields")

        forbidden = sorted(
            name for name in [
                "rphys.datasources",
                "rphys.datasources.refs",
                "rphys.datasources.schemas",
                "rphys.datasources.index_items",
                "rphys.data.sample_builders",
                "tests.support",
            ]
            if name in sys.modules
        )
        if forbidden:
            raise SystemExit("forbidden modules loaded: " + ", ".join(forbidden))
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


def test_sample_builder_import_does_not_load_test_support_or_heavy_modules() -> None:
    heavy_modules = ", ".join(repr(module_name) for module_name in HEAVY_OPTIONAL_MODULES)
    script = textwrap.dedent(
        f"""
        import importlib
        import sys

        importlib.import_module("rphys.data.sample_builders")

        forbidden = sorted(
            name for name in [
                "tests.support",
                "tests.support.synthetic_codecs",
                {heavy_modules},
            ]
            if name in sys.modules
        )
        if forbidden:
            raise SystemExit("forbidden modules loaded: " + ", ".join(forbidden))
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


def test_ops_import_does_not_load_heavy_or_optional_runtime_modules() -> None:
    heavy_modules = ", ".join(repr(module_name) for module_name in HEAVY_OPTIONAL_MODULES)
    forbidden = ", ".join(
        repr(module_name)
        for module_name in [
            "rphys.data",
            "rphys.datasources",
            "rphys.io",
            "rphys.io.codecs",
            "rphys.io.fields",
            "tests.support",
        ]
    )
    script = textwrap.dedent(
        f"""
        import importlib
        import sys

        importlib.import_module("rphys.ops")
        importlib.import_module("rphys.ops.contracts")
        importlib.import_module("rphys.ops.context")
        importlib.import_module("rphys.ops.core")
        importlib.import_module("rphys.ops.kernels")
        importlib.import_module("rphys.ops.pipelines")

        forbidden = sorted(
            name for name in [{forbidden}]
            if name in sys.modules
        )
        if forbidden:
            raise SystemExit("forbidden modules loaded: " + ", ".join(forbidden))

        heavy = sorted(
            name for name in [{heavy_modules}]
            if name in sys.modules
        )
        if heavy:
            raise SystemExit("heavy optional modules loaded: " + ", ".join(heavy))
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


def test_ops_sample_import_does_not_load_runtime_or_heavy_modules() -> None:
    heavy_modules = ", ".join(repr(module_name) for module_name in HEAVY_OPTIONAL_MODULES)
    forbidden = ", ".join(
        repr(module_name)
        for module_name in [
            "rphys.data.sample_builders",
            "rphys.data.sample_fields",
            "rphys.datasources",
            "rphys.datasources.adapters",
            "rphys.datasources.filters",
            "rphys.datasources.indexes",
            "rphys.datasources.index_items",
            "rphys.datasources.refs",
            "rphys.datasources.schemas",
            "rphys.datasources.splits",
            "rphys.datasources.validation",
            "rphys.io",
            "rphys.io.codecs",
            "rphys.io.fields",
            "rphys.io.indexes",
            "rphys.io.resources",
            "rphys.models",
            "rphys.training",
            "tests.support",
        ]
    )
    script = textwrap.dedent(
        f"""
        import importlib
        import sys

        importlib.import_module("rphys.ops.sample")

        forbidden = sorted(
            name for name in [{forbidden}]
            if name in sys.modules
        )
        if forbidden:
            raise SystemExit("forbidden modules loaded: " + ", ".join(forbidden))

        heavy = sorted(
            name for name in [{heavy_modules}]
            if name in sys.modules
        )
        if heavy:
            raise SystemExit("heavy optional modules loaded: " + ", ".join(heavy))
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


def test_stage_10_method_imports_do_not_load_training_export_or_heavy_modules() -> None:
    heavy_modules = ", ".join(repr(module_name) for module_name in HEAVY_OPTIONAL_MODULES)
    forbidden = ", ".join(
        repr(module_name)
        for module_name in [
            "rphys.analysis",
            "rphys.datasources",
            "rphys.evaluation",
            "rphys.io",
            "rphys.learning",
            "rphys.losses",
            "rphys.metrics",
            "rphys.models",
            "rphys.objectives",
            "rphys.ops",
            "rphys.ops.export",
            "rphys.prediction",
            "rphys.training",
            "tests.support",
        ]
    )
    script = textwrap.dedent(
        f"""
        import importlib
        import sys

        importlib.import_module("rphys.methods")
        importlib.import_module("rphys.methods.adapters")
        importlib.import_module("rphys.methods.context")
        importlib.import_module("rphys.methods.core")
        importlib.import_module("rphys.methods.output")
        importlib.import_module("rphys.methods.state")

        forbidden = sorted(
            name for name in [{forbidden}]
            if name in sys.modules
        )
        if forbidden:
            raise SystemExit("forbidden modules loaded: " + ", ".join(forbidden))

        heavy = sorted(
            name for name in [{heavy_modules}]
            if name in sys.modules
        )
        if heavy:
            raise SystemExit("heavy optional modules loaded: " + ", ".join(heavy))
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


def test_stage_10_model_imports_stay_below_batch_and_heavy_modules() -> None:
    heavy_modules = ", ".join(repr(module_name) for module_name in HEAVY_OPTIONAL_MODULES)
    forbidden = ", ".join(
        repr(module_name)
        for module_name in [
            "rphys.data",
            "rphys.datasources",
            "rphys.io",
            "rphys.methods",
            "rphys.ops",
            "rphys.training",
            "tests.support",
        ]
    )
    script = textwrap.dedent(
        f"""
        import importlib
        import sys

        importlib.import_module("rphys.models")
        importlib.import_module("rphys.models.core")

        forbidden = sorted(
            name for name in [{forbidden}]
            if name in sys.modules
        )
        if forbidden:
            raise SystemExit("forbidden modules loaded: " + ", ".join(forbidden))

        heavy = sorted(
            name for name in [{heavy_modules}]
            if name in sys.modules
        )
        if heavy:
            raise SystemExit("heavy optional modules loaded: " + ", ".join(heavy))
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


def test_deferred_packages_do_not_define_duplicate_vocabulary_surfaces() -> None:
    deferred_packages = [
        "rphys.analysis",
        "rphys.datasources",
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
    vocabulary_names = [
        "DataKey",
        "FieldLocator",
        "FieldRole",
        "SchemaName",
        "DataType",
        "MetadataKey",
        "SplitName",
    ]

    for package_name in deferred_packages:
        package = __import__(package_name, fromlist=["__all__"])
        for vocabulary_name in vocabulary_names:
            assert not hasattr(package, vocabulary_name)


def test_stage_5_private_synthetic_fixtures_are_not_public_imports() -> None:
    import rphys
    import rphys.datasources

    assert importlib.util.find_spec("tests.support.synthetic_datasources") is not None

    forbidden_packages = [
        "rphys.datasources.synthetic",
        "rphys.datasources.synthetic_datasources",
        "rphys.synthetic_datasources",
    ]
    for package_name in forbidden_packages:
        assert importlib.util.find_spec(package_name) is None

    for public_name in [
        "SyntheticDataSource",
        "SyntheticDataSourceAdapter",
        "ConcatDataSourceIndex",
    ]:
        assert not hasattr(rphys, public_name)
        assert not hasattr(rphys.datasources, public_name)
