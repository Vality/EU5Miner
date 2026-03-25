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
