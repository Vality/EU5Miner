from __future__ import annotations

import json
from pathlib import Path

import pytest

import eu5miner.inspection as inspection_module
from eu5miner.inspection import (
    EntityDetail,
    EntityField,
    EntitySummary,
    format_install_summary,
    format_system_report,
    get_system_entity,
    get_system_report,
    inspect_install,
    invalidate_system_entity_cache,
    list_entity_systems,
    list_supported_systems,
    list_system_entities,
    summarize_install,
)
from eu5miner.source import ContentPhase, GameInstall
from tests.integration_support import build_synthetic_install


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


def test_list_entity_systems_returns_expected_names_and_primary_kinds() -> None:
    systems = tuple((system.name, system.primary_entity_kind) for system in list_entity_systems())

    assert systems == (
        ("economy", "good"),
        ("diplomacy", "casus_belli"),
        ("government", "government_type"),
        ("religion", "religion"),
        ("map", "location"),
    )


def test_get_system_report_rejects_unknown_system(tmp_path: Path) -> None:
    install_root = _make_test_install(tmp_path / "install")
    install = GameInstall.discover(install_root)

    with pytest.raises(KeyError, match="Unknown system 'unknown'"):
        get_system_report(install, "unknown")


def test_list_system_entities_rejects_unknown_system(tmp_path: Path) -> None:
    install_root = _make_test_install(tmp_path / "install")
    install = GameInstall.discover(install_root)

    with pytest.raises(KeyError, match="Unknown entity system 'unknown'"):
        list_system_entities(install, "unknown")


@pytest.mark.parametrize(
    ("system", "expected_summary_fragment"),
    [
        ("economy", "goods definitions:"),
        ("diplomacy", "casus belli definitions:"),
        ("government", "government type definitions:"),
        ("religion", "religion definitions:"),
        ("interface", "GUI templates:"),
        ("map", "linked locations:"),
    ],
)
def test_get_system_report_and_formatting_are_install_independent(
    tmp_path: Path,
    system: str,
    expected_summary_fragment: str,
) -> None:
    install = _make_synthetic_report_install(tmp_path / system, system)

    report = get_system_report(install, system)
    formatted = format_system_report(report)

    assert report.name == system
    assert report.description
    assert len(report.representative_keys) > 0
    assert len(report.summary_lines) > 0
    assert any(
        summary_line.startswith(expected_summary_fragment) for summary_line in report.summary_lines
    )
    assert f"System report: {system}" in formatted
    assert "Representative files:" in formatted
    assert "Summary:" in formatted
    assert expected_summary_fragment in formatted


@pytest.mark.parametrize(
    ("system", "entity_name", "entity_kind", "group_name", "field_name"),
    [
        ("economy", "iron", "good", "raw_material", "default_market_price"),
        ("diplomacy", "sample_cb", "casus_belli", "sample_goal", "war_goal_type"),
        ("government", "monarchy", "government_type", "legitimacy", "government_power"),
        ("religion", "catholic", "religion", "christian", "group"),
        ("map", "stockholm", "location", "province", "hierarchy_path"),
    ],
)
def test_entity_browsing_is_install_independent_for_curated_subset(
    tmp_path: Path,
    system: str,
    entity_name: str,
    entity_kind: str,
    group_name: str,
    field_name: str,
) -> None:
    install = _make_synthetic_report_install(tmp_path / system, system)

    summaries = list_system_entities(install, system)
    detail = get_system_entity(install, system, entity_name)

    assert any(
        summary.name == entity_name
        and summary.entity_kind == entity_kind
        and summary.group == group_name
        for summary in summaries
    )
    assert detail.summary.system == system
    assert detail.summary.name == entity_name
    assert detail.summary.entity_kind == entity_kind
    assert any(field.name == field_name for field in detail.fields)


def test_diplomacy_entity_browsing_surfaces_linked_war_and_interaction_targets(
    tmp_path: Path,
) -> None:
    install = _make_synthetic_report_install(tmp_path / "diplomacy", "diplomacy")

    detail = get_system_entity(install, "diplomacy", "sample_cb")
    links = {(reference.role, reference.target_name) for reference in detail.references}

    assert ("wargoal", "sample_goal") in links
    assert ("peace_treaty", "peace_example") in links
    assert ("country_interaction", "country_link") in links


def test_get_system_entity_rejects_unknown_name(tmp_path: Path) -> None:
    install = _make_synthetic_report_install(tmp_path / "economy", "economy")

    with pytest.raises(KeyError, match="Unknown entity 'missing_good' for system 'economy'"):
        get_system_entity(install, "economy", "missing_good")


def test_entity_queries_cache_repeated_list_and_get_for_same_install_and_system(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install = _make_synthetic_report_install(tmp_path / "map", "map")
    original = inspection_module._build_system_entity_details
    call_count = 0

    inspection_module._ENTITY_QUERY_CACHE.clear()

    def counting_builder(
        install_arg: GameInstall,
        system: str,
        mod_roots: tuple[Path, ...] | list[Path] | None,
    ) -> tuple[EntityDetail, ...]:
        nonlocal call_count
        call_count += 1
        return original(install_arg, system, mod_roots)

    monkeypatch.setattr(inspection_module, "_build_system_entity_details", counting_builder)

    summaries = list_system_entities(install, "map")
    detail = get_system_entity(install, "map", "stockholm")
    repeated_summaries = list_system_entities(install, "map")

    assert call_count == 1
    assert any(summary.name == "stockholm" for summary in summaries)
    assert detail.summary.name == "stockholm"
    assert repeated_summaries == summaries


def test_entity_query_cache_is_keyed_by_mod_roots(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _make_test_install(tmp_path / "install")
    install = GameInstall.discover(install_root)
    first_mod_root = tmp_path / "mods" / "first"
    second_mod_root = tmp_path / "mods" / "second"
    _make_mod_root(first_mod_root)
    _make_mod_root(second_mod_root)

    original = inspection_module._build_system_entity_details
    call_count = 0

    inspection_module._ENTITY_QUERY_CACHE.clear()

    def counting_builder(
        install_arg: GameInstall,
        system: str,
        mod_roots: tuple[Path, ...] | list[Path] | None,
    ) -> tuple[EntityDetail, ...]:
        nonlocal call_count
        call_count += 1
        return original(install_arg, system, mod_roots)

    monkeypatch.setattr(inspection_module, "_build_system_entity_details", counting_builder)

    list_system_entities(install, "economy", mod_roots=[first_mod_root])
    list_system_entities(install, "economy", mod_roots=[first_mod_root])
    list_system_entities(install, "economy", mod_roots=[second_mod_root])

    assert call_count == 2


def test_invalidate_system_entity_cache_invalidates_only_requested_system(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _make_test_install(tmp_path / "install")
    install = GameInstall.discover(install_root)
    call_counts: dict[str, int] = {}

    inspection_module._ENTITY_QUERY_CACHE.clear()

    def counting_builder(
        install_arg: GameInstall,
        system: str,
        mod_roots: tuple[Path, ...] | list[Path] | None,
    ) -> tuple[EntityDetail, ...]:
        del install_arg, mod_roots
        call_counts[system] = call_counts.get(system, 0) + 1
        return (_cached_entity_detail(system),)

    monkeypatch.setattr(inspection_module, "_build_system_entity_details", counting_builder)

    list_system_entities(install, "economy")
    list_system_entities(install, "map")

    assert invalidate_system_entity_cache(install, "map") == 1

    list_system_entities(install, "economy")
    list_system_entities(install, "map")

    assert call_counts == {"economy": 1, "map": 2}


def test_invalidate_system_entity_cache_is_scoped_to_install_and_mod_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install = GameInstall.discover(_make_test_install(tmp_path / "install"))
    other_install = GameInstall.discover(_make_test_install(tmp_path / "other_install"))
    first_mod_root = tmp_path / "mods" / "first"
    second_mod_root = tmp_path / "mods" / "second"
    _make_mod_root(first_mod_root)
    _make_mod_root(second_mod_root)

    call_count = 0
    inspection_module._ENTITY_QUERY_CACHE.clear()

    def counting_builder(
        install_arg: GameInstall,
        system: str,
        mod_roots: tuple[Path, ...] | list[Path] | None,
    ) -> tuple[EntityDetail, ...]:
        nonlocal call_count
        del install_arg, system, mod_roots
        call_count += 1
        return (_cached_entity_detail("economy"),)

    monkeypatch.setattr(inspection_module, "_build_system_entity_details", counting_builder)

    list_system_entities(install, "economy", mod_roots=[first_mod_root])
    list_system_entities(install, "economy", mod_roots=[second_mod_root])
    list_system_entities(other_install, "economy", mod_roots=[first_mod_root])

    assert invalidate_system_entity_cache(install, "economy", mod_root=first_mod_root) == 1

    list_system_entities(install, "economy", mod_roots=[first_mod_root])
    list_system_entities(install, "economy", mod_roots=[second_mod_root])
    list_system_entities(other_install, "economy", mod_roots=[first_mod_root])

    assert call_count == 4


def test_get_system_entity_preserves_first_matching_detail_when_cached(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _make_test_install(tmp_path / "install")
    install = GameInstall.discover(install_root)
    first_detail = EntityDetail(
        summary=EntitySummary(
            system="economy",
            entity_kind="good",
            name="duplicate",
            group="first",
            description="first",
        ),
        fields=(EntityField(name="marker", value="first"),),
        references=(),
    )
    second_detail = EntityDetail(
        summary=EntitySummary(
            system="economy",
            entity_kind="good",
            name="duplicate",
            group="second",
            description="second",
        ),
        fields=(EntityField(name="marker", value="second"),),
        references=(),
    )

    inspection_module._ENTITY_QUERY_CACHE.clear()
    monkeypatch.setattr(
        inspection_module,
        "_build_system_entity_details",
        lambda _install, _system, _mod_roots: (first_detail, second_detail),
    )

    detail = get_system_entity(install, "economy", "duplicate")

    assert detail == first_detail


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


def _cached_entity_detail(system: str) -> EntityDetail:
    return EntityDetail(
        summary=EntitySummary(
            system=system,
            entity_kind="cached_entity",
            name=f"{system}_entity",
            group=None,
            description="cached",
        ),
        fields=(),
        references=(),
    )


def _make_synthetic_report_install(root: Path, system: str) -> GameInstall:
    install = build_synthetic_install(root / "install")
    representative_files = install.representative_files()

    for key, text in _synthetic_report_fixture_texts(system).items():
        path = representative_files[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    return install


def _synthetic_report_fixture_texts(system: str) -> dict[str, str]:
    if system == "economy":
        return {
            "goods_sample": (
                "iron = {\n"
                "    method = mining\n"
                "    category = raw_material\n"
                "    default_market_price = 3\n"
                "}\n"
            ),
            "goods_secondary_sample": "grain = { method = farming category = food }\n",
            "price_sample": "build_road = { gold = 10 }\n",
            "price_secondary_sample": "granary = { tools = 5 }\n",
            "goods_demand_category_sample": "building_construction = { display = integer }\n",
            "goods_demand_sample": (
                "sample_demand = { iron = 0.5 category = building_construction }\n"
            ),
            "goods_demand_secondary_sample": (
                "food_demand = { grain = 1 category = building_construction }\n"
            ),
            "goods_demand_tertiary_sample": (
                "event_demand = { iron = 0.25 category = building_construction }\n"
            ),
            "production_method_sample": (
                "maintenance = { tools = 0.1 category = building_maintenance }\n"
            ),
            "employment_system_sample": "equality = { priority = { value = 1 } }\n",
            "generic_action_market_sample": (
                "create_market = {\n"
                "    type = owncountry\n"
                "    select_trigger = { looking_for_a = market }\n"
                "}\n"
            ),
            "generic_action_secondary_sample": (
                "open_employment = {\n"
                "    type = owncountry\n"
                "    select_trigger = { looking_for_a = employment_system }\n"
                "}\n"
            ),
            "generic_action_loan_sample": (
                "take_loan = {\n"
                "    type = owncountry\n"
                "    select_trigger = { looking_for_a = bank_loan }\n"
                "}\n"
            ),
            "attribute_column_default_sample": (
                "defaults = { name = { widget = default_text_column } }\n"
            ),
            "attribute_column_market_sample": (
                "market = { name = { widget = default_text_column } }\n"
            ),
            "attribute_column_trade_sample": (
                "trade = { route = { widget = default_text_column } }\n"
            ),
            "attribute_column_secondary_sample": (
                "goods = { price = { widget = default_numeric_column } }\n"
            ),
            "attribute_column_loan_sample": (
                "loan = { size = { widget = default_numeric_column } }\n"
            ),
        }
    if system == "diplomacy":
        return {
            "casus_belli_sample": "sample_cb = { war_goal_type = sample_goal }\n",
            "casus_belli_secondary_sample": (
                "trade_cb = { war_goal_type = sample_goal trade = yes }\n"
            ),
            "casus_belli_subject_sample": (
                "subject_cb = { war_goal_type = sample_goal }\n"
            ),
            "casus_belli_religious_sample": (
                "religious_cb = { war_goal_type = sample_goal }\n"
            ),
            "casus_belli_trade_sample": (
                "trade_conflict = { war_goal_type = sample_goal }\n"
            ),
            "wargoal_sample": (
                "sample_goal = { type = superiority attacker = { conquer_cost = 1 } }\n"
            ),
            "peace_treaty_sample": (
                "peace_example = {\n"
                "    potential = { scope:war = { casus_belli ?= casus_belli:sample_cb } }\n"
                "    effect = { make_subject_of = { type = subject_type:sample_subject } }\n"
                "}\n"
            ),
            "peace_treaty_secondary_sample": (
                "peace_secondary = { effect = { add_prestige = 5 } }\n"
            ),
            "peace_treaty_special_sample": (
                "peace_special = { effect = { make_subject_of = { "
                "type = subject_type:sample_subject } } }\n"
            ),
            "subject_type_sample": (
                "sample_subject = { level = 1 allow_subjects = no }\n"
            ),
            "subject_type_secondary_sample": "tributary = { level = 1 }\n",
            "subject_type_colonial_sample": "colonial_subject = { level = 1 }\n",
            "subject_type_hre_sample": "hre_subject = { level = 2 }\n",
            "subject_type_special_sample": "special_subject = { level = 3 }\n",
            "country_interaction_sample": (
                "country_link = { effect = { add_casus_belli = { "
                "type = casus_belli:sample_cb } } }\n"
            ),
            "country_interaction_secondary_sample": (
                "country_subject = { effect = { make_subject_of = { "
                "type = subject_type:sample_subject } } }\n"
            ),
            "character_interaction_sample": (
                "character_link = { effect = { make_subject_of = { "
                "type = subject_type:sample_subject } } }\n"
            ),
            "character_interaction_secondary_sample": (
                "sample_character_interaction = { message = yes on_own_nation = yes }\n"
            ),
            "character_interaction_ui_sample": (
                "ui_character_interaction = { message = yes }\n"
            ),
            "unit_type_sample": (
                "sample_unit = { category = sample_category buildable = yes }\n"
            ),
            "unit_type_secondary_sample": (
                "secondary_unit = { category = sample_category buildable = yes }\n"
            ),
            "unit_ability_sample": (
                "sample_ability = { toggle = yes army_only = yes }\n"
            ),
            "unit_ability_secondary_sample": (
                "secondary_ability = { toggle = yes army_only = yes }\n"
            ),
            "unit_category_sample": (
                "sample_category = { is_army = yes startup_amount = 1 }\n"
            ),
            "unit_category_secondary_sample": (
                "naval_category = { is_navy = yes startup_amount = 1 }\n"
            ),
        }
    if system == "government":
        return {
            "government_type_sample": (
                "monarchy = {\n"
                "    heir_selection = cognatic\n"
                "    government_power = legitimacy\n"
                "    default_character_estate = sample_estate\n"
                "}\n"
            ),
            "government_reform_sample": (
                "sample_reform = { government = monarchy years = 2 "
                "country_modifier = { add = 1 } }\n"
            ),
            "government_reform_secondary_sample": (
                "secondary_reform = { government = monarchy years = 3 "
                "country_modifier = { add = 1 } }\n"
            ),
            "government_reform_special_sample": (
                "special_reform = { government = monarchy years = 4 "
                "country_modifier = { add = 1 } }\n"
            ),
            "law_sample": (
                "sample_law = {\n"
                "    law_category = administrative\n"
                "    law_gov_group = monarchy\n"
                "    policy_a = { years = 2 country_modifier = { add = 1 } "
                "estate_preferences = { sample_estate } }\n"
                "}\n"
            ),
            "law_secondary_sample": (
                "secondary_law = { law_category = diplomatic law_gov_group = monarchy }\n"
            ),
            "law_country_specific_sample": (
                "country_law = { law_category = military law_gov_group = monarchy }\n"
            ),
            "law_io_sample": (
                "io_law = { law_category = administrative law_gov_group = monarchy }\n"
            ),
            "law_io_secondary_sample": (
                "io_secondary_law = { law_category = diplomatic law_gov_group = monarchy }\n"
            ),
            "estate_sample": (
                "sample_estate = { color = pop_nobles power_per_pop = 25 "
                "tax_per_pop = 100 ruler = yes }\n"
            ),
            "estate_privilege_sample": (
                "sample_privilege = { estate = sample_estate "
                "country_modifier = { add = 1 } }\n"
            ),
            "estate_privilege_secondary_sample": (
                "sample_privilege_two = { estate = sample_estate "
                "country_modifier = { add = 1 } }\n"
            ),
            "estate_privilege_special_sample": (
                "sample_privilege_three = { estate = sample_estate "
                "country_modifier = { add = 1 } }\n"
            ),
            "parliament_type_sample": (
                "sample_parliament = { type = country modifier = { add = 1 } }\n"
            ),
            "parliament_type_secondary_sample": (
                "sample_io_parliament = { type = international_organization "
                "modifier = { add = 1 } }\n"
            ),
            "parliament_agenda_sample": (
                "sample_agenda = { type = country estate = sample_estate "
                "chance = 10 on_accept = { add = 1 } }\n"
            ),
            "parliament_agenda_secondary_sample": (
                "secondary_agenda = { type = country estate = sample_estate "
                "chance = 5 on_accept = { add = 1 } }\n"
            ),
            "parliament_agenda_special_sample": (
                "special_agenda = { type = country special_status = elector "
                "chance = 1 on_accept = { add = 1 } }\n"
            ),
            "parliament_issue_sample": (
                "sample_issue = { type = country estate = sample_estate chance = 0 "
                "on_debate_passed = { add = 1 } }\n"
            ),
            "parliament_issue_secondary_sample": (
                "secondary_issue = { type = country estate = sample_estate chance = 1 "
                "on_debate_passed = { add = 1 } }\n"
            ),
            "parliament_issue_special_sample": (
                "special_issue = { type = country special_status = emperor chance = 1 "
                "on_debate_passed = { add = 1 } }\n"
            ),
            "institution_sample": (
                "renaissance = { age = age_2_renaissance can_spawn = { always = yes } "
                "promote_chance = { add = 1 } }\n"
            ),
            "institution_secondary_sample": (
                "reformation = { age = age_4_reformation can_spawn = { always = yes } "
                "promote_chance = { add = 1 } }\n"
            ),
        }
    if system == "religion":
        return {
            "religion_sample": (
                "catholic = {\n"
                "    group = christian\n"
                "    factions = { sample_faction }\n"
                "    religious_focuses = { sample_focus }\n"
                "    religious_school = sample_school\n"
                "    religious_aspects = { sample_aspect }\n"
                "    tags = { catholic_gfx }\n"
                "}\n"
            ),
            "religion_secondary_sample": "orthodox = { group = christian }\n",
            "religion_muslim_sample": (
                "sunni = { group = muslim religious_school = sample_school }\n"
            ),
            "religion_tonal_sample": (
                "nahuatl = { group = tonal religious_focuses = { sample_focus } }\n"
            ),
            "religion_dharmic_sample": (
                "hindu = { group = dharmic religious_school = sample_school }\n"
            ),
            "religious_aspect_sample": (
                "sample_aspect = { religion = catholic enabled = { always = yes } "
                "modifier = { add = 1 } opinions = { sample_aspect = 10 } }\n"
            ),
            "religious_aspect_secondary_sample": (
                "secondary_aspect = { religion = orthodox enabled = { always = yes } "
                "modifier = { add = 1 } }\n"
            ),
            "religious_faction_sample": (
                "sample_faction = { visible = { always = yes } enabled = { always = yes } "
                "actions = { action_a action_b } }\n"
            ),
            "religious_focus_sample": (
                "sample_focus = { monthly_progress = { add = 1 } "
                "modifier_on_completion = { add = 1 } }\n"
            ),
            "religious_school_sample": (
                "sample_school = { color = rgb { 1 2 3 } enabled_for_country = { always = yes } "
                "modifier = { add = 1 } }\n"
            ),
            "religious_school_secondary_sample": (
                "secondary_school = { color = rgb { 3 2 1 } enabled_for_country = { always = yes } "
                "modifier = { add = 1 } }\n"
            ),
            "religious_figure_sample": (
                "sample_figure = { enabled_for_religion = { group = religion_group:christian } }\n"
            ),
            "religious_figure_secondary_sample": (
                "secondary_figure = { enabled_for_religion = { group = religion_group:dharmic } }\n"
            ),
            "holy_site_type_sample": "temple = { location_modifier = { add = 1 } }\n",
            "holy_site_sample": (
                "sample_site = { location = rome type = temple importance = 4 "
                "religions = { catholic } }\n"
            ),
            "holy_site_secondary_sample": (
                "secondary_site = { location = varanasi type = temple importance = 3 "
                "religions = { hindu } god = vishnu_god }\n"
            ),
        }
    if system == "interface":
        return {
            "customizable_localization_sample": (
                "GetOrderOfChivalry = {\n"
                "    parent = order_of_chivalry\n"
                "    suffix = \"_law\"\n"
                "    fallback = true\n"
                "}\n"
            ),
            "effect_localization_sample": (
                "sample_effect = {\n"
                "    global = SAMPLE_EFFECT\n"
                "    first = SAMPLE_EFFECT_FIRST\n"
                "}\n"
            ),
            "trigger_localization_sample": (
                "sample_trigger = {\n"
                "    global = SAMPLE_TRIGGER\n"
                "    global_not = SAMPLE_TRIGGER_NOT\n"
                "}\n"
            ),
            "english_laws_localization": 'l_english:\norder_of_chivalry_law: "Order of Chivalry"\n',
            "english_effects_localization": (
                'l_english:\nSAMPLE_EFFECT: "Effect"\nSAMPLE_EFFECT_FIRST: "First Effect"\n'
            ),
            "english_triggers_localization": (
                'l_english:\nSAMPLE_TRIGGER: "Trigger"\nSAMPLE_TRIGGER_NOT: "Not Trigger"\n'
            ),
            "gui_sample": (
                "@scale = 42\n"
                "template sample_template {\n"
                '    text = "HELLO"\n'
                "}\n"
                "window = {\n"
                '    name = "root_window"\n'
                '    widgetid = "root_widget"\n'
                "}\n"
            ),
            "gui_types_sample": (
                "types SampleTypes {\n"
                "    type FancyWindow = window {\n"
                '        name = "fancy_window"\n'
                "    }\n"
                "}\n"
                "window = {\n"
                '    name = "sample_types_root"\n'
                "}\n"
            ),
            "gui_library_sample": (
                "template text_section_description {\n"
                '    text = "Body"\n'
                "}\n"
                "types UiLibrary {\n"
                "    type LibraryWindow = window {\n"
                '        name = "ui_library_typed"\n'
                "    }\n"
                "}\n"
                "window = {\n"
                '    name = "ui_library_window"\n'
                "}\n"
            ),
            "main_menu_scenarios_sample": (
                "sample_scenario = {\n"
                "    country = FRA\n"
                "    flag = FRA_scenario\n"
                "    player_playstyle = MILITARY\n"
                "    player_proficiency = ADVANCED\n"
                "}\n"
            ),
            "loading_screen_localization_sample": 'l_english:\nLOADING_TIP_0: "Tip"\n',
        }
    if system == "map":
        return {
            "map_default": (
                'provinces = "locations.png"\n'
                'rivers = "rivers.png"\n'
                'topology = "heightmap.heightmap"\n'
                'adjacencies = "adjacencies.csv"\n'
                'setup = "definitions.txt"\n'
                'ports = "ports.csv"\n'
                'location_templates = "location_templates.txt"\n'
                "equator_y = 3340\n"
                "wrap_x = yes\n"
                "sound_toll = { oresund = helsingor }\n"
                "volcanoes = { klikitat }\n"
                "earthquakes = { lisbon }\n"
                "sea_zones = { baltic }\n"
                "lakes = { malaren }\n"
                "impassable_mountains = { skanderna }\n"
                "non_ownable = { sahara_corridor }\n"
            ),
            "map_definitions": (
                "world = {\n"
                "    region = {\n"
                "        area = {\n"
                "            province = { stockholm }\n"
                "        }\n"
                "    }\n"
                "}\n"
            ),
            "map_adjacencies": (
                "From;To;Type;Through;start_x;start_y;stop_x;stop_y;Comment\n"
                "messina;reggiocal;sea;strait_messina;8396;5518;8404;5519;xxx\n"
            ),
            "map_ports": "LandProvince;SeaZone;x;y;\nstockholm;stockholms_skargard;8532;6945;x\n",
            "main_menu_country_setup_sample": (
                "countries = {\n"
                "    countries = {\n"
                "        SWE = {\n"
                "            own_control_core = { stockholm }\n"
                "            capital = stockholm\n"
                "        }\n"
                "    }\n"
                "}\n"
            ),
            "main_menu_location_setup_sample": (
                "locations = {\n    stockholm = { timed_modifiers = { } }\n}\n"
            ),
        }
    raise KeyError(system)
