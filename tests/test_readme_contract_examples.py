from __future__ import annotations

from pathlib import Path

from eu5miner import (
    ContentPhase,
    GameInstall,
    VirtualFilesystem,
    format_mod_update_report,
    plan_mod_update,
)
from eu5miner.domains.diplomacy import (
    build_diplomacy_graph_catalog,
    build_war_flow_catalog,
    parse_casus_belli_document,
    parse_country_interaction_document,
    parse_peace_treaty_document,
    parse_subject_type_document,
    parse_wargoal_document,
)
from eu5miner.domains.economy import (
    build_market_catalog,
    parse_goods_document,
    parse_price_document,
)
from eu5miner.domains.government import build_government_catalog, parse_government_type_document
from eu5miner.domains.localization import build_localization_bundle
from eu5miner.domains.map import build_linked_location_document, parse_default_map_document
from eu5miner.domains.religion import build_religion_catalog, parse_religion_document
from eu5miner.domains.units import parse_unit_category_document
from eu5miner.inspection import (
    format_install_summary,
    format_system_report,
    get_system_entity,
    get_system_report,
    inspect_install,
    list_entity_systems,
    list_supported_systems,
    list_system_entities,
)
from tests.integration_support import build_synthetic_install, build_synthetic_mod_workflow_surface


def test_readme_root_package_example_remains_executable(tmp_path: Path) -> None:
    surface = build_synthetic_mod_workflow_surface(tmp_path / "mod_workflow")
    gui_relative_path = Path("gui") / "agenda_view.gui"
    gui_file = surface.install.phase_dir(ContentPhase.IN_GAME) / gui_relative_path
    gui_file.parent.mkdir(parents=True, exist_ok=True)
    gui_file.write_text("guiTypes = { widget = { name = agenda_view } }\n", encoding="utf-8")

    install = GameInstall.discover(surface.install_root)
    vfs = VirtualFilesystem.from_install(
        install,
        mod_roots=[surface.target_mod_root, surface.later_mod_root],
    )

    merged = vfs.get_merged_file(ContentPhase.IN_GAME, gui_relative_path)
    update = plan_mod_update(
        vfs,
        surface.target_mod_root.name,
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(surface.override_relative_path,),
        content_by_relative_path={surface.override_relative_path: "building = {}\n"},
    )

    assert merged is not None
    assert merged.relative_path == gui_relative_path
    assert update.target_source_name == surface.target_mod_root.name
    assert update.phase is ContentPhase.IN_GAME
    assert update.relative_root == Path("common") / "buildings"
    assert "Planned mod update: my_mod" in format_mod_update_report(update)


def test_readme_inspection_example_remains_executable(tmp_path: Path) -> None:
    install = _build_readme_inspection_install(tmp_path / "inspection")

    summary = inspect_install(install.root)
    formatted_summary = format_install_summary(summary)
    systems = list_supported_systems()
    entity_systems = list_entity_systems()
    discovered_install = GameInstall.discover(summary.root)
    economy_report = get_system_report(discovered_install, "economy")
    formatted_report = format_system_report(economy_report)
    economy_entities = list_system_entities(discovered_install, "economy")
    iron = get_system_entity(discovered_install, "economy", "iron")

    assert summary.root == install.root
    assert "Install root:" in formatted_summary
    assert [system.name for system in systems] == [
        "economy",
        "diplomacy",
        "government",
        "religion",
        "interface",
        "map",
    ]
    assert [system.name for system in entity_systems] == [
        "economy",
        "diplomacy",
        "government",
        "religion",
        "map",
    ]
    assert economy_report.name == "economy"
    assert "System report: economy" in formatted_report
    assert any(entity.name == "iron" for entity in economy_entities)
    assert iron.summary.name == "iron"
    assert any(field.name == "default_market_price" for field in iron.fields)


def test_readme_grouped_package_example_remains_executable() -> None:
    casus_belli_document = parse_casus_belli_document(
        "sample_cb = { war_goal_type = superiority }\n"
    )
    wargoal_document = parse_wargoal_document(
        "superiority = { type = superiority attacker = { conquer_cost = 1 } }\n"
    )
    peace_treaty_document = parse_peace_treaty_document(
        "peace_example = { effect = { make_subject_of = { "
        "type = subject_type:sample_subject } } }\n"
    )
    subject_type_document = parse_subject_type_document(
        "sample_subject = { level = 1 allow_subjects = no }\n"
    )
    country_interaction_document = parse_country_interaction_document(
        "sample_country_interaction = { type = diplomacy }\n"
    )

    war_catalog = build_war_flow_catalog(
        casus_belli_documents=(casus_belli_document,),
        wargoal_documents=(wargoal_document,),
        peace_treaty_documents=(peace_treaty_document,),
        subject_type_documents=(subject_type_document,),
    )
    diplomacy_catalog = build_diplomacy_graph_catalog(
        casus_belli_documents=(casus_belli_document,),
        wargoal_documents=(wargoal_document,),
        peace_treaty_documents=(peace_treaty_document,),
        subject_type_documents=(subject_type_document,),
        country_interaction_documents=(country_interaction_document,),
    )

    goods_document = parse_goods_document("iron = { method = mining category = raw_material }\n")
    price_document = parse_price_document("build_road = { gold = 10 }\n")
    market_catalog = build_market_catalog(
        goods_documents=(goods_document,),
        price_documents=(price_document,),
    )

    government_type_document = parse_government_type_document(
        "monarchy = { heir_selection = cognatic government_power = legitimacy }\n"
    )
    government_catalog = build_government_catalog(
        government_type_documents=(government_type_document,),
    )

    religion_document = parse_religion_document("example_faith = { group = abrahamic }\n")
    religion_catalog = build_religion_catalog(religion_documents=(religion_document,))

    default_map_document = parse_default_map_document('setup = "definitions.txt"\n')
    localization_bundle = build_localization_bundle(
        (("sample.yml", 'l_english:\nSAMPLE_KEY: "Sample"\n'),)
    )
    unit_category_document = parse_unit_category_document(
        "sample_category = { is_army = yes startup_amount = 1 }\n"
    )

    assert war_catalog.get_wargoal("superiority") is not None
    assert diplomacy_catalog.get_casus_belli("sample_cb") is not None
    assert market_catalog.get_good("iron") is not None
    assert government_catalog.get_government_type("monarchy") is not None
    assert religion_catalog.get_religion("example_faith") is not None
    assert default_map_document.referenced_files.setup == '"definitions.txt"'
    assert localization_bundle.get_value("SAMPLE_KEY") == "Sample"
    assert unit_category_document.get_definition("sample_category") is not None
    assert callable(build_linked_location_document)


def _build_readme_inspection_install(root: Path) -> GameInstall:
    install = build_synthetic_install(root / "install")
    representative_files = install.representative_files()

    economy_fixture_texts = {
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
        "goods_demand_sample": "sample_demand = { iron = 0.5 category = building_construction }\n",
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

    for key, text in economy_fixture_texts.items():
        representative_files[key].parent.mkdir(parents=True, exist_ok=True)
        representative_files[key].write_text(text, encoding="utf-8")

    return install
