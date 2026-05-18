"""Private deterministic synthetic fixture catalog for Stage 14 tests.

The helpers in this module are test support only. They generate tiny,
license-safe descriptors and primitive payload evidence through public
``rphys`` objects. They are intentionally not exported from ``rphys`` or from
``tests.support`` as a package-level facade.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from rphys.data.fields import FieldSpec
from rphys.data.metadata import GROUP, SOURCE_ID, SPLIT, SUBJECT_ID
from rphys.datasources.adapters import DataSourceScanResult, DataSourceSpec
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.datasources.schemas import DataSourceSchema
from rphys.io.codecs import CodecRegistry
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef

from tests.support.synthetic_codecs import SyntheticCodec
from tests.support.synthetic_datasources import SyntheticScanAdapter

VIDEO_KEY = "video.rgb"
BVP_KEY = "signal.bvp.reference"
TIMESTAMPS_KEY = "timestamps.video"
MASK_KEY = "mask.face"
QUALITY_KEY = "quality.ppg"
LANDMARKS_KEY = "landmarks.face"
SIDECAR_KEY = "metadata.sidecar"
COMPOUND_KEY = "custom.synthetic.compound"

REQUIRED_FIELD_KEYS = (VIDEO_KEY, BVP_KEY, TIMESTAMPS_KEY)
OPTIONAL_FIELD_KEYS = (MASK_KEY, QUALITY_KEY, LANDMARKS_KEY, SIDECAR_KEY, COMPOUND_KEY)
ALL_FIELD_KEYS = (*REQUIRED_FIELD_KEYS, *OPTIONAL_FIELD_KEYS)

FIELD_LOCATORS = {
    VIDEO_KEY: "inputs/video.rgb",
    BVP_KEY: "targets/signal.bvp.reference",
    TIMESTAMPS_KEY: "metadata/timestamps.video",
    MASK_KEY: "inputs/mask.face",
    QUALITY_KEY: "metadata/quality.ppg",
    LANDMARKS_KEY: "metadata/landmarks.face",
    SIDECAR_KEY: "metadata/metadata.sidecar",
    COMPOUND_KEY: "inputs/custom.synthetic.compound",
}


@dataclass(frozen=True, slots=True)
class SyntheticFieldEvidence:
    """Expected facts for one generated field in one synthetic record."""

    key: str
    locator: str
    data_type: str
    schema: str
    payload: tuple[Any, ...]
    sample_rate_hz: float | None
    timestamps_s: tuple[float, ...]
    metadata: Mapping[str, object]

    @property
    def payload_fingerprint(self) -> str:
        """Stable digest for the primitive generated payload."""

        return _fingerprint(self.payload)


@dataclass(frozen=True, slots=True)
class SyntheticScenario:
    """Generated field-role-oriented datasource scenario for tests."""

    scenario_id: str
    datasources: tuple[DataSourceRef, ...]
    records: tuple[RecordRef, ...]
    field_evidence: Mapping[str, Mapping[str, SyntheticFieldEvidence]]
    payloads: Mapping[tuple[str, str], tuple[Any, ...]]

    def records_for_datasource(self, datasource_id: str) -> tuple[RecordRef, ...]:
        """Return records belonging to ``datasource_id`` in scan order."""

        return tuple(
            record
            for record in self.records
            if record.datasource.datasource_id == datasource_id
        )

    def datasource(self, datasource_id: str) -> DataSourceRef:
        """Return one datasource descriptor by stable identity."""

        for datasource in self.datasources:
            if datasource.datasource_id == datasource_id:
                return datasource
        raise KeyError(datasource_id)

    def spec_for(
        self,
        datasource_id: str,
        *,
        required_fields: Sequence[str] = REQUIRED_FIELD_KEYS,
    ) -> DataSourceSpec:
        """Build a descriptor-only public scan spec for one datasource."""

        return DataSourceSpec(
            self.datasource(datasource_id),
            required_fields=required_fields,
            metadata={"scenario_id": self.scenario_id},
        )

    def scan_result_for(self, datasource_id: str) -> DataSourceScanResult:
        """Return a public descriptor-only scan result for one datasource."""

        records = self.records_for_datasource(datasource_id)
        return SyntheticScanAdapter(
            records,
            validation_evidence={
                "fixture_catalog": "stage14.synthetic_catalog.v1",
                "scenario_id": self.scenario_id,
                "datasource_count": len(self.datasources),
                "record_count": len(records),
                "field_roles": {
                    key: locator for key, locator in FIELD_LOCATORS.items()
                },
            },
        ).scan(self.spec_for(datasource_id))

    def field(self, record_id: str, key: str) -> SyntheticFieldEvidence:
        """Return generated field evidence for ``record_id`` and ``key``."""

        return self.field_evidence[record_id][key]

    def payload_for(self, record_id: str, key: str) -> tuple[Any, ...]:
        """Return the deterministic primitive payload for a generated field."""

        return self.payloads[(record_id, key)]

    def codec_registry(
        self,
        *,
        record_id: str | None = None,
        field_keys: Iterable[str] = REQUIRED_FIELD_KEYS,
    ) -> CodecRegistry:
        """Build dependency-light codecs for a selected record's payloads.

        ``SyntheticCodec`` is key based, so this registry is intentionally used
        by focused tests that materialize one selected record at a time.
        """

        selected_record_id = record_id or self.records[0].record_id
        codecs = []
        for key in field_keys:
            evidence = self.field(selected_record_id, key)
            codecs.append(
                SyntheticCodec(
                    name=f"stage14-{key.replace('.', '-')}",
                    key=key,
                    data_type=evidence.data_type,
                    schema=evidence.schema,
                    payload=evidence.payload,
                )
            )
        return CodecRegistry(codecs)


def make_synthetic_scenario(
    *,
    scenario_id: str = "stage14-catalog",
    datasource_count: int = 2,
    subjects: Sequence[str] = ("subject-001", "subject-002"),
    records_per_subject: int = 2,
    include_optional_fields: bool = True,
) -> SyntheticScenario:
    """Create a deterministic multi-source catalog scenario.

    The scenario records stable datasource, subject, group, split, sampling,
    timestamp, URI, and payload-fingerprint evidence without loading real data.
    """

    if datasource_count <= 0:
        raise ValueError("datasource_count must be positive")
    if records_per_subject <= 0:
        raise ValueError("records_per_subject must be positive")
    if not subjects:
        raise ValueError("subjects must not be empty")

    field_keys = ALL_FIELD_KEYS if include_optional_fields else REQUIRED_FIELD_KEYS
    datasources: list[DataSourceRef] = []
    records: list[RecordRef] = []
    field_evidence: dict[str, dict[str, SyntheticFieldEvidence]] = {}
    payloads: dict[tuple[str, str], tuple[Any, ...]] = {}
    splits = _subject_splits(subjects)

    for datasource_index in range(datasource_count):
        datasource_id = f"synthetic-source-{datasource_index + 1:03d}"
        datasource = _datasource_ref(
            datasource_id,
            field_keys=field_keys,
            source_index=datasource_index,
        )
        datasources.append(datasource)
        for subject_index, subject_id in enumerate(subjects):
            group_id = f"cohort-{subject_index % 2 + 1}"
            for record_index in range(records_per_subject):
                record_id = (
                    f"{subject_id}/source-{datasource_index + 1:03d}/"
                    f"record-{record_index + 1:03d}"
                )
                record_fields: dict[str, FieldRef] = {}
                record_evidence: dict[str, SyntheticFieldEvidence] = {}
                for key in field_keys:
                    evidence = _field_evidence(
                        key,
                        datasource_index=datasource_index,
                        subject_index=subject_index,
                        record_index=record_index,
                    )
                    record_fields[key] = _field_ref(record_id, evidence)
                    record_evidence[key] = evidence
                    payloads[(record_id, key)] = evidence.payload
                records.append(
                    RecordRef(
                        datasource,
                        record_id,
                        record_fields,
                        metadata={
                            SUBJECT_ID: subject_id,
                            SOURCE_ID: datasource_id,
                            GROUP: group_id,
                            SPLIT: splits[subject_id],
                            "record_id": record_id,
                            "scenario_id": scenario_id,
                            "fixture_family": "stage14.synthetic_catalog",
                        },
                    )
                )
                field_evidence[record_id] = record_evidence

    return SyntheticScenario(
        scenario_id=scenario_id,
        datasources=tuple(datasources),
        records=tuple(records),
        field_evidence=MappingProxyType(
            {record_id: MappingProxyType(fields) for record_id, fields in field_evidence.items()}
        ),
        payloads=MappingProxyType(payloads),
    )


def _datasource_ref(
    datasource_id: str,
    *,
    field_keys: Sequence[str],
    source_index: int,
) -> DataSourceRef:
    fields = {
        key: FieldSpec(key, _field_data_type(key), _field_schema(key))
        for key in field_keys
    }
    return DataSourceRef(
        datasource_id,
        source=ResourceRef(
            f"memory://stage14/{datasource_id}",
            "memory",
            storage_options={"fixture": "stage14", "source_index": source_index},
        ),
        schema=DataSourceSchema(fields, metadata={SOURCE_ID: datasource_id}),
        metadata={
            SOURCE_ID: datasource_id,
            "fixture_family": "stage14.synthetic_catalog",
            "license": "synthetic",
        },
    )


def _field_ref(record_id: str, evidence: SyntheticFieldEvidence) -> FieldRef:
    resource_key = evidence.key.replace(".", "/")
    return FieldRef(
        evidence.key,
        (
            ResourceRef(
                f"memory://stage14/{record_id}/{resource_key}",
                "memory",
                storage_options={
                    "fixture": "stage14",
                    "payload_fingerprint": evidence.payload_fingerprint,
                },
            ),
        ),
        schema=evidence.schema,
        metadata={
            **evidence.metadata,
            "payload_fingerprint": evidence.payload_fingerprint,
        },
    )


def _field_evidence(
    key: str,
    *,
    datasource_index: int,
    subject_index: int,
    record_index: int,
) -> SyntheticFieldEvidence:
    if key == VIDEO_KEY:
        sample_count = 4
        frame_rate = 30.0
        timestamps = _timestamps(sample_count, frame_rate, offset=0.01 * datasource_index)
        payload = tuple(
            f"ds{datasource_index + 1}:sub{subject_index + 1}:rec{record_index + 1}:frame{frame}"
            for frame in range(sample_count)
        )
        metadata = {
            "field_role": FIELD_LOCATORS[key],
            "sample_rate_hz": frame_rate,
            "sample_count": sample_count,
            "duration_s": round(sample_count / frame_rate, 6),
            "timestamp_start_s": timestamps[0],
            "timestamp_step_s": round(1.0 / frame_rate, 6),
            "timestamp_drift_s": 0.0,
            "alignment_group": "video_bvp",
        }
        return SyntheticFieldEvidence(
            key,
            FIELD_LOCATORS[key],
            "video",
            _field_schema(key),
            payload,
            frame_rate,
            timestamps,
            MappingProxyType(metadata),
        )
    if key == BVP_KEY:
        sample_count = 4
        sample_rate = 30.0
        frequency_hz = 1.2 + 0.05 * subject_index
        phase = 0.1 * record_index
        amplitude = 0.6
        timestamps = _timestamps(sample_count, sample_rate, offset=0.01 * datasource_index)
        payload = _waveform(sample_count, sample_rate, frequency_hz, phase, amplitude)
        metadata = {
            "field_role": FIELD_LOCATORS[key],
            "sample_rate_hz": sample_rate,
            "sample_count": sample_count,
            "duration_s": round(sample_count / sample_rate, 6),
            "timestamp_start_s": timestamps[0],
            "timestamp_step_s": round(1.0 / sample_rate, 6),
            "timestamp_drift_s": 0.0,
            "alignment_group": "video_bvp",
            "waveform.frequency_hz": round(frequency_hz, 6),
            "waveform.phase_rad": round(phase, 6),
            "waveform.amplitude": amplitude,
            "heart_rate_bpm": round(frequency_hz * 60.0, 3),
        }
        return SyntheticFieldEvidence(
            key,
            FIELD_LOCATORS[key],
            "signal",
            _field_schema(key),
            payload,
            sample_rate,
            timestamps,
            MappingProxyType(metadata),
        )
    if key == TIMESTAMPS_KEY:
        sample_count = 4
        sample_rate = 30.0
        timestamps = _timestamps(sample_count, sample_rate, offset=0.01 * datasource_index)
        metadata = {
            "field_role": FIELD_LOCATORS[key],
            "sample_rate_hz": sample_rate,
            "sample_count": sample_count,
            "timestamp_start_s": timestamps[0],
            "timestamp_step_s": round(1.0 / sample_rate, 6),
            "timestamp_drift_s": 0.0,
            "alignment_group": "video_bvp",
        }
        return SyntheticFieldEvidence(
            key,
            FIELD_LOCATORS[key],
            "timestamps",
            _field_schema(key),
            timestamps,
            sample_rate,
            timestamps,
            MappingProxyType(metadata),
        )

    payload = _optional_payload(key, subject_index=subject_index, record_index=record_index)
    metadata = {
        "field_role": FIELD_LOCATORS[key],
        "sample_count": len(payload),
        "optional": True,
        "alignment_group": "video_bvp" if key == MASK_KEY else "sidecar",
    }
    return SyntheticFieldEvidence(
        key,
        FIELD_LOCATORS[key],
        _field_data_type(key),
        _field_schema(key),
        payload,
        None,
        (),
        MappingProxyType(metadata),
    )


def _subject_splits(subjects: Sequence[str]) -> dict[str, str]:
    split_cycle = ("train", "valid", "test")
    return {
        subject_id: split_cycle[index % len(split_cycle)]
        for index, subject_id in enumerate(subjects)
    }


def _timestamps(count: int, rate_hz: float, *, offset: float = 0.0) -> tuple[float, ...]:
    return tuple(round(offset + index / rate_hz, 6) for index in range(count))


def _waveform(
    count: int,
    sample_rate_hz: float,
    frequency_hz: float,
    phase_rad: float,
    amplitude: float,
) -> tuple[float, ...]:
    return tuple(
        round(
            amplitude
            * math.sin((2.0 * math.pi * frequency_hz * index / sample_rate_hz) + phase_rad),
            6,
        )
        for index in range(count)
    )


def _optional_payload(
    key: str,
    *,
    subject_index: int,
    record_index: int,
) -> tuple[Any, ...]:
    if key == MASK_KEY:
        return (1, 1, 0, 1)
    if key == QUALITY_KEY:
        return tuple(round(0.9 - 0.05 * record_index, 3) for _ in range(4))
    if key == LANDMARKS_KEY:
        return (
            (round(0.1 + 0.01 * subject_index, 3), 0.2),
            (0.3, round(0.4 + 0.01 * record_index, 3)),
        )
    if key == SIDECAR_KEY:
        return (f"sidecar-subject-{subject_index + 1}", f"record-{record_index + 1}")
    if key == COMPOUND_KEY:
        return (("video.rgb", "signal.bvp.reference"),)
    raise KeyError(key)


def _field_data_type(key: str) -> str:
    return {
        VIDEO_KEY: "video",
        BVP_KEY: "signal",
        TIMESTAMPS_KEY: "timestamps",
        MASK_KEY: "mask",
        QUALITY_KEY: "quality",
        LANDMARKS_KEY: "landmarks",
        SIDECAR_KEY: "metadata",
        COMPOUND_KEY: "metadata",
    }[key]


def _field_schema(key: str) -> str:
    return {
        VIDEO_KEY: "video.rgb.v1",
        BVP_KEY: "signal.bvp.v1",
        TIMESTAMPS_KEY: "timestamps.seconds.v1",
        MASK_KEY: "mask.face.v1",
        QUALITY_KEY: "quality.ppg.v1",
        LANDMARKS_KEY: "landmarks.face.v1",
        SIDECAR_KEY: "metadata.sidecar.v1",
        COMPOUND_KEY: "custom.synthetic.compound.v1",
    }[key]


def _fingerprint(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=list)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
