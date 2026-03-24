from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.frontend_content import (
    build_phase_localization_bundle,
    iter_phase_localization_sources,
    parse_main_menu_scenarios_document,
)
from eu5miner.source import ContentPhase, GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_main_menu_scenarios_document_inline() -> None:
    document = parse_main_menu_scenarios_document(
        "sample_scenario = {\n"
        "    country = FRA\n"
        "    flag = FRA_scenario\n"
        "    player_playstyle = MILITARY\n"
        "    player_proficiency = ADVANCED\n"
        "}\n"
        "simple_scenario = {\n"
        "    country = HOL\n"
        "    player_playstyle = DIPLOMATIC\n"
        "}\n"
    )

    assert document.names() == ("sample_scenario", "simple_scenario")

    sample = document.get_definition("sample_scenario")
    assert sample is not None
    assert sample.country == "FRA"
    assert sample.flag == "FRA_scenario"
    assert sample.player_playstyle == "MILITARY"
    assert sample.player_proficiency == "ADVANCED"

    simple = document.get_definition("simple_scenario")
    assert simple is not None
    assert simple.flag is None
    assert simple.player_playstyle == "DIPLOMATIC"


@pytest.mark.timeout(5)
def test_parse_real_main_menu_scenarios(game_install: GameInstall) -> None:
    document = parse_main_menu_scenarios_document(
        _read_text(game_install.representative_files()["main_menu_scenarios_sample"])
    )

    tur = document.get_definition("TUR_scenario")
    assert tur is not None
    assert tur.country == "TUR"
    assert tur.flag == "TUR_scenario"
    assert tur.player_playstyle == "MILITARY"
    assert tur.player_proficiency == "NOVICE"

    hol = document.get_definition("HOL_scenario")
    assert hol is not None
    assert hol.country == "HOL"
    assert hol.flag is None
    assert hol.player_proficiency == "EXPERIENCED"


@pytest.mark.timeout(5)
def test_iter_loading_screen_localization_sources(game_install: GameInstall) -> None:
    sources = iter_phase_localization_sources(
        game_install,
        ContentPhase.LOADING_SCREEN,
        "english",
    )

    relative_paths = tuple(source.relative_path for source in sources)
    assert "load_tips_l_english.yml" in relative_paths
    assert "languages.yml" in relative_paths


@pytest.mark.timeout(5)
def test_build_loading_screen_localization_bundle(game_install: GameInstall) -> None:
    bundle = build_phase_localization_bundle(
        game_install,
        ContentPhase.LOADING_SCREEN,
        "english",
    )

    assert bundle.language == "l_english"
    assert bundle.get_value("LOADING_TIP_0") is not None
    assert bundle.get_value("LOADING_TIP_0").startswith(" #T ")


@pytest.mark.timeout(5)
def test_iter_main_menu_localization_sources(game_install: GameInstall) -> None:
    sources = iter_phase_localization_sources(
        game_install,
        ContentPhase.MAIN_MENU,
        "english",
    )

    relative_paths = tuple(source.relative_path for source in sources)
    assert "actions_l_english.yml" in relative_paths
    assert any(path.startswith("events/") for path in relative_paths)


def test_missing_phase_localization_raises() -> None:
    install = GameInstall(
        root=Path("C:/example"),
        game_dir=Path("C:/example/game"),
        dlc_dir=Path("C:/example/game/dlc"),
        mod_dir=Path("C:/example/game/mod"),
    )

    with pytest.raises(FileNotFoundError):
        build_phase_localization_bundle(
            install,
            ContentPhase.LOADING_SCREEN,
            "english",
        )
