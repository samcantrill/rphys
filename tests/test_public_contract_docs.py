"""Validation for the public architecture contract document."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "architecture" / "public-contracts.md"
RUNTIME_CORE = ROOT / "docs" / "data" / "runtime-core.md"
README = ROOT / "README.md"
LICENSE = ROOT / "LICENSE"


def _contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def test_contract_document_exists_and_is_linked_from_readme() -> None:
    assert CONTRACT.exists()
    assert "docs/architecture/public-contracts.md" in README.read_text(encoding="utf-8")


def test_contract_defines_api_labels_and_code_backed_docs() -> None:
    text = _contract_text()

    for phrase in (
        "Stable",
        "Provisional",
        "Private or internal",
        "Code-Backed Documentation",
        "Public API documentation should be backed by importable code and tests",
    ):
        assert phrase in text


def test_contract_names_first_wave_and_deferred_modules() -> None:
    text = _contract_text()

    for module_name in (
        "rphys.errors",
        "rphys.data",
        "rphys.io",
        "rphys.datasets",
        "rphys.transforms",
    ):
        assert module_name in text

    for module_name in (
        "rphys.methods",
        "rphys.models",
        "rphys.training",
        "rphys.losses",
        "rphys.evaluation",
        "rphys.analysis",
        "rphys.recipes",
        "rphys.stages",
        "rphys.ops",
        "rphys.testing",
    ):
        assert module_name in text


def test_contract_preserves_io_future_concepts() -> None:
    text = _contract_text()
    lower_text = text.lower()

    assert "`FieldRef`, `TemporalIndexSlice`, and `FieldView` are future `rphys.io`" in text
    assert "lazy requests" in lower_text
    assert "external field payloads" in lower_text


def test_runtime_core_doc_covers_phase_1_public_contracts() -> None:
    text = RUNTIME_CORE.read_text(encoding="utf-8")

    for phrase in (
        "Stable: `DataKey`",
        "Stable: `FieldSpec`",
        "Stable: `FieldValue`",
        "Stable for the exposed member: `CollatePolicy.LIST`",
        "Runtime And IO Boundary",
        "`FieldRef`, `TemporalIndexSlice`, and `FieldView` remain future `rphys.io`",
        "does not include `description`, `runtime_type`, coordinate frames",
        "Equality is object identity",
        "absent policy must fail",
        "RemotePhysDataError",
    ):
        assert phrase in text


def test_contract_defines_scientific_obligations() -> None:
    text = _contract_text()

    for phrase in (
        "shapes, units, dtypes",
        "Coordinate frames",
        "Sampling rates",
        "temporal alignment",
        "Normalization order",
        "Leakage risks",
        "Failure behavior for NaNs",
        "Validation tests",
        "Raw datasets must not be committed",
    ):
        assert phrase in text


def test_contract_defines_loom_boundary_extension_policy_and_registries() -> None:
    text = _contract_text()
    lower_text = text.lower()

    for phrase in (
        "`rphys` may depend on `loom`; `loom` must",
        "generic reproducible experiment infrastructure",
        "_target_",
        "Registries should be limited",
    ):
        assert phrase in text

    assert "symbolic name" in lower_text
    assert "scientific contract" in lower_text


def test_contract_defines_dependency_tooling_and_rights_policy() -> None:
    text = _contract_text()
    lower_text = text.lower()
    license_text = LICENSE.read_text(encoding="utf-8")

    for phrase in (
        "Base imports must stay lightweight",
        "Optional dependencies should be grouped by capability",
        "Python 3.12",
        'requires-python = ">=3.12"',
        "No public-use license has been selected",
    ):
        assert phrase in text

    assert "`uv.lock` is committed" in text
    assert "all rights reserved" in lower_text
    assert "All rights reserved" in license_text
    assert "not granted permission" in license_text
