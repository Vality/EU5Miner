"""Virtual filesystem primitives for EU5 content sources."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from eu5miner.formats.metadata import parse_metadata_json
from eu5miner.source import ContentPhase, GameInstall


class SourceKind(StrEnum):
    """Kinds of source roots that can contribute files."""

    VANILLA = "vanilla"
    DLC = "dlc"
    MOD = "mod"


@dataclass(frozen=True)
class ReplacePathRule:
    """A metadata-driven replace_path rule normalized to one content phase."""

    phase: ContentPhase
    relative_root: Path
    raw_path: str

    def matches(self, phase: ContentPhase, relative_path: Path) -> bool:
        if phase is not self.phase:
            return False
        return relative_path == self.relative_root or self.relative_root in relative_path.parents


@dataclass(frozen=True)
class ContentSource:
    """One loadable EU5 content source."""

    name: str
    kind: SourceKind
    root: Path
    priority: int
    replace_rules: tuple[ReplacePathRule, ...] = ()

    def phase_dir(self, phase: ContentPhase) -> Path:
        return self.root / phase.value

    def iter_files(self, phase: ContentPhase, relative_subpath: str | Path = "") -> list[Path]:
        search_root = self.phase_dir(phase) / Path(relative_subpath)
        if not search_root.exists():
            return []
        return sorted(path for path in search_root.rglob("*") if path.is_file())

    def replaces_path(self, phase: ContentPhase, relative_path: str | Path) -> bool:
        normalized_path = Path(relative_path)
        return any(rule.matches(phase, normalized_path) for rule in self.replace_rules)


@dataclass(frozen=True)
class SourceFile:
    """A file contributed by a specific source."""

    source: ContentSource
    phase: ContentPhase
    relative_path: Path
    absolute_path: Path


@dataclass(frozen=True)
class MergedFile:
    """Merged file entry with winner and full provenance."""

    phase: ContentPhase
    relative_path: Path
    winner: SourceFile
    contributors: tuple[SourceFile, ...]


@dataclass(frozen=True)
class WritePlanBlocker:
    """Reason a planned write would not become the visible file."""

    source: ContentSource
    reason: str
    replace_rule: ReplacePathRule | None = None


@dataclass(frozen=True)
class WritePlan:
    """Precedence-aware write destination analysis for one target path."""

    target_source: ContentSource
    phase: ContentPhase
    relative_path: Path
    absolute_path: Path
    current_visible_file: MergedFile | None
    blockers: tuple[WritePlanBlocker, ...]
    target_replace_rule: ReplacePathRule | None

    @property
    def is_visible(self) -> bool:
        return not self.blockers

    @property
    def will_override_current_file(self) -> bool:
        return (
            self.is_visible
            and self.current_visible_file is not None
            and self.current_visible_file.winner.source.priority < self.target_source.priority
        )


class DirectoryWriteActionKind(StrEnum):
    """Recommended action for one visible file within a subtree plan."""

    KEEP = "keep"
    OVERRIDE = "override"
    BLOCKED = "blocked"


class SubtreeWriteActionKind(StrEnum):
    """Recommended action for the subtree as a whole."""

    ADD_REPLACE_PATH = "add_replace_path"


class EmissionEntryActionKind(StrEnum):
    """Recommended action for one emitted file path."""

    KEEP = "keep"
    OVERRIDE = "override"
    BLOCKED = "blocked"
    CREATE = "create"


@dataclass(frozen=True)
class DirectoryWriteAction:
    """Concrete recommendation for one visible file beneath a subtree."""

    relative_path: Path
    kind: DirectoryWriteActionKind
    current_visible_file: MergedFile
    write_plan: WritePlan


@dataclass(frozen=True)
class SubtreeWriteAction:
    """Concrete recommendation for the subtree itself."""

    kind: SubtreeWriteActionKind
    relative_root: Path
    reason: str


@dataclass(frozen=True)
class DirectoryWritePlanEntry:
    """One visible file within a subtree-level write plan."""

    relative_path: Path
    current_visible_file: MergedFile
    write_plan: WritePlan


@dataclass(frozen=True)
class DirectoryWritePlan:
    """Precedence-aware planning for a subtree rooted at one relative path."""

    target_source: ContentSource
    phase: ContentPhase
    relative_root: Path
    absolute_root: Path
    entries: tuple[DirectoryWritePlanEntry, ...]
    target_replace_rule: ReplacePathRule | None

    @property
    def blocked_entries(self) -> tuple[DirectoryWritePlanEntry, ...]:
        return tuple(entry for entry in self.entries if not entry.write_plan.is_visible)

    @property
    def lower_priority_visible_entries(self) -> tuple[DirectoryWritePlanEntry, ...]:
        return tuple(
            entry
            for entry in self.entries
            if entry.current_visible_file.winner.source.priority < self.target_source.priority
        )

    @property
    def needs_replace_path_for_full_subtree_ownership(self) -> bool:
        return self.target_replace_rule is None and bool(self.lower_priority_visible_entries)

    def to_action_plan(self) -> DirectoryWriteActionPlan:
        subtree_actions: list[SubtreeWriteAction] = []
        if self.needs_replace_path_for_full_subtree_ownership:
            subtree_actions.append(
                SubtreeWriteAction(
                    kind=SubtreeWriteActionKind.ADD_REPLACE_PATH,
                    relative_root=self.relative_root,
                    reason="Lower-priority visible files remain under this subtree",
                )
            )

        entry_actions = tuple(_classify_directory_entry_action(entry) for entry in self.entries)
        return DirectoryWriteActionPlan(
            target_source=self.target_source,
            phase=self.phase,
            relative_root=self.relative_root,
            absolute_root=self.absolute_root,
            subtree_actions=tuple(subtree_actions),
            entry_actions=entry_actions,
        )


@dataclass(frozen=True)
class DirectoryWriteActionPlan:
    """Action-oriented view of a subtree write plan."""

    target_source: ContentSource
    phase: ContentPhase
    relative_root: Path
    absolute_root: Path
    subtree_actions: tuple[SubtreeWriteAction, ...]
    entry_actions: tuple[DirectoryWriteAction, ...]

    @property
    def blocked_entries(self) -> tuple[DirectoryWriteAction, ...]:
        return tuple(
            action
            for action in self.entry_actions
            if action.kind is DirectoryWriteActionKind.BLOCKED
        )


@dataclass(frozen=True)
class PlannedFileEmission:
    """Concrete emission recommendation for one file path."""

    relative_path: Path
    kind: EmissionEntryActionKind
    intended: bool
    current_visible_file: MergedFile | None
    write_plan: WritePlan


@dataclass(frozen=True)
class DirectoryEmissionPlan:
    """Emission-oriented view that includes intended new file paths."""

    target_source: ContentSource
    phase: ContentPhase
    relative_root: Path
    absolute_root: Path
    subtree_actions: tuple[SubtreeWriteAction, ...]
    emissions: tuple[PlannedFileEmission, ...]

    @property
    def blocked_entries(self) -> tuple[PlannedFileEmission, ...]:
        return tuple(
            emission
            for emission in self.emissions
            if emission.kind is EmissionEntryActionKind.BLOCKED
        )

    @property
    def create_entries(self) -> tuple[PlannedFileEmission, ...]:
        return tuple(
            emission
            for emission in self.emissions
            if emission.kind is EmissionEntryActionKind.CREATE
        )


class VirtualFilesystem:
    """Merged, phase-aware file view across ordered content sources."""

    def __init__(self, sources: list[ContentSource]) -> None:
        self._sources = sorted(sources, key=lambda source: source.priority)

    @property
    def sources(self) -> tuple[ContentSource, ...]:
        return tuple(self._sources)

    @classmethod
    def from_install(
        cls,
        install: GameInstall,
        mod_roots: list[Path] | None = None,
    ) -> VirtualFilesystem:
        sources: list[ContentSource] = [
            ContentSource(
                name="vanilla",
                kind=SourceKind.VANILLA,
                root=install.game_dir,
                priority=0,
                replace_rules=(),
            )
        ]

        dlc_priority = 10
        if install.dlc_dir.exists():
            for dlc_root in sorted(path for path in install.dlc_dir.iterdir() if path.is_dir()):
                sources.append(
                    ContentSource(
                        name=dlc_root.name,
                        kind=SourceKind.DLC,
                        root=dlc_root,
                        priority=dlc_priority,
                        replace_rules=_load_replace_rules(SourceKind.DLC, dlc_root),
                    )
                )
                dlc_priority += 1

        mod_priority = 100
        for mod_root in sorted(mod_roots or []):
            sources.append(
                ContentSource(
                    name=mod_root.name,
                    kind=SourceKind.MOD,
                    root=mod_root,
                    priority=mod_priority,
                    replace_rules=_load_replace_rules(SourceKind.MOD, mod_root),
                )
            )
            mod_priority += 1

        return cls(sources)

    def list_source_files(
        self,
        phase: ContentPhase,
        relative_subpath: str | Path = "",
    ) -> list[SourceFile]:
        normalized_subpath = Path(relative_subpath)
        files: list[SourceFile] = []

        for source in self._sources:
            phase_root = source.phase_dir(phase)
            search_root = phase_root / normalized_subpath
            if not search_root.exists():
                continue

            for absolute_path in sorted(path for path in search_root.rglob("*") if path.is_file()):
                relative_path = absolute_path.relative_to(phase_root)
                files.append(
                    SourceFile(
                        source=source,
                        phase=phase,
                        relative_path=relative_path,
                        absolute_path=absolute_path,
                    )
                )

        return files

    def list_visible_source_files(
        self,
        phase: ContentPhase,
        relative_subpath: str | Path = "",
    ) -> list[SourceFile]:
        visible_files: list[SourceFile] = []
        for source_file in self.list_source_files(phase, relative_subpath):
            if self._is_hidden_by_later_replace_path(source_file):
                continue
            visible_files.append(source_file)
        return visible_files

    def merge_phase(
        self,
        phase: ContentPhase,
        relative_subpath: str | Path = "",
    ) -> list[MergedFile]:
        grouped: dict[Path, list[SourceFile]] = {}
        for source_file in self.list_visible_source_files(phase, relative_subpath):
            grouped.setdefault(source_file.relative_path, []).append(source_file)

        merged_files: list[MergedFile] = []
        for relative_path in sorted(grouped):
            contributors = tuple(grouped[relative_path])
            merged_files.append(
                MergedFile(
                    phase=phase,
                    relative_path=relative_path,
                    winner=contributors[-1],
                    contributors=contributors,
                )
            )

        return merged_files

    def get_merged_file(
        self,
        phase: ContentPhase,
        relative_path: str | Path,
    ) -> MergedFile | None:
        normalized_path = Path(relative_path)
        for merged_file in self.merge_phase(phase):
            if merged_file.relative_path == normalized_path:
                return merged_file
        return None

    def get_source(self, name: str) -> ContentSource | None:
        for source in self._sources:
            if source.name == name:
                return source
        return None

    def plan_write(
        self,
        target_source_name: str,
        phase: ContentPhase,
        relative_path: str | Path,
    ) -> WritePlan:
        target_source = self.get_source(target_source_name)
        if target_source is None:
            raise ValueError(f"Unknown content source: {target_source_name}")

        normalized_path = Path(relative_path)
        blockers: list[WritePlanBlocker] = []
        target_replace_rule = _first_matching_replace_rule(target_source, phase, normalized_path)

        for source in self._sources:
            if source.priority <= target_source.priority:
                continue

            replace_rule = _first_matching_replace_rule(source, phase, normalized_path)
            if replace_rule is not None:
                blockers.append(
                    WritePlanBlocker(
                        source=source,
                        reason="replace_path",
                        replace_rule=replace_rule,
                    )
                )
                continue

            source_file = self._get_source_file(source, phase, normalized_path)
            if source_file is not None:
                blockers.append(WritePlanBlocker(source=source, reason="higher_priority_file"))

        return WritePlan(
            target_source=target_source,
            phase=phase,
            relative_path=normalized_path,
            absolute_path=target_source.phase_dir(phase) / normalized_path,
            current_visible_file=self.get_merged_file(phase, normalized_path),
            blockers=tuple(blockers),
            target_replace_rule=target_replace_rule,
        )

    def plan_directory_write(
        self,
        target_source_name: str,
        phase: ContentPhase,
        relative_root: str | Path,
    ) -> DirectoryWritePlan:
        target_source = self.get_source(target_source_name)
        if target_source is None:
            raise ValueError(f"Unknown content source: {target_source_name}")

        normalized_root = Path(relative_root)
        entries: list[DirectoryWritePlanEntry] = []
        for merged_file in self.merge_phase(phase, normalized_root):
            write_plan = self.plan_write(target_source_name, phase, merged_file.relative_path)
            entries.append(
                DirectoryWritePlanEntry(
                    relative_path=merged_file.relative_path,
                    current_visible_file=merged_file,
                    write_plan=write_plan,
                )
            )

        return DirectoryWritePlan(
            target_source=target_source,
            phase=phase,
            relative_root=normalized_root,
            absolute_root=target_source.phase_dir(phase) / normalized_root,
            entries=tuple(entries),
            target_replace_rule=_first_matching_replace_rule(target_source, phase, normalized_root),
        )

    def plan_directory_emission(
        self,
        target_source_name: str,
        phase: ContentPhase,
        relative_root: str | Path,
        intended_relative_paths: tuple[str | Path, ...] = (),
    ) -> DirectoryEmissionPlan:
        directory_plan = self.plan_directory_write(target_source_name, phase, relative_root)
        action_plan = directory_plan.to_action_plan()
        target_source = directory_plan.target_source

        emission_paths: set[Path] = {action.relative_path for action in action_plan.entry_actions}
        normalized_intended_paths: set[Path] = set()
        for intended_path in intended_relative_paths:
            normalized_path = Path(intended_path)
            if not _path_is_within_root(normalized_path, directory_plan.relative_root):
                raise ValueError(
                    "Intended path "
                    f"{normalized_path} is outside subtree "
                    f"{directory_plan.relative_root}"
                )
            emission_paths.add(normalized_path)
            normalized_intended_paths.add(normalized_path)

        emissions: list[PlannedFileEmission] = []
        for relative_path in sorted(emission_paths):
            write_plan = self.plan_write(target_source_name, phase, relative_path)
            current_visible_file = write_plan.current_visible_file
            intended = relative_path in normalized_intended_paths
            emissions.append(
                PlannedFileEmission(
                    relative_path=relative_path,
                    kind=_classify_emission_kind(write_plan, intended),
                    intended=intended,
                    current_visible_file=current_visible_file,
                    write_plan=write_plan,
                )
            )

        return DirectoryEmissionPlan(
            target_source=target_source,
            phase=phase,
            relative_root=directory_plan.relative_root,
            absolute_root=directory_plan.absolute_root,
            subtree_actions=action_plan.subtree_actions,
            emissions=tuple(emissions),
        )

    def _is_hidden_by_later_replace_path(self, source_file: SourceFile) -> bool:
        for source in self._sources:
            if source.priority <= source_file.source.priority:
                continue
            if source.replaces_path(source_file.phase, source_file.relative_path):
                return True
        return False

    def _get_source_file(
        self,
        source: ContentSource,
        phase: ContentPhase,
        relative_path: Path,
    ) -> SourceFile | None:
        absolute_path = source.phase_dir(phase) / relative_path
        if not absolute_path.is_file():
            return None
        return SourceFile(
            source=source,
            phase=phase,
            relative_path=relative_path,
            absolute_path=absolute_path,
        )


def _load_replace_rules(kind: SourceKind, root: Path) -> tuple[ReplacePathRule, ...]:
    metadata_path = _metadata_path_for_source(kind, root)
    if metadata_path is None or not metadata_path.exists():
        return ()

    metadata = parse_metadata_json(metadata_path.read_text(encoding="utf-8", errors="replace"))
    replace_paths = metadata.get("replace_path")
    if not isinstance(replace_paths, list):
        return ()

    rules: list[ReplacePathRule] = []
    for raw_path in replace_paths:
        if not isinstance(raw_path, str):
            continue
        rule = _parse_replace_rule(raw_path)
        if rule is not None:
            rules.append(rule)
    return tuple(rules)


def _metadata_path_for_source(kind: SourceKind, root: Path) -> Path | None:
    if kind is SourceKind.DLC:
        return root / f"{root.name}.dlc.json"
    if kind is SourceKind.MOD:
        return root / ".metadata" / "metadata.json"
    return None


def _parse_replace_rule(raw_path: str) -> ReplacePathRule | None:
    parts = Path(raw_path).parts
    if len(parts) < 3 or parts[0] != "game":
        return None

    phase_text = parts[1]
    try:
        phase = ContentPhase(phase_text)
    except ValueError:
        return None

    relative_root = Path(*parts[2:])
    if not relative_root.parts:
        return None

    return ReplacePathRule(phase=phase, relative_root=relative_root, raw_path=raw_path)


def _first_matching_replace_rule(
    source: ContentSource,
    phase: ContentPhase,
    relative_path: Path,
) -> ReplacePathRule | None:
    for rule in source.replace_rules:
        if rule.matches(phase, relative_path):
            return rule
    return None


def _classify_directory_entry_action(entry: DirectoryWritePlanEntry) -> DirectoryWriteAction:
    if not entry.write_plan.is_visible:
        kind = DirectoryWriteActionKind.BLOCKED
    elif entry.current_visible_file.winner.source.name == entry.write_plan.target_source.name:
        kind = DirectoryWriteActionKind.KEEP
    else:
        kind = DirectoryWriteActionKind.OVERRIDE

    return DirectoryWriteAction(
        relative_path=entry.relative_path,
        kind=kind,
        current_visible_file=entry.current_visible_file,
        write_plan=entry.write_plan,
    )


def _classify_emission_kind(write_plan: WritePlan, intended: bool) -> EmissionEntryActionKind:
    if not write_plan.is_visible:
        return EmissionEntryActionKind.BLOCKED
    if write_plan.current_visible_file is None:
        return EmissionEntryActionKind.CREATE if intended else EmissionEntryActionKind.KEEP
    if write_plan.current_visible_file.winner.source.name == write_plan.target_source.name:
        return EmissionEntryActionKind.KEEP
    return EmissionEntryActionKind.OVERRIDE


def _path_is_within_root(path: Path, root: Path) -> bool:
    return path == root or root in path.parents
