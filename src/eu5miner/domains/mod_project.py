"""Helpers for planning mod skeleton layouts and emitted files."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from eu5miner.formats.metadata import parse_metadata_json
from eu5miner.vfs import (
    EmissionEntryActionKind,
    ModEmissionPlan,
    ModMetadataUpdateActionKind,
    PlannedFileEmission,
)


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


@dataclass(frozen=True)
class PlannedFileWrite:
    """One concrete file write produced from a skeleton and emission plan."""

    path: Path
    content: str
    existed: bool
    relative_path: Path | None = None
    emission_kind: EmissionEntryActionKind | None = None


@dataclass(frozen=True)
class TargetedModEmission:
    """Concrete write payloads for a mod skeleton and its metadata updates."""

    root: Path
    directories: tuple[Path, ...]
    metadata_write: PlannedFileWrite
    content_writes: tuple[PlannedFileWrite, ...]
    blocked_emissions: tuple[PlannedFileEmission, ...]


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


def plan_targeted_mod_emission(
    emission_plan: ModEmissionPlan,
    content_by_relative_path: Mapping[Path, str] | None = None,
) -> TargetedModEmission:
    skeleton = plan_mod_skeleton(emission_plan)
    provided_content = content_by_relative_path or {}

    metadata_text = _build_metadata_json_text(emission_plan)
    metadata_write = PlannedFileWrite(
        path=skeleton.metadata_file.path,
        content=metadata_text,
        existed=skeleton.metadata_file.exists,
    )

    content_writes: list[PlannedFileWrite] = []
    for file in skeleton.content_files:
        relative_path = file.relative_path
        if relative_path is None:
            continue
        content_writes.append(
            PlannedFileWrite(
                path=file.path,
                content=provided_content.get(relative_path, ""),
                existed=file.exists,
                relative_path=relative_path,
                emission_kind=file.emission_kind,
            )
        )

    return TargetedModEmission(
        root=skeleton.root,
        directories=skeleton.directories,
        metadata_write=metadata_write,
        content_writes=tuple(content_writes),
        blocked_emissions=skeleton.blocked_emissions,
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


def _build_metadata_json_text(emission_plan: ModEmissionPlan) -> str:
    metadata_path = emission_plan.metadata_path
    if metadata_path.is_file():
        metadata = parse_metadata_json(metadata_path.read_text(encoding="utf-8", errors="replace"))
    else:
        metadata = {}

    replace_paths = metadata.get("replace_path")
    if not isinstance(replace_paths, list):
        replace_paths = []

    for action in emission_plan.metadata_update_actions:
        if (
            action.kind is ModMetadataUpdateActionKind.ADD_REPLACE_PATH
            and action.raw_path not in replace_paths
        ):
            replace_paths.append(action.raw_path)

    if replace_paths:
        metadata["replace_path"] = replace_paths

    return json.dumps(metadata, indent=2, sort_keys=False) + "\n"
