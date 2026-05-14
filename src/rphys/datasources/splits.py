"""Candidate-level grouping and explicit split assignment.

Grouping extracts named group values from selected ``IndexCandidate`` records.
Split assignment uses explicit group-to-split mappings and detects leakage at
the selected-candidate level. It does not implement trainer/evaluator modes,
implicit ratios, post-split filtering, or final datasource-index persistence.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from rphys.data.metadata import MetadataKey
from rphys.data.splits import SplitName
from rphys.errors import InvalidGroupAssignmentError, InvalidSplitAssignmentError

from .indexes import IndexCandidate, IndexCandidateView

__all__ = [
    "CandidateGroupAssignment",
    "GroupBuilder",
    "GroupPlan",
    "GroupResult",
    "SplitAssignment",
    "SplitBuilder",
    "SplitPlan",
    "SplitResult",
]


@dataclass(frozen=True, init=False, slots=True)
class GroupPlan:
    """Named candidate-group extraction plan.

    ``groups`` maps analysis group names such as ``subject`` or ``source`` to
    metadata keys. Required groups fail loudly when missing from a candidate's
    candidate metadata or record metadata.
    """

    groups: Mapping[str, MetadataKey]
    required_groups: tuple[str, ...]

    def __init__(
        self,
        groups: Mapping[str, MetadataKey | str],
        *,
        required_groups: Sequence[str] | None = None,
    ) -> None:
        coerced = _coerce_group_mapping(groups)
        required = (
            tuple(coerced)
            if required_groups is None
            else _coerce_group_names(required_groups)
        )
        unknown = set(required) - set(coerced)
        if unknown:
            raise InvalidGroupAssignmentError(
                "GroupPlan required_groups must be declared in groups.",
                field="required_groups",
                unknown=sorted(unknown),
            )
        object.__setattr__(self, "groups", MappingProxyType(coerced))
        object.__setattr__(self, "required_groups", required)


GroupPlan.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class CandidateGroupAssignment:
    """Named group values for one selected index candidate."""

    candidate_id: str
    groups: Mapping[str, str]

    def __init__(self, candidate_id: str, groups: Mapping[str, str]) -> None:
        object.__setattr__(self, "candidate_id", _non_empty_string(candidate_id))
        object.__setattr__(
            self,
            "groups",
            MappingProxyType(_coerce_string_mapping(groups, field="groups")),
        )


CandidateGroupAssignment.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class GroupResult:
    """Group extraction result for a selected candidate view."""

    assignments: Mapping[str, CandidateGroupAssignment]
    rejected_candidate_ids: Mapping[str, str]
    counts: Mapping[str, Mapping[str, int]]

    def __init__(
        self,
        assignments: Mapping[str, CandidateGroupAssignment],
        *,
        rejected_candidate_ids: Mapping[str, str] | None = None,
    ) -> None:
        assignment_map = _coerce_group_assignments(assignments)
        object.__setattr__(self, "assignments", MappingProxyType(assignment_map))
        object.__setattr__(
            self,
            "rejected_candidate_ids",
            MappingProxyType(
                _coerce_reason_mapping(
                    rejected_candidate_ids,
                    error_type=InvalidGroupAssignmentError,
                )
            ),
        )
        object.__setattr__(
            self,
            "counts",
            MappingProxyType(_group_counts(assignment_map.values())),
        )


GroupResult.__hash__ = None  # type: ignore[assignment]


class GroupBuilder:
    """Extract named groups from selected candidates."""

    def __init__(self, plan: GroupPlan) -> None:
        if not isinstance(plan, GroupPlan):
            raise InvalidGroupAssignmentError(
                "GroupBuilder plan must be a GroupPlan.",
                field="plan",
                actual=type(plan).__name__,
            )
        self.plan = plan

    def build(self, candidate_view: IndexCandidateView) -> GroupResult:
        """Return group assignments for selected candidates."""

        if not isinstance(candidate_view, IndexCandidateView):
            raise InvalidGroupAssignmentError(
                "GroupBuilder.build requires an IndexCandidateView.",
                field="candidate_view",
                actual=type(candidate_view).__name__,
            )
        assignments: dict[str, CandidateGroupAssignment] = {}
        rejected: dict[str, str] = {}
        for candidate in candidate_view.candidates:
            groups: dict[str, str] = {}
            missing: list[str] = []
            for group_name, metadata_key in self.plan.groups.items():
                value = _metadata_value(candidate, metadata_key)
                if value is None:
                    if group_name in self.plan.required_groups:
                        missing.append(group_name)
                    continue
                groups[group_name] = value
            if missing:
                rejected[candidate.candidate_id] = "missing_groups:" + ",".join(
                    sorted(missing)
                )
                continue
            assignments[candidate.candidate_id] = CandidateGroupAssignment(
                candidate.candidate_id,
                groups,
            )
        if rejected:
            raise InvalidGroupAssignmentError(
                "Required candidate groups are missing.",
                rejected_candidate_ids=rejected,
            )
        return GroupResult(assignments)


@dataclass(frozen=True, init=False, slots=True)
class SplitPlan:
    """Explicit group-disjoint split assignment plan."""

    split_group: str
    group_to_split: Mapping[str, SplitName]

    def __init__(
        self,
        *,
        split_group: str,
        group_to_split: Mapping[str, SplitName | str],
    ) -> None:
        object.__setattr__(self, "split_group", _non_empty_string(split_group))
        object.__setattr__(
            self,
            "group_to_split",
            MappingProxyType(_coerce_group_to_split(group_to_split)),
        )


SplitPlan.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class SplitAssignment:
    """Split assignment plus preserved analysis groups for one candidate."""

    candidate_id: str
    split: SplitName
    split_group: str
    split_group_value: str
    groups: Mapping[str, str]

    def __init__(
        self,
        candidate_id: str,
        *,
        split: SplitName | str,
        split_group: str,
        split_group_value: str,
        groups: Mapping[str, str],
    ) -> None:
        object.__setattr__(self, "candidate_id", _non_empty_string(candidate_id))
        object.__setattr__(self, "split", SplitName(split))
        object.__setattr__(self, "split_group", _non_empty_string(split_group))
        object.__setattr__(
            self,
            "split_group_value",
            _non_empty_string(split_group_value),
        )
        object.__setattr__(
            self,
            "groups",
            MappingProxyType(_coerce_string_mapping(groups, field="groups")),
        )


SplitAssignment.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class SplitResult:
    """Explicit split assignment result for grouped selected candidates."""

    assignments: Mapping[str, SplitAssignment]
    counts: Mapping[SplitName, int]
    rejected_candidate_ids: Mapping[str, str]

    def __init__(
        self,
        assignments: Mapping[str, SplitAssignment],
        *,
        rejected_candidate_ids: Mapping[str, str] | None = None,
    ) -> None:
        assignment_map = _coerce_split_assignments(assignments)
        object.__setattr__(self, "assignments", MappingProxyType(assignment_map))
        object.__setattr__(
            self,
            "counts",
            MappingProxyType(_split_counts(assignment_map.values())),
        )
        object.__setattr__(
            self,
            "rejected_candidate_ids",
            MappingProxyType(
                _coerce_reason_mapping(
                    rejected_candidate_ids,
                    error_type=InvalidSplitAssignmentError,
                )
            ),
        )


SplitResult.__hash__ = None  # type: ignore[assignment]


class SplitBuilder:
    """Assign candidates to explicit group-disjoint splits."""

    def __init__(self, plan: SplitPlan) -> None:
        if not isinstance(plan, SplitPlan):
            raise InvalidSplitAssignmentError(
                "SplitBuilder plan must be a SplitPlan.",
                field="plan",
                actual=type(plan).__name__,
            )
        self.plan = plan

    def build(self, group_result: GroupResult) -> SplitResult:
        """Assign splits and fail if required groups are missing."""

        if not isinstance(group_result, GroupResult):
            raise InvalidSplitAssignmentError(
                "SplitBuilder.build requires a GroupResult.",
                field="group_result",
                actual=type(group_result).__name__,
            )
        assignments: dict[str, SplitAssignment] = {}
        group_splits: dict[str, SplitName] = {}
        rejected: dict[str, str] = {}
        for candidate_id, group_assignment in group_result.assignments.items():
            if self.plan.split_group not in group_assignment.groups:
                rejected[candidate_id] = "missing_split_group:" + self.plan.split_group
                continue
            group_value = group_assignment.groups[self.plan.split_group]
            split = self.plan.group_to_split.get(group_value)
            if split is None:
                rejected[candidate_id] = "unassigned_split_group:" + group_value
                continue
            prior = group_splits.setdefault(group_value, split)
            if prior != split:
                raise InvalidSplitAssignmentError(
                    "Split group value maps to multiple splits.",
                    split_group=self.plan.split_group,
                    group_value=group_value,
                    prior=str(prior),
                    current=str(split),
                )
            assignments[candidate_id] = SplitAssignment(
                candidate_id,
                split=split,
                split_group=self.plan.split_group,
                split_group_value=group_value,
                groups=group_assignment.groups,
            )
        if rejected:
            raise InvalidSplitAssignmentError(
                "Candidates are missing explicit split assignments.",
                rejected_candidate_ids=rejected,
            )
        return SplitResult(assignments)


def _metadata_value(candidate: IndexCandidate, key: MetadataKey) -> str | None:
    value = candidate.metadata.get(key)
    if value is None:
        value = candidate.record.metadata.get(key)
    if value is None:
        value = candidate.record.datasource.metadata.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise InvalidGroupAssignmentError(
            "Candidate group metadata values must be non-empty strings.",
            candidate_id=candidate.candidate_id,
            metadata_key=str(key),
            actual=type(value).__name__,
        )
    return value


def _coerce_group_mapping(
    groups: Mapping[str, MetadataKey | str],
) -> dict[str, MetadataKey]:
    if not isinstance(groups, Mapping) or not groups:
        raise InvalidGroupAssignmentError(
            "GroupPlan groups must be a non-empty mapping.",
            field="groups",
            actual=type(groups).__name__,
        )
    return {
        _non_empty_string(name): MetadataKey(key)
        for name, key in groups.items()
    }


def _coerce_group_names(values: Sequence[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise InvalidGroupAssignmentError(
            "GroupPlan required_groups must be a sequence.",
            field="required_groups",
            actual=type(values).__name__,
        )
    names = tuple(_non_empty_string(value) for value in values)
    if len(set(names)) != len(names):
        raise InvalidGroupAssignmentError(
            "GroupPlan required_groups must not contain duplicates.",
            field="required_groups",
            values=list(names),
        )
    return names


def _coerce_group_to_split(
    values: Mapping[str, SplitName | str],
) -> dict[str, SplitName]:
    if not isinstance(values, Mapping) or not values:
        raise InvalidSplitAssignmentError(
            "SplitPlan group_to_split must be a non-empty mapping.",
            field="group_to_split",
            actual=type(values).__name__,
        )
    return {
        _non_empty_string(group_value): SplitName(split)
        for group_value, split in values.items()
    }


def _coerce_group_assignments(
    assignments: Mapping[str, CandidateGroupAssignment],
) -> dict[str, CandidateGroupAssignment]:
    if not isinstance(assignments, Mapping):
        raise InvalidGroupAssignmentError(
            "GroupResult assignments must be a mapping.",
            field="assignments",
            actual=type(assignments).__name__,
        )
    result: dict[str, CandidateGroupAssignment] = {}
    for candidate_id, assignment in assignments.items():
        candidate_id = _non_empty_string(candidate_id)
        if not isinstance(assignment, CandidateGroupAssignment):
            raise InvalidGroupAssignmentError(
                "GroupResult assignments must contain CandidateGroupAssignment values.",
                field="assignments",
                actual=type(assignment).__name__,
            )
        if assignment.candidate_id != candidate_id:
            raise InvalidGroupAssignmentError(
                "GroupResult assignment key must match candidate_id.",
                field="assignments",
                key=candidate_id,
                candidate_id=assignment.candidate_id,
            )
        result[candidate_id] = assignment
    return result


def _coerce_split_assignments(
    assignments: Mapping[str, SplitAssignment],
) -> dict[str, SplitAssignment]:
    if not isinstance(assignments, Mapping):
        raise InvalidSplitAssignmentError(
            "SplitResult assignments must be a mapping.",
            field="assignments",
            actual=type(assignments).__name__,
        )
    result: dict[str, SplitAssignment] = {}
    seen_groups: dict[str, SplitName] = {}
    for candidate_id, assignment in assignments.items():
        candidate_id = _non_empty_string(candidate_id)
        if not isinstance(assignment, SplitAssignment):
            raise InvalidSplitAssignmentError(
                "SplitResult assignments must contain SplitAssignment values.",
                field="assignments",
                actual=type(assignment).__name__,
            )
        if assignment.candidate_id != candidate_id:
            raise InvalidSplitAssignmentError(
                "SplitResult assignment key must match candidate_id.",
                field="assignments",
                key=candidate_id,
                candidate_id=assignment.candidate_id,
            )
        prior = seen_groups.setdefault(assignment.split_group_value, assignment.split)
        if prior != assignment.split:
            raise InvalidSplitAssignmentError(
                "Split leakage detected for split group value.",
                split_group=assignment.split_group,
                split_group_value=assignment.split_group_value,
                prior=str(prior),
                current=str(assignment.split),
            )
        result[candidate_id] = assignment
    return result


def _group_counts(
    assignments: Sequence[CandidateGroupAssignment],
) -> dict[str, Mapping[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for assignment in assignments:
        for group_name, group_value in assignment.groups.items():
            counts.setdefault(group_name, {})
            counts[group_name][group_value] = counts[group_name].get(group_value, 0) + 1
    return {group: MappingProxyType(values) for group, values in counts.items()}


def _split_counts(assignments: Sequence[SplitAssignment]) -> dict[SplitName, int]:
    counts: dict[SplitName, int] = {}
    for assignment in assignments:
        counts[assignment.split] = counts.get(assignment.split, 0) + 1
    return counts


def _coerce_reason_mapping(
    value: Mapping[str, str] | None,
    *,
    error_type: type[InvalidGroupAssignmentError | InvalidSplitAssignmentError],
) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise error_type(
            "Rejected candidate reasons must be a mapping.",
            field="rejected_candidate_ids",
            actual=type(value).__name__,
        )
    return {
        _non_empty_string(key): _non_empty_string(reason)
        for key, reason in value.items()
    }


def _coerce_string_mapping(value: Mapping[str, str], *, field: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise InvalidGroupAssignmentError(
            "Group values must be a mapping.",
            field=field,
            actual=type(value).__name__,
        )
    return {
        _non_empty_string(key): _non_empty_string(item)
        for key, item in value.items()
    }


def _non_empty_string(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise InvalidGroupAssignmentError(
            "Group and split identifiers must be non-empty strings.",
            actual=type(value).__name__,
            value=value,
        )
    return value
