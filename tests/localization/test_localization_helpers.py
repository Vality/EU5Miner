from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.localization.localization_helpers import (
    parse_customizable_localization_document,
    parse_effect_localization_document,
    parse_trigger_localization_document,
)
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_customizable_localization_document(game_install: GameInstall) -> None:
    document = parse_customizable_localization_document(
        _read_text(game_install.representative_files()["customizable_localization_sample"])
    )

    definition = document.get_definition("GetOrderOfChivalry")
    assert definition is not None
    assert definition.scope_type == "country"
    assert len(definition.texts) > 2
    assert definition.texts[-1].fallback is True
    assert definition.texts[-1].localization_key == "order_of_chivalry_law"


def test_parse_customizable_localization_variant_definition() -> None:
    document = parse_customizable_localization_document(
        "my_custom_loc = {\n"
        "    parent = parent_key\n"
        "    suffix = \"_suffix\"\n"
        "    fallback = true\n"
        "}\n"
    )

    definition = document.get_definition("my_custom_loc")
    assert definition is not None
    assert definition.parent == "parent_key"
    assert definition.suffix == "_suffix"
    assert definition.fallback is True
    assert definition.texts == ()


@pytest.mark.timeout(5)
def test_parse_real_effect_localization_document(game_install: GameInstall) -> None:
    document = parse_effect_localization_document(
        _read_text(game_install.representative_files()["effect_localization_sample"])
    )

    definition = document.get_definition("set_age_preference")
    assert definition is not None
    assert definition.get_variant("global") == "SET_AGE_PREFERENCE_EFFECT"
    assert definition.get_variant("first_past") == "PAST_WE_SET_AGE_PREFERENCE_EFFECT"

    add_inflation = document.get_definition("add_inflation")
    assert add_inflation is not None
    assert add_inflation.get_variant("global_neg") == "LOSE_CURRENCY_EFFECT"


def test_parse_effect_localization_inline_definition() -> None:
    document = parse_effect_localization_document(
        "sample_effect = {\n"
        "    global = SAMPLE_EFFECT\n"
        "    first = SAMPLE_EFFECT_FIRST\n"
        "    global_neg = SAMPLE_EFFECT_NEG\n"
        "}\n"
    )

    definition = document.get_definition("sample_effect")
    assert definition is not None
    assert definition.get_variant("global") == "SAMPLE_EFFECT"
    assert definition.get_variant("first") == "SAMPLE_EFFECT_FIRST"
    assert definition.get_variant("global_neg") == "SAMPLE_EFFECT_NEG"


@pytest.mark.timeout(5)
def test_parse_real_trigger_localization_document(game_install: GameInstall) -> None:
    document = parse_trigger_localization_document(
        _read_text(game_install.representative_files()["trigger_localization_sample"])
    )

    definition = document.get_definition("tag")
    assert definition is not None
    assert definition.get_variant("none") == "COUNTRYTAG_TRIGGER"
    assert definition.get_variant("global_not") == "IS_NOT_COUNTRY_TRIGGER"
    assert definition.get_variant("third_not") == "NOT_THIRD_COUNTRYTAG_TRIGGER"


def test_parse_trigger_localization_inline_definition() -> None:
    document = parse_trigger_localization_document(
        "sample_trigger = {\n"
        "    global = SAMPLE_TRIGGER\n"
        "    global_not = SAMPLE_TRIGGER_NOT\n"
        "    first = SAMPLE_TRIGGER_FIRST\n"
        "}\n"
    )

    definition = document.get_definition("sample_trigger")
    assert definition is not None
    assert definition.get_variant("global") == "SAMPLE_TRIGGER"
    assert definition.get_variant("global_not") == "SAMPLE_TRIGGER_NOT"
    assert definition.get_variant("first") == "SAMPLE_TRIGGER_FIRST"

