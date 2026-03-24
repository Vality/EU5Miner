"""Virtual filesystem primitives for EU5 content sources."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from eu5miner.source import ContentPhase, GameInstall


class SourceKind(StrEnum):
    """Kinds of source roots that can contribute files."""

    VANILLA = "vanilla"
    DLC = "dlc"
    MOD = "mod"


@dataclass(frozen=True)
class ContentSource:
    """One loadable EU5 content source."""

    name: str
    kind: SourceKind
    root: Path
    priority: int

    def phase_dir(self, phase: ContentPhase) -> Path:
        return self.root / phase.value

    def iter_files(self, phase: ContentPhase, relative_subpath: str | Path = "") -> list[Path]:
        search_root = self.phase_dir(phase) / Path(relative_subpath)
        if not search_root.exists():
            return []
        return sorted(path for path in search_root.rglob("*") if path.is_file())


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

    def merge_phase(
        self,
        phase: ContentPhase,
        relative_subpath: str | Path = "",
    ) -> list[MergedFile]:
        grouped: dict[Path, list[SourceFile]] = {}
        for source_file in self.list_source_files(phase, relative_subpath):
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
