from __future__ import annotations

from eu5miner.source import ContentPhase, GameInstall


def test_discover_install(game_install: GameInstall) -> None:
    assert game_install.root.exists()
    assert game_install.game_dir.exists()
    assert game_install.phase_dir(ContentPhase.LOADING_SCREEN).exists()
    assert game_install.phase_dir(ContentPhase.MAIN_MENU).exists()
    assert game_install.phase_dir(ContentPhase.IN_GAME).exists()


def test_representative_files_exist(game_install: GameInstall) -> None:
    for path in game_install.representative_files().values():
        assert path.exists(), f"Expected representative file to exist: {path}"


def test_can_list_in_game_common_files(game_install: GameInstall) -> None:
    files = game_install.iter_phase_files(ContentPhase.IN_GAME, "common")
    assert files
    assert any(path.suffix == ".txt" for path in files)
