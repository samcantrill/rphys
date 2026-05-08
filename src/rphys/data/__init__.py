"""In-memory field-centric runtime contracts for ``rphys``.

Phase 1 exposes the stable field identity and loaded-value contracts used by
later sample, batch, dataset IO, transform, learning, and evaluation packages.
Lazy IO references, Sample/Batch containers, data-object hooks, sample
contracts, and executable collation land in later accepted phases.
"""

from rphys.data.collation import CollatePolicy
from rphys.data.fields import FieldSpec, FieldValue
from rphys.data.keys import (
    ANNOTATION_NAMESPACE,
    BODY_NAMESPACE,
    CAMERA_NAMESPACE,
    CUSTOM_NAMESPACE,
    FACE_NAMESPACE,
    LABEL_NAMESPACE,
    PREDICTION_NAMESPACE,
    QUALITY_NAMESPACE,
    SIGNAL_NAMESPACE,
    STANDARD_NAMESPACES,
    TIMESTAMPS_NAMESPACE,
    VIDEO_NAMESPACE,
    VIEW_NAMESPACE,
    DataKey,
)

__all__ = [
    "ANNOTATION_NAMESPACE",
    "BODY_NAMESPACE",
    "CAMERA_NAMESPACE",
    "CUSTOM_NAMESPACE",
    "CollatePolicy",
    "DataKey",
    "FACE_NAMESPACE",
    "FieldSpec",
    "FieldValue",
    "LABEL_NAMESPACE",
    "PREDICTION_NAMESPACE",
    "QUALITY_NAMESPACE",
    "SIGNAL_NAMESPACE",
    "STANDARD_NAMESPACES",
    "TIMESTAMPS_NAMESPACE",
    "VIDEO_NAMESPACE",
    "VIEW_NAMESPACE",
]
