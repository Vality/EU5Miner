from __future__ import annotations

import json
from pathlib import Path

import pytest

from eu5miner.inspection import (
    format_install_summary,
    get_system_report,
    inspect_install,
    list_supported_systems,
    summarize_install,
)
from eu5miner.source import ContentPhase, GameInstall


def test_summarize_install_reports_phase_roots_and_sources(tmp_path: Path) -> None:
    install_root = _make_test_install(tmp_path / "install")
    dlc_root = install_root / "game" / "dlc" / "D000_shared"
    mod_root = tmp_path / "my_mod"

    dlc_root.mkdir(parents=True, exist_ok=True)
    _make_mod_root(mod_root)

    install = GameInstall.discover(install_root)
    summary = summarize_install(install, mod_roots=[mod_root])
    formatted = format_install_summary(summary)

    assert summary.root == install_root
    assert tuple(phase_root.phase for phase_root in summary.phase_roots) == tuple(ContentPhase)
    assert [source.name for source in summary.sources] == ["vanilla", "D000_shared", "my_mod"]
    assert summary.sources[-1].replace_paths == ("game/in_game/common/buildings",)
    assert "Install root:" in formatted
    assert "Sources:" in formatted
    assert "mod:my_mod" in formatted


def test_inspect_install_discovers_summary_from_root(tmp_path: Path) -> None:
    install_root = _make_test_install(tmp_path / "install")

    summary = inspect_install(install_root)

    assert summary.root == install_root
    assert summary.game_dir == install_root / "game"
    assert len(summary.sources) == 1


def test_list_supported_systems_returns_expected_names() -> None:
    names = tuple(system.name for system in list_supported_systems())

    assert names == ("economy", "diplomacy", "government", "religion", "interface", "map")


def test_get_system_report_rejects_unknown_system(tmp_path: Path) -> None:
    install_root = _make_test_install(tmp_path / "install")
    install = GameInstall.discover(install_root)

    with pytest.raises(KeyError, match="Unknown system 'unknown'"):
        get_system_report(install, "unknown")


def _make_test_install(install_root: Path) -> Path:
    game_dir = install_root / "game"
    for phase_name in ("loading_screen", "main_menu", "in_game"):
        (game_dir / phase_name).mkdir(parents=True, exist_ok=True)
    (game_dir / "dlc").mkdir(parents=True, exist_ok=True)
    (game_dir / "mod").mkdir(parents=True, exist_ok=True)
    return install_root


def _make_mod_root(mod_root: Path) -> None:
    (mod_root / "in_game").mkdir(parents=True, exist_ok=True)
    metadata_path = mod_root / ".metadata" / "metadata.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps({"replace_path": ["game/in_game/common/buildings"]}),
        encoding="utf-8",
    )