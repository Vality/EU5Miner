"""Public mod-planning and application workflow helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from eu5miner.domains.mod_project import (
    MaterializedWriteStatus,
    TargetedModEmission,
    materialize_targeted_mod_emission,
    plan_targeted_mod_emission,
)
from eu5miner.source import ContentPhase
from eu5miner.vfs import EmissionEntryActionKind, ModEmissionPlan, VirtualFilesystem


class ModUpdateWriteKind(StrEnum):
    """Kinds of explicit file writes within a mod update workflow."""

    METADATA = "metadata"
    CONTENT = "content"


class ModUpdateWarningKind(StrEnum):
    """Warning categories for permissive mod update workflows."""

    BLOCKED_EMISSION = "blocked_emission"


class ModUpdateAdvisoryKind(StrEnum):
    """Lower-severity advisory categories for important planned actions."""

    ADD_REPLACE_PATH = "add_replace_path"


@dataclass(frozen=True)
class BlockedModEmission:
    """One intended file that cannot become visible for the target mod."""

    relative_path: Path
    blocker_source_names: tuple[str, ...]
    blocker_reasons: tuple[str, ...]


@dataclass(frozen=True)
class ModUpdateWarning:
    """Human-readable warning for callers that want CLI/UX messaging."""

    kind: ModUpdateWarningKind
    message: str
    relative_path: Path | None = None
    blocker_source_names: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModUpdateAdvisory:
    """Human-readable advisory for non-failure but important planned actions."""

    kind: ModUpdateAdvisoryKind
    message: str
    raw_path: str | None = None


@dataclass(frozen=True)
class ModUpdateWrite:
    """One explicit file write prepared by a mod update plan."""

    path: Path
    kind: ModUpdateWriteKind
    content: str
    existed: bool
    relative_path: Path | None = None
    emission_kind: EmissionEntryActionKind | None = None


@dataclass(frozen=True)
class PlannedModUpdate:
    """Stable public view of a planned mod update."""

    target_source_name: str
    phase: ContentPhase
    relative_root: Path
    root: Path
    replace_paths_to_add: tuple[str, ...]
    blocked_emissions: tuple[BlockedModEmission, ...]
    warnings: tuple[ModUpdateWarning, ...]
    advisories: tuple[ModUpdateAdvisory, ...]
    metadata_write: ModUpdateWrite
    content_writes: tuple[ModUpdateWrite, ...]
    _targeted_emission: TargetedModEmission = field(repr=False, compare=False)

    @property
    def writes(self) -> tuple[ModUpdateWrite, ...]:
        return (self.metadata_write, *self.content_writes)

    @property
    def has_blockers(self) -> bool:
        return bool(self.blocked_emissions)

    @property
    def intended_content_write_count(self) -> int:
        return len(self.content_writes) + len(self.blocked_emissions)


@dataclass(frozen=True)
class AppliedModWrite:
    """One materialized file write from an applied mod update."""

    path: Path
    kind: ModUpdateWriteKind
    status: MaterializedWriteStatus
    relative_path: Path | None = None
    emission_kind: EmissionEntryActionKind | None = None


@dataclass(frozen=True)
class AppliedModUpdate:
    """Materialized result of applying a planned mod update."""

    plan: PlannedModUpdate
    created_directories: tuple[Path, ...]
    metadata_write: AppliedModWrite
    content_writes: tuple[AppliedModWrite, ...]

    @property
    def writes(self) -> tuple[AppliedModWrite, ...]:
        return (self.metadata_write, *self.content_writes)

    @property
    def blocked_emissions(self) -> tuple[BlockedModEmission, ...]:
        return self.plan.blocked_emissions

    @property
    def warnings(self) -> tuple[ModUpdateWarning, ...]:
        return self.plan.warnings

    @property
    def advisories(self) -> tuple[ModUpdateAdvisory, ...]:
        return self.plan.advisories

    @property
    def created_write_count(self) -> int:
        return sum(1 for write in self.writes if write.status is MaterializedWriteStatus.CREATED)

    @property
    def updated_write_count(self) -> int:
        return sum(1 for write in self.writes if write.status is MaterializedWriteStatus.UPDATED)

    @property
    def unchanged_write_count(self) -> int:
        return sum(1 for write in self.writes if write.status is MaterializedWriteStatus.UNCHANGED)


def plan_mod_update(
    vfs: VirtualFilesystem,
    target_source_name: str,
    phase: ContentPhase,
    relative_root: str | Path,
    *,
    intended_relative_paths: tuple[str | Path, ...] = (),
    content_by_relative_path: Mapping[str | Path, str] | None = None,
) -> PlannedModUpdate:
    emission_plan = vfs.plan_mod_directory_emission(
        target_source_name,
        phase,
        relative_root,
        intended_relative_paths=intended_relative_paths,
    )
    replace_paths_to_add = _collect_replace_paths(emission_plan)
    blocked_emissions = _collect_blocked_emissions(emission_plan)
    targeted_emission = plan_targeted_mod_emission(
        emission_plan,
        content_by_relative_path=_normalize_content_mapping(content_by_relative_path),
    )

    metadata_write = ModUpdateWrite(
        path=targeted_emission.metadata_write.path,
        kind=ModUpdateWriteKind.METADATA,
        content=targeted_emission.metadata_write.content,
        existed=targeted_emission.metadata_write.existed,
    )
    content_writes = tuple(
        ModUpdateWrite(
            path=file_write.path,
            kind=ModUpdateWriteKind.CONTENT,
            content=file_write.content,
            existed=file_write.existed,
            relative_path=file_write.relative_path,
            emission_kind=file_write.emission_kind,
        )
        for file_write in targeted_emission.content_writes
    )

    return PlannedModUpdate(
        target_source_name=target_source_name,
        phase=emission_plan.phase,
        relative_root=emission_plan.relative_root,
        root=targeted_emission.root,
        replace_paths_to_add=replace_paths_to_add,
        blocked_emissions=blocked_emissions,
        warnings=_build_warnings(blocked_emissions),
        advisories=_build_advisories(replace_paths_to_add),
        metadata_write=metadata_write,
        content_writes=content_writes,
        _targeted_emission=targeted_emission,
    )


def apply_mod_update(
    planned_update: PlannedModUpdate,
    *,
    overwrite: bool = True,
) -> AppliedModUpdate:
    materialized = materialize_targeted_mod_emission(
        planned_update._targeted_emission,
        overwrite=overwrite,
    )

    metadata_write = AppliedModWrite(
        path=materialized.metadata_write.path,
        kind=ModUpdateWriteKind.METADATA,
        status=materialized.metadata_write.status,
    )
    content_writes = tuple(
        AppliedModWrite(
            path=file_write.path,
            kind=ModUpdateWriteKind.CONTENT,
            status=file_write.status,
            relative_path=file_write.relative_path,
            emission_kind=file_write.emission_kind,
        )
        for file_write in materialized.content_writes
    )

    return AppliedModUpdate(
        plan=planned_update,
        created_directories=materialized.created_directories,
        metadata_write=metadata_write,
        content_writes=content_writes,
    )


def format_mod_update_report(update: PlannedModUpdate | AppliedModUpdate) -> str:
    if isinstance(update, AppliedModUpdate):
        return _format_applied_update_report(update)
    return _format_planned_update_report(update)


def _normalize_content_mapping(
    content_by_relative_path: Mapping[str | Path, str] | None,
) -> dict[Path, str] | None:
    if content_by_relative_path is None:
        return None
    return {
        Path(relative_path): content
        for relative_path, content in content_by_relative_path.items()
    }


def _collect_replace_paths(emission_plan: ModEmissionPlan) -> tuple[str, ...]:
    return tuple(action.raw_path for action in emission_plan.metadata_update_actions)


def _collect_blocked_emissions(emission_plan: ModEmissionPlan) -> tuple[BlockedModEmission, ...]:
    blocked: list[BlockedModEmission] = []
    for emission in emission_plan.directory_plan.blocked_entries:
        blocked.append(
            BlockedModEmission(
                relative_path=emission.relative_path,
                blocker_source_names=tuple(
                    blocker.source.name for blocker in emission.write_plan.blockers
                ),
                blocker_reasons=tuple(blocker.reason for blocker in emission.write_plan.blockers),
            )
        )
    return tuple(blocked)


def _build_warnings(
    blocked_emissions: tuple[BlockedModEmission, ...],
) -> tuple[ModUpdateWarning, ...]:
    warnings: list[ModUpdateWarning] = []
    for blocked in blocked_emissions:
        blocker_names = ", ".join(blocked.blocker_source_names)
        warnings.append(
            ModUpdateWarning(
                kind=ModUpdateWarningKind.BLOCKED_EMISSION,
                message=(
                    "Intended output "
                    f"{blocked.relative_path.as_posix()} will be shadowed by "
                    f"higher-priority sources: {blocker_names}"
                ),
                relative_path=blocked.relative_path,
                blocker_source_names=blocked.blocker_source_names,
            )
        )
    return tuple(warnings)


def _build_advisories(
    replace_paths_to_add: tuple[str, ...],
) -> tuple[ModUpdateAdvisory, ...]:
    advisories: list[ModUpdateAdvisory] = []
    for raw_path in replace_paths_to_add:
        advisories.append(
            ModUpdateAdvisory(
                kind=ModUpdateAdvisoryKind.ADD_REPLACE_PATH,
                message=(
                    "Planning metadata update to add replace_path entry: "
                    f"{raw_path}"
                ),
                raw_path=raw_path,
            )
        )
    return tuple(advisories)


def _format_planned_update_report(update: PlannedModUpdate) -> str:
    lines = [
        f"Planned mod update: {update.target_source_name}",
        f"Phase: {update.phase.value}",
        f"Subtree: {update.relative_root.as_posix()}",
        "Summary:",
        f"- intended content outputs: {update.intended_content_write_count}",
        f"- materialized writes: {len(update.writes)}",
        "- metadata writes: 1",
        f"- replace_path additions: {len(update.replace_paths_to_add)}",
        f"- blocked intended outputs: {len(update.blocked_emissions)}",
        f"- warnings: {len(update.warnings)}",
        f"- advisories: {len(update.advisories)}",
    ]

    if update.replace_paths_to_add:
        lines.append("Metadata replace_path additions:")
        lines.extend(f"- {raw_path}" for raw_path in update.replace_paths_to_add)

    if update.content_writes:
        lines.append("Content writes:")
        lines.extend(
            f"- {write.emission_kind.value}: {write.relative_path.as_posix()}"
            for write in update.content_writes
            if write.relative_path is not None and write.emission_kind is not None
        )

    if update.advisories:
        lines.append("Advisories:")
        lines.extend(f"- {advisory.message}" for advisory in update.advisories)

    if update.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning.message}" for warning in update.warnings)

    return "\n".join(lines)


def _format_applied_update_report(update: AppliedModUpdate) -> str:
    lines = [
        f"Applied mod update: {update.plan.target_source_name}",
        "Summary:",
        f"- created directories: {len(update.created_directories)}",
        f"- created writes: {update.created_write_count}",
        f"- updated writes: {update.updated_write_count}",
        f"- unchanged writes: {update.unchanged_write_count}",
        f"- blocked intended outputs: {len(update.blocked_emissions)}",
        f"- warnings: {len(update.warnings)}",
        f"- advisories: {len(update.advisories)}",
        "Write results:",
    ]
    lines.extend(
        f"- {write.status.value}: {write.path.as_posix()}"
        for write in update.writes
    )

    if update.advisories:
        lines.append("Advisories:")
        lines.extend(f"- {advisory.message}" for advisory in update.advisories)

    if update.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning.message}" for warning in update.warnings)

    return "\n".join(lines)
