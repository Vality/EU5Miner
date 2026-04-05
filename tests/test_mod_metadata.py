from __future__ import annotations

import os
from pathlib import Path

import pytest

from eu5miner.domains.mod_metadata import parse_mod_metadata_document
from eu5miner.source import GameInstall

LOCAL_MOD_METADATA_ENV_VAR = "EU5MINER_SAMPLE_MOD_METADATA_PATH"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _local_mod_metadata_path() -> Path | None:
    raw_path = os.environ.get(LOCAL_MOD_METADATA_ENV_VAR)
    if not raw_path:
        return None
    return Path(raw_path)


def test_parse_mod_metadata_document_inline() -> None:
    document = parse_mod_metadata_document(
        "{"
        '"name": "Example Mod", '
        '"id": "example.mod", '
        '"version": "1.2.3", '
        '"supported_game_version": "1.0.*", '
        '"relationships": ['
        '{"type": "requires", "target_id": "core.mod"}'
        "], "
        '"replace_path": ["game/in_game/common"], '
        '"tags": ["Gameplay"]'
        "}"
    )

    assert document.name == "Example Mod"
    assert document.mod_id == "example.mod"
    assert document.version == "1.2.3"
    assert document.supported_game_version == "1.0.*"
    assert document.replace_paths == ("game/in_game/common",)
    assert document.tags == ("Gameplay",)
    assert len(document.relationships) == 1
    assert document.relationships[0].relationship_type == "requires"
    assert document.relationships[0].target_id == "core.mod"


@pytest.mark.timeout(5)
def test_parse_real_dlc_metadata_document(game_install: GameInstall) -> None:
    document = parse_mod_metadata_document(
        _read_text(game_install.representative_files()["dlc_metadata"])
    )

    assert document.name == "Shared DLC Data"
    assert document.path == "dlc/D000_shared"
    assert document.dependencies == ()
    assert document.replace_paths == ()
    assert document.enabled is True
    assert document.hidden is True
    assert document.verify is False


@pytest.mark.timeout(5)
def test_parse_real_optional_local_mod_metadata_document() -> None:
    path = _local_mod_metadata_path()
    if path is None:
        pytest.skip(f"Set {LOCAL_MOD_METADATA_ENV_VAR} to run this optional local-sample test")
    if not path.exists():
        pytest.skip(f"Optional local metadata sample path does not exist: {path}")

    document = parse_mod_metadata_document(_read_text(path))

    assert document.raw
    assert document.name is not None
    assert document.name.strip()
    assert document.mod_id is not None
    assert document.mod_id.strip()
    assert isinstance(document.replace_paths, tuple)
    assert isinstance(document.tags, tuple)
    assert isinstance(document.relationships, tuple)
    assert document.game_custom_data is None or isinstance(document.game_custom_data, dict)
