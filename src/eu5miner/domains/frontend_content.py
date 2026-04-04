"""Helpers for loading-screen and main-menu content."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.domains.localization.localization_bundles import (
    LocalizationBundle,
    build_localization_bundle,
)
from eu5miner.formats import semantic
from eu5miner.source import ContentPhase, GameInstall


@dataclass(frozen=True)
class MainMenuScenarioDefinition:
    """One scenario entry from main-menu scenario definitions."""

    name: str
    body: semantic.SemanticObject
    country: str | None
    flag: str | None
    player_playstyle: str | None
    player_proficiency: str | None
    entry: semantic.SemanticEntry


@dataclass(frozen=True)
class MainMenuScenarioDocument:
    """Parsed main-menu scenario definitions."""

    definitions: tuple[MainMenuScenarioDefinition, ...]
    semantic_document: semantic.SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> MainMenuScenarioDefinition | None:
        return get_by_name(self.definitions, name)


@dataclass(frozen=True)
class PhaseLocalizationSource:
    """One localization file discovered under a specific content phase."""

    phase: ContentPhase
    language: str
    relative_path: str
    path: Path

    @property
    def source_name(self) -> str:
        return self.relative_path


def parse_main_menu_scenarios_document(text: str) -> MainMenuScenarioDocument:
    semantic_document = semantic.parse_semantic_document(text)
    definitions = tuple(
        _parse_main_menu_scenario(entry)
        for entry in semantic_document.entries
        if isinstance(entry.value, semantic.SemanticObject)
    )
    return MainMenuScenarioDocument(
        definitions=definitions,
        semantic_document=semantic_document,
    )


def iter_phase_localization_sources(
    install: GameInstall,
    phase: ContentPhase,
    language: str,
    relative_subpath: str | Path = "",
) -> tuple[PhaseLocalizationSource, ...]:
    base_dir = install.phase_dir(phase) / "localization" / language
    search_root = base_dir / Path(relative_subpath)
    if not search_root.exists():
        return ()

    sources = tuple(
        PhaseLocalizationSource(
            phase=phase,
            language=language,
            relative_path=path.relative_to(base_dir).as_posix(),
            path=path,
        )
        for path in sorted(search_root.rglob("*.yml"))
        if path.is_file()
    )
    return sources


def build_phase_localization_bundle(
    install: GameInstall,
    phase: ContentPhase,
    language: str,
    relative_subpath: str | Path = "",
) -> LocalizationBundle:
    sources = iter_phase_localization_sources(install, phase, language, relative_subpath)
    if not sources:
        phase_name = phase.value
        raise FileNotFoundError(
            f"No localization files found for {phase_name}/{language}/{relative_subpath}"
        )

    return build_localization_bundle(
        tuple(
            (source.source_name, source.path.read_text(encoding="utf-8", errors="replace"))
            for source in sources
        )
    )


def _parse_main_menu_scenario(entry: semantic.SemanticEntry) -> MainMenuScenarioDefinition:
    assert isinstance(entry.value, semantic.SemanticObject)

    return MainMenuScenarioDefinition(
        name=entry.key,
        body=entry.value,
        country=entry.value.get_scalar("country"),
        flag=entry.value.get_scalar("flag"),
        player_playstyle=entry.value.get_scalar("player_playstyle"),
        player_proficiency=entry.value.get_scalar("player_proficiency"),
        entry=entry,
    )
