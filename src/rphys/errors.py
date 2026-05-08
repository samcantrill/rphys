"""Broad exception hierarchy for :mod:`rphys`.

The classes in this module are stable bases for package-level failures. Detailed
future errors should inherit from the closest broad base so callers can catch
domain errors without depending on lower-level backend exceptions.
"""

__all__ = [
    "RemotePhysDataError",
    "RemotePhysDatasetError",
    "RemotePhysError",
    "RemotePhysEvaluationError",
    "RemotePhysIOError",
    "RemotePhysTrainingError",
    "RemotePhysTransformError",
]


class RemotePhysError(Exception):
    """Base class for errors raised by public ``rphys`` contracts."""


class RemotePhysDataError(RemotePhysError):
    """Error raised for in-memory field, sample, or batch contract failures."""


class RemotePhysIOError(RemotePhysError):
    """Error raised for field reference, codec, or external IO failures."""


class RemotePhysDatasetError(RemotePhysError):
    """Error raised for dataset discovery, filtering, indexing, or split failures."""


class RemotePhysTransformError(RemotePhysError):
    """Error raised for transform, augmentation, check, export, or materialization failures."""


class RemotePhysTrainingError(RemotePhysError):
    """Error raised for method, learner, trainer, model, or loss failures."""


class RemotePhysEvaluationError(RemotePhysError):
    """Error raised for prediction, metric, aggregation, evaluation, or analysis failures."""
