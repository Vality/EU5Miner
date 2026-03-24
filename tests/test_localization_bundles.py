from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.localization_bundles import (
    build_localization_bundle,
    collect_customizable_localization_references,
    collect_effect_localization_references,
    collect_trigger_localization_references,
    find_missing_localization_references,
)
from eu5miner.domains.localization_helpers import (
    parse_customizable_localization_document,
    parse_effect_localization_document,
    parse_trigger_localization_document,
)
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_build_localization_bundle_inline() -> None:
    bundle = build_localization_bundle(
        (
            (
                "first.yml",
                'l_english:\nHELLO: "Hello"\nSHARED: "Old"\n',
            ),
            (
                "second.yml",
                'l_english:\nWORLD: "World"\nSHARED: "New"\n',
            ),
        )
    )

    assert bundle.language == "l_english"
    assert bundle.get_value("HELLO") == "Hello"
    assert bundle.get_value("WORLD") == "World"
    assert bundle.get_value("SHARED") == "New"
    assert bundle.duplicate_keys() == ("SHARED",)
    assert bundle.get_entry("SHARED") is not None
    assert bundle.get_entry("SHARED").source_name == "second.yml"


@pytest.mark.timeout(5)
def test_real_customizable_localization_references_resolve(game_install: GameInstall) -> None:
    helper_document = parse_customizable_localization_document(
        _read_text(game_install.representative_files()["customizable_localization_sample"])
    )
    bundle = build_localization_bundle(
        (
            (
                "laws_and_policies_l_english.yml",
                _read_text(game_install.representative_files()["english_laws_localization"]),
            ),
        )
    )

    definition = helper_document.get_definition("GetOrderOfChivalry")
    assert definition is not None

    references = tuple(
        reference
        for reference in collect_customizable_localization_references(helper_document)
        if reference.definition_name == "GetOrderOfChivalry"
    )

    assert references
    assert find_missing_localization_references(bundle, references) == ()


@pytest.mark.timeout(5)
def test_real_effect_localization_references_resolve(game_install: GameInstall) -> None:
    helper_document = parse_effect_localization_document(
        _read_text(game_install.representative_files()["effect_localization_sample"])
    )
    bundle = build_localization_bundle(
        (
            (
                "effects_l_english.yml",
                _read_text(game_install.representative_files()["english_effects_localization"]),
            ),
        )
    )

    definition = helper_document.get_definition("set_age_preference")
    assert definition is not None

    references = tuple(
        reference
        for reference in collect_effect_localization_references(helper_document)
        if reference.definition_name == "set_age_preference"
    )

    assert references
    assert find_missing_localization_references(bundle, references) == ()


@pytest.mark.timeout(5)
def test_real_trigger_localization_references_resolve(game_install: GameInstall) -> None:
    helper_document = parse_trigger_localization_document(
        _read_text(game_install.representative_files()["trigger_localization_sample"])
    )
    bundle = build_localization_bundle(
        (
            (
                "triggers_l_english.yml",
                _read_text(game_install.representative_files()["english_triggers_localization"]),
            ),
        )
    )

    definition = helper_document.get_definition("tag")
    assert definition is not None

    references = tuple(
        reference
        for reference in collect_trigger_localization_references(helper_document)
        if reference.definition_name == "tag"
    )

    assert references
    assert find_missing_localization_references(bundle, references) == ()


def test_missing_localization_references_are_reported() -> None:
    helper_document = parse_effect_localization_document(
        "sample_effect = {\n"
        "    global = SAMPLE_EFFECT\n"
        "    first = SAMPLE_EFFECT_FIRST\n"
        "}\n"
    )
    bundle = build_localization_bundle(
        (
            (
                "sample.yml",
                'l_english:\nSAMPLE_EFFECT: "Effect"\n',
            ),
        )
    )

    missing = find_missing_localization_references(
        bundle,
        collect_effect_localization_references(helper_document),
    )

    assert len(missing) == 1
    assert missing[0].definition_name == "sample_effect"
    assert missing[0].variant_name == "first"
    assert missing[0].localization_key == "SAMPLE_EFFECT_FIRST"
