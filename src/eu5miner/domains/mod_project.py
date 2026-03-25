"""Helpers for planning mod skeleton layouts and emitted files."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from eu5miner.vfs import EmissionEntryActionKind, ModEmissionPlan, PlannedFileEmission


class ModSkeletonFileKind(StrEnum):
    """Kinds of files that can appear in a mod skeleton plan."""

    METADATA = "metadata"
    CONTENT = "content"


@dataclass(frozen=True)
class ModSkeletonFile:
    """One file that should exist within a planned mod skeleton."""

    path: Path
    kind: ModSkeletonFileKind
    exists: bool
    relative_path: Path | None = None
    emission_kind: EmissionEntryActionKind | None = None


@dataclass(frozen=True)
class ModSkeletonPlan:
    """Filesystem-oriented plan for a mod root derived from emission planning."""

    root: Path
    directories: tuple[Path, ...]
    files: tuple[ModSkeletonFile, ...]
    blocked_emissions: tuple[PlannedFileEmission, ...]
    metadata_update_actions_count: int

    @property
    def content_files(self) -> tuple[ModSkeletonFile, ...]:
        return tuple(file for file in self.files if file.kind is ModSkeletonFileKind.CONTENT)

    @property
    def metadata_file(self) -> ModSkeletonFile:
        for file in self.files:
            if file.kind is ModSkeletonFileKind.METADATA:
                return file
        raise ValueError("Mod skeleton plan is missing metadata.json")


def plan_mod_skeleton(emission_plan: ModEmissionPlan) -> ModSkeletonPlan:
    directories: set[Path] = {emission_plan.target_source.root, emission_plan.metadata_path.parent}
    files: list[ModSkeletonFile] = [
        ModSkeletonFile(
            path=emission_plan.metadata_path,
            kind=ModSkeletonFileKind.METADATA,
            exists=emission_plan.metadata_path.is_file(),
        )
    ]
    blocked_emissions: list[PlannedFileEmission] = []

    for emission in emission_plan.directory_plan.emissions:
        if not emission.intended:
            continue
        if emission.kind is EmissionEntryActionKind.BLOCKED:
            blocked_emissions.append(emission)
            continue

        absolute_path = (
            emission_plan.target_source.phase_dir(emission_plan.phase) / emission.relative_path
        )
        directories.update(
            _ancestor_dirs_within_root(absolute_path.parent, emission_plan.target_source.root)
        )
        files.append(
            ModSkeletonFile(
                path=absolute_path,
                kind=ModSkeletonFileKind.CONTENT,
                exists=absolute_path.is_file(),
                relative_path=emission.relative_path,
                emission_kind=emission.kind,
            )
        )

    return ModSkeletonPlan(
        root=emission_plan.target_source.root,
        directories=tuple(sorted(directories)),
        files=tuple(sorted(files, key=lambda file: file.path)),
        blocked_emissions=tuple(blocked_emissions),
        metadata_update_actions_count=len(emission_plan.metadata_update_actions),
    )


def _ancestor_dirs_within_root(path: Path, root: Path) -> tuple[Path, ...]:
    directories: list[Path] = []
    current = path
    while current != root and root in current.parents:
        directories.append(current)
        current = current.parent
    if current == root:
        directories.append(root)
    return tuple(reversed(directories))
