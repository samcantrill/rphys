from __future__ import annotations

import pytest

from rphys.data import Batch, FieldValue, Sample, UncollatePlan, uncollate_batch_fields
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.errors import CollatePolicyError, RemotePhysOperationError
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef
from rphys.ops import export
from rphys.ops.export import ExportTarget, sample_artifact_export_request


def test_stage13_uncollation_is_explicit_and_sample_granular() -> None:
    batch = Batch({"predictions/signal.bvp.predicted": FieldValue([0.1, 0.2])})

    with pytest.raises(CollatePolicyError):
        uncollate_batch_fields(batch, UncollatePlan(2))

    samples = uncollate_batch_fields(
        batch,
        UncollatePlan(2, ("predictions/signal.bvp.predicted",)),
    )

    assert len(samples) == 2
    assert all(isinstance(sample, Sample) for sample in samples)
    assert samples[0].require("predictions/signal.bvp.predicted") == 0.1
    assert samples[1].require("predictions/signal.bvp.predicted") == 0.2


def test_stage13_sample_artifact_export_requires_descriptor_evidence(tmp_path) -> None:
    sample = Sample({"predictions/signal.bvp.predicted": FieldValue(0.1)})
    source_record = RecordRef(
        DataSourceRef("source"),
        "record-001",
        {
            "signal.bvp.reference": FieldRef(
                "signal.bvp.reference",
                (ResourceRef("memory://record-001/reference", "memory"),),
                schema="signal.bvp.v1",
            )
        },
    )

    with pytest.raises(RemotePhysOperationError):
        sample_artifact_export_request(
            sample=sample,
            source_record=source_record,
            locators=("predictions/signal.bvp.predicted",),
            target=ExportTarget(ResourceRef(tmp_path.as_uri(), "file"), "exp-001"),
        )


def test_stage13_does_not_expose_prediction_export_or_storage_families() -> None:
    forbidden = [
        "PredictionExportPlan",
        "PredictionExportResult",
        "PredictionMaterializer",
        "PredictionMaterializationPlan",
        "PredictionMaterializationResult",
        "PredictionStore",
        "PredictionStorage",
    ]

    for name in forbidden:
        assert not hasattr(export, name)
